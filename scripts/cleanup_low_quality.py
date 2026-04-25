"""Drop documents flagged by audit_content.py as low-quality.

Drop rules (data/content_audit.csv):
  flag == "image_pdf"     and chars <= 200          -> drop (no usable text)
  flag == "low_polish"    and source != "eli"       -> drop (English-only, EU-Lex/EUR keep)
  flag == "off_topic"     and source == "pip"       -> drop (still slipped past keyword filter)
  flag == "off_topic"     and source == "podatki"   -> drop (e.g. "Pobierz" empty stubs)

Updates manifest + deletes raw + sidecars.
"""
from __future__ import annotations

import csv
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV, MANIFEST_FIELDS, load_manifest

AUDIT_CSV = DATA_DIR / "content_audit.csv"


def main() -> None:
    audit = {}
    with AUDIT_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            audit[row["relative_path"]] = row

    rows = load_manifest()
    keep = []
    dropped: list[tuple[str, str]] = []
    for r in rows:
        a = audit.get(r["relative_path"])
        if not a:
            keep.append(r)
            continue
        flag = a["flag"]
        chars = int(a.get("chars", 0))
        src = r.get("source", "")
        drop = False
        reason = ""
        if flag == "image_pdf" and chars <= 200:
            drop, reason = True, "image_pdf no text"
        elif flag == "low_polish" and src != "eli":
            drop, reason = True, "low_polish (English-only or empty stub)"
        elif flag == "off_topic" and src in ("pip", "podatki"):
            drop, reason = True, "off_topic per audit"
        if drop:
            dropped.append((r["relative_path"], reason))
            for p in (DATA_DIR / r["relative_path"], DATA_DIR / (r["relative_path"] + ".meta.json")):
                if p.exists():
                    p.unlink()
        else:
            keep.append(r)

    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in keep:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})

    print(f"dropped {len(dropped)} files; manifest now {len(keep)} rows")
    for p, why in dropped[:20]:
        print(f"  - {p}: {why}")
    if len(dropped) > 20:
        print(f"  ... +{len(dropped) - 20} more")


if __name__ == "__main__":
    main()
