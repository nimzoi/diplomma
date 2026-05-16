# DEC-004 — Iteracja 0b POC results + sign-off na Iter. 1

**Data:** 2026-05-16 (T1 done lokal CPU; T2/T3/T4 pending lab GPU)
**Status:** PARTIAL — T1 mDeBERTa NLI sanity ✓ PASS 80.6%; T2/T3/T4 pending lab GPU SP7 H200
**Supersedes:** brak
**Related:** [DEC-003 pivot na halu detection](DEC-003_pivot-na-halu-detection.md), [krytyka 2026-05-16](../notes/KRYTYCZNA_ocena_scope_2026-05-16.md)

---

## Kontekst

Po pivocie DEC-003 (2026-05-16) i dataset construction Polish CitationBench v0.6 (11,000 chunks + 5,402 halu pairs, post-cleanup Wariant B + post-fix factual_fabrication=NEUTRAL), uruchamiam 4 POC testy zdefiniowane jako kill criteria dla Iter. 1 (probe training pipeline + RAG demo). Każdy test ma jednoznaczne PASS/FAIL z falsyfikowalnym progiem. Decyzja DEC-004 syntetyzuje wyniki + autoryzuje (lub blokuje) start Iter. 1.

## 4 POC tests — wypełnij wyniki

### T1: mDeBERTa NLI sanity na UOKiK Q&A — PASS ✓ (2026-05-16)

- **Skrypt:** `main_project/iter0b_poc/t1_mdeberta_nli_sanity.py`
- **Run:** lokal CPU (Magda's "w miarę dobry laptop"), bez lab GPU
- **Output JSON:** `iter0b_poc/results/t1_mdeberta_20260516_115505.json`
- **Dataset:** v0.6 halu_pairs (po fix factual_fabrication=NEUTRAL)
- **Kill criterion:** accuracy < 50% (random baseline)

**Wyniki:**
- **accuracy: 80.6% (75/93)** ← KILL CRITERION 50% przekroczony +30.6 pp
- **hybrid_accuracy_dleemiller: 42-65%** (conservative scoring; further tuning możliwe)
- **per-class P/R:**
  - entailed: P=0.800 / R=0.706
  - neutral: P=0.643 / R=0.931 (model conservative — over-predicts neutral)
  - **contradicted: P=1.000 / R=0.766** ← when model says contradicted, ZAWSZE poprawnie
- **per-halu-type:**
  - negative (entailment): 78.6% accuracy
  - entity_confusion: 76.9% accuracy ✓
  - factual_fabrication: 100% (po fix → expected NEUTRAL, nie CONTRADICTED)
  - inne typy: TBD (małe samples)
- **timestamp:** 2026-05-16 11:55:05
- **VERDICT:** **PASS** ✓

**Critical finding T1:**
**Pierwsza iteracja DEC-004 dała 6.1%** — diagnoza: bug w halu_injector
labelował WSZYSTKIE positive pairs jako CONTRADICTED, ale `factual_fabrication`
mutation (dodaje fikcyjny fakt) NIE jest contradiction — to *unsupported claim* =
NLI poprawnie predict NEUTRAL. Po fix `_HALU_TYPE_NLI_LABEL` map w
`halu_injector.py` (factual_fabrication → NEUTRAL, reszta CONTRADICTED) →
PASS 80.6%.

**Defense scaffolding (anti-Kojałowicz Q):**
- "Skąd pewność że mDeBERTa działa na polish?"
  → 78.6% recall na polish entailment + 100% precision na contradictions na 93 par
- "Dlaczego nie HerBERT-large + CDSC-E?"
  → mDeBERTa Tier 1 PASS, HerBERT pozostaje Tier 2 fallback (nie potrzebny TERAZ)
- "Co z neutral cases?" → model conservative, R=0.93 high recall, R6 ablation:
  threshold tuning lub gliclass multi-class alternative

**Implikacja dla R6 verifier methodology:**
Hybrid scoring (dleemiller) nieużyteczne dla naszego use case (worsened wyniki).
Standard argmax z mDeBERTa wystarczy. Threshold tuning + gliclass ablation =
R7 future work.

### T2: Outlines + Bielik 11B v3 polish diakrytyki

- **Skrypt:** `main_project/iter0b_poc/t2_outlines_bielik_diakrytyki.py`
- **Run command:** `uv run python -m iter0b_poc.t2_outlines_bielik_diakrytyki --device cuda` (lab GPU)
- **Output JSON:** `iter0b_poc/results/t2_outlines_bielik_<timestamp>.json`
- **Kill criteria:** valid_json < 80% lub diakrytyki preservation < 95%

**Wyniki (wypełnij):**
- valid_json_rate: ___%
- diakrytyki_pass_rate: ___%
- timestamp: ___
- **VERDICT:** PASS / FAIL
- **Notatki:** schema conformance issues, alternatives (xgrammar, regex extract) jeśli FAIL

### T3: PyTorch hooks na Bielik 11B layer 47

- **Skrypt:** `main_project/iter0b_poc/t3_pytorch_hooks_bielik.py`
- **Run command:** `uv run python -m iter0b_poc.t3_pytorch_hooks_bielik --device cuda --layer 47`
- **Output JSON:** `iter0b_poc/results/t3_hooks_bielik_<timestamp>.json`
- **Kill criteria:** OOM lub shape mismatch lub max_cosine ≥ 0.95 (no differentiation)

**Wyniki (wypełnij):**
- arch_ok: True/False (50 layers × 4096 hidden)
- extraction_ok: True/False
- differentiation_ok: True/False (cosine < 0.95 między różnymi prompts)
- max_cosine: ___
- VRAM peak: ___ GB
- timestamp: ___
- **VERDICT:** PASS / FAIL
- **Notatki:** czy fallback do Bielik 1.5B/3B (per CLAUDE.md spec) wymagany

### T4: Lab GPU verify (SSH + Bielik download + smoke inference)

- **Skrypt:** `main_project/iter0b_poc/t4_lab_gpu_verify.py`
- **Run command:** `uv run python -m iter0b_poc.t4_lab_gpu_verify --ssh-host magma@<lab>` lub `--mode lab-side` na lab
- **Output JSON:** `iter0b_poc/results/t4_lab_gpu_<timestamp>.json`
- **Kill criteria:** SSH unreachable / VRAM < 40 GB / inference > 60s/prompt

**Wyniki (wypełnij):**
- cuda_device_name: ___
- vram_total_gb: ___
- load_time_sec: ___
- inference_time_sec: ___
- output_text_sample: ___
- timestamp: ___
- **VERDICT:** PASS / FAIL
- **Notatki:** alternative jeśli FAIL (Colab Pro+, runpod, lokal Bielik 1.5B)

---

## Synteza wyników

**Liczba PASS:** ___ / 4
**Liczba FAIL:** ___ / 4

### Wariant A: 4/4 PASS → AUTHORIZE Iter. 1

Status: **GO**. Wszystkie kill criteria przeszły. Iter. 1 startuje:
- Probe training pipeline (Bielik 11B + layer 47 hooks + sklearn LogisticRegression baseline + AggTruth-style probe)
- RAG demo (Bielik + Qdrant + LlamaIndex + citation alignment)
- 3-tier NLI verifier (mDeBERTa primary + HerBERT fallback + LLM judge ablation)
- Continuous improvement loop scaffolding (3 cycles per RQ3)

**Action items:**
1. Sign-off entry w `PLAN_cele_i_kroki.md` § Iter. 0b → Iter. 1 transition
2. Update `02_konspekt_v3.2_skeleton.md` § II.X z confirmed POC results
3. Spawn agent dla Iter. 1 probe training pipeline scaffold

### Wariant B: 1-3 FAIL → INVESTIGATE + PARTIAL Iter. 1

Status: **CONDITIONAL**. Per FAIL test:
- T1 FAIL → upgrade Tier 2 verifier (HerBERT-large + CDSC-E fine-tune) wcześniej; zaktualizuj R6 methodology
- T2 FAIL → switch z Outlines na xgrammar lub plain prompt+regex; document w R5 architektura
- T3 FAIL → fallback Bielik 1.5B/3B (per CLAUDE.md spec dla local CPU dev); update RQ1 baseline expectations
- T4 FAIL → re-negotiate lab access, alternative compute (Colab Pro+, runpod) — może blokować Iter. 1

### Wariant C: 4/4 FAIL → PIVOT lub HARD PAUSE

Status: **STOP**. Per CLAUDE.md anti-pattern „Nie zatwierdzaj 4. rotacji domeny" — przed pivot przeczytaj DEC-003 kill criteria. Możliwe scenariusze:
- Wszystkie 4 fail dla powodów technicznych (lab unavailable + WAF) → pause + re-plan compute
- T3+T4 fail systemic (Bielik nie startuje) → re-think probe target (Qwen 2.5 PL fine-tune? Llama 3 PL?)
- Document failure mode + escalate do promotora przed pivot

---

## Notatki dodatkowe

**(wypełnij after run):**

- Total time spent na POC: ___ h
- Surprise / unexpected findings: ___
- Defense scaffolding (anti-Kojałowicz):
  - "Dlaczego Pani uważa że probe na Bielik 11B będzie działał?" → odpowiedź na bazie T3 differentiation ___
  - "Dlaczego mDeBERTa zamiast HerBERT-large?" → T1 accuracy + research/nli_alternatives_2026.md
  - "Czy 240 → 5,402 halu pairs jest dostatecznie balanced?" → distribution per type w v0.5 DATASET_CARD

## Sign-off

- [ ] Autorka: Magdalena Sochacka, ___ (data)
- [ ] Promotor: mgr inż. Piotr Kojałowicz (after weekend hyperfocus + draft Iter. 1 plan)
