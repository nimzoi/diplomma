"""Discover and download in-force executive regulations + supporting acts (Layer 1+).

Uses the ELI search endpoint:
   GET /eli/acts/search?title=...&inForce=true&type=Rozporządzenie

For each query keep top 1-2 matching titles, download PDF text, validate.
Also adds a few extra Polish acts that are useful for JDG topics
(Kodeks cywilny, ustawa o swiadczeniach zdrowotnych, ustawa o KSeF zmianach itp.).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

from common import (
    fetch,
    load_manifest,
    log_fetch,
    log_rejected,
    magic_ok,
    now_iso,
    quarantine,
    save_artifact,
    session_factory,
)
from topics import assign_topics

SEARCH_URL = "https://api.sejm.gov.pl/eli/acts/search"

# Queries: (label, params, topic_hint, max_results)
QUERIES = [
    ("KPiR rozporzadzenie",
     {"title": "podatkowej księgi przychodów", "type": "Rozporządzenie", "inForce": "true"},
     "kpir podatkowej ksiegi przychodow rozchodow", 1),
    ("Wykaz stawek amortyzacyjnych (zalacznik PIT)",
     {"title": "wykaz rocznych stawek amortyzacyjnych", "inForce": "true"},
     "amortyzacja kśt wykaz rocznych stawek amortyzacyjnych", 1),
    ("Ewidencja przychodow ryczalt rozporzadzenie",
     {"title": "prowadzenia ewidencji przychodów", "type": "Rozporządzenie", "inForce": "true"},
     "ewidencja przychodow ryczalt", 1),
    ("JPK_V7 rozporzadzenie",
     {"title": "deklaracjach o podatku od towarów i usług", "type": "Rozporządzenie", "inForce": "true"},
     "jpk vat jpk_v7m jpk_v7k jednolity plik kontrolny", 1),
    ("Faktury - rozporzadzenie",
     {"title": "wystawiania faktur", "type": "Rozporządzenie", "inForce": "true"},
     "faktury vat faktury ustrukturyzowane ksef", 1),
    ("ZUA/ZWUA/DRA rozporzadzenie",
     {"title": "zgłaszania danych do ubezpieczeń", "type": "Rozporządzenie", "inForce": "true"},
     "zus zua zwua dra zgloszenie do ubezpieczen", 1),
    ("Stawki VAT rozporzadzenie wykonawcze",
     {"title": "stawek podatku od towarów i usług", "type": "Rozporządzenie", "inForce": "true"},
     "stawki vat matryca", 1),
    ("KSeF rozporzadzenie",
     {"title": "Krajowy System e-Faktur", "inForce": "true"},
     "ksef krajowy system e-faktur faktury ustrukturyzowane", 1),
    ("Swiadectwo pracy rozporzadzenie",
     {"title": "świadectwa pracy", "type": "Rozporządzenie", "inForce": "true"},
     "swiadectwo pracy", 1),
    ("BHP szkolenie rozporzadzenie",
     {"title": "szkolenia w dziedzinie bezpieczeństwa", "type": "Rozporządzenie", "inForce": "true"},
     "bhp szkolenie wstepne praca biurowa", 1),
    ("PKD klasyfikacja",
     {"title": "Polskiej Klasyfikacji Działalności", "inForce": "true"},
     "pkd klasyfikacja dzialalnosci", 1),
    ("Kodeks cywilny",
     {"title": "Kodeks cywilny", "inForce": "true"},
     "kodeks cywilny umowa zlecenie umowa o dzielo art. 734 art. 627", 1),
    ("Ustawa o swiadczeniach opieki zdrowotnej",
     {"title": "świadczeniach opieki zdrowotnej finansowanych", "inForce": "true"},
     "skladka zdrowotna jdg ryczalt skala liniowy", 1),
    ("Ustawa o swiadczeniach pienieznych z ubezpieczenia chorobowego",
     {"title": "świadczeniach pieniężnych z ubezpieczenia społecznego w razie", "inForce": "true"},
     "zasilek chorobowy ubezpieczenie chorobowe przedsiebiorca", 1),
    ("Ustawa o emeryturach i rentach z FUS",
     {"title": "emeryturach i rentach z Funduszu Ubezpieczeń", "inForce": "true"},
     "emerytura jdg zbieg tytulow ubezpieczen fus", 1),
    ("Ustawa o CEIDG i punkcie informacji",
     {"title": "Centralnej Ewidencji i Informacji o Działalności", "inForce": "true"},
     "ceidg rejestracja zawieszenie wznowienie zamkniecie wpisu", 1),
    ("Kodeks karny skarbowy",
     {"title": "Kodeks karny skarbowy", "inForce": "true"},
     "kks sankcje podatkowe naruszenie", 1),
    ("Ordynacja podatkowa",
     {"title": "Ordynacja podatkowa", "inForce": "true"},
     "ordynacja podatkowa interpretacje indywidualne kis terminy odsetki", 1),
]


def search_acts(params: dict, sess: requests.Session) -> list[dict]:
    full = f"{SEARCH_URL}?{urlencode(params)}&limit=10"
    try:
        r = sess.get(full, headers={"Accept": "application/json"}, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("items", [])
    except Exception as exc:
        print(f"search error {full}: {exc}")
        return []


def pick_canonical(items: list[dict]) -> dict | None:
    """Prefer items with status=obowiązujący and inForce=IN_FORCE; pick the
    most recent by year+pos."""
    candidates = [
        i for i in items
        if i.get("status") == "obowiązujący" and i.get("inForce") in ("IN_FORCE", None) and i.get("textPDF")
    ]
    if not candidates:
        candidates = [i for i in items if i.get("textPDF")]
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x.get("year", 0), x.get("pos", 0)), reverse=True)
    return candidates[0]


def fetch_act(item: dict, topic_hint: str, sess: requests.Session, have_urls: set[str]) -> None:
    publisher = item.get("publisher") or "DU"
    year = item.get("year")
    pos = item.get("pos")
    if not (year and pos):
        return
    eli_id = f"{publisher}/{year}/{pos}"
    pdf_url = f"https://api.sejm.gov.pl/eli/acts/{publisher}/{year}/{pos}/text.pdf"
    if pdf_url in have_urls:
        return
    res = fetch(pdf_url, session=sess, accept="application/pdf")
    log_fetch({
        "ts": now_iso(), "url": pdf_url, "ok": res.ok, "status": res.status,
        "bytes": len(res.content), "retries": res.retries, "error": res.error,
    })
    if not res.ok or not magic_ok(res.content, "pdf") or len(res.content) < 2048:
        quarantine(res.content or b"", f"eli_{publisher}_{year}_{pos}.bin",
                   "_failed", res.error or "magic_or_size")
        print(f"FAIL {eli_id}: {res.error}")
        return
    rel = Path("raw/legislation") / f"eli_{publisher}_{year}_{pos}.pdf"
    title = item.get("title", "")
    topics = assign_topics(title, topic_hint)
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
        title=title,
        last_modified=res.headers.get("Last-Modified", ""),
        is_official=True,
        eli_id=eli_id,
        discovery_source="references_api",
        headers=res.headers,
        extra_notes=f"status={item.get('status')} inForce={item.get('inForce')}",
    )
    print(f"OK   {eli_id} {len(res.content)} B  {title[:80]}")


def main() -> None:
    sess = session_factory({"Accept": "application/json"})
    have_urls = {r.get("url", "") for r in load_manifest()}
    seen_eli: set[str] = set()
    for label, params, hint, max_n in QUERIES:
        print(f"\n>>> {label}")
        items = search_acts(params, sess)
        if not items:
            print(f"  no items for {label}")
            continue
        # Filter: prefer matching the params type if specified
        ranked = sorted(
            items,
            key=lambda x: (
                0 if x.get("status") == "obowiązujący" else 1,
                -(x.get("year") or 0),
                -(x.get("pos") or 0),
            ),
        )
        picked = 0
        for item in ranked:
            if picked >= max_n:
                break
            eli = item.get("ELI", "")
            if eli in seen_eli:
                continue
            if not item.get("textPDF"):
                continue
            seen_eli.add(eli)
            fetch_act(item, hint, sess, have_urls)
            picked += 1
            time.sleep(0.4)


if __name__ == "__main__":
    main()
