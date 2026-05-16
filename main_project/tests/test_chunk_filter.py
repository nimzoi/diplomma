"""Unit tests dla chunk-level scope filter (per chunk_filter.py).

Sanity tests:
- DROP_SOURCES (ELI ustawa_id + S6 domain) drop poprawnie
- CHF content w SN orzeczenia drop poprawnie (TP) — non-CHF SN orzeczenia keep (TN)
- RF PDFs pure-insurance drop, banking-consumer keep
- KEEP-confirmed sources (UOKiK Q&A, UE Dyrektywy, TSUE, UPK, KC) NIE są dropped
- `loose` policy zachowuje edge cases (RF, SN, Prawo bankowe)
- `none` policy = pass-through
"""

from __future__ import annotations

from datetime import date

import pytest

from src.halu.chunk_filter import (
    LOOSE_DROP_ELI_USTAWY,
    STRICT_DROP_ELI_USTAWY,
    STRICT_DROP_S6_SOURCES,
    FilterPolicy,
    explain_drop_reason,
    filter_chunks,
)
from src.halu.schemas import Category, Chunk, SourceType


# === Fixtures ===


def make_chunk(
    chunk_id: str,
    source: str,
    source_type: SourceType,
    tresc: str = "Dummy treść chunk testowego o consumer rights.",
    title: str = "Testowy chunk",
    source_url: str = "https://example.test/x",
    metadata: dict | None = None,
    categories: list[Category] | None = None,
) -> Chunk:
    """Build minimal valid Chunk dla tests."""
    return Chunk(
        chunk_id=chunk_id,
        source_type=source_type,
        source=source,
        source_url=source_url,
        title=title,
        tresc=tresc,
        citation_string=None,
        cited_articles=[],
        categories=categories or [Category.OTHER],
        license="test",
        scrape_date=date(2026, 5, 16),
        process_date=date(2026, 5, 16),
        metadata=metadata or {},
    )


# === ELI ustawa drops ===


class TestStrictEliDrops:
    """STRICT policy: drop KPC + Prawo upadłościowe + Prawo bankowe + Usługi płatnicze
    + 3 uchylone."""

    @pytest.mark.parametrize(
        "ustawa_id",
        [
            "DU/1964/296",  # KPC
            "DU/2003/535",  # Prawo upadłościowe
            "DU/1997/939",  # Prawo bankowe
            "DU/2011/1175",  # Usługi płatnicze
            "DU/2003/2275",  # UCHYLONA bezp. produktów
            "DU/2002/1176",  # UCHYLONA sprzedaż konsumencka
            "DU/2000/271",  # UCHYLONA ochrona praw konsumentów
        ],
    )
    def test_drops_ustawa(self, ustawa_id: str) -> None:
        chunk = make_chunk(
            chunk_id="eli_test_drop",
            source="isap.sejm.gov.pl",
            source_type=SourceType.LEGAL_STATUTE,
            metadata={"ustawa_id": ustawa_id},
        )
        result = filter_chunks([chunk], policy="strict")
        assert result.kept_count == 0
        assert result.dropped_count == 1
        assert f"eli_{ustawa_id}" in result.drop_stats_by_reason

    @pytest.mark.parametrize(
        "ustawa_id",
        [
            "DU/2014/827",  # UPK ✓ KEEP
            "DU/1964/93",  # KC ✓ KEEP
            "DU/2007/331",  # UOKK ✓ KEEP
            "DU/2011/715",  # Kredyt konsumencki ✓ KEEP
            "DU/2016/1823",  # ADR ✓ KEEP
            "DU/2024/1221",  # Prawo komunikacji elektronicznej ✓ KEEP
            "DU/1997/483",  # Konstytucja (1 chunk) ✓ KEEP
            "DU/2002/1204",  # UŚUDE ✓ KEEP
        ],
    )
    def test_keeps_core_ustawa(self, ustawa_id: str) -> None:
        chunk = make_chunk(
            chunk_id="eli_test_keep",
            source="isap.sejm.gov.pl",
            source_type=SourceType.LEGAL_STATUTE,
            metadata={"ustawa_id": ustawa_id},
        )
        result = filter_chunks([chunk], policy="strict")
        assert result.kept_count == 1
        assert result.dropped_count == 0


class TestLooseEliDrops:
    """LOOSE policy: drop only uchylone (3) + KPC. Keep Prawo bankowe + Usługi płatnicze."""

    @pytest.mark.parametrize(
        "ustawa_id",
        ["DU/1964/296", "DU/2003/2275", "DU/2002/1176", "DU/2000/271"],
    )
    def test_drops_uchylone_and_kpc(self, ustawa_id: str) -> None:
        chunk = make_chunk(
            chunk_id="eli_loose_drop",
            source="isap.sejm.gov.pl",
            source_type=SourceType.LEGAL_STATUTE,
            metadata={"ustawa_id": ustawa_id},
        )
        result = filter_chunks([chunk], policy="loose")
        assert result.kept_count == 0

    @pytest.mark.parametrize(
        "ustawa_id",
        [
            "DU/2003/535",  # Prawo upadłościowe — loose KEEPS
            "DU/1997/939",  # Prawo bankowe — loose KEEPS
            "DU/2011/1175",  # Usługi płatnicze — loose KEEPS
        ],
    )
    def test_keeps_edge_case_ustawa_in_loose(self, ustawa_id: str) -> None:
        chunk = make_chunk(
            chunk_id="eli_loose_keep_edge",
            source="isap.sejm.gov.pl",
            source_type=SourceType.LEGAL_STATUTE,
            metadata={"ustawa_id": ustawa_id},
        )
        result = filter_chunks([chunk], policy="loose")
        assert result.kept_count == 1


# === S6 source drops ===


class TestStrictS6Drops:
    @pytest.mark.parametrize(
        "source",
        ["bankier.pl", "money.pl", "infor.pl", "gazetaprawna.pl", "prawo.pl", "bezprawnik.pl", "ing.pl"],
    )
    def test_drops_finance_journalism_and_ing(self, source: str) -> None:
        chunk = make_chunk(
            chunk_id="s6_test_drop",
            source=source,
            source_type=SourceType.ENCYCLOPEDIC,
        )
        result = filter_chunks([chunk], policy="strict")
        assert result.kept_count == 0
        assert f"s6_{source}" in result.drop_stats_by_reason

    @pytest.mark.parametrize(
        "source",
        [
            "konsument.gov.pl",  # ECC Polska ✓ KEEP
            "cik.uke.gov.pl",
            "uodo.gov.pl",
            "knf.gov.pl",
            "ure.gov.pl",
            "pl.wikipedia.org",
            "federacja-konsumentow.org.pl",
            "rf.gov.pl",
        ],
    )
    def test_keeps_official_consumer_sources(self, source: str) -> None:
        chunk = make_chunk(
            chunk_id="s6_test_keep",
            source=source,
            source_type=SourceType.ENCYCLOPEDIC,
        )
        result = filter_chunks([chunk], policy="strict")
        assert result.kept_count == 1


class TestLooseS6Drops:
    def test_loose_drops_only_ing(self) -> None:
        chunks = [
            make_chunk("c1", "bankier.pl", SourceType.ENCYCLOPEDIC),
            make_chunk("c2", "money.pl", SourceType.ENCYCLOPEDIC),
            make_chunk("c3", "infor.pl", SourceType.ENCYCLOPEDIC),
            make_chunk("c4", "bezprawnik.pl", SourceType.ENCYCLOPEDIC),
            make_chunk("c5", "ing.pl", SourceType.ENCYCLOPEDIC),
        ]
        result = filter_chunks(chunks, policy="loose")
        # Only ing.pl dropped in loose
        assert result.kept_count == 4
        assert result.dropped_count == 1
        assert "s6_ing.pl" in result.drop_stats_by_reason


# === SN orzeczenia CHF content filter ===


class TestSnChfFilter:
    """Strict: SN orzeczenia z CHF/franki content → drop. Non-CHF SN → keep."""

    def test_drops_sn_chf_content(self) -> None:
        chunk = make_chunk(
            chunk_id="sn_chf_test",
            source="www.sn.pl",
            source_type=SourceType.LEGAL_COURT_JUDGMENT,
            source_url="http://www.sn.pl/wyszukiwanie/SitePages/orzeczenia.aspx?Tresc=klauzula",
            title="Wyrok SN — abuzywność klauzul w umowach kredytu hipotecznego",
            tresc=(
                "Sąd Najwyższy rozpoznał skargę kasacyjną dotyczącą klauzul "
                "denominacji do CHF w umowie kredytu hipotecznego. Stwierdza, "
                "iż klauzula indeksowana do waluty obcej (frank szwajcarski) "
                "podlega kontroli abuzywności."
            ),
        )
        result = filter_chunks([chunk], policy="strict")
        assert result.kept_count == 0
        assert result.drop_stats_by_reason.get("sn_chf_content") == 1

    def test_keeps_sn_non_chf_content(self) -> None:
        chunk = make_chunk(
            chunk_id="sn_keep_test",
            source="www.sn.pl",
            source_type=SourceType.LEGAL_COURT_JUDGMENT,
            source_url="http://www.sn.pl/wyszukiwanie/SitePages/orzeczenia.aspx?Tresc=konsument",
            title="Wyrok SN — rękojmia za wady towaru",
            tresc=(
                "Sąd Najwyższy rozpoznał skargę dotyczącą rękojmi za wady "
                "rzeczy sprzedanej konsumentowi w sklepie internetowym. "
                "Konsument zgłosił wadę w terminie 2 lat."
            ),
        )
        result = filter_chunks([chunk], policy="strict")
        assert result.kept_count == 1
        assert result.dropped_count == 0

    def test_loose_keeps_sn_chf_content(self) -> None:
        """Loose policy NIE filtruje CHF content w SN orzeczenia."""
        chunk = make_chunk(
            chunk_id="sn_chf_loose_keep",
            source="www.sn.pl",
            source_type=SourceType.LEGAL_COURT_JUDGMENT,
            source_url="http://www.sn.pl/wyszukiwanie/SitePages/orzeczenia.aspx",
            title="Wyrok SN — CHF frankowicze",
            tresc="Klauzula denominowana do CHF, frank szwajcarski, waluty obcej.",
        )
        result = filter_chunks([chunk], policy="loose")
        assert result.kept_count == 1


# === RF PDFs insurance filter ===


class TestRfInsuranceFilter:
    """Strict: RF PDFs pure-insurance content (≥3 insurance kw, 0 credit kw) → drop."""

    def test_drops_pure_insurance_rf_pdf(self) -> None:
        chunk = make_chunk(
            chunk_id="rf_pdf_ins",
            source="rf.gov.pl",
            source_type=SourceType.LEGAL_DOCUMENT_PDF,
            title="Raport Rzecznika Finansowego — rynek ubezpieczeń",
            tresc=(
                "Raport analizuje rynek ubezpieczeń komunikacyjnych. "
                "Składka ubezpieczeniowa OC podlega regulacji. "
                "Polisa AC obejmuje ryzyka komunikacyjne. "
                "Fundusze inwestycyjne emerytalne stanowią uzupełnienie."
            ),
        )
        result = filter_chunks([chunk], policy="strict")
        assert result.kept_count == 0
        assert result.drop_stats_by_reason.get("rf_pure_insurance") == 1

    def test_keeps_rf_pdf_with_banking_consumer_content(self) -> None:
        """RF PDF z banking/consumer-credit keywords NIE drop nawet jeśli ma insurance words."""
        chunk = make_chunk(
            chunk_id="rf_pdf_credit",
            source="rf.gov.pl",
            source_type=SourceType.LEGAL_DOCUMENT_PDF,
            title="Raport RF — kredyt konsumencki w 2024",
            tresc=(
                "Analiza praktyk dotyczących kredytu konsumenckiego. "
                "RRSO jako kluczowy wskaźnik. Reklamacja bankowa "
                "podlega rygorom UPK. Rachunek bankowy konsumenta wymaga "
                "odrębnej regulacji ochronnej. Ubezpieczenie spłaty kredytu jest dodatkową usługą."
            ),
        )
        result = filter_chunks([chunk], policy="strict")
        assert result.kept_count == 1

    def test_keeps_rf_pdf_with_low_insurance_signal(self) -> None:
        """RF PDF z <3 insurance keywords → keep (nie spełnia threshold)."""
        chunk = make_chunk(
            chunk_id="rf_pdf_low_ins",
            source="rf.gov.pl",
            source_type=SourceType.LEGAL_DOCUMENT_PDF,
            title="Raport RF — sprzedaż konsumencka",
            tresc=(
                "Raport o praktykach w sprzedaży konsumenckiej. "
                "Wymienia się ubezpieczenie jako jedno z ryzyk."
            ),
        )
        result = filter_chunks([chunk], policy="strict")
        assert result.kept_count == 1


# === KEEP-confirmed sources (sanity: never drop) ===


class TestKeepConfirmedSources:
    """Sanity: KEEP-confirmed sources NIE są dropped w żadnej policy."""

    @pytest.mark.parametrize("policy", ["strict", "loose"])
    def test_keeps_uokik_qa(self, policy: FilterPolicy) -> None:
        chunk = make_chunk(
            chunk_id="uokik_qa_1",
            source="prawakonsumenta.uokik.gov.pl",
            source_type=SourceType.QA_GOLD,
        )
        assert filter_chunks([chunk], policy=policy).kept_count == 1

    @pytest.mark.parametrize("policy", ["strict", "loose"])
    def test_keeps_ue_directive(self, policy: FilterPolicy) -> None:
        chunk = make_chunk(
            chunk_id="ue_dir_1",
            source="eur-lex.europa.eu",
            source_type=SourceType.LEGAL_UE_DIRECTIVE,
        )
        assert filter_chunks([chunk], policy=policy).kept_count == 1

    @pytest.mark.parametrize("policy", ["strict", "loose"])
    def test_keeps_tsue_judgment(self, policy: FilterPolicy) -> None:
        chunk = make_chunk(
            chunk_id="tsue_1",
            source="eur-lex.europa.eu",
            source_type=SourceType.LEGAL_TSUE_JUDGMENT,
        )
        assert filter_chunks([chunk], policy=policy).kept_count == 1

    @pytest.mark.parametrize("policy", ["strict", "loose"])
    def test_keeps_uokik_decision(self, policy: FilterPolicy) -> None:
        chunk = make_chunk(
            chunk_id="uokik_dec_1",
            source="decyzje.uokik.gov.pl",
            source_type=SourceType.LEGAL_UOKIK_DECISION,
        )
        assert filter_chunks([chunk], policy=policy).kept_count == 1

    @pytest.mark.parametrize("policy", ["strict", "loose"])
    def test_keeps_consumer_question(self, policy: FilterPolicy) -> None:
        chunk = make_chunk(
            chunk_id="qraw_1",
            source="e-prawnik.pl",
            source_type=SourceType.QA_RAW,
        )
        assert filter_chunks([chunk], policy=policy).kept_count == 1

    @pytest.mark.parametrize("policy", ["strict", "loose"])
    def test_keeps_court_judgment_ms(self, policy: FilterPolicy) -> None:
        """ms.gov.pl orzeczenia KEEP w obu policies (chunked per orzeczenie)."""
        chunk = make_chunk(
            chunk_id="orz_test",
            source="orzeczenia.ms.gov.pl",
            source_type=SourceType.LEGAL_COURT_JUDGMENT,
            title="Wyrok sądu o reklamacji konsumenta",
            tresc="Sąd uznał reklamację konsumenta za zasadną.",
        )
        assert filter_chunks([chunk], policy=policy).kept_count == 1


# === Pass-through (none policy) ===


class TestNonePolicy:
    def test_none_policy_keeps_everything(self) -> None:
        chunks = [
            make_chunk(
                chunk_id="kpc_test",
                source="isap.sejm.gov.pl",
                source_type=SourceType.LEGAL_STATUTE,
                metadata={"ustawa_id": "DU/1964/296"},
            ),
            make_chunk(
                chunk_id="ing_test",
                source="ing.pl",
                source_type=SourceType.ENCYCLOPEDIC,
            ),
            make_chunk(
                chunk_id="bankier_test",
                source="bankier.pl",
                source_type=SourceType.ENCYCLOPEDIC,
            ),
        ]
        result = filter_chunks(chunks, policy="none")
        assert result.kept_count == 3
        assert result.dropped_count == 0


# === Mixed batch sanity (end-to-end smoke) ===


class TestMixedBatch:
    def test_strict_drops_expected_proportion(self) -> None:
        """Mixed batch — 10 chunks z różnymi sources, sprawdź per-reason counts."""
        chunks = [
            # KEEP (5)
            make_chunk("c_upk", "isap.sejm.gov.pl", SourceType.LEGAL_STATUTE,
                       metadata={"ustawa_id": "DU/2014/827"}),
            make_chunk("c_kc", "isap.sejm.gov.pl", SourceType.LEGAL_STATUTE,
                       metadata={"ustawa_id": "DU/1964/93"}),
            make_chunk("c_qa", "prawakonsumenta.uokik.gov.pl", SourceType.QA_GOLD),
            make_chunk("c_ue", "eur-lex.europa.eu", SourceType.LEGAL_UE_DIRECTIVE),
            make_chunk("c_ecc", "konsument.gov.pl", SourceType.ENCYCLOPEDIC),
            # DROP (5)
            make_chunk("c_kpc", "isap.sejm.gov.pl", SourceType.LEGAL_STATUTE,
                       metadata={"ustawa_id": "DU/1964/296"}),  # KPC
            make_chunk("c_upadl", "isap.sejm.gov.pl", SourceType.LEGAL_STATUTE,
                       metadata={"ustawa_id": "DU/2003/535"}),  # Prawo upadłościowe
            make_chunk("c_bankier", "bankier.pl", SourceType.ENCYCLOPEDIC),
            make_chunk("c_bezprawnik", "bezprawnik.pl", SourceType.ENCYCLOPEDIC),
            make_chunk("c_ing", "ing.pl", SourceType.ENCYCLOPEDIC),
        ]
        result = filter_chunks(chunks, policy="strict")
        assert result.kept_count == 5
        assert result.dropped_count == 5
        assert result.drop_ratio == 0.5


# === Explainer ===


class TestExplainDropReason:
    def test_eli_reason(self) -> None:
        msg = explain_drop_reason("eli_DU/1964/296", "strict")
        assert "KPC" in msg

    def test_s6_reason(self) -> None:
        msg = explain_drop_reason("s6_bankier.pl", "strict")
        assert "finance journalism" in msg.lower()

    def test_sn_chf_reason(self) -> None:
        msg = explain_drop_reason("sn_chf_content", "strict")
        assert "CHF" in msg or "frank" in msg.lower()

    def test_rf_insurance_reason(self) -> None:
        msg = explain_drop_reason("rf_pure_insurance", "strict")
        assert "insurance" in msg.lower() or "pure-insurance" in msg.lower()

    def test_unknown_reason_returns_fallback(self) -> None:
        msg = explain_drop_reason("unknown_xyz", "strict")
        assert "Unknown" in msg


# === FilterResult API ===


class TestFilterResultProperties:
    def test_kept_count_total_drop_ratio(self) -> None:
        chunks = [
            make_chunk("c1", "konsument.gov.pl", SourceType.ENCYCLOPEDIC),
            make_chunk("c2", "ing.pl", SourceType.ENCYCLOPEDIC),
            make_chunk("c3", "bankier.pl", SourceType.ENCYCLOPEDIC),
        ]
        result = filter_chunks(chunks, policy="strict")
        assert result.kept_count == 1
        assert result.dropped_count == 2
        assert result.total == 3
        assert result.drop_ratio == pytest.approx(2 / 3)

    def test_policy_recorded(self) -> None:
        result = filter_chunks([], policy="strict")
        assert result.policy == "strict"


# === Coverage: STRICT_DROP_ELI_USTAWY matches LOOSE_DROP_ELI_USTAWY structure ===


def test_loose_subset_of_strict_eli() -> None:
    """LOOSE_DROP_ELI_USTAWY musi być subset STRICT_DROP_ELI_USTAWY."""
    assert set(LOOSE_DROP_ELI_USTAWY.keys()).issubset(STRICT_DROP_ELI_USTAWY.keys())


def test_strict_drop_s6_has_known_sources() -> None:
    """Smoke: STRICT_DROP_S6_SOURCES zawiera oczekiwane domain entries."""
    expected_keys = {"bankier.pl", "money.pl", "infor.pl", "bezprawnik.pl", "ing.pl"}
    assert expected_keys.issubset(STRICT_DROP_S6_SOURCES.keys())
