"""Fix sidecar JSON quality issues flagged by PR review.

1. Strip `set-cookie` (and `cookie`) from headers.
2. Normalize `title` field: collapse whitespace, drop "BHP / Prawo / ..."
   cover-prefix that PIP scraper picked up from listing labels.
3. Re-tag `topic_ids` for items where the topic is clearly bogus
   (e.g. "Prasa mechaniczna" tagged kp_urlop) by re-running assign_topics()
   over the cleaned title.

Mirrors the changes back into manifest.csv.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV, MANIFEST_FIELDS, load_manifest
from topics import assign_topics

WS_RE = re.compile(r"\s+")
LISTING_PREFIX = re.compile(
    r"^(BHP|Prawo|Obcojęzyczne|Wzory|Nowości|Inne|Druki|Inne wyd\w*)\s+",
    re.I,
)
DROP_HEADERS = {"set-cookie", "cookie"}


def normalize_title(s: str) -> str:
    if not s:
        return ""
    s = WS_RE.sub(" ", s).strip()
    # Drop the leading category label (BHP, Prawo, …) that PIP scraper picked up
    s = LISTING_PREFIX.sub("", s).strip()
    return s


def clean_headers(h: dict) -> dict:
    if not isinstance(h, dict):
        return h
    return {k: v for k, v in h.items() if k.lower() not in DROP_HEADERS}


def main() -> None:
    rows = load_manifest()
    changed_titles = 0
    changed_topics = 0
    cleaned_sidecars = 0

    for r in rows:
        path = DATA_DIR / r["relative_path"]
        sidecar = path.with_suffix(path.suffix + ".meta.json")

        # Normalize title in row
        old_title = r.get("title", "")
        new_title = normalize_title(old_title)
        if new_title != old_title:
            r["title"] = new_title
            changed_titles += 1

        # Re-assign topics from the cleaned title + url + relative_path
        existing = set((r.get("topic_ids") or "").split(";")) - {""}
        new = set(assign_topics(new_title, r.get("url", ""), r.get("relative_path", "")))
        merged = existing & new if existing & new else (existing | new)
        # Only retain topics that match the cleaned title; if old set has 0
        # overlap with new keyword-derived set, replace with the new set.
        # If new set is empty, keep existing (manual tags via tag_*.py scripts).
        if new and existing != new:
            if new & existing:
                final = (existing | new)
            else:
                # No overlap → existing tags are likely bogus, replace.
                final = new
            if final != existing:
                r["topic_ids"] = ";".join(sorted(final))
                changed_topics += 1

        # Clean sidecar JSON: drop set-cookie + sync title + topic_ids + content_audit unchanged
        if sidecar.exists():
            try:
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
                meta["title"] = r["title"]
                meta["topic_ids"] = r["topic_ids"].split(";") if r.get("topic_ids") else []
                if "headers" in meta:
                    meta["headers"] = clean_headers(meta["headers"])
                sidecar.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
                cleaned_sidecars += 1
            except Exception as exc:
                print(f"  sidecar error {sidecar}: {exc}")

    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})

    print(f"normalized titles: {changed_titles}")
    print(f"updated topic_ids: {changed_topics}")
    print(f"cleaned sidecars:  {cleaned_sidecars}")


if __name__ == "__main__":
    main()
