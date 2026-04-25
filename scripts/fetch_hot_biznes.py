"""Hot-2025/2026 collector — biznes.gov.pl Playwright SSR HTML fetcher.

Targets specific portal IDs that cover the 11 uncovered hot topics:
DAC7, kasa fiskalna online, cudzoziemcy, estoński CIT, CRBR,
przekształcenie JDG, faktoring, b2b/UOP, ulga ekspansja, JPK_CIT,
pomoc de minimis.

Saves SSR-rendered HTML (post-hydration). Whitelist-first: explicit
list of portal IDs, no general crawl (avoids the gov.pl attachment
bloat lesson). Each saved page goes through topics.assign_topics +
explicit topic_hint fallback.
"""
from __future__ import annotations

import asyncio
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.async_api import async_playwright

from common import log_fetch, magic_ok, now_iso, save_artifact, load_manifest
from topics import assign_topics

UA_CHROME = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Portal/publication targets per hot topic (whitelist).
TARGETS: list[tuple[str, str]] = [
    # DAC7
    ("https://www.biznes.gov.pl/pl/portal/005075", "dac7_platformy"),
    # CRBR
    ("https://www.biznes.gov.pl/pl/portal/00165", "crbr_beneficjent_rzeczywisty"),
    # Kasa fiskalna online
    ("https://www.biznes.gov.pl/pl/portal/00243", "kasa_fiskalna_online"),
    ("https://www.biznes.gov.pl/pl/portal/02769", "kasa_fiskalna_online"),
    ("https://www.biznes.gov.pl/pl/portal/ou1575", "kasa_fiskalna_online"),
    ("https://www.biznes.gov.pl/pl/portal/ou1649", "kasa_fiskalna_online"),
    ("https://www.biznes.gov.pl/pl/portal/ou1650", "kasa_fiskalna_online"),
    # Cudzoziemcy
    ("https://www.biznes.gov.pl/pl/portal/0613", "zatrudnianie_cudzoziemcow"),
    ("https://www.biznes.gov.pl/pl/portal/0241", "zatrudnianie_cudzoziemcow"),
    ("https://www.biznes.gov.pl/pl/portal/0235", "zatrudnianie_cudzoziemcow"),
    ("https://www.biznes.gov.pl/pl/portal/00214", "zatrudnianie_cudzoziemcow"),
    ("https://www.biznes.gov.pl/pl/portal/ou1610", "zatrudnianie_cudzoziemcow"),
    # Estoński CIT
    ("https://www.biznes.gov.pl/pl/portal/001171", "estonski_cit"),
    ("https://www.biznes.gov.pl/pl/portal/00251", "estonski_cit"),
    ("https://www.biznes.gov.pl/pl/portal/ou78", "estonski_cit"),
    # Ulga ekspansja / podatkowe wsparcie
    ("https://www.biznes.gov.pl/pl/portal/001139", "ulga_ekspansja_prototyp_robotyzacja"),
    # Pomoc publiczna / de minimis
    ("https://www.biznes.gov.pl/pl/publikacje/3295-informacje", "pomoc_de_minimis"),
    ("https://www.biznes.gov.pl/pl/publikacje/3854-co-musisz-wiedziec-jesli-chcesz-uzyskac-pomoc-publiczna", "pomoc_de_minimis"),
    ("https://www.biznes.gov.pl/pl/publikacje/3867-na-czym-polegaja-ulgi-w-platnosciach-wobec-us-i-zus", "pomoc_de_minimis"),
    # Przekształcenie JDG -> sp. z o.o.
    ("https://www.biznes.gov.pl/pl/portal/00110", "przeksztalcenie_jdg_spzoo"),
    ("https://www.biznes.gov.pl/pl/portal/0259", "przeksztalcenie_jdg_spzoo"),
    # Faktoring / split payment / cesja
    ("https://www.biznes.gov.pl/pl/portal/001266K", "faktoring_cesja_wierzytelnosci"),
    ("https://www.biznes.gov.pl/pl/portal/ou896", "faktoring_cesja_wierzytelnosci"),
    ("https://www.biznes.gov.pl/pl/publikacje/3237-umowa-o-wspolprace", "b2b_zmiana_na_uop"),
    # Zmiany 2026 (ogólne, do JPK_CIT/estonski)
    ("https://www.biznes.gov.pl/pl/portal/006390", "jpk_cit_jpk_kr"),
]


def slug_from_url(url: str) -> str:
    name = url.rstrip("/").split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9._\-]", "_", name)[:80]
    return name or "page"


async def fetch_page(page, url: str) -> tuple[bool, str, str, int]:
    try:
        await page.goto(url, wait_until="networkidle", timeout=35000)
        await page.wait_for_timeout(2500)
        title = await page.title()
        html = await page.content()
        status = 200
        return True, html, title, status
    except Exception as exc:
        return False, "", f"ERR: {exc}", 0


async def main():
    manifest = load_manifest()
    have_url = {r["url"] for r in manifest}
    have_sha = {r["sha256"] for r in manifest}

    saved = 0
    skipped = 0

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent=UA_CHROME,
            locale="pl-PL",
            ignore_https_errors=True,
        )
        page = await ctx.new_page()
        # Bootstrap session (cookies/JS challenge)
        try:
            await page.goto("https://www.biznes.gov.pl/pl", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2500)
        except Exception as exc:
            print(f"bootstrap warn: {exc}")

        for url, hint in TARGETS:
            if url in have_url:
                skipped += 1
                continue
            ok, html, title, status = await fetch_page(page, url)
            log_fetch({"ts": now_iso(), "url": url, "ok": ok, "status": status, "bytes": len(html)})
            if not ok or len(html) < 20_000:
                print(f"  skip {url}: ok={ok} bytes={len(html)} ({title[:60]})")
                continue
            content = html.encode("utf-8")
            if not magic_ok(content, "html"):
                print(f"  not-html {url}")
                continue
            sha = hashlib.sha256(content).hexdigest()
            if sha in have_sha:
                print(f"  dup-sha {url}")
                continue
            have_sha.add(sha)

            # Compose topic ids: regex + explicit hint fallback
            topics = assign_topics(title, url) or []
            if hint and hint not in topics:
                topics.append(hint)
            if not topics:
                topics = [hint]

            slug = slug_from_url(url)
            rel = Path("raw/biznes_html") / f"bizgov_hot_{slug}.html"
            save_artifact(
                content=content,
                rel_path=rel,
                url=url,
                source="biznes_gov",
                topic_ids=topics,
                layer="L2",
                fmt="html",
                http_status=status,
                content_type="text/html; charset=utf-8",
                title=title,
                is_official=True,
                discovery_source="hot2025_whitelist",
                extra_notes=f"hot_hint={hint}",
            )
            saved += 1
            print(f"  saved [{','.join(topics)}] {slug}: {len(content)//1024}KB")

        await browser.close()
    print(f"\n[hot biznes] saved={saved} skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(main())
