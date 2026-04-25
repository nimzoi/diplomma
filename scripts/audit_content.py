"""Content sanity audit for every PDF in the dataset.

For each manifest row:
  1. extract first 2 pages of text via `pdftotext`
  2. measure: bytes_text, polish_diacritics_ratio, recognizable_topic_keywords
  3. flag rows as: ok / image_pdf / off_topic / suspicious / unreadable

Writes the result back into the sidecar JSON as `content_audit` and
into a separate CSV report `data/content_audit.csv` for review.

This catches:
  - PDFs that are image-only (OCR needed)
  - PDFs whose actual content does NOT match the act/topic the URL implied
  - corrupted / truncated PDFs that pdftotext cannot parse
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV, MANIFEST_FIELDS, load_manifest

POLISH_DIACRITICS = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
JDG_VOCAB = (
    "ustawa", "rozporządzenie", "art.", "ust.", "pkt", "podatek",
    "podatkow", "ubezpiec", "skladk", "składk", "działaln",
    "umowa", "pracown", "vat", "pit", "kpir", "ksef", "rodo",
    "ochrona", "danych", "kodeks", "obowiązuj",
)


def pdftotext(path: Path, pages: int = 12) -> str:
    """Extract text from up to `pages` pages (covers TOC + a few content pages)."""
    try:
        out = subprocess.run(
            ["pdftotext", "-l", str(pages), str(path), "-"],
            capture_output=True, timeout=30,
        )
        return out.stdout.decode("utf-8", errors="replace")
    except Exception:
        return ""


def audit(text: str) -> dict:
    n = len(text)
    if n == 0:
        return {"flag": "unreadable", "chars": 0, "diacritics_ratio": 0.0, "vocab_hits": 0}
    diacr = sum(1 for c in text if c in POLISH_DIACRITICS)
    diacr_ratio = diacr / max(n, 1)
    blob = text.lower()
    vocab_hits = sum(1 for w in JDG_VOCAB if w in blob)

    # Looser thresholds since we now sample 12 pages instead of 3:
    # < 500 chars across 12 pages → image-only PDF
    # diacritics ratio < 0.003 AND > 1000 chars → likely non-Polish (English brochure)
    # < 2 vocab hits AND > 1000 chars → likely off-topic
    if n < 500:
        flag = "image_pdf"
    elif diacr_ratio < 0.003 and n > 1000:
        flag = "low_polish"
    elif vocab_hits < 2 and n > 1000:
        flag = "off_topic"
    else:
        flag = "ok"
    return {
        "flag": flag,
        "chars": n,
        "diacritics_ratio": round(diacr_ratio, 4),
        "vocab_hits": vocab_hits,
    }


def extract_text_for_audit(path: Path) -> str:
    """Extract text by file type."""
    suf = path.suffix.lower()
    if suf == ".pdf":
        return pdftotext(path)
    if suf in (".html", ".htm"):
        try:
            html = path.read_text(encoding="utf-8", errors="replace")
            no_tags = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
            no_tags = re.sub(r"<style[^>]*>.*?</style>", " ", no_tags, flags=re.S | re.I)
            no_tags = re.sub(r"<[^>]+>", " ", no_tags)
            return re.sub(r"\s+", " ", no_tags)
        except Exception:
            return ""
    if suf == ".docx":
        # Simple unzip of word/document.xml
        try:
            import zipfile
            with zipfile.ZipFile(path) as z:
                with z.open("word/document.xml") as f:
                    xml = f.read().decode("utf-8", errors="replace")
            no_tags = re.sub(r"<[^>]+>", " ", xml)
            return re.sub(r"\s+", " ", no_tags)
        except Exception:
            return ""
    return ""


def main() -> None:
    rows = load_manifest()
    audit_csv = DATA_DIR / "content_audit.csv"
    out_rows = []
    flags_count: dict[str, int] = {}
    for r in rows:
        path = DATA_DIR / r["relative_path"]
        if not path.exists():
            ar = {"flag": "missing", "chars": 0, "diacritics_ratio": 0.0, "vocab_hits": 0}
        else:
            text = extract_text_for_audit(path)
            ar = audit(text)
        flags_count[ar["flag"]] = flags_count.get(ar["flag"], 0) + 1
        out_rows.append({
            "relative_path": r["relative_path"],
            "source": r["source"],
            "layer": r["layer"],
            "title": (r["title"] or "")[:100],
            **ar,
        })
        # update sidecar JSON
        sidecar = path.with_suffix(path.suffix + ".meta.json")
        if sidecar.exists():
            try:
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
                meta["content_audit"] = ar
                sidecar.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass

    with audit_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["relative_path", "source", "layer", "title",
                                            "flag", "chars", "diacritics_ratio", "vocab_hits"])
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"audit complete: {flags_count}")
    print(f"wrote {audit_csv}")


if __name__ == "__main__":
    main()
