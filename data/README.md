# Dataset — JDG chatbot baseline (data collection v2)

This folder is the artefact of the work described in
`descriptions/data_collection_spec.md` and `descriptions/12_data_collection_execution_plan.md`.
**Scope:** discover → fetch → save raw + sidecar metadata + content audit.
**Out of scope:** parsing, chunking, embeddings, vector indexing, semantic
dedup (see spec section 17). Those belong to the next pipeline stage.

## Layout

```
data/
  manifest.csv                    main index (one row per saved artifact)
  content_audit.csv               per-document content sanity check (chars,
                                  diacritics ratio, vocab hits, flag)
  coverage_report.md              auto-generated KPI/coverage report
  manifests/
    coverage_51_topics.csv        seed of the 51 topics from spec section 4
  raw/
    legislation/                  ELI / api.sejm.gov.pl PDFs (Layer 1)
    eurlex/                       EUR-Lex consolidated PL PDFs (Layer 1)
    podatki/                      podatki.gov.pl brochures + forms
    pip/                          PIP poradniki / publikacje (JDG-relevant)
    uodo/                         UODO poradniki i wytyczne
    zus/                          ZUS poradniki + wzory (chrome UA)
    biznes_gov/                   biznes.gov.pl PDFs via Playwright
    templates_docx/               biznes.gov.pl DOCX wzory via Playwright
  logs/
    fetch_log.ndjson              every HTTP attempt (one JSON per line)
    rejected_files.ndjson         rejected/quarantined files
  quarantine/
    _failed/                      404 / wrong magic / WAF redirects
    _too_small/                   below 2 KB threshold
```

For every saved file `data/raw/<source>/<name>.pdf` there is a sibling
`data/raw/<source>/<name>.pdf.meta.json` with full HTTP headers, hash,
detected topics, and the content_audit verdict.

## What changed in v2

After review of v1 we found and fixed multiple data-quality issues:

1. **Wrong L1 MUST acts.** Spec used legacy `Dz.U. nr/poz` notation (e.g.
   `WDU19910800350` = 1991 nr 80 poz 350) but ELI URLs accept *position* only,
   not issue number. Four MUST acts were therefore the wrong document
   (`/eli/acts/DU/1991/80/text.pdf` returned the act on Members of Parliament
   instead of the PIT law). Re-downloaded with corrected URLs:

   - Kodeks pracy → `DU/1974/141`
   - Ustawa o PIT → `DU/1991/350`
   - Ustawa o systemie ub. społ. → `DU/1998/887`
   - Ustawa o ryczałcie → `DU/1998/930`

2. **Content audit.** `scripts/audit_content.py` now runs `pdftotext` on the
   first 12 pages of every PDF and writes per-document flags into
   `content_audit.csv` and into each sidecar JSON's `content_audit` field:

   - `ok` — substantive Polish text, JDG vocabulary present
   - `image_pdf` — image-only / OCR-needed (text < 500 chars)
   - `low_polish` — non-Polish text (English brochures, etc.)
   - `off_topic` — Polish but not JDG-related (industrial machinery, etc.)

   The cleanup pipeline drops `image_pdf` entirely, `low_polish` for non-ELI
   sources (we keep EU-Lex acts even when consolidated PDFs have low Polish
   density), and `off_topic` for `pip`/`podatki` where we've confirmed by hand
   it's not JDG.

3. **Sidecar privacy.** `set-cookie` and `cookie` headers are now stripped
   from sidecar JSONs (PR review feedback).

4. **Title normalisation.** PIP scraper used to capture the section header
   ("BHP", "Prawo", "Wzory…") as part of the anchor text, which leaked into
   `title`. Whitespace is collapsed and the leading category prefix is
   removed.

5. **biznes.gov.pl via Playwright.** v1 noted the WAF blocked the academic
   UA. v2 uses Playwright with Chrome UA and `ignore_https_errors=True`,
   then post-processes asset links from rendered DOM. Cookies are handed
   off to a `requests` session for binary downloads.

6. **L1 fetchers idempotent.** Re-running `fetch_l1_must.py` /
   `fetch_l1_regs.py` no longer duplicates manifest rows.

7. **Topic auto-tagger broader.** Added keywords for `pit_roczny`,
   `ceidg_pkd`, `kp_wypowiedzenie`, `kp_bhp_biuro`, `rodo_monitoring`,
   `rodo_rekrutacja`. Manual tagging (`tag_ceidg_subtopics.py`,
   `tag_general_acts.py`) covers cases where keywords don't match the
   section heading but the act covers the topic (e.g. wznowienie/zamknięcie
   inside the Prawo przedsiębiorców act).

## Reproducing

All collection scripts live under `/scripts`:

```
scripts/common.py                shared helpers (fetch, manifest, save)
scripts/topics.py                51-topic catalogue + keyword auto-tagger
scripts/build_coverage_seed.py   one-shot CSV of the 51 topics
scripts/fetch_l1_must.py         8 MUST acts (spec 5.1) + RODO from EUR-Lex
scripts/fix_l1_must.py           fixes the 4 wrong MUST acts (run once)
scripts/fetch_l1_regs.py         executive regulations via ELI search
scripts/fetch_l1_consolidated.py tekst jednolity for KC / Ordynacja / etc.
scripts/fetch_extra_eurlex.py    extra EU acts (VAT directive, eIDAS, DSA,…)
scripts/fetch_l2_podatki.py      podatki.gov.pl BFS (PIT / VAT / JPK / KSeF)
scripts/fetch_l2_pip.py          pip.gov.pl publication paginator
scripts/fetch_l2_uodo.py         uodo.gov.pl accordion-driven hubs
scripts/fetch_l2_zus.py          zus.pl (chrome UA bypasses F5 ASM)
scripts/fetch_l2_biznes.py       biznes.gov.pl via Playwright (NEW)
scripts/cleanup_pip.py           drop industry-specific PIP files
scripts/cleanup_off_topic_pip.py extra prune for industrial machinery PIP
scripts/audit_content.py         pdftotext audit -> content_audit.csv
scripts/cleanup_low_quality.py   drop image_pdf / low_polish / off_topic
scripts/fix_sidecar_quality.py   strip cookies, normalise titles
scripts/retag_manifest.py        re-run topic auto-tag over manifest
scripts/tag_ceidg_subtopics.py   manual CEIDG sub-operations tag
scripts/tag_general_acts.py      manual tag for general legal acts
scripts/build_coverage_report.py refresh data/coverage_report.md
```

Recommended order for a clean rebuild:

```bash
python3 scripts/build_coverage_seed.py
python3 scripts/fetch_l1_must.py
python3 scripts/fetch_l1_regs.py
python3 scripts/fetch_l1_consolidated.py
python3 scripts/fetch_extra_eurlex.py
python3 scripts/fetch_l2_podatki.py
python3 scripts/fetch_l2_pip.py
python3 scripts/fetch_l2_uodo.py
python3 scripts/fetch_l2_zus.py
python3 scripts/fetch_l2_biznes.py            # needs playwright + chromium
python3 scripts/cleanup_pip.py
python3 scripts/cleanup_off_topic_pip.py
python3 scripts/audit_content.py
python3 scripts/cleanup_low_quality.py
python3 scripts/fix_sidecar_quality.py
python3 scripts/retag_manifest.py
python3 scripts/tag_ceidg_subtopics.py
python3 scripts/tag_general_acts.py
python3 scripts/build_coverage_report.py
```

Dependencies: standard library, `requests`, `playwright`, `pdftotext` (CLI).

## Citing

Each row in `manifest.csv` carries the original source URL, fetch timestamp
and HTTP headers. For any file `raw/<source>/<name>.pdf` you can quote it as:

> *<title>*, <source domain>, [URL] (pobrano: <fetched_at>; ELI: <eli_id> /
> CELEX: <celex>).
