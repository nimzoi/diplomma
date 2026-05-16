# `src/scrape/documents/` — long-form consumer documents scraper

## What

Scraper pełnych dokumentów polskiej ochrony konsumenta. Komplementarny do
istniejących `src/scrape/uokik/` (Q&A) i `src/scrape/legal_fora/` (forum
questions) — ten moduł zbiera EXCLUSIVELY long-form documents (>350 słów):

| Source | Type | Count |
|---|---|---|
| `uokik.gov.pl/Download/N` | poradniki + broszury PDF | 8 docs |
| `rf.gov.pl/edukacja/baza-wiedzy/` | analizy + raporty + poradniki PDF | 36 docs |
| `federacja-konsumentow.org.pl` | PDF + HTML artykuły | 5 docs |
| `orzeczenia.ms.gov.pl/content/$N/` | wyroki + uzasadnienia | 10 docs |

Output: 59 docs / 2,568 chunks / 515k słów (knowledge base 2,183 → 4,751,
2.18× growth).

## Files

- `scrape_consumer_docs.py` — main scraper (single file, 4 per-source adapter
  functions + chunking utilities). Entry: `main()` → CLI.
- `__init__.py` — package marker.

## Run

```bash
# Wszystkie sources, default output dir
uv run python -m src.scrape.documents.scrape_consumer_docs \
    --output ../main_project/data/raw/consumer_documents_2026-05-16

# Pojedynczy source (testing)
uv run python -m src.scrape.documents.scrape_consumer_docs \
    --output /tmp/test --source uokik

# Dry-run
uv run python -m src.scrape.documents.scrape_consumer_docs \
    --output /tmp/test --dry-run
```

## Dependencies

Wszystkie z `pyproject.toml`:

- `requests` — HTTP fetching
- `beautifulsoup4 + lxml` — HTML parsing
- `pdfplumber` — PDF text extraction

NIE wymaga nowych deps.

## Architecture

```
make_session()                       # User-Agent + Accept-Language
  └→ scrape_uokik_pdfs()             # hand-curated 11 PDF URLs
  └→ scrape_rf_pdfs()                # auto-discover via /baza-wiedzy/
       └→ scrape_rf_index()
  └→ scrape_federacja()              # 3 PDFs + 3 HTML articles
       └→ scrape_federacja_html()
  └→ scrape_orzeczenia()             # 10 hand-curated wyroki + search fallback
       └→ scrape_orzeczenie()
       └→ discover_orzeczenia_via_search()  # GET search (Tapestry, often empty)

extract_pdf_text(pdf_bytes) → (full_text, headings)   # heuristic heading detect
chunk_long_text(text, headings) → list[(section, body)]  # MAX_CHUNK_CHARS=1800
DocumentChunk dataclass → JSONL serialization
DocumentMeta dataclass   → per-doc sidecar
```

## Skip rules

Document skipped jeśli:
- Fetch fails (network/HTTP error)
- Not a PDF when expected (`content-type` check + magic bytes `%PDF`)
- `< MIN_DOCUMENT_WORDS = 350` (too short = faux long-form, e.g., landing page)
- Parse failure (pdfplumber raises wide exception variety)

Skip stats kept w `SourceStats.skip_reasons`, dumped do `scrape_summary.json`.

## Schema extension proposal (for `src/halu/schemas.py`)

Obecne `LegalChunk` jest specyficzny dla ELI ustaw (`ustawa_id`, `art`, etc.).
Dla long-form documents trzeba osobnego schema:

```python
class ConsumerDocumentChunk(BaseModel):
    """Long-form consumer document chunk (poradnik/raport/wyrok/artykul)."""

    model_config = ConfigDict(strict=True, frozen=True)

    chunk_id: str
    document_id: str
    document_title: str
    document_type: Literal["poradnik", "raport", "artykul", "orzeczenie", "broszura"]
    source: str       # domain
    source_url: str
    chunk_position: int = Field(..., ge=1)
    chunk_total: int = Field(..., ge=1)
    section_heading: str | None
    tresc: str = Field(..., min_length=200)
    scrape_date: date
    license: str
    metadata: dict[str, Any] = Field(default_factory=dict)
```

Validation logic identyczna jak `LegalChunk.validate_nfc`. Do dodania w
Iter. 1 razem z `dataset_builder.py` adapterem na embedder.

## Limitations / future work

1. **Orzeczenia.ms.gov.pl search** wymaga Apache Tapestry form state.
   Hand-curated 10 wyroków = proof of concept. Full automation
   → Selenium/Playwright w Iter. 1 jeśli potrzeba więcej.

2. **PDF heading heuristic** false positives (np. "Strona N", page footers).
   Częściowo odfiltrowane przez `NOISE_HEADING_RE`; może wymagać
   ulepszenia w Iter. 1.

3. **One giant RF report** (DKN nieprawidłowości, 167k słów, 786 chunks)
   dominuje korpus. Consider downsample lub stratified sample przed
   embedding w Iter. 1.

4. **Federacja Konsumentów `infoteka.*` domain** ma TLS cert mismatch
   (`ERR_TLS_CERT_ALTNAME_INVALID`); skipped. Może wymagać `verify=False`
   jeśli chcemy pokrycia.

## Quality samples

Spr `data/raw/consumer_documents_2026-05-16/README.md` dla per-source quality
breakdown + section heading coverage stats.
