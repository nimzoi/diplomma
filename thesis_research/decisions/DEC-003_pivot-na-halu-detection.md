# DEC-003: Pivot na hallucination detection + citation grounding + consumer rights

**Data:** 2026-05-16
**Status:** ACCEPTED (ACTIVE)
**Autorka:** Magdalena Sochacka
**Supersedes:** DEC-001 (rotacja psych → farma), DEC-002 (ChPL+Ulotka cross-register pairing)
**Related:** Iteracja 0a feasibility evidence (`_archive/v3-pharma-reranker/iter0_feasibility/`), `research/halu_detection_sota_2024_2026.md`

---

## Kontekst

Po przyjęciu DEC-001 (farma + reranker fine-tuning, 2026-05-15) i wykonaniu Iteracji 0a feasibility test (2026-05-16) ujawniły się trzy istotne problemy które wymagają strategicznego pivotu:

1. **Empiryczny: dataset za prosty dla nontrivial reranker improvement.** Iteracja 0a smoke test (100 par) potwierdził że ChPL/Ulotki mają **sztywną semantykę regulatorową** (frazeologia EMA QRD, deterministyczna struktura 10 sekcji, alignment 100% na complete-pair pool 12,973). Fine-tuning rerankera na takim corpusie da marginalną poprawę (~2pp nDCG@10) — H1 z konspektu v3.1 (≥10pp) odpadnie nie dlatego że reranker nie umie, tylko że problem mechanicznie zbyt łatwy. Negative-result z trywialnego powodu, NIE z metodologicznego insight.

2. **Trendowy: reranker fine-tuning jako central kontrybucja jest passé w 2025-2026.** Per `research/halu_detection_sota_2024_2026.md`, ciężar field przesunął się z fine-tunowania małych cross-encoder rerankerów na (a) lepsze embeddery z hybrid retrieval (BGE-M3, Qwen3-embedding), (b) LLM-as-reranker (większy model robi rerank w jednym call), (c) generative retrieval (GenIR), (d) hidden-states probes dla LLM quality control. Praca o reranker fine-tuning ryzykowałaby framing jako „mainstream 2022" zamiast „frontier 2025-2026".

3. **Motywacyjny: autorka straciła sense pracy.** Bez intrinsic motivation („nie umiem działać kiedy nie widzę sensu") postęp wszedł w paraliż 2026-05-16 wieczorem. Praca dyplomowa wymaga 2-3 miesięcy intensywnej pracy autorki — bez sensu nie da się tego utrzymać. To NIE jest sygnał o słabości autorki, to konsekwencja architektonicznego błędu w doborze tematu (DEC-001 motywowane „neutralnym ramowaniem zewnętrznym dla promotora", NIE intrinsic interest).

Plus pomocnicze:
- Sources research (post-DEC-001 in flight) zidentyfikował **wielowymiarową lukę w polish hallucination detection landscape** — Mu-SHROOM 2025 SemEval Task 3 pominął polski (14 języków bez PL), brak polish-specific Lynx / HHEM / FaithJudge equivalent, brak polish HaluBench. Realna luka z first-mover opportunity dla polish-first thesis.
- Autorka pracuje zawodowo jako AI engineer z konkretnym use case: **„LLM w miejscach gdzie nie możemy halucynować + chcemy dobrego cytowania źródeł"**. Direct alignment z hallucination detection + citation grounding kierunkiem.

## Opcje rozważane

| Opcja | Co znaczy | Pros | Cons |
|-------|-----------|------|------|
| **A: Kontynuować v3.1 farma + reranker** | Bez zmian, dociągnąć obecny temat | Brak kosztów pivot; drafty już 70% napisane; promotor zna kierunek | H1 mechanicznie odpadnie; reranker passé; autorka w paraliżu; ryzyko że praca wyjdzie słaba mimo wykonanej pracy |
| **B: Reverse priority RQ5↔RQ1** | Cross-register (RQ5) jako central, reranker (RQ1) jako negative-result contrast | Mały pivot; reuse 100%; intellectual depth cross-register | Odrzucone przez autorkę 2026-05-16 jako „kompromis, NIE coś dobrego"; dalej framuje wokół rerankera (passé) |
| **C: Multi-agent RAG z continuous improvement** | Pełen redesign, multi-agent architecture | Frontier, ambitious | Total reset, brak reuse, wysoki koszt; może być zbyt szeroki dla thesis scope |
| **D: Continuous LoRA fine-tuning Bielik z critic-driven loop** | LoRA fine-tuning małego LLM z observability | Modern, MLOps central | Reuse partial; LoRA na LLM jest „wszyscy to robią" tier (Magda kryterium 1) |
| **E: Hallucination detection + citation grounding + consumer rights** | Hidden-states probe + post-hoc citation alignment + polish legal RAG | Frontier (probes 2025-2026); polish-first (Mu-SHROOM gap); citation grounding = enterprise hot; reuse stack 70%; direct alignment z pracą zawodową autorki; deterministic citation grounding (ISAP art. X.Y); bezpieczne dataset (synthetic + 100 par manual + agent-scrape-able) | Drugi pivot wymaga silnego defense argument dla promotora; hidden-states probe wymaga PyTorch hooks (autorka manual, NIE agent); ryzyko że promotor odrzuci „znowu pivot" |

## Decyzja

**Wybrana: Opcja E — Hallucination detection + citation grounding + consumer rights.**

**Tytuł roboczy v3.2:** *„Citation-grounded polish RAG z hidden-states hallucination probe — pipeline produkcyjny dla domen krytycznych (studium przypadku: prawa konsumenta)"*

## Uzasadnienie

### 1. Spełnia 8 kryteriów autorki (intrinsic motivation captured)

Autorka 2026-05-16 explicit sformułowała 8 kryteriów dla wybranego tematu. Opcja E wynik:

| # | Kryterium | Match |
|---|-----------|-------|
| 1 | Niepowtarzalny + nietrywialny | ✅ STRONG (hidden-states probes 2025-2026 frontier, polish-first w halu = realna luka, citation grounding = enterprise hot — trzy wymiary novelty) |
| 2 | Praktyczny aspekt | ✅ STRONG (enterprise RAG z citations to production use case, Gradio fizycznie demonstrowalny) |
| 3 | Czas + agent-rozkładalne | ⚠ MEDIUM-STRONG (dataset programatic, ALE hidden-states extraction wymaga PyTorch hooks autorki + 100 par manual ground truth) |
| 4 | Fascynujący dla autorki | ✅ STRONG (autorka explicit feedback „dobre to jest", łączy modern + niche + practical + work-relevant) |
| 5 | PJATK schema fit | ✅ STRONG (klasyczny dane→trening→eval, każdy assignment chapter pasuje schematycznie) |
| 6 | Promotor szybko ogarnie | ⚠ MEDIUM-STRONG (MLOps mindset = continuous loop probe + observability + drift = sweet spot ✓; ALE drugi pivot wymaga silnego defense — ten dokument adresuje) |
| 7 | Connection do pracy zawodowej | ✅ STRONG (direct match z use case autorki — production RAG dla domen krytycznych z citation requirement) |
| 8 | Konkretny use case z pracy (LLM bez halu + cytowanie) | ✅ STRONG (bezpośrednio adresuje) |

**6/8 STRONG, 2/8 MEDIUM-STRONG z świadomymi caveats** (czas/agents + drugi pivot).

### 2. Realna luka literaturowa w polish landscape

Per `research/halu_detection_sota_2024_2026.md`:
- **Mu-SHROOM 2025 SemEval Task 3** — multilingual hallucination detection dla 14 języków (czeski, fiński, hindi, etc.), **bez polskiego**.
- **PolEval 2025** — 4 taski (MGT detection, gender bias, layout, emotion), **żaden nie dotyczy halucynacji ani faktualności**.
- **Polish landscape:** istnieją tylko safety classifiers (PL-Guard, Bielik Guard) — NIE faithfulness / hallucination detection. Brak polish HaluBench. Brak polish-specific Lynx / HHEM / FaithJudge equivalent. Plus **6 luk w polish landscape** zidentyfikowanych w deep literature research (`research/literature_deep_2026.md`): polish halu dataset, polish hidden-states probe, polish NLI dla legal text, ContractNLI-PL equivalent, LegalBERT-PL, polish RAG eval framework.

To **realna first-mover opportunity** dla autorki — pierwszy publicznie udokumentowany polish hallucination detection methodology + dataset + probe model.

**Prior art acknowledgment:** 
- **UOKiK ARBUZ AI tool** (operational od 2023-01-01) — closed-source AI dla consumer rights używany przez UOKiK. Cytowany w R2 jako prior art (NIE konkurencja — closed-source, NIE halu detection focus). Differentiation Twojej pracy: open-source, halu detection central, citation grounding deterministic, polish-first benchmark publishable.
- **Wrocław Tech (Kazienko, Kocoń, Ferdinan) — CLARIN-PL grant 2024-2026** explicit halu detection focus. Wypuścili **AggTruth (ICCS 2025, arXiv 2506.18628)** — **ALE English-only** datasety (NQ, HotPotQA, CNN/DM, XSum). Po 24 miesiącach grantu NIE polish halu benchmark. **First-mover risk: MEDIUM** — możliwy 6-miesięczny counter z polish benchmark. **Mitigation:** defense niche framing (4 zwężające axes — Polish + citation-grounded + consumer rights + hidden-states probe), defensive lock-in (HF dataset release + DOI Zenodo + arXiv preprint pre-obroną).
- **OPI (Dadas) PIRB** — MEDIUM threat na retrieval side, NIE halu detection focus.
- **`mGarbowski/llm-projekt`** (educational student project — found via SpeakLeash bielik-tools research 2026-05-16) — używa **identyczny stack** (polish-reranker-roberta-v3 + Bielik v3 + bracket citations + 38-question eval). **Differentiation w R8 obowiązkowa:** (1) 11B vs ich 1.5B generator (7× większy), (2) pełen MLOps pipeline z drift detection (oni brak), (3) hidden-states halu probe (NEW, oni brak), (4) full thesis statistical rigor (oni educational toy).

**Defense niche framing (per PolEval research recommendations):** *„First publicly documented Polish citation-grounded RAG benchmark for consumer rights, with hidden-states hallucination probe on Polish LLM"* — 4 zwężające axes: (1) Polish vs multilingual, (2) citation-grounded vs halu only, (3) consumer rights vs legal broadly, (4) hidden-states probe na polish LLM vs LLM-judge / semantic entropy. NIE „first Polish halu benchmark" (zbyt szerokie, AggTruth follow-up mogłoby counter).

**Defensive lock-in actions (early publish strategy):**
1. **HF dataset release z DOI Zenodo** — submit w Iter. 6 (zamiast Iter. 8) dla early public disclosure
2. **arXiv preprint cs.CL+cs.IR** — 2 tyg. przed obroną dla timeline lock (citable date)
3. **R2 sekcja explicit polish halu landscape audit** cytując AggTruth + PIRB + Wrocław Tech + Mu-SHROOM polish gap — prevents reviewer ambush

**Legal basis dla scrape (legal background):** Polish **TDM exception (Wrzesień 2024)** — text and data mining exception w prawie autorskim. Plus Art. 4 PrAut public domain dla urzędowych. Dwa równoczesne legal grounding dla ISAP + UOKiK scraping — bezpieczne defense.

### 3. Reuse 70% pracy v3.1 (NIE marnujemy poprzednich miesięcy)

Co zostaje z v3.1:
- **Stack technologiczny:** Bielik 11B v3 (generator), BGE-M3 (embedder), Qdrant (vectors), PostgreSQL (metadata), Prefect 3 (orchestration), MLflow (tracking), Langfuse (observability), Evidently (drift), DVC (versioning), MinIO (storage), SGLang (serving), TEI (embedder serving), FastAPI, Gradio (UI)
- **MLOps methodology:** continuous improvement loop, A/B test gating, drift detection na embedding distributions + halu rate distributions, Optuna hyperparameter search, multi-stage validation
- **Judge methodology** (LLM-as-judge) — przekształcamy z reranker-judge na response-halu-judge i citation-verifier
- **Iteration plan structure** (8 iteracji per `02b_konspekt_v3_updates.md` § II.16) — adaptujemy do nowego tematu
- **Defense scaffolding** (3 mikro-podszepty) — adaptujemy: ablations, error analysis taxonomy, 5-wymiarowa kontrybucja
- **Writing rules** (z `thesis_elements/CLAUDE.md`) — bez zmian, applicable do nowego tematu
- **ChPL+Ulotka corpus z poprzedniej iteracji — explicit NIE używany w v3.2** (Magda decision 2026-05-16: „już tej ulotki nie mieszajmy"). Pozostaje w archive jako historical record.

Co odpada z v3.1:
- Reranker fine-tuning jako central komponent (zostaje base reranker w RAG, ale NIE fine-tunowany)
- Cross-register retrieval (RQ5) jako central — może wrócić jako optional R7 sub-eksperyment
- Sources_catalog farma (6 strata pharma) — superseded przez consumer rights corpus (ISAP + UOKiK + Reddit)
- Training_dataset_spec dla reranker quadruplets — superseded przez halu detection dataset spec (claim, evidence) → faithful/hallucinated labels

### 4. Defensible defense argument dla promotora (drugi pivot)

Defense narrative dla rozmowy z promotorem mgr inż. Piotrem Kojałowiczem:

> „Po wykonaniu Iteracji 0a feasibility (test pre-conditions URPL na 100 par leków) ujawniliśmy że ChPL+Ulotka mają sztywną semantykę regulatorową — alignment 100%, perfekcyjny dla baseline retrieval. Konsekwencja: fine-tuning rerankera dałby marginalną poprawę (~2pp), H1 odpadłby z trywialnego powodu (problem za łatwy), nie z metodologicznego insight. Plus paralelne sources research wykazało że Mu-SHROOM 2025 (multilingual halu detection benchmark) **pominął polski** — realna luka w polish landscape z first-mover opportunity. Pivotowanie zachowuje 70% pracy v3.1 (cały stack MLOps, observability, drift detection — pana sweet spot, mindset MLOps applied to LLM quality control), zmienia central komponent z reranker fine-tuning na hidden-states halu probe + citation grounding pipeline. Use case practical: production RAG dla domen krytycznych z citation requirement (mój zawodowy obszar). Pełen audit trail w DEC-003."

Kluczowe punkty defense:
- **Empiryczne evidence** (Iteracja 0a numbers) — NIE „wymyśliłam że nie pasuje", tylko „test pokazał"
- **Literature gap evidence** (Mu-SHROOM 2025 pominął polski) — measurable rationale
- **Reuse 70%** — promotor nie traci poprzedniego nakładu
- **Pana sweet spot** (MLOps mindset zachowany — applied to LLM quality control)
- **Practical relevance** (use case z mojej pracy)

Risk acceptance: **10-20% prawdopodobieństwo** że promotor odrzuci pivot („znowu zmieniasz"). Mitigacja: prezentacja w formie *re-framing* zachowującego ducha pracy (MLOps + continuous improvement + observability) z conservative scope (3 main + 2 supporting RQ zamiast 5).

### 5. Modern technique — hidden-states probes

Per `research/halu_detection_sota_2024_2026.md`, SOTA przesunął się od semantic entropy (Farquhar Nature 2024) na **hidden-states probes** — cheap, single-pass, real-time inference, AUROC 0.85-0.92 z probe na last 2-3 hidden layers. Linia rozwoju: Semantic Entropy → SEP (NeurIPS 2024) → Semantic Energy (sierpień 2025) → real-time span-level probes (Obeso et al. 2025-2026). To 2025-2026 frontier, NIE crowded space.

### 6. Three publishable artifacts (defensible standalone)

Po obronie pracy autorka zostaje z trzema fizycznymi artefaktami publishable na HuggingFace:
1. **Polish CitationBench dataset** — pierwszy publicznie udokumentowany polish citation-grounded halu benchmark
2. **Polish hallucination probe model** — pierwszy hidden-states probe trenowany na polish LLM
3. **Polish citation verifier** — NLI-based verifier dla polish (claim, evidence) → entailed/contradicted/neutral

Każdy artifact standalone publishable, link na model card pokazuje praktyczną wartość pracy.

## Konsekwencje

### Pozytywne

- ~10-15k pairs realnego corpus z public sources (ISAP + UOKiK + Reddit) achievable w 2-3 tygodnie z agentami
- 3 publishable artefakty na HuggingFace
- Reuse 70% pracy v3.1 (stack, MLOps, observability)
- Direct alignment z pracą zawodową autorki (manager zafascynowany, możliwy deploy w pracy po obronie)
- Polish-first first-mover advantage (Mu-SHROOM 2025 pominął polski)
- Modern technique (hidden-states probes 2025-2026, NIE passé)
- Intrinsic motivation autorki captured (sense jasny, sense → flow)
- Defense scaffolding (5-wymiarowa kontrybucja) zaadaptowana — każdy z 5 wymiarów broni się niezależnie nawet przy odrzuceniu H1

### Negatywne / koszty

- **Trzeci pivot** — wymaga silnego defense argument dla promotora (10-20% odrzucenia ryzyka)
- Hidden-states extraction wymaga PyTorch hooks autorki (NIE agent-friendly task)
- 100 par manual gold standard wymaga weekend hyperfocus burst autorki
- Nowy konspekt v3.2 do napisania (~3 godziny)
- Drafts v3.1 (R1-R8 farma+reranker) zarchiwizowane — będą reusable strukturalnie ale prose nie do bezpośredniego użycia
- Ustawa o prawach konsumenta jest niewielka (~80 artykułów) — corpus chunks ograniczone, wymaga uzupełnienia (Kodeks cywilny, UOKiK, fora) dla wystarczającego material

### Neutralne (bez zmian)

- Stack technologiczny (Bielik, Qdrant, Prefect, MLflow, Langfuse, Evidently, etc.) — większość zostaje
- MLOps methodology — bez zmian
- Iteration plan structure (8 iteracji) — adaptujemy do nowego tematu
- Writing rules + Defense scaffolding (z `thesis_elements/CLAUDE.md`) — applicable do każdego tematu
- PJATK formatting requirements (TNR 12pt, IEEE footnotes, hardbinding) — bez zmian

## Kill criteria

Decyzja DEC-003 zostanie podważona jeśli:

- **ISAP scrape okaże się niefeasible** — np. URL pattern niestable, format trudny do parse, license wymaga negocjacji. Patrz `research/domain_A_feasibility.md` dla weryfikacji.
- **Polish NLI models nieadekwatne** — jeśli HerBERT-large NLI / sdadas-polish-nli daje <60% agreement na polish legal text, pipeline citation grounding nie zadziała programatycznie i wymaga LLM-judge (cost + latency overhead).
- **Hidden-states probe nie konwerguje** w Iter. 2 (probe AUROC <0.65 vs random baseline 0.50) — wtedy fallback na semantic entropy approach (Farquhar 2024) lub classifier-based detector.
- **Promotor explicit odrzuca pivot** jako „kolejny chaos" — wtedy rollback do v3.1 farma + reranker (drafts zachowane w archive) + reverse-priority RQ5↔RQ1 (Opcja B) jako kompromis.
- **Reddit API rate limits / scrape blokowane** — wtedy redukcja real questions do auto-generated z ustaw + fora scrape only.
- **Czas insufficient** — jeśli scope okazuje się 12+ tygodni a autorka ma <8 tygodni, redukcja: skip Iter. 4 cross-domain stress test, skip drift simulation, focus na probe + verifier + Gradio jako MVP.

## Audit trail

| Data | Wydarzenie |
|---|---|
| 2026-05-02 | v1 administracja rejected przez promotora |
| 2026-05-06 | v2 prompt injection rejected przez promotora |
| 2026-05-07 | v3 psychiatria committed jako FINAL |
| 2026-05-10 | feasibility psychiatria confirmed (raport_feasibility_psychiatria.docx) |
| 2026-05-15 | DEC-001 rotacja psych → farma; DEC-002 ChPL+Ulotka cross-register pairing |
| 2026-05-16 | Iteracja 0a smoke test wykonany (URPL probe 100 par): alignment 100%, OCR 17%, kill criteria NOT activated |
| 2026-05-16 | 8 chapter drafts napisane (R1-R8 farma+reranker, Track 1+2 fan-out) |
| 2026-05-16 | Cross-review agent verdict: NEEDS FIXES (16 issues identified) |
| 2026-05-16 | Cross-review fixes applied (16/16) |
| 2026-05-16 wieczorem | Autorka zgłasza paraliż: „nie umiem działać kiedy nie widzę sensu" + diagnoza farma+reranker = trywialny problem + reranker passé |
| 2026-05-16 | Sources research SOTA halu detection (`research/halu_detection_sota_2024_2026.md`) — Mu-SHROOM polish gap potwierdzony |
| 2026-05-16 | Autorka definiuje 8 kryteriów dla nowego tematu |
| 2026-05-16 | Wybór domain A (consumer rights) z opcji A/B/C/D — agent decyzyjny per data feasibility + agent automatability |
| 2026-05-16 | **DEC-003 ACCEPTED — pivot na hallucination detection + citation grounding + consumer rights** |
| 2026-05-16 | Cleanup projektu — v3.1 materials archived w `_archive/v3-pharma-reranker/` |
| 2026-05-16 | Domain A feasibility research agent spawned (in progress) |

## Powiązane

- **DEC-001**: Historical, superseded
- **DEC-002**: Historical, superseded; cross-register może wrócić jako optional R7 bonus eksperyment
- `research/halu_detection_sota_2024_2026.md`: SOTA evidence + polish gap rationale
- `research/domain_A_feasibility.md`: Feasibility verification dla ISAP + UOKiK + Reddit + polish NLI (in progress)
- `02_konspekt_v3.2_skeleton.md`: Nowy konspekt post-pivot
- `_archive/v3-pharma-reranker/`: Pełen archive v3.1 jako historical evidence
