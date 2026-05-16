# Konspekt v3.2 — Citation-grounded polish RAG z hallucination detection

**Data:** 2026-05-16 (evening — post-Wariant B + T1 PASS + v0.6)
**Status:** ACTIVE skeleton (post-DEC-003 pivot + post-DEC-004 POC partial PASS). Pełna prose w R1-R8 powstaje w Iter. 7 manual writing per build-first-finalize-last. Drafty PUSTE w `thesis_research/drafts/` (pre-cleanup R3/R4/R5 → `_archive/v3.2-pre-clean/drafts/`).
**Supersedes:** `_archive/v3-pharma-reranker/02_konspekt_v3_FINAL.docx` + `_archive/v3-pharma-reranker/02b_konspekt_v3_updates.md` (v3.1 farma+reranker)
**Related ADR:** [DEC-003](decisions/DEC-003_pivot-na-halu-detection.md), [DEC-004](decisions/DEC-004_iter0b_poc_results.md)

---

## I. Tytuł roboczy

**PL:** *„Citation-grounded polski RAG z hidden-states hallucination probe — pipeline produkcyjny dla domen krytycznych (studium przypadku: prawa konsumenta)"*

**EN:** *„Citation-grounded Polish RAG with hidden-states hallucination probe — production pipeline for high-stakes domains (case study: consumer rights)"*

---

## II.1 Streszczenie wykonawcze

Praca projektuje, implementuje i ewaluuje **trzykomponentowy pipeline** dla polskich systemów RAG w domenach krytycznych: (1) **citation-grounded generator** (Bielik 11B v3 + LlamaIndex z post-hoc citation alignment), (2) **hidden-states hallucination probe** trenowany na aktywacjach Bielika layer 47 (modern technique 2025-2026), (3) **3-tier NLI-based citation verifier** (mDeBERTa Tier 1 ✓ T1 PASS 80.6% 2026-05-16 → HerBERT-large Tier 2 fallback → LLM judge Tier 3 ablation) sprawdzający per-claim grounding w retrieved context. Pipeline objęty **continuous improvement loop** — failure cases (probe alarmy + verifier kontradykcje) trafiają do preference dataset → retrain probe co N cykli z A/B test gating.

Studium przypadku: **polskie prawa konsumenta** (Ustawa o prawach konsumenta + Kodeks cywilny art. 535-581 z ISAP, decyzje + raporty UOKiK, real consumer questions z Reddit r/Polska + fora prawne). Eval set 100 par manual gold standard by autorka.

Wkład pracy: **trzy publishable artefakty** na HuggingFace (Polish CitationBench dataset, hidden-states halu probe model, polish citation verifier model) + Gradio demo (3 zakładki: Chat / Inspect / Compare) + reprodukowalny pipeline MLOps. Komponenty oparte na otwartych modelach (Bielik 11B v3 + 1.5B/3B dla probe, BGE-M3 embedder, HerBERT NLI) i otwartych narzędziach MLOps (MLflow, Prefect, Evidently, Langfuse, Qdrant, PostgreSQL, SGLang serving).

**Polish-first first-mover:** Mu-SHROOM 2025 SemEval Task 3 pominął polski (14 języków bez PL). Brak polish-specific Lynx / HHEM / FaithJudge equivalent. Praca jest pierwszym publicznie udokumentowanym polish hallucination detection methodology + benchmark.

---

## II.2 Domena specjalistyczna jako testbed

### II.2.1 Wybór: prawa konsumenta

Wybór polskich praw konsumenta jako testbed motywowany pięcioma przesłankami:

1. **Citation grounding deterministic.** ISAP (Internetowy System Aktów Prawnych) dostarcza ustawy w strukturalnym XML/HTML — art. X ust. Y pkt Z mapuje 1:1 na chunk. Citation jest gold standard structure, ideal dla citation-grounded RAG. Halucynacje w paragrafach testowalne precyzyjnie.

2. **Real-world relevance.** Każdy konsument w Polsce kontaktuje się z prawami konsumenta (zwroty, reklamacje, gwarancja). Komisja obronna PJATK rozumie wagę bez specialist knowledge.

3. **Halu w domain prawnym jest realnym problemem.** LLM bez RAG często confabuluje paragrafy, daty wejścia w życie, kwoty. Halucynacja prawna = konsument idzie ze złą decyzją do sądu lub sklepu.

4. **Public, scrape-able data.** ISAP, UOKiK, Reddit r/Polska + fora prawne — wszystkie open-access, bez paywalla, bez login requirements. Agenty mogą scrape bez friction.

5. **Direct alignment z pracą zawodową autorki.** Production RAG dla domen krytycznych z citation requirement — exact use case z firmy autorki. Manager zafascynowany; możliwy deploy w pracy po obronie.

**Praca nie pretenduje do doradztwa prawnego.** Autorka nie jest prawniczką. Pipeline jest *informacyjny* — pomaga konsumentowi zrozumieć swoje prawa z explicit cytacją do źródła, NIE udziela porady prawnej. Mandatory disclaimer w UI: *„Nie udziela porad prawnych — w sprawach złożonych skontaktuj się z prawnikiem lub Rzecznikiem Konsumentów."*

### II.2.2 Polish-first first-mover opportunity (z honest framing)

Per `research/halu_detection_sota_2024_2026.md` + `research/poleval_2026.md`:
- **Mu-SHROOM 2025, MultiHal, HiTZ, HalluLens, RAGTruth**: wszystkie systematycznie **pomijają polski** ✓
- **PolEval 2017-2025** (8 edycji): **zero halu/faithfulness/RAG tasków**. PolEval 2026 NIE ogłoszony stan 2026-05-16.
- **Polish landscape**: tylko safety classifiers (PL-Guard, Bielik Guard) — NIE faithfulness.

**🚨 First-mover risk: MEDIUM** (nie LOW jak początkowo zakładano). Identified konkurent:
- **Wrocław Tech (Kazienko, Kocoń, Ferdinan)** — CLARIN-PL grant 2024-2026 explicit halu detection. AggTruth (ICCS 2025, arXiv 2506.18628) — ALE **English-only**. Logical next step = polish, mogą w 6 miesięcy zaserwować counter.
- **OPI (Dadas) PIRB** — retrieval-side threat, NIE halu focus.

**Defense niche framing (per PolEval research):**

> **„First publicly documented Polish citation-grounded RAG benchmark for consumer rights, with hidden-states hallucination probe on Polish LLM"**

4 zwężające axes (NIE „first Polish halu benchmark" — zbyt szerokie):
1. **Polish** (vs multilingual)
2. **Citation-grounded** (vs halu detection only)
3. **Consumer rights** (vs legal text broadly)
4. **Hidden-states probe na polish LLM** (vs LLM-judge / semantic entropy)

Każdy axis zwęża niche. AggTruth = English summarization halu, bardzo różny scope.

**Defensive lock-in actions (early publish):**
1. **HF dataset release + DOI Zenodo** — submit w Iter. 6 (zamiast Iter. 8) dla early public disclosure
2. **arXiv preprint cs.CL+cs.IR** — 2 tyg. przed obroną dla citable timeline lock
3. **R2 sekcja explicit polish halu landscape** cytując AggTruth + PIRB + Wrocław Tech + Mu-SHROOM polish gap — prevents reviewer ambush

---

## II.3 Pytania badawcze i hipotezy

**3 main + 1 supporting (NIE 5 jak w v3.1; RQ5 cross-domain deprecated post-Magda decision 2026-05-16 + Dubanowska EMNLP 2025 + Vaddi 2026-03 OOD evidence).**

### Main

**RQ1/H1 (probe quality, IN-DOMAIN).** Czy hidden-states halu probe trenowany na Bielik 11B v3 layer 47 (= ⌊0.95 × 50⌋ per Balcells et al. 2025) osiąga **AUROC ≥0.70 z bootstrap CI lower bound ≥0.60** detection halucynacji w polish consumer rights answers (in-domain)?
- *Falsyfikowalność:* AUROC <0.60 lub CI lower <0.50 = FAIL. AUROC 0.60-0.69 lub CI lower 0.50-0.59 = INCONCLUSIVE. AUROC ≥0.70 z CI lower ≥0.60 = PASS.
- *Threshold rationale:* Per Dubanowska EMNLP 2025 — SOTA polish-applicable LR probes osiągają 0.79 AUROC RAGTruth in-dist; ≥0.70 z CI lower ≥0.60 jest **realistic + defensible** dla polish-first niche.
- *Baseline:* random (0.50), Lynx multilingual 8B (~0.70-0.75 polish), HHEM 2.x, **plus naive baseline check** (probe musi beat trivial features ≥10pp per Dubanowska).
- *Architecture:* **linear probe (sklearn LogisticRegression) primary** (Liang & Wang Dec 2025 + Dubanowska 2025). Nonlinear MLP w ablation jeśli linear < threshold (+270% precision na boundary per Liang & Wang).
- *Extraction:* **PyTorch hooks + HF `output_hidden_states=True`** (NIE transformer-lens — brak natywnego support dla 50L Mistral; NIE nnsight — overhead dla pilota).
- *Reference impl:* `obalcells/hallucination_probes` (Apache-2.0) adapter dla Bielik = config edit + layer_idx update only. Reported AUROC EN: 0.87-0.90.
- *Bootstrap CI:* 95% z 1000 resamples per „Mirage of Halu Detection" 2025 critique.
- **🚨 OOD caveat (Dubanowska EMNLP 2025 + Vaddi 2026-03):** SOTA halu probes mają OOD AUROC ≈ random (in-domain 0.78 → cross-domain 0.56). **Niniejsza praca explicit NIE claimuje OOD generalization** — RQ5 cross-domain transferability dropped (po decyzji Magdy 2026-05-16 „już tej ulotki nie mieszajmy"). Honest scope framing w R8 limitations.
- **First-mover potential: HIGH** — ZERO existing polish-specific halu probes w landscape (Bielik Guard = safety classifier, POLygraph = text-only, PLLuM filter = post-generation, NIE hidden-state introspekcja).

**RQ2/H2 (citation grounding — TWO-METRIC).** Per Wallat ICTIR 2025 (arXiv 2412.18004): faithfulness ≠ correctness. **Mierzymy obie metryki osobno:**
- **H2a — Faithfulness:** czy citation linkuje do retrieved content (NIE wymyślone)? Precision ≥85% target.
- **H2b — Correctness:** czy linked content faktycznie wspiera claim (NIE post-rationalized)? Precision ≥75% target (lower threshold bo Wallat 2025 pokazuje że do 57% citations w real RAG systems są post-rationalized).
- *G-Cite vs P-Cite distinction* (arXiv 2509.21557 holistic eval) — implementuj jeśli czas pozwoli w Iter. 4 ablation.
- *Falsyfikowalność:* faithfulness <70% lub correctness <60% = FAIL. Threshold range = INCONCLUSIVE. Both ≥target = PASS.
- *Baseline:* RAGAS faithfulness ~0.75, expected post-hoc NLI alignment cooperative ≥0.85 faithfulness, ≥0.75 correctness.

**RQ3/H3 (continuous improvement convergence).** Czy continuous retraining loop probe (3 cykle) **konwerguje** — każdy cykl zwiększa AUROC lub plateau, brak regresji w >50% cykli?
- *Falsyfikowalność:* regresja w 2 z 3 cykli = FAIL (loop niestable). Plateau po cyklu 2 z cyklem 3 ≤2pp = PASS. Monotonic improvement = STRONG PASS.

### Supporting

**RQ4/H4 (verifier quality).** Czy programatic NLI verifier (HerBERT-large NLI lub sdadas/polish-nli) osiąga ≥75% agreement z manual labels na 100 par eval set dla (claim, evidence) → entailed/contradicted/neutral?
- *Falsyfikowalność:* <60% agreement = FAIL (verifier zbyt słaby, fallback na LLM-judge). ≥75% = PASS.

**(RQ5 deprecated — Magda decision 2026-05-16 + plus literature evidence: Dubanowska EMNLP 2025 + Vaddi 2026-03 pokazują że OOD generalization probe'ów jest OUT OF REACH dla SOTA. Cross-domain test byłby near-random — nie wniósłby wartości. Pozostają 3 main + 1 supporting RQ.)**

---

## II.4 Strategia danych

### II.4.1 Korpus — Polish CitationBench v0.6 (BUILT 2026-05-16, post-Wariant B cleanup)

**Output:** `main_project/data/processed/citationbench_v0.6_2026-05-16/` (chunks.jsonl 24 MB + halu_pairs.jsonl 7.9 MB + DATASET_CARD.md). Per-Wariant B audit: input 17,862 → kept 11,000 (61.6%) + dropped 6,862 (38.4%) per `notes/scope_cleanup_decisions_2026-05-16.md`.

| Komponent (source_type) | count | source dominant |
|---|---|---|
| `legal_statute` (ISAP ELI) | 2,541 | isap.sejm.gov.pl |
| `qa_raw` (real consumer questions) | 2,945 | forumprawne / e-prawnik / reddit / eporady24 / federacja / konsument.gov.pl / ... |
| `legal_document_pdf` (UOKiK/RF/FK poradniki) | 1,965 | rf.gov.pl + uokik.gov.pl + federacja-konsumentow + uodo + cik.uke + knf |
| `legal_ue_directive` (EUR-Lex) | 1,360 | eur-lex.europa.eu |
| `encyclopedic` | 1,167 | wikipedia (CC BY-SA — share-alike caveat) |
| `legal_court_judgment` | 534 | orzeczenia.ms.gov.pl |
| `qa_gold` (UOKiK Q&A scraped) | 433 | prawakonsumenta.uokik.gov.pl + ekspansja |
| `legal_tsue_judgment` | 29 | EUR-Lex CURIA |
| `legal_uokik_decision` | 26 | uokik.gov.pl decyzje |
| **Unified chunks total** | **11,000** | — |
| **Synthetic halu pairs** | **5,402** | Bielik+injection 5 typów; balanced; factual_fabrication=NEUTRAL, reszta CONTRADICTED |
| **Manual gold standard** | UOKiK Q&A 60 par ready-made (✓ DONE) + ~50-100 par hand-annotated by autorka (Magda weekend hyperfocus) → ~110-160 total | Magda + agent |

### II.4.2 Halu injection strategy (5 typów)

Każdy typ z jasną definicją operacyjną + skript-based generator:

| Typ | Definicja | Przykład |
|---|---|---|
| **Factual fabrication** | LLM dodaje claim którego NIE ma w retrieved context | „Ustawa daje 60 dni na zwrot" gdy ustawa mówi 14 |
| **Entity confusion** | LLM myli podmioty/instytucje | „UOKiK rozpatruje reklamacje" gdy faktycznie sprzedawca |
| **Temporal drift** | LLM podaje błędną datę / okres | „Zgodnie z ustawą z 2020" gdy ustawa z 2014 |
| **Negation flip** | LLM odwraca sens (zamienia „mogę" na „nie mogę") | „Konsument nie ma prawa do zwrotu" gdy ma |
| **Paragraph mis-citation** | LLM cytuje art. X ale treść z art. Y | „Per art. 27 — masz 14 dni" gdy art. 27 mówi o czymś innym |

### II.4.3 Programatic NLI labeling — 3-tier strategy

**Tier 1 — production default ✓ T1 PASS 2026-05-16 (DEC-004):** **`MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`**
- Polish **explicitly w training set** (27 langs, NIE tylko cross-lingual transfer)
- 0.3B params, MIT license, 275k downloads/mo
- **CONFIRMED: 80.6% accuracy** na 93 par v0.6 sanity check (lokal CPU, 2026-05-16 11:55)
- Per-class P/R: contradicted P=1.000/R=0.766 (perfect precision); entailed P=0.800/R=0.706; neutral P=0.643/R=0.931 (model conservative — over-predicts neutral)
- Critical finding: model wymaga `_HALU_TYPE_NLI_LABEL` map fix — `factual_fabrication` mutation (dodaje fikcyjny fakt) NIE jest contradiction lecz *unsupported claim* = NLI poprawnie predict NEUTRAL. Po fix → PASS 80.6%.
- Production-friendly latency (~10 ms/inference)

**Tier 2 — accuracy upgrade (NIE wymagany TERAZ — T1 PASS):** **HerBERT-large + custom CDSC-E fine-tune**
- Status: NIE potrzebny dla MVP (T1 PASS 80.6%, próg ≥75% przekroczony +5.6pp)
- Reserved jako fallback jeśli probe training (Iter. 1) wykaże że Tier 1 niedostateczne dla downstream pipeline (np. wymagane wyższe precision dla rzadkich halu types)
- KLEJ leaderboard: 96.4% na CDSC-E (caveat: CDSC-E = image captions, domain shift do legal text obniża real accuracy do ~80-85%)
- Cost: ~1-2h na A100, ~$2-5
- License: CDSC-E CC-BY-NC-SA-4.0 (NonCommercial — OK badawczo, flag w R8 limitations + HuggingFace dataset card)

**Tier 3 — oracle baseline w ablations (NIE production):** **Bielik-11B-v3 few-shot prompting**
- 200-500ms latency, 100-200× drożej niż mDeBERTa
- Used jako **upper bound w R7 ablation A3** (verifier → LLM-as-judge) — pokazuje „co byłoby możliwe" gdyby compute nie był constraint
- Apache 2.0

**Validation methodology:** agreement z manual gold standard (UOKiK Q&A 50-200 par + 50-100 par autorki = ~100-300 total) — RQ4/H4 = ≥75% threshold. Decyzja Tier 1 → Tier 2 podejmowana w Iter. 0b POC checkpoint na podstawie sanity check 50 par UOKiK Q&A.

**Honest framing dla R8 limitations:** brak production-ready polish-specific NLI w 2026 — flag jako future work „polish NLI fine-tune jako standalone HuggingFace artifact dla społeczności polish NLP".

### II.4.4 Eval set design

- **Primary eval set:** ~110-160 par mix:
  - **UOKiK Q&A scrape — 60 par ready-made** (✓ DONE 2026-05-16; 55/60 z citations, 52 unique legal refs) — **ZERO manual annotation cost** dla tej części
  - Plus **50-100 par hand-annotated by autorka** dla diversity coverage (typy halu spoza UOKiK distribution: paragraph mis-citation, temporal drift, fabrication w less-covered areas typu RODO, prawo telekomunikacyjne edge cases)
- **Secondary eval set:** ~1000 par programatic (Bielik+NLI silver labels) + spot-check 5% (50 par) by autorka — dla larger-scale evaluation z confidence intervals.

---

## II.5 Architektura pipeline (CENTRALNY rozdział R5)

7 figur diagramów (Mermaid sources w R5):

1. **C4 Context (Diagram 1)** — system w otoczeniu (user → RAG → external sources ISAP/UOKiK/Reddit, internal services)
2. **C4 Container (Diagram 2)** — services (retriever Qdrant+TEI, generator Bielik+SGLang, probe extraction, verifier, citation alignment, observability stack)
3. **C4 Component (Diagram 3)** — probe training loop internals (hidden-states extraction → small classifier → MLflow tracking → A/B gate)
4. **Flow: ingestion (Diagram 4)** — ISAP scrape → UOKiK scrape → Reddit/fora questions → halu injection → NLI labeling → BGE-M3 embed → Qdrant index
5. **Flow: inference + citation alignment (Diagram 5)** — query → retrieval → Bielik generation → claim extraction → NLI verifier per claim → citation badge UI
6. **Flow: continuous improvement (Diagram 6)** — failure cases (probe alarm + verifier contradict) → preference dataset → probe retrain → A/B gate → deploy
7. **Sequence: drift detection trigger logic (Diagram 7)** — Evidently halu rate distributions → Alibi Detect KS/MMD → Prefect retraining trigger → MLflow registry update

Dodatkowo Figura 5.8 — Gradio UI mockup (3 zakładki).

---

## II.6 Modele

| Rola | Model | Rozmiar | Status | Uzasadnienie |
|---|---|---|---|---|
| Embedder | BGE-M3 | 568M | frozen | Multilingual, polish coverage, hybrid dense+sparse, MIT license |
| Generator RAG | Bielik 11B v3 | 11B | frozen | Apache 2.0, native polish, ~131k context (YaRN) |
| **Probe target** | Bielik 11B v3 (primary, lab GPU SP7 H200 80GB; fallback 1.5B/3B dla local CPU dev jeśli T4 lab GPU verify FAIL) | 11B (1.5-3B fallback) | hidden-states extracted | Confirmed PyTorch hooks compatible (50 layers × 4096 hidden, ~22 GB VRAM bf16). T3 lab GPU verify pending. |
| **Halu probe** | sklearn LogisticRegression linear primary (Liang & Wang Dec 2025 + Dubanowska EMNLP 2025) lub 1-3 layer MLP nonlinear w ablation | <10M | trained from scratch | Modern technique 2025-2026, single-pass, real-time |
| **Citation verifier (Tier 1) ✓ T1 PASS 80.6% 2026-05-16** | **MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7** (300M, MIT) — primary, polish explicit w training | 300M | frozen | **CONFIRMED 80.6% accuracy** na 93 par v0.6; per-class contradicted P=1.000/R=0.766 |
| **Citation verifier (Tier 2 — fallback, NIE wymagany teraz)** | **HerBERT-large + custom CDSC-E fine-tune** | 340M | LoRA fine-tune ~1-2h A100 | Reserved jeśli probe training Iter. 1 wykaże potrzebę wyższej precision; KLEJ 96.4% (ale CDSC-E domain shift do legal ~80-85%) |
| **Citation verifier (Tier 3 — oracle baseline + RQ4 supporting)** | **Bielik / PLLuM / Gemma 3 / Claude Haiku few-shot** | 11B+ | frozen | Ablation A3 jako upper bound + RQ4 supporting (LLM-judge kappa ≥0.50 vs manual labels) |
| **Tier 0 ablation (R7)** | gliclass-multilang-ultra | small | frozen | Alternative NLI baseline per `research/nli_models_2026_update.md` |
| Multilingual baseline (compare) | Lynx 8B (Patronus AI), HHEM 2.x (Vectara) | 8B / small | frozen | Baseline dla R7 comparison vs polish-trained probe |

---

## II.7 Citation grounding — methodology

### II.7.1 Post-hoc citation alignment (preferred)

Bielik generuje free-form polish answer. Osobny pipeline rozkłada answer na claims (sentence segmentation polish + claim extraction prompt). Per claim:
- Retrieve top-k evidence chunks z Qdrant
- NLI scoring per (claim, evidence) → entailed / contradicted / neutral
- Najlepszy evidence z entailment → citation badge

Plus per claim: hidden-states probe daje halu score (independent signal).

UI shows per-claim: kolorowany badge (zielony / żółty / czerwony) + linkowany evidence chunk.

### II.7.2 Generation-time citations (alternative, jeśli post-hoc nie wystarcza)

Bielik instruct-tuned (LoRA) na polish citation examples z explicit JSON schema output. Validation via Outlines / Instructor library.

Decyzja w Iter. 2 po empirical comparison.

---

## II.8 MLOps + observability

Stack (z v3.1, większość zostaje):
- **Orchestration:** Prefect 3 (async natywny)
- **Tracking:** MLflow + Optuna
- **Versioning:** DVC (datasets) + MinIO (raw)
- **Observability:** Langfuse (LLM-specific) + OpenTelemetry SDK + LGTM stack (Loki/Grafana/Tempo/Mimir) + Alertmanager
- **Drift detection:** Evidently (data + halu rate distributions) + Alibi Detect (statistical KS/MMD na hidden activations distributions)
- **A/B test gating:** MLflow Model Registry + custom A/B logic w Prefect flow

---

## II.9 Defense scaffolding (post-pivot)

3 mikro-podszepty zatwierdzone 2026-05-16 (post-DEC-003 adapt):

### 1. Ablation studies w cyklu 1 (R6 + R7)

Cykl 1 retreningu probe ma uwzględniać 4 ablacje:

| Ablacja | Wariant | Cel diagnostyczny |
|---|---|---|
| **A0 (baseline)** | Probe na last 3 hidden layers + NLI verifier (HerBERT-large) + Bielik 11B generator + post-hoc citation | Pełen pipeline reference |
| **A1: probe → semantic entropy** | Klasyczny semantic entropy (Farquhar 2024) zamiast hidden-states probe | Czy hidden-states bije classic uncertainty? |
| **A2: probe target → mniejszy / większy Bielik** | Probe na Bielik 1.5B vs 3B vs 11B activations | Trade-off compute vs detection quality |
| **A3: verifier → LLM-as-judge** | Bielik 11B z few-shot prompting zamiast HerBERT NLI | Czy programatic NLI bije LLM-judge dla polish? |
| **A4: citation → generation-time** | Bielik instruct-tuned z structured output zamiast post-hoc alignment | Czy generation-time bije post-hoc dla polish? |

Każda ablacja = osobny MLflow run, osobny wynik R7.

### 2. Kategoryczna error analysis (R7)

Po każdym cyklu: kategoryzacja ≥100 błędów per typ:

| Kategoria | Definicja operacyjna |
|---|---|
| **Factual fabrication** | LLM claim NIE w retrieved context, probe NIE alarm |
| **Entity confusion** | LLM myli podmioty, probe nie alarm |
| **Temporal drift** | LLM błąd daty/okresu, probe nie alarm |
| **Negation flip** | LLM odwraca sens, probe nie alarm (subtle) |
| **Paragraph mis-citation** | art. X cited ale treść z art. Y |
| **Ambiguous claim** | claim multi-interpretable, multiple evidence equally plausible |

### 3. 5-wymiarowa kontrybucja (R8)

W R8 explicit zapisz rozdzielność kontrybucji:

> Wkład pracy ma pięć niezależnych wymiarów:
> 1. **Metodologiczny:** pierwszy publicznie udokumentowany polish hallucination detection methodology (audit trail dla polish landscape — Mu-SHROOM 2025 pominął)
> 2. **Inżynierski:** reprodukowalny pipeline citation-grounded RAG + halu probe + verifier (open-source)
> 3. **Artefaktowy:** trzy modele/datasety na HuggingFace (CitationBench dataset + halu probe model + citation verifier)
> 4. **Eksperymentalny:** porównanie hidden-states probe vs multilingual baselines (Lynx, HHEM) na polish corpus
> 5. **Korpusowy:** pierwszy polish CitationBench dataset z deterministic citation grounding (ISAP-based)
>
> Każdy z pięciu wymiarów broni się niezależnie. W przypadku odrzucenia H1 (probe AUROC <0.70 lub bootstrap CI lower <0.60), kontrybucje (2)-(5) stoją niezależnie — z szczególnym wyróżnieniem dataset jako standalone publishable artifact.

---

## II.10 Out of scope / future work

1. **Doradztwo prawne** — informational only, NIE legal advice. Disclaimer mandatory w UI.
2. **Real-time production deployment z user traffic** — out of scope, simulated drift only.
3. **Cross-language transfer** — polish-only, inne języki UE = future work.
4. **Reranker fine-tuning** — passé per Iter. 0a feasibility (v3.1 archived).
5. **Full fine-tuning Bielika** — probe NIE LoRA pełna; LoRA dla verifier OK ale generator frozen.
6. **Multi-turn chat formal evaluation** — implicit chat działa via LlamaIndex ChatEngine memory; formal multi-turn coherence eval = future work.
7. **Cybersec angle (adversarial halu)** — może być future work R8 (probe wykrywa halu wywołane przez prompt injection); nie central.
8. **Cross-domain stress test** (RQ5 supporting) — opcjonalne R7 sub-eksperyment, NIE wymagane.

---

## II.11 Iteration plan (8 iteracji, ~10-11 tygodni speed-run)

| Iter. | Czas | Magda robi | Agenty robią |
|---|---|---|---|
| **0b** | DONE 2026-05-16 (PARTIAL) | Sign-off na temat ✓ + halu type taxonomy ✓ + Wariant B cleanup ✓ + T1 mDeBERTa sanity ✓ PASS 80.6% | DEC-003 + DEC-004 + konspekt v3.2 (TEN PLIK) + Polish CitationBench v0.6 (11,000 chunks + 5,402 halu pairs) + halu_injector fix factual_fabrication=NEUTRAL + Wariant B scope filter (drop 38.4%); **Pending lab GPU:** T2 Outlines+Bielik diakrytyki + T3 PyTorch hooks layer 47 + T4 lab smoke inference |
| **1a** | 1 tydz | Konfiguruje scrape (które ustawy in/out scope, fora wybór) | Scrape ISAP + UOKiK + Reddit/fora, format do HF datasets |
| **1b** | 1 tydz | **100 par manual gold standard** (weekend hyperfocus burst) | Halu injection script (5 typów) → ~5-10k synthetic pairs + NLI labeling pipeline + EDA notebook + R3 Dane draft skeleton |
| **2** | 2 tydz | Probe training (PyTorch hooks Bielik, hyperparam Optuna) + verifier training (HerBERT NLI LoRA) | Boilerplate code + monitoring scripts + R6 Modele draft skeleton |
| **3** | 1 tydz | Continuous improvement loop config (cykle 1-3) | Loop scaffolding + drift detection setup + R5 Architektura diagrams (Mermaid) |
| **4** | 1 tydz | Probe ablations (probe target size, layer choice, hidden vs entropy) + szlifowanie metryk | Eval scripts + R7 Wyniki tabele scaffolding |
| **5** | 1 tydz | Drift simulation methodology + Mirage critique address | Bibliografia research + citation pass + R7 text draft |
| **6** | 1 tydz | Gradio app polish (Magda wpinasz real models) | Gradio skeleton (3 zakładki) + HuggingFace dataset/model card publishing |
| **7** | 2 tydz | Writing review + decisions per sekcja | R1+R2+R8 drafty + cross-draft review + bibliography polish |
| **8** | 1 tydz | Final review, submit | PJATK formatting (TNR 12pt, IEEE footnotes), abstract PL+EN |

**Iteration-based, NIE time-based** (per Magda decision 2026-05-16: „nie patrz na czas, planuj iteracjami"). Każda iteracja ma jasne done criterion + agent task split. Magda kontroluje kadencję per własny speed-run mode + flow.

**Compress możliwy** (jeśli ona zdecyduje na MVP): skip Iter. 4 ablations, simpler drift, focus na probe + verifier + Gradio jako minimum viable.

---

## II.12 Strategia rozmowy z promotorem

Defense narrative dla DEC-003 pivot (drugi pivot po DEC-001):

> „Po wykonaniu Iteracji 0a feasibility test (URPL probe 100 par) ujawniliśmy że ChPL/Ulotki mają sztywną semantykę regulatorową — alignment 100%, perfekcyjny dla baseline retrieval. Konsekwencja: fine-tuning rerankera dałby marginalną poprawę (~2pp), H1 z konspektu v3.1 (≥10pp) odpadłby z trywialnego powodu. Plus paralelne sources research wykazało **Mu-SHROOM 2025 pominął polski** — realna luka w polish landscape z first-mover opportunity. Pivot na hallucination detection + citation grounding zachowuje 70% pracy v3.1 (cały stack MLOps, observability, drift detection — Pana sweet spot, mindset MLOps applied to LLM quality control), zmienia central komponent z reranker fine-tuning na hidden-states halu probe. Use case practical: production RAG dla domen krytycznych z citation requirement (mój zawodowy obszar). Pełen audit trail w `decisions/DEC-003`."

Argumenty pomocnicze:
- **Reuse 70%** — promotor nie traci poprzedniego nakładu
- **Pana sweet spot zachowany** — MLOps + continuous improvement + observability + drift + A/B gating
- **Practical relevance** (use case z mojej pracy zawodowej, manager zafascynowany)
- **3 publishable artefakty** standalone na HuggingFace
- **Polish-first** — pierwszy publicznie udokumentowany w polskim landscape
- **Modern technique** — hidden-states probes 2025-2026 frontier

---

## Zakończenie

Konspekt v3.2 jest *living document* — szkielet do uszczegółowienia w trakcie iteracji. Zmiany:
- Przed Iter. 1: sign-off na 5 typów halu + scrape scope
- Po Iter. 1: refresh dataset numbers (real vs estimate)
- Po Iter. 2: probe results + decision na ablation A2 (probe target size)
- W Iter. 7: pełen draft R1-R8 powstaje z tego skeleton
