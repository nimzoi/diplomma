"""Pełne dokumenty consumer rights polish — scraper long-form materiałów.

Komplementarny do UOKiK Q&A scraper i legal fora (które zbierają krótkie pytania).
Ten scraper zbiera EXCLUSIVELY long-form documents (>500 słów typically):

  1. UOKiK PDFs            -- poradniki/broszury (publikacje + materiały-do-pobrania)
  2. RF analizy/raporty    -- Rzecznik Finansowy PDFs (baza-wiedzy)
  3. Federacja Konsumentów -- HTML artykuły + PDF poradniki
  4. orzeczenia.ms.gov.pl  -- pełne wyroki + uzasadnienia (consumer cases)

Output struktura:

    data/raw/consumer_documents_2026-05-16/
        uokik_pdfs/
            documents.jsonl            -- chunks z PDFs (per-section split)
            <doc_id>.meta.json         -- metadata per dokument
        rf_pdfs/
            documents.jsonl
            <doc_id>.meta.json
        federacja_konsumentow/
            documents.jsonl
            <doc_id>.meta.json
        orzeczenia/
            documents.jsonl
            <doc_id>.meta.json
        scrape_summary.json            -- agregat statystyk

Schema (rozszerzony LegalChunk pattern, zob. `src/halu/schemas.py`):

    {
        "chunk_id":         "uokik_pdf_1185_chunk_3",
        "document_id":      "uokik_pdf_1185",
        "document_title":   "Ty też masz wpływ! - poradnik",
        "document_type":    "poradnik" | "raport" | "artykul" | "orzeczenie" | "broszura",
        "source":           "uokik.gov.pl" | "rf.gov.pl" | "federacja-konsumentow.org.pl"
                            | "orzeczenia.ms.gov.pl",
        "source_url":       "https://...",
        "chunk_position":   3,
        "chunk_total":      12,
        "section_heading":  "Procedura odstąpienia" | null,
        "tresc":            "...",                  # NFC-normalized
        "scrape_date":      "2026-05-16",
        "license":          "urzędowe (Art. 4 PrAut)" | "CC BY-SA 4.0" | "fair-use Art. 29" | "TBD",
        "metadata":         {...}                   # author, date, etc.
    }

License rationale:
  - UOKiK + RF + orzeczenia: urzędowe (Art. 4 ust. 2 ustawy o prawie autorskim,
    DU/1994/83). Materiały urzędowe (broszury edukacyjne agencji państwowej +
    publikacje sądu) NIE są przedmiotem prawa autorskiego.
  - Federacja Konsumentów: NGO, formalnie © Federacja, ale używamy w ramach
    fair-use art. 29 PrAut (cytowanie utworów w celach naukowych do pracy
    inżynierskiej). Attribution retained w metadata.

Usage:
    uv run python -m src.scrape.documents.scrape_consumer_docs \\
        --output ../data/raw/consumer_documents_2026-05-16

    # Single source
    uv run python -m src.scrape.documents.scrape_consumer_docs \\
        --output ../data/raw/consumer_documents_2026-05-16 \\
        --source uokik

    # Dry-run (skip actual download, print plan)
    uv run python -m src.scrape.documents.scrape_consumer_docs \\
        --output ../data/raw/consumer_documents_2026-05-16 --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from io import BytesIO
from pathlib import Path

import pdfplumber
import requests
from bs4 import BeautifulSoup, Tag

LOGGER = logging.getLogger("scrape_consumer_docs")

USER_AGENT = (
    "Mozilla/5.0 (compatible; PJATK-thesis-bot/1.0; +research, contact magmarsochacka@gmail.com)"
)
RATE_LIMIT_SECONDS = 1.0
REQUEST_TIMEOUT = 60
MIN_DOCUMENT_WORDS = 350  # skip if shorter (faux long-form)
MAX_CHUNK_CHARS = 1800  # target ~500-2000 chars/chunk
MIN_CHUNK_CHARS = 250  # don't emit tiny stub chunks
SCRAPE_DATE = "2026-05-16"

LICENSE_URZEDOWE = "urzędowe (Art. 4 ust. 2 PrAut)"
LICENSE_FAIR_USE = "fair-use Art. 29 PrAut"


# ---------------------------------------------------------------------------
# data model
# ---------------------------------------------------------------------------


@dataclass
class DocumentChunk:
    """Chunk z pełnego dokumentu (per-section split lub paragraph cluster)."""

    chunk_id: str
    document_id: str
    document_title: str
    document_type: str  # "poradnik" / "raport" / "artykul" / "orzeczenie" / "broszura"
    source: str
    source_url: str
    chunk_position: int
    chunk_total: int
    section_heading: str | None
    tresc: str
    scrape_date: str
    license: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class DocumentMeta:
    """Per-document metadata file."""

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


@dataclass
class SourceStats:
    """Per-source aggregate stats."""

    source: str
    attempted_urls: int = 0
    documents_scraped: int = 0
    documents_skipped: int = 0
    skip_reasons: dict[str, int] = field(default_factory=dict)
    total_chunks: int = 0
    total_words: int = 0
    license: str = ""


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "pl,en;q=0.7"})
    return s


def normalize_text(text: str) -> str:
    """NFC + whitespace collapse + zap non-breaking spaces."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\xa0", " ").replace("​", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def chunk_long_text(
    full_text: str,
    *,
    headings: list[tuple[str, int]] | None = None,
) -> list[tuple[str | None, str]]:
    """Split long text into chunks targeted at MAX_CHUNK_CHARS.

    Strategy:
      1. If `headings` is given as list[(heading_text, char_offset)], split there.
      2. Within each section (or whole text if no headings), if longer than
         MAX_CHUNK_CHARS, split on paragraph boundaries (double newline / \\n\\n)
         and pack greedily into chunks ≤ MAX_CHUNK_CHARS.
      3. Drop chunks shorter than MIN_CHUNK_CHARS unless they're the only chunk.

    Returns: list[(section_heading_or_None, chunk_text)]
    """
    full_text = full_text.strip()
    if not full_text:
        return []

    # Step 1: section split.
    sections: list[tuple[str | None, str]]
    if headings:
        sections = []
        # Sort by offset to ensure ascending.
        h = sorted(headings, key=lambda x: x[1])
        for i, (title, start) in enumerate(h):
            end = h[i + 1][1] if i + 1 < len(h) else len(full_text)
            body = full_text[start:end].strip()
            if body:
                sections.append((title, body))
        # Pre-heading content (if any) becomes a "Lead" section.
        first_off = h[0][1] if h else 0
        if first_off > 0:
            lead = full_text[:first_off].strip()
            if lead:
                sections.insert(0, (None, lead))
        if not sections:
            sections = [(None, full_text)]
    else:
        sections = [(None, full_text)]

    # Step 2: within each section, paragraph-greedy pack into MAX_CHUNK_CHARS.
    output: list[tuple[str | None, str]] = []
    for sec_title, sec_body in sections:
        if len(sec_body) <= MAX_CHUNK_CHARS:
            output.append((sec_title, sec_body))
            continue

        # Split on paragraph boundaries first; if individual paragraph still
        # too long, sentence-split that one.
        paragraphs = re.split(r"\n\s*\n", sec_body)
        # If no paragraph boundaries (single-paragraph blob), fall back to
        # sentence split.
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
                # If single paragraph alone exceeds MAX, hard split it.
                if len(para) > MAX_CHUNK_CHARS:
                    for offset in range(0, len(para), MAX_CHUNK_CHARS):
                        output.append((sec_title, para[offset : offset + MAX_CHUNK_CHARS]))
                    buf = ""
                else:
                    buf = para
        if buf:
            output.append((sec_title, buf))

    # Step 3: drop tiny stub chunks unless only one.
    if len(output) > 1:
        output = [(t, b) for t, b in output if len(b) >= MIN_CHUNK_CHARS]
        if not output:
            # All too small; fall back to single concatenated chunk.
            joined = "\n\n".join(s for _, s in sections if s)
            output = [(None, joined)]

    return output


def write_jsonl(path: Path, items: Iterable[DocumentChunk]) -> int:
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")
            n += 1
    return n


def write_meta(path: Path, meta: DocumentMeta) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(asdict(meta), f, ensure_ascii=False, indent=2)


def fetch(url: str, session: requests.Session) -> requests.Response | None:
    try:
        LOGGER.info("GET %s", url)
        resp = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        time.sleep(RATE_LIMIT_SECONDS)
        return resp
    except requests.RequestException as exc:
        LOGGER.warning("  failed: %s", exc)
        return None


def extract_pdf_text(pdf_bytes: bytes) -> tuple[str, list[tuple[str, int]]]:
    """Wyciągnij tekst PDF + heuristic heading detection.

    Returns: (full_text, headings) — headings as [(text, char_offset)].
    Heuristic: linia będąca heading gdy:
      - kończy się bez kropki
      - <80 chars
      - cała duża litera lub ma "Rozdział"/"Część"/"Sekcja"
    """
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            page_texts = []
            for page in pdf.pages:
                txt = page.extract_text() or ""
                page_texts.append(txt)
        full = "\n\n".join(page_texts)
    except Exception as exc:
        LOGGER.warning("  pdfplumber failed: %s", exc)
        return "", []

    # Heading detection: collect candidate heading texts from raw lines, then
    # re-locate offsets w znormalizowanym tekście (offsety w raw vs normalized
    # różnią się po collapse'ie whitespace). Filter noise: single roman numerals,
    # SPIS TREŚCI, page/footer markers, very short stubs.
    noise_heading_re = re.compile(
        r"^(SPIS\s+TREŚCI|I{1,3}V?|VI{0,3}|IX|X|RF\s+DLA\s+POSZKODOWANYCH:?|"
        r"Strona\s+\d+|\d+|©.*)$",
        re.IGNORECASE,
    )
    candidate_headings: list[str] = []
    for line in full.split("\n"):
        ln = line.strip()
        if (
            ln
            and 5 <= len(ln) < 80
            and not ln.endswith((".", "?", "!"))
            and not noise_heading_re.match(ln)
            and (
                ln.isupper()
                or re.match(r"^(Rozdział|Część|Sekcja|Cz\.)\s+\w+", ln, re.IGNORECASE)
                or re.match(r"^\d+(\.\d+)*\.?\s+[A-ZĄĆĘŁŃÓŚŹŻ]", ln)
            )
        ):
            candidate_headings.append(normalize_text(ln))

    normalized = normalize_text(full)
    # Re-locate each heading in normalized text. Dedup duplicates (TOC repeats);
    # for each heading text take FIRST occurrence past the previous one.
    headings: list[tuple[str, int]] = []
    cursor = 0
    seen_titles: set[str] = set()
    for title in candidate_headings:
        if not title or title in seen_titles:
            continue
        idx = normalized.find(title, cursor)
        if idx == -1:
            continue
        headings.append((title, idx))
        cursor = idx + len(title)
        seen_titles.add(title)

    return normalized, headings


# ---------------------------------------------------------------------------
# UOKiK PDFs adapter
# ---------------------------------------------------------------------------

# Hand-curated z `/publikacje` + `/materialy-do-pobrania/` 2026-05-16.
# Każdy ma >2 MB i kilkadziesiąt stron — high quality long-form consumer education.
UOKIK_PDFS: list[dict[str, str]] = [
    {
        "id": "uokik_pdf_1185",
        "title": "Ty też masz wpływ! Poradnik dla konsumentów (UOKiK 2025)",
        "url": "https://uokik.gov.pl/Download/1185",
        "type": "poradnik",
        "year": "2025",
    },
    {
        "id": "uokik_pdf_1313",
        "title": "Zakupy z Azji – poradnik (UOKiK 2025)",
        "url": "https://uokik.gov.pl/Download/1313",
        "type": "poradnik",
        "year": "2025",
    },
    {
        "id": "uokik_pdf_1811",
        "title": "Nie klikaj w ciemno! Poradnik (UOKiK 2026)",
        "url": "https://uokik.gov.pl/Download/1811",
        "type": "poradnik",
        "year": "2026",
    },
    {
        "id": "uokik_pdf_1882",
        "title": "Poradnik koncertowy UOKiK (UOKiK 2026)",
        "url": "https://uokik.gov.pl/Download/1882",
        "type": "poradnik",
        "year": "2026",
    },
    {
        "id": "uokik_pdf_716",
        "title": "Reklamacja. Niezgodność towaru z umową (UOKiK 2025)",
        "url": "https://uokik.gov.pl/Download/716",
        "type": "broszura",
        "year": "2025",
    },
    {
        "id": "uokik_pdf_958",
        "title": "Pomoc dla konsumentów (UOKiK 2025)",
        "url": "https://uokik.gov.pl/Download/958",
        "type": "broszura",
        "year": "2025",
    },
    {
        "id": "uokik_pdf_653",
        "title": "Badanie na pokaz. Uważaj! (UOKiK 2025)",
        "url": "https://uokik.gov.pl/Download/653",
        "type": "broszura",
        "year": "2025",
    },
    {
        "id": "uokik_pdf_954",
        "title": "O czym pamiętać po stracie bliskiej osoby (UOKiK 2024)",
        "url": "https://uokik.gov.pl/Download/954",
        "type": "broszura",
        "year": "2024",
    },
    {
        "id": "uokik_pdf_96",
        "title": "Przewodnik po zmianach w prawie konsumenckim (UOKiK)",
        "url": "https://uokik.gov.pl/Download/96",
        "type": "poradnik",
        "year": "2014",
    },
    {
        "id": "uokik_pdf_1203",
        "title": "Bezpieczny plac zabaw. Porady dla rodziców i opiekunów (UOKiK 2025)",
        "url": "https://uokik.gov.pl/Download/1203",
        "type": "broszura",
        "year": "2025",
    },
    {
        "id": "uokik_pdf_1204",
        "title": "Bezpieczny plac zabaw. Porady dla zarządców i właścicieli (UOKiK 2025)",
        "url": "https://uokik.gov.pl/Download/1204",
        "type": "broszura",
        "year": "2025",
    },
]


def scrape_uokik_pdfs(
    session: requests.Session,
    output_dir: Path,
    stats: SourceStats,
    dry_run: bool = False,
) -> list[DocumentChunk]:
    """Pobierz hand-curated PDFs z UOKiK i splituj na chunks."""
    out_chunks: list[DocumentChunk] = []
    pdfs_dir = output_dir / "uokik_pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)

    for spec in UOKIK_PDFS:
        stats.attempted_urls += 1
        url = spec["url"]
        doc_id = spec["id"]
        title = spec["title"]

        if dry_run:
            LOGGER.info("[dry] would fetch %s", url)
            continue

        resp = fetch(url, session)
        if resp is None:
            stats.documents_skipped += 1
            stats.skip_reasons["fetch_failed"] = stats.skip_reasons.get("fetch_failed", 0) + 1
            continue

        ctype = resp.headers.get("content-type", "")
        if "pdf" not in ctype.lower() and not resp.content.startswith(b"%PDF"):
            LOGGER.warning("  %s not PDF (ctype=%s); skipping", url, ctype)
            stats.documents_skipped += 1
            stats.skip_reasons["not_pdf"] = stats.skip_reasons.get("not_pdf", 0) + 1
            continue

        full_text, headings = extract_pdf_text(resp.content)
        words = count_words(full_text)
        if words < MIN_DOCUMENT_WORDS:
            LOGGER.warning("  %s only %d words (<%d); skipping", url, words, MIN_DOCUMENT_WORDS)
            stats.documents_skipped += 1
            stats.skip_reasons["too_short"] = stats.skip_reasons.get("too_short", 0) + 1
            continue

        # Drop "page N of M" + footer/repetitive boilerplate (heuristic).
        full_text = re.sub(r"Strona\s+\d+\s+z\s+\d+", "", full_text)

        sections = chunk_long_text(full_text, headings=headings or None)
        total = len(sections)
        for i, (sec_title, sec_body) in enumerate(sections, start=1):
            out_chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc_id}_chunk_{i:03d}",
                    document_id=doc_id,
                    document_title=title,
                    document_type=spec["type"],
                    source="uokik.gov.pl",
                    source_url=url,
                    chunk_position=i,
                    chunk_total=total,
                    section_heading=sec_title,
                    tresc=sec_body,
                    scrape_date=SCRAPE_DATE,
                    license=LICENSE_URZEDOWE,
                    metadata={
                        "publication_year": spec.get("year"),
                        "format": "pdf",
                    },
                )
            )

        # Per-document meta sidecar.
        meta = DocumentMeta(
            document_id=doc_id,
            document_title=title,
            document_type=spec["type"],
            source="uokik.gov.pl",
            source_url=url,
            total_chunks=total,
            total_words=words,
            license=LICENSE_URZEDOWE,
            scrape_date=SCRAPE_DATE,
            citation_recommendation=(
                f"UOKiK ({spec.get('year', 'n.d.')}). {title}. "
                f"Urząd Ochrony Konkurencji i Konsumentów. {url}"
            ),
            author="Urząd Ochrony Konkurencji i Konsumentów",
            publication_year=int(spec["year"]) if spec.get("year") else None,
            pdf_size_bytes=len(resp.content),
        )
        write_meta(pdfs_dir / f"{doc_id}.meta.json", meta)

        stats.documents_scraped += 1
        stats.total_chunks += total
        stats.total_words += words
        LOGGER.info(
            "  scraped %s: %d words → %d chunks (%d sections detected)",
            doc_id,
            words,
            total,
            len(headings or []),
        )

    return out_chunks


# ---------------------------------------------------------------------------
# Rzecznik Finansowy PDFs adapter
# ---------------------------------------------------------------------------


def scrape_rf_index(session: requests.Session) -> list[dict[str, str]]:
    """Pobierz indeks PDFs z analizy-i-raporty.

    Returns: list[{"title", "url"}] gdzie url == direct PDF download.
    """
    index_urls = [
        "https://rf.gov.pl/edukacja/baza-wiedzy/analizy-i-raporty/",
        "https://rf.gov.pl/edukacja/baza-wiedzy/poradniki/",
    ]
    found: dict[str, dict[str, str]] = {}  # dedup by url

    for index_url in index_urls:
        resp = fetch(index_url, session)
        if resp is None:
            continue
        soup = BeautifulSoup(resp.text, "lxml")

        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if not isinstance(href, str):
                continue
            if not href.lower().endswith(".pdf"):
                continue
            # Absolute URL
            if href.startswith("/"):
                href = "https://rf.gov.pl" + href
            elif not href.startswith("http"):
                continue
            # Skip non-rf domains.
            if "rf.gov.pl" not in href:
                continue
            title_raw = a.get_text(" ", strip=True)
            title = normalize_text(title_raw) or Path(href).stem
            # Drop generic "Pobierz" / "PDF" link captions; use parent context.
            if len(title) < 20:
                parent = a.find_parent(["li", "p", "div", "article"])
                if isinstance(parent, Tag):
                    parent_text = normalize_text(parent.get_text(" ", strip=True))
                    if len(parent_text) > len(title):
                        title = parent_text[:200]
            found.setdefault(href, {"title": title, "url": href})

    LOGGER.info("RF index discovered %d unique PDFs", len(found))
    return list(found.values())


def scrape_rf_pdfs(
    session: requests.Session,
    output_dir: Path,
    stats: SourceStats,
    dry_run: bool = False,
    max_docs: int | None = None,
) -> list[DocumentChunk]:
    """Pobierz PDFs z indeksu RF analizy/raporty/poradniki."""
    out_chunks: list[DocumentChunk] = []
    rf_dir = output_dir / "rf_pdfs"
    rf_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        LOGGER.info("[dry] would discover RF index")
        return []

    catalog = scrape_rf_index(session)
    if max_docs:
        catalog = catalog[:max_docs]

    for i, spec in enumerate(catalog, start=1):
        stats.attempted_urls += 1
        url = spec["url"]
        title = spec["title"][:300] or f"RF analiza {i}"
        # Deterministic doc_id from URL.
        slug = re.sub(r"[^a-z0-9]+", "-", url.lower())[-60:].strip("-")
        doc_id = f"rf_pdf_{slug}"

        resp = fetch(url, session)
        if resp is None:
            stats.documents_skipped += 1
            stats.skip_reasons["fetch_failed"] = stats.skip_reasons.get("fetch_failed", 0) + 1
            continue
        if not resp.content.startswith(b"%PDF"):
            stats.documents_skipped += 1
            stats.skip_reasons["not_pdf"] = stats.skip_reasons.get("not_pdf", 0) + 1
            continue

        full_text, headings = extract_pdf_text(resp.content)
        words = count_words(full_text)
        if words < MIN_DOCUMENT_WORDS:
            stats.documents_skipped += 1
            stats.skip_reasons["too_short"] = stats.skip_reasons.get("too_short", 0) + 1
            LOGGER.warning("  %s only %d words; skipping", doc_id, words)
            continue

        full_text = re.sub(r"Strona\s+\d+\s+z\s+\d+", "", full_text)
        sections = chunk_long_text(full_text, headings=headings or None)
        total = len(sections)
        for j, (sec_title, sec_body) in enumerate(sections, start=1):
            out_chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc_id}_chunk_{j:03d}",
                    document_id=doc_id,
                    document_title=title,
                    document_type="raport",
                    source="rf.gov.pl",
                    source_url=url,
                    chunk_position=j,
                    chunk_total=total,
                    section_heading=sec_title,
                    tresc=sec_body,
                    scrape_date=SCRAPE_DATE,
                    license=LICENSE_URZEDOWE,
                    metadata={"format": "pdf"},
                )
            )

        meta = DocumentMeta(
            document_id=doc_id,
            document_title=title,
            document_type="raport",
            source="rf.gov.pl",
            source_url=url,
            total_chunks=total,
            total_words=words,
            license=LICENSE_URZEDOWE,
            scrape_date=SCRAPE_DATE,
            citation_recommendation=(f"Rzecznik Finansowy. {title}. {url}"),
            author="Rzecznik Finansowy",
            pdf_size_bytes=len(resp.content),
        )
        write_meta(rf_dir / f"{doc_id}.meta.json", meta)

        stats.documents_scraped += 1
        stats.total_chunks += total
        stats.total_words += words
        LOGGER.info("  scraped %s: %d words → %d chunks", doc_id, words, total)

    return out_chunks


# ---------------------------------------------------------------------------
# Federacja Konsumentów adapter (PDFs + HTML)
# ---------------------------------------------------------------------------

# Hand-curated PDFs + long-form HTML articles z federacji.
# Discovered via WebSearch + manual browse 2026-05-16.
FEDERACJA_PDFS: list[dict[str, str]] = [
    {
        "id": "fk_pdf_swiadomy_konsument_2023",
        "title": "Świadomy i bezpieczny konsument – poradnik (Federacja Konsumentów 2023)",
        "url": "https://www.federacja-konsumentow.org.pl/p,1810,9711e,poradnik-swiadomy-i-bezpieczny-konsument-fk-2023.pdf",
        "type": "poradnik",
        "year": "2023",
    },
    {
        "id": "fk_pdf_prawa_konsumenta_samochod",
        "title": "Prawa konsumenta przy zakupie samochodu – przewodnik (Federacja Konsumentów)",
        "url": "https://www.federacja-konsumentow.org.pl/p,1927,c02bc,prawa-konsumenta-przy-zakupie-zamochodu--przewodnik.pdf",
        "type": "poradnik",
        "year": None,
    },
    {
        "id": "fk_pdf_bezpieczne_e_zakupy",
        "title": "(NIE)BEZPIECZNE e-ZAKUPY – broszura (Federacja Konsumentów)",
        "url": "https://www.federacja-konsumentow.org.pl/download/internet_bezpieczne_zakupy_w_internecie.pdf",
        "type": "broszura",
        "year": None,
    },
]

# Long-form HTML articles z federacji (discovered via WebSearch).
FEDERACJA_HTML: list[dict[str, str]] = [
    {
        "id": "fk_html_swiadomy_konsument_n1532",
        "title": "Świadomy i bezpieczny konsument – wprowadzenie (FK)",
        "url": "https://www.federacja-konsumentow.org.pl/n,6,1532,1,1,swiadomy-i-bezpieczny-konsument--poradnik-dla-konsumentow.html",
    },
    {
        "id": "fk_html_abc_uslugi_n391",
        "title": "ABC konsumenta – usługi (Potyczki z fachowcem) (FK)",
        "url": "https://www.federacja-konsumentow.org.pl/n,155,391,89,1,abc-konsumenta--uslugi-potyczki-z-fachowcem.html",
    },
    {
        "id": "fk_html_dane_osobowe_n226",
        "title": "Najpierw zgoda konsumenta – potem oferta (dane osobowe) (FK)",
        "url": "http://www.federacja-konsumentow.org.pl/226,dane-osobowe.html",
    },
]


def scrape_federacja_html(
    session: requests.Session, spec: dict[str, str]
) -> tuple[str, str | None]:
    """Pobierz HTML artykuł federacji i wyciągnij main text."""
    resp = fetch(spec["url"], session)
    if resp is None:
        return "", None
    # Force UTF-8 (some pages serve windows-1250 by header).
    resp.encoding = resp.apparent_encoding or "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")
    # Strip nav/footer/script/style.
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
        tag.decompose()
    # Try common main-content containers.
    main = None
    for selector in ["#content", "main", ".content", "#main", ".main", "article", "#text"]:
        node = soup.select_one(selector)
        if node and len(node.get_text(strip=True)) > 300:
            main = node
            break
    if main is None:
        main = soup.body or soup
    text = normalize_text(main.get_text("\n", strip=True))
    # Try to detect title.
    title = None
    h1 = soup.find("h1")
    if isinstance(h1, Tag):
        title = normalize_text(h1.get_text(strip=True))
    return text, title


def scrape_federacja(
    session: requests.Session,
    output_dir: Path,
    stats: SourceStats,
    dry_run: bool = False,
) -> list[DocumentChunk]:
    """PDFs + HTML articles z Federacji Konsumentów."""
    out_chunks: list[DocumentChunk] = []
    fk_dir = output_dir / "federacja_konsumentow"
    fk_dir.mkdir(parents=True, exist_ok=True)

    # PDFs first.
    for spec in FEDERACJA_PDFS:
        stats.attempted_urls += 1
        if dry_run:
            LOGGER.info("[dry] would fetch FK PDF %s", spec["url"])
            continue
        resp = fetch(spec["url"], session)
        if resp is None or not resp.content.startswith(b"%PDF"):
            stats.documents_skipped += 1
            stats.skip_reasons["fetch_failed_or_not_pdf"] = (
                stats.skip_reasons.get("fetch_failed_or_not_pdf", 0) + 1
            )
            continue
        full_text, headings = extract_pdf_text(resp.content)
        words = count_words(full_text)
        if words < MIN_DOCUMENT_WORDS:
            stats.documents_skipped += 1
            stats.skip_reasons["too_short"] = stats.skip_reasons.get("too_short", 0) + 1
            continue
        sections = chunk_long_text(full_text, headings=headings or None)
        total = len(sections)
        for j, (sec_title, sec_body) in enumerate(sections, start=1):
            out_chunks.append(
                DocumentChunk(
                    chunk_id=f"{spec['id']}_chunk_{j:03d}",
                    document_id=spec["id"],
                    document_title=spec["title"],
                    document_type=spec["type"],
                    source="federacja-konsumentow.org.pl",
                    source_url=spec["url"],
                    chunk_position=j,
                    chunk_total=total,
                    section_heading=sec_title,
                    tresc=sec_body,
                    scrape_date=SCRAPE_DATE,
                    license=LICENSE_FAIR_USE,
                    metadata={"format": "pdf", "publication_year": spec.get("year")},
                )
            )
        meta = DocumentMeta(
            document_id=spec["id"],
            document_title=spec["title"],
            document_type=spec["type"],
            source="federacja-konsumentow.org.pl",
            source_url=spec["url"],
            total_chunks=total,
            total_words=words,
            license=LICENSE_FAIR_USE,
            scrape_date=SCRAPE_DATE,
            citation_recommendation=(
                f"Federacja Konsumentów ({spec.get('year', 'n.d.')}). "
                f"{spec['title']}. {spec['url']}"
            ),
            author="Federacja Konsumentów",
            publication_year=int(spec["year"]) if spec.get("year") else None,
            pdf_size_bytes=len(resp.content),
        )
        write_meta(fk_dir / f"{spec['id']}.meta.json", meta)
        stats.documents_scraped += 1
        stats.total_chunks += total
        stats.total_words += words
        LOGGER.info("  scraped FK PDF %s: %d words → %d chunks", spec["id"], words, total)

    # HTML articles.
    for spec in FEDERACJA_HTML:
        stats.attempted_urls += 1
        if dry_run:
            LOGGER.info("[dry] would fetch FK HTML %s", spec["url"])
            continue
        text, detected_title = scrape_federacja_html(session, spec)
        title = detected_title or spec["title"]
        words = count_words(text)
        if words < MIN_DOCUMENT_WORDS:
            stats.documents_skipped += 1
            stats.skip_reasons["too_short"] = stats.skip_reasons.get("too_short", 0) + 1
            LOGGER.warning("  FK %s only %d words; skipping", spec["id"], words)
            continue
        sections = chunk_long_text(text)
        total = len(sections)
        for j, (sec_title, sec_body) in enumerate(sections, start=1):
            out_chunks.append(
                DocumentChunk(
                    chunk_id=f"{spec['id']}_chunk_{j:03d}",
                    document_id=spec["id"],
                    document_title=title,
                    document_type="artykul",
                    source="federacja-konsumentow.org.pl",
                    source_url=spec["url"],
                    chunk_position=j,
                    chunk_total=total,
                    section_heading=sec_title,
                    tresc=sec_body,
                    scrape_date=SCRAPE_DATE,
                    license=LICENSE_FAIR_USE,
                    metadata={"format": "html"},
                )
            )
        meta = DocumentMeta(
            document_id=spec["id"],
            document_title=title,
            document_type="artykul",
            source="federacja-konsumentow.org.pl",
            source_url=spec["url"],
            total_chunks=total,
            total_words=words,
            license=LICENSE_FAIR_USE,
            scrape_date=SCRAPE_DATE,
            citation_recommendation=(f"Federacja Konsumentów. {title}. {spec['url']}"),
            author="Federacja Konsumentów",
        )
        write_meta(fk_dir / f"{spec['id']}.meta.json", meta)
        stats.documents_scraped += 1
        stats.total_chunks += total
        stats.total_words += words
        LOGGER.info("  scraped FK HTML %s: %d words → %d chunks", spec["id"], words, total)

    return out_chunks


# ---------------------------------------------------------------------------
# orzeczenia.ms.gov.pl adapter (court rulings)
# ---------------------------------------------------------------------------

# Hand-curated list court rulings discovered via WebSearch 2026-05-16,
# all consumer-rights related (rękojmia, sprzedaż konsumencka, niezgodność
# towaru, klauzule abuzywne).
ORZECZENIA_URLS: list[dict[str, str]] = [
    {
        "id": "orz_I_C_448_2020",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/153505100000503_I_C_000448_2020_Uz_2021-09-16_001",
        "syg": "I C 448/20",
    },
    {
        "id": "orz_I_C_25_2023",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/153505050000503_I_C_000025_2023_Uz_2024-08-22_001",
        "syg": "I C 25/23",
    },
    {
        "id": "orz_I_C_435_2018",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/150525050000503_I_C_000435_2018_Uz_2021-04-21_001",
        "syg": "I C 435/18",
    },
    {
        "id": "orz_I_C_619_2019",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/154505200000503_I_C_000619_2019_Uz_2021-03-10_001",
        "syg": "I C 619/19",
    },
    {
        "id": "orz_I_C_50_2022",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/152510450000503_I_C_000050_2022_Uz_2023-03-06_002",
        "syg": "I C 50/22",
    },
    {
        "id": "orz_I_C_175_2022",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/153505100000503_I_C_000175_2022_Uz_2023-05-10_001",
        "syg": "I C 175/22",
    },
    {
        "id": "orz_XVII_AmC_1252_2015",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/154505000005127_XVII_AmC_001252_2015_Uz_2018-08-06_001",
        "syg": "XVII AmC 1252/15",
    },
    {
        "id": "orz_III_Ca_1369_2019",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/152510000001503_III_Ca_001369_2019_Uz_2020-03-09_001",
        "syg": "III Ca 1369/19",
    },
    {
        "id": "orz_I_C_841_2020",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/155515300000503_I_C_000841_2020_Uz_2021-06-14_002",
        "syg": "I C 841/20",
    },
    {
        "id": "orz_XI_GC_953_2021",
        "url": "https://orzeczenia.ms.gov.pl/content/$N/155515300005527_XI_GC_000953_2021_Uz_2023-02-13_001",
        "syg": "XI GC 953/21",
    },
]


def discover_orzeczenia_via_search(
    session: requests.Session, queries: list[str]
) -> list[dict[str, str]]:
    """Try ETL: scrape the search results listing dla consumer queries.

    Search returns HTML with links to /content/$N/<id>. Extract rulings up to
    per-query cap.

    NOTE: Search jest stateful Tapestry endpoint; często wymaga sesji + form
    state. Tutaj próbujemy GET pattern z parametrami URL (works dla simple
    queries). Jeśli pusto — wracamy do hand-curated ORZECZENIA_URLS.
    """
    found: dict[str, dict[str, str]] = {}
    for q in queries:
        # GET pattern (works for simple search): /search/advanced/szukaj?all=...
        url = (
            "https://orzeczenia.ms.gov.pl/search/advanced/szukaj?"
            "wszystkie-slowa=" + requests.utils.quote(q)
        )
        resp = fetch(url, session)
        if resp is None:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.select('a[href*="/content/$N/"]'):
            href = a.get("href", "")
            if not isinstance(href, str) or "/content/$N/" not in href:
                continue
            if href.startswith("/"):
                href = "https://orzeczenia.ms.gov.pl" + href
            syg = normalize_text(a.get_text(strip=True))[:30] or "?"
            doc_id = "orz_" + re.sub(r"[^A-Za-z0-9]+", "_", href.split("/")[-1])[:60]
            found.setdefault(href, {"url": href, "syg": syg, "id": doc_id})
    LOGGER.info("orzeczenia search discovered %d rulings", len(found))
    return list(found.values())


def scrape_orzeczenie(
    session: requests.Session, spec: dict[str, str]
) -> tuple[str, dict[str, str]] | None:
    """Fetch + parse pojedynczy wyrok. Returns (full_text, metadata) lub None."""
    resp = fetch(spec["url"], session)
    if resp is None:
        return None
    soup = BeautifulSoup(resp.text, "lxml")
    main = soup.select_one(".grid9.simple.single.content")
    if main is None:
        return None
    # Drop sidebar/navigation links and "powołane przepisy" inner link cluster
    # (przepisy referenced as separate metadata, leave w tekście).
    for tag in main.select("nav, .sidebar, script, style"):
        tag.decompose()
    # Detect title (h2 first child).
    h2 = main.find("h2")
    title = ""
    if isinstance(h2, Tag):
        title = normalize_text(h2.get_text(strip=True))
    # Extract data + sąd from title heuristically.
    # Format typowy: "I C 448/20 - wyrok z uzasadnieniem Sąd Rejonowy w Koninie z 2021-09-16"
    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", title)
    court_match = re.search(r"Sąd\s+\w+(?:\s+w\s+\w+)?", title)
    metadata = {
        "sygnatura": spec.get("syg", ""),
        "court": court_match.group(0) if court_match else "",
        "ruling_date": date_match.group(1) if date_match else "",
    }
    body = normalize_text(main.get_text("\n", strip=True))
    return body, metadata


def scrape_orzeczenia(
    session: requests.Session,
    output_dir: Path,
    stats: SourceStats,
    dry_run: bool = False,
    expand_via_search: bool = True,
) -> list[DocumentChunk]:
    """Pobierz pełne wyroki + uzasadnienia z orzeczenia.ms.gov.pl."""
    out_chunks: list[DocumentChunk] = []
    orz_dir = output_dir / "orzeczenia"
    orz_dir.mkdir(parents=True, exist_ok=True)

    catalog = list(ORZECZENIA_URLS)
    if expand_via_search and not dry_run:
        extra = discover_orzeczenia_via_search(
            session, ["konsument rękojmia", "klauzula abuzywna", "niezgodność towaru"]
        )
        existing_urls = {s["url"] for s in catalog}
        catalog.extend(s for s in extra if s["url"] not in existing_urls)

    for spec in catalog:
        stats.attempted_urls += 1
        if dry_run:
            LOGGER.info("[dry] would fetch orzeczenie %s", spec["url"])
            continue
        result = scrape_orzeczenie(session, spec)
        if result is None:
            stats.documents_skipped += 1
            stats.skip_reasons["parse_failed"] = stats.skip_reasons.get("parse_failed", 0) + 1
            continue
        body, ruling_meta = result
        words = count_words(body)
        if words < MIN_DOCUMENT_WORDS:
            stats.documents_skipped += 1
            stats.skip_reasons["too_short"] = stats.skip_reasons.get("too_short", 0) + 1
            continue

        # Pre-split na strukturalne sekcje wyroku (WYROK / UZASADNIENIE /
        # Powołane przepisy / etc.) jeśli wykrywalne. Tekst już znormalizowany
        # (jednoliniowy), więc szukamy po spacjach + dużych literach.
        section_pattern = re.compile(
            r"(?<=\s)(WYROK|UZASADNIENIE|POSTANOWIENIE|"
            r"Powołane\s+przepisy|Orzeczenia\s+podobne|Sygn\.\s*akt)\b",
        )
        headings: list[tuple[str, int]] = []
        for m in section_pattern.finditer(body):
            headings.append((normalize_text(m.group(1)), m.start()))

        sections = chunk_long_text(body, headings=headings or None)
        total = len(sections)
        doc_title = f"{spec.get('syg', '?')} – wyrok"
        for j, (sec_title, sec_body) in enumerate(sections, start=1):
            out_chunks.append(
                DocumentChunk(
                    chunk_id=f"{spec['id']}_chunk_{j:03d}",
                    document_id=spec["id"],
                    document_title=doc_title,
                    document_type="orzeczenie",
                    source="orzeczenia.ms.gov.pl",
                    source_url=spec["url"],
                    chunk_position=j,
                    chunk_total=total,
                    section_heading=sec_title,
                    tresc=sec_body,
                    scrape_date=SCRAPE_DATE,
                    license=LICENSE_URZEDOWE,
                    metadata=dict(ruling_meta) | {"format": "html"},
                )
            )

        meta = DocumentMeta(
            document_id=spec["id"],
            document_title=doc_title,
            document_type="orzeczenie",
            source="orzeczenia.ms.gov.pl",
            source_url=spec["url"],
            total_chunks=total,
            total_words=words,
            license=LICENSE_URZEDOWE,
            scrape_date=SCRAPE_DATE,
            citation_recommendation=(
                f"{ruling_meta.get('court', 'Sąd Powszechny')}. "
                f"Wyrok z dnia {ruling_meta.get('ruling_date', 'n.d.')}, "
                f"sygn. akt {spec.get('syg', '?')}. {spec['url']}"
            ),
            author=ruling_meta.get("court") or "Sąd Powszechny",
        )
        write_meta(orz_dir / f"{spec['id']}.meta.json", meta)

        stats.documents_scraped += 1
        stats.total_chunks += total
        stats.total_words += words
        LOGGER.info(
            "  scraped orzeczenie %s (%s): %d words → %d chunks",
            spec["id"],
            spec.get("syg", ""),
            words,
            total,
        )

    return out_chunks


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


SOURCES = {
    "uokik": scrape_uokik_pdfs,
    "rf": scrape_rf_pdfs,
    "federacja": scrape_federacja,
    "orzeczenia": scrape_orzeczenia,
}

LICENSE_PER_SOURCE = {
    "uokik": LICENSE_URZEDOWE,
    "rf": LICENSE_URZEDOWE,
    "federacja": LICENSE_FAIR_USE,
    "orzeczenia": LICENSE_URZEDOWE,
}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scrape-date", default=SCRAPE_DATE)
    parser.add_argument(
        "--source",
        choices=[*list(SOURCES.keys()), "all"],
        default="all",
        help="Single source or 'all' (default).",
    )
    parser.add_argument(
        "--rf-max-docs", type=int, default=None, help="Cap na liczbę RF PDFs (testing)."
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
        stream=sys.stderr,
    )

    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    session = make_session()
    all_stats: list[SourceStats] = []
    sources_to_run = list(SOURCES.keys()) if args.source == "all" else [args.source]

    for src in sources_to_run:
        stats = SourceStats(source=src, license=LICENSE_PER_SOURCE[src])
        LOGGER.info("=== source: %s ===", src)
        scraper = SOURCES[src]
        try:
            if src == "rf":
                chunks = scraper(  # type: ignore[call-arg]
                    session,
                    output_dir,
                    stats,
                    dry_run=args.dry_run,
                    max_docs=args.rf_max_docs,
                )
            else:
                chunks = scraper(session, output_dir, stats, dry_run=args.dry_run)
        except Exception as exc:
            LOGGER.exception("source %s crashed: %s", src, exc)
            chunks = []

        # Write per-source documents.jsonl.
        src_dir = (
            output_dir
            / {
                "uokik": "uokik_pdfs",
                "rf": "rf_pdfs",
                "federacja": "federacja_konsumentow",
                "orzeczenia": "orzeczenia",
            }[src]
        )
        src_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = src_dir / "documents.jsonl"
        n = write_jsonl(jsonl_path, chunks)
        LOGGER.info("wrote %d chunks to %s", n, jsonl_path)
        all_stats.append(stats)

    # Aggregate summary.
    summary = {
        "scrape_date": args.scrape_date,
        "dry_run": args.dry_run,
        "per_source": [asdict(s) for s in all_stats],
        "totals": {
            "documents_scraped": sum(s.documents_scraped for s in all_stats),
            "documents_skipped": sum(s.documents_skipped for s in all_stats),
            "total_chunks": sum(s.total_chunks for s in all_stats),
            "total_words": sum(s.total_words for s in all_stats),
        },
    }
    summary_path = output_dir / "scrape_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    LOGGER.info("=== DONE ===  totals: %s", summary["totals"])
    LOGGER.info("summary at %s", summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
