# Pełne dokumenty consumer rights polish — scrape 2026-05-16 (Agent E2)

## Verdict

- **Total nowych chunks: 2,568** (z 4 source'ów, all long-form)
- **Total nowych dokumentów: 59**
- **Knowledge-base growth: 2,183 → 4,751 chunks (2.18× growth)**
  - baseline: 2,123 ELI ustawy + 60 UOKiK Q&A = 2,183
  - nowe: +2,568 long-form chunks (515k słów)
- **Top 3 sources by quality:**
  1. **orzeczenia.ms.gov.pl** (10 wyroków, 191 chunks, 44k słów) —
     real legal reasoning, 100% section heading coverage, sygnatura preserved
  2. **rf.gov.pl** (36 PDFs analiz/raportów, 2,105 chunks, 422k słów) —
     największa skala, legal opinions z TSUE orzecznictwem, akty Sądu Najwyższego
  3. **uokik.gov.pl** (8 PDFs poradników/broszur, 202 chunks, 36k słów) —
     consumer-facing educational, 96% section heading coverage

## Per source

| # | Source | Docs | Chunks | Words | License | Format | Quality |
|---|---|---|---|---|---|---|---|
| 1 | `orzeczenia.ms.gov.pl` (wyroki + uzasadnienia) | 10 | 191 | 44,744 | urzędowe Art. 4 ust. 2 PrAut | HTML strukturalne | ★★★★★ legal reasoning, sygn + court + data preserved |
| 2 | `rf.gov.pl` (analizy + raporty + poradniki) | 36 | 2,105 | 422,731 | urzędowe Art. 4 ust. 2 PrAut | PDF | ★★★★★ — TSUE orzecznictwo, frankowe, AI, OC, uchwały SN |
| 3 | `uokik.gov.pl` (poradniki PDF) | 8 | 202 | 36,085 | urzędowe Art. 4 ust. 2 PrAut | PDF | ★★★★ — consumer-facing, dobre section structure |
| 4 | `federacja-konsumentow.org.pl` | 5 | 70 | 11,557 | fair-use Art. 29 PrAut | PDF + HTML | ★★★ — NGO, consumer ABC, dane osobowe |

**Section heading coverage** (jakość parsingu):
- orzeczenia: 100% (WYROK / UZASADNIENIE / Sygn. akt detected)
- uokik PDFs: 96%
- rf PDFs: 88%
- federacja: 79%

**Skip stats** (filtered out poniżej `MIN_DOCUMENT_WORDS = 350`):
- UOKiK: 3/11 skipped (Download/958 pomoc-ulotka 154w; /653 badanie 226w; /1203 plac zabaw 321w — to ulotki, nie poradniki)
- Federacja: 1/6 skipped (HTML `swiadomy_konsument_n1532` 103w — landing page do PDF)
- RF / orzeczenia: 0 skipped

## Schema extension (recommendation dla `src/halu/schemas.py`)

Obecne `LegalChunk` w schemas.py jest specyficzny dla ELI ustaw (`ustawa_id`,
`art`, `paragraf`, etc.). Dla long-form documents potrzebny osobny schema:

```python
class ConsumerDocumentChunk(BaseModel):
    """Long-form consumer document chunk (poradnik/raport/wyrok/artykul)."""

    model_config = ConfigDict(strict=True, frozen=True)

    chunk_id: str
    document_id: str
    document_title: str
    document_type: Literal["poradnik", "raport", "artykul", "orzeczenie", "broszura"]
    source: str
    source_url: str
    chunk_position: int = Field(..., ge=1)
    chunk_total: int = Field(..., ge=1)
    section_heading: str | None
    tresc: str = Field(..., min_length=200)
    scrape_date: date
    license: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    # Validation: validate_nfc identical do LegalChunk
```

Alternatywnie: extend `LegalChunk` o opcjonalne pola `document_type`,
`section_heading`, czyniąc `ustawa_id`/`art` opcjonalne — ale to psuje
existing ELI usage. Lepiej osobny schema z shared validator helper.

## Recommendation dla Iter. 1

**Primary KB stratification** (proponowany retrieval split):

| Strata | Source | ~chunks | Use case |
|---|---|---|---|
| **Statutes** (atomic) | `eli_ustawy_konsumenckie_2026-05-16/` | 2,123 | Ground truth for `Podstawa prawna:` citations |
| **Expert Q&A** | `uokik_qa_2026-05-16/` (E1) + nowe Q&A z E1 | 60+? | Gold answers z explicit citations |
| **Court precedents** | `consumer_documents_2026-05-16/orzeczenia/` | 191 | Case-based reasoning |
| **Educational poradniki** | `uokik_pdfs/` + `federacja_konsumentow/` | 272 | Lay-friendly explanations |
| **Legal analyses** | `rf_pdfs/` | 2,105 | Expert opinions, TSUE precedents |
| **Encyclopedic** | `extended_consumer_2026-05-16/` (Wikipedia) | 31 | Generic background |
| **Real queries** | `consumer_questions_polish_2026-05-16/` | 2,967 | Query distribution (test, not corpus) |

**Embedding cost estimate** (BGE-M3, ~512 tokens/chunk, ~1024-dim):
- New 2,568 chunks × ~512 tokens = ~1.3M tokens to embed
- BGE-M3 inference @ ~100 docs/s on RTX 3090 → ~25 s wallclock
- Disk: ~10 MB float32 vectors → negligible
- Qdrant collection growth: 2,183 → 4,751 vectors → ~20 MB

**Concerning dominance:** `rf_pdf_DKN_raport_nieprawidlowosci_2019` jeden
dokument ma 786 chunks (37% wszystkich RF chunks). Recommend
**downsample** w embedding stage do max 100 chunks per dokument lub
**stratified sample** by document_id przed eval split — w przeciwnym razie
ten jeden raport zdominuje retrieval similarity scores.

**Secondary / supplementary** (lower priority dla iter. 1):
- Federacja Konsumentów HTML articles (tylko 70 chunks; consider łączenie z FK PDFs)
- UOKiK Q&A (już mała baseline 60 par; może warta expansion w E1)

## Gotchas

1. **PDF letter-spacing artifacts** w UOKiK poradnikach (np. "T y t r ó j a" zamiast "Ty trójka")
   — graficzny effect dla branding, pdfplumber rozdziela. Workaround: post-process
   regex `re.sub(r'\\b(\\w)\\s(\\w)\\s(\\w)\\b', ...)` przed embedding, albo dropować
   chunki z >10% single-char tokens.

2. **One giant document dominates RF** (DKN nieprawidłowości 167k słów).
   Stratified downsample przed split eval/train.

3. **Orzeczenia search NOT working** via simple GET (Apache Tapestry form state).
   Hand-curated 10 wyroków jako MVP. Expansion plan: Selenium/Playwright session
   replay lub direct cooperation z Ministerstwem Sprawiedliwości dla bulk export
   (jeśli dostępny).

4. **License: Federacja Konsumentów = fair-use Art. 29** — nie public-domain.
   Attribution preserved w `citation_recommendation`. NIE udostępniać poza
   pracą inżynierską.

5. **Domain shift risk:** RF (Rzecznik Finansowy) ma ~60% materiałów
   ubezpieczeniowych + ~30% bankowych + ~10% pure consumer. To insurance/banking
   tilt w korpusie — może wpłynąć na retrieval dla pure consumer queries
   (zwrot, reklamacja, rękojmia). Consider per-doc-type filtering w retrieval.

## Diff vs. existing scrapers

- **E1 (agent paralelny)** — Q&A pairs z UOKiK FAQ, prawakonsumenta.uokik
  pytania-i-odpowiedzi. Format: short Q + A z explicit citation.
- **E2 (this)** — long-form documents only. Skip if <350 słów.
  Format: chunked sections per dokument.

Brak overlap — E1 i E2 mają disjoint document sets (E1 zbiera tylko `/pytania-i-odpowiedzi/`,
E2 zbiera `/publikacje/`, `/materialy-do-pobrania/`, RF, orzeczenia, FK).

Wikipedia consumer law (`extended_consumer_2026-05-16/`) była scraped przez
**poprzednia iteracja** (`scrape/extended/`). NIE re-scraped tutaj.

## Output

- Script: `D:\diplomma\main_project\src\scrape\documents\scrape_consumer_docs.py` (~700 LOC)
- Data: `D:\diplomma\main_project\data\raw\consumer_documents_2026-05-16\`
  - `uokik_pdfs/documents.jsonl` (202 chunks) + 8 `<doc_id>.meta.json`
  - `rf_pdfs/documents.jsonl` (2,105 chunks) + 36 `<doc_id>.meta.json`
  - `federacja_konsumentow/documents.jsonl` (70 chunks) + 5 `<doc_id>.meta.json`
  - `orzeczenia/documents.jsonl` (191 chunks) + 10 `<doc_id>.meta.json`
  - `scrape_summary.json` (aggregate)
  - `README.md`

## Reproducibility

```bash
cd D:\diplomma\main_project
uv run python -m src.scrape.documents.scrape_consumer_docs \
    --output ../main_project/data/raw/consumer_documents_2026-05-16
# ~16 min wallclock (rate-limited 1 req/sec; 60 docs × ~3 sec PDF parse)
```

Hand-curated URLs (UOKiK 11 PDFs + orzeczenia 10 wyroków + FK 6 items)
embedded w `scrape_consumer_docs.py` jako module-level constants.
RF auto-discovers PDFs z `/baza-wiedzy/analizy-i-raporty/` + `/poradniki/`.

## Dependencies

Wszystkie z `pyproject.toml` (NIE dodawane nowe):
- `requests` 2.34+
- `beautifulsoup4` 4.14+ + `lxml` 6.1+
- `pdfplumber` 0.11.9
