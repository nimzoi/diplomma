# Plan: cele + kroki

**Status:** *operational document, daily reference dla autorki*. Pisany po polsku, konkretnie, agent-friendly.
**Data:** 2026-05-16 (evening — post-Wariant B + T1 PASS + v0.6)
**Powiązane:** `EXPLAINER_temat_dla_siebie.md` (narrative kontekst), `02_konspekt_v3.2_skeleton.md` (akademicki konspekt), `decisions/DEC-003_pivot-na-halu-detection.md` (ADR pivotu), `decisions/DEC-004_iter0b_poc_results.md` (POC results PARTIAL)

---

## 0. Tryb pracy — iteracjami (NIE czasowo)

Per Magda decision 2026-05-16: **„nie patrz na czas, planuj iteracjami. Będę chciała to się wyrobię."**
- Drop „~X tygodni" estimates per iteracji
- Każda iteracja ma jasne **done criterion** + **agent task split** (Magda vs agent)
- Magda kontroluje kadencję; iteracja N+1 startuje gdy N done
- Re-iteration acceptable (np. Iter. 2a, 2b jeśli potrzeba)

## 1. CEL główny (1 zdanie)

Zbudować **citation-grounded RAG dla polskich praw konsumenta** który (a) odpowiada z explicit cytacją do paragrafu ustawy, (b) wykrywa halucynacje real-time (hidden-states probe), (c) sam się ulepsza w continuous improvement loop. Plus **publishable benchmark** (Polish CitationBench dataset) — explicit per Magda requirement „benchmark musi być".

## 2. CELE szczegółowe (5 punktów)

1. **Hidden-states halu probe** dla Bielik 11B v3 layer 47 (lab GPU SP7 H200; fallback 1.5B/3B local CPU) — pierwszy publicznie udokumentowany polish hallucination probe model → publish na HuggingFace
2. **Citation grounding pipeline** post-hoc (3-tier NLI: mDeBERTa Tier 1 ✓ T1 PASS 80.6% + HerBERT Tier 2 fallback + LLM judge Tier 3 ablation) — per claim verification entailment z retrieved evidence
3. **Polish CitationBench dataset v0.6** (✓ DONE 2026-05-16: 11,000 chunks + 5,402 halu pairs, post-Wariant B cleanup) — pierwszy publicznie udokumentowany polish citation-grounded halu benchmark → publish na HuggingFace w Iter. 6
4. **Continuous improvement loop** — failure cases (probe alarmy + NLI kontradykcje) → preference dataset → retrain probe → A/B gate → deploy
5. **Gradio demo** (3 zakładki: Chat / Inspect / Compare) — fizyczny artifact do pokazania na obronie + manager's office

---

## 3. Kroki (Iteracja 0 → 8)

### Iteracja 0a (DONE 2026-05-16) — sign-off + setup post-pivot

✅ Sign-off na temat
✅ DEC-003 ADR napisane
✅ Konspekt v3.2 skeleton napisany
✅ Cleanup projektu (v3.1 farma archive)
✅ Project structure (`src/halu/probe/verifier/citation/scrape/{isap,uokik,reddit}/`)
✅ Feasibility research (verdict CONDITIONAL GO)
✅ EXPLAINER + PLAN docs (this file)

### Iteracja 0b — POC + halu type taxonomy (PARTIAL DONE 2026-05-16)

**Twoja praca:**
- [x] 5 typów halu zdefiniowane (factual_fabrication / entity_confusion / temporal_drift / negation_flip / paragraph_mis_citation) — patrz EXPLAINER § 4
- [x] Decyzja: **Bielik 11B v3 primary** (lab GPU SP7 H200 80GB), 1.5B/3B fallback dla local CPU dev
- [ ] **PENDING:** Setup Bielika na lab GPU — T3 PyTorch hooks layer 47 + T4 lab GPU smoke inference + T2 Outlines diakrytyki
- [x] Manualna weryfikacja sample 10 chunks ELI po scrape — DONE w EDA notebook

**Agent robi:**
- [x] **Scrape ELI ustawy konsumenckie** (Ustawa o prawach konsumenta + KC + Nieuczc. praktyki + Ochrona konkurencji + Usługi płatnicze + Pozasądowe spory) — 2,541 chunks legal_statute → v0.6
- [x] **Scrape UOKiK Q&A** → 60 par ready-made + ekspansja → 433 qa_gold w v0.6
- [x] **mDeBERTa NLI sanity-check ✓ PASS 80.6%** (2026-05-16 lokal CPU, DEC-004 T1)
  - Output: `iter0b_poc/results/t1_mdeberta_20260516_115505.json`
- [x] **Wariant B cleanup** (17,862 → 11,000 chunks, drop 38.4% off-scope) per `notes/scope_cleanup_decisions_2026-05-16.md`
- [x] **Polish CitationBench v0.6 build** → `data/processed/citationbench_v0.6_2026-05-16/` (11,000 chunks + 5,402 halu pairs)
- [ ] **PENDING lab GPU:** T2 Outlines + Bielik 11B v3 polish diakrytyki (D8+D13)
- [ ] **PENDING lab GPU:** T3 PyTorch hooks Bielik 11B layer 47 (D10+D11)
- [ ] **PENDING lab GPU:** T4 lab GPU SSH + smoke inference (D9)

**Checkpoint go/no-go po Iter. 0b:** PARTIAL PASS (T1) — full PASS pending T2/T3/T4. Per DEC-004:
- ✅ T1 PASS 80.6% (kill criterion 50% przekroczone +30.6pp) → Tier 1 mDeBERTa confirmed dla downstream
- ⏳ T2/T3/T4 zależne od lab GPU access — Iter. 1 probe training STARTS dopiero po T3 PASS

### Iteracja 1 — full corpus + dataset + EDA

**Twoja praca (weekend hyperfocus burst):**
- [ ] **50-100 par hand-annotated** dla diversity (typy halu spoza UOKiK distribution: paragraph mis-citation, temporal drift, etc.) — total z UOKiK ~100-300 par gold standard
- [ ] Konfiguracja stratified sampling (które ustawy + jakie chunks per ustawa)
- [ ] Review EDA notebook (agenty dostarczą draft)

**Agent robi:**
- [ ] **Full ELI scrape** wszystkich ustaw konsumenckich (lista w konspekcie § II.4.1) → ~500-1000 chunks
- [ ] **UOKiK decyzje + raporty** scrape → ~200-500 chunks
- [ ] **Reddit r/Polska + r/Polish** Pushshift dumps (Academic Torrents, ~5-15 GB compressed) → filter consumer-related → ~1-3k pytań
- [ ] **e-prawnik.pl** sekcja ochrona-konsumenta scrape → ~970 wątków
- [ ] **forumprawne.org** consumer scrape → ~kilka tysięcy postów
- [ ] **Halu injection script** (5 typów) → ~5-10k synthetic pairs
- [ ] **NLI labeling pipeline** (mDeBERTa) → labels per (claim, evidence) pair
- [ ] **EDA notebook** — distribution halu types, citation lengths, paragraph distribution z ustaw, polish question characteristics
- [ ] **Format dataset → HuggingFace dataset spec** (model card draft)

**Output Iter. 1:**
- `data/processed/citationbench_v0.1_2026-05-XX.jsonl` (~10-15k pairs)
- `notebooks/eda_citationbench.ipynb`
- `data/eval/manual_gold_2026-05-XX.jsonl` (100-300 par by autorka + UOKiK)

### Iteracja 2 — probe + verifier training

**Twoja praca:**
- [ ] **Probe training** — PyTorch hooks na Bielik 1.5B forward pass, extract last 2-3 hidden layers, train small classifier (1-3 layer MLP) na (hidden_state, label) pairs
  - Reference impl: `obalcells/hallucination_probes` (Mistral-compatible = Bielik-compat)
  - Output: probe weights + Optuna best hyperparams + 3 random seeds
- [ ] **Verifier training/setup** — mDeBERTa NLI frozen lub HerBERT-large fine-tune (decyzja w Iter. 0b)
  - Output: verifier model + eval accuracy
- [ ] Hyperparam tuning Optuna search

**Agent robi:**
- [ ] **Boilerplate probe training pipeline** (PyTorch + Bielik hooks template + MLflow tracking)
- [ ] **Boilerplate verifier training pipeline** (HF Trainer + LoRA config jeśli HerBERT)
- [ ] **Eval scripts** — AUROC, precision/recall, F1, bootstrap CI dla probe; agreement % dla verifier
- [ ] **R6 Modele draft skeleton** (placeholder z Twoich hyperparams + wyników)
- [ ] **Monitoring scripts** — MLflow dashboard, training loss curves, eval per epoch

**Output Iter. 2:**
- `models/probe_bielik_1.5b_cycle_1/` (HF format, model card draft)
- `models/verifier_polish_nli/` (HF format)
- MLflow runs z 3 random seeds + Optuna best hyperparams
- Probe AUROC + verifier accuracy reported

**RQ1/H1 first answer:** czy probe AUROC ≥0.70 z bootstrap CI lower ≥0.60 na polish consumer rights eval set (per D14)?
**RQ4/H4 first answer:** czy LLM-as-judge → kappa ≥0.50 z manual labels (substantial agreement per Landis-Koch)?

### Iteracja 3 — continuous improvement loop

**Twoja praca:**
- [ ] Configure cykle 1-3 retraining (Prefect flow)
- [ ] Decyzja na probe target size (z Iter. 2 ablation A2 — 1.5B / 3B / 11B)
- [ ] Review continuous improvement architecture (Prefect DAG)

**Agent robi:**
- [ ] **Loop scaffolding** (Prefect flow template — failure detection + preference dataset construction + probe retrain + A/B gate)
- [ ] **Drift detection setup** (Evidently na halu rate distributions + Alibi Detect na hidden activations distributions)
- [ ] **R5 Architektura diagrams** (7 figur Mermaid: RAG flow + probe extraction + verifier + citation alignment + training loop + observability + drift)

**Output Iter. 3:**
- Continuous improvement loop działający (3 cykle retraining demonstrowalne)
- Drift detection alerts trigger retraining
- A/B gate decyduje deploy lub rollback

**RQ3/H3 first answer:** czy loop konwerguje (każdy cykl better lub plateau)?

### Iteracja 4 — ablations

**Twoja praca:**
- [ ] **Probe ablations:**
  - A1: probe → semantic entropy (Farquhar 2024) — czy hidden-states bije classic uncertainty?
  - A2: probe target → 1.5B vs 3B vs 11B Bielik — trade-off compute vs detection quality
  - A3: verifier → LLM-as-judge (Bielik 11B) — czy programatic NLI bije LLM-judge dla polish?
  - A4: citation → generation-time (Outlines structured) vs post-hoc (default) — empirical comparison

**Agent robi:**
- [ ] **Eval scripts per ablation** + tabele porównawcze
- [ ] **R7 Wyniki tabele scaffolding** (placeholder z Twoich wyników)

**Output Iter. 4:** Ablation results table → R7 ready

### Iteracja 5 — drift simulation + Mirage critique address

**Twoja praca:**
- [ ] Drift simulation methodology (np. perturbed queries, OOD legal domain)
- [ ] **Mirage of Halu Detection critique** address — explicit metryki które NIE są ROUGE-based (AUROC z bootstrap CI, agreement z manual)

**Agent robi:**
- [ ] **Bibliografia research** — finalize ~30 ref citation list
- [ ] **Citation pass** — verify każda cytacja przez `/citations` skill
- [ ] **R7 text draft** (per RQ section)

### Iteracja 6 — Gradio app polish

**Twoja praca:**
- [ ] Gradio app polish — wpinasz real models (probe + verifier + Bielik) zamiast mockups
- [ ] UX testing (sam wpisujesz 20 queries, sprawdzasz UX)
- [ ] Mandatory disclaimer „Nie udziela porad prawnych" w UI

**Agent robi:**
- [ ] **Gradio skeleton** (3 zakładki Chat / Inspect / Compare z mockups)
- [ ] **HuggingFace dataset card publishing** (CitationBench)
- [ ] **HuggingFace model card publishing** (probe + verifier)

**Output Iter. 6:** Gradio demo deployable + 3 artefakty na HF live

### Iteracja 7 — writing R1-R8

**Twoja praca:**
- [ ] Writing review + decisions per sekcja
- [ ] Review draftów per chapter (agenty draft-ują, Ty review/edit)
- [ ] Final decisions na narrative

**Agent robi:**
- [ ] **R1 Wprowadzenie draft** (classic intro structure per Writing rules)
- [ ] **R2 Literatura draft** (~30 ref, source selection methodology, evidence-to-conclusion linking)
- [ ] **R3 Dane draft** (z Iter. 1 EDA + scrape methodology)
- [ ] **R4 EDA draft** (z Iter. 1 EDA results)
- [ ] **R5 Architektura draft** (z Iter. 3 diagrams + system description)
- [ ] **R6 Modele draft** (z Iter. 2 hyperparams + ablations design)
- [ ] **R7 Wyniki draft** (z Iter. 2-5 wyniki + tabele + 4-part discussion)
- [ ] **R8 Podsumowanie draft** (5-wymiarowa kontrybucja per Defense scaffolding pkt 3)
- [ ] **Cross-draft review** (terminology consistency, time-proofing audit, citation propagation, defense scaffolding placement)

### Iteracja 8 — finalization + submit

**Twoja praca:**
- [ ] Final review wszystkiego
- [ ] Submit do PJATK

**Agent robi:**
- [ ] **PJATK formatting** (TNR 12pt, IEEE footnotes, hardbinding spec)
- [ ] **Abstract PL + EN** (max 1000 znaków każdy)
- [ ] **Lista tabel + lista rysunków**
- [ ] **Self-check Task 10 PRO-D** (0pkt — checklist)
- [ ] **Task 11 PRO-D comprehensive summary**

---

## 4. Decyzje pending (Twoje)

| # | Decyzja | Termin | Default jeśli nie zdecydujesz |
|---|---|---|---|
| D1 | Probe target LLM: **Bielik 11B v3** (current), Qwen 3.5/4 (do 32B), Gemma 4 (do 34B) — czeka na agent #4 research output | Iter. 0b | Bielik 11B v3 (polish-first, confirmed) — **CONFIRMED 2026-05-16; T3 lab GPU verify pending** |
| D2 | Verifier: mDeBERTa Tier 1 (frozen) vs HerBERT-large Tier 2 (custom fine-tune CDSC-E ~1-2h A100) | Iter. 0b checkpoint (po sanity check 50 par) | **DECIDED 2026-05-16: mDeBERTa Tier 1 ✓ PASS 80.6%** (DEC-004 T1) — Tier 2 NIE wymagany teraz (reserved jako fallback dla wyższej precision w Iter. 1 jeśli probe training tego potrzebuje) |
| D3 | Halu typy: 5 (current) vs 6-7 | Iter. 0b | 5 (current) |
| D4 | Real questions source priority: Reddit Pushshift vs e-prawnik.pl vs forumprawne.org | Iter. 1 (czeka na agent #4 z poprzedniej batch) | All three (mix) |
| D5 | Drift simulation type: perturbed polish queries vs OOD different polish legal domain | Iter. 5 | Perturbed (cheaper) |
| D6 | Citation: post-hoc default vs generation-time fallback | Iter. 4 (po A4 ablation) | Post-hoc (default) |
| D7 | Probe architecture: linear primary vs nonlinear MLP fallback | Iter. 2 | Linear primary, MLP w ablation jeśli linear nie konwerguje (per Liang & Wang Dec 2025) |
| D8 (NEW) | Structured output library: Outlines vs xgrammar vs Instructor | Iter. 0b POC | **Outlines** (Uğur et al. 2025: 93-97% success vs xgrammar 60-78%; speed nie warto) |
| D9 (NEW) | Lab GPU verification: H100 (FP8 path 11GB) lub A100 (bf16 22GB) | Iter. 0b POC | Magda check + adjust deploy plan |
| D10 (UPDATED) | Probe extraction layer init | Iter. 0b POC | **Layer 47** (= ⌊0.95 × 50⌋ per Balcells et al. 2025) primary; ablation w Iter. 4 może test {12, 25, 38, 49} jako multi-layer comparison |
| D11 (UPDATED) | Extraction tool: PyTorch hooks vs transformer-lens vs nnsight | Iter. 0b POC | **PyTorch hooks + HF `output_hidden_states=True`** — agent rekomenduje (transformer-lens NIE supports natively 50L Mistral; nnsight overhead dla pilota) |
| D14 (NEW) | RQ1/H1 threshold update | Iter. 2 | **AUROC ≥0.70 z CI lower ≥0.60** (vs my poprzednio ≥0.80) — realistic per Dubanowska 2025 SOTA evidence |
| D15 (NEW) | Reference implementation fork: `obalcells/hallucination_probes` | Iter. 1 | YES — Mistral Small 24B native = Bielik 11B compat trivially. Apache-2.0 license. Adapter = config edit + layer_idx update only |
| D12 (NEW) | Bonus ablation: cross-model probe transferability (Bielik → Qwen 3.5-27B) | Iter. 4 / R7 bonus | Yes/decide later — wzmacnia kontrybucję bez extra training (OpenRouter Qwen API) |
| D13 (NEW) | Iter. 0b POC critical test: polish diakrytyki w FSM/regex Outlines (ą/ę/ł/ó/ś/ż/ź) | Iter. 0b POC priority 1 | If fail → drop generation-time citation, focus post-hoc only |

## 5. Co JA (Claude) robię w tle

- ✅ Spawnnę agenta na ELI scrape Ustawy o prawach konsumenta + KC (Iter. 0b agent task) gdy dasz sign-off „start Iter. 0b"
- ✅ Spawnnę agenta na UOKiK Q&A scrape równolegle
- ✅ Boilerplate probe training pipeline + verifier pipeline + Gradio skeleton — gdy dasz sign-off na Iter. 2
- ✅ Updates dokumentów (ten plan, konspekt, DEC-003) w trakcie iteracji
- ✅ Citation pass via `/citations` skill (Iter. 5+)
- ✅ Cross-draft review po każdej Iter. (jeśli requested)

## 6. Czego NIE robię (zostaje do Ciebie)

- Probe training (PyTorch hooks Bielik) — manual decisions + debugging
- Hyperparam tuning Optuna — manual setup
- Manual annotation 50-100 par hand-labeled — weekend hyperfocus burst
- Architectural decisions (probe size, verifier choice, halu typy)
- Final writing review + decisions per chapter narrative
- PJATK submit (Ty znasz proces uczelniany)

## 7. Risk register (krótko)

| Risk | Prawdopodobieństwo | Impact | Mitigation |
|---|---|---|---|
| Promotor odrzuca pivot | 10-20% | High (rollback do v3.1 farma) | Strong DEC-003 defense argument + reuse 70% reasoning |
| Probe AUROC <0.65 | 20-30% | Medium (fallback semantic entropy) | Iter. 0b POC checkpoint + Iter. 4 ablation A1 |
| mDeBERTa za słaby na polish legal | 30-40% | Medium (fallback HerBERT custom NLI fine-tune) | Iter. 0b sanity check ~50 par |
| Reddit Pushshift dumps niedostępne | 10% | Low (mitigation e-prawnik + forumprawne) | Multi-source approach |
| Czas insufficient (<8 tygodni) | 20% | Medium | Compress: skip Iter. 4 ablations, simpler drift, MVP |
| Outlines + Bielik nie współpracują | 30% | Medium (drop hidden-states probe → NLI-judge only) | Iter. 0b POC checkpoint |

---

## 8. Daily reference: następne 24-48h

1. **Decyzja Twoja:** sign-off na PLAN ten + EXPLAINER OK?
2. **Po sign-off (jeśli yes):** ja spawnuję agentów na Iter. 0b (ELI scrape + UOKiK Q&A scrape + Outlines POC + mDeBERTa sanity)
3. **Twój hyperfocus burst (kiedy Ci pasuje):** sprecyzuj 5 typów halu (definicje operacyjne, przykłady) + decyzja D1 (Bielik probe target size)
4. **Jutro / pojutrze checkpoint** Iter. 0b → go/no-go decyzja na full Iter. 1
