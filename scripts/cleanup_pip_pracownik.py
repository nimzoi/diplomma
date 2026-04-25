"""Drop PIP files identified by the first agent as low-value for a JDG
chatbot — predominantly addressed to pracownicy (employees) rather than
pracodawcy (employers/JDG owners), or industry-specific that slipped past
earlier cleanups.
"""
from __future__ import annotations

import csv
from pathlib import Path

from common import DATA_DIR, MANIFEST_CSV, MANIFEST_FIELDS, load_manifest

# From agent's section "Co WYRZUCIĆ z obecnych (PIP balast — ~30-40 docs)"
DROP_FILES = {
    # industry-specific
    "raw/pip/Bezpieczna-praca-w-handlu.pdf",
    "raw/pip/Bezpieczna-praca-w-restauracjach-i-innych-placowkach-gastronomicznych.pdf",
    "raw/pip/LISTA-KONTROLNA-DREWNO-INTERMET.pdf",
    "raw/pip/Pracownicy-delegowani-w-sektorze-budowlanym.pdf",
    "raw/pip/Bezpieczenstwo-uzytkowania-maszyn-Poradnik-dla-pracodawcow.pdf",
    "raw/pip/bhp---obowiazki-kierownika-budowy.pdf",
    "raw/pip/czas-pracy-kierowcow.pdf",
    "raw/pip/czynniki-szkodliwe-badania-i-pomiary.pdf",
    # addressed to pracownicy not pracodawcy
    "raw/pip/PRACOWNIK-WOBEC-MOBBINGU-DRUK-19.pdf",
    "raw/pip/Pracownik.pdf",
    "raw/pip/Prawa-i-obowiazki-pracownika-w-zakresie-BHP.pdf",
    "raw/pip/Stres-por-pracow-dodruk2016-Intern.pdf",
    "raw/pip/Uprawnienia-pracownikow-powoanych-do-suby-wojskowej.pdf",
    # niche / not relevant for biurowa JDG
    "raw/pip/Ocena-ryzyka-zawodowego-Czynniki-psychospoleczne.pdf",
    "raw/pip/Wizja-zero.pdf",
    "raw/pip/pierwsza-pomoc-apteczka.pdf",
    "raw/pip/praca-tymczasowa.pdf",
    "raw/pip/Bezpieczny-gornik.pdf",
    "raw/pip/bezpieczna-praca-w-zawodzie-magazyniera.pdf",
    "raw/pip/bezpieczne-odsniezanie-dachow.pdf",
    "raw/pip/profilaktyzna-ochorna-zdrowia.pdf",
    "raw/pip/produkty-biobojcze.pdf",
    "raw/pip/nanomaterialy.pdf",
    "raw/pip/Zaburzenia-ukladu-miesniowo-szkieletowego-u-dzieci-i-mlodziezy.pdf",
    "raw/pip/karta1.pdf",
    "raw/pip/karta2.pdf",
    "raw/pip/karta3.pdf",
    "raw/pip/karta4.pdf",
    "raw/pip/jak-kocenic-ryzyko-zawodowe.pdf",
    "raw/pip/dyskrym.pdf",
    "raw/pip/niepelnospr-pracow.pdf",
    "raw/pip/choroby-narzadu-glosu.pdf",
}


def main() -> None:
    rows = load_manifest()
    keep = []
    dropped = 0
    for r in rows:
        if r.get("relative_path") in DROP_FILES:
            for p in (DATA_DIR / r["relative_path"], DATA_DIR / (r["relative_path"] + ".meta.json")):
                if p.exists():
                    p.unlink()
            dropped += 1
        else:
            keep.append(r)
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in keep:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})
    print(f"dropped {dropped} pracownik/industry PIP; manifest now {len(keep)} rows")


if __name__ == "__main__":
    main()
