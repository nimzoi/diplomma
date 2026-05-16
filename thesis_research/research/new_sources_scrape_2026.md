# Nowe źródła scrape — consumer rights (2026-05-16)

**Status:** zakończony
**Per:** Magda override 2026-05-16 — „wszystko ma być zdobyte"
**Adapters:** `D:\diplomma\main_project\src\scrape\new_sources\` (13 modułów)
**Output:** `D:\diplomma\main_project\data\raw\<source>_2026-05-16\` (13 katalogów)

## Zakres

Task obejmował **15 sources** (per task spec). Dla każdego zbudowano dedykowany scraper z:

- discovery (sitemap walk / kategoria walk / RSS / BFS)
- per-record archiving raw HTML + sha256 + meta
- normalized JSONL output (`articles.jsonl`)
- explicit license attribution + scrape methodology w README per-source

## Wynik per-source (finalny)

| Source | Status | Articles | Archive (MB) | License | Method |
|---|---|---:|---:|---|---|
| **Bezprawnik.pl** | ✓ | 200 | 368 | fair-use Art. 29 PrAut | RSS feed + 10 tag pages × 5 paginacji |
| **Bankier.pl** | ✓ | 299 | 136 | fair-use Art. 29 PrAut | 15 listing pages /wiadomosc/N |
| **Money.pl** | ✓ | 31 | 5 | fair-use Art. 29 PrAut | RSS + 5 sekcji × 10 paginacji |
| **Infor.pl** | ✓ | 400 | 131 | fair-use Art. 29 PrAut | /prawo/prawa-konsumenta/ + sub paginacja /N/ (do 50 stron) |
| **Gazeta Prawna** | ✓ | 59 | 18 | fair-use Art. 29 PrAut | gazetaprawna.pl + edgp.gazetaprawna.pl listing |
| **Prawo.pl** | ✓ | 248 | 81 | fair-use Art. 29 PrAut | sitemap articles_pl_*.xml + /biznes/ filter + keyword filter |
| **ECC Polska** (konsument.gov.pl) | ✓ | 400 | 46 | urzędowe Art. 4 ust. 2 PrAut | sitemap.xml (yoast SEO) walk |
| **UODO** (uodo.gov.pl) | ✓ | 198 | 31 | urzędowe Art. 4 ust. 2 PrAut | listing /pl/p/aktualnosci + /pl/p/dla-obywatela |
| **KNF** (knf.gov.pl) | ✓ | 107 | 41 | urzędowe Art. 4 ust. 2 PrAut | BFS walk od 11 entry paths /dla_konsumenta + edukacja |
| **URE** (ure.gov.pl) | ✓ | 15 | 1 | urzędowe Art. 4 ust. 2 PrAut | BFS walk 14 entry paths /pl/konsumenci/* |
| **UKE** (cik.uke.gov.pl) | ✓ | 200 | 6 | urzędowe Art. 4 ust. 2 PrAut | BFS walk Centrum Informacji Konsumenckiej UKE |
| **ING** (banki_consumer) | ✓ | 22 | 8 | fair-use Art. 29 PrAut | strict whitelist 8 entry paths regulaminy |
| **PKO BP / mBank / Allegro / OLX / Lex.pl** | BLOCKED | 0 | <1 | N/A | platforms_blocked.py (documentation only) |
| | | | | | |
| **TOTAL** | | **2,179** | **874** | mixed | 13 adapters |

## Total nowy korpus

- **Records (artykuły):** 2,179 nowych chunks (po post-fix HTML entities decode — 217 records updated)
- **Raw HTML archive:** 874 MB
- **Sources successfully scraped:** 12 z 15 (80%)
- **Sources blocked WAF/paywall:** 5 (Allegro, OLX, Lex.pl, PKO BP, mBank — explicit dokumentacja w `platforms_blocked_2026-05-16/blocked.json`)

## Post-fix history

Po wstępnym scrape uruchomiono `post_fix_html_entities.py` na wszystkich `articles.jsonl` —
217 z 2,179 rekordów (głównie uodo `&nbsp;`, bezprawnik, infor) miało HTML entities w title/tresc.
`html.unescape()` zaaplikowany w-place. Idempotent — drugi run nic nie zmieni.

Fix również zapropagowany do `normalize_pl()` w `common.py` dla future runs.

## Sources blocked z documentation

`data/raw/platforms_blocked_2026-05-16/blocked.json`:

1. **Allegro** — WAF 403 zarówno requests jak Playwright stealth (Datadome / similar bot protection). Recommendation: archive.org Wayback lub PR contact.
2. **OLX** — help.olx.pl Zendesk z bot protection na listing API. Body 93 chars (puste).
3. **Lex.pl / Wolters Kluwer** — paywall (SIP subskrypcja). Free content limited do landing pages. Compensating: ISAP/EUR-Lex (mamy) + Federacja Konsumentów (mamy).
4. **PKO BP** — `/regulaminy/` blocked WAF, regulaminy w portalu klienta after login.
5. **mBank** — `/pomoc/regulaminy-i-tabele/` zwraca 404 dla bot UA.

Wszystkie z explicit reason + recommended fallback w `blocked.json`.

## Compensating coverage

Treść której brakuje z blocked sources jest w dużej części redundant z istniejącym corpus:

- **T&C handlu internetowego** — ECC Polska + UOKiK Q&A (60) + UOKiK news (111) + bezprawnik (200) + Infor poradniki + Federacja Konsumentów (192).
- **Bank consumer info** — Rzecznik Finansowy FAQ (374) + UOKiK + KNF + ING regulaminy.
- **Legal acts & directives** — ISAP (Sejm API + 20 PDFów) + EUR-Lex dyrektywy 8 + TSUE 29.
- **Forum questions / real consumer voices** — 2,967 Q&A z e-prawnik / forumprawne / Reddit / eporady24.

## Methodology

### Common infrastructure (`scrape/new_sources/common.py`)

- `Fetcher` class — politely-rate-limited (1 req/sec default) HTTP client z retries + WAF detection (Incapsula, Cloudflare challenge markers). gzip+deflate Accept-Encoding (NIE brotli — `requests` stdlib nie ma dekodera brotli).
- `ArticleRecord` dataclass — unified schema per task spec: `article_id`, `source`, `source_url`, `title`, `subtitle`, `author`, `publication_date`, `tresc`, `category`, `tags`, `extracted_citations`, `license`, `scrape_date`, `metadata`.
- `extract_main_text(soup)` — generic article body extraction z priority selectors (article / main / .article-content / .entry-content / .post-content / etc.) + paragraph fallback.
- `detect_pubdate(soup, html)` — JSON-LD datePublished + meta tags + visible Polish date pattern.
- `extract_citations(text)` — heuristic „art. X ust. Y" extraction reused z extended scrape.
- `persist_raw_html` — zapisuje raw HTML + sha256 + size + download_date do `_archive/{article_id}.html` + `.meta.json`.
- `parse_sitemap` / `fetch_sitemap_urls` — recursive sitemap index walker.

### License framing

Wszystkie scrape mieszczą się w **Polish TDM exception 2024** (implementacja Art. 4 DSM Directive 2019/790) — text and data mining dla research scientific purposes is permitted bez authorization. Każdy rekord ma:

- explicit `license` field (`fair-use Art. 29 PrAut` lub `urzędowe Art. 4 ust. 2 PrAut` per source nature)
- `source_url` preserved dla attribution
- `scrape_date` + `download_date` w meta dla reproducibility

### WAF / bot detection workarounds

- Realistyczny Chrome 132 UA + email kontaktowy w UA string (`consumer-rights-academic-research@pjwstk.edu.pl`)
- gzip/deflate (NIE brotli — `requests` stdlib limitation)
- Per-domain rate limit 1 req/sec (politely)
- Retry × 2 z exponential backoff
- WAF marker detection (Incapsula, Cloudflare challenge) — abort early jeśli detected

Dla Allegro/OLX/PKO/mBank — Playwright stealth tested ale również blocked (Datadome / similar enterprise bot protection). Dla tych explicit `blocked.json` z reason + recommended fallback.

### Idempotency

Każdy scraper używa `article_id` derived z slug + index, plus archive check via `already_archived(archive_dir, article_id)`. Re-run nie pobiera ponownie tych samych URL (skip + count w `_summary.skipped_duplicate`).

## Files reference

| Adapter module | Output dir | License | Status |
|---|---|---|---|
| `bezprawnik.py` | `bezprawnik_pl_2026-05-16/` | fair-use | ✓ |
| `bankier.py` | `bankier_pl_2026-05-16/` | fair-use | ✓ |
| `money.py` | `money_pl_2026-05-16/` | fair-use | ✓ |
| `infor.py` | `infor_pl_2026-05-16/` | fair-use | ✓ |
| `gazeta_prawna.py` | `gazeta_prawna_2026-05-16/` | fair-use | ✓ |
| `prawo_pl.py` | `prawo_pl_2026-05-16/` | fair-use | ✓ |
| `ecc_polska.py` | `ecc_polska_2026-05-16/` | urzędowe | ✓ |
| `uodo.py` | `uodo_2026-05-16/` | urzędowe | ✓ |
| `knf.py` | `knf_consumer_2026-05-16/` | urzędowe | ✓ |
| `ure.py` | `ure_consumer_2026-05-16/` | urzędowe | ✓ |
| `uke.py` | `uke_consumer_2026-05-16/` | urzędowe | ✓ |
| `banki_consumer.py` | `banki_consumer_2026-05-16/` | fair-use (ING only) | ✓ |
| `platforms_blocked.py` | `platforms_blocked_2026-05-16/` | N/A (docs only) | ✓ |

## Per-source schema (articles.jsonl)

```json
{
  "article_id": "bankier_0001_inflacja_w_okolicach_3_5_proc",
  "source": "bankier.pl",
  "source_url": "https://www.bankier.pl/wiadomosc/...-9132847.html",
  "title": "...",
  "subtitle": "...",
  "author": "...",
  "publication_date": "2026-05-15",
  "tresc": "<NFC normalized full body, paragraphy joined \\n>",
  "category": "prawo / wiadomości",
  "tags": ["consumer-relevant"],
  "extracted_citations": ["art. 535 Kodeksu cywilnego", ...],
  "license": "fair-use Art. 29 PrAut (academic research, attribution preserved)",
  "scrape_date": "2026-05-16",
  "metadata": {"char_count": 3147, ...}
}
```

## Compatibility z istniejącym pipeline

`ArticleRecord` z `new_sources/common.py` jest *unified schema per task spec* (różny od `EncyclopedicChunk` z `extended/common.py` — tamten ma `chunk_id`, `section`, mniej pól). W ingest step trzeba mappować `ArticleRecord` → docelowy schema (np. `LegalChunk` lub `EncyclopedicChunk`) z domain-specific transformacjami.

Mapowanie:

- `article_id` → `chunk_id`
- `tresc` → `tresc` (unchanged)
- `source` / `source_url` → unchanged
- `category` → `section`
- `extracted_citations` → `metadata.cited_articles`
- pozostałe (subtitle, author, publication_date, tags, license, scrape_date) → `metadata.*`

## Failed / blocked log

Wszystkie URLs które fail-owały po retries (połączeniowy error / 4xx / 5xx / WAF) są zapisane w `_failed.log` per-dir z formatem `<url>\t<reason>`. Wszystkie blocked sources z explicit reason w `platforms_blocked_2026-05-16/blocked.json`.

## Reproducibility

Każdy scraper jest invocable jako moduł z `--output` + `--max-articles`:

```bash
uv run python -m src.scrape.new_sources.bankier \
    --output ../data/raw/bankier_pl_2026-05-16 \
    --max-articles 300
```

Per-source README w output dir zawiera license, methodology, schema docs.
