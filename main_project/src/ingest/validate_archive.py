"""Quick spot-check validator for forum HTML archive.

Reads ``_archive/_manifest.json`` and verifies:
  - every entry's archive file actually exists on disk
  - sha256 matches what is recorded
  - HTML/JSON files contain expected Polish/structural markers
  - reports per-domain success rate, size totals, and any anomalies

Usage::

    cd D:\\diplomma\\main_project
    $env:PYTHONPATH = "src"
    uv run python -m ingest.validate_archive
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def domain_health_markers() -> dict[str, list[str]]:
    """For each domain, plausible substring markers we expect to find."""
    return {
        "e_prawnik": ["<title>", "e-prawnik", "</html>"],
        "forumprawne": ["<title>", "ForumPrawne", "</html>"],
        "reddit": ['"kind":', '"data":', '"title"'],
        "legal_other": ["<title>", "</html>"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=Path(
            "D:/diplomma/main_project/data/raw/"
            "consumer_questions_polish_2026-05-16/_archive"
        ),
    )
    args = parser.parse_args(argv)

    manifest_path = args.archive_dir / "_manifest.json"
    if not manifest_path.exists():
        print(f"missing manifest: {manifest_path}", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries: dict[str, dict] = manifest.get("entries", {})
    print(f"manifest entries: {len(entries)}")

    markers = domain_health_markers()
    per_domain: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "total": 0,
            "ok": 0,
            "missing_file": 0,
            "sha256_mismatch": 0,
            "marker_missing": 0,
            "error_recorded": 0,
            "skipped": 0,  # error rows we just count
            "min_size": 10**12,
            "max_size": 0,
            "sum_size": 0,
        }
    )

    samples_bad: list[tuple[str, str, str]] = []
    samples_small: list[tuple[str, str, int]] = []

    for qid, e in entries.items():
        dom = e.get("domain") or "unknown"
        p = per_domain[dom]
        p["total"] += 1

        if e.get("error"):
            p["error_recorded"] += 1
            continue

        rel = e.get("archive_file")
        if not rel:
            samples_bad.append((qid, dom, "no archive_file"))
            p["missing_file"] += 1
            continue
        path = args.archive_dir / rel
        if not path.exists():
            samples_bad.append((qid, dom, f"missing: {rel}"))
            p["missing_file"] += 1
            continue

        actual_sha = sha256_file(path)
        if e.get("sha256") and actual_sha != e["sha256"]:
            samples_bad.append((qid, dom, "sha256 mismatch"))
            p["sha256_mismatch"] += 1
            continue

        size = path.stat().st_size
        p["sum_size"] += size
        p["min_size"] = min(p["min_size"], size)
        p["max_size"] = max(p["max_size"], size)

        # marker check
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            text = ""
        expected = markers.get(dom, [])
        if expected and not all(m in text for m in expected):
            p["marker_missing"] += 1
            if len(samples_bad) < 20:
                samples_bad.append((qid, dom, "marker missing"))
            continue

        if size < 2000:
            samples_small.append((qid, dom, size))

        p["ok"] += 1

    print()
    print(f"{'domain':<14} {'total':>6} {'ok':>6} {'miss':>6} {'sha!':>6} "
          f"{'no-mk':>6} {'err':>6} {'avg-kb':>7} {'min-kb':>7} {'max-kb':>7}")
    print("-" * 90)
    overall_ok = 0
    overall_total = 0
    for dom, p in sorted(per_domain.items()):
        avg_kb = round(p["sum_size"] / max(p["ok"], 1) / 1024.0, 1)
        min_kb = (
            round(p["min_size"] / 1024.0, 1) if p["min_size"] < 10**12 else 0.0
        )
        max_kb = round(p["max_size"] / 1024.0, 1)
        print(
            f"{dom:<14} {p['total']:>6} {p['ok']:>6} "
            f"{p['missing_file']:>6} {p['sha256_mismatch']:>6} "
            f"{p['marker_missing']:>6} {p['error_recorded']:>6} "
            f"{avg_kb:>7} {min_kb:>7} {max_kb:>7}"
        )
        overall_ok += p["ok"]
        overall_total += p["total"]

    print()
    print(
        f"overall: {overall_ok}/{overall_total} healthy ({100 * overall_ok / max(overall_total, 1):.1f}%)"
    )
    if samples_bad:
        print()
        print(f"first {len(samples_bad)} anomalies:")
        for qid, dom, reason in samples_bad[:20]:
            print(f"  [{dom}] {qid}: {reason}")
    if samples_small:
        print()
        print(f"{len(samples_small)} files < 2 KB (sample):")
        for qid, dom, sz in samples_small[:10]:
            print(f"  [{dom}] {qid}: {sz} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
