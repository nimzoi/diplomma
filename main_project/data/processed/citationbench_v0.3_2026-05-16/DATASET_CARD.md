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

# Polish CitationBench (vv0.3)

**Snapshot date:** 2026-05-16
**Domena:** polskie prawa konsumenta + EU consumer law context
**Use case:** citation-grounded RAG hallucination detection benchmark

## Aggregate stats

- **Total unified chunks:** 15790
- **Chunks z cytacjami:** 3143 (19.9%)
- **Avg tresc length:** 997 chars
- **Synthetic halu pairs:** 240 (1 negative + N positive per UOKiK gold pair)

## Source types

| source_type | count |
|---|---|
| legal_statute | 7687 |
| qa_raw | 2945 |
| legal_document_pdf | 2371 |
| legal_ue_directive | 1360 |
| legal_court_judgment | 597 |
| qa_gold | 433 |
| encyclopedic | 342 |
| legal_tsue_judgment | 29 |
| legal_uokik_decision | 26 |

## Sources (top 15)

| source | count |
|---|---|
| isap.sejm.gov.pl | 7687 |
| rf.gov.pl | 2472 |
| eur-lex.europa.eu | 1389 |
| forumprawne.org | 1186 |
| e-prawnik.pl | 948 |
| orzeczenia.ms.gov.pl | 597 |
| reddit.com/r/Polska | 509 |
| uokik.gov.pl | 313 |
| eporady24.pl | 302 |
| federacja-konsumentow.org.pl | 262 |
| prawakonsumenta.uokik.gov.pl | 60 |
| pl.wikipedia.org | 34 |
| decyzje.uokik.gov.pl | 26 |
| gov.pl | 5 |

## Categories (multi-label)

| category | count |
|---|---|
| finance_adjacent | 12279 |
| consumer_contract | 6822 |
| consumer_core | 4142 |
| eu_directive | 2906 |
| other | 2227 |
| consumer_return_refund | 1987 |
| consumer_credit | 1252 |
| consumer_dispute_resolution | 442 |
| court_precedent | 425 |
| tsue_judgment | 331 |
| regulatory_decision | 189 |
| consumer_digital | 164 |
| consumer_telecom | 77 |
| consumer_unfair_practices | 70 |

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

1. **Source type bias:** legal_statute + legal_document_pdf dominują (~70%) względem QA pairs (~25%)
2. **Finance adjacent bias:** RF FAQ (~22% E1 extended) jest finance/banking dominated — oznaczone `FINANCE_ADJACENT` category
3. **Recency bias:** post-2014 content dominuje (UPK 2014/827 jako CORE)
4. **Polish-only bias:** wyłączony EN content (świadomy: praca dotyczy polish-specific halu detection)
5. **Court judgment selection bias:** orzeczenia wybierane głównie via Google search (10 wyroków w E4)

## Note dla v3.1 → v3.2 pivot (DEC-003)

Pierwotny plan był farma+reranker domain. Po pivocie 2026-05-16 na halu detection +
consumer rights. Wszystkie chunki w tym dataset są post-pivot (od 2026-05-16).
v3.1 farma materials zarchiwizowane w `_archive/v3-pharma-reranker/`.
