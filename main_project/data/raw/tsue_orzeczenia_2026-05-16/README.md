# TSUE orzeczenia konsumenckie (PL) — S3 scrape output

**Date:** 2026-05-16
**Total:** 29 orzeczeń (1 skipped — Benincasa C-269/95 pre-akcesyjne, brak PL wersji)
**Source:** EUR-Lex `https://eur-lex.europa.eu/legal-content/PL/TXT/HTML/?uri=CELEX:{celex}`
**License:** (c) European Union, free reuse per Decyzja 2011/833/UE (attribution required)

## Files
- `tsue_orzeczenia.jsonl` — wszystkie orzeczenia (TSUEOrzeczenie schema z `halu.schemas`)
- `per_case_meta/{case_id}_meta.json` — metadata per sprawa (case_id, sklad,
  streszczenie, tezy_kluczowe, related_directives)
- `_summary.json` — aggregate stats + skipped list

## Schema (per case)
```json
{
  "case_id": "C-260/18",
  "celex_id": "62018CJ0260",
  "case_name": "Kamil Dziubak, Justyna Dziubak v Raiffeisen Bank International AG",
  "data_orzeczenia": "2019-10-03",
  "sklad": "trzecia izba: A. Prechal (sprawozdawczyni)",
  "streszczenie": "Odesłanie prejudycjalne – Dyrektywa 93/13/EWG – Umowy ...",
  "tezy_kluczowe": [
    "Artykuł 6 ust. 1 dyrektywy Rady 93/13/EWG z dnia 5 kwietnia 1993 r. ..."
  ],
  "pelna_tresc": "WYROK TRYBUNAŁU (trzecia izba) z dnia 3 października 2019 r. ...",
  "citation_string": "Wyrok TSUE z dnia 3 października 2019 r. w sprawie C-260/18 Dziubak",
  "license": "(c) UE — free reuse per Decyzja 2011/833/UE (attribution required)",
  "scrape_date": "2026-05-16",
  "source_url": "https://eur-lex.europa.eu/legal-content/PL/TXT/HTML/?uri=CELEX:62018CJ0260",
  "metadata": {
    "case_name_short": "Dziubak",
    "related_directives": ["93/13/EWG"],
    "legal_topic": "klauzule abuzywne, CHF kredyty hipoteczne, polskie tlo",
    "jurystdykcja": "TSUE (Court of Justice EU)",
    "notes": "CRITICAL — fundament polskiego CHF orzecznictwa"
  }
}
```

## Skipped cases
**C-269/95 Benincasa** — orzeczenie z 1997 r., przed akcesją Polski do UE (2004-05-01).
EUR-Lex zwraca tylko EN/DE/FR/IT/ES wersje. W pracy badawczej należy cytować
z streszczeń wtórnych (np. komentarz SN, podręczniki KC).

## Reproducibility
```bash
uv run python -m src.scrape.ue.tsue              # all priority cases
uv run python -m src.scrape.ue.tsue --case C-260/18  # single
```

## Priority list rationale
Hand-curated 30 spraw oparta o:
- Dyrektywa 93/13/EWG (UCT) — 18 spraw, najwięcej praktyki sądowej:
  - **CHF**: Dziubak C-260/18, Kásler C-26/13, Bank BPH C-19/20, Andriciuc C-186/16,
    Bank M. C-520/21 (post-Dziubak), Gómez del Moral C-125/18, Dunai C-118/17
  - **Ex officio kontrola**: Pannon C-243/08, Aziz C-415/11
  - **Skutek abuzywności**: Perenicová C-453/10, Abanca C-70/17
- Dyrektywa 2008/48/WE (CCD) — 5 spraw (Radlinger C-377/14, CA Consumer C-449/13,
  Home Credit C-42/15, Kreissparkasse C-66/19, LCL C-565/12)
- Dyrektywa 2011/83/UE (CRD) — 4 sprawy (Fuhrmann-2 C-249/21, NK C-208/19,
  Verbraucherzentrale 2x)
- Dyrektywa 2005/29/WE (UCPD) — 3 sprawy (Mediaprint, Orange Polska, Perenicová crossover)

## Defense argument
TSUE wykładnia dyrektyw konsumenckich jest wiążąca dla polskich sądów (acquis
communautaire) → pełen consumer law stack wymaga cytowania orzeczeń. Probe + verifier
mogą weryfikować claim consistency cross-language (Polish answer ↔ Polish ustawa ↔
UE dyrektywa ↔ TSUE wykładnia).
