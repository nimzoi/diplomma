# ELI PDF corpus — canonical Dziennik Ustaw (2026-05-16)

Original Dziennik Ustaw PDFs (publication of record) dla **11 ustaw
konsumenckich** ze scope CitationBench. Side-by-side z XML/HTML scrape
w `data/raw/eli_ustawy_konsumenckie_2026-05-16/`.

**Skrypt:** `main_project/src/scrape/isap/download_pdf.py`
**Download date:** 2026-05-16
**Łącznie:** 20 plików, 62 666 167 bajtów (~59.76 MB), 0 errors

## Defense argument

PDF Dziennik Ustaw jest **official publication** Government of Poland (per art.
4 ust. 1 ustawy o prawie autorskim — akty normatywne public domain de facto).
HTML/XML z `api.sejm.gov.pl/eli` jest representation tego samego authoritative
tekstu. PDF służy jako **canonical cross-check source** dla deterministic
citation alignment:

- Każdy chunk w `DU_*.jsonl` ma deterministic `citation_string` zbudowany z XML
- PDF (oryginał) służy jako **gold standard** dla post-hoc audit alignment
- W przypadku discrepancy XML vs PDF — PDF jest source of truth (po Art. 4 PrAut)

## Per-ustawa layout

```
DU_YYYY_NNN/
  text.pdf                        # current announcement / latest publication
  text.pdf.meta.json              # {ustawa_id, kind, source_url, sha256, size_bytes, ...}
  tekst_jednolity_DU_YYYY_NNN.pdf # opcjonalnie — najnowszy tekst jednolity
  tekst_jednolity_*.meta.json
```

## Status

| Ustawa | text.pdf (MB) | Tekst jedn. (MB) | Łącznie (MB) | inForce |
|---|---:|---:|---:|---|
| DU/2014/827 (UPK) | 0.64 | 0.60 | 1.24 | IN_FORCE |
| DU/1964/93 (KC) | 25.13 | 9.16 | 34.29 | IN_FORCE |
| DU/2007/1206 (nieuczc. praktyki) | 0.21 | 0.18 | 0.39 | IN_FORCE |
| DU/2007/331 (ochrona konkur.) | 0.81 | 0.69 | 1.50 | IN_FORCE |
| DU/2011/1175 (usługi płatnicze) | 0.86 | 1.07 | 1.93 | IN_FORCE |
| DU/2016/1823 (pozasądowe spory) | 0.34 | — | 0.34 | IN_FORCE |
| DU/1997/939 (Prawo bankowe) | 6.97 | 7.19 | 14.16 | IN_FORCE |
| DU/2002/1204 (usługi elektr.) | 0.18 | 0.22 | 0.40 | IN_FORCE |
| DU/2024/1221 (Prawo kom. elektr.) | 3.27 | — | 3.27 | IN_FORCE |
| DU/2011/715 (kredyt konsum.) | 0.54 | 0.92 | 1.46 | IN_FORCE |
| DU/2010/44 (post. grupowe) | 0.32 | 0.45 | 0.77 | IN_FORCE |
| **TOTAL** | **39.27** | **20.49** | **59.76** | |

Wszystkie 11 ustaw są **IN_FORCE** at download time. Sha256 verified
post-download dla wszystkich 20 plików.

## Endpoints used

Primary:
```
GET https://api.sejm.gov.pl/eli/acts/{publisher}/{year}/{pos}/text.pdf
```

Tekst jednolity (najnowszy z `references."Inf. o tekście jednolitym"`):
```
GET https://api.sejm.gov.pl/eli/acts/{publisher}/{tj_year}/{tj_pos}/text.pdf
```

**Rate limit:** 1 req/sec polite (per scope brief). Timeout 60s.
**User-Agent:** `ELI corpus collector - MgSochacka PJATK thesis (citation-grounded RAG)`

## Reprodukcja

```powershell
# Wszystkie 11 ustaw
cd D:\diplomma
uv run python -m main_project.src.scrape.isap.download_pdf --scope all --output-dir main_project/data/raw/eli_pdf_2026-05-16

# Tylko nowe (5)
uv run python -m main_project.src.scrape.isap.download_pdf --scope new

# Pojedyncza
uv run python -m main_project.src.scrape.isap.download_pdf --ustawa DU/2014/827
```

## License

Art. 4 ust. 1 ustawy o prawie autorskim i prawach pokrewnych (Dz.U. 1994 poz. 83):
akty normatywne nie stanowią przedmiotu prawa autorskiego. Public domain de facto.

## Aggregate summary

`_download_summary.json` zawiera per-ustawa breakdown wszystkich files +
errors + sha256 + sources.

## Known gotchas

1. **DU/2016/1823 brak tekstu jednolitego** — ustawa pozasądowe spory została
   uchwalona w 2016 i jeszcze nie ma konsolidacji (niewiele nowelizacji).
2. **DU/2024/1221 brak tekstu jednolitego** — ustawa Prawo komunikacji
   elektronicznej weszła w życie ~2024, no consolidated yet.
3. **KC PDF ~34 MB** — KC ma ogromny tekst, w tym przepisy nie-konsumenckie. Pełen
   PDF (NIE filtered jak JSONL chunks).
4. **PDFs zawierają cały tekst ustawy** (NIE filtered jak JSONL z `art_filter`).
   PDF jest authoritative original — XML/HTML jest selektywne reprezentacja
   dla naszego scope (np. KC tylko art. 384-385 + 535-581 w chunks, ale PDF
   pełen).
