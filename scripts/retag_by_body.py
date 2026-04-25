"""Re-tag manifest rows using their actual HTML/PDF body text instead of
just title. Biznes.gov rendered HTML pages have proper Polish content
that mentions specific topics — use that for tagging.
"""
from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV, MANIFEST_FIELDS, load_manifest
from topics import assign_topics


def extract_body_text(path: Path) -> str:
    suf = path.suffix.lower()
    if suf == ".pdf":
        try:
            out = subprocess.run(
                ["pdftotext", "-l", "12", str(path), "-"],
                capture_output=True, timeout=20,
            )
            return out.stdout.decode("utf-8", errors="replace")
        except Exception:
            return ""
    if suf in (".html", ".htm"):
        try:
            html = path.read_text(encoding="utf-8", errors="replace")
            no_tags = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
            no_tags = re.sub(r"<style[^>]*>.*?</style>", " ", no_tags, flags=re.S | re.I)
            no_tags = re.sub(r"<[^>]+>", " ", no_tags)
            return re.sub(r"\s+", " ", no_tags)
        except Exception:
            return ""
    return ""


def main() -> None:
    rows = load_manifest()
    changed = 0
    for r in rows:
        path = DATA_DIR / r.get("relative_path", "")
        if not path.exists():
            continue
        body = extract_body_text(path)
        if not body:
            continue
        # Use first 8000 chars as fingerprint
        sample = body[:8000]
        existing = set((r.get("topic_ids") or "").split(";")) - {""}
        # Tag from title + body sample + url
        new = set(assign_topics(r.get("title", ""), sample, r.get("url", ""), r.get("relative_path", "")))
        if not new:
            continue
        merged = existing | new
        # Special case: if rendered HTML body strongly matches a NEW topic
        # but existing has a default fallback (ceidg_rejestracja with no real
        # match), replace.
        # But default we just merge so we don't lose previously-tagged.
        if merged != existing:
            r["topic_ids"] = ";".join(sorted(merged))
            changed += 1

    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})

    print(f"retagged by body: {changed} rows")


if __name__ == "__main__":
    main()
