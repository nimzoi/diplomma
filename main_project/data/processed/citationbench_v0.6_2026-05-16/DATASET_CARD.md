---
language:
- pl
license: cc-by-nc-sa-4.0
task_categories:
- question-answering
- text-classification
tags:
- polish
- consumer-rights
- hallucination-detection
- citation-grounding
- legal-nlp
- rag
size_categories:
- 1K<n<10K
---

# Polish CitationBench (v0.6)

**Snapshot date:** 2026-05-16
**Domena:** polskie prawa konsumenta + EU consumer law context
**Use case:** citation-grounded RAG hallucination detection benchmark

## Aggregate stats

- **Total unified chunks:** 11000
- **Chunks z cytacjami:** 2345 (21.3%)
- **Avg tresc length:** 1324 chars
- **Synthetic halu pairs:** 5402 (1 negative + N positive per UOKiK gold pair)

## Source types

| source_type | count |
|---|---|
| qa_raw | 2945 |
| legal_statute | 2541 |
| legal_document_pdf | 1965 |
| legal_ue_directive | 1360 |
| encyclopedic | 1167 |
| legal_court_judgment | 534 |
| qa_gold | 433 |
| legal_tsue_judgment | 29 |
| legal_uokik_decision | 26 |

## Sources (top 15)

| source | count |
|---|---|
| isap.sejm.gov.pl | 2541 |
| rf.gov.pl | 2066 |
| eur-lex.europa.eu | 1389 |
| forumprawne.org | 1186 |
| e-prawnik.pl | 948 |
| orzeczenia.ms.gov.pl | 534 |
| reddit.com/r/Polska | 509 |
| konsument.gov.pl | 393 |
| uokik.gov.pl | 313 |
| eporady24.pl | 302 |
| federacja-konsumentow.org.pl | 262 |
| uodo.gov.pl | 198 |
| cik.uke.gov.pl | 128 |
| knf.gov.pl | 91 |
| prawakonsumenta.uokik.gov.pl | 60 |

## Categories (multi-label)

| category | count |
|---|---|
| finance_adjacent | 9076 |
| consumer_contract | 5872 |
| consumer_core | 4169 |
| eu_directive | 2906 |
| consumer_return_refund | 1896 |
| consumer_credit | 1189 |
| other | 945 |
| consumer_dispute_resolution | 543 |
| tsue_judgment | 296 |
| court_precedent | 275 |
| consumer_digital | 237 |
| regulatory_decision | 193 |
| consumer_telecom | 79 |
| consumer_unfair_practices | 47 |

## Schema (unified Chunk — option b per author decision 2026-05-16)

```python
class Chunk(BaseModel):
    chunk_id: str
    source_type: SourceType  # legal_statute | legal_ue_directive | legal_tsue_judgment | ...
    source: str
    source_url: str
    title: str
    tresc: str
    citation_string: str | None
    cited_articles: list[str]
    categories: list[Category]  # multi-label
    language: str = "pl"
    license: str
    scrape_date: date
    process_date: date
    metadata: dict
```

Pełna specyfikacja: `src/halu/schemas.py`.

## Files

- `chunks.jsonl` — unified Chunk records (all sources)
- `halu_pairs.jsonl` — synthetic HaluPair records (train probe + verifier)
- `splits/` — stratified train/val/test by source_type + category

## Citation

```bibtex
@misc{sochacka2026citationbench,
  title = {Polish CitationBench: citation-grounded RAG hallucination detection benchmark},
  author = {Sochacka, Magdalena},
  year = {2026},
  howpublished = {HuggingFace Datasets},
  note = {Praca inżynierska, PJATK}
}
```

## Licensing

Mixed-license dataset z explicit per-chunk attribution:

- **ELI / Polish statutes:** urzędowe (Art. 4 ust. 2 PrAut + TDM exception Wrzesień 2024)
- **UOKiK Q&A + decyzje:** urzędowe (Art. 4 ust. 2 PrAut)
- **UE EUR-Lex content:** © European Union, reuse per Decision 2011/833/UE
- **Wikipedia:** CC BY-SA 4.0 (share-alike required)
- **Forum/Reddit:** fair-use (Art. 29 PrAut, academic + anonymized usernames sha1:10)
- **PDF poradniki UOKiK/RF/FK:** urzędowe lub fair-use NGO

⚠ **CC BY-SA share-alike:** Wikipedia component oznacza że downstream MUST cite Wikipedia
i zachować SA license dla derivative. Filter `source_type != 'encyclopedic'` jeśli SA jest
problemem dla downstream use.

## Świadome biases (per R3 thesis chapter v3.2)

1. **Source type bias:** legal_statute + legal_document_pdf dominują względem QA pairs
2. **Finance adjacent bias:** RF FAQ + consumer credit chunks oznaczone `FINANCE_ADJACENT` category (świadomy bias, audytowany w R3)
3. **Recency bias:** post-2014 content dominuje (UPK 2014/827 jako CORE)
4. **Polish-only bias:** wyłączony EN content (świadomy: praca dotyczy polish-specific halu detection)
5. **Court judgment selection bias:** orzeczenia wybierane głównie via Google search (38 unikalnych orzeczeń ms.gov.pl chunked do 534 chunks)
6. **Scope filter bias (v0.5+ z `--filter-policy strict`):** drop ~50% chunks v0.4 per Wariant B krytyki — KPC, Prawo upadłościowe, Prawo bankowe, Usługi płatnicze, finance journalism (bankier/money/infor/gazeta_prawna/prawo.pl/bezprawnik), uchylone ustawy, CHF/franki orzeczenia SN, pure-insurance RF chunks. Świadome zwężenie do consumer-rights core dla probe training distribution. Per-source decyzje + uzasadnienie: `thesis_research/notes/scope_cleanup_decisions_2026-05-16.md`.


## Scope filter audit (policy: `strict`)

Per-source decyzje + uzasadnienie: `thesis_research/notes/scope_cleanup_decisions_2026-05-16.md`.

- **Input chunks (pre-filter):** 17862
- **Kept chunks:** 11000 (61.6%)
- **Dropped chunks:** 6862 (38.4%)

### Drops by reason

| reason | count | wyjaśnienie |
|---|---|---|
| `eli_DU/1964/296` | 2077 | KPC — 96% NIE consumer-specific (procedural law) |
| `eli_DU/2003/535` | 1237 | Prawo upadłościowe — separate domain (future work R8) |
| `eli_DU/2011/1175` | 856 | Usługi płatnicze — regulator-side, NIE consumer-rights |
| `eli_DU/1997/939` | 663 | Prawo bankowe — regulator-bank side, NIE consumer-rights centralne |
| `rf_pure_insurance` | 406 | RF PDF chunk z pure-insurance content (≥3 insurance kw, 0 banking-credit kw) |
| `s6_infor.pl` | 398 | Generic legal/finance journalism (krytyka § Red Flag) |
| `s6_bankier.pl` | 299 | Generic finance journalism, NIE consumer rights (krytyka § Red Flag) |
| `s6_prawo.pl` | 248 | Borderline professional/media |
| `s6_bezprawnik.pl` | 200 | Opinion site, garbage-in-garbage-out risk dla probe |
| `eli_DU/2003/2275` | 188 | UCHYLONA bezp. produktów (replaced by 2024/1221) |
| `eli_DU/2000/271` | 83 | UCHYLONA ochrona praw konsumentów (replaced by UPK 2014/827) |
| `sn_chf_content` | 63 | SN orzeczenie z CHF/franki content (domain shift risk — krytyka § Red Flag #3) |
| `s6_gazetaprawna.pl` | 59 | Borderline media, mała próbka |
| `eli_DU/2002/1176` | 42 | UCHYLONA sprzedaż konsumencka (replaced by UPK 2014/827) |
| `s6_money.pl` | 31 | Generic finance journalism, mała próbka |
| `s6_ing.pl` | 12 | Single-bank sample, większość to CSS scrape artifacts (NIE bank regulations) |


## Note dla v3.1 → v3.2 pivot (DEC-003)

Pierwotny plan był farma+reranker domain. Po pivocie 2026-05-16 na halu detection +
consumer rights. Wszystkie chunki w tym dataset są post-pivot (od 2026-05-16).
v3.1 farma materials zarchiwizowane w `_archive/v3-pharma-reranker/`.
