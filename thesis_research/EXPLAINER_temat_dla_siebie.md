# Co właściwie robisz w tej pracy — explainer dla siebie

**Status:** *internal narrative document, NIE część pracy dyplomowej*. Pisany prostym językiem dla orientacji autorki.
**Data:** 2026-05-16 (post-DEC-003)
**Cel:** żebyś zawsze wiedziała w jednym miejscu „o co tu chodzi", bez dłubania w konspekcie.

---

## 1. O co chodzi w jednym akapicie

Budujesz **system wyszukiwania informacji o prawach konsumenta po polsku**, który (a) odpowiada na pytania użytkownika z **dokładnym wskazaniem źródła** (art. X ust. Y konkretnej ustawy), (b) **wykrywa kiedy się halucynuje** — czyli kiedy model wymyśla coś czego nie ma w przepisach. Plus pokazujesz że taki system **sam się ulepsza** w czasie (continuous improvement loop). Dlaczego polskie prawa konsumenta — bo (i) mało kto to robił po polsku, (ii) ustawy są strukturalne (idealne do citation grounding), (iii) realny problem (każdy kupujący online to przeszedł), (iv) Twoja praca zawodowa też dotyczy production RAG z citation requirement.

---

## 2. Dlaczego to jest ciekawe (i nie „kolejny prosty klasyfikator")

### Halucynacje LLM są problemem #1 dla production AI

Każdy używał ChatGPT/Claude i wie że **modele kłamią z pewną siebie** — wymyślają fakty, daty, paragrafy ustaw, źródła. W konsumenckim chatbocie to denerwujące. W medycynie / prawie / finansach to **niebezpieczne**. Rynek production LLM (Twoja praca to potwierdza) wymaga rozwiązań:
- Citation grounding (każde zdanie odpowiedzi musi być wsparte cytacją do źródła)
- Halu detection (model sam mówi „hej, tu nie jestem pewny")
- Continuous monitoring (system widzi gdy halu rate rośnie i alarmuje)

### Polish landscape ma realną lukę

Z research agent (`research/halu_detection_sota_2024_2026.md`):
- **Mu-SHROOM 2025** (główny multilingual halu benchmark) — 14 języków, **bez polskiego**
- **PolEval 2025** — żaden z 4 tasków nie dotyczy halucynacji
- W polish landscape istnieją tylko safety classifiers (PL-Guard, Bielik Guard) — to **inny problem** (toxicity / harmful content), NIE faithfulness

To znaczy że publikujesz **pierwszy publicznie udokumentowany polish hallucination detection methodology + dataset + probe model**. To nie jest „mainstream 2022 reranker" — to jest first-mover w polish frontier.

### Hidden-states probes to modern technique 2025-2026

Klasyczne approach do halu detection:
- **Wczesne (2020-2023):** prompt LLM-judge, pytaj „czy ta odpowiedź jest faktyczna?". Wolne, drogie, niespójne.
- **Semantic entropy (Farquhar Nature 2024):** generuj wiele samples, mierz jak bardzo się różnią semantycznie. Drogie (multiple samples per query).
- **Hidden-states probes (2024-2026):** trenuj mały klasyfikator nad ukrytymi aktywacjami LLM. **Single-pass, real-time, cheap.** State-of-the-art teraz.

Twoja praca robi hidden-states probe **dla polskiego LLM (Bielik)**. Nikt jeszcze tego publicznie nie zrobił.

---

## 3. Architektura w skrócie (4 komponenty + 1 pętla)

### Komponent 1: RAG generator (Bielik)

Standard. User pyta po polsku → embedder (BGE-M3) wyszukuje top-k evidence chunks z corpusu → Bielik 11B generuje odpowiedź na podstawie chunks. To jest baseline, nic specjalnego.

### Komponent 2: Citation grounding

Po generacji odpowiedzi:
- Rozkładasz odpowiedź na pojedyncze claims (zdania faktualne)
- Per claim → pytasz NLI model „czy ten claim wynika z któregoś z retrieved chunks?"
- Jeśli tak → przypisujesz cytację do tego chunk
- Jeśli nie → flag „no support found" (halucynacja!)

W UI każdy claim dostaje **kolorowy badge** z linkowanym evidence: zielony grounded, żółty uncertain, czerwony halucynacja.

**Po co NLI a nie embedder do tego?** Embedder mówi „chunk X jest podobny do query" (semantic similarity). NLI mówi „claim Y faktycznie wynika z chunk X" (logical entailment). To są **różne pytania**. Dla halu detection musisz pytać o entailment, NIE similarity.

### Komponent 3: Hidden-states halu probe

Niezależny od NLI sygnał. Podczas gdy Bielik generuje każdy token, **podsłuchujesz jego ostatnie 2-3 warstwy ukryte** (poprzez PyTorch hooks). Mały klasyfikator nauczony na (hidden_state, label_halu_yes_no) przewiduje — czy to wygenerowane słowo prawdopodobnie jest halucynacją?

Dlaczego to działa? Hidden states zawierają „self-knowledge" modelu — kiedy LLM zmyśla, jego ukryte stany różnią się od tych gdy mówi prawdę. To było zaskoczenie w research 2023-2024 — *modele „wiedzą" że kłamią, tylko zwykle nie mówią*. Probe to wyciąga.

### Komponent 4: Ensemble

Per claim masz 2 niezależne sygnały:
- NLI verifier score (post-hoc z evidence)
- Probe score (z generation hidden states)

Łączysz je w final halu confidence (np. weighted avg lub trained meta-classifier). Wyższa confidence = większa pewność że to halucynacja.

### Pętla: continuous improvement

Co jakiś czas:
- Zbierasz failure cases (probe alarmował + user kliknął „błędne" lub NLI kontradicted)
- Te trafiają do preference dataset
- Retrain probe na rozszerzonym dataset
- A/B test new probe vs old
- Deploy lepszej

To jest MLOps centralny — system **sam się poprawia** w czasie. Magnetic dla Twojego promotora (mindset MLOps).

---

## 4. Dane (skąd to wszystko wziąć)

### Corpus (~500-1500 chunks ustaw)

**ISAP/ELI API** (`api.sejm.gov.pl/eli`) — official polish ustawy, deterministic URL per art./§/ust./pkt. Public domain (Art. 4 PrAut). Pobierasz:
- Ustawa o prawach konsumenta z 2014 (Dz.U. 2014 poz. 827) — 80 artykułów
- Kodeks cywilny art. 535-581 (sprzedaż, rękojmia, gwarancja) — kilkaset chunks
- Ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym (2007)
- Ust. o RODO PL
- Plus opcjonalnie ustawy pokrewne

**UOKiK** — decyzje + raporty edukacyjne ze strony.

### Evaluation pairs (~100-300 par gold standard)

**🎁 Goldmine: UOKiK Q&A** — `prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/` ma **~50-200 ekspert Q&A pairs z explicit cytacjami** do KC + Ustawy. To są **gotowe gold standard pairs** — nie musisz manualnie annotate. Eliminuje ~połowę pracy.

Plus **50-100 par hand-annotated by Ty** dla diversity (typy halu spoza UOKiK distribution — np. paragraph mis-citation, temporal drift). Weekend hyperfocus burst.

### Real consumer questions (~2-4k/miesiąc)

- **Reddit r/Polska, r/Polish** — pobierane z Pushshift dumps via Academic Torrents (Reddit live API jest zablokowane, ale archive 5-15 GB compressed dla r/Polska slice działa)
- **e-prawnik.pl** — sekcja ochrona-konsumenta (970 wątków, scrape OK)
- **forumprawne.org** — 2436 stron paginacji
- Plus auto-generated z ustaw (z każdego art. → pytanie o jego treść)

### Synthetic halu pairs (~5-10k)

Skrypt który bierze prawdziwe Q&A pair z UOKiK + losuje typ halu z 5 kategorii:
- **Factual fabrication:** dodaj claim którego nie ma w evidence
- **Entity confusion:** zamień podmiot („sklep" → „UOKiK")
- **Temporal drift:** zmień datę („z 2014" → „z 2020")
- **Negation flip:** odwróć sens („masz prawo" → „nie masz prawa")
- **Paragraph mis-citation:** cytuj art. X ale treść z art. Y

Programatic, agent-runable. Daje Ci tysiące syntetycznych przykładów halucynacji do trenowania probe.

---

## 5. Co dostajesz na koniec (3 fizyczne artefakty + 1 demo)

### Artefakt 1: Polish CitationBench dataset (HuggingFace)

Pierwszy publicznie udokumentowany polish citation-grounded halu benchmark. Format: `(query, retrieved_chunks, generated_answer, per_claim_label_faithful_or_halu, citation_span_in_evidence)`. ~10-15k pairs.

**Komu się przyda:** każdy researcher polish NLP może pobrać i evaluate własne modele. Plus dla Ciebie — model card link → praktyczny output który manager zobaczy.

### Artefakt 2: Polish hallucination probe model (HuggingFace)

Trained probe (small classifier nad hidden states Bielika 1.5B/3B). Wagi + config + przykłady użycia. Pierwszy hidden-states halu probe dla polskiego LLM publicznie.

### Artefakt 3: Polish citation verifier (HuggingFace)

mDeBERTa NLI fine-tuned (lub HerBERT-large NLI custom fine-tune jeśli mDeBERTa za słabe na polish legal). Plus model card.

### Artefakt 4: Gradio demo z 3 zakładkami

- **Chat:** wpisujesz polish query → RAG odpowiedź z inline citation badges
- **Inspect:** per-claim halu score (probe + NLI ensemble), kolorowane (zielony / żółty / czerwony), klikasz badge → expanduje retrieved evidence
- **Compare:** Twoja polish probe vs multilingual baseline (Lynx, HHEM)

To jest co pokażesz na obronie — live demo, każdy w komisji może wpisać pytanie i zobaczyć rezultat.

---

## 6. Dlaczego to spełnia Twoje kryteria (przypomnienie)

- **Niepowtarzalny + nietrywialny** ✓ Polish-first w halu (luka), hidden-states probes (frontier 2025-2026), citation grounding (enterprise hot)
- **Praktyczny aspekt** ✓ Production use case, manager zafascynowany, możesz deployować w pracy
- **Czas + agent-rozkładalne** ✓ Dataset programatic + UOKiK Q&A ready-made eliminuje połowę manual work; agenty robią scaffolding/scrape/format
- **Fascynujący** ✓ Modern + niche + practical + work-relevant
- **PJATK schema fit** ✓ Klasyczny dane→trening→eval, każdy chapter pasuje
- **Promotor** ✓ MLOps mindset = continuous loop + observability + drift = sweet spot
- **Connection do pracy** ✓ Direct match z use case
- **Konkretny use case (LLM bez halu + cytowanie)** ✓ Bezpośrednio adresuje

---

## 7. Co jeszcze warto wiedzieć (reality check)

### Limitations (uczciwie)

- **Hidden-states extraction nie jest agent-friendly.** Wymaga PyTorch hooks na Bielik forward pass — to Twoja praca, nie agentów. Plus compute intensive (forward pass przez Bielik na 5-10k samples).
- **Programatic NLI ma ceiling.** Jeśli mDeBERTa multilingual baseline daje <70% agreement na polish legal text, fallback to LLM-as-judge (Bielik z few-shot prompting) — drożej, wolniej.
- **Drugi pivot ma defense cost.** Promotor może spytać „dlaczego znowu zmieniasz". DEC-003 ma silny argument (Iter. 0a evidence + Mu-SHROOM gap + reuse 70%), ale nie 100% gwarancji że przejdzie. Risk: 10-20%.
- **Czas:** ~10-11 tygodni speed-run. Compress możliwy do 7-8 tygodni jeśli skip ablations + simpler eval.

### Fallback jeśli coś nie wyjdzie

- **Probe nie konwerguje w Iter. 2** (AUROC <0.65): fallback na semantic entropy approach (Farquhar 2024) — klasyczny ale działający.
- **mDeBERTa za słaby**: HerBERT-large + custom NLI fine-tune na CDSC-E (~1d GPU work).
- **Reddit blokowany**: Pushshift dumps via Academic Torrents + e-prawnik + forumprawne wystarczą (mitigacja confirmed).
- **Outlines + Bielik nie współpracują** (technical blocker): drop hidden-states probe jako optional, focus na NLI-judge only — mniej ambitious ale defendable.

---

## 8. Defense narrative (krótko, gdyby promotor pytał)

> „Pierwszy publicznie udokumentowany polish hallucination detection methodology + dataset + probe model dla domeny krytycznej (prawa konsumenta). Polish landscape ma realną lukę — Mu-SHROOM 2025 pominął polski, brak polish HaluBench, brak polish-specific Lynx/HHEM/FaithJudge equivalent. Pivot z reranker fine-tuning bo Iter. 0a feasibility ujawnił że reranking dla schematic regulatory text jest mechanicznie trywialny — H1 odpadłby z trywialnego powodu. Pivot zachowuje 70% pracy v3.1 (cały stack MLOps, observability, drift detection — Pana sweet spot, mindset MLOps applied to LLM quality control), zmienia central komponent z reranker fine-tuning na hidden-states halu probe + citation grounding pipeline (modern technique 2025-2026, NIE crowded). Use case practical: production RAG dla domen krytycznych z citation requirement — mój zawodowy obszar."

---

## 9. Co teraz (operational — zobacz `PLAN_cele_i_kroki.md`)

Ten dokument jest *narrative explainer*. Konkretne kroki + co kto robi + sequence iteracji → drugi dokument: `PLAN_cele_i_kroki.md`.

W skrócie: Iteracja 0 POC (1 tydzień) — ELI scrape Ustawy + UOKiK Q&A + Outlines+Bielik POC + mDeBERTa NLI sanity. Checkpoint go/no-go po tygodniu. Potem Iteracje 1-8 per `02_konspekt_v3.2_skeleton.md` § II.11.

---

## 10. Słownik kluczowych pojęć (mini-glossary)

Dla orientacji. Skupiam się na koncepcji niche / nowych — pomijam basics typu „LLM to model językowy". Jeśli czegokolwiek nie wiesz, pytaj — dopisuję.

### A. RAG i retrieval

**RAG (Retrieval-Augmented Generation)** — wzorzec: zamiast LLM odpowiadać z głowy, najpierw retrievuje relevant chunks z bazy wiedzy (corpus), potem generuje odpowiedź na podstawie chunks. Twój pipeline: query → embedder → top-k chunks z Qdrant → Bielik generation.

**Embedder** (sentence encoder) — model który przekształca tekst na **wektor** (np. 1024-dim). Sens semantyczny zakodowany w geometrii — podobne teksty mają wektory blisko siebie. Examples: BGE-M3 (multilingual), sdadas/stella-pl (polish), OpenAI text-embedding-3.

**Cosine similarity** — `cos(A, B) = (A·B) / (|A|·|B|)`. Mierzy kąt między wektorami, w zakresie [-1, 1]. 1 = identyczne, 0 = ortogonalne, -1 = przeciwne. Standard dla retrieval ranking.

**Reranker** — drugi etap retrievalu. Embedder retrievuje top-50 (cheap, batch), reranker (cross-encoder, dokładniejszy ale wolniejszy) przesortuje i zwraca top-10. **Twoja v3.1 fokusowała się na fine-tuning rerankera. v3.2 NIE używa fine-tuned rerankera — base BGE-M3 wystarczy do retrieval.**

**Bi-encoder vs cross-encoder:**
- Bi-encoder: koduje (q, p) NIEZALEŻNIE → 2 wektory → cosine sim. Szybkie, batch-friendly. Embeddery są bi-encoder.
- Cross-encoder: koduje (q, p) RAZEM → jeden forward pass → score. Dokładniejsze ale ~100× wolniejsze. Rerankery są cross-encoder.

**Late interaction** (ColBERT, ColBERTv2) — kompromis między bi/cross. Per-token embeddings + MaxSim aggregation. Nowsza technika 2020-2024.

**Generative retrieval (GenIR)** — najnowsza idea: LLM **generuje** doc IDs zamiast retrieve via similarity. Frontier 2024-2025.

### B. Hallucination detection

**Halucynacja** — LLM generuje tekst który (a) nie ma podstawy w retrieved context, (b) jest faktualnie nieprawdziwy, (c) zaprzecza temu co model „wie" (hidden activations sygnalizują uncertainty ale model i tak generuje).

**NLI (Natural Language Inference)** — zadanie klasyfikacji (premise, hypothesis) → 3 klasy:
- *entailed:* hypothesis wynika z premise
- *contradicted:* hypothesis zaprzecza premise
- *neutral:* nie ma związku

W Twoim pipeline: **claim** = hypothesis, **retrieved evidence chunk** = premise. NLI mówi „czy claim wynika z evidence?". Halu jeśli „contradicted" lub „neutral".

**Semantic entropy (Farquhar et al. Nature 2024)** — generuj N samples odpowiedzi LLM, zgrupuj semantycznie (paraphrazy = ten sam grupa), policz entropy nad grupami. Wysoka entropy = niepewność = potencjalna halucynacja. **Drogie** (N samples) ale działa bez retrieved context.

**Hidden states / activations** — wewnętrzne reprezentacje LLM. Po każdym forward pass każda warstwa generuje wektor (np. 4096-dim dla Bielika 11B). „Hidden" bo nie widoczne na output, „state" bo represent intermediate computation. **Last few layers zawierają semantic info.**

**Probe** (probing classifier) — mały klasyfikator (1-3 layer MLP, lub linear) trenowany NA hidden states LLM (LLM frozen). Pyta: „czy te aktywacje wskazują na halucynację?". **Single-pass, real-time, cheap** w porównaniu do semantic entropy. SOTA 2024-2026.

**LLM-as-judge / LLM-as-critic** — używasz drugi LLM (np. GPT-4, Claude, Bielik) do oceny outputu pierwszego. Pytasz „czy ta odpowiedź jest faktyczna?". Drogie + wolne ale często accurate. Twój pipeline NIE używa jako primary (Mirage critique 2025: LLM-judge agreement spada w expert tasks na 64-68%), używasz NLI + probe jako alternatywa.

**Self-consistency** — generuj N odpowiedzi, sprawdź czy się zgadzają. Jeśli divergent → potential halu.

### C. Citation grounding

**Grounded generation** — LLM generuje odpowiedź z explicit pointers do source chunks. Przykład: „Per art. 27 ust. 1 Ustawy o prawach konsumenta [1], masz 14 dni na zwrot." [1] linkuje do exact paragraph.

**Span-level attribution** — per claim w odpowiedzi, oznaczasz konkretny fragment evidence chunk który ten claim wspiera. Granular niż „cite whole document".

**Post-hoc citation** — generujesz odpowiedź free-form, POTEM osobno mapujesz claims → evidence chunks. **Twój default w v3.2.**

**Generation-time citation** — LLM generuje odpowiedź już w structured format z citations (np. JSON `{claim: "...", citation: "art_27_ust_1"}`). Wymaga structured output libraries (Outlines / Instructor) lub instruct fine-tuning. **Alternatywa testowana w Iter. 4 ablation A4.**

### D. Training techniques

**Fine-tuning** — kontynuujesz training pre-trained modelu na własnym dataset. Full fine-tuning = update wszystkich wag (drogie). Modern preferują parameter-efficient.

**LoRA (Low-Rank Adaptation)** — zamiast update wszystkich wag, dodajesz low-rank matrices (np. rank=8, 16, 32) per layer. Update tylko te. **~100-1000× mniej parametrów do trenowania, podobny jakość.** Standard 2023-2026.

**QLoRA** — LoRA + 4-bit quantization base modelu. Pozwala fine-tune 70B model na 1 GPU. SOTA dla compute-constrained.

**PEFT (Parameter-Efficient Fine-Tuning)** — umbrella term: LoRA, QLoRA, prefix tuning, prompt tuning, adapters.

**DPO (Direct Preference Optimization)** — uczenie z preference pairs (chosen, rejected) bez explicit reward model (alternatywa dla RLHF). Standard dla alignment 2023-2024.

**RLHF (Reinforcement Learning from Human Feedback)** — klasyczne (ChatGPT). Wymaga human labelers + reward model + PPO.

**RLAIF (Reinforcement Learning from AI Feedback)** — zamiast humans, używasz LLM-as-judge jako sygnał preference. Cheaper, scalable.

**Probe training** — train small classifier na frozen activations LLM. **Twój pipeline: probe na Bielik hidden states.** Differs from LoRA (LoRA modifies LLM, probe NIE).

### E. MLOps

**Continuous training (CT)** — automatic retraining model w pętli na nowych danych. Vs static deployment (one-shot training, never updated).

**Drift detection** — monitorowanie czy distribution input data zmienia się w czasie. Tools: Evidently (data drift), Alibi Detect (statistical KS test, MMD).

**A/B test gating** — przed deploy nowej wersji modelu, run side-by-side z current production model na sample traffic. Jeśli new bije old z statistical significance → deploy. Jeśli nie → rollback.

**Model Registry** — wersjonowanie modeli z metadata (version, accuracy, hyperparams, training data, deployment status). MLflow Model Registry standard.

**Observability** — beyond logging — distributed tracing (każdy request ma trace ID przez wszystkie services), metrics (latency, throughput, errors), structured logs. Tools: OpenTelemetry standard, Langfuse LLM-specific.

**Langfuse** — observability layer specifically dla LLM apps. Trace per user query: retrieval → reranking → generation → output. Token usage, cost, latency per step. Open-source.

**Prefect** — workflow orchestration (DAGs). Alternative do Airflow. Async-native, modern.

**MLflow** — experiment tracking + model registry + projects. Standard MLOps platform.

**Evidently** — drift detection + data quality monitoring. Open-source.

### F. Metryki

**AUROC (Area Under ROC Curve)** — dla binary classification (halu vs no-halu). Mierzy jak dobrze model separuje klasy across all thresholds. Range [0, 1], 0.5 = random, 1.0 = perfect. Standard dla halu detection (better than accuracy bo class imbalance).

**ROC curve** — plot True Positive Rate (TPR) vs False Positive Rate (FPR) for varying decision threshold.

**Precision** = TP / (TP + FP) — z wszystkich „pozytywnych" przewidywań, ile rzeczywiście pozytywne.

**Recall** = TP / (TP + FN) — z wszystkich rzeczywistych pozytywnych, ile model złapał.

**F1** = 2 · (P · R) / (P + R) — harmonic mean P i R.

**Cohen's kappa (κ)** — agreement metric między 2 raterami (e.g., LLM-judge vs human), uwzględnia chance agreement. Range [-1, 1], 0 = chance, 1 = perfect agreement. Landis-Koch interpretation: <0.2 slight, 0.21-0.4 fair, 0.41-0.6 moderate, 0.61-0.8 substantial, >0.8 almost perfect.

**Bootstrap confidence interval** — resampling z dataset N razy → distribution metric → 95% CI. Robust dla small samples.

**Statistical significance (paired t-test)** — czy różnica między 2 modelami jest „real" czy chance. p<0.05 standard threshold.

### G. Benchmarki i datasets

**Mu-SHROOM (SemEval 2025 Task 3)** — multilingual hallucination detection benchmark. **14 języków, BEZ polskiego.** Twoja praca adresuje tę lukę.

**FELM, HaluBench, HaluEval, RAGTruth** — angielskie halu detection benchmarki. Reference dla Twojego polish CitationBench.

**FaithJudge (EMNLP 2025)** — Vectara hallucination evaluation framework. Reference dla methodology.

**KLEJ benchmark** — polish NLP benchmark (10 tasków). Includes CDSC-E (NLI subset polish).

**PoQuAD, PolQA** — polish QA datasets. Reusable jako base dla Twojego corpus.

**CDSC-E** — polish NLI dataset (~10k pairs). Ewentualne fine-tuning HerBERT dla polish NLI.

### H. Polish LLM-y

**Bielik** (SpeakLeash) — open-source polish LLM. v3 ma 11B params, Apache 2.0, ~131k context (YaRN scaling). Twój generator + probe target.

**PLLuM** (PolEval consortium / NASK / IPI PAN) — polish LLM 12B-instruct. CC BY-NC. Alternative judge candidate.

**Trurl, Qra** — inne polish LLM-y, mniej popular.

**HerBERT (Allegro)** — polish BERT. Dla embedding lub NLI fine-tuning.

### I. Tools / libraries

**HuggingFace** — platforma dla open-source ML models + datasets + Spaces (apps). Standard dla publishing artefaktów.

**Transformers (HF library)** — Python lib do load/run/fine-tune modeli z HuggingFace. Standard.

**LlamaIndex** — RAG framework (alternative LangChain). Citation Query Engine + ChatEngine z built-in memory.

**LangChain** — drugi RAG framework. Bardziej elastyczny, ale messier API.

**Outlines** — structured output library. Forces LLM output to match grammar (regex / JSON schema / Pydantic). Useful dla generation-time citations.

**Instructor** — alternative do Outlines. Pydantic-first API. Plus type validation.

**transformer-lens** — interpretability library. Easy access to hidden states, attention patterns, activations during forward pass. Usable dla probe training.

**nnsight** — alternative do transformer-lens. Newer, czystszy API.

**PyTorch hooks** — niskopoziomowe — register callback na konkretną warstwę modelu, automatycznie capture activations during forward pass. Manual approach (vs transformer-lens / nnsight).

**Optuna** — Bayesian hyperparameter search. Alternative dla grid/random search. Standard dla MLflow integration.

**SGLang** — fast LLM serving (alternative do vLLM). Production-grade inference.

**TEI (Text Embeddings Inference)** — HuggingFace fast embedder serving (Rust-based, 2-3× szybsze niż naive sentence-transformers).

**Qdrant** — vector database. Alternative dla Pinecone, Weaviate, Milvus. Open-source, Rust-based.

### J. Critique / methodology terms

**„Mirage of Hallucination Detection" (EMNLP 2025)** — paper krytykujący że ROUGE-based eval przeszacowuje halu detection AUROC o ~46pp. Wniosek: używaj rigorous metrics (AUROC z bootstrap CI, agreement z manual labels), NIE shortcuts.

**Negative-result framing** — explicit acknowledgment że H1 może odpadnąć. Defense: kontrybucje (2)-(5) stoją niezależnie. Twoja Defense scaffolding pkt 3.

**5-wymiarowa kontrybucja** — Twoja praca ma 5 niezależnych wymiarów contribution: metodologiczny, inżynierski, artefaktowy, eksperymentalny, korpusowy. Każdy broni się niezależnie nawet przy odrzuceniu H1.

**Ablation study** — systematic remove component i compare → measure how much each component contributes. Twój pipeline: A1-A4 ablations.

---

## 11. Co dalej

Operational plan + sequence iteracji → `PLAN_cele_i_kroki.md`. Konkretny akademicki konspekt → `02_konspekt_v3.2_skeleton.md`. Pivot rationale + defense → `decisions/DEC-003_pivot-na-halu-detection.md`. SOTA research z cytacjami → `research/halu_detection_sota_2024_2026.md`. Domain feasibility → `research/domain_A_feasibility.md`.

**Jeśli czegokolwiek tu nie rozumiesz — pytaj. Słownik dopisuję live, NIE musi być wyczerpujący od razu.**
