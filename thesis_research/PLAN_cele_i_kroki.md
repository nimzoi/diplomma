# Plan: cele + kroki

**Status:** *operational document, daily reference dla autorki*. Iteration-based, NIE czasowy.
**Data:** 2026-05-16 (evening — post-Wariant B + T1 PASS + v0.6)
**Powiązane:** `02_konspekt_v3.2_skeleton.md` (academic spec) · `EXPLAINER_temat_dla_siebie.md` (narrative + glossary) · `decisions/DEC-003` + `DEC-004` (active ADR)

---

## 0. Tryb pracy — iteracjami (NIE czasowo)

Per Magda decision 2026-05-16: *„nie patrz na czas, planuj iteracjami. Będę chciała to się wyrobię."*

- Drop „~X tygodni" estimates per iteracji
- Każda iteracja ma jasne **done criterion** + **Twoja praca / Agent robi** split
- Magda kontroluje kadencję; iteracja N+1 startuje gdy N done
- Re-iteration acceptable (np. Iter. 2a, 2b jeśli failure)

## 1. CEL główny

Zbudować **citation-grounded RAG dla polskich praw konsumenta** który (a) odpowiada z explicit cytacją do paragrafu ustawy, (b) wykrywa halucynacje real-time (hidden-states probe), (c) sam się ulepsza w continuous improvement loop. Plus **publishable benchmark** (Polish CitationBench dataset) — explicit Magda requirement.

## 2. CELE szczegółowe (5)

1. **Hidden-states halu probe** dla Bielik 11B v3 layer 47 — pierwszy publicznie udokumentowany polish halu probe → publish na HuggingFace
2. **Citation grounding pipeline** post-hoc (3-tier NLI: mDeBERTa Tier 1 ✓ T1 PASS 80.6% + HerBERT Tier 2 fallback + LLM judge Tier 3 ablation)
3. **Polish CitationBench v0.6** (✓ DONE: 11,000 chunks + 5,402 halu pairs, post-Wariant B) → HF publish w Iter. 6
4. **Continuous improvement loop** — failure cases → preference dataset → probe retrain → A/B gate → deploy
5. **Gradio demo** (3 zakładki: Chat / Inspect / Compare) — artifact na obronie + manager's office

---

## 3. Iteracje (status + done criterion + split)

### Iteracja 0a ✅ DONE 2026-05-16

Sign-off na temat + DEC-003 ADR + konspekt v3.2 + cleanup v3.1 archive + project structure + feasibility research + EXPLAINER + PLAN.

### Iteracja 0b — PARTIAL DONE (T1 PASS, T2-T4 pending)

**Done criterion:** wszystkie 4 POC kill-criteria testy PASS → DEC-004 sign-off → Iter. 1 START.

**Twoja praca:**
- ✅ Halu type taxonomy (5 typów) — patrz EXPLAINER § 4
- ✅ D1 Bielik 11B v3 primary (lab GPU SP7 H200)
- ✅ Sign-off na Wariant B cleanup (38.4% drop)
- ⏳ **PENDING:** lab GPU access → uruchom T4 SSH verify + T3 PyTorch hooks layer 47 + T2 Outlines diakrytyki
- ⏳ Po POC: fill DEC-004 + decision A/B/C → sign-off Iter. 1

**Agent zrobił:**
- ✅ ELI scrape 27 ustaw konsumenckich + 20 PDFów Dz.U. (Sejm S1) → legal_statute 2,541
- ✅ UOKiK Q&A 60 par + RF FAQ 373 → qa_gold 433
- ✅ UE 8 dyrektyw + 29 TSUE orzeczeń (S3 EUR-Lex)
- ✅ Decyzje UOKiK + 121 SN orzeczeń (S2 Playwright WAF bypass)
- ✅ 12 portali professional (Bankier/Money/Infor/...) (S6) → encyclopedic 1,167
- ✅ Forum questions 2,656 raw HTML archive (S5, 89.5% coverage)
- ✅ Polish CitationBench v0.6 build (11,000 chunks + 5,402 halu pairs, factual_fabrication=NEUTRAL fix)
- ✅ mDeBERTa Tier 1 NLI sanity ✓ **PASS 80.6%** (T1 lokal CPU) — `iter0b_poc/results/t1_mdeberta_20260516_115505.json`
- ✅ Wariant B chunk_filter strict policy + 4 POC test scaffolds + DEC-004 template
- ⏳ T2/T3/T4 scaffolds gotowe — czekają na Magdy lab GPU run

### Iteracja 1 — Probe training + RAG MVP

**Trigger:** Iter. 0b DONE (T3 PASS lab GPU).

**Done criterion:** probe AUROC z bootstrap CI ≥0.70 (CI lower ≥0.60) na primary eval set + 3-tier NLI verifier plugged + Gradio MVP działa end-to-end na 1 polish query.

**Twoja praca:**
- [ ] **Probe training** — PyTorch hooks na Bielik 11B v3 layer 47, extract activations dla 5,402 halu pairs, train sklearn LogisticRegression linear primary (MLP ablation jeśli linear < threshold)
- [ ] Hyperparam tuning Optuna (regularization, class balance)
- [ ] 3 random seeds + bootstrap CI 95%
- [ ] **RAG MVP integration** — Bielik + BGE-M3 retrieve top-k + post-hoc claim extraction + mDeBERTa NLI per claim
- [ ] **Gradio MVP** — 1 zakładka Chat z citation badges (Inspect + Compare w Iter. 6)

**Agent robi:**
- [ ] Boilerplate probe training pipeline (PyTorch + Bielik hooks + MLflow tracking)
- [ ] RAG MVP scaffolding (LlamaIndex + Qdrant indexing + Bielik gen wrapper)
- [ ] Eval scripts (AUROC + bootstrap CI + per-class precision/recall + F1)
- [ ] R6 Modele draft skeleton (placeholder z Twoich hyperparams + wyników)

**Output:** `models/probe_bielik_11b_cycle_1/` (HF format) + MLflow runs + probe AUROC reported + RAG MVP demonstrable.

**RQ1/H1 first answer:** probe AUROC ≥0.70 z bootstrap CI lower ≥0.60?

### Iteracja 2 — Ablations A1-A4

**Done criterion:** wszystkie 4 ablacje przeszły, wyniki w R7 tabele.

**Twoja praca:**
- [ ] **A1: probe → semantic entropy** (Farquhar 2024) — czy hidden-states bije classic uncertainty?
- [ ] **A2: probe target → 1.5B/3B vs 11B Bielik** — compute vs detection trade-off
- [ ] **A3: verifier → LLM-judge** (Bielik / PLLuM / Gemma 3 / Claude Haiku few-shot) — vs mDeBERTa NLI (RQ4 supporting kappa ≥0.50)
- [ ] **A4: citation → generation-time** (Outlines structured) vs post-hoc (default)
- [ ] R7 Tier 0 bonus: gliclass-multilang-ultra ablation per `research/nli_models_2026_update.md`

**Agent robi:**
- [ ] Eval scripts per ablation + tabele porównawcze
- [ ] R7 Wyniki tabele scaffolding (placeholder z wyników)

**Output:** Ablation results table → R7 ready.

### Iteracja 3 — Continuous improvement loop

**Done criterion:** 3 cykle retraining demonstrowalne + drift triggers działają.

**Twoja praca:**
- [ ] Configure cykle 1-3 Prefect flow (failure detection → preference dataset → probe retrain → A/B gate)
- [ ] Decyzja na probe target size z Iter. 2 A2 ablation
- [ ] Run 3 cykle + raportuj Δ AUROC per cykl

**Agent robi:**
- [ ] Loop scaffolding (Prefect flow template + MLflow registry integration + A/B gate logic)
- [ ] R5 Architektura diagrams (7 figur Mermaid)

**Output:** Continuous improvement loop działający + R5 figury ready.

**RQ3/H3 first answer:** loop konwerguje (Δ ≤2pp po cyklu 2, regresja w <50% cykli)?

### Iteracja 4 — Observability + Mirage critique

**Done criterion:** Langfuse + Evidently + Alibi Detect + LGTM + Alertmanager production-ready; Mirage critique address w R5.

**Twoja praca:**
- [ ] Langfuse integration na RAG pipeline (LLM call traces)
- [ ] Evidently halu rate distributions
- [ ] Alibi Detect embedding drift KS/MMD na hidden activations
- [ ] Alertmanager halu rate spike thresholds
- [ ] **Mirage of Halu Detection** address — explicit metryki NIE ROUGE-based (AUROC z bootstrap CI, agreement z manual)

**Agent robi:**
- [ ] Bibliografia research — finalize ~30 ref citation list
- [ ] Citation pass via `/citations` skill

### Iteracja 5 — Manual gold standard + 4-way verifier

**Done criterion:** Eval set complete (~110-160 par) + 4-way verifier comparison (mDeBERTa + HerBERT + gliclass + LLM-judge) reported.

**Twoja praca:**
- [ ] **50-100 par hand-annotated** (weekend hyperfocus burst) — diversity coverage (paragraph mis-citation, temporal drift, fabrication w RODO/telekom edge cases)
- [ ] Eval 4-way verifier comparison na complete eval set
- [ ] (Opcjonalnie) HerBERT-large + CDSC-E LoRA fine-tune (~1-2h A100) jeśli Iter. 1 wykazała potrzebę Tier 2

**Agent robi:**
- [ ] Eval scripts dla 4-way comparison (kappa per verifier vs gold)
- [ ] R6/R7 tabele update z 4-way results

### Iteracja 6 — Gradio polish + HF publishing

**Done criterion:** Gradio 3-zakładki działający z real models + 3 artefakty live na HF z DOI Zenodo + arXiv preprint submitted (early disclosure dla first-mover lock-in per II.2.2).

**Twoja praca:**
- [ ] Gradio polish — wpinasz real models (probe + verifier + Bielik) zamiast mockups
- [ ] UX testing (20 queries, sprawdź UX)
- [ ] Mandatory disclaimer „Nie udziela porad prawnych"
- [ ] HF dataset/model card final review przed publish
- [ ] arXiv preprint cs.CL+cs.IR submit

**Agent robi:**
- [ ] Gradio skeleton 3 zakładki (Chat / Inspect / Compare)
- [ ] HF dataset/model card publishing scripts
- [ ] DOI Zenodo metadata
- [ ] arXiv preprint draft

**Output:** Gradio demo deployable + 3 HF artefakty live + arXiv preprint submitted.

### Iteracja 7 — Writing R1-R8

**Done criterion:** wszystkie 8 rozdziałów draft + cross-review + citation pass.

**Twoja praca:**
- [ ] Writing review + decisions per sekcja
- [ ] Review draftów (agenty draftują, Ty edit/decide)
- [ ] Final narrative decisions

**Agent robi:**
- [ ] R1 Wprowadzenie draft (classic intro structure per Writing rules — `thesis_elements/CLAUDE.md`)
- [ ] R2 Literatura draft (~30 ref, source selection methodology, evidence-to-conclusion linking)
- [ ] R3 Dane draft (z Iter. 0b-1 EDA + scrape methodology + Wariant B cleanup audit)
- [ ] R4 EDA draft
- [ ] R5 Architektura draft (z Iter. 3 diagrams)
- [ ] R6 Modele draft (z Iter. 1-2 hyperparams + ablations)
- [ ] R7 Wyniki draft (z Iter. 1-5 wyniki + 4-part discussion)
- [ ] R8 Podsumowanie draft (5-wymiarowa kontrybucja)
- [ ] Cross-draft review (terminology + time-proofing + citation propagation + defense scaffolding)

### Iteracja 8 — Finalization + submit

**Done criterion:** PJATK format + abstract PL+EN + lista tabel/rysunków + bind + submit.

**Twoja praca:**
- [ ] Final review wszystkiego
- [ ] Submit do PJATK

**Agent robi:**
- [ ] PJATK formatting (TNR 12pt, IEEE footnotes, hardbinding spec)
- [ ] Abstract PL + EN (max 1000 znaków każdy)
- [ ] Lista tabel + lista rysunków
- [ ] Self-check Task 10 PRO-D (checklist 0pkt)
- [ ] Task 11 PRO-D comprehensive summary

**Compress option:** skip Iter. 2 ablations (focus MVP probe + RAG + Gradio) jeśli Magda zdecyduje na MVP scope.

---

## 4. Decyzje (status)

### Decided ✅

| # | Decyzja | Wybór |
|---|---|---|
| **D1** | Probe target LLM | **Bielik 11B v3** (lab GPU SP7 H200; 1.5B/3B fallback local CPU) |
| **D2** | Verifier Tier 1 | **mDeBERTa Tier 1 ✓ T1 PASS 80.6%** (DEC-004); HerBERT Tier 2 reserved fallback |
| **D3** | Halu typy | **5 (factual_fabrication/entity_confusion/temporal_drift/negation_flip/paragraph_mis_citation)** + per-type NLI label (factual_fabrication=NEUTRAL, reszta=CONTRADICTED) |
| **D7** | Probe architecture | **Linear primary** (sklearn LR), MLP nonlinear ablation jeśli linear < threshold |
| **D8** | Structured output library | **Outlines** (Uğur et al. 2025: 93-97% success vs xgrammar 60-78%) |
| **D10** | Probe extraction layer | **Layer 47** (= ⌊0.95 × 50⌋ per Balcells 2025); Iter. 2 ablation może test {12, 25, 38, 49} multi-layer |
| **D11** | Extraction tool | **PyTorch hooks + HF `output_hidden_states=True`** (NIE transformer-lens / nnsight) |
| **D14** | RQ1/H1 threshold | **AUROC ≥0.70 z CI lower ≥0.60** (per Dubanowska 2025 SOTA evidence) |
| **D15** | Reference implementation | **`obalcells/hallucination_probes` fork** (Apache-2.0, Mistral Small 24B = Bielik compat) |
| **DW** (Wariant B) | Scope cleanup | **strict policy** w `chunk_filter.py` (drop 38.4% off-scope chunks per `notes/scope_cleanup_decisions_2026-05-16.md`) |

### Pending

| # | Decyzja | Termin | Default |
|---|---|---|---|
| **D4** | Real questions source priority | Iter. 1 | All three (mix: Reddit + e-prawnik + forumprawne) |
| **D5** | Drift simulation type | Iter. 4 | Perturbed (cheaper) |
| **D6** | Citation: post-hoc default vs generation-time fallback | Iter. 2 (po A4 ablation) | Post-hoc (default) |
| **D9** | Lab GPU verification: H100 FP8 vs A100 bf16 | Iter. 0b (T4 pending) | Magda check + adjust deploy plan |
| **D12** | Bonus ablation: cross-model probe transferability (Bielik → Qwen 3.5-27B via OpenRouter) | Iter. 2 / R7 bonus | TBD |
| **D13** | Outlines polish diakrytyki test | Iter. 0b (T2 pending) | If fail → drop generation-time citation, focus post-hoc only |

---

## 5. Risk register

| Risk | Prawdopodobieństwo | Impact | Status / Mitigation |
|---|---|---|---|
| Promotor odrzuca pivot | 10-20% | High | DEC-003 + DEC-004 audit trail + reuse 70% reasoning + T1 PASS evidence |
| Probe AUROC <0.65 in-domain | 15-25% (obniżone z 20-30% po Dubanowska evidence) | Medium | Iter. 1 checkpoint + Iter. 2 ablation A1 (semantic entropy fallback) |
| ~~mDeBERTa za słaby na polish legal~~ | ~~30-40%~~ | ~~Medium~~ | **MITIGATED** — T1 PASS 80.6% 2026-05-16 |
| T3 PyTorch hooks Bielik 11B OOM na lab GPU | 10-15% | Medium | Fallback Bielik 1.5B/3B (per CLAUDE.md spec); D9 H100 FP8 path |
| T2 Outlines + Bielik diakrytyki broken | 25-30% | Medium | Drop generation-time citation (A4 ablation), focus post-hoc only (D13 fallback) |
| Lab GPU access permanent block | 5-10% | High | Alternative compute: Colab Pro+, runpod (per DEC-004 T4 fallback) |
| arXiv preprint scooped przez Wrocław Tech | 10-15% | Medium | Iter. 6 early HF disclosure + arXiv 2 tyg. przed obroną (per II.2.2 lock-in actions) |

---

## 6. Następny krok (current state 2026-05-16 evening)

1. **Magda kiedy będzie miała lab GPU access:** uruchom T4 SSH verify → T3 PyTorch hooks layer 47 → T2 Outlines diakrytyki
2. **Po wszystkich T1-T4 PASS:** fill DEC-004 sign-off (Wariant A 4/4 PASS → AUTHORIZE Iter. 1)
3. **Iter. 1 start (po DEC-004 sign-off):** probe training + RAG MVP — wszystkie scaffolds gotowe

Current state pre-Iter. 1:
- ✅ Polish CitationBench v0.6 ready (11,000 chunks + 5,402 halu pairs)
- ✅ mDeBERTa Tier 1 confirmed working na polish (T1 PASS)
- ✅ POC test scaffolds w `main_project/iter0b_poc/`
- ✅ Origin/main aktualne, working tree clean
- ⏳ Lab GPU run (T2+T3+T4) blocked na Magdy SSH access
