"""Extract plain-text corpus from downloaded JDG source documents.

Input:
  - data/manifest.csv
  - data/raw/**/*.{pdf,html,docx}
  - optionally data/content_audit.csv for quality flags

Output:
  - data/text/<source>/<original-stem>.txt
  - data/text/text_manifest.csv

This script intentionally performs only deterministic text extraction. It does
not chunk, embed, deduplicate semantically, or build a vector index. Those steps
belong to the retrieval pipeline.

Requirements:
  - stdlib only for HTML/DOCX
  - `pdftotext` CLI for PDFs, e.g. poppler-utils on Linux

Usage:
  python3 scripts/extract_text_corpus.py
  python3 scripts/extract_text_corpus.py --only-ok
  python3 scripts/extract_text_corpus.py --limit 10
  python3 scripts/extract_text_corpus.py --force
"""
from __future__ import annotations

import argparse
import csv
import html
import re
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path

from common import DATA_DIR, load_manifest

TEXT_DIR = DATA_DIR / "text"
TEXT_MANIFEST = TEXT_DIR / "text_manifest.csv"
CONTENT_AUDIT = DATA_DIR / "content_audit.csv"

TEXT_MANIFEST_FIELDS = [
    "id",
    "source",
    "layer",
    "format",
    "topic_ids",
    "title",
    "raw_relative_path",
    "text_relative_path",
    "chars",
    "words",
    "audit_flag",
    "extraction_status",
    "error",
]

SKIP_TAGS = {"script", "style", "noscript", "svg", "canvas"}


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        if tag.lower() in SKIP_TAGS:
            self._skip_depth += 1
        if tag.lower() in {"p", "br", "li", "section", "article", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        if tag.lower() in SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        if tag.lower() in {"p", "li", "section", "article", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if not self._skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        return normalize_text(" ".join(self.parts))


def normalize_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def extract_pdf(path: Path) -> tuple[str, str]:
    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        return "", "pdftotext CLI not found; install poppler-utils"
    except subprocess.TimeoutExpired:
        return "", "pdftotext timeout"

    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        return "", err or f"pdftotext failed with return code {proc.returncode}"
    return normalize_text(proc.stdout.decode("utf-8", errors="replace")), ""


def extract_html(path: Path) -> tuple[str, str]:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
        parser = VisibleTextParser()
        parser.feed(raw)
        return parser.text(), ""
    except Exception as exc:  # pragma: no cover - defensive corpus tooling
        return "", f"{type(exc).__name__}: {exc}"


def extract_docx(path: Path) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml").decode("utf-8", errors="replace")
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<[^>]+>", " ", xml)
        return normalize_text(xml), ""
    except Exception as exc:  # pragma: no cover - defensive corpus tooling
        return "", f"{type(exc).__name__}: {exc}"


def extract_text(path: Path, fmt: str) -> tuple[str, str]:
    suffix = path.suffix.lower().lstrip(".")
    kind = (fmt or suffix).lower()
    if kind == "pdf" or suffix == "pdf":
        return extract_pdf(path)
    if kind in {"html", "htm"} or suffix in {"html", "htm"}:
        return extract_html(path)
    if kind == "docx" or suffix == "docx":
        return extract_docx(path)
    return "", f"unsupported format: {fmt or suffix}"


def safe_text_path(row: dict) -> Path:
    raw_rel = Path(row["relative_path"])
    source = row.get("source") or "unknown"
    raw_name = raw_rel.name
    # Handles names like file.pdf, file.html, file.docx.
    stem = Path(raw_name).stem
    return TEXT_DIR / source / f"{stem}.txt"


def load_audit_flags() -> dict[str, str]:
    if not CONTENT_AUDIT.exists():
        return {}
    with CONTENT_AUDIT.open("r", encoding="utf-8", newline="") as fh:
        return {row["relative_path"]: row.get("flag", "") for row in csv.DictReader(fh)}


def write_text_manifest(rows: list[dict]) -> None:
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    with TEXT_MANIFEST.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=TEXT_MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract plain text from data/raw documents.")
    parser.add_argument("--only-ok", action="store_true", help="Extract only rows with content_audit flag == ok.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing text files.")
    parser.add_argument("--limit", type=int, default=0, help="Process only first N manifest rows, useful for smoke tests.")
    args = parser.parse_args()

    manifest = load_manifest()
    audit_flags = load_audit_flags()
    out_rows: list[dict] = []
    processed = 0

    for row in manifest:
        raw_rel = row.get("relative_path", "")
        if not raw_rel:
            continue
        audit_flag = audit_flags.get(raw_rel, "")
        if args.only_ok and audit_flag and audit_flag != "ok":
            continue

        raw_path = DATA_DIR / raw_rel
        text_path = safe_text_path(row)
        text_rel = text_path.relative_to(DATA_DIR).as_posix()
        text_path.parent.mkdir(parents=True, exist_ok=True)

        status = "ok"
        error = ""
        text = ""
        if not raw_path.exists():
            status = "missing_raw"
            error = f"missing file: {raw_rel}"
        elif text_path.exists() and not args.force:
            text = text_path.read_text(encoding="utf-8", errors="replace")
            status = "exists"
        else:
            text, error = extract_text(raw_path, row.get("format", ""))
            if error:
                status = "error"
            elif not text:
                status = "empty"
            else:
                text_path.write_text(text + "\n", encoding="utf-8")

        out_rows.append({
            "id": row.get("id", ""),
            "source": row.get("source", ""),
            "layer": row.get("layer", ""),
            "format": row.get("format", ""),
            "topic_ids": row.get("topic_ids", ""),
            "title": row.get("title", ""),
            "raw_relative_path": raw_rel,
            "text_relative_path": text_rel,
            "chars": len(text),
            "words": len(re.findall(r"\w+", text, flags=re.UNICODE)),
            "audit_flag": audit_flag,
            "extraction_status": status,
            "error": error,
        })
        processed += 1
        if args.limit and processed >= args.limit:
            break

    write_text_manifest(out_rows)
    counts: dict[str, int] = {}
    for row in out_rows:
        key = row["extraction_status"]
        counts[key] = counts.get(key, 0) + 1
    print(f"processed={len(out_rows)} status={counts}")
    print(f"wrote {TEXT_MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
