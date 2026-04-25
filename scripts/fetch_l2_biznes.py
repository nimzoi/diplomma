"""biznes.gov.pl scraper using Playwright (chromium-headless-shell).

Strategy:
  1. Open the SPA homepage to bootstrap the session.
  2. Navigate to the index page of opisy procedur ("Sprawy do załatwienia"
     /pl/opisy-procedur or /pl/portal/00235 / /pl/firma) and let JS render.
  3. Collect all on-page links to /pl/opisy-procedur/...
  4. Visit each procedure page; extract every PDF / DOCX link.
  5. Download those binaries with the cookies the browser session collected.

We persist the storage_state so re-runs reuse session cookies.
"""
from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).parent))
from common import (
    DATA_DIR,
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

BASE = "https://www.biznes.gov.pl"
SEED_LISTING_URLS = [
    "/pl/opisy-procedur",
    "/pl/firma/zakladanie-firmy",
    "/pl/firma/podatki-i-ksiegowosc",
    "/pl/firma/pracownicy-w-firmie",
    "/pl/firma/zamykanie-firmy",
    "/pl/firma/zawieszenie-i-wznowienie",
    "/pl/firma/sprawy-urzedowe",
    "/pl/firma/obowiazki-przedsiebiorcy",
    "/pl/firma/rozwoj-firmy",
    "/pl/firma/ubezpieczenia-spoleczne",
    # Direct portal IDs that we already know contain JDG topics
    "/pl/portal/00115",  # Działalność nierejestrowana
    "/pl/portal/00116",  # Lista uprawnień / koncesje
    "/pl/portal/00117",  # Rejestracja firmy
    "/pl/portal/00118",  # Umowa o pracę
    "/pl/portal/00170",  # CEIDG
    "/pl/portal/00171",  # Pracownik
    "/pl/portal/00226",  # ZUS
    "/pl/portal/00228",
    "/pl/portal/00230",
    "/pl/portal/00233",
    "/pl/portal/00235",  # PIT
    "/pl/portal/00236",
    "/pl/portal/00237",
    "/pl/portal/00239",
    "/pl/portal/00241",
    "/pl/portal/0510",
    "/pl/portal/0516",
]

JDG_KEEP_KEYWORDS = (
    "ceidg", "vat", "pit", "ryczalt", "ryczałt", "zus", "umowa",
    "rejestracj", "zawiesz", "wznowien", "zamknięci", "wykreśle",
    "zmiana", "kpir", "ksef", "jpk", "amortyz", "ip box", "skladk",
    "składk", "rodo", "klauzul", "iod", "monitoring", "rekrutacj",
    "ubezpiec", "zwolnien", "wypowied", "urlop", "świadectw",
    "działalność", "działalnosc", "dzialalnosc", "pkd", "regon",
    "podatek", "fakt", "ewidencj",
)
JDG_DROP_KEYWORDS = (
    "akcyza", "celne", "cło", "transgraniczn", "wojska", "rolnictw",
    "lasów", "zwierząt", "leśnictw", "loterie", "hazard", "morsk",
    "lotnisko", "broń", "narkotyk", "alkohol", "reklam", "muzeum",
    "zabytk", "rodzic-zastępczy", "obraz cyfrow",
)


def slug_from_url(url: str) -> str:
    p = urlparse(url)
    name = unquote(p.path.rstrip("/").split("/")[-1])
    name = re.sub(r"[^A-Za-z0-9._\-]", "_", name)
    return name[:120] or "doc"


def title_relevant(title: str, url: str) -> bool:
    blob = (title + " " + url).lower()
    if any(k in blob for k in JDG_DROP_KEYWORDS):
        return False
    return any(k in blob for k in JDG_KEEP_KEYWORDS)


async def collect_links(playwright_page, url: str, depth: int = 0, max_depth: int = 1) -> list[tuple[str, str, str]]:
    """Return list of (url, anchor_text, parent_url) for procedure links + asset (pdf/docx) links."""
    found: list[tuple[str, str, str]] = []
    print(f"  visit (depth={depth}): {url}")
    try:
        await playwright_page.goto(url, wait_until="networkidle", timeout=30000)
    except Exception as exc:
        print(f"    error visiting {url}: {exc}")
        return found
    # Pause for hydration + any lazy-loaded content
    await playwright_page.wait_for_timeout(2000)
    # Use absolute href (.href) instead of getAttribute (which gives relative)
    anchors = await playwright_page.evaluate("""() => {
        const out = [];
        for (const a of document.querySelectorAll('a[href]')) {
            const href = a.href || '';
            const text = (a.innerText || a.textContent || '').trim();
            if (href) out.push({href, text});
        }
        return out;
    }""")

    for a in anchors:
        href = a.get("href", "")
        if not href or href.startswith(("javascript:", "mailto:", "#")):
            continue
        absolute = href if href.startswith("http") else urljoin(url, href)
        host = urlparse(absolute).netloc.lower()
        # Accept biznes.gov.pl, pliki.biznes.gov.pl, media.biznes.gov.pl
        if "biznes.gov.pl" not in host:
            continue
        anchor_text = a.get("text", "")
        found.append((absolute, anchor_text, url))
    return found


async def main() -> None:
    seen_urls: set[str] = set()
    manifest = load_manifest()
    have_url = {r["url"] for r in manifest}
    have_sha = {r["sha256"] for r in manifest}

    saved_pdf = 0
    saved_docx = 0
    procedure_links: list[tuple[str, str, str]] = []
    asset_links: list[tuple[str, str, str]] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="pl-PL",
            ignore_https_errors=True,
        )
        page = await context.new_page()
        # Bootstrap: open homepage to drop session cookies
        try:
            await page.goto(f"{BASE}/pl", wait_until="networkidle", timeout=30000)
        except Exception as exc:
            print(f"  bootstrap warn: {exc}")
        await page.wait_for_timeout(1000)

        # Crawl seed listing pages
        for path in SEED_LISTING_URLS:
            url = BASE + path
            if url in seen_urls:
                continue
            seen_urls.add(url)
            links = await collect_links(page, url)
            for u, t, p in links:
                lo = u.lower().split("?")[0]
                if lo.endswith((".pdf", ".docx", ".doc", ".xlsx")):
                    asset_links.append((u, t, p))
                elif "/opisy-procedur/" in u or "/portal/" in u or "/firma/" in u:
                    procedure_links.append((u, t, p))
            await page.wait_for_timeout(600)

        # Visit a sample of procedure pages (cap to avoid endless crawl)
        proc_seen: set[str] = set()
        for u, t, p in procedure_links:
            if u in proc_seen or u in seen_urls:
                continue
            proc_seen.add(u)
            seen_urls.add(u)
            if not title_relevant(t, u):
                continue
            if len(proc_seen) > 80:
                break
            sub = await collect_links(page, u, depth=1)
            for su, st, sp in sub:
                lo = su.lower().split("?")[0]
                if lo.endswith((".pdf", ".docx", ".doc", ".xlsx")):
                    asset_links.append((su, st, sp))
            await page.wait_for_timeout(400)

        # Pass cookies to a requests session for binary downloads
        cookies = await context.cookies()
        await browser.close()

    sess = session_factory({
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pl-PL,pl;q=0.9",
    })
    for c in cookies:
        sess.cookies.set(c["name"], c["value"], domain=c.get("domain", ""), path=c.get("path", "/"))

    print(f"\n[biznes] discovered procedures={len(procedure_links)} assets={len(asset_links)}")
    seen_assets: set[str] = set()
    for url, title, parent in asset_links:
        if url in seen_assets or url in have_url:
            continue
        seen_assets.add(url)
        title = title.strip() or slug_from_url(url)
        if not title_relevant(title, url):
            continue
        ext = "docx" if url.lower().split("?")[0].endswith(".docx") else "pdf"
        time.sleep(0.4)
        res = fetch(url, sess, accept="application/pdf" if ext == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok or not magic_ok(res.content, ext) or len(res.content) < 2048:
            quarantine(res.content or b"", slug_from_url(url), "_failed", res.error or "magic_or_size")
            continue
        sha = __import__("hashlib").sha256(res.content).hexdigest()
        if sha in have_sha:
            continue
        have_sha.add(sha)
        topics = assign_topics(title, url, parent)
        if not topics:
            topics = ["ceidg_rejestracja"]  # default for biznes.gov.pl context
        rel_dir = "raw/biznes_gov" if ext == "pdf" else "raw/templates_docx"
        rel = Path(rel_dir) / f"bizgov_{slug_from_url(url)}"
        save_artifact(
            content=res.content,
            rel_path=rel,
            url=url,
            source="biznes_gov",
            topic_ids=topics,
            layer="L2",
            fmt=ext,
            http_status=res.status,
            content_type=res.headers.get("Content-Type", ""),
            title=title,
            last_modified=res.headers.get("Last-Modified", ""),
            is_official=True,
            parent_url=parent,
            discovery_source="playwright",
            headers=res.headers,
        )
        if ext == "pdf":
            saved_pdf += 1
        else:
            saved_docx += 1
        if (saved_pdf + saved_docx) % 5 == 0:
            print(f"  saved pdf={saved_pdf} docx={saved_docx}")

    print(f"\n[biznes] done. pdf={saved_pdf} docx={saved_docx}")


if __name__ == "__main__":
    asyncio.run(main())
