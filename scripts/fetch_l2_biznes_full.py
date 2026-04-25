"""biznes.gov.pl — pełny crawl rendered DOM jako kontent.

Strategia:
  1. Playwright bootstrap session (visit homepage, accept cookies).
  2. Dla każdego /pl/portal/{id} (curated list of JDG-relevant portals):
     - goto domcontentloaded + 4s hydration
     - rozwiń wszystkie accordion / "Pokaż więcej" buttons (klik)
     - jeśli body innerText >= 2000 chars → save outerHTML jako kontent
     - ekstrakcja wszystkich linków PDF/DOCX z DOM (pliki.biznes, media.biznes,
       static.biznes itp.) + download

Saves to data/raw/biznes_gov/ (PDF) i data/raw/biznes_html/ (HTML pages).
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

# Curated JDG-relevant /pl/portal/{id} + /pl/firma/* pages.
# Discovered earlier via crawl of /pl/firma/*
PORTAL_TARGETS = [
    # Direct JDG topics
    "/pl/portal/00115",  # Działalność nierejestrowana
    "/pl/portal/00116",  # Lista uprawnień
    "/pl/portal/00117",  # Rejestracja firmy
    "/pl/portal/00118",  # Umowa o pracę
    "/pl/portal/00119",
    "/pl/portal/00120",
    "/pl/portal/00124",
    "/pl/portal/0510",
    "/pl/portal/0516",
    "/pl/portal/00161",
    "/pl/portal/00162",
    "/pl/portal/00163",
    "/pl/portal/00164",
    "/pl/portal/00170",
    "/pl/portal/00171",
    "/pl/portal/00226",
    "/pl/portal/00228",
    "/pl/portal/00230",
    "/pl/portal/00232",
    "/pl/portal/00233",
    "/pl/portal/00234",
    "/pl/portal/00235",
    "/pl/portal/00236",
    "/pl/portal/00237",
    "/pl/portal/00239",
    "/pl/portal/00241",
    "/pl/portal/0091",
    "/pl/portal/0212",
    "/pl/portal/0214",
    "/pl/portal/0215",
    "/pl/portal/0222",
    "/pl/portal/0223",
    "/pl/portal/0224",
    "/pl/portal/0225",
    "/pl/portal/0228",
    "/pl/portal/0229",
    "/pl/portal/0232",
    "/pl/portal/026",
    "/pl/portal/0244",
    "/pl/portal/0245",
    "/pl/portal/0253",
    "/pl/portal/02132",
    "/pl/portal/02140",
    "/pl/portal/02141",
    "/pl/portal/02145",
    "/pl/portal/02148",
    "/pl/portal/02149",
    "/pl/portal/00151",
    "/pl/portal/00157",
    "/pl/portal/00108",
    "/pl/portal/0084",
    # /pl/firma/* hub pages
    "/pl/firma",
    "/pl/firma/zakladanie-firmy",
    "/pl/firma/podatki-i-ksiegowosc",
    "/pl/firma/pracownicy-w-firmie",
    "/pl/firma/zamykanie-firmy",
    "/pl/firma/zawieszenie-i-wznowienie",
    "/pl/firma/sprawy-urzedowe",
    "/pl/firma/obowiazki-przedsiebiorcy",
    "/pl/firma/rozwoj-firmy",
    "/pl/firma/ubezpieczenia-spoleczne",
    "/pl/firma/dotacje-i-dofinansowania",
    "/pl/firma/handel-zagraniczny",
    "/pl/firma/inwestycje-budowlane",
]

ASSET_HOSTS = ("biznes.gov.pl", "pliki.biznes.gov.pl", "media.biznes.gov.pl")
EXPAND_BUTTON_SELECTORS = [
    "button[aria-expanded='false']",
    ".accordion-button.collapsed",
    "[data-bs-toggle='collapse'][aria-expanded='false']",
    "button.collapsed",
]


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


def slug_from(url: str) -> str:
    p = urlparse(url)
    name = unquote(p.path.rstrip("/").split("/")[-1])
    return re.sub(r"[^A-Za-z0-9._\-]", "_", name)[:120]


async def main() -> None:
    manifest = load_manifest()
    have_url = {r.get("url", "") for r in manifest}
    have_sha = {r.get("sha256", "") for r in manifest}

    saved_html = 0
    saved_pdf = 0
    saved_docx = 0
    asset_pool: list[tuple[str, str, str]] = []  # (url, anchor_text, parent)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent=UA,
            locale="pl-PL",
            ignore_https_errors=True,
        )
        page = await ctx.new_page()

        # Bootstrap
        try:
            await page.goto("https://www.biznes.gov.pl/pl", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
        except Exception as exc:
            print(f"bootstrap warn: {exc}")

        for path in PORTAL_TARGETS:
            url = f"https://www.biznes.gov.pl{path}"
            if url in have_url:
                continue
            print(f"\n>>> {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)
                # Expand all collapsible content
                await expand_all(page)
                await page.wait_for_timeout(1000)

                body_len = await page.evaluate("document.body.innerText.length")
                title = await page.title()
                # detect 404 / "Nie znaleziono"
                if "Nie znaleziono" in title or body_len < 1500:
                    print(f"  thin/404 body_len={body_len} title={title[:60]!r}")
                    continue

                # 1) Save rendered HTML as content
                html = await page.content()
                content = html.encode("utf-8")
                sha = hashlib.sha256(content).hexdigest()
                if sha not in have_sha:
                    have_sha.add(sha)
                    topics = assign_topics(title, path)
                    if not topics:
                        topics = ["ceidg_rejestracja"]
                    rel = Path("raw/biznes_html") / f"bizgov_{slug_from(url)}.html"
                    save_artifact(
                        content=content,
                        rel_path=rel,
                        url=url,
                        source="biznes_gov",
                        topic_ids=topics,
                        layer="L2",
                        fmt="html",
                        http_status=200,
                        content_type="text/html",
                        title=title,
                        is_official=True,
                        discovery_source="playwright_render",
                        extra_notes=f"rendered DOM, body_text={body_len}",
                    )
                    saved_html += 1
                    print(f"  HTML saved ({body_len} chars body)")

                # 2) Extract all PDF/DOCX links from rendered DOM
                anchors = await page.evaluate("""() => {
                    const out = [];
                    for (const a of document.querySelectorAll('a[href]')) {
                        const h = a.href || '';
                        out.push({href: h, text: (a.innerText||a.textContent||'').trim().slice(0, 120)});
                    }
                    return out;
                }""")
                for a in anchors:
                    href = a.get("href", "")
                    if not href:
                        continue
                    lo = href.lower().split("?")[0].split("#")[0]
                    if not lo.endswith((".pdf", ".docx", ".doc", ".xlsx")):
                        continue
                    host = urlparse(href).netloc.lower()
                    if not any(h in host for h in ASSET_HOSTS):
                        continue
                    asset_pool.append((href, a.get("text", ""), url))
            except Exception as exc:
                print(f"  ERR {url}: {type(exc).__name__}: {exc}")

        # capture cookies for download phase
        cookies = await ctx.cookies()
        await browser.close()

    # 3) Download discovered PDFs/DOCX with the cookies
    sess = session_factory({"User-Agent": UA, "Accept-Language": "pl-PL,pl;q=0.9"})
    for c in cookies:
        sess.cookies.set(c["name"], c["value"], domain=c.get("domain", ""), path=c.get("path", "/"))

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
        if not r.ok or len(r.content) < 2048:
            continue
        if not magic_ok(r.content, ext):
            continue
        sha = hashlib.sha256(r.content).hexdigest()
        if sha in have_sha:
            continue
        have_sha.add(sha)
        topics = assign_topics(anchor, url, parent)
        if not topics:
            topics = ["ceidg_rejestracja"]
        rel_dir = "raw/biznes_gov" if ext == "pdf" else "raw/templates_docx"
        rel = Path(rel_dir) / f"bizgov_{slug_from(url)}.{ext}"
        save_artifact(
            content=r.content,
            rel_path=rel,
            url=url,
            source="biznes_gov",
            topic_ids=topics,
            layer="L2",
            fmt=ext,
            http_status=r.status,
            content_type=r.headers.get("Content-Type", ""),
            title=anchor or slug_from(url),
            last_modified=r.headers.get("Last-Modified", ""),
            is_official=True,
            parent_url=parent,
            discovery_source="playwright_render",
            headers=r.headers,
        )
        if ext == "pdf":
            saved_pdf += 1
        else:
            saved_docx += 1

    print(f"\n[biznes_full] html={saved_html} pdf={saved_pdf} docx={saved_docx}")


if __name__ == "__main__":
    asyncio.run(main())
