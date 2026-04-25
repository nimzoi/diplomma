"""Apply Agent B drop list from data/research/agent_b_audit.md.

For each (relative_path, reason) pair parsed from the fenced ```csv block:
- move data/<relative_path>            -> data/quarantine/<source>/<basename>
- move data/<relative_path>.meta.json  -> data/quarantine/<source>/<basename>.meta.json
- write data/quarantine/<source>/<basename>.reason.txt with the reason
- update manifest.csv: quality_flag=quarantine, notes=<reason>,
                      relative_path=quarantine/<source>/<basename>
  (row is preserved, never deleted).

Usage:
    python3 scripts/quarantine_from_audit.py            # apply
    python3 scripts/quarantine_from_audit.py --dry-run  # preview only
"""
from __future__ import annotations

import argparse
import csv
import io
import shutil
import sys
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV, MANIFEST_FIELDS, QUARANTINE_DIR

AUDIT_MD = DATA_DIR / "research" / "agent_b_audit.md"


def parse_drop_list(md_text: str) -> list[tuple[str, str]]:
    """Find the first ```csv … ``` block whose header is `relative_path,reason`."""
    lines = md_text.splitlines()
    in_block = False
    buf: list[str] = []
    for line in lines:
        if not in_block:
            if line.strip().startswith("```csv"):
                in_block = True
            continue
        if line.strip() == "```":
            break
        buf.append(line)
    if not buf:
        raise SystemExit(f"no ```csv block found in {AUDIT_MD}")

    reader = csv.DictReader(io.StringIO("\n".join(buf)))
    if reader.fieldnames != ["relative_path", "reason"]:
        raise SystemExit(
            f"unexpected CSV header: {reader.fieldnames!r}, expected ['relative_path','reason']"
        )
    drops: list[tuple[str, str]] = []
    for row in reader:
        rp = (row.get("relative_path") or "").strip()
        rs = (row.get("reason") or "").strip()
        if rp and rs:
            drops.append((rp, rs))
    return drops


def source_from_relpath(rel: str) -> str:
    """raw/govpl/foo.pdf -> govpl ;  raw/govpl_html/x.html -> govpl_html."""
    parts = rel.split("/")
    return parts[1] if len(parts) >= 2 and parts[0] == "raw" else "misc"


def move_one(rel_path: str, reason: str, dry_run: bool) -> tuple[str, str]:
    """Move file + sidecar; return (new_relative_path, status)."""
    source = source_from_relpath(rel_path)
    src = DATA_DIR / rel_path
    if not src.exists():
        return rel_path, f"missing-src: {src}"

    target_dir = QUARANTINE_DIR / source
    target = target_dir / src.name
    sidecar_src = src.with_suffix(src.suffix + ".meta.json")
    sidecar_target = target.with_suffix(target.suffix + ".meta.json")
    reason_target = target.with_suffix(target.suffix + ".reason.txt")
    new_rel = f"quarantine/{source}/{src.name}"

    if dry_run:
        return new_rel, "dry-run"

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(target))
    if sidecar_src.exists():
        shutil.move(str(sidecar_src), str(sidecar_target))
    reason_target.write_text(reason + "\n", encoding="utf-8")
    return new_rel, "moved"


def update_manifest(
    drops: dict[str, tuple[str, str]],  # rel_path -> (new_rel, reason)
    dry_run: bool,
) -> tuple[int, int]:
    rows = list(csv.DictReader(MANIFEST_CSV.open(encoding="utf-8")))
    matched = 0
    for r in rows:
        if r["relative_path"] in drops:
            new_rel, reason = drops[r["relative_path"]]
            r["relative_path"] = new_rel
            r["quality_flag"] = "quarantine"
            r["notes"] = reason
            matched += 1
    if not dry_run:
        with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})
    return matched, len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    md = AUDIT_MD.read_text(encoding="utf-8")
    drops = parse_drop_list(md)
    print(f"parsed drop list: {len(drops)} entries")

    moves: dict[str, tuple[str, str]] = {}
    skipped = 0
    for rel, reason in drops:
        new_rel, status = move_one(rel, reason, args.dry_run)
        moves[rel] = (new_rel, reason)
        if status.startswith("missing-src"):
            print(f"  ! {rel}: {status}")
            skipped += 1
        elif status == "dry-run":
            print(f"  [dry] {rel} -> {new_rel}")
        else:
            print(f"  ok   {rel} -> {new_rel}")

    matched, total = update_manifest(moves, args.dry_run)
    print(f"manifest: matched={matched}/{total} (drops={len(drops)}, skipped-files={skipped})")
    if args.dry_run:
        print("DRY RUN: no files moved, manifest not written.")


if __name__ == "__main__":
    sys.exit(main())
