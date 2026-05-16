# Consumer documents 2026-05-16 — pełne dokumenty long-form

Output `scrape_consumer_docs.py` (agent E2, 2026-05-16). Komplementarny do:

- `data/raw/uokik_qa_2026-05-16/` (Q&A pairs, agent E1)
- `data/raw/consumer_questions_polish_2026-05-16/` (forum/Reddit questions)
- `data/raw/extended_consumer_2026-05-16/` (Wikipedia sections)
- `data/raw/eli_ustawy_konsumenckie_2026-05-16/` (ELI ustawy chunks)

## Cel
Knowledge-base extension dla polskiego consumer-rights RAG przez **dodanie
long-form documents** (poradniki PDF, raporty, pełne wyroki sądowe, długie
artykuły edukacyjne). Każdy dokument ≥350 słów (filter), typowy chunk
500-1800 znaków.

## Wyniki agregat

| Source | Docs | Chunks | Words | License |
|---|---|---|---|---|
| `uokik.gov.pl` (PDFs) | 8 | 202 | 36,085 | urzędowe (Art. 4 ust. 2 PrAut) |
| `rf.gov.pl` (PDFs analizy/raporty/poradniki) | 36 | 2,105 | 422,731 | urzędowe (Art. 4 ust. 2 PrAut) |
| `federacja-konsumentow.org.pl` (PDF + HTML) | 5 | 70 | 11,557 | fair-use Art. 29 PrAut |
| `orzeczenia.ms.gov.pl` (wyroki + uzasadnienia) | 10 | 191 | 44,744 | urzędowe (Art. 4 ust. 2 PrAut) |
| **Total** | **59** | **2,568** | **515,117** | mixed |

**Knowledge-base growth:** 2,183 → 4,751 chunks (**2.18× growth**).

## Struktura katalogów

```
consumer_documents_2026-05-16/
├── README.md                       (this file)
├── scrape_summary.json             (agregat statystyk)
├── uokik_pdfs/
│   ├── documents.jsonl             (202 chunks)
│   └── <doc_id>.meta.json          (8 sidecar meta)
├── rf_pdfs/
│   ├── documents.jsonl             (2105 chunks)
│   └── <doc_id>.meta.json          (36)
├── federacja_konsumentow/
│   ├── documents.jsonl             (70 chunks)
│   └── <doc_id>.meta.json          (5)
└── orzeczenia/
    ├── documents.jsonl             (191 chunks)
    └── <doc_id>.meta.json          (10)
```

## Schema JSONL (per chunk)

```json
{
  "chunk_id": "rf_pdf_<slug>_chunk_003",
  "document_id": "rf_pdf_<slug>",
  "document_title": "AI w finansach. Zastosowanie i ryzyko...",
  "document_type": "poradnik" | "raport" | "artykul" | "orzeczenie" | "broszura",
  "source": "rf.gov.pl",
  "source_url": "https://...",
  "chunk_position": 3,
  "chunk_total": 55,
  "section_heading": "Korzyści i zagrożenia",
  "tresc": "...",                  // NFC normalized
  "scrape_date": "2026-05-16",
  "license": "urzędowe (Art. 4 ust. 2 PrAut)",
  "metadata": {
    "format": "pdf",
    "publication_year": 2025,
    "sygnatura": "I C 448/20"       // only for orzeczenia
  }
}
```

Plus per-document `<doc_id>.meta.json` z `total_chunks`, `total_words`,
`citation_recommendation` (dla R3 thesis), author, publication_year.

## License rationale

**urzędowe (Art. 4 ust. 2 ustawy o prawie autorskim DU/1994/83):**
Materiały urzędowe (publikacje agencji państwowej — UOKiK, RF; orzeczenia
sądowe) NIE są przedmiotem prawa autorskiego.

**fair-use Art. 29 PrAut (Federacja Konsumentów):**
NGO, formalnie © FK; używane na podstawie prawa cytatu w celach naukowych
do pracy inżynierskiej. Attribution zachowany w `metadata.citation_recommendation`.

## Section heading coverage (jakość parsing)

| Source | Chunks with `section_heading` |
|---|---|
| orzeczenia (WYROK/UZASADNIENIE/Sygn.) | 100% (191/191) |
| uokik_pdfs (numerowane sekcje) | 96% (193/202) |
| rf_pdfs (mix sections + headers) | 88% (1857/2105) |
| federacja_konsumentow | 79% (55/70) |

## Re-run / partial scrape

```bash
# Wszystkie sources
uv run python -m src.scrape.documents.scrape_consumer_docs \
    --output ../main_project/data/raw/consumer_documents_2026-05-16

# Pojedynczy source
uv run python -m src.scrape.documents.scrape_consumer_docs \
    --output ../main_project/data/raw/consumer_documents_2026-05-16 \
    --source rf  # | uokik | federacja | orzeczenia

# Dry-run (bez fetcha)
uv run python -m src.scrape.documents.scrape_consumer_docs \
    --output ../main_project/data/raw/consumer_documents_2026-05-16 --dry-run

# RF cap (testing, default 36)
uv run python -m src.scrape.documents.scrape_consumer_docs \
    --output ../main_project/data/raw/consumer_documents_2026-05-16 \
    --source rf --rf-max-docs 5
```

## Sources NIE scraped (i dlaczego)

- **Wikipedia consumer law** — już w `extended_consumer_2026-05-16/` (Agent
  poprzedni). Nie duplikuję.
- **Gazeta Prawna / Infor.pl** — paywall + niski signal-to-noise dla expert
  legal reasoning. Fair-use ryzyko bez clear case.
- **Allegro / OLX guides** — commercial perspective; brak strukturalnego
  legal reasoning. Skip.
- **Bank consumer guides** — głównie product marketing; niski signal-to-noise.
- **prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/** — Q&A, robi to E1.
- **orzeczenia.ms.gov.pl /search/szukaj** — stateful Tapestry form, ICR
  search endpoint nie wspiera prostego GET. Hand-curated 10 wyroków wystarczy
  jako proof of concept; expansion via Selenium/Playwright zostawione na
  Iter. 1 jeśli potrzeba.

## Known gotchas

1. **PDF letter-spacing artifacts:** niektóre UOKiK poradniki używają wide
   letter-spacing dla efektu graficznego — pdfplumber rozdziela na "T y "
   zamiast "Ty". Workaround: post-process w embedding stage albo dropować
   chunki z >10% single-char tokens.

2. **RF "DKN_Raport_nieprawidlowosci_wrzesien2019":** 167k słów, 786 chunks.
   Jeden dokument generuje 37% wszystkich RF chunks. Może wymagać dedupe
   /downsampling w Iter. 1 jeśli embedding kosztuje za dużo.

3. **Orzeczenia.ms.gov.pl search** wymaga form state (Apache Tapestry).
   Discovery via search nie działa z prostym requests. Hand-curated 10
   wyroków discovered via Google search `site:orzeczenia.ms.gov.pl`.

4. **Federacja Konsumentów HTML article `swiadomy_konsument_n1532`**: 103
   słowa (poniżej MIN_DOCUMENT_WORDS=350) — to landing page do PDF, nie
   long-form article. Skipped automatycznie.

5. **PDF heading detection** używa heurystyki UPPER + sekcja-style; może
   złapać false positives (np. "Strona", "RF DLA POSZKODOWANYCH:" jako
   headers — częściowo odfiltrowane przez `NOISE_HEADING_RE`).

## Citation hygiene dla R3

Każdy `<doc_id>.meta.json` ma `citation_recommendation` w formacie:

- UOKiK: `UOKiK (2025). Tytuł poradnika. Urząd Ochrony Konkurencji i Konsumentów. <url>`
- RF:    `Rzecznik Finansowy. Tytuł raportu. <url>`
- Orz:   `<Sąd>. Wyrok z dnia <data>, sygn. akt <syg>. <url>`
- FK:    `Federacja Konsumentów (<rok>). Tytuł. <url>`

Polecam dodać `sources_catalog.md` extension dla R3 z per-source coverage.
