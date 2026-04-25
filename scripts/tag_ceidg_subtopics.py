"""Manually tag CEIDG-related laws with the 3 sub-topics that the keyword
matcher missed (wznowienie / zamkniecie / zmiana_wpisu).

Reason: these are operations defined inside the Prawo przedsiębiorców /
CEIDG acts I already have, but their headings don't include the literal
keywords my regex looks for.
"""
from __future__ import annotations

import csv

from common import MANIFEST_CSV, MANIFEST_FIELDS, load_manifest

TARGET_ELI = {
    "DU/2018/646",   # Prawo przedsiębiorców (oryg.)
    "DU/2025/1480",  # Prawo przedsiębiorców (tekst jednolity)
    "DU/2026/30",    # CEIDG (tekst jednolity)
    "DU/2026/507",   # CEIDG (zmiana 2026)
}
EXTRA_TOPICS = {"ceidg_wznowienie", "ceidg_zamkniecie", "ceidg_zmiana_wpisu"}


def main() -> None:
    rows = load_manifest()
    changed = 0
    for r in rows:
        if r.get("eli_id") not in TARGET_ELI:
            continue
        existing = set(r.get("topic_ids", "").split(";")) - {""}
        merged = existing | EXTRA_TOPICS
        if merged != existing:
            r["topic_ids"] = ";".join(sorted(merged))
            changed += 1
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})
    print(f"tagged {changed} CEIDG/PrPrz rows with {EXTRA_TOPICS}")


if __name__ == "__main__":
    main()
