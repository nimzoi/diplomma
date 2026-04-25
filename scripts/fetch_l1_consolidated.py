"""Fetch consolidated 'tekst jednolity' versions of important acts.

Some queries from fetch_l1_regs.py returned amendment acts (zmieniajace)
instead of full consolidated texts. Here we explicitly target Obwieszczenie
Marszalka Sejmu w sprawie ogloszenia tekstu jednolitego for the most
important acts. We use the ELI search endpoint with publisher-keyword filter.
"""
from __future__ import annotations

import time
from pathlib import Path
from urllib.parse import urlencode

import requests

from common import (
    fetch,
    log_fetch,
    magic_ok,
    now_iso,
    quarantine,
    save_artifact,
    session_factory,
    load_manifest,
)
from topics import assign_topics

SEARCH_URL = "https://api.sejm.gov.pl/eli/acts/search"

# Title keyword + topic hints for tekst jednolity discovery.
QUERIES = [
    ("Kodeks cywilny",
     "ogłoszenia jednolitego tekstu ustawy - Kodeks cywilny",
     "kodeks cywilny art. 734 art. 627 umowa zlecenie umowa o dzielo"),
    ("Ustawa o świadczeniach opieki zdrowotnej",
     "ogłoszenia jednolitego tekstu ustawy o świadczeniach opieki zdrowotnej",
     "skladka zdrowotna jdg ryczalt skala liniowy"),
    ("Ustawa o świadczeniach pieniężnych z ub. społ. w razie choroby",
     "ogłoszenia jednolitego tekstu ustawy o świadczeniach pieniężnych z ubezpieczenia społecznego w razie",
     "zasilek chorobowy jdg ubezpieczenie chorobowe przedsiebiorca"),
    ("Ustawa o emeryturach i rentach z FUS",
     "ogłoszenia jednolitego tekstu ustawy o emeryturach i rentach z Funduszu Ubezpieczeń",
     "emerytura jdg zbieg tytulow ubezpieczen"),
    ("Ordynacja podatkowa",
     "ogłoszenia jednolitego tekstu ustawy - Ordynacja podatkowa",
     "ordynacja podatkowa interpretacje indywidualne kis terminy odsetki naruszenie"),
    ("Ustawa o CEIDG",
     "ogłoszenia jednolitego tekstu ustawy o Centralnej Ewidencji i Informacji o Działalności",
     "ceidg rejestracja zawieszenie wznowienie zamkniecie wpisu pkd"),
    ("Ustawa o swobodzie działalności / Prawo przedsiębiorców",
     "ogłoszenia jednolitego tekstu ustawy - Prawo przedsiębiorców",
     "prawo przedsiebiorcow ulga na start zawieszenie dzialalnosci dzialalnosc nierejestrowana"),
    ("Kodeks karny skarbowy",
     "ogłoszenia jednolitego tekstu ustawy - Kodeks karny skarbowy",
     "kks naruszenie sankcje podatkowe kara grzywny"),
    ("Ustawa o Krajowym Rejestrze Sądowym",
     "ogłoszenia jednolitego tekstu ustawy o Krajowym Rejestrze Sądowym",
     "krs"),
    ("Ustawa - Kodeks postępowania administracyjnego",
     "ogłoszenia jednolitego tekstu ustawy - Kodeks postępowania administracyjnego",
     "kpa decyzja administracyjna"),
    ("Ustawa o minimalnym wynagrodzeniu",
     "ogłoszenia jednolitego tekstu ustawy o minimalnym wynagrodzeniu",
     "minimalne wynagrodzenie dzialalnosc nierejestrowana umowa zlecenie podstawa wymiaru"),
    ("Ustawa o zwalczaniu nieuczciwej konkurencji",
     "ogłoszenia jednolitego tekstu ustawy o zwalczaniu nieuczciwej konkurencji",
     "tajemnica przedsiebiorstwa nieuczciwa konkurencja"),
    ("Ustawa o prawie autorskim i prawach pokrewnych",
     "ogłoszenia jednolitego tekstu ustawy o prawie autorskim",
     "ip box prawa autorskie umowa o dzielo wzor"),
    ("Ustawa o rachunkowości",
     "ogłoszenia jednolitego tekstu ustawy o rachunkowości",
     "rachunkowosc ksiegi handlowe sprawozdanie finansowe"),
    ("Ustawa o krajowym systemie e-faktur (KSeF)",
     "ogłoszenia jednolitego tekstu ustawy o zmianie ustawy o podatku od towarów i usług",
     "ksef faktury ustrukturyzowane"),
]


def search(query: dict, sess: requests.Session) -> list[dict]:
    full = f"{SEARCH_URL}?{urlencode(query)}&limit=15"
    try:
        r = sess.get(full, headers={"Accept": "application/json"}, timeout=30)
        r.raise_for_status()
        return r.json().get("items", [])
    except Exception as exc:
        print(f"search err: {exc}")
        return []


def already_have_eli(eli_id: str, manifest: list[dict]) -> bool:
    for r in manifest:
        if r.get("eli_id") == eli_id:
            return True
    return False


def fetch_act(item: dict, hint: str, sess: requests.Session, manifest: list[dict]) -> bool:
    publisher = item.get("publisher") or "DU"
    year = item.get("year")
    pos = item.get("pos")
    eli_id = f"{publisher}/{year}/{pos}"
    if already_have_eli(eli_id, manifest):
        return False
    pdf_url = f"https://api.sejm.gov.pl/eli/acts/{publisher}/{year}/{pos}/text.pdf"
    res = fetch(pdf_url, session=sess, accept="application/pdf")
    log_fetch({
        "ts": now_iso(), "url": pdf_url, "ok": res.ok, "status": res.status,
        "bytes": len(res.content), "retries": res.retries, "error": res.error,
    })
    if not res.ok or not magic_ok(res.content, "pdf") or len(res.content) < 2048:
        quarantine(res.content or b"", f"eli_{publisher}_{year}_{pos}.bin",
                   "_failed", res.error or "magic_or_size")
        return False
    rel = Path("raw/legislation") / f"eli_{publisher}_{year}_{pos}.pdf"
    title = item.get("title", "")
    topics = assign_topics(title, hint)
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
        discovery_source="search_consolidated",
        headers=res.headers,
        extra_notes=f"status={item.get('status')} inForce={item.get('inForce')} consolidated_attempt",
    )
    print(f"OK   {eli_id} {len(res.content)} B  {title[:90]}")
    return True


def is_consolidated(item: dict) -> bool:
    title = (item.get("title") or "").lower()
    typ = (item.get("type") or "").lower()
    if "obwieszczenie" in typ and "ogłoszenia jednolitego tekstu" in title:
        return True
    if "ogłoszenia tekstu jednolitego" in title:
        return True
    if "ogłoszenia jednolitego tekstu" in title:
        return True
    return False


def is_amendment(item: dict) -> bool:
    title = (item.get("title") or "").lower()
    return "o zmianie" in title or "zmieniające" in title or "zmieniającej" in title


def main() -> None:
    sess = session_factory({"Accept": "application/json"})
    manifest = load_manifest()
    for label, title_query, hint in QUERIES:
        print(f"\n>>> {label}")
        items = search({"title": title_query, "inForce": "true"}, sess)
        if not items:
            # fallback: drop "ogłoszenia jednolitego tekstu" prefix
            short_q = title_query.split("tekstu ")[-1] if "tekstu " in title_query else title_query
            items = search({"title": short_q, "inForce": "true"}, sess)
        if not items:
            print(f"  no items for {label}")
            continue
        # Prefer consolidated obwieszczenia, then non-amendment in-force, sorted by recency.
        ranked = sorted(
            items,
            key=lambda x: (
                0 if is_consolidated(x) else (2 if is_amendment(x) else 1),
                0 if x.get("status") == "obowiązujący" else 1,
                -(x.get("year") or 0),
                -(x.get("pos") or 0),
            ),
        )
        for item in ranked:
            if not item.get("textPDF"):
                continue
            if fetch_act(item, hint, sess, manifest):
                manifest = load_manifest()
                break
            time.sleep(0.3)
        time.sleep(0.4)


if __name__ == "__main__":
    main()
