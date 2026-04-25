"""Walker for pip.gov.pl publication listings.

Iterates ?start=N paginator across the three publication sections,
filters by JDG-relevant keywords (skip BHP-rolnictwo/budownictwo etc.),
downloads PDFs into data/raw/pip/.
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

BASE = "https://www.pip.gov.pl"
SECTIONS = [
    "/publikacje/publikacje-dla-pracodawcow",
    "/publikacje/publikacje-dla-pracownikow",
    "/publikacje/publikacje-dla-sluzb-bhp",
]

DROP_KEYWORDS = [
    "rolnictw", "budownictw", "kopalni", "leśnic", "lesnic",
    "żuraw", "zuraw", "rusztowan", "wysokoś", "wysokos",
    "rolnik", "ogniopalnyc", "spawanie", "fajerwer",
]
KEEP_KEYWORDS = [
    "umowa", "umowy", "praca", "pracown", "pracodaw", "urlop",
    "wypowiedz", "swiadectwo", "świadectw", "czas pracy",
    "rodzic", "macierz", "wynagrodz", "praca zdaln", "biuro",
    "bhp", "monitoring", "zatrudnien", "delegowan", "kodeks pracy",
    "minimaln", "samozatrudn", "umowa zlecenie", "umowa o dzielo",
    "umowa o dzieło", "ryzyk", "ergonom",
]


def find_pdf_links(html: str, base: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in re.finditer(r'<a[^>]*href="([^"]+\.pdf[^"]*)"[^>]*>(.*?)</a>', html, re.I | re.S):
        href = html_lib.unescape(m.group(1))
        anchor = html_lib.unescape(re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        url = urljoin(base, href)
        out.append((url, anchor))
    return out


def passes_filter(anchor: str, url: str) -> bool:
    blob = (anchor + " " + url).lower()
    if any(k in blob for k in DROP_KEYWORDS):
        return False
    return any(k in blob for k in KEEP_KEYWORDS)


def slugify(url: str) -> str:
    name = url.rstrip("/").split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9._\-]", "_", name)
    if not name.lower().endswith(".pdf"):
        name = (name or "doc") + ".pdf"
    return name[:120]


def discover_section(section_path: str, sess) -> dict[str, dict]:
    """Walk paginator until empty page."""
    pdfs: dict[str, dict] = {}
    start = 0
    empty_pages = 0
    while empty_pages < 2 and start < 500:
        url = f"{BASE}{section_path}?start={start}"
        res = fetch(url, session=sess)
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok:
            empty_pages += 1
            start += 9
            continue
        html = res.content.decode("utf-8", errors="replace")
        page_pdfs = find_pdf_links(html, BASE)
        if not page_pdfs:
            empty_pages += 1
        else:
            for u, a in page_pdfs:
                if u not in pdfs:
                    pdfs[u] = {"anchor": a, "parent": url}
        start += 9
        time.sleep(0.5)
    return pdfs


def main() -> None:
    sess = session_factory()
    all_pdfs: dict[str, dict] = {}
    for sec in SECTIONS:
        print(f"\n>>> walking {sec}")
        s = discover_section(sec, sess)
        print(f"   found {len(s)} candidate PDFs")
        all_pdfs.update(s)

    print(f"\n[pip] total unique PDF candidates: {len(all_pdfs)}")
    manifest = load_manifest()
    have_urls = {r.get("url") for r in manifest}
    have_sha = {r.get("sha256") for r in manifest}

    saved = 0
    skipped = 0
    for url, meta in all_pdfs.items():
        anchor = meta["anchor"]
        parent = meta["parent"]
        if not passes_filter(anchor, url):
            skipped += 1
            continue
        if url in have_urls:
            continue
        time.sleep(0.5)
        res = fetch(url, sess, accept="application/pdf")
        log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
        if not res.ok or not magic_ok(res.content, "pdf") or len(res.content) < 2048:
            quarantine(res.content or b"", slugify(url), "_failed", res.error or "magic_or_size")
            continue
        sha = __import__("hashlib").sha256(res.content).hexdigest()
        if sha in have_sha:
            continue
        have_sha.add(sha)
        topics = assign_topics(anchor, url, parent)
        if not topics:
            # default tag based on section
            if "pracodawc" in parent or "pracodawcow" in parent:
                topics = ["kp_umowa_o_prace"]
            elif "pracownikow" in parent:
                topics = ["kp_urlop"]
            elif "bhp" in parent:
                topics = ["kp_bhp_biuro"]
            else:
                topics = ["kp_umowa_o_prace"]
        rel = Path("raw/pip") / slugify(url)
        save_artifact(
            content=res.content,
            rel_path=rel,
            url=url,
            source="pip",
            topic_ids=topics,
            layer="L2",
            fmt="pdf",
            http_status=res.status,
            content_type=res.headers.get("Content-Type", "application/pdf"),
            title=anchor,
            last_modified=res.headers.get("Last-Modified", ""),
            is_official=True,
            parent_url=parent,
            discovery_source="paginacja",
            headers=res.headers,
        )
        saved += 1
        if saved % 5 == 0:
            print(f"  pip saved {saved}")
    print(f"\n[pip] done. saved={saved} skipped={skipped}")


if __name__ == "__main__":
    main()
