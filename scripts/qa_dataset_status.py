#!/usr/bin/env python3
"""QA checks for dataset manifest: duplicates and topic coverage."""

from __future__ import annotations

import argparse
import csv
import pathlib
from collections import Counter, defaultdict


def read_csv_rows(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(text: str | None) -> str:
    return (text or "").strip()


def summarize_manifest(rows: list[dict[str, str]]) -> dict[str, object]:
    by_hash = Counter(normalize(r.get("sha256")) for r in rows if normalize(r.get("sha256")))
    by_url = Counter(normalize(r.get("source_url")) for r in rows if normalize(r.get("source_url")))
    by_topic = Counter(normalize(r.get("topic_group")) for r in rows if normalize(r.get("topic_group")))

    duplicate_hashes = {h: n for h, n in by_hash.items() if n > 1}
    duplicate_urls = {u: n for u, n in by_url.items() if n > 1}

    return {
        "total_rows": len(rows),
        "unique_hashes": len(by_hash),
        "unique_urls": len(by_url),
        "duplicate_hashes": duplicate_hashes,
        "duplicate_urls": duplicate_urls,
        "by_topic_group": dict(sorted(by_topic.items())),
    }


def coverage_report(rows: list[dict[str, str]], catalog_rows: list[dict[str, str]]) -> dict[str, object]:
    catalog_ids = [normalize(r.get("topic_id")) for r in catalog_rows if normalize(r.get("topic_id"))]
    covered = set()

    for r in rows:
        topic_group = normalize(r.get("topic_group"))
        doc_id = normalize(r.get("doc_id"))
        if topic_group:
            covered.add(topic_group)
        if doc_id:
            covered.add(doc_id)

    missing = [topic_id for topic_id in catalog_ids if topic_id not in covered]

    by_priority = defaultdict(lambda: {"total": 0, "covered": 0})
    for row in catalog_rows:
        topic_id = normalize(row.get("topic_id"))
        priority = normalize(row.get("priority")) or "UNSET"
        by_priority[priority]["total"] += 1
        if topic_id and topic_id not in missing:
            by_priority[priority]["covered"] += 1

    return {
        "catalog_total": len(catalog_ids),
        "covered_count": len(catalog_ids) - len(missing),
        "missing_count": len(missing),
        "missing_topics": missing,
        "priority_coverage": dict(by_priority),
    }


def print_report(summary: dict[str, object], coverage: dict[str, object], show_missing_limit: int) -> None:
    print("=== Dataset QA ===")
    print(f"Rows in manifest: {summary['total_rows']}")
    print(f"Unique source_url: {summary['unique_urls']}")
    print(f"Unique sha256: {summary['unique_hashes']}")
    print(f"Duplicate URLs: {len(summary['duplicate_urls'])}")
    print(f"Duplicate hashes: {len(summary['duplicate_hashes'])}")

    print("\n--- Coverage ---")
    print(f"Catalog topics: {coverage['catalog_total']}")
    print(f"Covered topics: {coverage['covered_count']}")
    print(f"Missing topics: {coverage['missing_count']}")

    print("\nPriority coverage:")
    for priority, stats in sorted(coverage["priority_coverage"].items()):
        total = stats["total"]
        covered = stats["covered"]
        pct = (covered / total * 100) if total else 0.0
        print(f"- {priority}: {covered}/{total} ({pct:.1f}%)")

    missing_topics = coverage["missing_topics"]
    if missing_topics:
        print(f"\nFirst {show_missing_limit} missing topics:")
        for topic in missing_topics[:show_missing_limit]:
            print(f"- {topic}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QA checks for manifest duplicates and topic coverage")
    parser.add_argument("--manifest", type=pathlib.Path, default=pathlib.Path("data/manifests/manifest_l1.csv"))
    parser.add_argument("--topic-catalog", type=pathlib.Path, default=pathlib.Path("data/seeds/topic_catalog.csv"))
    parser.add_argument("--missing-limit", type=int, default=25)
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 if any topic from catalog is missing")
    args = parser.parse_args()

    manifest_rows = read_csv_rows(args.manifest)
    catalog_rows = read_csv_rows(args.topic_catalog)

    summary = summarize_manifest(manifest_rows)
    coverage = coverage_report(manifest_rows, catalog_rows)

    print_report(summary, coverage, show_missing_limit=args.missing_limit)

    if args.strict and coverage["missing_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
