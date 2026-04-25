# Dataset — JDG chatbot baseline (data collection v1)

This folder is the artefact of the work described in
`descriptions/data_collection_spec.md` and `descriptions/12_data_collection_execution_plan.md`.
**Scope:** discover → fetch → save raw + sidecar metadata.
**Out of scope:** parsing, chunking, embeddings, vector indexing, semantic dedup
(see spec section 17). Those belong to the next pipeline stage.

## Layout

```
data/
  manifest.csv                    main index (one row per saved artifact)
  coverage_report.md              auto-generated KPI/coverage report
  manifests/
    coverage_51_topics.csv        seed of the 51 topics from spec section 4
  raw/
    legislation/                  ELI / api.sejm.gov.pl PDFs (Layer 1)
    eurlex/                       EUR-Lex consolidated PL PDFs (Layer 1)
    podatki/                      podatki.gov.pl brochures + forms
    pip/                          PIP poradniki / publikacje
    uodo/                         UODO poradniki i wytyczne
    zus/                          ZUS poradniki + wzory
    biznes_gov/                   (empty — see "biznes.gov.pl" below)
    kis/                          (empty — see "Layer 3" below)
    templates_docx/               (empty — see "Layer 3" below)
  logs/
    fetch_log.ndjson              every HTTP attempt (one JSON per line)
    rejected_files.ndjson         rejected/quarantined files
  quarantine/
    _failed/                      404 / wrong magic / WAF redirects
    _too_small/                   below 2 KB threshold
    _waf_blocked/                 (empty — biznes.gov.pl was not attempted)
```

For every saved file `data/raw/<source>/<name>.pdf` there is a sibling
`data/raw/<source>/<name>.pdf.meta.json` with full HTTP headers, hash,
detected topics and audit fields.

## Reproducing

All collection scripts live under `/scripts`:

```
scripts/common.py                shared helpers (fetch, manifest, save)
scripts/topics.py                51-topic catalogue + keyword auto-tagger
scripts/build_coverage_seed.py   one-shot CSV of the 51 topics
scripts/fetch_l1_must.py         8 MUST acts (spec 5.1) + RODO from EUR-Lex
scripts/fetch_l1_regs.py         executive regulations via ELI search
scripts/fetch_l1_consolidated.py tekst jednolity for KC / Ordynacja / etc.
scripts/fetch_extra_eurlex.py    additional EU acts (VAT directive, eIDAS, DSA,…)
scripts/fetch_l2_podatki.py      podatki.gov.pl BFS (PIT / VAT / JPK / KSeF)
scripts/fetch_l2_pip.py          pip.gov.pl publication paginator
scripts/fetch_l2_uodo.py         uodo.gov.pl accordion-driven hubs (679/598/383)
scripts/fetch_l2_zus.py          zus.pl (chrome UA bypasses F5 ASM)
scripts/cleanup_pip.py           drop industry-specific PIP files
scripts/retag_manifest.py        re-run topic auto-tag over an existing manifest
scripts/tag_ceidg_subtopics.py   manual tag for CEIDG sub-operations
scripts/tag_general_acts.py      manual tag for general legal acts
scripts/build_coverage_report.py refresh data/coverage_report.md
```

Run them in this order:

```bash
python3 scripts/build_coverage_seed.py
python3 scripts/fetch_l1_must.py
python3 scripts/fetch_l1_regs.py
python3 scripts/fetch_l1_consolidated.py
python3 scripts/fetch_extra_eurlex.py
python3 scripts/fetch_l2_podatki.py
python3 scripts/fetch_l2_pip.py
python3 scripts/cleanup_pip.py        # twice if running again
python3 scripts/fetch_l2_uodo.py
python3 scripts/fetch_l2_zus.py
python3 scripts/retag_manifest.py
python3 scripts/tag_ceidg_subtopics.py
python3 scripts/tag_general_acts.py
python3 scripts/build_coverage_report.py
```

Dependencies: standard library + `requests`. No proxies, no headless browser,
no selenium.

## What was collected

See `data/coverage_report.md` for the live numbers, but on the run committed:

- **260 documents**, **51/51 topics** covered (spec section 16 minimum: 51/51).
- Layer 1 (legislation): **42** acts — 8 MUST + 4 extra EU + 30 executive
  regulations and consolidated acts (Ordynacja, Kodeks cywilny, KKS, KPA,
  KRS, świadczenia opieki zdrowotnej, ust. chorobowa, FUS, prawo autorskie,
  rachunkowość, minimalne wynagrodzenie, nieuczciwa konkurencja, KSeF zmiana,
  KPiR, ewidencja ryczałtu, JPK_V7, faktury, stawki VAT, świadectwo pracy,
  BHP szkolenie wstępne, PKD 2025).
- Layer 2 (poradniki rządowe): **218** docs — `podatki.gov.pl` 72,
  `pip.gov.pl` 118 (after off-topic prune of azbest, budownictwo, rolnictwo,
  fryzjer, masarn, tartak…), `uodo.gov.pl` 8, `zus.pl` 20.
- 100 % files have validated `%PDF` magic; quarantine holds 404/WAF redirects.
- 100 % rows are `.gov.pl` / `eur-lex.europa.eu` (spec target ≥ 80 %).

## Known gaps (intentional)

1. **biznes.gov.pl** — Akamai WAF blocks plain `requests`. Per spec section 19
   we did not bypass it. To collect it, run undetected-chromedriver locally.
2. **KIS individual interpretations** — `sip.mf.gov.pl` is a JS SPA. Headless
   browser required; out of this run.
3. **DOCX templates** — folder is in place; can be filled from biznes.gov.pl
   `pliki.biznes.gov.pl/...` and `zus.pl/wzory-formularzy` once WAF is solved.

## Citing the dataset

Each row in `manifest.csv` carries the original source URL, fetch timestamp
and HTTP headers. For any file `raw/<source>/<name>.pdf` you can quote it as:

> *<title>*, <source domain>, [URL] (pobrano: <fetched_at>; ELI: <eli_id> /
> CELEX: <celex>).
