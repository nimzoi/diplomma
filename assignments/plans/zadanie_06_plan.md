# Plan zadania 06 — Modele ML (R6)

**Institutional source:** `assignments/06.md` (Task 06, 10 pkt)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/07-Baseline-Models.md` (Assignment 7) + `08-Target-Model-and-Optimization.md` (Assignment 8)
**Mapuje na rozdział:** R6 Modele ML
**Iteracja realizacji:** 2 (pipeline core + cykl 1 + ablations A1-A4) + 3 (cykle 2+3) + 4 (RQ5 cross-register) + 7 (writing)

## 1. Czego instytucjonalnie wymaga Task 06

Dla każdego modelu **konsystentna 8-elementowa struktura** (Task 06 sekcja 0):
1. Problem formulation (input/output/task type/loss/metrics + uzasadnienie metryk)
2. Data representation post-preprocessing (shape, type, normalizacja)
3. Model selection rationale (theoretical + practical reasons)
4. Model architecture / structure (layers, components, diagrams)
5. Hyperparameters + tuning method (grid/random/bayesian/optuna)
6. Training setup (optimizer, batch, epochs, split, hardware, early stopping)
7. Evaluation setup (validation strategy, baselines, metrics)
8. Model interpretation & diagnostics (feature importance, error analysis prep)

W naszej pracy modele: **polish-reranker-roberta-v3** (target, fine-tuned) + **BGE-M3** (frozen embedder) + **Bielik 11B v3** (generator) + `<judge_model>` (LLM-as-judge — wybór z {Bielik 11B v3 / Gemma 3 27B / Qwen 3 32B / Claude Haiku 4.5} w Iteracji 0)

## 2. Czego wymaga PRO-D-THESIS Assignment 7 (Baseline) + 8 (Target Model)

**Assignment 7 (2-4 stron):**
- A. Definition + justification baselines (≥1 simple + ≥1 classical ML)
- B. Controlled training protocol (identical splits/preprocessing, no leakage, fixed seeds)
- C. Hyperparameter strategy (defaults vs tuned, justified)
- D. Performance evaluation (structured tables, metric definitions, cross-val mean ± std)
- E. Critical interpretation (best model + alignment z literatury + practical significance)

**Assignment 8 (3-5 stron):**
- A. Justification target model selection (literature + baseline gap)
- B. Architecture + configuration (input/output interface, core hyperparams)
- C. Optimization strategy (search method, space, computational constraints, early stopping)
- D. Generalization + overfitting analysis (train vs val curves, fold stability, sensitivity)
- E. Comparative evaluation against baselines (absolute + relative improvement + cost)
- F. Interpretation re research question (does target support hypothesis?)

## 3. Jak to wygląda w naszym v3.1

### Sekcja 6.1: Reranker target model (centralny ML contribution)

**polish-reranker-roberta-v3** — fine-tuned cross-encoder, ~360M params, RoBERTa-large.

- **Problem formulation:** pairwise ranking (query, passage_A, passage_B) → preferred passage
- **Loss:** preference loss (margin ranking lub Plackett-Luce — wybór w cyklu 1)
- **Hyperparameters z Optuna search:**
  - learning rate {1e-5, 3e-5, 5e-5}
  - batch size {16, 32}
  - epochs {2, 3, 4}
  - max_length {512, 768}
  - warmup ratio {0.06, 0.1}
- **Training:** AdamW optimizer, cosine schedule, early stopping na val nDCG@10, **3 random seeds, mean ± std**
- **Hardware:** SP7 GPU H200 (transfer infrastructure z poprzedniej pracy v1)

### Sekcja 6.2: 4 baselines (Assignment 7 wymóg)

| # | Baseline | Type | Rationale |
|---|---|---|---|
| 1 | BM25 (Pyserini) | Lexical sparse | Foundational IR baseline; literature standard (Robertson 2009) |
| 2 | Dense BGE-M3 alone | Embedding-only | Czy embedder sam wystarcza bez reranker? |
| 3 | Base polish-reranker (no fine-tune) | Off-the-shelf reranker | Strongest baseline — test fine-tuning gain (per BEIR Thakur 2021) |
| 4 | Chunking variants | Same reranker × różne chunking | Czy chunking strategy matters dla pharma corpus? |

**Controlled protocol:** identical splits + preprocessing + fixed seeds dla wszystkich 4 baselines + target.

### Sekcja 6.3: LLM-as-judge — 4 protokoły (z konspekt II.7)

1. **Pairwise** — główny sygnał treningowy
2. **Pointwise** — sanity check spójności
3. **Faithfulness** — end-to-end RAG metric (Bielik generation evaluated)
4. **Cross-register pair scoring (NEW dla RQ5)** — dwa wymiary: semantic match (0-5) + register appropriateness (0-5)

`<judge_model>` wybrany w Iteracji 0 z kandydatów {Bielik 11B v3 / Gemma 3 27B / Qwen 3 32B / Claude Haiku 4.5} na podstawie pilot Cohen's kappa porównania na 30 par cross-register.

### Sekcja 6.4: Hard negatives strategy (z konspekt II.4.6)

4-poziomowa strategia (Karpukhin et al. 2020 DPR-style):
- **L1 (15%)** Easy: different ATC class
- **L2 (50%)** Medium: same class, different drug
- **L3 (30%)** Hard: same drug, different section
- **L4 (5%)** Very hard: cross-register confusion (RQ5-specific)

Total scale: ~145k preference quadruplets (positive + 3 negatives per quad).

### Sekcja 6.5: Ablations A1-A4 (Defense scaffolding pkt 1)

| # | Ablation | Cel diagnostyczny |
|---|---|---|
| A0 | baseline | Pełen pipeline reference |
| A1 | judge → random preferences | Czy signal quality matters? Random pairs daje gain → judge nic nie wnosi |
| A2 | judge → Bielik vs `<judge_model>` | Cross-model robustness; H2 conclusions per judge |
| A3 | corpus → psych-only N05/N06 vs full pharma | Domain breadth effect (DEC-001 świadoma decyzja) |
| A4 | ChPL-only vs ChPL+Ulotka training | Register diversity (motywacja dla RQ5 RQ5-specific) |

Każda ablacja = osobny MLflow run, osobny wynik do dyskusji w R7.

### Sekcja 6.6: Cross-register evaluation setup (RQ5)

Z konspekt II.3.3 + DEC-002 + II.4.6:
- Test query set: 1800 cross-register pairs (900 lay→pro + 900 pro→lay)
- Gold standard: deterministic alignment przez `productID` z URPL RPL
- **Metryki PER DIRECTION**: accuracy@10 + MRR@10 osobno lay→pro vs pro→lay
- Direction asymmetry gap `Δ_dir = |MRR(lay→pro) − MRR(pro→lay)|`
- A4 ablation specific dla cross-register test set

## 4. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Outline R6 | Proponuje 6 podsekcji per Task 06 8-element template | Sign-off |
| 2 | Sekcja 6.1 Target reranker | Drafts 8-element opis (problem/data/architecture/hyperparams/training/eval) | Reviews accuracy |
| 3 | Sekcja 6.2 Baselines | Drafts 4 baselines + controlled protocol + leakage prevention statement | Reviews fairness |
| 4 | Sekcja 6.3 LLM-judge protokoły | Drafts 4 protokoły + judge selection methodology (kandydaci + kappa) | Reviews |
| 5 | Sekcja 6.4 Hard negatives | Drafts 4-poziomową strategy + DPR literature anchor | Reviews |
| 6 | Sekcja 6.5 Ablations A1-A4 | Drafts każdą ablację z motywacją + expected outcome | Reviews logic |
| 7 | Sekcja 6.6 Cross-register setup | Drafts RQ5 evaluation z MRR per direction + A4 ablation specific | Reviews |
| 8 | Sekcja 6.7 Interpretation guidelines | Drafts interpretation framework (do R7 expansion) | Reviews |
| 9 | Citation pass | `/citations` audit literatury z R2 references | Reviews |
| 10 | Writing rules check | 3rd person, no time-proofing, consistent terminology z R2+R5 | Final read-through |

**Workflow note:** sekcje 6.2-6.6 mogą być drafted paralelnie po sign-off na outline 6.1.

## 5. Co musimy znaleźć / przygotować

### Referencje literaturowe (z R2)
- DPR (Karpukhin 2020) — hard negatives strategy
- BEIR (Thakur 2021) — domain adaptation cross-encoder
- Optuna framework reference (Akiba 2019)
- polish-reranker-roberta-v3 model card + paper
- Sentence-transformers / cross-encoders library
- BGE-M3 paper (Chen 2024)

### Artefakty
- **Tabela 6.1:** Target reranker hyperparams (z Optuna)
- **Tabela 6.2:** 4 baselines summary
- **Tabela 6.3:** Judge selection comparison (kandydaci × pilot kappa)
- **Tabela 6.4:** Hard negatives 4-level strategy z proporcjami
- **Tabela 6.5:** Ablations A1-A4 design
- **Tabela 6.6:** Cross-register evaluation setup
- **Figura 6.1:** Training pipeline overview (mini-version z R5 Figure 5.4)
- **Figura 6.2:** Hard negatives sampling strategy diagram

### Pre-conditions
- Iteracja 0: judge wybrany z {Bielik/Gemma 3/Qwen 3/Claude Haiku}
- Iteracja 1: corpus + 200 par gold standard ready
- Iteracja 2: pipeline core działający + cykl 1 trained

## 6. Writing rules application

- Reguła 1 classic structure: 6 podsekcji w kolejności per Task 06 template
- Reguła 5 consistent table formatting: 6 tabel R6 z jedną konwencją (Component | Value | Rationale)
- Reguła 6 evidence-conclusion linking: każda decyzja modelowania cytuje literaturę z R2

## 7. Defense scaffolding application

**Wszystkie 3 mikro-podszepty BAKED IN tu:**

1. **Ablation studies A1-A4** — sekcja 6.5 explicit + każdy = osobny MLflow run
2. **Kategoryczna error analysis taxonomy** — mention w sekcji 6.7 (full development w R7)
3. **5-wymiarowa kontrybucja** — implicit: każdy z 4 ablations + cross-register = niezależny eval axis

## 8. Acceptance checklist

- [ ] 6 podsekcji w kolejności per Task 06 template (problem/data/architecture/hyperparams/training/eval/interpretation)
- [ ] Target reranker z pełnym 8-elementowym opisem
- [ ] 4 baselines explicit + controlled protocol
- [ ] 4 judge protocols z `<judge_model>` decyzją + uzasadnieniem
- [ ] Hard negatives 4-level strategy + DPR anchor
- [ ] 4 ablations A1-A4 explicit z motywacją
- [ ] Cross-register setup z MRR per direction
- [ ] Wszystkie hyperparams w tabeli z search space + best value
- [ ] 3 random seeds + mean ± std w protokole

## 9. Risks / common pitfalls

- ❌ Promotor MLOps mindset → daj szczegóły training infrastructure (SP7 H200, SGLang serving, batch sizes per GPU memory)
- ❌ Brak controlled training protocol → identyczne splits + preprocessing + seeds w każdej tabeli (Assignment 7 strict wymóg)
- ❌ Phantom citations literatury (Optuna, BEIR, DPR) → citation-checker przed submission
- ❌ Over-formalizm metryk w R6 → progi statystyczne OK w R6 (eval methodology miejscem), narrative descriptive też potrzebny
- ❌ Brak ablations → Defense scaffolding **wymaga** A1-A4 w cyklu 1
- ❌ Judge selection bez uzasadnienia → kappa pilot results muszą być explicit w sekcji 6.3
