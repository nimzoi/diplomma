"""Assign topic_ids to ELI rows that ended up with no auto-detected topic.

These are general legal acts (Ordynacja podatkowa, KKS, KPA, KRS,
nieuczciwa konkurencja, rachunkowosc, BHP szkolenia, Wykaz amortyzacyjny)
that touch many JDG topics indirectly — give them a broad set so they
appear in retrieval for the right questions.
"""
from __future__ import annotations

import csv

from common import MANIFEST_CSV, MANIFEST_FIELDS, load_manifest

MANUAL = {
    "DU/2025/1417": ["pit_kpir", "vat_jpk", "vat_rejestracja"],          # Ordynacja podatkowa zmiana
    "DU/2025/111":  ["pit_kpir", "vat_jpk", "vat_rejestracja"],          # Ordynacja podatkowa tekst jednolity
    "DU/2024/628":  ["pit_skala", "vat_jpk"],                            # Kodeks karny skarbowy tekst jednolity
    "DU/2025/633":  ["pit_skala", "vat_jpk"],                            # KKS obwieszczenie
    "DU/2025/869":  ["ceidg_rejestracja", "ceidg_zmiana_wpisu"],         # Ustawa o KRS tekst jednolity
    "DU/2025/1691": ["ceidg_rejestracja", "ceidg_zmiana_wpisu",
                     "ceidg_zawieszenie", "ceidg_zamkniecie"],           # KPA tekst jednolity
    "DU/2026/85":   ["ceidg_rejestracja"],                               # Nieuczciwa konkurencja
    "DU/2026/522":  ["pit_kpir", "pit_amortyzacja"],                     # Rachunkowosc
    "DU/2025/1640": ["kp_bhp_biuro"],                                    # BHP szkolenia
}


def main() -> None:
    rows = load_manifest()
    changed = 0
    for r in rows:
        eli = r.get("eli_id", "")
        if eli in MANUAL:
            existing = set(r.get("topic_ids", "").split(";")) - {""}
            merged = existing | set(MANUAL[eli])
            if merged != existing:
                r["topic_ids"] = ";".join(sorted(merged))
                changed += 1
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})
    print(f"manually tagged {changed} rows")


if __name__ == "__main__":
    main()
