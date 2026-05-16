# Konspekt v3.2 — Citation-grounded polish RAG z hallucination detection

**Data:** 2026-05-16 (evening — post-Wariant B + T1 PASS + v0.6)
**Status:** ACTIVE skeleton. Pełna prose w R1-R8 powstaje w Iter. 7 manual writing per build-first-finalize-last.
**Related ADR:** [DEC-003](decisions/DEC-003_pivot-na-halu-detection.md) · [DEC-004](decisions/DEC-004_iter0b_poc_results.md)

---

## I. Tytuł roboczy

**PL:** *„Citation-grounded polski RAG z hidden-states hallucination probe — pipeline produkcyjny dla domen krytycznych (studium przypadku: prawa konsumenta)"*

**EN:** *„Citation-grounded Polish RAG with hidden-states hallucination probe — production pipeline for high-stakes domains (case study: consumer rights)"*

---

## II.1 Streszczenie wykonawcze

Praca projektuje, implementuje i ewaluuje **trzykomponentowy pipeline** dla polskich systemów RAG w domenach krytycznych: (1) **citation-grounded generator** (Bielik 11B v3 + LlamaIndex z post-hoc citation alignment), (2) **hidden-states hallucination probe** trenowany na aktywacjach Bielika layer 47 (modern technique 2025-2026), (3) **3-tier NLI-based citation verifier** (mDeBERTa Tier 1 ✓ T1 PASS 80.6% → HerBERT-large Tier 2 fallback → LLM judge Tier 3 ablation) sprawdzający per-claim grounding w retrieved context. Pipeline objęty **continuous improvement loop** — failure cases (probe alarmy + verifier kontradykcje) trafiają do preference dataset → retrain probe co N cykli z A/B test gating.

Studium przypadku: **polskie prawa konsumenta** (UPK + Kodeks cywilny art. 535-581 z ISAP, UE dyrektywy konsumenckie + TSUE orzeczenia z EUR-Lex, decyzje + raporty UOKiK, real consumer questions z fora prawne). Eval set **200 par gold standard** (60 UOKiK Q&A ready-made + 140 manual gold by autorka — per DEC-005 2026-05-16).

Wkład: **trzy publishable artefakty** na HuggingFace (Polish CitationBench dataset, hidden-states halu probe model, polish citation verifier model) + Gradio demo (3 zakładki: Chat / Inspect / Compare) + reprodukowalny pipeline MLOps. Komponenty open-source (Bielik 11B v3, BGE-M3, mDeBERTa, MLflow, Prefect, Evidently, Langfuse, Qdrant, SGLang).

**Polish-first first-mover:** Mu-SHROOM 2025 SemEval Task 3 pominął polski (14 języków bez PL). Brak polish-specific Lynx / HHEM / FaithJudge equivalent. Praca jest pierwszym publicznie udokumentowanym polish halu detection methodology + benchmark.

---

## II.2 Domena specjalistyczna jako testbed

### II.2.1 Wybór: prawa konsumenta

Wybór polskich praw konsumenta jako testbed motywowany pięcioma przesłankami:

1. **Citation grounding deterministic.** ISAP dostarcza ustawy w strukturalnym XML/HTML — art. X ust. Y pkt Z mapuje 1:1 na chunk. Citation jako gold standard structure, ideal dla citation-grounded RAG.
2. **Real-world relevance.** Każdy konsument w Polsce kontaktuje się z prawami konsumenta (zwroty, reklamacje, gwarancja). Komisja PJATK rozumie wagę bez specialist knowledge.
3. **Halu w domain prawnym jest realnym problemem.** LLM bez RAG confabuluje paragrafy, daty, kwoty. Halucynacja prawna = zła decyzja konsumenta.
4. **Public, scrape-able data.** ISAP, UOKiK, EUR-Lex, fora — open-access, bez paywalla.
5. **Direct alignment z pracą zawodową autorki.** Production RAG dla domen krytycznych z citation requirement — exact use case z firmy.

**Praca NIE jest doradztwem prawnym.** Pipeline jest *informacyjny* z mandatory disclaimer w UI: *„Nie udziela porad prawnych — w sprawach złożonych skontaktuj się z prawnikiem lub Rzecznikiem Konsumentów."*

### II.2.2 Polish-first first-mover opportunity

Per `research/halu_detection_sota_2024_2026.md` + `research/poleval_2026.md`:
- **Mu-SHROOM 2025, MultiHal, HiTZ, HalluLens, RAGTruth**: systematycznie pomijają polski
- **PolEval 2017-2025** (8 edycji): zero halu/faithfulness/RAG tasków
- **Polish landscape**: tylko safety classifiers (PL-Guard, Bielik Guard) — NIE faithfulness

**🚨 First-mover risk: MEDIUM.** Konkurent: **Wrocław Tech (Kazienko, Kocoń, Ferdinan)** CLARIN-PL grant 2024-2026 explicit halu detection. AggTruth (ICCS 2025, arXiv 2506.18628) ALE English-only — logical next step = polish.

**Defense niche framing — 4 zwężające axes** (NIE „first Polish halu benchmark" — zbyt szerokie):
1. **Polish** (vs multilingual)
2. **Citation-grounded** (vs halu detection only)
3. **Consumer rights** (vs legal text broadly)
4. **Hidden-states probe na polish LLM** (vs LLM-judge / semantic entropy)

**Defensive lock-in actions:**
1. HF dataset release + DOI Zenodo — submit w Iter. 6 (early)
2. arXiv preprint cs.CL+cs.IR — 2 tyg. przed obroną
3. R2 sekcja explicit polish halu landscape (AggTruth + PIRB + Wrocław Tech + Mu-SHROOM gap) — prevents reviewer ambush

---

## II.3 Pytania badawcze i hipotezy

**3 main + 1 supporting** (RQ5 cross-domain deprecated post-Magda 2026-05-16 + Dubanowska EMNLP 2025 OOD evidence: SOTA probes OOD AUROC ≈ random).

### Main

**RQ1/H1 (probe quality, IN-DOMAIN).** Hidden-states halu probe trenowany na Bielik 11B v3 layer 47 (= ⌊0.95 × 50⌋ per Balcells et al. 2025) osiąga **AUROC ≥0.70 z bootstrap CI lower bound ≥0.60** detection halucynacji w polish consumer rights (in-domain).
- Falsyfikowalność: AUROC <0.60 lub CI lower <0.50 = FAIL. 0.60-0.69 lub 0.50-0.59 = INCONCLUSIVE. ≥0.70 + CI lower ≥0.60 = PASS.
- Threshold rationale: Dubanowska EMNLP 2025 — SOTA LR probes 0.79 AUROC RAGTruth in-dist; ≥0.70 z CI ≥0.60 realistic + defensible.
- Baselines: random (0.50), Lynx multilingual 8B (~0.70-0.75 polish), HHEM 2.x, **plus naive baseline check** (probe musi beat trivial features ≥10pp).
- Bootstrap CI 95% z 1000 resamples per „Mirage of Halu Detection" 2025 critique.
- **🚨 OOD caveat:** praca explicit NIE claimuje OOD generalization (RQ5 dropped, honest scope framing w R8 limitations).

**RQ2/H2 (citation grounding, Wallat ICTIR 2025 two-metric).** Faithfulness ≠ correctness:
- **H2a Faithfulness:** citation linkuje do retrieved content (NIE wymyślone)? Precision ≥85%.
- **H2b Correctness:** linked content faktycznie wspiera claim (NIE post-rationalized)? Precision ≥75% (lower bo Wallat 2025 pokazuje że do 57% real RAG citations są post-rationalized).
- Falsyfikowalność: faithfulness <70% lub correctness <60% = FAIL. Threshold range = INCONCLUSIVE. Both ≥target = PASS.
- Baseline: RAGAS faithfulness ~0.75, expected post-hoc NLI alignment cooperative ≥0.85 faithfulness, ≥0.75 correctness.

**RQ3/H3 (continuous improvement convergence).** 3-cyklowy retraining loop probe konwerguje — każdy cykl zwiększa AUROC lub plateau, brak regresji w >50% cykli.
- Falsyfikowalność: regresja w 2/3 cykli = FAIL. Plateau po cyklu 2 z cyklem 3 ≤2pp = PASS. Monotonic improvement = STRONG PASS.

### Supporting

**RQ4/H4 (LLM-as-judge quality).** LLM-judge (Bielik / PLLuM / Gemma 3 / Claude Haiku few-shot) → kappa ≥0.50 z manual labels (substantial agreement per Landis-Koch).
- Falsyfikowalność: kappa <0.40 = FAIL (LLM-judge zbyt słaby dla ablation A3).

---

## II.4 Strategia danych

**Source-of-truth:** [`main_project/data/processed/citationbench_v0.6_2026-05-16/DATASET_CARD.md`](../main_project/data/processed/citationbench_v0.6_2026-05-16/DATASET_CARD.md) — full per-source breakdown + biases + cleanup audit.

### II.4.1 Korpus — Polish CitationBench v0.6

**Quick stats:** 11,000 unified chunks (z 17,862 → drop 38.4% post-Wariant B) + 5,402 synthetic halu pairs (balanced 5/5 typów). 9 source_types: legal_statute 2,541 + qa_raw 2,945 + legal_document_pdf 1,965 + legal_ue_directive 1,360 + encyclopedic 1,167 + legal_court_judgment 534 + qa_gold 433 + legal_tsue_judgment 29 + legal_uokik_decision 26.

**Wariant B cleanup** (per `notes/scope_cleanup_decisions_2026-05-16.md`): dropped KPC + Prawo upadłościowe + Prawo bankowe + Usługi płatnicze + finance journalism + uchylone ustawy + CHF/franki SN + pure-insurance RF chunks.

### II.4.2 Halu injection strategy (5 typów)

| Typ | Definicja | NLI label | Przykład |
|---|---|---|---|
| **Factual fabrication** | LLM dodaje claim NIE w retrieved context | **NEUTRAL** (per T1 fix 2026-05-16) | „60 dni na zwrot" gdy ustawa mówi 14 |
| **Entity confusion** | LLM myli podmioty/instytucje | CONTRADICTED | „UOKiK rozpatruje reklamacje" gdy faktycznie sprzedawca |
| **Temporal drift** | LLM podaje błędną datę / okres | CONTRADICTED | „ustawa z 2020" gdy z 2014 |
| **Negation flip** | LLM odwraca sens | CONTRADICTED | „Konsument NIE ma prawa do zwrotu" gdy ma |
| **Paragraph mis-citation** | LLM cytuje art. X ale treść z art. Y | CONTRADICTED | „art. 27 — 14 dni" gdy art. 27 o czymś innym |

Generator: `main_project/src/halu/halu_injector.py` (programatic templates, deterministic, seeded).

### II.4.3 Eval set design

- **Primary (200 par gold per DEC-005):** UOKiK Q&A 60 par ready-made (✓ DONE, 55/60 z citations) + 140 par hand-annotated by autorka (weekend hyperfocus, diversity coverage: rare halu types, RODO/telekom edge cases)
- **Secondary (~1000 par):** programatic z Bielik+NLI silver labels + spot-check 5% (50 par) by autorka

---

## II.5 Modele

| Rola | Model | Rozmiar | Status | Uzasadnienie |
|---|---|---|---|---|
| Embedder | BGE-M3 | 568M | frozen | Multilingual, polish coverage, hybrid dense+sparse, MIT |
| Generator RAG | Bielik 11B v3 | 11B | frozen | Apache 2.0, native polish, ~131k context (YaRN) |
| Probe target | Bielik 11B v3 (1.5B/3B fallback) | 11B | hidden-states extracted | 50 layers × 4096 hidden, ~22 GB VRAM bf16. T3 lab GPU verify pending |
| **Halu probe** | sklearn LogisticRegression linear primary; MLP nonlinear ablation jeśli linear < threshold | <10M | trained from scratch | Per Liang & Wang Dec 2025 + Dubanowska EMNLP 2025 |
| **Verifier Tier 1** ✓ T1 PASS 80.6% | `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | 300M | frozen | Polish explicit w training (27 langs), MIT, contradicted P=1.000/R=0.766 |
| Verifier Tier 2 fallback | HerBERT-large + custom CDSC-E fine-tune | 340M | LoRA ~1-2h A100 | NIE wymagany teraz; reserved jeśli Iter. 1 probe pokaże potrzebę wyższej precision; CC-BY-NC-SA-4.0 NC clause flag w R8 |
| Verifier Tier 3 (oracle ablation) | Bielik / PLLuM / Gemma 3 / Claude Haiku few-shot | 11B+ | frozen | R7 ablation A3 + RQ4 supporting (kappa ≥0.50) |
| Verifier Tier 0 R7 ablation | gliclass-multilang-ultra | small | frozen | Multi-class native maps na 6 halu types per `research/nli_models_2026_update.md` |
| Multilingual baselines (compare) | Lynx 8B (Patronus), HHEM 2.x (Vectara) | 8B / small | frozen | Baseline dla R7 comparison vs polish probe |

**Extraction stack:** PyTorch hooks + HF `output_hidden_states=True` (NIE transformer-lens — brak 50L Mistral support; NIE nnsight — overhead dla pilota).

**Reference impl:** `obalcells/hallucination_probes` (Apache-2.0, Mistral Small 24B native = Bielik 11B compat trivially via config edit + layer_idx update). Reported AUROC EN: 0.87-0.90.

---

## II.6 Architektura pipeline (CENTRALNY R5)

7 figur diagramów Mermaid (sources w `thesis_research/diagrams/`):

1. **C4 Context** — Magda + lab GPU + judge LLM ablation + źródła ISAP/UOKiK/EUR-Lex
2. **C4 Container** — SGLang (Bielik) / TEI (BGE-M3 + mDeBERTa) / FastAPI / Qdrant / Prefect / Langfuse / LGTM
3. **RAG flow** — Query → BGE-M3 retrieve top-k → Bielik 11B v3 gen (Outlines) → per-claim citation alignment
4. **Probe extraction** — Bielik forward pass → PyTorch hooks layer 47 → mean-pool last 5 tokens → sklearn LR probe → halu score
5. **3-tier NLI verifier** — claim+evidence → mDeBERTa Tier 1 → (confidence < threshold) HerBERT Tier 2 → (R7 ablation) LLM-judge Tier 3
6. **Continuous improvement loop** — halu probe + verifier outputs → Langfuse → preference dataset → retrain probe → A/B gating (3 cykle per RQ3)
7. **Observability + drift** — Langfuse traces → Evidently data drift + Alibi Detect embedding KS/MMD → Alertmanager halu rate spike

Plus Figura 5.8 — Gradio UI mockup (3 zakładki).

---

## II.7 Citation grounding — methodology

### II.7.1 Post-hoc citation alignment (preferred)

Bielik generuje free-form polish answer. Osobny pipeline rozkłada answer na claims (sentence segmentation polish + claim extraction prompt). Per claim:
1. Retrieve top-k evidence chunks z Qdrant
2. NLI scoring per (claim, evidence) → entailed / contradicted / neutral
3. Najlepszy evidence z entailment → citation badge

Plus per claim: hidden-states probe daje halu score (independent signal).

UI: per-claim kolorowany badge (zielony / żółty / czerwony) + linkowany evidence chunk.

### II.7.2 Generation-time citations (alternative)

Bielik instruct-tuned na polish citation examples z explicit JSON schema output. Validation via Outlines (per T2 POC test — pending lab GPU).

Decyzja post-Iter. 2 po empirical comparison (R7 ablation A4).

---

## II.8 Ewaluacja: protokół + metryki

### II.8.1 Primary metryki (per RQ)

| RQ | Metryka | Threshold | Tool |
|---|---|---|---|
| RQ1 probe | AUROC z bootstrap CI 95% (1000 resamples) | ≥0.70 + CI lower ≥0.60 | sklearn + custom |
| RQ2a faithfulness | Per-claim precision (citation→retrieved) | ≥85% | mDeBERTa Tier 1 |
| RQ2b correctness | Per-claim precision (linked→supports claim) | ≥75% | mDeBERTa + manual verify |
| RQ3 convergence | Δ AUROC per cykl + regresja count | ≤2pp Δ po cyklu 2, regresja w <50% cykli | MLflow track |
| RQ4 LLM-judge | Cohen's kappa z manual labels | ≥0.50 (Landis-Koch substantial) | scikit |

### II.8.2 Eval datasets

- **Primary:** 200 par manual gold (UOKiK 60 + autorka 140) — per DEC-005 commitment
- **Secondary:** ~1000 par silver labels (Bielik+NLI), spot-check 5%
- **Out-of-distribution baseline:** explicit NIE testowane (Dubanowska 2025 evidence — OOD AUROC ≈ random; honest scope w R8 limitations)

### II.8.3 Ablations A0-A4 (cykl 1, R6 + R7)

| Ablacja | Wariant | Cel diagnostyczny |
|---|---|---|
| **A0 baseline** | Probe layer 47 + mDeBERTa Tier 1 + Bielik 11B + post-hoc citation | Pełen pipeline reference |
| **A1: probe → semantic entropy** | Farquhar 2024 classic uncertainty | Czy hidden-states bije classic uncertainty? |
| **A2: probe target → 1.5B/3B vs 11B** | Bielik smaller probe target | Trade-off compute vs detection quality |
| **A3: verifier → LLM-judge** | Bielik / PLLuM / Gemma 3 / Claude Haiku few-shot zamiast mDeBERTa | Programatic NLI vs LLM-judge dla polish (RQ4 supporting) |
| **A4: citation → generation-time** | Outlines structured output zamiast post-hoc | Generation-time vs post-hoc dla polish (pending T2 PASS) |

R7 dodatkowe: gliclass-multilang-ultra jako Tier 0 alternative.

### II.8.4 Error analysis (6-poziomowa taksonomia, R7)

Po każdym cyklu, kategoryzacja ≥100 błędów (probe predicted halu=False ale faktycznie halu, lub odwrotnie):

| Kategoria | Definicja | Mitygacja |
|---|---|---|
| Factual fabrication | Claim NIEobjęty retrieved context, probe NIE alarm | Probe re-train z więcej factual_fabrication |
| Entity confusion | LLM myli podmioty, probe nie alarm | NLI verifier secondary signal |
| Temporal drift | Błąd daty/okresu, probe nie alarm | Probe re-train (Wariant B drop CHF noise) |
| Negation flip | Subtle odwrócenie sensu, probe nie alarm | Hardest case, known limitation flag R8 |
| Paragraph mis-citation | Cite art. X ale treść z art. Y | Citation alignment catches independently |
| Ambiguous claim | Multi-interpretable | Acceptable — flag, NIE liczyć jako error |

---

## II.9 MLOps + observability stack

- **Orchestration:** Prefect 3 (async natywny)
- **Tracking:** MLflow + Optuna (HP search)
- **Versioning:** DVC (datasets) + MinIO (raw blob)
- **Observability:** Langfuse (LLM-specific) + OpenTelemetry SDK + LGTM stack (Loki / Grafana / Tempo / Mimir) + Alertmanager
- **Drift detection:** Evidently (data + halu rate distributions) + Alibi Detect (statistical KS/MMD na hidden activations)
- **A/B test gating:** MLflow Model Registry + custom A/B logic w Prefect flow
- **Serving:** SGLang (Bielik) + TEI (BGE-M3 + mDeBERTa) + FastAPI
- **CI/CD:** GitHub Actions + Docker + pre-commit hooks (ruff + pyrefly)

---

## II.10 Out of scope / future work

1. **Doradztwo prawne** — informational only. Mandatory disclaimer.
2. **Real-time production deployment z user traffic** — out of scope, simulated drift only.
3. **Cross-language transfer** — polish-only.
4. **Reranker fine-tuning** — passé per Iter. 0a (v3.1 archived).
5. **Full fine-tuning Bielika** — probe NIE LoRA pełna; LoRA dla Tier 2 verifier OK ale generator frozen.
6. **Multi-turn chat formal evaluation** — implicit chat działa via LlamaIndex ChatEngine memory; formal multi-turn coherence eval = future work.
7. **Cybersec angle (adversarial halu)** — future work R8.
8. **Cross-domain stress test** (RQ5 deprecated per Dubanowska 2025) — opcjonalne R7 sub-eksperyment jeśli czas pozwoli, NIE wymagane.

---

## II.11 Defense scaffolding

### 1. Ablation studies w cyklu 1 (R6 + R7) — patrz II.8.3

### 2. Error analysis 6-poziomowa (R7) — patrz II.8.4

Nawet jeśli AUROC nie poprawia się dramatically, rozkład błędów to wartościowy wynik metodologiczny.

### 3. 5-wymiarowa kontrybucja (R8) — negative-result publishability

Każdy wymiar broni się niezależnie. Jeśli H1 odpada (AUROC <0.70 lub CI lower <0.60), kontrybucje 2-5 stoją niezależnie:

1. **Metodologiczny** — pierwszy publicznie udokumentowany polish hallucination detection methodology (Mu-SHROOM 2025 pominął polski; AggTruth ICCS 2025 English-only)
2. **Inżynierski** — reprodukowalny pipeline citation-grounded RAG + halu probe + 3-tier NLI verifier (open-source)
3. **Artefaktowy** — 3 modele/datasety na HuggingFace (Polish CitationBench v0.6 + halu probe + mDeBERTa polish-tuned verifier jeśli Tier 2 fine-tune)
4. **Eksperymentalny** — porównanie hidden-states probe vs multilingual baselines (Lynx, HHEM, gliclass) + Wallat 2-metric
5. **Korpusowy** — pierwszy polish CitationBench dataset z deterministic citation grounding (ISAP-based), Wariant B cleanup audit, 9 source_types diverse coverage

Dataset jako wyróżniona standalone publishable artifact dla polish NLP community.

---

## II.12 Iteration plan

**Iteration-based, NIE time-based** (per Magda decision 2026-05-16). Każda iteracja ma jasne done criterion + agent task split. Operational reference: [`PLAN_cele_i_kroki.md`](PLAN_cele_i_kroki.md).

| Iter. | Goal | Done criterion |
|---|---|---|
| **0a** ✓ DONE | Sign-off + setup post-pivot | DEC-003 + konspekt v3.2 + cleanup v3.1 archive |
| **0b** PARTIAL | POC kill criteria | T1 ✓ PASS 80.6%; T2/T3/T4 pending lab GPU |
| **1** | RAG MVP + probe training | Probe AUROC z bootstrap CI dla H1; 3-tier NLI plugged; Gradio MVP |
| **2** | Ablations A1-A4 | Wszystkie 4 ablations zaszły z wynikami → R7 tabele |
| **3** | Continuous improvement loop | 3 cykle retraining demonstrowalne + drift triggers |
| **4** | Observability + Mirage critique | Langfuse + LGTM + Alertmanager production-ready |
| **5** | Manual gold 140 par + 4-way verifier comp | Eval set 200 par complete (60 UOKiK + 140 autorka per DEC-005); gliclass + LLM-judge ablations |
| **6** | Gradio polish + HF publishing | 3 artefakty live na HF + DOI Zenodo + arXiv preprint |
| **7** | R1-R8 writing | Drafty + cross-review + citation pass |
| **8** | Finalization + submit | PJATK format + abstract PL+EN + bind |

Compress możliwy: skip Iter. 2 ablations (focus probe + RAG + Gradio MVP) jeśli Magda zdecyduje na MVP scope.

---

## II.13 Strategia rozmowy z promotorem

Defense narrative dla DEC-003 pivot (drugi pivot po DEC-001):

> *„Po wykonaniu Iteracji 0a feasibility test (URPL probe 100 par) ujawniliśmy że ChPL/Ulotki mają sztywną semantykę regulatorową — alignment 100%, perfekcyjny dla baseline retrieval. Fine-tuning rerankera dałby marginalną poprawę (~2pp), H1 z konspektu v3.1 (≥10pp) odpadłby z trywialnego powodu. Plus paralelne sources research wykazało Mu-SHROOM 2025 pominął polski — realna luka z first-mover opportunity. Pivot na hallucination detection + citation grounding zachowuje 70% pracy v3.1 (cały stack MLOps, observability, drift detection — Pana sweet spot, mindset MLOps applied to LLM quality control), zmienia central komponent z reranker fine-tuning na hidden-states halu probe. Use case practical: production RAG dla domen krytycznych z citation requirement (mój zawodowy obszar). Pełen audit trail w `decisions/DEC-003`."*

Argumenty pomocnicze:
- **Reuse 70%** — promotor nie traci poprzedniego nakładu
- **Pana sweet spot zachowany** — MLOps + continuous improvement + observability + drift + A/B gating
- **Practical relevance** — production use case z pracy zawodowej
- **3 publishable artefakty** standalone na HuggingFace
- **Polish-first** — pierwszy publicznie udokumentowany w polskim landscape
- **Modern technique** — hidden-states probes 2025-2026 frontier
- **T1 PASS 80.6%** — empiryczna walidacja Tier 1 verifier 2026-05-16

---

## Zakończenie

Konspekt v3.2 jest *living document* — szkielet do uszczegółowienia w trakcie iteracji. Aktualizacje:
- Po Iter. 0b lab GPU PASS (T2/T3/T4): refresh DEC-004 + sign-off na Iter. 1 start
- Po Iter. 2 ablations: probe results + decisions na ablation A2 + A3 + A4
- Po Iter. 5: manual gold ready → final eval set
- W Iter. 7: pełen draft R1-R8 powstaje z tego skeleton
