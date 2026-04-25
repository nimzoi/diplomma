"""Fix the 4 MUST acts that were downloaded with incorrect ELI URLs.

The spec used legacy DzU `nr/poz` notation but ELI URLs use POSITION only.
Spec gave nr instead of poz for pre-2012 acts:

  Kodeks pracy:  WDU19740240141 = 1974 nr 24  poz 141 -> /DU/1974/141 (was /DU/1974/24)
  PIT:           WDU19910800350 = 1991 nr 80  poz 350 -> /DU/1991/350 (was /DU/1991/80)
  Ryczalt:       WDU19981440930 = 1998 nr 144 poz 930 -> /DU/1998/930 (was /DU/1998/144)
  USUS:          WDU19981370887 = 1998 nr 137 poz 887 -> /DU/1998/887 (was /DU/1998/137)

This script:
  1. Removes the 4 wrong acts from disk + manifest.
  2. Downloads the 4 correct acts.
  3. Re-runs topic auto-tagger.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

# Make scripts importable
sys.path.insert(0, str(Path(__file__).parent))

from common import (
    DATA_DIR,
    MANIFEST_CSV,
    MANIFEST_FIELDS,
    fetch,
    load_manifest,
    log_fetch,
    magic_ok,
    now_iso,
    save_artifact,
    session_factory,
)
from topics import assign_topics

WRONG_ELI = {"DU/1974/24", "DU/1991/80", "DU/1998/137", "DU/1998/144"}

CORRECT = [
    {
        "title": "Kodeks pracy",
        "publisher": "DU", "year": 1974, "position": 141,
        "topics_hint": "kodeks pracy umowa o prace urlop wypowiedzenie czas pracy bhp swiadectwo",
    },
    {
        "title": "Ustawa o podatku dochodowym od osob fizycznych (PIT)",
        "publisher": "DU", "year": 1991, "position": 350,
        "topics_hint": "skala podatkowa podatek liniowy art 30c koszty uzyskania przychodu amortyzacja IP Box pit-36 pit-36l kpir",
    },
    {
        "title": "Ustawa o systemie ubezpieczen spolecznych",
        "publisher": "DU", "year": 1998, "position": 887,
        "topics_hint": "preferencyjny zus maly zus plus art 18a art 18c podstawa wymiaru skladek zua zwua dra ubezpieczenie chorobowe wakacje skladkowe",
    },
    {
        "title": "Ustawa o zryczaltowanym podatku dochodowym (ryczalt)",
        "publisher": "DU", "year": 1998, "position": 930,
        "topics_hint": "ryczalt od przychodow stawki ryczaltu pkd karta podatkowa pit-28 ewidencja przychodow",
    },
]


def remove_wrong() -> int:
    rows = load_manifest()
    keep = []
    removed = 0
    for r in rows:
        if r.get("eli_id") in WRONG_ELI:
            for p in (DATA_DIR / r["relative_path"], DATA_DIR / (r["relative_path"] + ".meta.json")):
                if p.exists():
                    p.unlink()
            removed += 1
        else:
            keep.append(r)
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in keep:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})
    return removed


def fetch_one(act: dict, sess) -> bool:
    eli_id = f"{act['publisher']}/{act['year']}/{act['position']}"
    pdf_url = f"https://api.sejm.gov.pl/eli/acts/{act['publisher']}/{act['year']}/{act['position']}/text.pdf"
    res = fetch(pdf_url, session=sess, accept="application/pdf")
    log_fetch({
        "ts": now_iso(), "url": pdf_url, "ok": res.ok, "status": res.status,
        "bytes": len(res.content), "retries": res.retries, "error": res.error,
    })
    if not res.ok or not magic_ok(res.content, "pdf") or len(res.content) < 2048:
        print(f"FAIL {eli_id}: {res.error}")
        return False
    rel = Path("raw/legislation") / f"eli_{act['publisher']}_{act['year']}_{act['position']}.pdf"
    topics = assign_topics(act["title"], act.get("topics_hint", ""))
    save_artifact(
        content=res.content,
        rel_path=rel,
        url=pdf_url,
        source="eli",
        topic_ids=topics,
        layer="L1",
        fmt="pdf",
        http_status=res.status,
        content_type=res.headers.get("Content-Type", "application/pdf"),
        title=act["title"],
        last_modified=res.headers.get("Last-Modified", ""),
        is_official=True,
        eli_id=eli_id,
        discovery_source="seed_corrected",
        headers=res.headers,
        extra_notes="MUST act per spec 5.1 (corrected URL: spec used nr instead of poz)",
    )
    print(f"OK   {eli_id} {len(res.content)} B  {act['title']}")
    return True


def main() -> None:
    n = remove_wrong()
    print(f"removed {n} wrong rows from manifest + disk")
    sess = session_factory({"Accept": "application/pdf"})
    for act in CORRECT:
        fetch_one(act, sess)
        time.sleep(0.4)


if __name__ == "__main__":
    main()
