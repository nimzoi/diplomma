"""Drop pure-form PDFs from podatki.gov.pl + a few other quality issues
revealed by deep content audit (random sample of 27 docs).

Drop categories:
1. podatki blank tax-form PDFs (PIT-2, PIT-4R, PIT-8C, ... pdfs whose first
   page is just the POLTAX form-fill template) — they have no informational
   content for a chatbot knowledge base.
2. PIP files explicitly off-topic for JDG: school accidents, construction
   site checklists.
3. biznes_gov mojibake / duplicate items.

Keep blank PIT-36/PIT-37/PIT-28 brochures (these are full informational
broszury, not just blank forms) and PIT-2/PIT-2A title (those go via
broszura-... naming).
"""
from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV, MANIFEST_FIELDS, load_manifest

FORM_RE = re.compile(r"POLA JASNE|WYPEŁNIA P[ŁL]ATNIK|WYPEŁNIA PODATNIK|WYPEŁNIA URZĄD|POLTAX|WYPEŁNIĆ DUŻYMI", re.I)

EXPLICIT_DROPS = [
    "raw/pip/wypadki-w-szkole.pdf",
    "raw/biznes_gov/bizgov_zalacznik_1_pelnomocncitwo_do_skladania_deklaracji_w_wersji_papierowej.pdf",
    "raw/biznes_gov/bizgov_Lista-uprawnie_.pdf",
]


def is_pure_form(p: Path) -> bool:
    if not p.exists():
        return False
    try:
        out = subprocess.run(
            ["pdftotext", "-l", "1", str(p), "-"],
            capture_output=True, timeout=10,
        )
    except Exception:
        return False
    text = out.stdout.decode("utf-8", "replace")
    return bool(FORM_RE.search(text))


def main() -> None:
    rows = load_manifest()
    keep = []
    dropped = []
    for r in rows:
        rel = r.get("relative_path", "")
        path = DATA_DIR / rel
        drop_reason = None

        if rel in EXPLICIT_DROPS:
            drop_reason = "explicit drop"
        elif r.get("source") == "podatki":
            # Skip broszura — those are real informational docs
            t = r.get("title", "").lower()
            if "broszura" in t or "informator" in t or "poradnik" in t:
                pass
            elif is_pure_form(path):
                drop_reason = "pure tax form (blank fillable PDF)"

        if drop_reason:
            dropped.append((rel, drop_reason))
            for q in (path, path.with_suffix(path.suffix + ".meta.json")):
                if q.exists():
                    q.unlink()
        else:
            keep.append(r)

    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in keep:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})
    print(f"dropped {len(dropped)} files; manifest now {len(keep)} rows")
    for p, why in dropped[:10]:
        print(f"  - {p}: {why}")


if __name__ == "__main__":
    main()
