"""Focused biznes.gov.pl crawl: only known JDG-relevant portal IDs, longer
hydration wait, fragment-stripped URL dedup. Bootstrap session before
batch crawl."""
import asyncio
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

sys.path.insert(0, "/home/user/diplomma/scripts")
from playwright.async_api import async_playwright
from common import fetch, log_fetch, magic_ok, now_iso, save_artifact, session_factory, load_manifest
from topics import assign_topics

# Known JDG portals with content
PORTAL_IDS = [
    "00115",  # Działalność nierejestrowana
    "00116",  # Lista uprawnień
    "00117",  # Rejestracja firmy
    "00118",  # Umowy
    "00119", "00120", "00124",
    "00161", "00162", "00163", "00164",
    "00170", "00171",  # CEIDG, pracownicy
    "00226", "00228", "00230", "00232", "00233", "00234", "00235", "00236",
    "00237", "00239", "00241",
    "0084", "0091", "0212", "0214", "0215", "0222", "0223", "0224", "0225",
    "0228", "0229", "0232", "026", "0245", "0510", "0516",
    "00151", "00157", "00108",
]

async def main():
    manifest = load_manifest()
    have_url = {r["url"] for r in manifest}
    have_sha = {r["sha256"] for r in manifest}
    asset_links = []
    seen_pages = set()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pl-PL", ignore_https_errors=True)
        page = await ctx.new_page()
        # Bootstrap
        try:
            await page.goto("https://www.biznes.gov.pl/pl", wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"bootstrap warn: {e}")
        await page.wait_for_timeout(2000)
        # Visit each portal directly
        for pid in PORTAL_IDS:
            url = f"https://www.biznes.gov.pl/pl/portal/{pid}"
            if url in seen_pages:
                continue
            seen_pages.add(url)
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(3000)  # longer for hydration
                anchors = await page.evaluate("""() => {
                    const out = [];
                    for (const a of document.querySelectorAll('a[href]')) {
                        out.push({href: a.href, text: (a.innerText||a.textContent||'').trim().slice(0,80)});
                    }
                    return out;
                }""")
                pdf_count = 0
                for a in anchors:
                    href = a.get("href", "")
                    lo = href.lower().split("?")[0].split("#")[0]
                    if lo.endswith((".pdf", ".docx", ".doc", ".xlsx")) and "biznes.gov.pl" in href:
                        asset_links.append((href, a.get("text", ""), url))
                        pdf_count += 1
                print(f"  {pid}: {pdf_count} assets ({len(anchors)} anchors)")
            except Exception as exc:
                print(f"  {pid}: ERR {exc}")
        cookies = await ctx.cookies()
        await browser.close()

    # Dedup by URL (no fragments/query)
    seen_dl = set()
    unique = []
    for u, t, p in asset_links:
        key = u.split("#")[0].split("?")[0]
        if key in seen_dl:
            continue
        seen_dl.add(key)
        unique.append((u, t, p))
    print(f"\nUnique assets to download: {len(unique)}")

    sess = session_factory({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pl-PL,pl;q=0.9",
    })
    for c in cookies:
        sess.cookies.set(c["name"], c["value"], domain=c.get("domain", ""), path=c.get("path", "/"))

    saved_pdf = saved_docx = 0
    for url, title, parent in unique:
        if url in have_url:
            continue
        time.sleep(0.4)
        ext = "docx" if ".docx" in url.lower() else "pdf"
        res = fetch(url, sess, accept="application/pdf" if ext == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok or not magic_ok(res.content, ext) or len(res.content) < 2048:
            continue
        sha = __import__("hashlib").sha256(res.content).hexdigest()
        if sha in have_sha:
            continue
        have_sha.add(sha)
        topics = assign_topics(title, url, parent)
        if not topics:
            topics = ["ceidg_rejestracja"]
        rel_dir = "raw/biznes_gov" if ext == "pdf" else "raw/templates_docx"
        # slug from URL
        name = unquote(urlparse(url).path.rstrip("/").split("/")[-1])
        name = re.sub(r"[^A-Za-z0-9._\-]", "_", name)[:120]
        if not name.lower().endswith(("." + ext)):
            name = (name or "doc") + "." + ext
        rel = Path(rel_dir) / f"bizgov_{name}"
        save_artifact(
            content=res.content, rel_path=rel, url=url, source="biznes_gov",
            topic_ids=topics, layer="L2", fmt=ext, http_status=res.status,
            content_type=res.headers.get("Content-Type", ""), title=title,
            last_modified=res.headers.get("Last-Modified", ""), is_official=True,
            parent_url=parent, discovery_source="playwright_focused", headers=res.headers)
        if ext == "pdf":
            saved_pdf += 1
        else:
            saved_docx += 1
    print(f"\n[biznes focused] saved pdf={saved_pdf} docx={saved_docx}")

asyncio.run(main())
