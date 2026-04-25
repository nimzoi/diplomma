"""Drop PIP files that survived earlier cleanups but are clearly off-topic
for a JDG (single-person business) chatbot.

Targets industrial machinery / agriculture / construction-only docs that
crept in via loose 'praca'/'pracown' keyword matching.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV, MANIFEST_FIELDS, load_manifest

OFF_TOPIC_RE = re.compile(
    r"(prasa[\-_ ]?(mech|hydraul)|"
    r"prasa do slomy|prase do slomy|prase mechaniczn|"
    r"opryskiwacz|kombajn|kosiark|wal[\-_ ]?przeg|przegubo|"
    r"ladowark|ciagnik|kombajn|"
    r"frezar|tokark|szlifierk|"
    r"pilarka[\-_ ]?(spalin|tarczow|ramow)|"
    r"strugark|wytlaczark|"
    r"nozyce[\-_ ]?gilotyn|wal[\-_ ]?przegub|wytlaczar|"
    r"naprawa[\-_ ]?pojazd|magazynier|gornik|"
    r"przewoz[\-_ ]?towarow[\-_ ]?niebezpiec|adr|"
    r"sianokisz|kleszcze|"
    r"wycia(g|ż)i[\-_ ]?towar|wozkiem[\-_ ]?jezdn|"
    r"masarn|piekar|tartak|stolarn|fryzjer|"
    r"odsnie(z|ż)|wykop|drabini?|drabin[\-_ ]?przen|"
    r"siano(\b|kis)|biobojcz|nanomateria|"
    r"kart[ay][1-9]|"
    r"narzadu[\-_ ]?glos|narzadu[\-_ ]?sluch|cytostatyk|"
    r"przewoz[\-_ ]?ladunk|powolan[\-_ ]?do[\-_ ]?suby[\-_ ]?wojskow|"
    r"transport[\-_ ]?i[\-_ ]?rozladunek|zwierza|"
    r"choroby[\-_ ]?narzadu|znalezion|"
    r"pracown_uprawn[\-_ ]?wojskow|"
    r"miesniow|szkieletow|miesniowo|"
    r"obsluga[\-_ ]?zwierz)",
    re.I,
)

ALWAYS_KEEP = {
    # Even if name matches, keep these explicitly (may have JDG content)
    # add specific titles here later if needed.
}


def main() -> None:
    rows = load_manifest()
    keep = []
    dropped = []
    for r in rows:
        if r.get("source") != "pip":
            keep.append(r)
            continue
        path = r.get("relative_path", "")
        if path in ALWAYS_KEEP:
            keep.append(r)
            continue
        if OFF_TOPIC_RE.search(path):
            dropped.append(path)
            for p in (DATA_DIR / path, DATA_DIR / (path + ".meta.json")):
                if p.exists():
                    p.unlink()
        else:
            keep.append(r)

    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in keep:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})

    print(f"dropped {len(dropped)} off-topic PIP files; manifest now {len(keep)} rows")


if __name__ == "__main__":
    main()
