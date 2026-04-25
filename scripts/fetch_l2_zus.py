"""ZUS poradniki + wzory scraper.

ZUS rejects the academic UA — but accepts a realistic Chrome UA. We restrict
to publicly-listed PDF documents under www.zus.pl/documents/ and a small
set of poradnik landing pages. Per spec, we save raw + sidecar; no parsing.
"""
from __future__ import annotations

import html as html_lib
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

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

BASE = "https://www.zus.pl"
SEEDS = [
    "/baza-wiedzy/biblioteka-zus/poradniki/firmy",
    "/baza-wiedzy/biblioteka-zus/poradniki/archiwum-poradnikow",
    "/baza-wiedzy/skladki-wskazniki-odsetki",
    "/baza-wiedzy/biezace-wyjasnienia-komorek-merytorycznych",
    "/baza-wiedzy/biblioteka-zus/poradniki/swiadczenia-pieniezne-z-ub-spol",
    "/baza-wiedzy/biblioteka-zus/poradniki/przedsiebiorcy",
    "/baza-wiedzy/biblioteka-zus/poradniki/ubezpieczeni",
    "/wzory-formularzy",
]

UA_CHROME = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

PDF_RE = re.compile(r'href="([^"]+\.pdf[^"]*)"', re.I)
ANCHOR_RE = re.compile(r'<a[^>]*href="([^"]+\.pdf[^"]*)"[^>]*>(.*?)</a>', re.I | re.S)

DROP_KEYWORDS = [
    "english", "anglo", "deutsch", "ucraina", "ukrain", "espanol",
    "rolnicz", "ker", "rolnik",
]
KEEP_KEYWORDS = [
    "poradnik", "przewodnik", "kompendium", "informator",
    "zus", "skladk", "składk", "ubezpiecz", "swiadczen", "świadczen",
    "przedsiebiorc", "przedsiębiorc", "dzialalnosc", "działalność",
    "preferenc", "ulga na start", "maly zus", "mały zus",
    "wakacje", "chorobow", "macierz", "emerytur", "rent",
    "wypadkow", "wskazn",
    "zua", "zwua", "dra", "rca", "rzu", "zaa", "zha", "zia", "zsw", "zwpa",
    "kpip", "iwa", "osw", "ria", "kedu",
]


def relative_to_abs(href: str) -> str:
    return urljoin(BASE, href)


def slug_from_url(url: str) -> str:
    path = urlparse(url).path
    raw = path.rstrip("/").split("/")[-1]
    raw = unquote(raw)
    raw = re.sub(r"[^A-Za-z0-9._\-]", "_", raw)
    if not raw.lower().endswith(".pdf"):
        raw = (raw or "doc") + ".pdf"
    return raw[:120]


def passes_filter(title: str, url: str) -> bool:
    blob = (title + " " + unquote(url)).lower()
    if any(k in blob for k in DROP_KEYWORDS):
        return False
    return any(k in blob for k in KEEP_KEYWORDS)


def discover(seeds: list[str], sess) -> dict[str, dict]:
    pdfs: dict[str, dict] = {}
    for path in seeds:
        url = relative_to_abs(path)
        res = fetch(url, sess)
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok:
            continue
        html = res.content.decode("utf-8", errors="replace")
        for m in ANCHOR_RE.finditer(html):
            href = html_lib.unescape(m.group(1))
            anchor = html_lib.unescape(re.sub(r"<[^>]+>", " ", m.group(2))).strip()
            absu = relative_to_abs(href)
            if "zus.pl" not in urlparse(absu).netloc:
                continue
            if absu not in pdfs:
                pdfs[absu] = {"title": anchor, "parent": url}
        time.sleep(0.6)
    return pdfs


def main() -> None:
    sess = session_factory({
        "User-Agent": UA_CHROME,
        "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.5",
    })
    pdfs = discover(SEEDS, sess)
    print(f"\n[zus] discovered {len(pdfs)} PDF candidates")

    manifest = load_manifest()
    have_urls = {r.get("url") for r in manifest}
    have_sha = {r.get("sha256") for r in manifest}

    saved = 0
    skipped = 0
    for url, meta in pdfs.items():
        title = meta["title"] or slug_from_url(url)
        parent = meta["parent"]
        if not passes_filter(title, url):
            skipped += 1
            continue
        if url in have_urls:
            continue
        time.sleep(0.7)
        res = fetch(url, sess, accept="application/pdf")
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok or not magic_ok(res.content, "pdf") or len(res.content) < 2048:
            quarantine(res.content or b"", slug_from_url(url), "_failed", res.error or "magic_or_size")
            continue
        sha = __import__("hashlib").sha256(res.content).hexdigest()
        if sha in have_sha:
            continue
        have_sha.add(sha)
        topics = assign_topics(title, url)
        if not topics:
            lo = (title + " " + unquote(url)).lower()
            if "preferenc" in lo: topics = ["zus_preferencyjny"]
            elif "ulga na start" in lo: topics = ["zus_ulga_na_start"]
            elif "maly zus" in lo or "mały zus" in lo: topics = ["zus_maly_zus_plus"]
            elif "wakacje" in lo: topics = ["zus_wakacje_skladkowe"]
            elif "zdrow" in lo: topics = ["zus_skladka_zdrowotna_jdg"]
            elif "chorob" in lo: topics = ["zus_zasilek_chorobowy_jdg"]
            elif "emerytur" in lo: topics = ["zus_emerytura_jdg"]
            elif "zua" in lo or "zwua" in lo or "dra" in lo: topics = ["zus_zua_zwua_dra"]
            elif "zawiesz" in lo: topics = ["zus_zawieszenie_dzialalnosci"]
            elif "wskazn" in lo or "skladki" in lo or "składki" in lo: topics = ["zus_podstawa_wymiaru"]
            else: topics = ["zus_skladka_zdrowotna_jdg"]
        rel = Path("raw/zus") / slug_from_url(url)
        save_artifact(
            content=res.content,
            rel_path=rel,
            url=url,
            source="zus",
            topic_ids=topics,
            layer="L2",
            fmt="pdf",
            http_status=res.status,
            content_type=res.headers.get("Content-Type", "application/pdf"),
            title=title,
            last_modified=res.headers.get("Last-Modified", ""),
            is_official=True,
            parent_url=parent,
            discovery_source="bfs",
            headers=res.headers,
        )
        saved += 1
        if saved % 5 == 0:
            print(f"  zus saved {saved}")
    print(f"\n[zus] done. saved={saved} skipped={skipped} candidates={len(pdfs)}")


if __name__ == "__main__":
    main()
