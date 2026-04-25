"""Re-run topic assignment over the existing manifest.

Pulls title + relative_path + url for every row, runs assign_topics() with the
current (possibly extended) topic keywords, and writes the union into the row.
Existing topic_ids are preserved (we add, never remove).
"""
from __future__ import annotations

import csv

from common import MANIFEST_CSV, MANIFEST_FIELDS, load_manifest, append_manifest, ensure_manifest_header
from topics import assign_topics


def main() -> None:
    rows = load_manifest()
    changed = 0
    for r in rows:
        existing = set(r.get("topic_ids", "").split(";")) - {""}
        text_pool = " ".join([
            r.get("title", ""),
            r.get("relative_path", ""),
            r.get("url", ""),
            r.get("notes", ""),
        ])
        new = set(assign_topics(text_pool))
        merged = existing | new
        if merged != existing:
            r["topic_ids"] = ";".join(sorted(merged))
            changed += 1
    # rewrite manifest
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})
    print(f"retagged: {changed} rows changed (out of {len(rows)})")


if __name__ == "__main__":
    main()
