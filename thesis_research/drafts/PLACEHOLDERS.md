# PLACEHOLDERS registry — 48h-draft R1-R8

**Cel:** rejestr wszystkich `{{SCREAMING_SNAKE_CASE}}` placeholders w `drafts/R*.md`. Po Iter. 1-6 (post-assignments-sprint) → regex replace pass / `tools/fill_placeholders.py` zamienia w jednym przebiegu.

**Konwencja:** `{{NAZWA_SNAKE}}` — używaj spójnych nazw między rozdziałami. Każdy nowy placeholder dodawaj tutaj z (a) opis co oznacza, (b) expected source (skrypt/iteracja), (c) plik(i) gdzie używany.

**Status legend:** ⏳ pending | ✅ FILLED | ❌ DROPPED (decision: usunięto z rozdziałów)

---

## Probe metryki (RQ1)

| Placeholder | Opis | Source | Status | Files |
|---|---|---|---|---|
| `{{PROBE_AUROC_PRIMARY}}` | AUROC linear probe na in-domain eval set | Iter. 1 probe training output | ⏳ | R06, R07, R08 |
| `{{PROBE_AUROC_CI_LOW}}` | Bootstrap CI 95% lower bound | Iter. 1 | ⏳ | R06, R07 |
| `{{PROBE_AUROC_CI_HIGH}}` | Bootstrap CI 95% upper bound | Iter. 1 | ⏳ | R06, R07 |
| `{{PROBE_AUROC_VERDICT}}` | "potwierdza" / "częściowo potwierdza" / "obala" H1 | Iter. 1 (po CI) | ⏳ | R07, R08 |
| `{{PROBE_TARGET_SIZE_DECIDED}}` | Bielik 11B vs 1.5B/3B fallback z A2 ablation | Iter. 2 A2 | ⏳ | R06 |
| `{{PROBE_LAYER_FINAL}}` | Confirmed layer 47 lub alternative z multi-layer ablation | Iter. 2 | ⏳ default 47 | R06 |

## NLI verifier (RQ3)

| Placeholder | Opis | Source | Status | Files |
|---|---|---|---|---|
| `{{TIER1_NLI_ACCURACY}}` | mDeBERTa accuracy na test set | DEC-004 T1 PASS | ✅ 80.6% (n=93) | R06, R07 |
| `{{TIER1_NLI_CONTRADICTED_PRECISION}}` | Per-class contradicted P | DEC-004 T1 | ✅ 1.000 | R06, R07 |
| `{{TIER1_NLI_ENTAILED_RECALL}}` | Per-class entailed R | DEC-004 T1 | ✅ 0.706 | R06, R07 |
| `{{TIER2_HERBERT_F1}}` | HerBERT-large + CDSC-E fine-tune jeśli wykonane | Iter. 5 (opcjonalne) | ⏳ | R06 |
| `{{TIER3_LLM_JUDGE_KAPPA}}` | Cohen's kappa LLM-judge vs manual (RQ4) | Iter. 2 A3 ablation | ⏳ | R06, R07 |

## Citation grounding (RQ2 Wallat 2-metric)

| Placeholder | Opis | Source | Status | Files |
|---|---|---|---|---|
| `{{CITATION_FAITHFULNESS_PRECISION}}` | H2a — citation→retrieved precision | Iter. 1 RAG MVP eval | ⏳ | R07 |
| `{{CITATION_CORRECTNESS_PRECISION}}` | H2b — linked→supports claim precision | Iter. 1 + manual verify | ⏳ | R07 |

## Continuous improvement (RQ3)

| Placeholder | Opis | Source | Status | Files |
|---|---|---|---|---|
| `{{LOOP_CYCLE1_AUROC}}` | Probe AUROC po cyklu 1 retraining | Iter. 3 | ⏳ | R07 |
| `{{LOOP_CYCLE2_AUROC}}` | Po cyklu 2 | Iter. 3 | ⏳ | R07 |
| `{{LOOP_CYCLE3_AUROC}}` | Po cyklu 3 | Iter. 3 | ⏳ | R07 |
| `{{LOOP_CONVERGENCE_VERDICT}}` | "konwerguje (plateau po cyklu 2)" / "monotonic improvement" / "regresja" | Iter. 3 | ⏳ | R07, R08 |

## Ablations A1-A4 (R7)

| Placeholder | Opis | Source | Status | Files |
|---|---|---|---|---|
| `{{ABLATION_A1_SEMANTIC_ENTROPY_AUROC}}` | Farquhar 2024 baseline | Iter. 2 A1 | ⏳ | R07 |
| `{{ABLATION_A2_SMALLER_BIELIK_AUROC}}` | Probe na 1.5B/3B vs 11B | Iter. 2 A2 | ⏳ | R07 |
| `{{ABLATION_A3_LLM_JUDGE_F1}}` | LLM-judge vs mDeBERTa | Iter. 2 A3 | ⏳ | R07 |
| `{{ABLATION_A4_GENERATION_TIME_FAITHFULNESS}}` | Outlines structured vs post-hoc | Iter. 2 A4 (pending T2 lab GPU) | ⏳ | R07 |
| `{{ABLATION_TIER0_GLICLASS_F1}}` | gliclass-multilang-ultra (R7 bonus) | Iter. 5 4-way verifier comp | ⏳ | R07 |

## Error analysis 6-poziomowa (R7)

| Placeholder | Opis | Source | Status | Files |
|---|---|---|---|---|
| `{{ERROR_FACTUAL_FAB_PCT}}` | % błędów typu factual_fabrication | Iter. 3 post-loop | ⏳ | R07 |
| `{{ERROR_ENTITY_CONFUSION_PCT}}` | % entity_confusion | Iter. 3 | ⏳ | R07 |
| `{{ERROR_TEMPORAL_DRIFT_PCT}}` | % temporal_drift | Iter. 3 | ⏳ | R07 |
| `{{ERROR_NEGATION_FLIP_PCT}}` | % negation_flip | Iter. 3 | ⏳ | R07 |
| `{{ERROR_PARAGRAPH_MIS_CITATION_PCT}}` | % paragraph_mis_citation | Iter. 3 | ⏳ | R07 |
| `{{ERROR_AMBIGUOUS_CLAIM_PCT}}` | % ambiguous_claim (acceptable) | Iter. 3 | ⏳ | R07 |

## Eval set sizes

| Placeholder | Opis | Source | Status | Files |
|---|---|---|---|---|
| `{{TEST_N}}` | Liczba par w primary eval set | Magda commitment 200 (60 UOKiK + 140 hand-annotated) | ✅ 200 par | R06, R07 |
| `{{SECONDARY_EVAL_N}}` | Silver labels secondary eval | Iter. 1 (~1000) | ✅ ~1000 par | R07 |

## Infrastructure

| Placeholder | Opis | Source | Status | Files |
|---|---|---|---|---|
| `{{REPO_COMMIT_HASH}}` | Git commit hash dla reprodukcji bit-identical v0.6 | post-final commit R3 | ⏳ | R03 |

## Baselines (R7 comparison)

| Placeholder | Opis | Source | Status | Files |
|---|---|---|---|---|
| `{{BASELINE_RANDOM_AUROC}}` | Random baseline | constant | ✅ 0.50 | R06, R07 |
| `{{BASELINE_LYNX_8B_AUROC}}` | Lynx multilingual 8B na polish corpus | Iter. 2 baseline run | ⏳ | R07 |
| `{{BASELINE_HHEM_AUROC}}` | HHEM 2.x baseline | Iter. 2 | ⏳ | R07 |

## Dataset stats (z DATASET_CARD v0.6 — already FILLED, NIE używać jako placeholders)

Wartości real (NIE placeholder):
- ✅ Total chunks: **11,000** (z 17,862 → drop 38.4% Wariant B)
- ✅ Halu pairs: **5,402** (balanced 5/5 typów)
- ✅ Source types: 9 (legal_statute 2,541 + qa_raw 2,945 + legal_document_pdf 1,965 + legal_ue_directive 1,360 + encyclopedic 1,167 + legal_court_judgment 534 + qa_gold 433 + legal_tsue_judgment 29 + legal_uokik_decision 26)
- ✅ Halu distribution per type: factual_fabrication 1,620 / entity_confusion 985 / negation_flip 467 / paragraph_mis_citation 427 / temporal_drift 343 / neg (entailed) 1,560

## Citation refs (placeholder format `[CYT: Author Year topic]`)

Lista canonical refs (rozszerzaj per rozdział, źródło: `thesis_research/research/*.md`):

- `[CYT: Lewis 2020 RAG NeurIPS]` — RAG foundation
- `[CYT: Karpukhin 2020 DPR EMNLP]` — dense retrieval
- `[CYT: Chen 2024 BGE-M3 arXiv]` — embedder
- `[CYT: Farquhar 2024 Nature semantic entropy]` — halu detection foundation
- `[CYT: Balcells 2025 layer 47 hallucination probes]` — probe layer selection
- `[CYT: Dubanowska 2025 EMNLP OOD probe limits]` — OOD AUROC limitations
- `[CYT: Wallat 2025 ICTIR citation 2-metric arXiv:2412.18004]` — faithfulness vs correctness
- `[CYT: Mu-SHROOM 2025 SemEval Task 3]` — polish gap evidence
- `[CYT: AggTruth Wrocław Tech 2025 ICCS arXiv:2506.18628]` — English-only competitor
- `[CYT: Zheng 2023 NeurIPS LLM-as-judge MT-Bench]` — LLM-judge methodology
- `[CYT: Cohen 1960 kappa]` + `[CYT: Landis Koch 1977 kappa interpretation Biometrics]`
- `[CYT: Ociepa 2025 Bielik v3 APT4 tokenizer arXiv:2604.10799]` — Bielik architecture
- `[CYT: Kocoń 2025 PLLuM arXiv:2511.03823]` — Polish LLM ecosystem
- `[CYT: MoritzLaurer mDeBERTa-v3-base-xnli HF model card]` — Tier 1 verifier
- `[CYT: Mirage of Halu Detection EMNLP 2025]` — eval methodology critique

Phantom watchlist (NIE cytuj):
- ❌ `sdadas/polish-nli` — NIE istnieje na HF (confirmed 2026-05-16)
- ❌ `finecat-nli-l` — license UNSPECIFIED, NIE używać dla HF publication
