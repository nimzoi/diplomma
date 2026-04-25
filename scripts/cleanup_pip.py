"""Remove off-topic PIP files from manifest + filesystem.

Some publications passed the loose 'praca' filter but are clearly out of scope
for a JDG chatbot (azbest, budownictwo, rolnictwo, lesnictwo, komiksy, drewno,
pielegniark, urawi, etc.). Drop them to keep dataset focused.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV, MANIFEST_FIELDS, load_manifest

DROP_PATTERNS = [
    r"azbest", r"budowni", r"rolnic", r"lesni", r"leśni", r"komiks",
    r"drewn", r"piel(e|ę)gniar", r"żuraw|zuraw", r"rusztowa", r"szybkomontuj",
    r"wsi", r"gospodarstw", r"przedrolni", r"r[óo]wieśn",
    r"hodowl", r"strazak|stra(z|ż)acy", r"wojska", r"lotniska", r"morsk",
    r"chemicz", r"fajerwer", r"wyburz", r"kabel", r"r[ęe]czne prace transportow",
    r"alkohol", r"cudzoziemc", r"pi[ec]komat", r"alko-",
    r"bezpieczne-pozyskiwa", r"NagrodaGIP", r"r[óo]wnouprawni",
    r"przygod", r"wakacj", r"piotrek-i-patryk",
    r"r-wno-traktowanie", r"profilaktyka",
    r"instalacje-elektryczne", r"wykopy?", r"siatki", r"transport[\-_]?(mech|r[ęe]czny|na[\-_]plac)",
    r"masarn", r"ubojn", r"roboty[\-_]torow", r"u[zż]ytkowanie[\-_]maszyn",
    r"poslizgniec", r"po[śs]li[zż]gni", r"sygnalisci",
    r"transport[\-_]?r[ęe]czny", r"r[ęe]czne[\-_]prace",
    r"bezpieczestwo[\-_]na[\-_]stanowi", r"PORADNIK[\-_]DOTUBEZPIECZE",
    r"prewencja[\-_]wypadkow", r"lista[\-_]kontrolna",
    r"czynnikipsychos", r"dla[\-_]kierowcow",
    r"PracownicyMlodociani", r"ochrona[\-_]pracy[\-_]kobiet",
    r"agencja[\-_]pracy[\-_]tymcz",
    r"o[\-_]bezpiecznej[\-_]pracy", r"bezp[\-_]wyk[\-_]wyb",
    r"Spoeczna[\-_]odpowiedzialno", r"katalogdobry?epraktyki",
    r"rodki[\-_]ochrony[\-_]indywid", r"sciaga[\-_]?dla",
    r"dostosuj[\-_]swoj[\-_]zaklad",
    # Industry-specific off-topic
    r"tartak", r"masarn", r"piekar", r"fryzjer|fryzier",
    r"stolar", r"pieczar", r"przetw[óo]r",
    r"studzienk", r"narz[aą]du[\-_]?sluchu", r"srodki[\-_]ochron",
    r"normatywy[\-_]higieniczn", r"wypadki[\-_]w[\-_]pracy",
    r"poradnik[\-_]dla[\-_]pracownika", r"poradnik[\-_]dla[\-_]pracodawcy",
    r"bezpieczna[\-_]praca[\-_]w[\-_](tartaku|stolarni|masarn|ubojn|piekar|zakl)",
    r"prewencja", r"sciaga[\-_]?dla", r"wykop", r"siatk",
    r"linie[\-_]nap", r"pracodawca[\-_]u[zż]ytkownik", r"odbieranie[\-_]?przesy",
    r"ABC[\-_]BHP",  # generic BHP, not strictly JDG-relevant
    r"PORADNIK[\-_]DOTUBEZPIECZE", r"prewencja[\-_]wypad",
    r"zgodnie[\-_]z[\-_]prawem[\-_]i[\-_]bezpiecznie",
    r"u[zż]ytkowanie[\-_]maszyn",
    r"sposoby[\-_]na[\-_]stres",
    r"podroze[\-_]?sluzbow", r"PodrozeSluzbow",
    r"Bezpieczestwo[\-_](na[\-_]stanowisk|stanowisk)",
    r"O[\-_]bezpieczne", r"bezp[\-_]wyk[\-_]wyb",
]
DROP_RE = re.compile("|".join(DROP_PATTERNS), re.I)

KEEP_PATTERNS = [
    "umowa", "kodeks-prac", "urlop", "wypowiedz", "swiadectw", "świadectw",
    "czas-pracy", "praca-zdaln", "biuro", "macierz", "rodzic",
    "minimalnych-wymag", "ergonom", "monitoring", "monitorin",
    "kontrol", "wynagrodz", "zatrudn", "delegowan", "umowy",
    "rejestr-czynnosci", "ochron-pracy",
]
KEEP_RE = re.compile("|".join(KEEP_PATTERNS), re.I)


def main() -> None:
    manifest = load_manifest()
    keep_rows: list[dict] = []
    dropped: list[str] = []
    for row in manifest:
        if row.get("source") != "pip":
            keep_rows.append(row)
            continue
        path = row.get("relative_path", "")
        title = row.get("title", "")
        url = row.get("url", "")
        blob = f"{path} {title} {url}"
        if KEEP_RE.search(blob):
            keep_rows.append(row)
            continue
        if DROP_RE.search(blob):
            dropped.append(path)
            continue
        # If neither matched, keep (conservative).
        keep_rows.append(row)

    # Delete dropped files from disk.
    for rel in dropped:
        full = DATA_DIR / rel
        for p in (full, full.with_suffix(full.suffix + ".meta.json")):
            if p.exists():
                p.unlink()

    # Rewrite manifest.
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in keep_rows:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})

    print(f"removed {len(dropped)} off-topic PIP files")
    print(f"manifest now: {len(keep_rows)} rows")


if __name__ == "__main__":
    main()
