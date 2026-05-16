"""Tighten the eporady24 `umowy/47` records to consumer-only.

The umowy/47 (Umowy) category mixes consumer purchase disputes with
non-consumer matters: real estate transfers, agricultural land, donations,
employment contracts, prenups. We post-filter by:

  - keep the record if `extracted_topics` is non-empty (any consumer keyword
    hit somewhere), OR
  - keep if title contains a consumer-relevance keyword.

Records from other categories (Ochrona_konsumenta/54,
Aukcje_internetowe/82, swiadczenie_uslug_droga_elektroniczna/110) are kept
unchanged — they are inherently scoped.

Usage:
  uv run python -m scrape.legal_fora.postfilter_eporady24 `
      --in data/raw/consumer_questions_polish_2026-05-16/legal_other_polish.jsonl `
      --out data/raw/consumer_questions_polish_2026-05-16/legal_other_polish.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Keywords that, if present in the title, qualify the record as
# consumer-relevant even when extracted_topics is empty.
RELEVANCE_KEYWORDS: tuple[str, ...] = (
    "konsum",
    "reklamac",
    "rękojm",
    "rekojmi",
    "gwaranc",
    "zwrot",
    "zakup",
    "sklep",
    "sprzed",
    "sprzedawc",
    "allegro",
    "olx",
    "vinted",
    "amazon",
    "kupien",
    "kupil",
    "kupie",
    "kurier",
    "paczk",
    "inpost",
    "dpd",
    "wadliw",
    "uszkodz",
    "naprawa",
    "serwis",
    "odstąp",
    "odstapi",
    "klauzul",
    "nieuczciw",
    "uokik",
    "odszkodow",
    "umowa o świadcz",
    "umow",
    "pożyczk",
    "pozyczk",
    "kredyt konsum",
    "ubezpiecz",
    "polisa",
    "abonament",
    "operator",
    "telekom",
    "telewizor",
    "pralka",
    "laptop",
    "lodówk",
    "mebl",
    "energi",
    "prąd",
    "samoch",
    "auto",
    "rezerwac",
    "wycieczk",
    "turyst",
    "apartament",
)


def keep(rec: dict) -> bool:
    cat = rec.get("category", "")
    if cat != "umowy/47":
        return True  # other categories are scoped already
    if rec.get("extracted_topics"):
        return True
    low = rec.get("question", "").lower()
    return any(kw in low for kw in RELEVANCE_KEYWORDS)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)

    keep_n, drop_n = 0, 0
    kept_records = []
    for line in args.inp.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if keep(rec):
            kept_records.append(rec)
            keep_n += 1
        else:
            drop_n += 1

    # Re-id sequentially so question_id stays gap-free after dropping.
    for i, rec in enumerate(kept_records, 1):
        rec["question_id"] = f"eporady24_{i:05d}"

    with args.out.open("w", encoding="utf-8") as fh:
        for rec in kept_records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"kept={keep_n} dropped={drop_n} (in={args.inp}, out={args.out})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
