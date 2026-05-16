# UE dyrektywy konsumenckie (PL) — S3 scrape output

**Date:** 2026-05-16
**Total:** 8 dyrektyw, 1480 chunks
**Source:** EUR-Lex `https://eur-lex.europa.eu/legal-content/PL/TXT/HTML/?uri=CELEX:{id}`
**License:** (c) European Union, free reuse per Decyzja 2011/833/UE (attribution required)

## Files (per dyrektywa)
- `{CELEX_ID}.jsonl` — atomic chunks (UEDyrektywa schema z `halu.schemas`)
- `{CELEX_ID}_meta.json` — metadata, scrape stats, source URLs, license
- `_summary.json` — aggregate stats wszystkich dyrektyw

## Schema (per chunk)
```json
{
  "chunk_id": "celex_32011L0083_art_6_ust_1_lit_a",
  "celex_id": "32011L0083",
  "direktywa_id": "2011/83/UE",
  "direktywa_title_pl": "Dyrektywa ... 2011/83/UE z dnia 25 października 2011 r. ...",
  "art": "6", "ust": "1", "pkt": null, "lit": "a", "motyw": null,
  "tresc": "główne cechy towarów lub usług w zakresie, w jakim ...",
  "citation_string": "art. 6 ust. 1 lit. a Dyrektywy 2011/83/UE",
  "license": "(c) UE — free reuse per Decyzja 2011/833/UE (attribution required)",
  "scrape_date": "2026-05-16",
  "source_url": "https://eur-lex.europa.eu/legal-content/PL/TXT/HTML/?uri=CELEX:32011L0083",
  "metadata": {
    "data_publikacji": "2011-11-22",
    "data_wejscia_w_zycie": "2011-12-12",
    "data_implementacji": "2013-12-13",
    "polska_implementacja": "DU/2014/827",
    "section": "articles",
    "art_subtitle": "Wymogi informacyjne dotyczące umów zawieranych na odległość ..."
  }
}
```

## Reproducibility
```bash
uv run python -m src.scrape.ue.dyrektywy                  # all 8
uv run python -m src.scrape.ue.dyrektywy --celex 32011L0083  # single
```

## Source legacy parser fallback
Stara dyrektywa **31993L0013 (93/13/EWG)** używa pre-2004 HTML format (TXT_TE flat
`<p>` tags bez semantic classes) — automatycznie wykrywane przez `parse_directive_html`
i kierowane do `parse_directive_html_legacy`. Preambuła nie chunkowana (struktura
nieregularna), ale pełen tekst preambuły dostępny w `source_url` URL.

## Defense argument
Pełen consumer law stack wymaga UE dyrektyw konsumenckich jako źródła polskich
implementacji (mapping w `../ue_polska_implementacja_2026-05-16/mapping.json`).
Cross-language citation chains umożliwiają validation polskich claims przeciwko
oryginałom UE.
