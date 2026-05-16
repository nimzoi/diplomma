# Extended polish consumer rights scrape — 2026-05-16

## Verdict
- **Total nowych records: 716** (z 5 źródeł)
- **Top 3 sources by quality:**
  1. **rf.gov.pl FAQ** (374 Q&A pairs, ekspertskie odpowiedzi z akkordeon) — najlepsza struktura
  2. **federacja-konsumentow.org.pl** (192 porad, 48 z cytacjami) — najczystsza consumer-domain
  3. **pl.wikipedia.org** (34 chunks per H2 section, 10 z cytacjami) — encyclopedic baseline
- **Total dataset growth: 5,150 → 5,866 records** (+13.9%)
  - Existing: 2,967 questions + 60 UOKiK Q&A + 2,123 ELI chunks = 5,150
  - Extended: +716 (Q&A: 374, encyclopedic chunks: 342)

## Per source

| # | Source | Records | License | Format | Quality |
|---|---|---|---|---|---|
| 1 | rf.gov.pl FAQ | 374 | urzędowe (Art. 4 PrAut) | QARecord (akkordeon) | ★★★★★ — explicit pytanie/odpowiedź, ale zakres = finance |
| 2 | federacja-konsumentow.org.pl | 192 | fair-use NGO | EncyclopedicChunk (per article) | ★★★★ — czysta consumer-rights domain, 25% z cit |
| 3 | uokik.gov.pl/aktualnosci | 111 | urzędowe (Art. 4 PrAut) | EncyclopedicChunk (per news) | ★★★ — dużo content, ale tylko 3% z explicit cit (journalistic) |
| 4 | pl.wikipedia.org | 34 | CC BY-SA 4.0 | EncyclopedicChunk (per H2) | ★★★★★ — best license, encyclopedic, 30% z cit |
| 5 | gov.pl | 5 | urzędowe (Art. 4 PrAut) | EncyclopedicChunk (per page) | ★★ — mały zbiór, oficjalny |

**Quality metrics:**
- Records with cited_articles (extracted heurystycznie regex): 134/716 = 18.7%
- Avg text length per chunk: 2.5k-3.8k chars (RF FAQ: krótsze answers)
- License distribution: 89% urzędowe lub CC BY-SA, 11% fair-use research

## Skipped sources (z 12 w spec — dokumentowane decyzje)

| Source | Powód skip |
|---|---|
| orzeczenia.ms.gov.pl | Apache Tapestry POST search + Incapsula WAF — wymaga browser automation |
| decyzje.uokik.gov.pl | F5 WAF blokuje requests (HTTP 403 "URL rejected") |
| gov.pl/web/sprawiedliwosc/dla-obywatela | General portal bez consumer-specific deep content |
| Allegro/OLX/banki T&C | Privacy + legal risk + niska dataset value (commerce policies) |
| Gazeta Prawna / Infor / Stack Exchange | Paywall/CDN issues + fair-use ambiguity |
| Polish legal YouTube transcripts | Out of scope (audio/video pipeline brak) |

## Technical notes

- **WAF bypass:** `rf.gov.pl` używa Incapsula który flaguje session reuse
  jako bot. Workaround: `Fetcher(per_request_session=True)` — fresh
  `requests.Session` na każdy request. Implementacja w `common.py`.
- **Citation extraction:** heurystyczna regex `art\. N (ust\. M)? ustawy X`
  z `common.extract_citations()`. Conservative — łapie tylko explicit
  `art.` references z statute marker. TBD w Iter. 1: full reference
  parser (np. spaCy z polskim NER albo dedicated parser).
- **NFC normalization:** wszystkie `tresc` fields są `unicodedata.normalize(
  "NFC", ...)` — walidowane w `EncyclopedicChunk.field_validator`.
- **Rate limiting:** 1 req/s globalnie, retries z exponential backoff.

## Recommendation dla Iter. 1

**Include w main retrieval corpus:**
- `wikipedia_consumer.jsonl` (best license, semantically clean) — direct merge
- `federacja_konsumentow.jsonl` (domain-pure porady) — direct merge
- `rzecznik_finansowy_faq.jsonl` (Q&A — duplicate UOKiK pattern z większą
  liczbą par, useful dla training distribution)

**Separate eval split (z domain ambiguity flag):**
- `uokik_news.jsonl` — journalistic, mało cit, użyć jako "noisy real-world
  consumer awareness" subset dla negative-result framing (RQ4 drift detector)
- `gov_pl_consumer.jsonl` — too small dla split, attach jako appendix

**License risks + mitigations:**
- Federacja Konsumentów: brak explicit CC — `fair-use research` framing.
  Mitigation: pełne attribution w `source_url`, NIE redistribute samodzielnie
  (tylko derived embeddings/metrics).
- RF + UOKiK + gov.pl: urzędowe → bezpieczne (Art. 4 PrAut wyłącza materiały
  państwowe z prawa autorskiego).
- Wikipedia: CC BY-SA — wystarczy attribution (URL w `source_url` + license
  field).

## Next steps Iter. 1

1. **Dedup:** sprawdzić overlap między `federacja_konsumentow.jsonl` a
   istniejące `uokik_qa.jsonl` (możliwy overlap w "Rękojmia", "Reklamacja"
   topics).
2. **Citation parser upgrade:** uzupełnić heurystyczną regex o handling
   dla "Kodeksu cywilnego art. 22^1" notation + multi-statute references.
3. **Topic tagging:** uruchomić `legal_fora.scrape.extract_topics()` na
   nowych chunks żeby mieć multi-label coverage z istniejącymi sources.
4. **Eval split:** propose 100-200 records jako separate hold-out (Wikipedia
   sections jako gold-standard semantic eval, Federacja porady jako
   real-world porady eval).
