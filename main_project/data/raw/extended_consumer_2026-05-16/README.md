# Extended Polish Consumer Rights Dataset — 2026-05-16

Rozszerzenie Polish CitationBench dataset poza oryginalne źródła
(`consumer_questions_polish_2026-05-16/`, `uokik_qa_2026-05-16/`,
`eli_ustawy_konsumenckie_2026-05-16/`). Scrape uruchomiony 2026-05-16
przez `src/scrape/extended/` (5 adapterów).

## Pliki

| Plik | Rekordów | Source | License | Schema |
|---|---|---|---|---|
| `wikipedia_consumer.jsonl` | 34 | pl.wikipedia.org | CC BY-SA 4.0 | EncyclopedicChunk (per H2 section) |
| `federacja_konsumentow.jsonl` | 192 | federacja-konsumentow.org.pl | fair-use NGO | EncyclopedicChunk (per article) |
| `rzecznik_finansowy_faq.jsonl` | 374 | rf.gov.pl | urzędowe (Art. 4 PrAut) | QARecord (akkordeon Q&A) |
| `uokik_news.jsonl` | 111 | uokik.gov.pl/aktualnosci | urzędowe (Art. 4 PrAut) | EncyclopedicChunk (per news) |
| `gov_pl_consumer.jsonl` | 5 | gov.pl | urzędowe (Art. 4 PrAut) | EncyclopedicChunk (per page) |
| **TOTAL** | **716** | 5 sources | mixed | — |

Każdy `*_meta.json` zawiera per-source stats (licencja, kategoria breakdown,
notes nt. parsing strategy + warnings).

## Schemas

Patrz `src/halu/schemas.py`:
- `EncyclopedicChunk` — nowy (dodany 2026-05-16). Elastyczny chunk dla
  Wikipedia / porad / news. NIE wymaga citation hierarchy (art./§/ust.).
- `QAGoldPair` — istniejący. RF FAQ records mapują się 1:1 (modulo extra
  `license`, `source`, `metadata` fields).
- `ExtendedSource` enum — dodany, wartości dla 5 nowych źródeł.

## Pipeline

1. Scrape: `uv run python -m src.scrape.extended.<adapter> --output <DIR>`
2. Validation: `EncyclopedicChunk.model_validate(...)` na każdym record
3. Citation extraction: heurystyczna regex z `common.extract_citations()`
   — flaguje `art. N ust. M ustawy X` ale nie wszystkie warianty (TBD: full
   reference parser)

## Quality notes

- **Federacja Konsumentów:** najwięcej cytacji (48/192 = 25%). Najbardziej
  consumer-rights-domain-pure (porady prawne).
- **RF FAQ:** najwięcej Q&A par (374). UWAGA: zakres = finance/banking
  (transakcje nieautoryzowane, kredyty, ubezpieczenia) — consumer-adjacent
  ale NIE czyste klasyczne consumer rights.
- **UOKiK news:** dużo content (111 articles, avg 3.8k chars) ale TYLKO 3
  z explicit citations — journalistic style.
- **Wikipedia:** highest-quality encyclopedic (avg 2.5k chars/section).
  10/34 z citations (30%).
- **Gov.pl:** mały ale oficjalny (5 records, avg ~16k chars including
  wizard tabs).

## Skipped sources (z 12 w spec)

- **orzeczenia.ms.gov.pl** — Apache Tapestry POST search + Incapsula WAF
  na single-court subdomenach. Infeasible bez browser automation.
- **decyzje.uokik.gov.pl** — F5 WAF (HTTP 403, "URL rejected"). Blokuje
  scrape z standardowego klienta.
- **gov.pl/web/sprawiedliwosc/dla-obywatela** — landing page bez
  konsumencko-specyficznego content (general portal).
- **Allegro/OLX/banki T&C** — privacy / legal risk dla public scrape;
  out of scope.
- **Gazeta Prawna / Infor** — paywall/CDN, fair-use ambiguity. Skipped.

## Repro

```powershell
# Aktywacja env
cd D:\diplomma\main_project

# Wszystkie 5 adapterów (sekwencyjnie):
uv run python -m src.scrape.extended.wikipedia_consumer --output data/raw/extended_consumer_2026-05-16
uv run python -m src.scrape.extended.federacja_konsumentow --output data/raw/extended_consumer_2026-05-16
uv run python -m src.scrape.extended.rzecznik_finansowy --output data/raw/extended_consumer_2026-05-16
uv run python -m src.scrape.extended.uokik_news --output data/raw/extended_consumer_2026-05-16 --max-pages 12
uv run python -m src.scrape.extended.gov_pl_consumer --output data/raw/extended_consumer_2026-05-16
```

Czas wykonania całości: ~15 min (rate limit 1 req/s, ~600 unique URLs
fetched).
