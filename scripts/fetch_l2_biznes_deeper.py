"""Deeper biznes.gov.pl crawl: visit additional /pl/portal/{id} URLs that were
discovered as cross-links inside the first 60 pages. Same render-DOM-as-HTML
strategy.
"""
from __future__ import annotations

import asyncio
import hashlib
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

sys.path.insert(0, str(Path(__file__).parent))
from playwright.async_api import async_playwright
from common import (
    fetch,
    log_fetch,
    magic_ok,
    now_iso,
    save_artifact,
    session_factory,
    load_manifest,
)
from topics import assign_topics

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# JDG-relevant filter on portal ID anchor text — only visit when keywords match
JDG_KEEP = re.compile(
    r"(jdg|firm|przedsi[ęe]bior|dzia[lł]aln|"
    r"vat|pit|ryczalt|ryczałt|ksef|jpk|kp[ip]r|kpir|"
    r"zus|skladk|sk[lł]adk|emerytur|chorobow|"
    r"ceidg|pkd|rejestrac|zawiesz|wznowien|zamkni|"
    r"umow|prac|urlop|wypowiedz|swiadectw|świadectw|"
    r"rodo|ochron[a-zżźćń]+ danych|monitorin|iod|"
    r"faktur|paragon|kasa fiskaln|"
    r"nieuczciw|konsumenc|reklam|gwaranc|"
    r"podat|nip|regon|"
    r"dotacj|pomoc|de minimis|parp|"
    r"e-doreczeni|e-doręczeni|ade|"
    r"b2b|samozatrudn|"
    r"przeksztal|likwidac|zmiana wpisu|"
    r"import|eksport|wewn[a-zżźćń]+wsp[oó]ln|"
    r"fakto|cesja|wierzy|"
    r"sygnali|whistleblow)",
    re.I,
)

EXPAND_BUTTON_SELECTORS = [
    "button[aria-expanded='false']",
    ".accordion-button.collapsed",
    "[data-bs-toggle='collapse'][aria-expanded='false']",
]


def slug_from(url: str) -> str:
    p = urlparse(url)
    name = unquote(p.path.rstrip("/").split("/")[-1])
    return re.sub(r"[^A-Za-z0-9._\-]", "_", name)[:120]


async def expand_all(page) -> None:
    for sel in EXPAND_BUTTON_SELECTORS:
        try:
            handles = await page.query_selector_all(sel)
            for h in handles[:30]:
                try:
                    await h.click(timeout=1500, force=True)
                    await page.wait_for_timeout(150)
                except Exception:
                    continue
        except Exception:
            continue


def discover_new_portals() -> set[str]:
    """Mine cross-links from already-saved biznes_html files."""
    base = Path("data/raw/biznes_html")
    crawled: set[str] = set()
    found: set[str] = set()
    if not base.exists():
        return found
    for p in base.glob("*.html"):
        name = p.stem
        m = re.match(r"bizgov_([0-9]+)$", name)
        if m:
            crawled.add(m.group(1))
        try:
            html = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        # find anchor + nearby text for relevance filter
        for m in re.finditer(r'<a[^>]*href="[^"]*?/pl/portal/(\d{3,6})"[^>]*>(.*?)</a>',
                             html, re.S | re.I):
            pid = m.group(1)
            if pid in crawled:
                continue
            anchor = re.sub(r"<[^>]+>", " ", m.group(2)).strip()
            if JDG_KEEP.search(anchor):
                found.add(pid)
    return found


async def main() -> None:
    portal_ids = discover_new_portals()
    # Cap to 80 to respect time
    targets = sorted(portal_ids)[:80]
    print(f"[biznes_deeper] {len(portal_ids)} new candidates, visiting first {len(targets)}")

    manifest = load_manifest()
    have_url = {r.get("url", "") for r in manifest}
    have_sha = {r.get("sha256", "") for r in manifest}

    saved_html = 0
    asset_pool: list[tuple[str, str, str]] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent=UA, locale="pl-PL", ignore_https_errors=True,
        )
        page = await ctx.new_page()
        try:
            await page.goto("https://www.biznes.gov.pl/pl",
                            wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
        except Exception as exc:
            print(f"bootstrap warn: {exc}")

        for pid in targets:
            url = f"https://www.biznes.gov.pl/pl/portal/{pid}"
            if url in have_url:
                continue
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2500)
                await expand_all(page)
                await page.wait_for_timeout(700)
                title = await page.title()
                body_len = await page.evaluate("document.body.innerText.length")
                if "Nie znaleziono" in title or body_len < 1500:
                    print(f"  thin/404 {pid} body_len={body_len}")
                    continue
                html = await page.content()
                content = html.encode("utf-8")
                sha = hashlib.sha256(content).hexdigest()
                if sha in have_sha:
                    continue
                have_sha.add(sha)
                topics = assign_topics(title, html[:8000], url)
                if not topics:
                    topics = ["ceidg_rejestracja"]
                rel = Path("raw/biznes_html") / f"bizgov_{pid}.html"
                save_artifact(
                    content=content, rel_path=rel, url=url, source="biznes_gov",
                    topic_ids=topics, layer="L2", fmt="html",
                    http_status=200, content_type="text/html",
                    title=title, is_official=True,
                    discovery_source="playwright_deeper",
                    extra_notes=f"rendered DOM, body_text={body_len}",
                )
                saved_html += 1
                print(f"  saved {pid} ({body_len} chars)")
                # collect asset links
                anchors = await page.evaluate("""() => {
                    const out = [];
                    for (const a of document.querySelectorAll('a[href]')) {
                        out.push({href: a.href || '', text: (a.innerText||a.textContent||'').trim().slice(0,120)});
                    }
                    return out;
                }""")
                for a in anchors:
                    href = a.get("href", "")
                    lo = href.lower().split("?")[0].split("#")[0]
                    if not lo.endswith((".pdf", ".docx")):
                        continue
                    if "biznes.gov.pl" not in href:
                        continue
                    asset_pool.append((href, a.get("text", ""), url))
            except Exception as exc:
                print(f"  ERR {pid}: {type(exc).__name__}")
        cookies = await ctx.cookies()
        await browser.close()

    sess = session_factory({"User-Agent": UA, "Accept-Language": "pl-PL,pl;q=0.9"})
    for c in cookies:
        sess.cookies.set(c["name"], c["value"], domain=c.get("domain", ""), path=c.get("path", "/"))

    saved_pdf = 0
    seen_assets: set[str] = set()
    for url, anchor, parent in asset_pool:
        key = url.split("?")[0].split("#")[0]
        if key in seen_assets or url in have_url:
            continue
        seen_assets.add(key)
        time.sleep(0.4)
        ext = "docx" if ".docx" in url.lower().split("?")[0] else "pdf"
        r = fetch(url, sess)
        log_fetch({"ts": now_iso(), "url": url, "ok": r.ok, "status": r.status, "bytes": len(r.content)})
        if not r.ok or len(r.content) < 2048 or not magic_ok(r.content, ext):
            continue
        sha = hashlib.sha256(r.content).hexdigest()
        if sha in have_sha:
            continue
        have_sha.add(sha)
        topics = assign_topics(anchor, url, parent) or ["ceidg_rejestracja"]
        rel_dir = "raw/biznes_gov" if ext == "pdf" else "raw/templates_docx"
        rel = Path(rel_dir) / f"bizgov_{slug_from(url)}.{ext}"
        save_artifact(
            content=r.content, rel_path=rel, url=url, source="biznes_gov",
            topic_ids=topics, layer="L2", fmt=ext,
            http_status=r.status, content_type=r.headers.get("Content-Type", ""),
            title=anchor or slug_from(url), is_official=True, parent_url=parent,
            discovery_source="playwright_deeper", headers=r.headers,
        )
        saved_pdf += 1

    print(f"\n[biznes_deeper] html={saved_html} pdf={saved_pdf}")


if __name__ == "__main__":
    asyncio.run(main())
