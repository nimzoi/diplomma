"""Generate data/coverage_report.md from manifest.csv.

Sections:
- summary KPIs (per spec section 16)
- counts by source / layer / format
- counts by topic_id (and the 51-topic gap list)
- biggest files (sanity)
- missing/unused topics
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV
from topics import TOPICS, all_topic_ids


def main() -> None:
    all_rows: list[dict] = []
    with MANIFEST_CSV.open(encoding="utf-8") as fh:
        all_rows = list(csv.DictReader(fh))

    rows = [r for r in all_rows if r.get("quality_flag", "accepted") == "accepted"]
    quarantined = [r for r in all_rows if r.get("quality_flag") == "quarantine"]
    n = len(rows)
    by_source = Counter(r["source"] for r in rows)
    by_layer = Counter(r["layer"] for r in rows)
    by_format = Counter(r["format"] for r in rows)
    by_topic: Counter[str] = Counter()
    for r in rows:
        for t in r["topic_ids"].split(";"):
            t = t.strip()
            if t:
                by_topic[t] += 1
    covered = {t for t in by_topic if by_topic[t] > 0}
    uncovered = [t for t in all_topic_ids() if t not in covered]
    total_bytes = sum(int(r.get("bytes") or 0) for r in rows)

    biggest = sorted(rows, key=lambda r: int(r.get("bytes") or 0), reverse=True)[:10]

    out = []
    out.append("# Dataset coverage report")
    out.append("")
    out.append("Auto-generated from `data/manifest.csv`. Run `python3 scripts/build_coverage_report.py` to refresh.")
    out.append("")
    out.append("## KPI vs spec section 16")
    out.append("")
    out.append("| Kryterium | Wartosc |")
    out.append("|---|---|")
    out.append(f"| Liczba dokumentow | {n} |")
    out.append(f"| Pokrycie tematyczne (51) | {len(covered)}/51 |")
    out.append(f"| Warstwa L1 | {by_layer.get('L1', 0)} |")
    out.append(f"| Warstwa L2 | {by_layer.get('L2', 0)} |")
    out.append(f"| Stosunek .gov.pl | {sum(1 for r in rows if r.get('is_official') in ('True', 'true'))}/{n} |")
    out.append(f"| Total MB on disk | {total_bytes / 1_048_576:.1f} |")
    out.append("")
    out.append("## By source")
    out.append("")
    out.append("| Source | Count |")
    out.append("|---|---|")
    for k, v in by_source.most_common():
        out.append(f"| {k} | {v} |")
    out.append("")
    out.append("## By layer")
    out.append("")
    out.append("| Layer | Count |")
    out.append("|---|---|")
    for k, v in by_layer.most_common():
        out.append(f"| {k} | {v} |")
    out.append("")
    out.append("## By format")
    out.append("")
    out.append("| Format | Count |")
    out.append("|---|---|")
    for k, v in by_format.most_common():
        out.append(f"| {k} | {v} |")
    out.append("")

    out.append("## Topic coverage (51 topics)")
    out.append("")
    out.append("| topic_id | group | docs |")
    out.append("|---|---|---|")
    for tid, grp, _ in TOPICS:
        out.append(f"| {tid} | {grp} | {by_topic.get(tid, 0)} |")
    out.append("")
    out.append(f"Covered: **{len(covered)}/51**.  Gaps: **{len(uncovered)}**.")
    if uncovered:
        out.append("")
        out.append("### Uncovered")
        for t in uncovered:
            out.append(f"- {t}")
    out.append("")

    out.append("## Biggest files")
    out.append("")
    out.append("| size MB | source | path |")
    out.append("|---|---|---|")
    for r in biggest:
        size = int(r.get("bytes") or 0) / 1_048_576
        out.append(f"| {size:.1f} | {r.get('source')} | `{r.get('relative_path')}` |")
    out.append("")

    out.append("## Quarantine")
    out.append("")
    if quarantined:
        from collections import Counter as _C
        by_q_src = _C(r["source"] for r in quarantined)
        out.append(f"**{len(quarantined)} dokumentow** zarekwarantowanych przez Agent B audit (off-topic / niska jakosc / redundant).")
        out.append("Pliki w `data/quarantine/<source>/`, wpisy w manifescie zachowane z `quality_flag=quarantine`.")
        out.append("")
        out.append("| Source | Count |")
        out.append("|---|---|")
        for k, v in by_q_src.most_common():
            out.append(f"| {k} | {v} |")
        out.append("")
    rej_dir = DATA_DIR / "quarantine" / "_failed"
    if rej_dir.exists():
        rejected = sorted(rej_dir.iterdir())
        out.append(f"Plus `data/quarantine/_failed/` z **{len(rejected)}** items z fetch-time validation (404, brak PDF magic, WAF redirects).")
    out.append("")

    out.append("## Notes")
    out.append("")
    out.append("- biznes.gov.pl Layer-2 was not collected because the portal sits behind a WAF (Akamai). Per spec section 19 we did not bypass it. Consider running undetected-chromedriver locally for that source if needed.")
    out.append("- KIS individual interpretations (Layer-3) require headless browser (sip.mf.gov.pl is JS-driven). Not collected here.")
    out.append("- All HTTP fetch attempts including failures are logged in `data/logs/fetch_log.ndjson`.")

    target = DATA_DIR / "coverage_report.md"
    target.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {target}")
    print(f"summary: {n} docs, {len(covered)}/51 topics covered")


if __name__ == "__main__":
    main()
