"""Seed coverage_51_topics.csv with the 51 topics and source hints.

Run once at the start of data collection. Updated later by build_coverage_report.py
based on the actual manifest contents.
"""
from __future__ import annotations

import csv

from common import MANIFESTS_DIR
from topics import TOPICS

# Hint mapping: topic_id -> (preferred_l1_source, preferred_l2_source)
HINTS: dict[str, tuple[str, str]] = {
    # ZUS
    "zus_ulga_na_start": ("Prawo przedsiebiorcow art. 18", "biznes.gov.pl/zus"),
    "zus_preferencyjny": ("Ustawa o systemie ub. spol. art. 18a", "zus.pl poradniki"),
    "zus_maly_zus_plus": ("Ustawa o systemie ub. spol. art. 18c", "zus.pl mzp"),
    "zus_wakacje_skladkowe": ("Ustawa o systemie ub. spol. (zmiana 2024)", "zus.pl rws"),
    "zus_skladka_zdrowotna_jdg": ("Ustawa o swiad. zdrow./PIT", "zus.pl skladka zdrowotna"),
    "zus_zua_zwua_dra": ("Rozp. zgloszenia ub. spol.", "zus.pl druki"),
    "zus_zasilek_chorobowy_jdg": ("Ustawa o swiadczeniach pien. z ub. chor.", "zus.pl zasilek"),
    "zus_podstawa_wymiaru": ("Ustawa o systemie ub. spol.", "zus.pl skladki-wskazniki"),
    "zus_zawieszenie_dzialalnosci": ("Prawo przedsiebiorcow art. 22-25", "biznes.gov.pl"),
    "zus_emerytura_jdg": ("Ustawa o emeryt. i rentach z FUS", "zus.pl"),

    # PIT
    "pit_skala": ("Ustawa o PIT art. 27", "podatki.gov.pl PIT-36"),
    "pit_liniowy": ("Ustawa o PIT art. 30c", "podatki.gov.pl PIT-36L"),
    "pit_ryczalt": ("Ustawa o ryczalcie", "podatki.gov.pl PIT-28"),
    "pit_stawki_ryczalt_pkd": ("Zalacznik do ustawy o ryczalcie", "podatki.gov.pl"),
    "pit_karta_podatkowa": ("Ustawa o ryczalcie (karta)", "podatki.gov.pl"),
    "pit_ip_box": ("Ustawa o PIT art. 30ca-30cb", "podatki.gov.pl ip box"),
    "pit_kup": ("Ustawa o PIT art. 22", "podatki.gov.pl"),
    "pit_amortyzacja": ("Rozp. wykaz stawek amort.", "podatki.gov.pl"),
    "pit_kpir": ("Rozp. KPiR", "podatki.gov.pl ksiegowosc"),
    "pit_ewidencja_ryczalt": ("Rozp. ewidencja ryczalt", "podatki.gov.pl"),
    "pit_roczny": ("Ustawa o PIT", "podatki.gov.pl kalendarz"),

    # VAT
    "vat_rejestracja": ("Ustawa o VAT art. 96", "podatki.gov.pl VAT-R"),
    "vat_zwolnienie_200k": ("Ustawa o VAT art. 113", "podatki.gov.pl"),
    "vat_jpk": ("Rozp. JPK_V7", "podatki.gov.pl JPK"),
    "vat_ksef": ("Ustawa o VAT (KSeF)", "podatki.gov.pl KSeF"),
    "vat_stawki": ("Ustawa o VAT zal.", "podatki.gov.pl matryca"),
    "vat_ue": ("Ustawa o VAT", "podatki.gov.pl VAT-UE"),
    "vat_marza": ("Ustawa o VAT art. 119-120", "podatki.gov.pl"),
    "vat_biala_lista": ("Ustawa o VAT art. 96b", "podatki.gov.pl/biala-lista"),

    # CEIDG
    "ceidg_rejestracja": ("Prawo przedsiebiorcow", "biznes.gov.pl ceidg-1"),
    "ceidg_pkd": ("Rozp. PKD 2007", "biznes.gov.pl/pkd"),
    "ceidg_zawieszenie": ("Prawo przedsiebiorcow art. 22-25", "biznes.gov.pl"),
    "ceidg_wznowienie": ("Prawo przedsiebiorcow", "biznes.gov.pl"),
    "ceidg_zamkniecie": ("Prawo przedsiebiorcow", "biznes.gov.pl"),
    "ceidg_zmiana_wpisu": ("Prawo przedsiebiorcow", "biznes.gov.pl"),
    "ceidg_dzialalnosc_nierejestrowana": ("Prawo przedsiebiorcow art. 5", "biznes.gov.pl"),

    # KP
    "kp_umowa_o_prace": ("Kodeks pracy", "pip.gov.pl"),
    "kp_umowa_zlecenie": ("Kodeks cywilny art. 734", "pip.gov.pl"),
    "kp_umowa_o_dzielo": ("Kodeks cywilny art. 627", "pip.gov.pl"),
    "kp_czas_pracy": ("Kodeks pracy dzial VI", "pip.gov.pl"),
    "kp_urlop": ("Kodeks pracy dzial VII", "pip.gov.pl"),
    "kp_wypowiedzenie": ("Kodeks pracy art. 30-36", "pip.gov.pl"),
    "kp_swiadectwo_pracy": ("Rozp. swiadectwo pracy", "pip.gov.pl"),
    "kp_bhp_biuro": ("Kodeks pracy dzial X", "pip.gov.pl bhp biuro"),

    # RODO
    "rodo_mala_firma": ("RODO 2016/679", "uodo.gov.pl"),
    "rodo_rejestr_czynnosci": ("RODO art. 30", "uodo.gov.pl rcp"),
    "rodo_iod": ("RODO art. 37-39", "uodo.gov.pl iod"),
    "rodo_klauzula_informacyjna": ("RODO art. 13-14", "uodo.gov.pl"),
    "rodo_monitoring": ("Kodeks pracy art. 22[2]", "uodo.gov.pl monitoring"),
    "rodo_naruszenie": ("RODO art. 33-34", "uodo.gov.pl naruszenie"),
    "rodo_rekrutacja": ("RODO + KP", "uodo.gov.pl rekrutacja"),
}


def main() -> None:
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    out = MANIFESTS_DIR / "coverage_51_topics.csv"
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["topic_id", "group", "l1_hint", "l2_hint", "keywords"])
        for tid, grp, kws in TOPICS:
            l1, l2 = HINTS.get(tid, ("", ""))
            writer.writerow([tid, grp, l1, l2, "|".join(kws)])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
