"""Scrape podatki.gov.pl - PDF brochures and structured pages.

Strategy: BFS from a curated set of seeds (since spec paths are stale).
Filter PDF links by JDG-relevant keywords, fetch only PDFs (HTML pages are
crawled for discovery only, not saved). Save absolute URLs unique by hash.
"""
from __future__ import annotations

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

BASE = "https://www.podatki.gov.pl"

SEED_URLS = [
    f"{BASE}/abc-podatkow/broszury-informacyjne/broszury-pit/",
    f"{BASE}/poradniki-i-informatory/",
    f"{BASE}/podatki-firmowe/vat/",
    f"{BASE}/podatki-firmowe/jednolity-plik-kontrolny/jpk_vat-z-deklaracja/",
    f"{BASE}/podatki-firmowe/pit/informacje-podstawowe/",
    f"{BASE}/podatki-firmowe/cit/informacje-podstawowe/",
    f"{BASE}/podatki-osobiste/pit/informacje-podstawowe/",
    f"{BASE}/podatki-osobiste/pit/stawki-i-limity/",
    f"{BASE}/podatki-osobiste/pit/ulgi-i-odliczenia/",
    f"{BASE}/podatki-osobiste/pit/informacje-podstawowe/co-jest-opodatkowane/dochody-z-dzialalnosci-nierejestrowanej/",
    f"{BASE}/podatki-osobiste/pit/informacje-podstawowe/co-jest-opodatkowane/dochody-z-umowy-zlecenia-lub-o-dzielo/",
    f"{BASE}/narzedzia/white-list/",
    f"{BASE}/e-deklaracje/",
    f"{BASE}/interpretacje-podatkowe/",
]

ALLOW_HOST = {"www.podatki.gov.pl", "podatki.gov.pl"}
PDF_EXT_RE = re.compile(r"\.pdf(\?|$)", re.I)
HREF_RE = re.compile(r'href="([^"]+)"', re.I)
TITLE_TAG_RE = re.compile(r"<title>([^<]+)</title>", re.I)

# JDG-relevant keywords for filtering
KEYWORDS_RELEVANT = [
    "pit", "vat", "jpk", "ksef", "ryczalt", "ryczałt", "skala", "liniow",
    "ip box", "amortyzacj", "kpir", "ksiega", "księga", "ewidencj", "faktur",
    "biala lista", "biała lista", "pkd", "ceidg", "dzialalnosc", "działalnosc",
    "działalność", "ulga", "kalendarz", "obywatele", "interpretac",
    "swiad", "świad", "podatnik", "stawk",
]
KEYWORDS_DROP = [
    "akcyza", "celne", "globe", "alkohol", "okupacja", "krym",
    "rolnictwo", "myto", "kopaliny", "loterie", "hazard",
]


def normalize_url(u: str) -> str:
    parsed = urlparse(u)
    if not parsed.scheme:
        return u
    netloc = parsed.netloc.lower()
    path = parsed.path
    return f"{parsed.scheme}://{netloc}{path}"


def link_score(text_blob: str, url: str) -> int:
    """Higher score = more relevant for JDG. Negative if drop keyword present."""
    blob = (text_blob + " " + url).lower()
    score = 0
    for kw in KEYWORDS_RELEVANT:
        if kw in blob:
            score += 1
    for kw in KEYWORDS_DROP:
        if kw in blob:
            score -= 5
    return score


def slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = parsed.path.rstrip("/").split("/")[-1]
    name = name.replace("%20", "_").replace(" ", "_")
    if not name.lower().endswith(".pdf"):
        name = (name or "doc") + ".pdf"
    name = re.sub(r"[^A-Za-z0-9._\-]", "_", name)
    return name[:120]


def crawl_listing(seed_url: str, sess) -> list[tuple[str, str]]:
    """Return (absolute_url, anchor_text) pairs of all links found on a listing page."""
    res = fetch(seed_url, session=sess)
    log_fetch({"ts": now_iso(), "url": seed_url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
    if not res.ok:
        return []
    html = res.content.decode("utf-8", errors="replace")
    out = []
    # crude anchor extractor: get href + 200 chars of context
    for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.I | re.S):
        href = m.group(1)
        anchor = re.sub(r"<[^>]+>", " ", m.group(2)).strip()
        absolute = urljoin(seed_url, href)
        out.append((absolute, anchor))
    return out


def collect_pdf_links(seeds: list[str], sess) -> dict[str, dict]:
    """BFS depth=1 over seeds collecting PDF links, deduped by URL.
    Returns dict url -> {anchor, parent}."""
    pdfs: dict[str, dict] = {}
    visited: set[str] = set()
    queue: list[tuple[str, int]] = [(s, 0) for s in seeds]
    while queue:
        url, depth = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        host = urlparse(url).netloc.lower()
        if host not in ALLOW_HOST:
            continue
        links = crawl_listing(url, sess)
        for abs_url, anchor in links:
            host2 = urlparse(abs_url).netloc.lower()
            if host2 not in ALLOW_HOST:
                continue
            if PDF_EXT_RE.search(abs_url):
                if abs_url not in pdfs:
                    pdfs[abs_url] = {"anchor": anchor, "parent": url}
            elif depth == 0:
                # only follow internal links one level (limited expansion)
                # take a few "informacje" or "broszury" sublinks per seed
                if any(k in abs_url.lower() for k in ("/broszur", "/informator", "/poradnik", "/abc-podatkow", "informacje")):
                    if abs_url not in visited and len(visited) < 80:
                        queue.append((abs_url, 1))
        time.sleep(0.5)
    return pdfs


def main() -> None:
    sess = session_factory()
    pdfs = collect_pdf_links(SEED_URLS, sess)
    print(f"\nDiscovered {len(pdfs)} PDF candidates")

    manifest = load_manifest()
    have_urls = {r.get("url") for r in manifest}
    have_sha = {r.get("sha256") for r in manifest}

    saved = 0
    skipped_irrelevant = 0
    for url, meta in pdfs.items():
        anchor = meta["anchor"]
        parent = meta["parent"]
        score = link_score(anchor, url)
        if score <= 0:
            skipped_irrelevant += 1
            continue
        if url in have_urls:
            continue
        time.sleep(0.6)
        res = fetch(url, sess, accept="application/pdf")
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok or not magic_ok(res.content, "pdf") or len(res.content) < 2048:
            quarantine(res.content or b"", slug_from_url(url), "_failed", res.error or "magic_or_size")
            continue
        sha = __import__("hashlib").sha256(res.content).hexdigest()
        if sha in have_sha:
            continue
        have_sha.add(sha)
        title = anchor or slug_from_url(url)
        topics = assign_topics(title, url)
        if not topics:
            skipped_irrelevant += 1
            continue
        rel = Path("raw/podatki") / slug_from_url(url)
        save_artifact(
            content=res.content,
            rel_path=rel,
            url=url,
            source="podatki",
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
            print(f"  saved {saved} so far...")
    print(f"\nDone podatki.gov.pl: saved={saved} skipped_irrelevant={skipped_irrelevant}")


if __name__ == "__main__":
    main()
