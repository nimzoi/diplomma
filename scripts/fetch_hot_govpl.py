"""Hot-2025/2026 collector — gov.pl + podatki.gov.pl + mf.gov.pl pages.

Two-pass per seed:
  pass1 — fetch the SSR HTML (saved as L2 doc when content > 20KB).
  pass2 — discover and download every /attachment/<uuid> link inside
          (PDFs/DOCX), guarded by topic-hint whitelist.

Whitelist-first: only the explicit seeds below; no generalised crawl
(avoids the 'fetch-all-attachments' bloat lesson).
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, quote

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

# (page_url, topic_hint, follow_attachments, save_html)
SEEDS: list[tuple[str, str, bool, bool]] = [
    # DAC7
    ("https://www.gov.pl/web/finanse/co-warto-wiedziec-o-dyrektywie-dac7",
     "dac7_platformy", True, True),
    ("https://www.gov.pl/web/finanse/wspolpraca-panstw-ue-w-walce-z-unikaniem-opodatkowania-dyrektywa-dac7-w-praktyce",
     "dac7_platformy", True, True),
    ("https://www.gov.pl/web/finanse/rzad-przyjal-projekt-ustawy-dac7",
     "dac7_platformy", True, True),
    ("https://www.podatki.gov.pl/podatkowa-wspolpraca-miedzynarodowa/dpi-digital-platform-information/",
     "dac7_platformy", True, True),
    ("https://www.podatki.gov.pl/podatkowa-wspolpraca-miedzynarodowa/dpi-digital-platform-information/informacje-o-obowiazkach-operatorow-platform/",
     "dac7_platformy", True, True),
    ("https://www.podatki.gov.pl/podatkowa-wspolpraca-miedzynarodowa/dpi-digital-platform-information/pytania-i-odpowiedzi-dla-operatorow-platform/",
     "dac7_platformy", True, True),
    ("https://www.podatki.gov.pl/wyjasnienia/co-warto-wiedziec-o-dyrektywie-dac7/",
     "dac7_platformy", True, True),
    # JPK_CIT / JPK_KR_PD / księgi 2026
    ("https://www.gov.pl/web/kas/struktury-jpk-w-podatkach-dochodowych",
     "jpk_cit_jpk_kr", True, True),
    ("https://www.gov.pl/web/kas/elektroniczne-ksiegi-rachunkowe-w-podatku-pit-w-2026-r",
     "jpk_cit_jpk_kr", True, True),
    ("https://www.gov.pl/web/finanse/nowe-zasady-dokumentacji-ksiegowej-w-podatku-pit-od-2026-r-wazne-informacje",
     "jpk_cit_jpk_kr", True, True),
    ("https://www.gov.pl/web/finanse/elektroniczne-ksiegi-i-ewidencje-podatkowe",
     "jpk_cit_jpk_kr", True, True),
    ("https://www.podatki.gov.pl/wyjasnienia/nowe-zasady-cyfryzacji-dokumentacji-ksiegowej-w-podatku-cit/",
     "jpk_cit_jpk_kr", True, True),
    # Estoński CIT
    ("https://www.gov.pl/web/finanse/estonski-cit",
     "estonski_cit", True, True),
    ("https://www.gov.pl/web/finanse/objasnienia-do-estonskiego-cit-u-w-konsultacjach-zewnetrznych",
     "estonski_cit", True, True),
    ("https://www.gov.pl/web/finanse/konsultacje-podatkowe---estonski-cit",
     "estonski_cit", True, True),
    ("https://www.gov.pl/web/finanse/mf-zachecamy-do-przejscia-na-estonski-cit",
     "estonski_cit", True, True),
    ("https://www.podatki.gov.pl/media/dxrabsmd/estonski_cit_2-0_praktyczny_przewodnik_dla_biznesu.pdf",
     "estonski_cit", False, False),  # direct PDF guide
    # Ulga ekspansja / B+R / robotyzacja / prototyp
    ("https://www.gov.pl/web/finanse/ulga-na-badania-i-rozwoj",
     "ulga_ekspansja_prototyp_robotyzacja", True, True),
    ("https://www.gov.pl/web/finanse/ulga-na-ekspansje",
     "ulga_ekspansja_prototyp_robotyzacja", True, True),
    ("https://www.gov.pl/web/finanse/ulga-na-robotyzacje",
     "ulga_ekspansja_prototyp_robotyzacja", True, True),
    ("https://www.gov.pl/web/finanse/ulga-na-prototyp",
     "ulga_ekspansja_prototyp_robotyzacja", True, True),
    # CRBR
    ("https://www.gov.pl/web/finanse/centralny-rejestr-beneficjentow-rzeczywistych",
     "crbr_beneficjent_rzeczywisty", True, True),
    ("https://www.podatki.gov.pl/crbr/",
     "crbr_beneficjent_rzeczywisty", True, True),
    # Kasa fiskalna online
    ("https://www.gov.pl/web/kas/kasy-rejestrujace--informacje-ogolne",
     "kasa_fiskalna_online", True, True),
    ("https://www.podatki.gov.pl/vat/kasy-rejestrujace/",
     "kasa_fiskalna_online", True, True),
    ("https://www.podatki.gov.pl/vat/kasy-rejestrujace/centralne-repozytorium-kas/",
     "kasa_fiskalna_online", True, True),
    # Pomoc de minimis / SUDOP
    ("https://www.uokik.gov.pl/pomoc-de-minimis",
     "pomoc_de_minimis", True, True),
    # Zatrudnianie cudzoziemców
    ("https://www.gov.pl/web/rodzina/zatrudnianie-cudzoziemcow",
     "zatrudnianie_cudzoziemcow", True, True),
    ("https://www.gov.pl/web/rodzina/oswiadczenie-o-powierzeniu-wykonywania-pracy-cudzoziemcowi",
     "zatrudnianie_cudzoziemcow", True, True),
    # Faktoring / split payment / cesja
    ("https://www.gov.pl/web/finanse/mechanizm-podzielonej-platnosci",
     "faktoring_cesja_wierzytelnosci", True, True),
    ("https://www.podatki.gov.pl/vat/mechanizm-podzielonej-platnosci-mpp/",
     "faktoring_cesja_wierzytelnosci", True, True),
    # B2B vs UOP / art. 22 KP
    ("https://www.pip.gov.pl/pl/baza-wiedzy/prawo-pracy/nawiazanie-stosunku-pracy",
     "b2b_zmiana_na_uop", True, True),
]

ATTACHMENT_RE = re.compile(
    r'<a[^>]*href="(/attachment/[a-f0-9-]+)"[^>]*>(.*?)</a>',
    re.I | re.S,
)
PAGE_TITLE_RE = re.compile(r"<title>([^<]+)</title>", re.I)


def is_homepage_redirect(html: str) -> bool:
    return ("active_menu_item\" content=\"gov_home" in html
            or "active_menu_item\" content=\"finanse_home" in html and len(html) < 50_000)


def slug(url: str) -> str:
    name = urlparse(url).path.rstrip("/").split("/")[-1] or "page"
    name = re.sub(r"[^A-Za-z0-9._\-]", "_", name)[:90]
    return name


def safe_url(u: str) -> str:
    # Polish chars in path: percent-encode while preserving existing %XX
    return quote(u, safe=":/?=&%")


def parse_attachments(html: str) -> list[tuple[str, str]]:
    out, seen = [], set()
    for m in ATTACHMENT_RE.finditer(html):
        href = m.group(1)
        if href in seen:
            continue
        seen.add(href)
        text = re.sub(r"<[^>]+>", " ", m.group(2)).strip()
        text = re.sub(r"\s+", " ", text)
        out.append((href, text))
    return out


def main() -> None:
    sess = session_factory({"User-Agent": UA_CHROME})
    manifest = load_manifest()
    have_url = {r["url"] for r in manifest}
    have_sha = {r["sha256"] for r in manifest}

    saved_html = saved_pdf = saved_docx = 0
    skipped = 0

    for page_url, hint, follow_attach, save_html in SEEDS:
        time.sleep(0.6)
        url = safe_url(page_url)
        if page_url in have_url:
            skipped += 1
            continue
        host = urlparse(page_url).netloc.lower()
        source = "govpl"
        if host.endswith("podatki.gov.pl"):
            source = "podatki"
        elif host.endswith("uokik.gov.pl"):
            source = "uokik"
        elif host.endswith("pip.gov.pl"):
            source = "pip"

        # Direct PDF case (e.g. media/.../przewodnik.pdf)
        if page_url.lower().endswith(".pdf") and not save_html:
            r = fetch(url, sess, accept="application/pdf")
            log_fetch({"ts": now_iso(), "url": page_url, "ok": r.ok, "status": r.status, "bytes": len(r.content)})
            if not r.ok or not magic_ok(r.content, "pdf") or len(r.content) < 50_000:
                print(f"  pdf-fail {page_url}")
                continue
            sha = hashlib.sha256(r.content).hexdigest()
            if sha in have_sha:
                continue
            have_sha.add(sha)
            topics = assign_topics(page_url, hint) or [hint]
            if hint not in topics:
                topics.append(hint)
            rel = Path(f"raw/{source}") / f"{source}_hot_{slug(page_url)}"
            save_artifact(
                content=r.content, rel_path=rel, url=page_url, source=source,
                topic_ids=topics, layer="L2", fmt="pdf", http_status=r.status,
                content_type=r.headers.get("Content-Type", "application/pdf"),
                title=slug(page_url), is_official=True, parent_url=page_url,
                discovery_source="hot2025_direct", headers=r.headers,
                extra_notes=f"hot_hint={hint}",
            )
            saved_pdf += 1
            print(f"  saved-pdf [{hint}] {slug(page_url)}: {len(r.content)//1024}KB")
            continue

        # HTML page fetch
        r = fetch(url, sess, accept="text/html")
        log_fetch({"ts": now_iso(), "url": page_url, "ok": r.ok, "status": r.status, "bytes": len(r.content)})
        if not r.ok:
            print(f"  page-fail {page_url} ({r.error})")
            continue
        html = r.content.decode("utf-8", errors="replace")
        if is_homepage_redirect(html):
            print(f"  homepage-redirect {page_url}")
            continue

        title_m = PAGE_TITLE_RE.search(html)
        title = title_m.group(1).strip() if title_m else slug(page_url)

        # Save HTML if it's substantive
        if save_html and len(r.content) >= 20_000 and magic_ok(r.content, "html"):
            sha = hashlib.sha256(r.content).hexdigest()
            if sha not in have_sha:
                have_sha.add(sha)
                topics = assign_topics(title, page_url, hint) or []
                if hint not in topics:
                    topics.append(hint)
                rel_dir = "raw/govpl_html" if source == "govpl" else f"raw/{source}_html"
                rel = Path(rel_dir) / f"{source}_hot_{slug(page_url)}.html"
                save_artifact(
                    content=r.content, rel_path=rel, url=page_url, source=source,
                    topic_ids=topics, layer="L2", fmt="html", http_status=r.status,
                    content_type=r.headers.get("Content-Type", "text/html"),
                    title=title, is_official=True, parent_url="",
                    discovery_source="hot2025_seed", headers=r.headers,
                    extra_notes=f"hot_hint={hint}",
                )
                saved_html += 1
                print(f"  saved-html [{hint}] {slug(page_url)}: {len(r.content)//1024}KB")

        if not follow_attach:
            continue

        # Pass 2: download attachments referenced from this page
        attachments = parse_attachments(html)
        # Limit per-page to avoid bloat
        for href, anchor in attachments[:8]:
            att_url = "https://www.gov.pl" + href if source == "govpl" else urljoin(page_url, href)
            if att_url in have_url:
                continue
            time.sleep(0.4)
            ar = fetch(safe_url(att_url), sess, accept="application/pdf")
            log_fetch({"ts": now_iso(), "url": att_url, "ok": ar.ok, "status": ar.status, "bytes": len(ar.content)})
            if not ar.ok or len(ar.content) < 50_000:
                continue
            if magic_ok(ar.content, "pdf"):
                fmt = "pdf"
            elif ar.content[:2] == b"PK":
                fmt = "docx"
            else:
                continue
            sha = hashlib.sha256(ar.content).hexdigest()
            if sha in have_sha:
                continue
            have_sha.add(sha)
            topics = assign_topics(anchor, att_url, hint) or []
            if hint not in topics:
                topics.append(hint)
            anchor_slug = re.sub(r"[^A-Za-z0-9._\-]", "_", anchor)[:80] or href.split("/")[-1]
            rel_dir = f"raw/{source}"
            rel = Path(rel_dir) / f"{source}_hot_{anchor_slug}.{fmt}"
            save_artifact(
                content=ar.content, rel_path=rel, url=att_url, source=source,
                topic_ids=topics, layer="L2", fmt=fmt, http_status=ar.status,
                content_type=ar.headers.get("Content-Type", ""), title=anchor or title,
                is_official=True, parent_url=page_url,
                discovery_source="hot2025_attachment", headers=ar.headers,
                extra_notes=f"hot_hint={hint}",
            )
            if fmt == "pdf":
                saved_pdf += 1
            else:
                saved_docx += 1
            print(f"    attach [{hint}] {anchor_slug}: {len(ar.content)//1024}KB ({fmt})")

    print(f"\n[hot govpl] saved html={saved_html} pdf={saved_pdf} docx={saved_docx} skipped={skipped}")


if __name__ == "__main__":
    main()
