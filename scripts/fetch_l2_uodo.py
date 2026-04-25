"""UODO publications scraper.

Hub pages list poradniki as `accordion-button` anchors pointing to /pl/{hub}/N
detail pages. Each detail page contains article__downloads__item blocks with
/pl/file/M PDF links. We:
  1. Discover detail-page URLs from hubs (679, 598, 383).
  2. Visit each detail page and extract PDF download anchors.
  3. Filter, fetch, save with sidecar.

Use a Chrome-like UA — UODO returns a 503/empty body for the academic UA.
"""
from __future__ import annotations

import html as html_lib
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

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

BASE = "https://uodo.gov.pl"
HUB_PAGES = [
    "/pl/679",   # Poradniki i wytyczne (current)
    "/pl/598",   # Poradniki i wskazowki (od 2025 r.)
    "/pl/383",   # Poradniki i wskazowki 2018-2020
]
UA_CHROME = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DROP_KEYWORDS = [
    "english", "deutsch", "francais", "espanol", "ucraina", "ukraine",
    "fundamental rights", "border guards", "managers",
    " en ", " de ",
]
KEEP_KEYWORDS = [
    "porad", "wskazow", "rodo", "rcp", "rejestr czynnosci", "rejestr czynności",
    "iod", "inspektor", "ochrony danych", "naruszen", "monitoring",
    "rekrutac", "klauzula", "umowa powierzen", "powierzeni", "administrat",
    "art. 13", "art. 14", "art. 30",
    "mała firma", "mala firma", "pracodawc", "przedsiebiorc", "przedsiębiorc",
    "rekrutac", "cv", "kandydat", "marketing", "newsletter", "kontrola",
    "kompendium", "obowiazek informacyjny", "obowiązek informacyjny",
]


ACCORDION_BTN = re.compile(
    r'<a[^>]*class="[^"]*accordion-button[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
    re.I | re.S,
)
DOWNLOAD_ITEM = re.compile(
    r'<div class="article__downloads__item">.*?'
    r'<a href="(?P<url>https?://[^"]+/pl/file/\d+)"[^>]*>.*?'
    r'<span[^>]*ui-link__text[^>]*>(?P<title>.*?)</span>',
    re.I | re.S,
)


def parse_listing(html: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in DOWNLOAD_ITEM.finditer(html):
        url = m.group("url")
        title = html_lib.unescape(re.sub(r"<[^>]+>", " ", m.group("title"))).strip()
        out.append((url, title))
    return out


def parse_accordion(html: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in ACCORDION_BTN.finditer(html):
        href = html_lib.unescape(m.group(1)).strip()
        text = html_lib.unescape(re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        out.append((href, text))
    return out


def passes_filter(title: str, url: str) -> bool:
    blob = (title + " " + url).lower()
    if any(k in blob for k in DROP_KEYWORDS):
        return False
    return any(k in blob for k in KEEP_KEYWORDS) or "rodo" in blob or "ochrony danych" in blob


def slugify(url: str, title: str) -> str:
    fid = url.rstrip("/").split("/")[-1]
    base = re.sub(r"[^A-Za-z0-9]+", "_", title.lower())[:60].strip("_") or fid
    return f"uodo_{fid}_{base}.pdf"


def main() -> None:
    sess = session_factory({"User-Agent": UA_CHROME})
    all_items: list[tuple[str, str, str]] = []
    detail_pages: list[tuple[str, str]] = []  # (url, hint_title)

    for path in HUB_PAGES:
        url = f"{BASE}{path}"
        res = fetch(url, sess)
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok:
            print(f"  failed {url}: {res.error}")
            continue
        html = res.content.decode("utf-8", errors="replace")
        # Direct PDF items on hub
        items = parse_listing(html)
        for u, t in items:
            all_items.append((u, t, url))
        # Accordion sub-pages
        accordion = parse_accordion(html)
        for sub_href, sub_title in accordion:
            sub_abs = urljoin(BASE, sub_href.strip())
            detail_pages.append((sub_abs, sub_title))
        print(f"{path}: hub_pdfs={len(items)} accordion_subpages={len(accordion)}")
        time.sleep(0.5)

    # Fetch detail pages and extract PDFs
    print(f"\n[uodo] visiting {len(detail_pages)} detail pages")
    for det_url, hint in detail_pages:
        time.sleep(0.6)
        res = fetch(det_url, sess)
        log_fetch({"ts": now_iso(), "url": det_url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok:
            continue
        html = res.content.decode("utf-8", errors="replace")
        items = parse_listing(html)
        for u, t in items:
            # If the file title is empty/generic, fall back on the accordion hint.
            t2 = t or hint
            all_items.append((u, t2, det_url))

    manifest = load_manifest()
    have_urls = {r.get("url") for r in manifest}
    have_sha = {r.get("sha256") for r in manifest}

    saved = 0
    skipped = 0
    for url, title, parent in all_items:
        if url in have_urls:
            continue
        if not passes_filter(title, url):
            skipped += 1
            continue
        time.sleep(0.5)
        res = fetch(url, sess, accept="application/pdf")
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok or not magic_ok(res.content, "pdf") or len(res.content) < 2048:
            quarantine(res.content or b"", slugify(url, title), "_failed", res.error or "magic_or_size")
            continue
        sha = __import__("hashlib").sha256(res.content).hexdigest()
        if sha in have_sha:
            continue
        have_sha.add(sha)
        topics = assign_topics(title, url)
        if not topics:
            topics = ["rodo_mala_firma"]
        rel = Path("raw/uodo") / slugify(url, title)
        save_artifact(
            content=res.content,
            rel_path=rel,
            url=url,
            source="uodo",
            topic_ids=topics,
            layer="L2",
            fmt="pdf",
            http_status=res.status,
            content_type=res.headers.get("Content-Type", "application/pdf"),
            title=title,
            last_modified=res.headers.get("Last-Modified", ""),
            is_official=True,
            parent_url=parent,
            discovery_source="article_downloads",
            headers=res.headers,
        )
        saved += 1
        if saved % 5 == 0:
            print(f"  uodo saved {saved}")
    print(f"\n[uodo] done. saved={saved} skipped={skipped} total_candidates={len(all_items)}")


if __name__ == "__main__":
    main()
