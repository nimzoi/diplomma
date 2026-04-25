"""Save valuable gov.pl pages as raw HTML (when SSR works) + harvest
any /attachment/ links.

The user pointed out: when a page has substantive content but no PDF
attachment, just save the rendered HTML — that's the knowledge content.
"""
from __future__ import annotations

import hashlib
import html as html_lib
import re
import time
from pathlib import Path

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

UA_CHROME = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Curated set of gov.pl sub-pages worth preserving as HTML for chatbot context.
# Includes both pages we expect to render with SSR and pages where attachments
# exist. (page_url, topic_hint)
PAGES = [
    # From actual gov.pl/web/finanse navigation (verified non-homepage size):
    ("https://www.gov.pl/web/finanse/elektroniczne-ksiegi-i-ewidencje-podatkowe",
     "kpir ewidencja jpk_cit jpk_kr"),
    ("https://www.gov.pl/web/finanse/konsultacje-podatkowe",
     "konsultacje podatkowe interpretacje ogolne"),
    ("https://www.gov.pl/web/finanse/indywidualne-dane-podatnikow-cit",
     "cit dane indywidualne"),
    ("https://www.gov.pl/web/finanse/generalny-inspektor-informacji-finansowej",
     "giif aml zglaszanie transakcji"),
    ("https://www.gov.pl/web/finanse/akty-prawne-budzet-panstwa",
     "akty prawne budzet panstwa"),
    ("https://www.gov.pl/web/finanse/edukacja-finansowa",
     "edukacja finansowa podatki podstawy"),

    # KAS:
    ("https://www.gov.pl/web/kas",
     "kas krajowa administracja skarbowa"),
    ("https://www.gov.pl/web/kas/krajowy-system-e-faktur",
     "ksef faktury ustrukturyzowane vat"),
    ("https://www.gov.pl/web/kas/kasy-online",
     "kasy fiskalne online vat"),
    ("https://www.gov.pl/web/kas/indywidualny-rachunek-podatkowy",
     "mikrorachunek podatkowy nip indywidualny"),
    ("https://www.gov.pl/web/kas/e-deklaracje",
     "e-deklaracje pit vat ceidg"),
    ("https://www.gov.pl/web/kas/agenci-rozliczeniowi",
     "agenci rozliczeniowi platnosci"),
    ("https://www.gov.pl/web/kas/dostawcy-uslug-platniczych",
     "dostawcy uslug platniczych psp"),
    ("https://www.gov.pl/web/kas/edukacja-i-akcje-informacyjne-kas",
     "edukacja kas akcje informacyjne podatki"),
    ("https://www.gov.pl/web/kas/egzekucja-administracyjna",
     "egzekucja administracyjna podatki"),

    # Other potentially valuable:
    ("https://www.gov.pl/web/e-doreczenia",
     "e-doreczenia ade jdg obowiazek 2025"),
    ("https://www.gov.pl/web/gov/uslugi-dla-przedsiebiorcy",
     "uslugi dla przedsiebiorcy"),

    # B2B + samozatrudnienie (per user feedback - hot 2025 topic)
    ("https://www.gov.pl/web/finanse/samozatrudnienie",
     "samozatrudnienie b2b uop test stosunku pracy"),
    ("https://www.gov.pl/web/rodzina/dzialalnosc-jednoosobowa-czy-umowa-o-prace",
     "b2b vs uop wymuszenie pip"),

    # KAS sub-pages
    ("https://www.gov.pl/web/kas/biezace-informacje-z-kas",
     "kas aktualnosci wakacje skladkowe ksef"),
    ("https://www.gov.pl/web/kas/zaplata-podatkow",
     "platnosc podatkow mikrorachunek terminy"),
    ("https://www.gov.pl/web/kas/jak-jest-finansowana-ochrona-zdrowia",
     "skladka zdrowotna nfz"),

    # Inne resorty
    ("https://www.gov.pl/web/uodo",
     "uodo ochrona danych osobowych"),
    ("https://www.gov.pl/web/zus",
     "zus skladki ubezpieczenia"),
    ("https://www.gov.pl/web/rozwoj-technologia/dla-przedsiebiorcy",
     "rozwoj technologia przedsiebiorcy ip box"),
    ("https://www.gov.pl/web/rozwoj-technologia/maly-zus-plus",
     "maly zus plus art 18c"),
    ("https://www.gov.pl/web/rozwoj-technologia/zalozenie-firmy",
     "zalozenie firmy ceidg"),

    # Rzecznik MŚP
    ("https://rzecznikmsp.gov.pl/",
     "rzecznik msp interwencje opinie"),
    ("https://rzecznikmsp.gov.pl/aktualnosci/",
     "rzecznik msp aktualnosci wakacje skladkowe"),
    ("https://rzecznikmsp.gov.pl/interwencje/",
     "rzecznik msp interwencje skarbowka zus"),

    # Senior wiedzy: PARP grants index
    ("https://www.parp.gov.pl/",
     "parp dotacje wsparcie msp"),
]

ATTACH_RE = re.compile(r'href="(/attachment/[a-f0-9-]+)"', re.I)
HOMEPAGE_MARKER = 'active_menu_item" content="gov_home"'


def is_homepage_redirect(html: str) -> bool:
    return HOMEPAGE_MARKER in html


def extract_main_text_chars(html: str) -> int:
    """Cheap content estimator — strip tags, count Polish chars."""
    no_tags = re.sub(r"<[^>]+>", " ", html)
    no_tags = re.sub(r"\s+", " ", no_tags).strip()
    return len(no_tags)


def slug_from_url(url: str) -> str:
    last = url.rstrip("/").split("/")[-1]
    return re.sub(r"[^A-Za-z0-9._\-]", "_", last)[:120]


def main() -> None:
    sess = session_factory({"User-Agent": UA_CHROME, "Accept-Language": "pl-PL,pl;q=0.9"})
    manifest = load_manifest()
    have_url = {r.get("url", "") for r in manifest}
    have_sha = {r.get("sha256", "") for r in manifest}

    saved_html = 0
    saved_pdf = 0
    skipped = 0
    seen_attachments: set[str] = set()
    for url, hint in PAGES:
        if url in have_url:
            skipped += 1
            continue
        time.sleep(0.5)
        res = fetch(url, sess)
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok:
            print(f"  fail {url}")
            continue
        html = res.content.decode("utf-8", errors="replace")
        if is_homepage_redirect(html):
            print(f"  homepage redirect: {url}")
            continue
        chars = extract_main_text_chars(html)
        if chars < 1500:
            print(f"  too thin ({chars} chars): {url}")
            continue

        # 1) Save the page as HTML
        sha = hashlib.sha256(res.content).hexdigest()
        if sha not in have_sha:
            have_sha.add(sha)
            topics = assign_topics(url, hint)
            if not topics:
                topics = ["ceidg_rejestracja"]
            slug = slug_from_url(url)
            rel = Path("raw/govpl_html") / f"govpl_{slug}.html"
            # extract <title>
            title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
            page_title = html_lib.unescape(title_m.group(1).strip()) if title_m else url
            save_artifact(
                content=res.content,
                rel_path=rel,
                url=url,
                source="govpl",
                topic_ids=topics,
                layer="L2",
                fmt="html",
                http_status=res.status,
                content_type=res.headers.get("Content-Type", "text/html"),
                title=page_title,
                last_modified=res.headers.get("Last-Modified", ""),
                is_official=True,
                discovery_source="ssr_html",
                headers=res.headers,
                extra_notes=f"Rendered SSR HTML, ~{chars} chars text",
            )
            saved_html += 1
            print(f"  HTML  {url} ({chars} chars)")

        # 2) Harvest /attachment/ PDFs
        for m in ATTACH_RE.finditer(html):
            href = m.group(1)
            if href in seen_attachments:
                continue
            seen_attachments.add(href)
            asset_url = "https://www.gov.pl" + href
            if asset_url in have_url:
                continue
            time.sleep(0.3)
            r = fetch(asset_url, sess)
            log_fetch({"ts": now_iso(), "url": asset_url, "ok": r.ok, "status": r.status, "bytes": len(r.content)})
            if not r.ok or len(r.content) < 2048:
                continue
            asha = hashlib.sha256(r.content).hexdigest()
            if asha in have_sha:
                continue
            have_sha.add(asha)
            # detect format
            if r.content[:4] == b"%PDF":
                fmt = "pdf"
            elif r.content[:2] == b"PK":
                fmt = "docx"
            else:
                continue
            attach_id = href.split("/")[-1]
            rel = Path("raw/govpl") / f"govpl_attach_{attach_id}.{fmt}"
            topics = assign_topics(hint, url)
            if not topics:
                topics = ["ceidg_rejestracja"]
            save_artifact(
                content=r.content,
                rel_path=rel,
                url=asset_url,
                source="govpl",
                topic_ids=topics,
                layer="L2",
                fmt=fmt,
                http_status=r.status,
                content_type=r.headers.get("Content-Type", ""),
                title=f"attachment from {url}",
                last_modified=r.headers.get("Last-Modified", ""),
                is_official=True,
                parent_url=url,
                discovery_source="ssr_attachment",
                headers=r.headers,
            )
            saved_pdf += 1
    print(f"\n[govpl-html] html={saved_html} pdf={saved_pdf} skipped={skipped}")


if __name__ == "__main__":
    main()
