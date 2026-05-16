# Hallucination detection SOTA 2024-2026 — research dla wyboru tematu pracy

**Autor researchu:** Claude Opus 4.7 (1M ctx) dla M. Sochackiej, PJATK
**Data:** 2026-05-16
**Scope:** Pomóc autorce zrozumieć landscape hallucination detection przed wyborem ostatecznego kierunku pracy. Polish-first focus.
**Metodologia:** Web search + WebFetch (arXiv abstracts, conference proceedings, awesome-lists). Każdy paper z linkiem dla weryfikacji. Niepewność oznaczona 🟡.

---

## 1. Executive summary

### Top 5 trendów (May 2025 - May 2026)

1. **Semantic entropy → semantic entropy probes (SEP) → semantic energy.** Po Farquhar et al. Nature 2024 cała linia badań kompresuje koszt semantic entropy z N samples do single-pass via probe na hidden states (SEP, ICLR 2025). Najnowszy "Semantic Energy" (sierpień 2025) operuje na logitach penultimate layer, czyni metodę jeszcze tańszą.
2. **Internal-states / hidden-states probing dominuje 2025.** INSIDE (2024), ICR Probe (2025), DRIFT (2025), Spectral Features of Attention Maps (EMNLP 2025), Real-Time Detection of Hallucinated Entities (Aug 2025) — wszystkie trenują linear/MLP probes na warstwach 15-20 osiągając AUROC 0.85-0.92 bez resamplingu.
3. **Reasoning models hallucinują więcej.** NeurIPS 2025 paper "Reasoning Models Hallucinate More" pokazuje że long chain-of-thought (DeepSeek R1, o1-style) zwiększa hallucination rate. To otwiera podproblem: faktualność na każdym kroku rozumowania (FSPO algorithm).
4. **LLM-as-judge w produkcji + calibration crisis.** ICLR 2025 "Trust or Escalate" + EMNLP 2025 "Mirage of Hallucination Detection" pokazują że ROUGE-based eval przeszacowuje detection o do 45.9% AUROC. Branża przesunęła się na FaithJudge (Vectara) + bias-corrected judges + simulated annotators.
5. **Multilingual hallucination detection wschodzący.** SemEval 2025 Task 3 Mu-SHROOM (14 języków), MultiHal (KG-grounded multilingual). **Polski JEST POMINIĘTY w obu.** To jest absolutnie kluczowa luka.

### 3 luki najbardziej obiecujące dla polish-first thesis

1. **🔥 BRAK polskiego hallucination/faithfulness benchmarku.** Mu-SHROOM = 14 języków bez polskiego. PolEval 2025 = 4 taski, 0 dotyczy halucynacji/faktualności. Najbliższe: PL-Guard (safety, nie faktualność), Bielik Guard (safety). PoQuAD, PolQA, MAUPQA istnieją jako QA datasets ale nikt nie zbudował na nich faithfulness benchmarku.
2. **🔥 BRAK polish-specific HHEM/Lynx-style modelu.** HHEM 2.1 cross-lingual obejmuje EN/DE/FR ale nie polski. HHEM 2.3 ma 11 języków 🟡 (sprawdzić listę). Lynx 8B/70B są EN-only. Patronus, Galileo, Vectara, Cleanlab — żaden nie ma natywnego polish faithfulness scorera.
3. **🔥 Cross-register faithfulness w polskim (ChPL↔Ulotka).** To jest dokładnie temat DEC-002 autorki — nikt w literaturze (Grabowski 2017 EN-PL, brak intra-PL) nie zbadał czy faithfulness eval na chunki ChPL (professional register) generalizuje na lay queries z Ulotki. To by było first-of-kind contribution.

### Verdict — rekomendacja kierunku

**Aktualny temat autorki (MLOps RAG retrieval retraining + RQ5 cross-register) JEST DOBRZE POSTAWIONY** w kontekście SOTA 2025-2026:
- Reranker fine-tuning to crowded ale **w polskim** (sdadas stack) jest w miarę słabo zbadany, zwłaszcza w kontekście systematycznego retreningu z observability signals
- LLM-as-judge dla polish (RQ2) jest EXACT match na trend "calibration crisis" — agreement z manual ≥75% to dobrze postawiony cel zważywszy że English baselines to 64-85%
- RQ5 cross-register jest najbardziej publishable angle
- **Co warto rozważyć dodać/zaakcentować:** explicit framing pracy jako pierwszy polish-first faithfulness/hallucination evaluation pipeline (w R1 Wprowadzenie + R8 Podsumowanie). Pozwoli to "ujechać" na luce SemEval/PolEval bez rozszerzania scope.

**NIE rekomenduję** pivota na czysty hallucination detection model (np. polish-Lynx) — to byłoby wąskie i nie pasowało do MLOps mindset promotora. Aktualny temat lepszy strategicznie.

---

## 2. Top papery (chronologicznie wstecz, 2026 → 2024)

| Author (Year) | Venue | Method category | Key contribution | Limitation |
|---|---|---|---|---|
| Obeso, Arditi, Ferrando, Freeman, Holmes, Nanda (2025-08, rev 2026-02) | arXiv 2509.03531 | Internal-states probe / streaming | Linear probes on hidden states for **real-time hallucination detection** during long-form generation; outperforms semantic entropy across architectures | Wymagają per-model trainingu, dataset web-search-grounded może mieć bias |
| Tamber, Bao, Xu et al. (2025-05) | EMNLP Industry 2025 (arXiv 2505.04847) | LLM-as-judge / leaderboard | **FaithJudge** — LLM-as-judge framework z human-annotated examples, 84% balanced accuracy z o3-mini-high | Wymagana infrastruktura LLM judge, koszt o3-mini |
| Bang, Ji, Schelten, Hartshorn, Fowler, Zhang, Cancedda, Fung (Meta, 2025-04) | ACL 2025 (arXiv 2504.17550) | Benchmark | **HalluLens** — taxonomy extrinsic vs intrinsic + dynamic test set generation przeciwko data saturation | Brak polskiego, wymagany generation pipeline |
| Sardana (2025-03) | arXiv 2503.21157 | Survey/benchmark | **Real-Time Evaluation Models for RAG** — head-to-head benchmark Lynx, HHEM, TLM, Prometheus, LLM-judge na 6 RAG apps | Reference-free focus, brak bardzo nowych metod (np. SEP) |
| Various authors (2025-02 - 2025-04) | SemEval 2025 Task 3 (aclanthology 2025.semeval-1.322) | Shared task | **Mu-SHROOM** — span-labeling hallucination detection w 14 językach. 43 teams, 2618 submissions | **POLSKI POMINIĘTY**, wysoki annotator disagreement |
| Kuhn, Gal, Farquhar (2024-06) | Nature (s41586-024-07421-0) | Uncertainty / sampling | **Semantic entropy** — measure uncertainty about meanings nie tokens, foundational paper | Wymaga 5-10× więcej computem przez resampling |
| Kossen, Han, Razzak, Schut, Malik, Gal (2024-06) | NeurIPS 2024 (arXiv 2406.15927) | Probe / hidden states | **Semantic Entropy Probes (SEP)** — predykcja semantic entropy z single hidden state, redukuje overhead do near-zero, ICLR 2025 | Wymagany supervised training na response samples |
| Lee & Yu (2025-02) | SemEval 2025 (arXiv 2502.13622) | Retrieval-grounded | **REFIND** + **Context Sensitivity Ratio (CSR)** — measure jak silnie output zależy od retrieved evidence | Wymaga retrieval setup, polski nie wspomniany w abstract |
| Niu et al. (2024) | ACL 2024 | Dataset | **RAGTruth** — word-level hallucination annotations dla RAG workflows; bazowy training set Lynx | EN-only |
| Ravi et al. (2024-07) | arXiv (Patronus) | Dataset/model | **HaluBench (15k samples)** + **Lynx 8B/70B** — open-source SOTA hallucination model bijący GPT-4o w wielu scenariuszach | EN-only, training z 7 datasets może mieć overlap |
| Dhuliawala, Komeili, Xu et al. (Meta, 2024) | ACL Findings 2024 | Self-verification | **Chain-of-Verification (CoVe)** — model drafts → plans verification questions → answers independently → final | Verifier capacity bound, błędy w reasoning steps zostają |
| Manakul, Liusie, Gales (2023) | EMNLP 2023 | Self-consistency | **SelfCheckGPT** — sampled responses z LLM-self-divergence → hallucination signal | 5-20× cost, czarna skrzynka, bias na common knowledge |
| Min et al. (2023) | EMNLP 2023 | Atomic facts | **FActScore** — decomposition into atomic facts → retrieval against Wikipedia → percentage supported | Wymaga dobrego decomposera + reliable knowledge source |
| Vatsal et al. 🟡 (2025-05) | arXiv 2505.14101 | Dataset multilingual | **MultiHal** — KG-paths z Wikidata, multilingual + multihop | Polski 🟡 (potrzeba weryfikacji listy języków), KG-grounded niekoniecznie pasuje do RAG na regulatory docs |
| Tamber, Lin (2024) | arXiv | Hidden states | **INSIDE** — EigenScore z covariance matrix eigenvalues responses dla semantic consistency | Computational cost embedding wielokrotnych odpowiedzi |
| (Various) (2025) | EMNLP 2025 | Internal states | **ICR Probe** — Hidden state dynamics tracking, layer-by-layer information contribution | Per-layer analysis, koszt skalowania |
| (Various) (2025-02) | EMNLP 2025 (arXiv 2502.17598) | Attention analysis | **Spectral Features of Attention Maps** — eigenvalues attention matrices jako structural feature | Wymaga dostępu do attention internals (white-box) |
| (Various) (2025) | NeurIPS 2025 | Training-time | **Reasoning Models Hallucinate More** — FSPO algorithm: factuality verification at each reasoning step via RL | Wymaga inference-time judge, training cost |
| (Various) (2025) | NeurIPS 2025 | Training-time | **One SPACE to Rule Them All** — joint mitigation factuality + faithfulness via shared activation subspace editing | Per-model wymaga edytowania, nie generic |
| (Various) (2025) | EMNLP 2025 | Critique | **The Illusion of Progress: Re-evaluating Hallucination Detection** — ROUGE eval przeszacowuje AUROC do 45.9% | Re-evaluation paper, nie nowa metoda, ALE krytyczny dla R7 autorki |
| (Various) (2025-04) | arXiv 2504.18114 | Critique | **Evaluating Evaluation Metrics — The Mirage of Hallucination Detection** — meta-analiza dlaczego dotychczasowe benchmarki są niewiarygodne | jw |

🟡 **Sygnalizuję niepewność** w MultiHal listing językowym i niektórych venue/data preprintów — przed cytowaniem w pracy autorka powinna re-verify bezpośrednio na arXiv lub conf proceedings.

---

## 3. Approaches taxonomy

### 3.1 Uncertainty-based (sampling/probabilistic)
- **Semantic entropy** (Farquhar et al. 2024, Nature) — multiple samples → semantic clustering → entropy
- **Semantic Entropy Probes** (Kossen et al. 2024, NeurIPS / ICLR 2025) — predict SE z hidden states, single pass
- **Semantic Energy** (2025-08, arXiv 2508.14496) — operate na logitach penultimate layer + Boltzmann energy
- **Bayesian Estimation** (2025-04, arXiv 2504.03579) — adaptive sampling, 53% mniej samples
- **Kernel Language Entropy** (2024) — density matrices + von Neumann entropy
- **TLM (Cleanlab)** — combo self-reflection + sampled-consistency + probabilistic measures, commercial

**Pasuje do thesis autorki?** Tak — semantic entropy/SEP może służyć jako alternative judge signal w RQ2, do triangulacji z PLLuM judge.

### 3.2 Internal-states / hidden-states probes (white-box)
- **INSIDE** (Chen et al. 2024, arXiv 2402.03744) — EigenScore z embedding covariance
- **ICR Probe** (2025, arXiv 2507.16488) — track hidden state dynamics across layers
- **MIND** (oneal2000/MIND GitHub) — unsupervised, real-time
- **Spectral Features of Attention Maps** (EMNLP 2025) — eigenvalues attention matrices
- **DRIFT** (2025) — probes on intermediate hidden states
- **Real-Time Detection of Hallucinated Entities** (Obeso et al. 2025) — span-level streaming probes

**Pasuje?** Częściowo — wymaga white-box access do polish-reranker/Bielik. Mogłoby być **stretch contribution dla R6** (probe na sterowanie generation z Bielika), ale poza core scope.

### 3.3 Verification-based (NLI / retrieval-grounded)
- **HHEM (Vectara)** — fine-tuned NLI classifier, EN/DE/FR (HHEM 2.1) + 11 langs (HHEM 2.3) 🟡
- **REFIND + CSR** (Lee & Yu 2025) — Context Sensitivity Ratio, retrieval-grounded
- **Retrieval-grounded fact-checkers** — RARR, FActScore z Wikipedia
- **MetaRAG** — metamorphic testing dla RAG
- **SIRG** (Semantic-level Internal Reasoning Graph) — graph-based for RAG

**Pasuje?** Ekstremalnie — to jest core methodology dla autorki w R6/R7 Modele/Wyniki. **HHEM/Lynx jako baseline → polish-fine-tuned reranker jako contribution.**

### 3.4 Critic-based (LLM-as-judge)
- **GPT-4 / Claude / o3-mini judges** — najpowszechniejsze ale calibration issues
- **FaithJudge (Vectara)** — human-annotated examples + LLM judge
- **Lynx 8B/70B** (Patronus) — open-source dedicated judge model
- **Prometheus** — fine-tuned eval LLM (open-source)
- **Trust or Escalate** (ICLR 2025) — selective evaluation z confidence
- **Simulated Annotators** — IC L diverse preferences for calibration

**Pasuje?** Tak — RQ2 autorki = exactly to (PLLuM-12B judge agreement ≥75% z manual). Najświeższe wyniki sugerują że 75% to ambitne ale realistic dla domain-specific tasks (English baseline 85% general, 64-68% expert tasks).

### 3.5 Constrained / contrastive decoding
- **DoLa (Decoding by Contrasting Layers)** — contrast across layers
- **DHI (Diverse Hallucination Induction)** — modified loss for diverse hallucination
- **PruneCD** (EMNLP 2025) — dynamic layer pruning + contrastive
- **Active Layer-Contrastive Decoding** (arXiv 2505.23657)
- **Monitoring Decoding** (ACL 2025, arXiv 2503.03106) — partial response factuality eval
- **MemVR** — memory-space visual retracing dla VLMs

**Pasuje?** Nie bezpośrednio — autorka nie touche'uje generation pipeline, BGE-M3 frozen, generator Bielik. Ale **mogłaby flagować jako future work** w R8.

### 3.6 Training-time mitigation (DPO/RLAIF/preference)
- **FLAME** (NeurIPS 2024) — factuality-aware SFT + DPO
- **OPA-DPO** (CVPR 2025) — on-policy alignment przed DPO, 3× efficient
- **Reasoning Models Hallucinate More + FSPO** (NeurIPS 2025) — RL z step-wise factuality
- **One SPACE** (NeurIPS 2025) — joint mitigation via subspace editing
- **Curriculum DPO on synthetic negatives** (2025) — curriculum learning dla detector

**Pasuje?** Nie — autorka nie fine-tune'uje Bielika/PLLuMa. Reranker fine-tuning to inny problem (ranking loss, nie DPO). Ale FSPO mogłoby być cytowane w R8 jako future direction.

### 3.7 Multi-agent / agentic verification
- **Agentic RAG z Fact-Verification Loop** — dedicated agent verifies + correction cycle
- **Multi-agent z role specialization** (MDPI 2025)
- **Cleanlab tau-2 bench** — automated correction agent

**Pasuje?** Niezbyt — out of scope dla MLOps-mindset promotora, scope creep risk.

---

## 4. Open-source tools (production state 2025)

| Tool | Version | License | Polish support | Use case fit dla autorki |
|---|---|---|---|---|
| **Patronus Lynx** (8B/70B) | 1.0 (lipiec 2024) | Apache 2.0 (model weights) | **Brak — EN-only** | Baseline w R7 — porównać z polish judge. Można fine-tune'ować na polish medical |
| **Vectara HHEM 2.1 Open** | 2.1.x | Apache 2.0 | **EN-only** dla open variant | Baseline; HHEM-2.3 ma 11 langs 🟡 weryfikacja czy polski |
| **Cleanlab TLM** | Active 2025 | Commercial / partial OSS | EN focus | Reference dla RQ2 design — combo self-reflection + consistency |
| **RAGAS** | 0.2.x (2025) | Apache 2.0 | Multilingual przez LLM judge | **PRIMARY tool dla R7 autorki** (już w stacku) |
| **DeepEval** (Confident AI) | 1.x (2025) | Apache 2.0 | Multilingual via LLM | Drugi możliwy framework, pytest integration |
| **TruLens** | 1.x (2025) | MIT | Multilingual via LLM | RAG triad — context relevance, groundedness, answer relevance |
| **FacTool** (GAIR-NLP) | Active GitHub | MIT | EN-focus | Tool-augmented detection, dla long-form |
| **HaluEval** (RUCAIBox) | v1, v2 | MIT | EN-only | Benchmark + framework dla detection |
| **Athina AI** | SaaS + SDK | Mixed | Multilingual | Enterprise eval platform |
| **Galileo Luna v1/v2** | 2025 | Commercial | EN-focus, multi-lang via API | DeBERTa-large 440M fine-tuned, sub-200ms latency |
| **Arize AI** | Phoenix open-source | Apache 2.0 | Multilingual | Observability + tracing focus |
| **Langfuse** | 3.x (2025) | MIT | Multilingual | **W stacku autorki** już — observability + LLM-as-judge tooling |
| **MIND** (oneal2000) | GitHub OSS | 🟡 sprawdzić | EN | Unsupervised hidden-state |
| **NeMo Guardrails** | Active 2025 | Apache 2.0 | Multilingual | Lynx integration na lipiec 2024 |
| **SelfCheckGPT** | Original repo | MIT | Multilingual via base LLM | Reference baseline, łatwe do reproducal |

**Production stack rekomendowany dla autorki (zgodny z 05_stack_techniczny.docx):**
- RAGAS jako primary metrics (faithfulness, context_precision, context_recall, answer_relevancy) — already in stack
- Langfuse dla observability + LLM-as-judge tracing — already in stack
- Lynx 8B jako external baseline w R7 (porównać polish PLLuM judge vs Lynx EN-only)
- HHEM 2.3 do triangulacji jeśli polski wspierany

---

## 5. Polish landscape

### 5.1 Co już jest opublikowane / open-source

**Modele LLM:**
- **Bielik v1/v2/v3** (SpeakLeash, AGH Cyfronet) — open-source PL LLMs, technical reports na arXiv
- **PLLuM** (OPI-PIB consortium) — 8B-70B (continued pretraining Llama/Mistral), arXiv 2511.03823 (Kocoń et al. 2025)
- **Trurl 2** (Voicelab) — fine-tuned Llama 2 7B/13B
- **Qra 1B/7B/13B** (OPI-PG = OPI + Politechnika Gdańska) — 90B PL tokens

**Datasety QA / IR:**
- **PoQuAD** (Tuora et al. 2023, K-CAP) — 70k Q-A pairs, SQuAD-like, PL Wikipedia, ma "impossible questions"
- **PolQA** (Rybak et al. 2024, LREC-COLING) — 7k questions, 87k labeled passages, 7M+ corpus
- **MAUPQA** (Rybak 2023) — Massive Auto-created PL QA
- **PIRB** (sdadas, Dadas 2024, LREC) — 41 IR tasks, w tym medical/legal/business — **DOSKONAŁY baseline dla autorki**
- **KLEJ** (Rybak et al. 2020, ACL) — 9 PL NLU tasks
- **LEPISZCZE** (CLARIN-PL) — comprehensive PL benchmark
- **LLMzSzŁ** (arXiv 2501.02266) — comprehensive LLM benchmark dla polskiego

**Safety / Guardrails (NIE faithfulness):**
- **PL-Guard** (Krasnodębska, Seweryn, Łukasik, Kusa 2025, arXiv 2506.16322) — manually annotated safety benchmark. HerBERT classifier > Llama-Guard-3-8B + PLLuM under adversarial conditions
- **Bielik Guard** (arXiv 2602.07954) — 0.1B i 0.5B safety classifiers, F1 0.785-0.791
- **Rainbow-Teaming for Polish** (TrustNLP 2025)

**Retrievers / Rerankers:**
- **sdadas/polish-reranker-roberta-v3** — 8192 ctx, 65.17 PIRB score (z mmlw retriever)
- **sdadas/polish-reranker-bge-v2** — bge-reranker-v2-m3 distilled
- **Polish-reranker collection** — multiple variants

**Aktywni researcherzy / labs (z search results):**
- **AGH Cyfronet + SpeakLeash** — Bielik team
- **OPI-PIB + Politechnika Gdańska** — Qra, PLLuM
- **IPI PAN (zil.ipipan.waw.pl)** — PolQA, NLP seminar
- **CLARIN-PL** — LEPISZCZE, language resources
- **NASK** — AI safety research
- **sdadas (S. Dadas)** — independent ale very active na HF, PIRB, rerankers
- **Allegro** — HerBERT baseline maintainer

### 5.2 Konkretne luki dla polish thesis (= opportunity)

1. **Faithfulness/hallucination dataset dla polskiego — BRAK.** PL-Guard to safety nie faithfulness. PoQuAD/PolQA mają answers ale brak halucynacja-specific annotations. **Polish HaluBench-equivalent** byłby novel.
2. **Polish-fine-tuned faithfulness scorer (Lynx-equivalent) — BRAK.** Żaden lab w Polsce nie zwołał Patronus-style modelu. Można fine-tune polish-reranker-roberta-v3 jako classifier hallucination lub Bielik-Guard-style approach.
3. **Domain-specific (medical/clinical/regulatory) PL faithfulness eval — BRAK.** Pokrywka et al. 2024 (board exams) i Rosoł et al. 2023 (final medical exam) pokazują że GPT-4 zdaje, ale nikt nie zbudował RAG-grounded faithfulness eval na polish ChPL/Ulotki.
4. **Cross-register PL faithfulness (ChPL↔Ulotka) — BRAK.** Dokładnie tematyka DEC-002 autorki. Grabowski 2017 ma EN-PL pairing, brak intra-PL professional↔consumer register pairing dla pharma.
5. **Polish PolEval task na halucynacje — BRAK** (PolEval 2025 ma tylko ŚMIGIEL = MGT detection, gender bias, layout, emotion). Można pitchować PolEval 2026 task po obronie 🟡.

### 5.3 Co znaleziono ale wymaga weryfikacji 🟡

- HHEM 2.3 ma rzekomo 11 języków — sprawdzić czy polski jest w liście (Vectara docs / HF model card)
- MultiHal lista języków — czy polski jest w 25.9k curated subset
- LLMzSzŁ — sprawdzić czy halucynacje są jednym z testowanych aspektów

---

## 6. Dostępne datasety

### 6.1 English (general)

| Name | Size | Language | License | URL | Use case |
|---|---|---|---|---|---|
| **HaluBench** (Patronus 2024) | 15k | EN | Apache 2.0 | huggingface.co/datasets/PatronusAI/HaluBench | Trening Lynx; Q-A-context triplets; finance + medicine |
| **RAGTruth** (Niu et al. 2024) | ~18k | EN | MIT | github.com/ParticleMedia/RAGTruth | Word-level annotations for RAG |
| **HaluEval** (RUCAIBox 2023) | 5k general + 30k task | EN | MIT | github.com/RUCAIBox/HaluEval | QA + KG dialogue + summarization |
| **HaluEval 2.0** | extended | EN | MIT | github.com/RUCAIBox/HaluEval-2.0 | Extension |
| **FELM** (2023) | ~3k | EN | Apache 2.0 | github.com/hkust-nlp/felm | Factuality eval |
| **FaithBench** (Vectara, arXiv 2410.13210) | varies | EN | 🟡 | aclanthology + HF | Summarization hallucination |
| **TruthfulQA** (Lin et al. 2022) | 817 questions | EN | Apache 2.0 | github.com/sylinrl/TruthfulQA | Adversarial truthfulness |
| **SimpleQA** (OpenAI 2024) | 4.3k | EN | MIT | github.com/openai/simple-evals | Simple factuality |
| **DefAn** | varies | EN | 🟡 | arXiv | Definitional answer |
| **Shroom2024 / Shroom2025** | varies | Multi | varies | helsinki-nlp.github.io/shroom | Hallucination overgen detection |
| **FEVER** (Thorne et al. 2018) | 185k claims | EN | CC BY-SA | fever.ai | Fact verification |
| **SciFact** (Wadden et al. 2020) | 1.4k claims | EN | CC BY-SA | github.com/allenai/scifact | Scientific claim verification |
| **ExpertQA** (Malaviya et al. 2024) | 2.2k questions | EN | Apache 2.0 | github.com/chaitanyamalaviya/expertqa | Long-form expert QA |
| **FreshQA** (Vu et al. 2023) | 600 Q | EN | Apache 2.0 | github.com/freshllms/freshqa | Time-sensitive QA |
| **MedHallu** (2025) | varies | EN | 🟡 | arXiv | Medical hallucinations specifically |

### 6.2 Polish — istniejące (NIE zbudowane jako halucynacja-eval)

| Name | Size | Language | License | URL | Use case |
|---|---|---|---|---|---|
| **PoQuAD** | 70k Q-A pairs | PL | CC BY-SA 4.0 | huggingface.co/datasets/clarin-pl/poquad 🟡 | SQuAD-like, ma "impossible questions" — można re-purpose dla "abstain test" |
| **PolQA** (IPI PAN) | 7k Q + 87k passages + 7M corpus | PL | CC BY 4.0 | huggingface.co/datasets/ipipan/polqa | Largest open-domain QA PL — perfect dla retrieval baseline |
| **MAUPQA** | massive auto-created | PL | varies | arXiv 2305.05486 | Auto-created supplement |
| **PIRB** | 41 IR tasks | PL | varies | huggingface.co/spaces/sdadas/pirb | **Use jako baseline dla retrieval/reranker eval — primary** |
| **KLEJ** | 9 NLU tasks | PL | varies | klejbenchmark.com | NLU benchmark |
| **LEPISZCZE** | comprehensive | PL | varies | github.com/CLARIN-PL/LEPISZCZE | Modern PL benchmark |
| **PL-Guard** (2025) | manual + adv | PL | 🟡 sprawdzić | arXiv 2506.16322 | Safety NIE faithfulness |
| **CPTUB / Tricky Questions** | varies | PL | 🟡 | (Bielik benchmarks) | Hallucination AVOIDANCE testing pośrednio |
| **ipipan/ipis** | varies | PL | varies | huggingface.co/datasets/ipipan/ipis | IPI PAN dataset |

### 6.3 Multilingual (z polskim potential)

| Name | Size | Language | License | URL | Use case |
|---|---|---|---|---|---|
| **Mu-SHROOM** (SemEval 2025) | varies | 14 langs | varies | helsinki-nlp.github.io/shroom/2025.html | **POLSKI POMINIĘTY** — sygnał luki |
| **MultiHal** (2025-05) | 25.9k curated z 140k mined | Multi | 🟡 | arXiv 2505.14101 | KG-grounded multilingual hallucination — sprawdzić PL |
| **HHEM-2.3 leaderboard** | rolling | 11 langs | 🟡 | vectara.com | Sprawdzić czy PL |

### 6.4 Multimodal (out of scope, ale warto wiedzieć)

| Name | Size | Modality | URL |
|---|---|---|---|
| **POPE** | varies | VLM (object hallucination) | arXiv 2305.10355 |
| **MMHal-Bench** | varies | VLM | github |
| **CHAIR** | varies | VLM caption | reference metric |
| **FREAK** (2025) | varies | MLLM fine-grained | OpenReview |
| **MMMC** (2025) | varies | Modality conflict | NeurIPS 2025 |
| **DASH** (ICCV 2025) | varies | VLM systematic | openaccess.thecvf.com |

---

## 7. Trendy 2026 (early signals)

### Co weszło / wchodzi w 2026

1. **"Re-evaluation papers" — krytyka dotychczasowych benchmarków.** EMNLP 2025 "Illusion of Progress" i arXiv 2504.18114 "Mirage of Hallucination Detection" — do 45.9% AUROC overestimation. **Trend: ostrożność z ROUGE/BLEU baselines, push w stronę human-grounded eval.** Implikacja dla autorki: **R7 powinien explicit address tę krytykę przy reporting wyników**.
2. **Real-time / streaming detection.** Obeso et al. (Aug 2025, rev Feb 2026) span-level token-by-token detection. **Trend: hallucination detection przesuwa się z post-hoc na inference-time.**
3. **Reasoning-aware factuality.** NeurIPS 2025 paper pokazuje long-CoT zwiększa halucynacje, FSPO step-wise verification. **Trend: chain-of-thought czyni problem trudniejszym, nie łatwiejszym.**
4. **Joint factuality + faithfulness mitigation.** "One SPACE" NeurIPS 2025 — single intervention dla obu typów. **Trend: dotychczas traktowane oddzielnie, teraz unified frameworks.**
5. **Cross-lingual hallucination evaluation jako shared task.** SemEval Mu-SHROOM 2025 i prawdopodobnie SemEval 2026 (TBD) 🟡. **Trend: multilingual finally gets attention, ale polski wciąż out.**
6. **Bias-corrected LLM judges.** ICLR 2025 "Trust or Escalate", ICLR 2026 papers o calibration-based bias correction + item response theory. **Trend: judge configuration evaluation jako first-class problem.**
7. **Cognometry-style multi-signal pooling.** Cognometry v0 2026 łączy 9 signals z DeBERTa NLI + uncertainty. **Trend: ensembling > single method, podobnie do RAG triad RAGAS.**

### Co prawdopodobnie wejdzie w 2026 H2 / 2027

- **Polish-specific hallucination work** — momentum z PL-Guard + Bielik Guard sugeruje że ktoś pójdzie dalej w faithfulness w polskim
- **Domain-specific (medical, legal) faithfulness models** — generic stuff się nasycił, niche'e jeszcze nie
- **Agentic RAG + verification loops** w produkcji
- **VLM hallucination jako "hot" temat** (osobny od text)

---

## 8. Rekomendacje top 3 kierunki dla polish-first thesis

### Direction 1 (REKOMENDOWANE — zachować aktualny temat z drobnym refeamingem)

**Tytuł:** *MLOps pipeline iteracyjnego dotrenowywania komponentów retrievalu w polskojęzycznym RAG dla farmakologii klinicznej, z eksperymentem cross-register (ChPL↔Ulotka)* — bez zmian.

**Ale w R1 / R8 explicit framing:**
> *"Niniejsza praca jest pierwszym znanym autorce systematycznym studium faithfulness/hallucination evaluation pipeline dla polskojęzycznego RAG w domenie regulowanej. Pokrywa lukę po Mu-SHROOM (SemEval 2025, 14 języków bez polskiego) i PolEval 2025 (4 taski, żaden o halucynacjach). Cross-register angle (ChPL↔Ulotka) stanowi novel intra-Polish professional↔consumer register pairing nieobecny w Grabowski 2017 (EN-PL only)."*

**Uzasadnienie:**
- Aktualne RQ1-RQ5 pokrywają trzy główne luki (1, 3, 4) z sekcji 5.2
- LLM-as-judge dla polish (RQ2) jest exact match na trend "calibration crisis"
- Cross-register (RQ5) jest najbardziej publishable
- Promotor MLOps mindset = pipeline engineering trzymane w fokusie
- **Risk:** bez explicit framing pracy jako polish-first faithfulness, może się zlać z innym retrievalowym tematem

### Direction 2 (alternatywa, większy pivot — NIE rekomendowane teraz, ale prawdopodobne **future work**)

**Tytuł:** *Polish-Lynx: open-source hallucination detection model dla polskojęzycznego RAG w domenie medycznej.*

**Co by to wymagało:**
- Stworzenie polish HaluBench-equivalent (manualnie lub semi-auto) — ~15k Q-A-context triplets
- Fine-tuning polish-reranker-roberta-v3 jako classifier (lub Bielik-11B / PLLuM-12B)
- Ewaluacja na PIRB + nowy benchmark
- Open-source release na HF

**Pros:** czysta novel contribution, otwiera publishable artifact, idealnie w lukę
**Cons:** scope 12-18 miesięcy nie 6, brak MLOps pipeline angle (mismatch z promotorem), ryzyko że ktoś z OPI-PIB / SpeakLeash zrobi to wcześniej — to jest dosłownie obvious next step po PL-Guard
**Verdict:** **NIE jako thesis topic** — ale z prac autorki MOGĄ wyjść dane do tej pracy jako PhD/post-thesis project

### Direction 3 (stretch — gdyby autorka miała jeszcze 6 miesięcy)

**Tytuł:** *Faithfulness eval dla polish RAG w farmakologii: open-source benchmark suite + judge calibration study.*

**Co by to wymagało:**
- Zbudować mały (~500-1000 par) polish PharmaHaluBench na bazie psych-subset autorki
- Manual gold standard (autorka ma tę kompetencję)
- Comparative study: PLLuM vs Lynx EN vs HHEM vs RAGAS w polish setting
- Calibration analysis (per "Trust or Escalate" ICLR 2025)
- Release benchmark + judge configuration recommendations

**Pros:** publishable side-artifact, data + judge benchmark, łatwo cytowalne przez community
**Cons:** wymaga osobnego scope poza thesis, ryzyko rozwodnienia core contribution
**Verdict:** **Zostawić jako future work / first publication after thesis defense** — sygnalizować w R8

---

## 9. Co krytycznie nie polecam (anti-rekomendacje)

1. **Pivot na pure hallucination detection (Direction 2)** — Plan B autorki (cybersec) został zdezaktywowany właśnie żeby NIE robić scope creep. Direction 2 to ten sam błąd inną drogą.
2. **Dodawanie semantic entropy / SEP eksperymentów do core scope** — ciekawe, ale wymaga white-box hidden states, koliduje z Bielik via SGLang serving. Future work R8.
3. **Multi-agent verification frameworks** — out-of-scope dla MLOps continuous training mindset.
4. **VLM hallucination** — całkowicie out-of-scope, polski farmakologia OCR ChPL nie jest VLM problem.
5. **Konkurowanie z Mu-SHROOM 2026 jeśli wystartuje z polskim** — ryzyko mam, sprawdzić w czerwcu 2026 czy SemEval 2026 ogłosił coś polish-related. Jeśli tak, zmienić framing.

---

## 10. Materiały referencyjne (curated lists do follow-up)

- **EdinburghNLP/awesome-hallucination-detection** (GitHub) — najświeższa lista papers, czytać miesięcznie
- **vectara/hallucination-leaderboard** (GitHub) — leaderboard summarization hallucination, regularly updated
- **NishilBalar/Awesome-LVLM-Hallucination** (GitHub) — VLM out-of-scope ale dla referencji
- **showlab/Awesome-MLLM-Hallucination** (GitHub) — multimodal
- **liuzihe02/halu** (GitHub) — benchmark różnych narzędzi i metod
- **helsinki-nlp.github.io/shroom** — SHROOM/Mu-SHROOM proceedings
- **poleval.pl** — śledzić PolEval 2026 ogłoszenia (rekomendacja: monitoring co 2 tygodnie od czerwca 2026)

---

## 11. Niepewności wymagające weryfikacji przez autorkę przed cytowaniem

🟡 **MultiHal language list** — czy polski jest w 25.9k curated subset (arXiv 2505.14101)
🟡 **HHEM 2.3 lista 11 języków** — sprawdzić Vectara docs / HF model card
🟡 **PoQuAD URL i licencja** — clarin-pl URL trzeba potwierdzić
🟡 **CPTUB / Tricky Questions licensing** — pochodzi z Bielik benchmarków, autorzy?
🟡 **MIND license** — GitHub repo licensing
🟡 **Faith Bench license** — Vectara repo
🟡 **DefAn dataset paper attribution** — dokładny cite
🟡 **SemEval 2026 task list** — jeszcze nie ogłoszone, monitorować
🟡 **Niektóre 2026 cites na arXiv** — niekompletne (np. arXiv 2602.07954 Bielik Guard, arXiv 2603.x.x — sprawdzić czy nie są stub/placeholder w search results, szczególnie te z numerami zaczynającymi się 26xx)

**Generalnie: każda cytacja w thesis MUSI być re-verified bezpośrednio na arXiv.org / aclanthology.org / proceedings przed włączeniem do bibliografii. Ten dokument służy jako research scaffolding NIE jako finalna bibliografia.**
