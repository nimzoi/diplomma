"""orzeczenia.ms.gov.pl Apache Tapestry search expansion (via Playwright).

E4 zebrał 10 wyroków przez Google search redirects (handCurated). Ta moduła
dopisuje setki kolejnych przez pełną Apache Tapestry search z form fillingiem.

Search keywords (per `consumer_documents` task):

* "konsument"
* "rękojmia"
* "umowa konsumencka"
* "klauzule niedozwolone"
* "zwrot towaru"
* "reklamacja"
* "kredyt konsumencki"

Per query iterujemy result pages (z paginatorem). Z każdego result row
wyciągamy URL → content page → strukturalny chunking (analogicznie do
istniejącego ``scrape_consumer_docs.scrape_orzeczenia``).

Output:

    data/raw/consumer_documents_2026-05-16/orzeczenia/
        documents.jsonl          -- DOCLUTED chunks (kompat z E4 format)
        orz_<sygnatura>.meta.json
        _snapshots/              -- HTML snapshots (gitignored)

Kompatybilność: identyczny LegalChunk-like schema co E4 (chunk_id,
document_id, document_title, document_type, source, source_url,
chunk_position, chunk_total, section_heading, tresc, scrape_date, license,
metadata{sygnatura, court, ruling_date, format}).

License: urzędowe (Art. 4 ust. 2 PrAut).
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from playwright.sync_api import Page

from .common import (
    LICENSE_URZEDOWE,
    SCRAPE_DATE,
    BrowserSession,
    ScrapeStats,
    count_words,
    normalize_pl,
    save_snapshot,
    write_jsonl,
    write_meta,
)

logger = logging.getLogger("orzeczenia_ms_expansion")

SEARCH_URL = "https://orzeczenia.ms.gov.pl/search/"
RESULT_BASE = "https://orzeczenia.ms.gov.pl"

DEFAULT_KEYWORDS = [
    "konsument",
    "rękojmia",
    "umowa konsumencka",
    "klauzule niedozwolone",
    "zwrot towaru",
    "reklamacja",
    "kredyt konsumencki",
]

# Konfiguracja chunkowania (mirror z scrape_consumer_docs).
MAX_CHUNK_CHARS = 1800
MIN_CHUNK_CHARS = 250
MIN_DOCUMENT_WORDS = 350


@dataclass
class OrzeczenieChunk:
    """Kompat z E4 LegalChunk-like format z scrape_consumer_docs.

    Identyczne pola — można merge'ować do tego samego documents.jsonl.
    """

    chunk_id: str
    document_id: str
    document_title: str
    document_type: str  # = "orzeczenie"
    source: str  # = "orzeczenia.ms.gov.pl"
    source_url: str
    chunk_position: int
    chunk_total: int
    section_heading: str | None
    tresc: str
    scrape_date: str
    license: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrzeczenieMeta:
    """Per-orzeczenie meta sidecar (kompat z E4)."""

    document_id: str
    document_title: str
    document_type: str
    source: str
    source_url: str
    total_chunks: int
    total_words: int
    license: str
    scrape_date: str
    citation_recommendation: str = ""
    author: str | None = None
    publication_year: int | None = None
    pdf_size_bytes: int | None = None


# ---------------------------------------------------------------------------
# chunking — local copy z scrape_consumer_docs
# ---------------------------------------------------------------------------


def _chunk_long_text(
    full_text: str,
    *,
    headings: list[tuple[str, int]] | None = None,
) -> list[tuple[str | None, str]]:
    full_text = full_text.strip()
    if not full_text:
        return []
    sections: list[tuple[str | None, str]]
    if headings:
        sections = []
        h = sorted(headings, key=lambda x: x[1])
        for i, (title, start) in enumerate(h):
            end = h[i + 1][1] if i + 1 < len(h) else len(full_text)
            body = full_text[start:end].strip()
            if body:
                sections.append((title, body))
        first_off = h[0][1] if h else 0
        if first_off > 0:
            lead = full_text[:first_off].strip()
            if lead:
                sections.insert(0, (None, lead))
        if not sections:
            sections = [(None, full_text)]
    else:
        sections = [(None, full_text)]

    output: list[tuple[str | None, str]] = []
    for sec_title, sec_body in sections:
        if len(sec_body) <= MAX_CHUNK_CHARS:
            output.append((sec_title, sec_body))
            continue
        paragraphs = re.split(r"\n\s*\n", sec_body)
        if len(paragraphs) <= 1:
            paragraphs = re.split(r"(?<=[.!?])\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ])", sec_body)
        buf = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(buf) + len(para) + 2 <= MAX_CHUNK_CHARS:
                buf = (buf + "\n\n" + para) if buf else para
            else:
                if buf:
                    output.append((sec_title, buf))
                if len(para) > MAX_CHUNK_CHARS:
                    for offset in range(0, len(para), MAX_CHUNK_CHARS):
                        output.append((sec_title, para[offset : offset + MAX_CHUNK_CHARS]))
                    buf = ""
                else:
                    buf = para
        if buf:
            output.append((sec_title, buf))

    if len(output) > 1:
        output = [(t, b) for t, b in output if len(b) >= MIN_CHUNK_CHARS]
        if not output:
            joined = "\n\n".join(s for _, s in sections if s)
            output = [(None, joined)]
    return output


# ---------------------------------------------------------------------------
# Tapestry search
# ---------------------------------------------------------------------------


def _search_for_phrase(page: Page, phrase: str, max_pages: int = 5) -> list[dict[str, str]]:
    """Wypełnij Tapestry search form + iteruj pages → URLs do orzeczeń.

    Returns: lista dict {url, sygnatura_preview, court_preview}.
    """
    logger.info("search phrase=%r", phrase)
    if not page.goto(SEARCH_URL, timeout=60_000):
        return []
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception:
        pass
    page.wait_for_timeout(2_000)

    # Fill phrase input.
    try:
        page.fill("#phrase", phrase, timeout=15_000)
    except Exception as exc:
        logger.warning("  failed to fill #phrase: %s", exc)
        return []

    # Submit.
    try:
        page.click("#advancedSearchFormSubmit", timeout=15_000)
        page.wait_for_load_state("networkidle", timeout=20_000)
    except Exception as exc:
        logger.warning("  submit failed: %s", exc)
        return []
    page.wait_for_timeout(2_000)

    results: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for pg in range(max_pages):
        # Tapestry search wynik linki: /details/{phrase}/{doc_id} albo /content/...
        # Bierzemy BOTH; każda strona pokazuje ~10 result rows.
        items = page.eval_on_selector_all(
            "a[href*='/details/'], a[href*='/content/$N/']",
            """els => Array.from(new Set(els.map(e => e.href)))""",
        )
        for href in items:
            if href in seen_urls:
                continue
            seen_urls.add(href)
            results.append({"url": href, "phrase": phrase})

        # Tapestry pagination via /search.gridpager/N. Po pierwszej stronie
        # pojawiają się linki do strony 2,3,4,... Klikamy "następną" stronę.
        # Strategy: find next gridpager link z numerem (current+1).
        nav_clicked = False
        next_page_idx = pg + 2  # page 1 → click "2"
        try:
            sel = f"a[href*='search.gridpager/{next_page_idx}']"
            btn = page.query_selector(sel)
            if btn:
                btn.click(timeout=10_000)
                try:
                    page.wait_for_load_state("networkidle", timeout=15_000)
                except Exception:
                    pass
                page.wait_for_timeout(1_500)
                nav_clicked = True
        except Exception:
            pass
        if not nav_clicked:
            # Fallback: try numeric text click.
            try:
                btn = page.query_selector(f"a:has-text('{next_page_idx}'):below(:text('Wyniki'))")
                if btn:
                    btn.click(timeout=10_000)
                    page.wait_for_timeout(1_500)
                    nav_clicked = True
            except Exception:
                pass
        if not nav_clicked:
            logger.info("  no next page link, stopping at page %d", pg + 1)
            break
    logger.info("  → %d unique URLs from phrase=%r", len(results), phrase)
    return results


# ---------------------------------------------------------------------------
# scrape per-orzeczenie (kompat z scrape_consumer_docs.scrape_orzeczenie)
# ---------------------------------------------------------------------------


def _doc_id_from_url(url: str) -> str:
    """ID z URL: /content/$N/<court_id>_<syg>_<date>_<seq> ALBO /details/<kw>/<id>."""
    tail = url.rstrip("/").split("/")[-1]
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", tail)[:80]
    return f"orz_{cleaned}"


def _details_to_content_url(details_url: str) -> str:
    """Konwertuj /details/<phrase>/<doc_id> → /content/<phrase>/<doc_id>.

    Tapestry zwraca /details/ jako "metryka" page; /content/ ma pełną treść
    (chunk z tabu "Treść"). Mapping jest deterministyczny — same path component
    swap.
    """
    if "/details/" in details_url:
        return details_url.replace("/details/", "/content/", 1)
    return details_url


_SYG_PARSE_RE = re.compile(
    r"^\s*([IVXC]+\s+[A-Za-z]+(?:\s*[a-z]+)?\s+\d+/\d+)", re.IGNORECASE
)


def _scrape_orzeczenie_page(page: Page, url: str) -> dict[str, Any] | None:
    """Fetch + parsuj pojedyncze orzeczenie.

    Returns dict z polami {syg, date, court, body, doc_id, title} lub None.

    Akceptuje zarówno ``/content/...`` (pełna treść) jak ``/details/...``
    (metadata + tabs). Dla ``/details/`` URLi automatycznie przerzuca na
    ``/content/<keyword>/<doc_id>`` wariant.
    """
    # /details/ pages mają tylko metadata. /content/ ma pełną treść.
    fetch_url = _details_to_content_url(url)
    if not page.goto(fetch_url, timeout=60_000):
        return None
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception:
        pass
    page.wait_for_timeout(1_500)

    # Title — z H1/H2.
    title = ""
    try:
        for sel in ["h1", "h2", "h3"]:
            node = page.query_selector(sel)
            if node:
                t = normalize_pl(node.inner_text() or "")
                if t and len(t) > len(title):
                    title = t
        if not title:
            title = page.title()
    except Exception:
        pass

    # Body — szukamy strukturalnych selektorów. Tapestry portal używa
    # ``.grid9.simple.single.content`` lub po prostu ``#content``.
    body = ""
    try:
        for sel in [".grid9.simple.single.content", "#content", "main", "article", ".content"]:
            node = page.query_selector(sel)
            if node:
                txt = normalize_pl(node.inner_text() or "")
                if len(txt) > len(body):
                    body = txt
    except Exception as exc:
        logger.warning("  body extract failed: %s", exc)
    if not body or len(body) < 300:
        try:
            body = normalize_pl(page.locator("body").inner_text())
        except Exception:
            pass

    # Sygnatura, court, date z tytułu i body.
    syg_match = _SYG_PARSE_RE.match(title)
    syg = syg_match.group(1).strip() if syg_match else ""
    if not syg:
        m = re.search(r"\b([IVXC]+\s+[A-Za-z]+(?:\s*[a-z]+)?\s+\d+/\d+)", body[:500])
        if m:
            syg = m.group(1).strip()
    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", title + " " + body[:500])
    ruling_date = date_match.group(1) if date_match else ""
    court_match = re.search(r"Sąd\s+\w+(?:\s+w\s+\w+\w*)?", title + " " + body[:500])
    court = court_match.group(0) if court_match else ""

    return {
        "url": fetch_url,
        "title": title,
        "body": body,
        "sygnatura": syg,
        "ruling_date": ruling_date,
        "court": court,
        "doc_id": _doc_id_from_url(fetch_url),
    }


def _build_chunks_for_orzeczenie(
    parsed: dict[str, Any],
) -> tuple[list[OrzeczenieChunk], int]:
    """Z parsed body → chunks (mirror z scrape_consumer_docs)."""
    body = parsed["body"]
    words = count_words(body)
    if words < MIN_DOCUMENT_WORDS:
        return [], words

    # Strukturalne sekcje wyroku.
    section_pattern = re.compile(
        r"(?<=\s)(WYROK|UZASADNIENIE|POSTANOWIENIE|"
        r"Powołane\s+przepisy|Orzeczenia\s+podobne|Sygn\.\s*akt)\b",
    )
    headings: list[tuple[str, int]] = []
    for m in section_pattern.finditer(body):
        headings.append((normalize_pl(m.group(1)), m.start()))

    sections = _chunk_long_text(body, headings=headings or None)
    total = len(sections)
    doc_title = f"{parsed['sygnatura']} – wyrok" if parsed["sygnatura"] else parsed["title"][:120]
    chunks: list[OrzeczenieChunk] = []
    for j, (sec_title, sec_body) in enumerate(sections, start=1):
        chunks.append(
            OrzeczenieChunk(
                chunk_id=f"{parsed['doc_id']}_chunk_{j:03d}",
                document_id=parsed["doc_id"],
                document_title=doc_title,
                document_type="orzeczenie",
                source="orzeczenia.ms.gov.pl",
                source_url=parsed["url"],
                chunk_position=j,
                chunk_total=total,
                section_heading=sec_title,
                tresc=sec_body,
                scrape_date=SCRAPE_DATE,
                license=LICENSE_URZEDOWE,
                metadata={
                    "sygnatura": parsed["sygnatura"],
                    "court": parsed["court"],
                    "ruling_date": parsed["ruling_date"],
                    "format": "html",
                },
            )
        )
    return chunks, words


# ---------------------------------------------------------------------------
# main entry point
# ---------------------------------------------------------------------------


def scrape_orzeczenia_ms_expansion(
    output_dir: Path,
    *,
    keywords: list[str] | None = None,
    max_per_keyword: int = 100,
    max_pages_per_keyword: int = 5,
    headless: bool = True,
    skip_existing: bool = True,
) -> ScrapeStats:
    """Tapestry search expansion.

    Args:
        output_dir: katalog (musi zawierać ``orzeczenia/`` lub być nim).
        keywords: lista phrases (default ``DEFAULT_KEYWORDS``).
        max_per_keyword: kap na liczbę URLs per phrase.
        max_pages_per_keyword: kap na pages w paginatorze.
        headless: czy headless browser.
        skip_existing: nie pobieraj ponownie jeśli meta istnieje.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = output_dir / "_snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    keywords = keywords or DEFAULT_KEYWORDS
    stats = ScrapeStats(source="orzeczenia.ms.gov.pl-expansion", license=LICENSE_URZEDOWE)
    all_chunks: list[OrzeczenieChunk] = []
    seen_urls: set[str] = set()

    # Pre-load existing meta files dla skip_existing.
    existing_doc_ids: set[str] = set()
    if skip_existing:
        for f in output_dir.glob("orz_*.meta.json"):
            existing_doc_ids.add(f.stem)
        logger.info("pre-existing orz docs in output: %d", len(existing_doc_ids))

    with BrowserSession(headless=headless) as sess:
        page = sess.new_page()

        # Phase 1 — collect URLs per keyword.
        url_pool: list[dict[str, str]] = []
        for kw in keywords:
            sess.throttle()
            results = _search_for_phrase(page, kw, max_pages=max_pages_per_keyword)
            for r in results[:max_per_keyword]:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    url_pool.append(r)
        stats.attempted = len(url_pool)
        logger.info("URL pool: %d unique orzeczenia URLs across %d keywords", len(url_pool), len(keywords))

        # Phase 2 — scrape per-orzeczenie.
        for item in url_pool:
            url = item["url"]
            doc_id = _doc_id_from_url(url)
            if doc_id in existing_doc_ids:
                logger.info("skip existing %s", doc_id)
                stats.skipped += 1
                stats.skip_reasons["already_exists"] = stats.skip_reasons.get("already_exists", 0) + 1
                continue
            sess.throttle()
            try:
                parsed = _scrape_orzeczenie_page(page, url)
            except Exception as exc:
                logger.warning("scrape page %s failed: %s", url, exc)
                stats.failed += 1
                stats.parse_errors += 1
                continue
            if parsed is None or not parsed["body"]:
                stats.failed += 1
                stats.skip_reasons["empty_body"] = stats.skip_reasons.get("empty_body", 0) + 1
                continue

            chunks, words = _build_chunks_for_orzeczenie(parsed)
            if not chunks:
                stats.skipped += 1
                stats.skip_reasons["too_short"] = stats.skip_reasons.get("too_short", 0) + 1
                continue

            # Per-orzeczenie meta.
            meta = OrzeczenieMeta(
                document_id=doc_id,
                document_title=chunks[0].document_title,
                document_type="orzeczenie",
                source="orzeczenia.ms.gov.pl",
                source_url=url,
                total_chunks=len(chunks),
                total_words=words,
                license=LICENSE_URZEDOWE,
                scrape_date=SCRAPE_DATE,
                citation_recommendation=(
                    f"{parsed['court'] or 'Sąd Powszechny'}. "
                    f"Wyrok z dnia {parsed['ruling_date'] or 'n.d.'}, "
                    f"sygn. akt {parsed['sygnatura'] or '?'}. {url}"
                ),
                author=parsed["court"] or None,
            )
            write_meta(output_dir / f"{doc_id}.meta.json", meta)
            all_chunks.extend(chunks)
            stats.succeeded += 1
            stats.total_words += words
            logger.info(
                "  scraped %s (%s, %s): %d words → %d chunks",
                doc_id,
                parsed["sygnatura"],
                parsed["court"],
                words,
                len(chunks),
            )

    # Append-write do documents.jsonl (zachowując istniejące rekordy E4).
    jsonl_path = output_dir / "documents.jsonl"
    if jsonl_path.exists():
        # Append-mode: czytamy existing + dodajemy nowe.
        existing_count = 0
        with jsonl_path.open(encoding="utf-8") as f:
            for _ in f:
                existing_count += 1
        logger.info("appending %d new chunks to %d existing", len(all_chunks), existing_count)
        with jsonl_path.open("a", encoding="utf-8") as f:
            import json as _json

            for ch in all_chunks:
                f.write(_json.dumps(asdict(ch), ensure_ascii=False) + "\n")
        n = existing_count + len(all_chunks)
    else:
        n = write_jsonl(all_chunks, jsonl_path)
    logger.info("documents.jsonl now has %d records", n)
    stats.notes += f"jsonl_records_total={n}; new_added={len(all_chunks)}"
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-per-keyword", type=int, default=100)
    parser.add_argument("--max-pages-per-keyword", type=int, default=5)
    parser.add_argument("--keywords", nargs="*", default=None)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
        stream=sys.stderr,
    )

    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    stats = scrape_orzeczenia_ms_expansion(
        output_dir,
        keywords=args.keywords,
        max_per_keyword=args.max_per_keyword,
        max_pages_per_keyword=args.max_pages_per_keyword,
        headless=not args.headed,
        skip_existing=not args.no_skip_existing,
    )
    summary_path = output_dir / "scrape_expansion_summary.json"
    import json

    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(stats.as_dict(), f, ensure_ascii=False, indent=2)
    logger.info("=== DONE === %s", stats.as_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
