---
name: Praca dyplomowa context
description: Temat pracy inżynierskiej (post-pivot DEC-003), promotor, RQ, stack, single sources of truth
type: project
originSessionId: 5630a386-3d25-4119-adc8-3884cf68b58c
---

**Praca inżynierska** Magdaleny Sochackiej (s25508), PJATK, Data Science. Promotor: **mgr inż. Piotr Kojałowicz** — klasyczny MLOps mindset, structured technical defensiveness. **NIE magisterska.**

## Temat (v3.2 post-DEC-003 pivot 2026-05-16)

*„Citation-grounded polski RAG z hidden-states hallucination probe — pipeline produkcyjny dla domen krytycznych (studium przypadku: prawa konsumenta)"*

**3 pivots history (audit trail w `thesis_research/decisions/`):**
- v1 administracja → v2 prompt injection → v3 psychiatria → v3.1 farma+reranker (DEC-001/DEC-002, archived) → **v3.2 halu detection + consumer rights (DEC-003 ACTIVE)**
- v3.1 materials → `_archive/v3-pharma-reranker/` (audit trail, NIE używać)

## Pytania badawcze (3 main + 1 supporting, NIE 5)

- **RQ1/H1:** hidden-states halu probe Bielik 11B v3 layer 47 → AUROC ≥0.70 (CI ≥0.60)
- **RQ2/H2:** LLM-as-judge (Bielik / PLLuM / Gemma 3) → kappa ≥0.50 z manual halu labels
- **RQ3/H3:** 3-tier NLI verifier (mDeBERTa → HerBERT → judge LLM) → ≥85% citation precision
- **RQ4 supporting:** Wallat 2025 2-metric framework (faithfulness vs correctness) defensible na Polish

## Active ADRs (`thesis_research/decisions/`)

- **DEC-003** (2026-05-16): pivot na halu detection + consumer rights ACTIVE
- **DEC-004** (2026-05-16): Iter. 0b POC results PARTIAL — T1 mDeBERTa NLI sanity ✅ PASS 80,6 % (lokal CPU); T2/T3/T4 czekają na lab GPU SSH access
- **DEC-005** (2026-05-16): Eval set zwiększony do 200 par gold (60 UOKiK + 140 hand-annotated by autorka) — supersedes konspekt v3.2 "110-160 par"
- DEC-001/DEC-002 SUPERSEDED (psych→farma, ChPL+Ulotka — explicit NIE w v3.2)

## Stack v3.2

- **Generator + probe target:** Bielik 11B v3 (Mistral arch, 50 layers × 4096 hidden, layer 47 dla probe = ⌊0.95×50⌋)
- **Embedder:** BGE-M3 (frozen, multilingual)
- **Tier 1 NLI:** `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (T1 confirmed PASS 80.6% lokal CPU 2026-05-16)
- **Tier 2 fallback:** HerBERT-large + CDSC-E custom fine-tune (CC-BY-NC-SA-4.0 ⚠ NC clause check)
- **Tier 3 ablation:** LLM-as-judge (Bielik / PLLuM / Gemma 3 27B / Claude Haiku)
- **R7 ablation extra:** `knowledgator/gliclass-multilang-ultra` — multi-class native maps na 6 halu types taksonomię
- **Storage:** Qdrant + PostgreSQL + Redis + DVC + MinIO
- **MLOps:** Prefect 3 + MLflow + Optuna + Langfuse + Evidently + Alibi Detect + LGTM stack + Alertmanager
- **Serving + UI:** SGLang + TEI + FastAPI + Docker + GitHub Actions + Gradio (3-tab: Chat / Inspect / Compare)

## Polish CitationBench dataset (post-Wariant B cleanup)

**v0.6 (2026-05-16):** 11,000 unified chunks + 5,402 halu pairs (5/5 typów balanced)

Source types (z `chunk_filter.py` strict policy):
- legal_statute 2,541 (UPK + KC art. 535-581 + Konstytucja art. 76 + 16 ustaw konsumenckich)
- qa_raw 2,945 (forum questions e-prawnik/forumprawne/Reddit/eporady24)
- legal_document_pdf 1,965 (E4 UOKiK/RF/FK poradniki)
- legal_ue_directive 1,360 (8 dyrektyw konsumenckich PL z EUR-Lex)
- encyclopedic 1,167 (Wikipedia 342 + ECC/UODO/KNF/UKE/URE/Federacja)
- legal_court_judgment 597 (38 ms.gov.pl + 121 SN orzeczenia po dedup)
- qa_gold 433 (60 UOKiK + 373 RF FAQ z citations)
- legal_tsue_judgment 29 (Dziubak C-260/18 + Kásler C-26/13 + Bank BPH + 26 innych)
- legal_uokik_decision 26 (decyzje Prezesa UOKiK)

Plus 1.4 GB raw archive (118 PDFs + 4,763 HTMLs + 21 _archive/ dirów + sha256 manifests).

## Single sources of truth (post-pivot — read order priorities)

P0 (zawsze first w nowej sesji):
- `D:\diplomma\CLAUDE.md` — root project state v3.2
- `thesis_research/02_konspekt_v3.2_skeleton.md` — 12 sekcji konspekt aktualny
- `thesis_research/decisions/DEC-003_pivot-na-halu-detection.md` — pivot rationale
- `thesis_research/decisions/DEC-004_iter0b_poc_results.md` — POC sign-off framework

P1 (do work):
- `thesis_research/research/halu_detection_sota_2024_2026.md` — SOTA halu (Mu-SHROOM polish gap, AggTruth, Wallat, Farquhar)
- `thesis_research/research/nli_models_2026_update.md` — gliclass + dleemiller + mDeBERTa verify
- `thesis_research/notes/sources_z_v3.1_do_reuse_w_v3.2.md` — bibliography mining (24/31 v3.1 refs reusable + ~80 modern 2024-2026)
- `thesis_research/notes/KRYTYCZNA_ocena_scope_2026-05-16.md` — devil's advocate scope review
- `thesis_research/notes/scope_cleanup_decisions_2026-05-16.md` — per-source DROP/KEEP audit (Wariant B)
- 17 research files w `thesis_research/research/` (E1-E4 + S1-S7 outputs + nli_models_2026)

## Iteracje plan (po POC PASS)

- **Iter. 0b POC** (in progress): 4 kill-criteria tests w `main_project/iter0b_poc/`
  - T1 mDeBERTa NLI sanity ✅ **PASS 80.6%** (lokal CPU 2026-05-16)
  - T2 Outlines+Bielik diakrytyki — czeka na lab GPU
  - T3 PyTorch hooks Bielik layer 47 — czeka na lab GPU
  - T4 Lab GPU verify — Magda SSH access
- **Iter. 1:** RAG MVP (Bielik + Qdrant + LlamaIndex + 3-tier NLI + Gradio 3-tab) + halu probe layer 47 training
- **Iter. 2:** Continuous improvement loop (3 cykle retraining z drift triggers)
- **Iter. 3:** Observability stack (Langfuse + Evidently + Alibi Detect + LGTM + Alertmanager)
- **Iter. 4:** Serving + CI/CD (SGLang + TEI + FastAPI + Docker + GH Actions)
- **Iter. 5:** Manual gold standard 200 par (Magdy weekend hyperfocus) + 4-way verifier ablation (mDeBERTa + HerBERT + gliclass + LLM-judge)
- **Iter. 6:** 6-poziomowa error analysis + ablations A1-A4 + RAGAS faithfulness
- **Iter. 7-8:** R1-R8 writing (świeżo, NIE z pre-cleanup drafts) + PJATK formatting + citation pass

Total estimate: 6-10 tygodni real engineering po POC PASS.

## Scope IN/OUT (per CLAUDE.md)

**IN (4 komponenty central):**
- Hidden-states halu probe + post-hoc citation grounding pipeline (NLI-based)
- Polish consumer rights RAG demo (Bielik + Qdrant + LlamaIndex)
- Continuous improvement loop probe (cykle retreningu z drift triggers)
- Observability stack + 3 publishable artefakty na HF (dataset + probe + verifier) + Gradio 3-tab

**OUT:** doradztwo prawne (informational, NIE legal advice — explicit disclaimer), reranker fine-tuning (passé), farma domain (DEC-003 supersession), LLM full fine-tuning (probe NIE LoRA), real-time production deployment, cross-language transfer, reranker dla consumer rights.

## 5-wymiarowa kontrybucja (defense scaffolding R8)

Każdy wymiar broni się niezależnie (jeśli H1 odpada, 2-5 stoją):
1. **Metodologiczny** — pierwszy publicznie udokumentowany polish hallucination detection methodology
2. **Inżynierski** — reprodukowalny pipeline citation-grounded RAG + halu probe + verifier
3. **Artefaktowy** — 3 publishable na HuggingFace (dataset + probe model + verifier model)
4. **Eksperymentalny** — porównanie hidden-states probe vs multilingual baselines (Lynx, HHEM)
5. **Korpusowy** — pierwszy polish CitationBench dataset z deterministic citation grounding (ISAP-based)

## Honest motivation framing (CRITICAL — Wzorzec 7 CLAUDE.md)

**NIE overstating:** ❌ „LLM nie umie polish prawa" / „brak prac w temacie"
**Defensible:** ✅ „polish-specific halu detection nie zostało publicznie udokumentowane (Mu-SHROOM 2025 pominął polski) + production RAG dla legal domain wymaga citation grounding + halu control"

Polish-first first-mover RISK MEDIUM (Wrocław Tech AggTruth English-only, mGarbowski/llm-projekt = direct prior art Bielik 1.5B → MUST cite + differentiation w R8).

## Why

Speed-run mode + 3 pivots history = każda decyzja musi być audit-trailed (ADR) + falsyfikowalna (RQ z explicit thresholds) + defensive scaffolded (5 wymiarów wkład niezależnie). Engineering layers (Gradio demo, observability, drift detection) wzmacniają R5 architectural breadth bez scope creep w RQ.

## How to apply

Referencja przy każdej decyzji projektowej — sprawdź czy nie koliduje z DEC-003 + 02_konspekt_v3.2_skeleton + scope IN/OUT. Updates wymagają nowego ADR. NIE wracać do reranker fine-tuning, farma, ChPL/Ulotka — DEC-003 explicit superseded DEC-001/002.
