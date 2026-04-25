"""Additional EU acts useful for JDG context (consolidated PL versions).

VAT directive 2006/112, e-invoicing directive, Services directive, eIDAS,
DSA (digital services), digital tax info, etc. — anything a Polish JDG
might reference indirectly.

Each entry: (title, CELEX id, topics_hint).
"""
from __future__ import annotations

import time
from pathlib import Path

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

ACTS = [
    ("Dyrektywa Rady 2006/112/WE w sprawie wspólnego systemu podatku od wartości dodanej",
     "02006L0112-20240101", "vat stawki vat-ue wdt wnt vat marza"),
    ("Dyrektywa 2014/55/UE w sprawie fakturowania elektronicznego",
     "02014L0055-20140521", "ksef faktury ustrukturyzowane"),
    ("Dyrektywa 2006/123/WE - usługi (Services Directive)",
     "02006L0123-20151028", "uslugi swoboda swiadczenia uslug uslugi"),
    ("Dyrektywa 2011/83/UE - prawa konsumentów",
     "02011L0083-20220528", "prawa konsumenta sprzedaz na odleglosc"),
    ("Rozporządzenie 910/2014 (eIDAS)",
     "02014R0910-20240520", "eidas podpis elektroniczny e-doreczenia"),
    ("Rozporządzenie 2022/2065 (Digital Services Act)",
     "32022R2065", "dsa platformy uslugi cyfrowe"),
    ("Dyrektywa 2008/9/WE - zwrot VAT podatnikom UE",
     "02008L0009-20210101", "zwrot vat ue"),
    ("Dyrektywa 2003/88/WE - czas pracy",
     "02003L0088-20000802", "czas pracy nadgodziny urlop"),
]


def main() -> None:
    sess = session_factory({"Accept": "application/pdf"})
    manifest = load_manifest()
    have_urls = {r.get("url") for r in manifest}
    have_sha = {r.get("sha256") for r in manifest}
    saved = 0

    for title, celex, hint in ACTS:
        url = f"https://eur-lex.europa.eu/legal-content/PL/TXT/PDF/?uri=CELEX:{celex}"
        if url in have_urls:
            continue
        time.sleep(0.5)
        res = fetch(url, sess, accept="application/pdf")
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok or not magic_ok(res.content, "pdf") or len(res.content) < 2048:
            quarantine(res.content or b"", f"eurlex_{celex}.bin", "_failed", res.error or "magic_or_size")
            print(f"FAIL {celex}: {res.error}")
            continue
        sha = __import__("hashlib").sha256(res.content).hexdigest()
        if sha in have_sha:
            print(f"DUP  {celex}")
            continue
        have_sha.add(sha)
        topics = assign_topics(title, hint)
        if not topics:
            topics = ["vat_stawki"] if "vat" in hint.lower() else ["ceidg_rejestracja"]
        rel = Path("raw/eurlex") / f"celex_{celex}.pdf"
        save_artifact(
            content=res.content,
            rel_path=rel,
            url=url,
            source="eurlex",
            topic_ids=topics,
            layer="L1",
            fmt="pdf",
            http_status=res.status,
            content_type=res.headers.get("Content-Type", "application/pdf"),
            title=title,
            last_modified=res.headers.get("Last-Modified", ""),
            is_official=True,
            eli_id=f"CELEX:{celex}",
            discovery_source="seed",
            headers=res.headers,
            extra_notes="EU act (PL consolidated)",
        )
        saved += 1
        print(f"OK   {celex} {len(res.content)} B")
    print(f"\n[eurlex extra] saved={saved}")


if __name__ == "__main__":
    main()
