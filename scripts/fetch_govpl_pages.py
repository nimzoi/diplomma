"""Fetch gov.pl /web/* pages and download all /attachment/{uuid} files.

gov.pl uses SSR — many sub-pages render full HTML with `/attachment/{uuid}`
links to PDF/DOCX assets. We seed with high-value JDG-relevant pages
(per agent recommendations: KAS KSeF, e-Doręczenia, składka zdrowotna,
wakacje składkowe, IP Box, ulga na B+R, KSeF FA(3) etc.) and download
every attachment.
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from urllib.parse import urlparse

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

UA_CHROME = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# (page_url, topic_hint, is_official)
SEEDS = [
    # KAS - KSeF
    ("https://www.gov.pl/web/kas/krajowy-system-e-faktur",
     "ksef faktury ustrukturyzowane vat", True),
    # e-Doręczenia (CRITICAL od 2025 dla JDG)
    ("https://www.gov.pl/web/e-doreczenia",
     "e-doreczenia ade ceidg obowiazek 2025", True),
    # IP Box objaśnienia 2019 (najważniejsze wyjaśnienie MF)
    ("https://www.gov.pl/web/finanse/objasnienia-podatkowe-z-15-lipca-2019-r-w-sprawie-ip-box",
     "ip box programisci 5% objasnienia mf", True),
    # B+R / innowacje
    ("https://www.gov.pl/web/finanse/ulga-na-badania-i-rozwoj",
     "ulga b+r badan rozwoj", True),
    # Składka zdrowotna
    ("https://www.gov.pl/web/finanse/skladka-zdrowotna-przedsiebiorcow",
     "skladka zdrowotna jdg ryczalt skala liniowy", True),
    # Wakacje od składek (2024+)
    ("https://www.gov.pl/web/finanse/wakacje-od-skladek-zus",
     "wakacje skladkowe rws zus", True),
    # KAS root + sub-pages
    ("https://www.gov.pl/web/kas",
     "kas krajowa administracja skarbowa", True),
    # Usługi dla przedsiębiorcy
    ("https://www.gov.pl/web/gov/uslugi-dla-przedsiebiorcy",
     "uslugi dla przedsiebiorcy", True),
    # Założ JDG
    ("https://www.gov.pl/web/gov/zaloz-firme-jednoosobowa-dzialalnosc-gospodarcza-jdg",
     "ceidg rejestracja jdg dzialalnosc", True),
    # Polski Ład / podatki firmowe
    ("https://www.gov.pl/web/finanse/podreczniki-i-broszury",
     "podreczniki broszury podatki", True),
    # DAC7 platformy
    ("https://www.gov.pl/web/finanse/dac7-platformy-cyfrowe",
     "dac7 platformy cyfrowe raportowanie", True),
    # Estoński CIT
    ("https://www.gov.pl/web/finanse/estonski-cit",
     "estonski cit ryczalt od dochodow spolek", True),
    # Mały ZUS Plus
    ("https://www.gov.pl/web/finanse/maly-zus-plus",
     "maly zus plus art 18c", True),
    # Sankcje AML
    ("https://www.gov.pl/web/finanse/giif",
     "aml giif zglaszanie transakcji", True),
    # Kasa fiskalna online
    ("https://www.gov.pl/web/finanse/kasy-rejestrujace",
     "kasy rejestrujace online", True),
]

ATTACHMENT_RE = re.compile(r'href="(/attachment/[a-f0-9-]+)"', re.I)
TITLE_NEAR_ATTACHMENT_RE = re.compile(
    r'<a[^>]*href="(/attachment/[a-f0-9-]+)"[^>]*>(.*?)</a>',
    re.I | re.S,
)
PAGE_TITLE_RE = re.compile(r"<title>([^<]+)</title>", re.I)


def parse_attachments(html: str) -> list[tuple[str, str]]:
    """Return [(href, anchor_text)] pairs."""
    out = []
    seen = set()
    for m in TITLE_NEAR_ATTACHMENT_RE.finditer(html):
        href = m.group(1)
        if href in seen:
            continue
        seen.add(href)
        text = re.sub(r"<[^>]+>", " ", m.group(2)).strip()
        text = re.sub(r"\s+", " ", text)
        out.append((href, text))
    return out


def is_homepage(html: str) -> bool:
    """Detect when gov.pl returned its boilerplate homepage instead of the
    requested page (size ~39382 bytes, contains specific homepage markers)."""
    return "active_menu_item\" content=\"gov_home" in html


def slug_from_anchor(text: str, fallback: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_\- ]", "", text).strip()[:80].replace(" ", "_") or fallback
    return name.lower() + ".pdf"


def main() -> None:
    sess = session_factory({"User-Agent": UA_CHROME, "Accept-Language": "pl-PL,pl;q=0.9"})
    manifest = load_manifest()
    have_url = {r.get("url", "") for r in manifest}
    have_sha = {r.get("sha256", "") for r in manifest}

    saved = 0
    skipped = 0
    for page_url, hint, official in SEEDS:
        if page_url in have_url:
            continue
        time.sleep(0.5)
        res = fetch(page_url, sess)
        log_fetch({"ts": now_iso(), "url": page_url, "ok": res.ok,
                    "status": res.status, "bytes": len(res.content)})
        if not res.ok:
            print(f"  page-fail {page_url}")
            continue
        html = res.content.decode("utf-8", errors="replace")
        if is_homepage(html):
            print(f"  homepage redirect {page_url}")
            continue

        page_title_m = PAGE_TITLE_RE.search(html)
        page_title = page_title_m.group(1).strip() if page_title_m else ""
        attachments = parse_attachments(html)
        print(f"  {page_url}: {len(attachments)} attachments")

        for href, anchor in attachments:
            url = "https://www.gov.pl" + href
            if url in have_url:
                skipped += 1
                continue
            time.sleep(0.4)
            r = fetch(url, sess, accept="application/pdf")
            log_fetch({"ts": now_iso(), "url": url, "ok": r.ok,
                        "status": r.status, "bytes": len(r.content)})
            if not r.ok or len(r.content) < 2048:
                continue
            if not magic_ok(r.content, "pdf"):
                # Maybe it's DOCX or XLSX
                if r.content[:2] == b"PK":
                    fmt = "docx"
                else:
                    fmt = "html"
                    if not magic_ok(r.content, "html"):
                        quarantine(r.content, slug_from_anchor(anchor, "govpl"),
                                   "_failed", "unknown magic")
                        continue
            else:
                fmt = "pdf"

            sha = hashlib.sha256(r.content).hexdigest()
            if sha in have_sha:
                continue
            have_sha.add(sha)

            title = anchor or page_title
            topics = assign_topics(title, hint, page_url)
            if not topics:
                # Map by URL slug
                lo = page_url.lower()
                if "ksef" in lo or "e-faktur" in lo: topics = ["vat_ksef"]
                elif "doreczen" in lo: topics = ["ceidg_zmiana_wpisu"]
                elif "ip-box" in lo: topics = ["pit_ip_box"]
                elif "skladka-zdrowotna" in lo: topics = ["zus_skladka_zdrowotna_jdg"]
                elif "wakacje" in lo: topics = ["zus_wakacje_skladkowe"]
                elif "maly-zus" in lo: topics = ["zus_maly_zus_plus"]
                elif "estonski" in lo: topics = ["pit_skala"]
                elif "kas" in lo: topics = ["vat_jpk", "vat_ksef"]
                elif "uslugi" in lo or "zaloz-firme" in lo: topics = ["ceidg_rejestracja"]
                elif "dac7" in lo: topics = ["vat_jpk"]
                elif "kas" in lo: topics = ["vat_jpk"]
                elif "rozwoj" in lo or "b+r" in lo or "badania" in lo: topics = ["pit_ip_box"]
                else: topics = ["ceidg_rejestracja"]

            slug = slug_from_anchor(anchor, href.split("/")[-1])
            ext = fmt
            slug = slug.rsplit(".", 1)[0] + "." + ext
            rel = Path(f"raw/govpl") / f"govpl_{slug}"
            save_artifact(
                content=r.content,
                rel_path=rel,
                url=url,
                source="govpl",
                topic_ids=topics,
                layer="L2",
                fmt=ext,
                http_status=r.status,
                content_type=r.headers.get("Content-Type", ""),
                title=title,
                last_modified=r.headers.get("Last-Modified", ""),
                is_official=official,
                parent_url=page_url,
                discovery_source="ssr_attachment",
                headers=r.headers,
            )
            saved += 1
            if saved % 5 == 0:
                print(f"    saved {saved}")
    print(f"\n[govpl] saved={saved} skipped={skipped}")


if __name__ == "__main__":
    main()
