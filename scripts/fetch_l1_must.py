"""Download the 8 MUST legislation acts (Layer 1) defined in spec 5.1.

7 from ELI (api.sejm.gov.pl) + RODO from EUR-Lex.
Saves PDFs to data/raw/legislation/ and data/raw/eurlex/.
"""
from __future__ import annotations

import time
from pathlib import Path

from common import (
    DATA_DIR,
    fetch,
    log_fetch,
    log_rejected,
    magic_ok,
    now_iso,
    quarantine,
    save_artifact,
    session_factory,
    short_id,
)
from topics import assign_topics

# spec 5.1
ELI_ACTS = [
    {
        "title": "Kodeks pracy",
        "publisher": "DU", "year": 1974, "position": 24,
        "topics_hint": "kodeks pracy umowa o prace urlop wypowiedzenie czas pracy bhp",
    },
    {
        "title": "Ustawa o podatku dochodowym od osob fizycznych (PIT)",
        "publisher": "DU", "year": 1991, "position": 80,
        "topics_hint": "skala podatkowa podatek liniowy art 30c koszty uzyskania przychodu amortyzacja IP Box ip box pit-36 pit-36l",
    },
    {
        "title": "Ustawa o zryczaltowanym podatku dochodowym od niektorych przychodow (ryczalt)",
        "publisher": "DU", "year": 1998, "position": 144,
        "topics_hint": "ryczalt od przychodow stawki ryczaltu pkd karta podatkowa pit-28 ewidencja przychodow",
    },
    {
        "title": "Ustawa o podatku od towarow i uslug (VAT)",
        "publisher": "DU", "year": 2004, "position": 535,
        "topics_hint": "vat-r rejestracja vat zwolnienie 200 tys art. 113 jpk_v7 ksef faktury ustrukturyzowane stawki vat matryca vat vat-ue wdt wnt vat marza biala lista vat",
    },
    {
        "title": "Prawo przedsiebiorcow",
        "publisher": "DU", "year": 2018, "position": 646,
        "topics_hint": "ulga na start art. 18 prawo przedsiebiorcow zawieszenie dzialalnosci wznowienie zamkniecie ceidg dzialalnosc nierejestrowana art. 5 art. 22-25",
    },
    {
        "title": "Ustawa o systemie ubezpieczen spolecznych",
        "publisher": "DU", "year": 1998, "position": 137,
        "topics_hint": "preferencyjny zus maly zus plus art. 18c podstawa wymiaru skladek zua zwua dra deklaracja rozliczeniowa ubezpieczenie chorobowe wakacje skladkowe",
    },
    {
        "title": "Ustawa o ochronie danych osobowych",
        "publisher": "DU", "year": 2018, "position": 1000,
        "topics_hint": "rodo mala firma ochrona danych osobowych iod inspektor naruszenie zgloszenie do uodo",
    },
]

EURLEX_ACTS = [
    {
        "title": "RODO (Rozporzadzenie 2016/679) - tekst skonsolidowany PL",
        "celex": "02016R0679-20160504",
        "url": "https://eur-lex.europa.eu/legal-content/PL/TXT/PDF/?uri=CELEX:02016R0679-20160504",
        "topics_hint": "rodo mala firma rejestr czynnosci przetwarzania art. 30 rodo iod inspektor klauzula informacyjna art. 13 rodo monitoring naruszenie ochrony danych zgloszenie do uodo rekrutacja",
    },
]


def fetch_eli_pdf(act: dict, session) -> None:
    eli_id = f"{act['publisher']}/{act['year']}/{act['position']}"
    pdf_url = f"https://api.sejm.gov.pl/eli/acts/{act['publisher']}/{act['year']}/{act['position']}/text.pdf"
    res = fetch(pdf_url, session=session, accept="application/pdf")
    log_fetch({
        "ts": now_iso(), "url": pdf_url, "ok": res.ok, "status": res.status,
        "bytes": len(res.content), "retries": res.retries, "error": res.error,
    })
    if not res.ok or not magic_ok(res.content, "pdf"):
        quarantine(res.content or b"", f"eli_{act['publisher']}_{act['year']}_{act['position']}.bin",
                   "_failed", res.error or "magic_mismatch")
        print(f"FAIL {eli_id}: {res.error}")
        return
    if len(res.content) < 2048:
        quarantine(res.content, f"eli_{act['publisher']}_{act['year']}_{act['position']}.pdf",
                   "_too_small", "below 2KB threshold")
        print(f"REJECT {eli_id}: too small ({len(res.content)} B)")
        return

    rel = Path("raw/legislation") / f"eli_{act['publisher']}_{act['year']}_{act['position']}.pdf"
    topics = assign_topics(act["title"], act.get("topics_hint", ""))
    row = save_artifact(
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
        discovery_source="seed",
        headers=res.headers,
        extra_notes="MUST act per spec 5.1",
    )
    print(f"OK   {eli_id} {row['bytes']} B -> {rel}")


def fetch_eurlex(act: dict, session) -> None:
    res = fetch(act["url"], session=session, accept="application/pdf")
    log_fetch({
        "ts": now_iso(), "url": act["url"], "ok": res.ok, "status": res.status,
        "bytes": len(res.content), "retries": res.retries, "error": res.error,
    })
    if not res.ok or not magic_ok(res.content, "pdf"):
        quarantine(res.content or b"", f"eurlex_{act['celex']}.bin", "_failed",
                   res.error or "magic_mismatch")
        print(f"FAIL {act['celex']}: {res.error}")
        return
    rel = Path("raw/eurlex") / f"celex_{act['celex']}.pdf"
    topics = assign_topics(act["title"], act.get("topics_hint", ""))
    row = save_artifact(
        content=res.content,
        rel_path=rel,
        url=act["url"],
        source="eurlex",
        topic_ids=topics,
        layer="L1",
        fmt="pdf",
        http_status=res.status,
        content_type=res.headers.get("Content-Type", "application/pdf"),
        title=act["title"],
        last_modified=res.headers.get("Last-Modified", ""),
        is_official=True,
        eli_id=f"CELEX:{act['celex']}",
        discovery_source="seed",
        headers=res.headers,
        extra_notes="MUST act per spec 5.1 (EUR-Lex)",
    )
    print(f"OK   CELEX:{act['celex']} {row['bytes']} B -> {rel}")


def main() -> None:
    sess = session_factory({"Accept": "application/pdf"})
    for act in ELI_ACTS:
        fetch_eli_pdf(act, sess)
        time.sleep(0.4)
    for act in EURLEX_ACTS:
        fetch_eurlex(act, sess)
        time.sleep(0.4)


if __name__ == "__main__":
    main()
