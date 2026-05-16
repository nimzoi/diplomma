# bezprawnik.pl — consumer rights scrape (2026-05-16)

**Source:** <https://bezprawnik.pl>

**License:** fair-use Art. 29 PrAut (academic research, attribution preserved)

**Method:** RSS feed + 10 tag pages walked (z paginacją 5 stron każdy)

**Scrape date:** 2026-05-16

## Schema

Każdy rekord w `articles.jsonl` ma pola: `article_id`, `source`, `source_url`, `title`, `subtitle`, `author`, `publication_date`, `tresc`, `category`, `tags`, `extracted_citations`, `license`, `scrape_date`, `metadata`.

## Files

- `articles.jsonl` — extracted, normalized text
- `_archive/{article_id}.html` + `.meta.json` — raw HTML + sha256
- `_manifest.json` — full mapping article_id → url, status, size
- `_summary.json` — aggregate stats
- `_failed.log` — URLs które nie udało się pobrać (jeśli istnieje)

## License rationale

fair-use Art. 29 PrAut (academic research, attribution preserved). Pobór mieści się w Polish TDM exception 2024 (implementacja Art. 4 DSM Directive 2019/790) — text and data mining dla research scientific purposes is permitted without authorization. Attribution preserved via `source_url` w każdym rekordzie.
