"""Post-fix: rerun html.unescape on `title` + `tresc` + `subtitle` w existing
articles.jsonl files dla wszystkich new_sources dirs.

Use case: scrape ran before HTML entity decoding był dodany do normalize_pl.
Tylko mutuje pola JSON — NIE re-fetcha HTML. Idempotent (drugiego runu nic nie zmieni).
"""

from __future__ import annotations

import argparse
import html
import json
import logging
from pathlib import Path

logger = logging.getLogger("scrape.new_sources.post_fix")


def fix_jsonl(path: Path) -> tuple[int, int]:
    """Fix entities in title/subtitle/tresc. Returns (records_total, records_changed)."""
    if not path.exists():
        return 0, 0
    records = []
    changed = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            orig = (r.get("title", ""), r.get("subtitle", "") or "", r.get("tresc", ""))
            new_t = html.unescape(orig[0])
            new_s = html.unescape(orig[1]) if orig[1] else None
            new_b = html.unescape(orig[2])
            if (new_t, (new_s or ""), new_b) != orig:
                changed += 1
                r["title"] = new_t
                if new_s is not None:
                    r["subtitle"] = new_s
                r["tresc"] = new_b
            records.append(r)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(records), changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("D:/diplomma/main_project/data/raw"),
        help="parent directory containing *_2026-05-16/articles.jsonl files",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    targets = sorted(args.data_dir.glob("*_2026-05-16/articles.jsonl"))
    total_changed = 0
    total_recs = 0
    for path in targets:
        n, c = fix_jsonl(path)
        if n:
            logger.info("%s: total=%d changed=%d", path.parent.name, n, c)
            total_recs += n
            total_changed += c
    logger.info("DONE: %d records total, %d changed", total_recs, total_changed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
