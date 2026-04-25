"""Build human-readable source registry from manifest.csv.

Output: data/SOURCES.md — markdown table for human review.
Each row: # | source | title | URL | format | layer | topic_ids | size | quality_flag
"""
from __future__ import annotations

import csv
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV

OUT = DATA_DIR / "SOURCES.md"


def fmt_size(b: int) -> str:
    if b > 1_048_576:
        return f"{b/1_048_576:.1f} MB"
    if b > 1024:
        return f"{b/1024:.0f} KB"
    return f"{b} B"


def main() -> None:
    all_rows = list(csv.DictReader(MANIFEST_CSV.open(encoding="utf-8")))
    rows = [r for r in all_rows if r.get("quality_flag", "accepted") == "accepted"]
    quarantined = [r for r in all_rows if r.get("quality_flag") == "quarantine"]
    rows.sort(key=lambda r: (r["source"], r["layer"], r["title"][:40]))

    lines: list[str] = []
    lines.append("# Source registry — JDG chatbot dataset")
    lines.append("")
    lines.append(f"**Total documents (accepted): {len(rows)}**")
    if quarantined:
        lines.append(f"**Quarantined (excluded from production): {len(quarantined)}**")
    lines.append("")
    lines.append("Auto-generated from `data/manifest.csv` via `scripts/build_source_registry.py`.")
    lines.append("Production view shows only `quality_flag=accepted` rows.")
    lines.append("Use this file for human review of dataset quality / relevance.")
    lines.append("")

    # Per-source summary
    from collections import Counter
    by_src = Counter(r["source"] for r in rows)
    by_fmt = Counter(r["format"] for r in rows)
    by_layer = Counter(r["layer"] for r in rows)

    lines.append("## Summary")
    lines.append("")
    lines.append("| Source | Count |")
    lines.append("|---|---:|")
    for s, c in by_src.most_common():
        lines.append(f"| `{s}` | {c} |")
    lines.append("")
    lines.append(f"**Formats:** {dict(by_fmt.most_common())}  ")
    lines.append(f"**Layers:** {dict(by_layer.most_common())}")
    lines.append("")

    # Group by source for the detailed table
    by_source: dict[str, list[dict]] = {}
    for r in rows:
        by_source.setdefault(r["source"], []).append(r)

    for source in sorted(by_source.keys()):
        srows = by_source[source]
        lines.append(f"## {source} ({len(srows)} docs)")
        lines.append("")
        lines.append("| # | Title | URL | Format | Layer | Topics | Size | Quality |")
        lines.append("|---|---|---|---|---|---|---:|---|")
        for i, r in enumerate(srows, 1):
            title = (r.get("title") or "").replace("|", "\\|").replace("\n", " ")[:120]
            url = r.get("url", "")
            url_short = url[:80] + ("…" if len(url) > 80 else "")
            fmt = r.get("format", "")
            layer = r.get("layer", "")
            topics = (r.get("topic_ids") or "").replace(";", ", ")[:80]
            size = fmt_size(int(r.get("bytes", 0) or 0))
            qual = r.get("quality_flag", "")
            lines.append(f"| {i} | {title} | [{url_short}]({url}) | {fmt} | {layer} | {topics} | {size} | {qual} |")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
