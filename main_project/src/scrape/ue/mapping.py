"""UE dyrektywa konsumencka -> polska ustawa implementacyjna mapping.

Generuje `mapping.json` — strukturalny mapping per CELEX z metadata:
- polska_ustawa (ELI ID, np. "DU/2014/827")
- polska_ustawa_title
- transposition_deadline (data implementacji per dyrektywa)
- polska_implementation_date (data wejscia w zycie polskiej ustawy)

Defense argument (per task brief):
    "claim w polish jest grounded w polish ustawie ktora implementuje
    UE dyrektywe X" — mapping pozwala na cross-language cross-register
    citation chains w halu probe + verifier reasoning.

Source: DYREKTYWY config w `dyrektywy.py` + ISAP ELI metadata cross-reference.

Usage::

    uv run python -m src.scrape.ue.mapping
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Setup PYTHONPATH for direct module execution.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scrape.ue.common import TODAY, write_json  # noqa: E402
from scrape.ue.dyrektywy import DYREKTYWY  # noqa: E402

logger = logging.getLogger("scrape.ue.mapping")


# === Ground truth polska implementacja ===
# Mapping ELI -> title (krotki). Cross-referenced z scrape_eli.py UstawaConfig.
POLSKA_USTAWY_TITLES: dict[str, str] = {
    "DU/2014/827": "Ustawa o prawach konsumenta",
    "DU/2022/2337": (
        "Ustawa o zmianie ustawy o prawach konsumenta oraz ustawy "
        "Kodeks cywilny (towary cyfrowe + sprzedaz, DCD+SGD implementacja)"
    ),
    "DU/2022/2581": (
        "Ustawa o zmianie ustawy o prawach konsumenta oraz niektorych "
        "innych ustaw (Omnibus implementacja)"
    ),
    "DU/1964/93": "Kodeks cywilny",
    "DU/2000/443": (
        "Ustawa o ochronie niektorych praw konsumentow oraz odpowiedzialnosci "
        "za szkode wyrzadzona przez produkt niebezpieczny (uchylona przez DU/2014/827; "
        "wprowadzila art. 385^1 KC implementujace dyrektywe 93/13/EWG)"
    ),
    "DU/2007/1206": "Ustawa o przeciwdzialaniu nieuczciwym praktykom rynkowym",
    "DU/2011/126": "Ustawa o kredycie konsumenckim",
    "DU/2007/331": "Ustawa o ochronie konkurencji i konsumentow",
    "DU/2011/1175": "Ustawa o uslugach platniczych",
    "DU/2016/1823": "Ustawa o pozasadowym rozwiazywaniu sporow konsumenckich",
}


# === Polska implementation dates (kiedy polska ustawa weszla w zycie) ===
POLSKA_IMPLEMENTATION_DATES: dict[str, str] = {
    "DU/2014/827": "2014-12-25",
    "DU/2022/2337": "2023-01-01",  # weszla w zycie 2023-01-01
    "DU/2022/2581": "2023-01-01",  # Omnibus PL — 2023-01-01
    "DU/1964/93": "1965-01-01",  # KC oryginal; klauzule abuzywne dodano 2000-07-01 via DU/2000/443
    "DU/2000/443": "2000-07-01",
    "DU/2007/1206": "2007-12-21",
    "DU/2011/126": "2011-12-18",
    "DU/2007/331": "2007-04-21",
    "DU/2011/1175": "2011-10-24",
    "DU/2016/1823": "2017-01-10",
}


def build_mapping() -> dict[str, Any]:
    """Compose dyrektywa -> polska ustawa mapping z DYREKTYWY config."""
    out: dict[str, Any] = {}
    for cfg in DYREKTYWY:
        polska = cfg.polska_implementacja  # ELI ID
        polska_title = (
            POLSKA_USTAWY_TITLES.get(polska, "(brak — w trakcie transpozycji)")
            if polska
            else "(brak — w trakcie transpozycji)"
        )
        polska_date = POLSKA_IMPLEMENTATION_DATES.get(polska) if polska else None

        out[cfg.celex_id] = {
            "celex_id": cfg.celex_id,
            "direktywa_id": cfg.direktywa_id,
            "title_pl": cfg.title_pl,
            "data_publikacji": cfg.data_publikacji,
            "data_wejscia_w_zycie": cfg.data_wejscia_w_zycie,
            "transposition_deadline": cfg.data_implementacji,
            "polska_ustawa": polska,
            "polska_ustawa_title": polska_title,
            "polska_implementation_date": polska_date,
            "notes": cfg.notes,
        }
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).resolve().parents[3]
            / "data"
            / "raw"
            / "ue_polska_implementacja_2026-05-16"
            / "mapping.json"
        ),
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if not args.verbose else logging.DEBUG,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
    )

    mapping = build_mapping()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(mapping, out_path)

    # Sidecar README explanation
    readme = out_path.parent / "README.md"
    readme.write_text(
        f"""# UE dyrektywa -> polska ustawa implementacyjna mapping

Generated: {TODAY}

## Cel
Mapping kazdej UE dyrektywy konsumenckiej (CELEX id) na polska ustawe implementacyjna
(ELI id z systemu ISAP).

## Defense argument
"Claim w polish jest grounded w polish ustawie ktora implementuje UE dyrektywe X"
— mapping pozwala na cross-language cross-register citation chains w halu probe
+ verifier reasoning.

## Struktura
`mapping.json` — dict `{{ celex_id: {{ celex_id, direktywa_id, title_pl,
data_publikacji, data_wejscia_w_zycie, transposition_deadline, polska_ustawa,
polska_ustawa_title, polska_implementation_date, notes }} }}`

## Kompletność
{len(mapping)}/8 dyrektyw zmapowanych. Dyrektywa 2023/2225 (CCD II) bez polskiej
ustawy — transpozycja w toku (deadline 20 listopada 2025).

## Źródła
- Daty implementacji: EUR-Lex per-directive metadata
- ELI ID polskich ustaw: cross-reference z ISAP api.sejm.gov.pl/eli
- Date wejscia w zycie polskich ustaw: ISAP `data_wejscia_w_zycie` field

## License
- UE dyrektywy: (c) UE, free reuse per Decyzja 2011/833/UE (attribution req.)
- Polskie ustawy: art. 4 ust. 1 ustawy o prawie autorskim (DU/1994/83) — akty
  normatywne nie sa przedmiotem prawa autorskiego (public domain de facto)
""",
        encoding="utf-8",
    )
    logger.info("wrote -> %s", readme)

    logger.info("DONE — %d directives mapped", len(mapping))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
