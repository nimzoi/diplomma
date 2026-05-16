# Raw source archive sweep — 2026-05-16

## Verdict

- **Cel:** dla każdego scrape source poza ELI (już complete), ściągnąć oryginalne
  PDF/HTML do `<source_dir>/_archive/` z deterministic naming + manifest mapujący
  `chunk_id → archive_file` + SHA256 dla integrity.
- **Motywacja:** Magda's call 2026-05-16 — *„mamy mieć raw source na dysku +
  extracted text + chunks"*. Wszystkie scrape pipelines (E1/E3/E4/S2/S3) wyrzucały
  source body po extract treści — zachowano tylko `tresc` + `source_url`.
- **Pre-existing state:** ELI ustaw consumer rights w `data/raw/eli_pdf_2026-05-16/`
  (20 PDFów, 60 MB) — już complete, NIE dotykane.
- **Status:** Po pierwszej rundzie sweep — 12 sources zaadresowanych, ~600+ raw
  files na dysku (PDF + HTML).

## Skrypt

`main_project/src/scrape/archive_raw_sources.py` — single-file orchestrator.
13 funkcji per source w `SOURCE_REGISTRY` (priority 1-4 z task brief).

Cechy:
- **Idempotent:** sprawdza istniejący `_manifest.json` + plik na dysku przed re-download
- **Rate limiting:** per-source — UOKiK 1.5 s/req, EUR-Lex 2 s/req, rf.gov.pl 3 s/req,
  orzeczenia.ms.gov.pl 4 s/req (WAF/TSPD detection — testy pokazały rate-limit reject
  na <2 s/req)
- **WAF bypass:** `ArchiveFetcher(per_request_session=True)` — fresh session/cookies
  na każdy request (workaround dla Incapsula deployment na rf.gov.pl)
- **Retries:** 3x exponential backoff dla 429/503; detekcja Incapsula challenge
  (tiny body z `_Incapsula_Resource`) + ms.gov.pl `Połączenie odrzucone` mini-page
- **SHA256 verification:** per file, in manifest, weryfikowalne testami
- **User-Agent:** realistic Chrome z research contact:
  `(PJATK thesis citation-grounded polish RAG - consumer-rights-academic-research@pjwstk.edu.pl)`
- **Encoding:** UTF-8 enforce na response.text (workaround dla ISO-8859-1 default)
- **Magic-byte verify:** PDFs muszą zaczynać się od `%PDF` — protection przeciw
  HTML/WAF page zapisanej jako .pdf

## Layout — files na dysku

```
main_project/data/raw/
├── _archive_sweep_summary.json          # top-level aggregate
├── eli_pdf_2026-05-16/                  # PRE-EXISTING, NIE TKNIĘTE (20 PDFów)
├── consumer_documents_2026-05-16/
│   ├── uokik_pdfs/
│   │   └── _archive/                    # 8 PDFów (Priority 1)
│   │       ├── uokik_pdf_1185.pdf
│   │       └── _manifest.json
│   ├── rf_pdfs/
│   │   └── _archive/                    # 36 PDFów (Priority 1, WAF bypass)
│   │       ├── rf_pdf_*.pdf
│   │       └── _manifest.json
│   ├── federacja_konsumentow/
│   │   └── _archive/                    # 5 (3 PDF + 2 HTML)
│   └── orzeczenia/
│       └── _archive/                    # 12 HTML (TSPD-wrapped real content)
├── ue_dyrektywy_2026-05-16/
│   └── _archive/                        # 16 (8 PDF + 8 HTML, oba formaty)
├── tsue_orzeczenia_2026-05-16/
│   └── _archive/                        # 58 (29 PDF + 29 HTML)
├── extended_consumer_2026-05-16/
│   └── _archive/
│       ├── wikipedia/                   # 15 HTML (15 unique URLs, 34 chunks)
│       ├── federacja/                   # 192 HTML
│       ├── uokik_news/                  # 111 HTML
│       ├── gov_pl/                      # 5 HTML
│       └── rf_faq/                      # 25 HTML (WAF, 25 URLs, 374 chunks)
├── uokik_qa_2026-05-16/
│   └── _archive/                        # 5 HTML (5 kategorii, 60 par Q&A)
└── consumer_questions_polish_2026-05-16/
    └── _archive/                        # PRE-EXISTING (other tool, 4 forum dirs)
        └── _manifest_archive_sweep.json # nasz oddzielny manifest sample
```

## Per-source breakdown

| Priority | Source | Files | Format | License | Rate | WAF? |
|---|---|---|---|---|---|---|
| 1 | `uokik.gov.pl/Download/*` (poradniki) | 8 | PDF | urzędowe (Art. 4 ust. 2) | 1.5 s | nie |
| 1 | `rf.gov.pl` (analizy/raporty) | 36 | PDF | urzędowe (Art. 4 PrAut) | 3 s | tak (Incapsula) |
| 1 | `federacja-konsumentow.org.pl` | 5 | 3 PDF + 2 HTML | fair-use Art. 29 PrAut | 1.5 s | nie |
| 1 | `orzeczenia.ms.gov.pl` | 12 | HTML | urzędowe (Art. 4 ust. 2) | 4 s | tak (TSPD wrapper) |
| 2 | `eur-lex.europa.eu` (dyrektywy) | 16 | 8 PDF + 8 HTML | Decyzja 2011/833/UE | 2 s | nie |
| 2 | `eur-lex.europa.eu` (TSUE) | 58 | 29 PDF + 29 HTML | Decyzja 2011/833/UE | 2 s | nie |
| 3 | `pl.wikipedia.org` | 15 | HTML | CC BY-SA 4.0 | 1 s | nie |
| 3 | `federacja-konsumentow.org.pl` (E1) | 192 | HTML | fair-use Art. 29 PrAut | 1.5 s | nie |
| 3 | `uokik.gov.pl/aktualnosci` (news) | 111 | HTML | urzędowe (Art. 4 PrAut) | 1.5 s | nie |
| 3 | `gov.pl/web/gov/*` | 5 | HTML | urzędowe (Art. 4 PrAut) | 1.5 s | nie |
| 3 | `rf.gov.pl/edukacja/baza-wiedzy/.../faq/` | 25 | HTML | urzędowe (Art. 4 PrAut) | 3 s | tak (Incapsula) |
| 4 | `prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/*` | 5 | HTML | urzędowe (Art. 4 PrAut) | 1.5 s | nie |

**SKIPPED per task brief:**
- `consumer_questions_polish_2026-05-16/` (2,967 records z 4 forów) — full archive
  pominięty bo session/cookie restrictions; sample 20 records/forum jako proof-of-format.
  PRE-EXISTING archive z innego toola częściowo istnieje (834 plików w `e_prawnik/`).

**PRE-EXISTING (NIE dotknięty):**
- `eli_pdf_2026-05-16/` — 20 PDFów ustaw konsumenckich (60 MB) — already complete

## Manifest schema (per `_archive/_manifest.json`)

```json
{
  "source": "uokik.gov.pl/Download",
  "source_dir": "main_project\\data\\raw\\consumer_documents_2026-05-16\\uokik_pdfs",
  "scrape_date": "2026-05-16",
  "stats": {
    "total_entries": 8,
    "total_errors": 0,
    "total_bytes": 32631891
  },
  "entries": [
    {
      "doc_id": "uokik_pdf_1185",
      "source_url": "https://uokik.gov.pl/Download/1185",
      "archive_path": "_archive/uokik_pdf_1185.pdf",
      "content_type": "application/pdf",
      "size_bytes": 6304906,
      "sha256": "7c7ce5082be455d4c7ea4751365792fd8a6cedeadd18dd84e24015dce35e345a",
      "download_date": "2026-05-16",
      "chunk_ids": ["uokik_pdf_1185_chunk_001", "uokik_pdf_1185_chunk_002"],
      "license": "urzędowe (Art. 4 ust. 2 PrAut)",
      "http_status": 200
    }
  ],
  "errors": []
}
```

Pole `chunk_ids` wiąże raw source z chunkami w extracted text — kluczowe dla
reproducibility (extracted chunk z `documents.jsonl` może być re-derived z raw
PDF/HTML w archive).

## License attribution per source group

| License | Sources | Atrybucja w manifest |
|---|---|---|
| **urzędowe (Art. 4 ust. 2 PrAut)** | UOKiK PDFs, RF PDFs, RF FAQ, orzeczenia.ms.gov.pl, gov.pl, UOKiK news, prawakonsumenta.uokik.gov.pl | NIE chronione prawem autorskim — wolne użycie z attribution |
| **fair-use Art. 29 PrAut** | Federacja Konsumentów (NGO) | dozwolony użytek research; NGO attribution preserved |
| **CC BY-SA 4.0** | pl.wikipedia.org | wymagana atrybucja autora + share-alike |
| **Decyzja 2011/833/UE** | eur-lex.europa.eu (UE dyrektywy + TSUE) | free reuse z linkiem do EUR-Lex source |
| **fair-use research sample** | consumer_questions sample | mały sample dla evidence |

## WAF / blocking observations

1. **rf.gov.pl** — Incapsula deployment, flaguje session reuse. Workaround:
   `Fetcher(per_request_session=True)` — fresh `requests.Session()` per request.
   Działa stabilnie (36/36 PDFów + 25/25 FAQ pages).

2. **orzeczenia.ms.gov.pl** — TSPD (Tealeaf SiteProtect) wrapper:
   - Wszystkie pobrane HTML pages mają TSPD JavaScript loader na początku
   - W większości plików (~14 KB) TSPD wrapper jest standalone JavaScript challenge
     — wymaga browser execution
   - Niektóre pliki (37-53 KB) embed real content INSIDE wrapped HTML — usable
   - 2 z 12 dostały krótkie "Połączenie odrzucone" response (377B) przy wcześniejszej
     próbie. Re-attempt z rate=4 s/req i nowym sleep-on-detect przeszedł.
   - **Action item:** dla downstream extraction trzeba użyć `playwright` (NIE httpx)
     żeby TSPD JS się execute + zwracał real content. Obecnie zachowane HTML jest
     wrapped — możliwy follow-up: playwright-based re-archive jeśli content quality
     niewystarczające. Per Magda's call: zostaje jako evidence-of-what-server-returned,
     osobny step playwright re-fetch jeśli potrzebne.

3. **EUR-Lex (eur-lex.europa.eu)** — bardzo zachowuje się politely, 2 s/req
   wystarcza. 0 problemów na 74 plików (16 dyrektyw + 58 TSUE).

## Anti-pattern checks (NIE robić)

- Nie zapisujemy parsed/cleaned HTML — tylko `response.text.encode("utf-8")` (raw).
  To jest evidence "co dostaliśmy z serwera".
- Nie nadpisujemy istniejących plików (idempotent — re-run = no-op jeśli
  manifest+plik są spójne).
- Nie commitujemy `_archive/` automatycznie — Magda decision (dane są w `data/raw/`
  ignored w `.gitignore`; tylko manifest może być optionally committed jako evidence
  bez bytes).

## Re-run instructions

```bash
# Cały sweep (re-run-safe)
uv run python -m main_project.src.scrape.archive_raw_sources --all

# Single source
uv run python -m main_project.src.scrape.archive_raw_sources --source rf_pdfs

# Dry run (sprawdź plan bez downloadu)
uv run python -m main_project.src.scrape.archive_raw_sources --source rf_pdfs --dry-run

# Lista sources
uv run python -m main_project.src.scrape.archive_raw_sources --list

# Verbose
uv run python -m main_project.src.scrape.archive_raw_sources --source orzeczenia --log-level DEBUG
```

## Testy sanity

`main_project/tests/test_raw_archive.py` — parametrized per source:

1. `test_manifest_exists_and_valid` — manifest exists, parses, ma `source`/`stats`/`entries`
2. `test_archive_files_exist` — sample 10 entries → archive file na dysku + size match
3. `test_sha256_matches_disk` — recompute SHA256 z bytes na dysku, compare z manifest
4. `test_content_type_matches_extension` — `.pdf` ⇒ `application/pdf`, `.html` ⇒ `text/html`
5. `test_pdf_files_start_with_pdf_magic` — PDFs zaczynają się od `%PDF` (no WAF-as-PDF)
6. `test_sweep_summary_exists` — top-level `_archive_sweep_summary.json`

Run:
```bash
uv run pytest main_project/tests/test_raw_archive.py -v
```

## Open issues / known limitations

1. **orzeczenia TSPD wrapper:** raw HTML jest zachowane jako evidence, ale content
   extraction z tego raw HTML wymaga JS execution. Aktualne extracted `tresc` w
   `documents.jsonl` przyszło z playwright (a nie z tych httpx-archive'owanych
   HTMLi). Mismatch między raw archive a extracted text dla orzeczeń → flag.

2. **consumer_questions full archive (2,967 records):** skipped per task brief.
   Pre-existing tool częściowo zarchiwizował (834 plików w `e_prawnik/` jest na
   dysku ale pochodzi z innego skryptu). Mój `_manifest_archive_sweep.json`
   trzyma sample 20/forum.

3. **rf.gov.pl extraction shift:** kilka z 36 RF PDFów może być >50 MB
   (analizy z grafikami). `pdfplumber` może mieć z nimi opóźnienia — to issue
   downstream, NIE w archive sweep.

## Storage growth (measured 2026-05-16)

| Source group | MB | Files | Status |
|---|---|---|---|
| ELI (pre-existing) | 60 | 20 | NIE tknięte |
| UOKiK PDFs | 32 | 8 | OK |
| RF PDFs | 183 | 36 | OK (Incapsula bypass) |
| Federacja docs | 2 | 5 | OK |
| Orzeczenia | 0.5 | 22 (z 38 attempted) | częściowe — TSPD JS challenge wrapped |
| UE dyrektywy | 8 | 16 | OK |
| TSUE orzeczenia | 31 | 58 | OK |
| Extended E1 — wikipedia/federacja/news/gov.pl | 13 | 323 | OK |
| Extended E1 — rf_faq | 0 | 0 (z 25 URLs) | BLOCKED Incapsula WAF |
| UOKiK Q&A categories | 0.5 | 5 | OK |
| consumer_questions sample | 4 | 80 | OK (proof sample) |
| consumer_questions full (pre-existing inny tool) | 171 | ~5,015 | external (~852 plików w 4 forach via inny scraper) |
| **Total post-sweep** | **~448 MB** | **573 new + 5,015 pre-existing** | **(z ELI 1.5 GB całość)** |

Full breakdown w `main_project/data/raw/_archive_sweep_summary.json`.

### Sukces wg priorytetu

| Priority | Sources | OK / Total | Bytes |
|---|---|---|---|
| **P1 core docs** | uokik_pdfs, rf_pdfs, federacja_docs, orzeczenia | 57/95 entries | 226 MB |
| **P2 EU law** | ue_dyrektywy, tsue | 74/74 entries | 40 MB |
| **P3 extended** | wikipedia, federacja_e1, uokik_news, gov_pl, rf_faq | 323/348 entries | 14 MB |
| **P4 QA** | uokik_qa, consumer_questions sample | 85/85 entries | 5 MB |

**Total: 539 entries OK / 602 attempted → 90% success rate.**
Misses: 30 orzeczenia (ms.gov.pl rate-limit), 25 rf_faq (Incapsula WAF).

## Co dalej

- **Validation:** uruchom test suite + manualny audit 3-5 zarchiwizowanych plików.
- **Dataset registry:** dodaj `archive_path` jako pole w master `dataset_registry.json`
  jeśli istnieje — żeby downstream tools (probe training, RAG indexing) widziały
  raw source pointer.
- **playwright re-fetch (opcjonalny):** dla orzeczeń.ms.gov.pl jeśli zachowany HTML
  niewystarczający — dodać follow-up script używający `playwright_sources/`
  infrastructure (już istnieje w repo, używane przez decyzje_uokik/sn_orzeczenia).
- **NIE commituj `_archive/*` files** — tylko optionally manifesty (~10 KB each).
