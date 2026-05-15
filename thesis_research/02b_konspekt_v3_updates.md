# Konspekt v3 — UPDATES (delta v3.1)

**Data:** 2026-05-15
**Status:** ACTIVE. Supersedes specified sections of `02_konspekt_v3_FINAL.docx`.
**Related ADRs:** DEC-001 (rotacja domeny), DEC-002 (ChPL+Ulotka pairing jako RQ5)

**Read order:** Najpierw `01_agent_brief.docx`, potem TĄ delta. Pełen kontekst v3 FINAL .docx dla sekcji niezmienionych (II.5, II.6, II.8, II.9, II.10, II.11, II.12, II.14).

---

## Globalne zmiany terminologiczne (apply globally)

| Stare (v3 FINAL) | Nowe (v3.1) |
|---|---|
| psychiatria kliniczna | farmakologia kliniczna (psychiatryczny eval subset) |
| polska psychiatria | polska farmakologia |
| domena psychiatrii | domena farmakologii (testbed) |
| polish-reranker dla psychiatrii | polish-reranker dla farmakologii |
| psychiatric corpus | pharmaceutical corpus (ATC-stratified) |
| PTP, IPiN, psychiatria.org.pl jako primary sources | URPL ChPL+Ulotki, AOTMiT, NFZ, OA pharma journals (zobacz `sources_catalog.md`) |
| eksperckie kompetencje psychiatryczne autorki | manual validation kompetencji autorki w psychiatrycznej podgrupie ATC N05/N06 |

---

## Tytuł roboczy (ZASTĘPUJE II.1 nagłówek)

**NEW PL:** *„Pipeline MLOps do iteracyjnego dotrenowywania komponentów retrievalu w polskojęzycznych systemach RAG na podstawie sygnałów z observability — studium przypadku dla domeny farmakologii klinicznej z eksperymentem cross-register retrieval (paired ChPL↔Ulotka)"*

**NEW EN:** *„MLOps Pipeline for Iterative Retraining of RAG Retrieval Components Based on Observability Signals — A Case Study in Polish Clinical Pharmacology with Cross-Register Retrieval Experiment"*

---

## II.1 Streszczenie wykonawcze (ZASTĘPUJE)

Praca projektuje, implementuje i ewaluuje pipeline MLOps do iteracyjnego dotrenowywania rerankera w polskojęzycznym systemie RAG dla domeny specjalistycznej (farmakologia kliniczna). Pipeline integruje sześć kluczowych komponentów: (1) generację syntetycznych zapytań przez LLM, (2) ranking par passage przez LLM-as-judge w protokole pairwise, (3) iteracyjny fine-tuning rerankera typu cross-encoder na preferencjach, (4) ewaluację retrieval quality przeciwko external benchmarkowi proxy oraz manualnie zwalidowanej próbce (z psychiatrycznej podgrupy ATC N05/N06 dla leverage'u kompetencji autorki), (5) drift detection na embedding distributions z trigger logic do retrainingu, (6) **eksperyment cross-register retrieval na paired Polish ChPL↔Ulotka corpus** — pierwsza publicznie udokumentowana polska aligned para professional/lay register w domenie farmaceutycznej.

Wkład inżynierski pracy: reprodukowalny pipeline retreningu komponentów RAG, framework LLM-as-judge walidowany przeciwko manualnym labelom dla domeny polskiej farmakologii, dotrenowany reranker dla domeny farmakologii, komponent monitoringu drift z simulated drift evaluation, oraz aligned ChPL↔Ulotka corpus + cross-register retrieval methodology. Wszystkie komponenty oparte na otwartych modelach (Bielik 11B v3 jako generator; `<judge_model>` jako sędzia — kandydaci: Bielik 11B v3 / Gemma 3 27B / Qwen 3 32B / Claude Haiku 4.5 z final decyzją w Iteracji 0; BGE-M3 jako embedder, polish-reranker-roberta-v3 jako reranker) i otwartych narzędziach MLOps (MLflow, Prefect, Evidently, Langfuse, Qdrant, PostgreSQL, SGLang serving).

---

## II.2.1 Domena specjalistyczna jako testbed (ZASTĘPUJE)

Wybór farmakologii klinicznej jako testbedu jest motywowany pięcioma przesłankami:

1. **Long tail terminologii.** Polska terminologia farmaceutyczna (nazwy międzynarodowe DCI, kody ATC, terminologia łacińsko-polska, nazewnictwo postaci leku, terminologia farmakokinetyczna) jest słabo reprezentowana w pretrainingu off-the-shelf rerankerów — co czyni domain adaptation realnie wartościową, a nie marginalną poprawą.

2. **Deterministyczna struktura ChPL.** Charakterystyka Produktu Leczniczego jest **standardyzowana w 10 sekcji** (Wskazania, Dawkowanie, Przeciwwskazania, Interakcje, etc.) zgodnie z wytycznymi EMA QRD. Tworzy to deterministyczny ground truth dla query→passage extraction, gdzie sekcja header jest naturalnym query, a body jest gold passage. ~14k zarejestrowanych leków × 9 użytecznych sekcji = ~126k natural pairs możliwe do extracji bez manualnej anotacji.

3. **Dostępność open-access źródeł.** Wszystkie kluczowe źródła (URPL, AOTMiT, MZ, NFZ) są urzędowymi materiałami zwolnionymi z ochrony prawnoautorskiej (Art. 4 ustawy o prawie autorskim). Open-access czasopisma (Farmacja Polska CC BY-NC, Lek w Polsce CC BY-NC-ND, AAMS CC BY-SA, CIPMS CC BY-NC-ND) uzupełniają corpus z czystą license story.

4. **Manual validation kompetencje autorki** w psychiatrycznej podgrupie ATC N05/N06. Eval set 200 par gold standard próbkowany **świadomie z psych subset**, aby leverage'ować kompetencje autorki dla rygorystycznej walidacji LLM-as-judge agreement (RQ2/H2). Trening korpus pozostaje szeroki (cała farmakologia), eval set wąski w domenie którą autorka faktycznie zna.

5. **Strukturalna parowalność professional/lay register.** URPL udostępnia paired ChPL (professional) + Ulotka dla pacjenta (lay) dla każdego leku — ten sam content semantyczny, dwa rejestry językowe. To enabluje RQ5 (cross-register retrieval) jako novel sub-contribution bez kosztu manualnej anotacji.

**Praca nie pretenduje do oceny farmaceutycznej / medycznej.** Autorka nie jest farmaceutką ani lekarzem. Mierzona jest wyłącznie retrieval quality (czy reranker zwraca passage'y merytorycznie relewantne dla query) oraz faithfulness (czy odpowiedź LLM jest wsparta przez retrieved passages). Praca jest research artefaktem z evaluation pipeline; domena farmaceutyczna służy jako testbed dla precyzji retrievalu, gdzie tolerancja błędu jest niska (regulowana dziedzina). **Praca nie jest systemem doradztwa farmaceutycznego i nie może być takim wdrażana.**

---

## II.3.3 Pytania badawcze (DODAJE RQ5 do v3 FINAL listy)

RQ1, RQ2, RQ3, RQ4 i ich hipotezy H1-H4 — **bez zmian** względem v3 FINAL (tylko psychiatria → farmakologia w domenie ewaluacji).

### NOWY RQ5 — Cross-register retrieval

Czy reranker dotrenowany na corpus z paired pro/lay versions (ChPL ↔ Ulotka tych samych leków) handluje cross-register queries (lay query → professional answer, i odwrotnie) z accuracy@10 ≥70%, z gap ≤5pp poniżej same-register accuracy?

**Hipoteza H5:** Reranker dotrenowany na corpus zawierającym ChPL+Ulotka pairs osiąga ≥70% accuracy@10 na cross-register pairs (gdzie query = sekcja Ulotka, gold passage = odpowiadająca sekcja ChPL tego samego leku, lub odwrotnie), z gap ≤5pp poniżej same-register accuracy.

**Falsyfikowalność:** Hipoteza odrzucona jeśli (a) accuracy@10 < 60%, lub (b) gap same-vs-cross > 15pp, lub (c) trening na pairs degraduje base-line retrieval na same-register (regresja > 2pp).

**Setup ewaluacyjny:**

- **Test query set:** 1800 cross-register pairs (900 lay→pro + 900 pro→lay) wygenerowane programatycznie z 900 paired par leków.
- **Gold standard:** alignment deterministyczny przez `productID` z URPL RPL feed.
- **Hard negatives:** 4-poziomowa strategia (different ATC class / same class different drug / same drug different section / cross-register confusion) — pełen opis w II.4.6.
- **Metryki — kluczowe rozdzielenie per direction (asymmetric difficulty):**
  - **accuracy@10 lay→pro** — query z Ulotki, gold = ChPL sekcja tego samego leku
  - **accuracy@10 pro→lay** — query z ChPL, gold = Ulotka sekcja tego samego leku
  - **MRR@10 lay→pro** i **MRR@10 pro→lay** osobno (cross-register może być asymmetric — lay queries zwykle krótsze, mniej technical; pro queries dłuższe, bogatsze terminologicznie → różny ranking difficulty)
  - **Aggregate accuracy@10 i MRR@10** (mean obu directions) jako single-number reporting
  - **Direction asymmetry gap:** `Δ_dir = | MRR(lay→pro) − MRR(pro→lay) |` — measure czy reranker jest stronniczy
  - **Same-register baseline** (in-distribution training set) jako reference
- **Ablation A4:** porównanie ChPL-only training vs ChPL+Ulotka training (oba evaluated na tym samym cross-register test set).
- **Power (rule-of-thumb, NIE formalny power analysis):** 900 par per direction jest borderline-adequate dla detekcji gap ~5pp przy α=0.05 (n≥1000 per group dla 80% power wg standard proportion-difference test). Jesteśmy na granicy — *jeśli wyniki są jednoznaczne, 900 wystarczy; jeśli ambiguous, expandujemy do 1500 per group w Iteracji 4.* **Focus na effect size + error bars across 3 random seeds**, NIE na formal p-values. (Promotor preferuje engineering rigor nad over-statistical testing.)

**Novel angle — literature gap:** Brak publicznie udokumentowanego Polish ChPL↔Ulotka aligned corpus w literaturze BioNLP. Grabowski (2017) ma EN-PL comparable PIL corpus, ale **cross-language, nie intra-Polish cross-register**. Niniejsza praca jest pierwszą publiczną dokumentacją cross-register retrieval methodology dla polskiego farmaceutycznego RAG.

---

## II.3.4 Scope (MODIFIES)

**IN scope (DODAJE do v3 FINAL):**
- Cross-register retrieval evaluation (paired ChPL↔Ulotka)
- Manual psych eval subset (200 par z ATC N05-N06 jako gold standard)
- Aligned ChPL↔Ulotka corpus jako standalone artefakt do publikacji poza pracą

**OUT scope (BEZ ZMIAN, plus):**
- Medical/pharmaceutical correctness validation
- Hard negative mining dla embeddera
- Embedder fine-tuning (BGE-M3 frozen)
- End-user clinical deployment
- Real-time drift detection na produkcyjnym ruchu
- Cross-domain generalization
- **NEW:** Cross-language register transfer (czy lessons z PL ChPL↔Ulotka transferują do EN PIL↔SPC — przyszła praca)

---

## II.4 Strategia danych (ZASTĘPUJE całą II.4 z v3 FINAL)

### II.4.1 Plan A — farmakologia szeroka, psychiatryczny eval subset

**Pełna tabela źródeł:** `sources_catalog.md` (single source of truth).

**Skrót strata:**

| Strata | Source | ~docs | % korpusu |
|---|---|---|---|
| 1. Regulatory professional | ChPL (URPL RPL XML) stratified ATC, N05/N06 over-rep | 900 | 22% |
| 2. **Regulatory consumer (paired)** | Ulotki dla pacjenta — paired z ChPL | 900 | 22% |
| 3. HTA + refundation legal | AOTMiT raporty + MZ obwieszczenia + programy B.xx | 700 | 17% |
| 4. Refundation operational | Zarządzenia Prezesa NFZ + BIP komunikaty | 400 | 10% |
| 5. OA PL journals | Farmacja Polska + Lek w Polsce + AAMS + CIPMS | 900 | 22% |
| 6. Adjacencies | URPL DHPC + MZ braki list | 300 | 7% |
| **TOTAL** | | **~4100** | 100% |

**Stratified sampling:** Strata 1 (ChPL) — 900 leków próbkowane proporcjonalnie do klasy ATC, z over-representacją N05 (Psycholeptica) i N06 (Psychoanaleptica) do ~30% próby (zamiast natural rate ~10%). To wzmacnia psych signal w training bez zmiany scope korpusu na "psychiatria".

**Implikacja:** trzy strata content do explicit nazwania w Rozdz. 3:
- Regulatory ~44% (ChPL + Ulotki, dwa rejestry tego samego semantycznego content)
- HTA/regulatory secondary ~27% (AOTMiT + MZ + NFZ)
- Scientific/educational ~29% (OA journals + adjacencies)

Cztery chunking strategies (rozszerzone vs v3):
- **ChPL:** section-aware (10 sekcji deterministycznych)
- **Ulotki:** section-aware (6 sekcji QRD)
- **HTA/NFZ:** named-section split + legal-aware fallback
- **Journals:** recursive markdown 512+50 / heading-based

### II.4.2 Plan B (DEACTIVATED)

Plan B (cybersec — CERT.pl, NASK, UODO, MSWiA, KNF) zdezaktywowany 2026-05-15. Powody:
- Plan A (farmakologia) ma stabilny corpus realnie ~4100+ dokumentów z czystymi licencjami
- URPL RPL XML feed dostępny, scrape trivial
- Brak feasibility risk wymagającego fallback w Tygodniu 0

Plan B pozostaje w historical record (v3 FINAL) jako referencja, ale **nie należy go aktywować bez zmiany DEC-001 kill criteria**.

### II.4.3 Strategia eval setu

**Eval set podstawowy (200 par) — manual gold standard:**
- Próbkowane z psychiatrycznej podgrupy korpusu (ATC N05/N06)
- Manual relevance labels (relevant / partially relevant / irrelevant) by autorka
- **Uzasadnienie świadomego sample bias** (w R5): leverage manual validation kompetencji autorki dla rygorystycznej walidacji LLM-judge (RQ2/H2). Eval set wąski (psych), training corpus szeroki (cała farma). To **świadoma decyzja architektoniczna**, nie nieuwaga.

**Eval set RQ5 cross-register (1800 par):**
- Programatycznie wygenerowane z 900 paired par leków (zobacz DEC-002)
- Gold standard implicite przez deterministyczny `productID` alignment
- Spot-check manual na 50 par (5% wielkości)

**Eval set rozszerzony LLM-generated (~1500-2000 par):**
- Bielik/PLLuM few-shot template
- 70% syntetyczne, 30% z external proxy (jeśli istnieje pharma equivalent MIRACL-pl)
- Walidacja spot-check 10%

### II.4.4 Synthetic queries — strategia hybrydowa

Z konspekt v3 FINAL — strategia bez zmian. Tylko domain swap (psych queries → pharma queries z over-rep N05/N06).

### II.4.5 Splity i protokół ewaluacji

Z konspekt v3 FINAL — bez zmian. Document-level split (NIE chunk-level), 3 random seeds, mean ± std.

### II.4.6 Hard negatives strategy (explicit)

Hard negatives dla preference learning rerankera próbkowane na **4 poziomach trudności**, żeby model uczył się fine-grained distinctions zamiast tylko coarse separation. Strategia inspirowana DPR (Karpukhin i in., 2020 — *Dense Passage Retrieval*); rozszerzona o L4 cross-register layer dla RQ5.

| Level | Definicja | Przykład (sertralina jako positive context) | Proporcja | Trudność |
|---|---|---|---|---|
| **L1 (easy anchor)** | Inna klasa ATC | Query: *„przeciwwskazania do sertraliny (N06AB)"*, negative: ChPL metforminy (A10BA antidiabetic), sekcja 4.3 | 15% | 🟢 easy |
| **L2 (medium, standard)** | Ta sama klasa ATC, inny lek | Query: *„przeciwwskazania do sertraliny"*, negative: ChPL fluoksetyny (N06AB SSRI), sekcja 4.3 | 50% | 🟡 medium |
| **L3 (hard, core ML challenge)** | Ten sam lek, inna sekcja | Query: *„przeciwwskazania do sertraliny"*, negative: ChPL sertraliny sekcja 4.4 (specjalne ostrzeżenia — overlap leksykalny z 4.3) | 30% | 🔴 hard |
| **L4 (very hard, RQ5-specific)** | Ten sam lek, cross-register confusion | Query: *„co zrobić jak zapomniałem dawki"* (Ulotka register), negative: ChPL sekcja 4.4 (specjalne ostrzeżenia — wspomina missed doses w innym kontekście) | 5% | 🔴🔴 very hard |

**Rationale per poziom:**

- **L1 (15%)** — anchors. Model uczy się że completely different pharmaceutical domains mają być daleko w embedding space (sanity check). Bez L1 ryzyko overfittingu na fine-grained intra-class distinctions z utratą coarse separation.
- **L2 (50%)** — standard. Najczęstszy realny scenariusz query → distinguish między lekami w obrębie klasy farmaceutycznej (np. wybór między SSRI'ami, między ACE inhibitorami).
- **L3 (30%)** — core ML challenge. Testuje czy reranker rozróżnia **intent sekcji** (przeciwwskazania ≠ specjalne ostrzeżenia ≠ działania niepożądane ≠ interakcje) nawet dla tego samego leku. To **najważniejszy poziom** dla quality reranker.
- **L4 (5%)** — specialty dla RQ5. Testuje czy cross-register training pomaga w paraphrastic queries. Mała proporcja, bo zbyt wysokie L4 = noise sygnał (model uczyłby się unik pomyłek register, nie distinguish semantyki).

**Strategia generacji:** dla każdej (query, gold_passage) pary, próbkowane 3 hard negatives z proportional levels — czyli każdy training example to **1 positive + 3 negatives** (preference loss z expectation `score(positive) > score(negative_i)` dla wszystkich `i`).

**Total scale przyrostu:** ~900 ChPL × 9 użytecznych sekcji × ~6 LLM-paraphrased queries × 3 negatives ≈ **145k preference samples** (vs ~50k bez hard negative mining z proportional levels).

**Walidacja jakości hard negatives:** spot-check 100 quadrupletów (positive + 3 negatives) manualnie sprawdzonych przez autorkę — czy proporcje L1/L2/L3/L4 trzymają się + czy negatives są faktycznie negatywne (a nie tied/synonymous z positive).

---

## II.7 LLM-as-judge (DODAJE 4. protokół do v3 FINAL listy)

**1. Pairwise** — bez zmian (główny sygnał treningowy)
**2. Pointwise** — bez zmian (sanity check)
**3. Faithfulness** — bez zmian (end-to-end metric)

### NOWY 4. Cross-register pair scoring

Format: judge dostaje query (z Ulotki layperson register) + passage A (z ChPL professional register) + passage B (z innego ChPL tej samej klasy ATC, hard negative). Output JSON: `{ preferred: A | B | tie, semantic_match_quality: 0-5, register_appropriateness: 0-5, reasoning: "..." }`.

Dwa wymiary scoringu:
- **Semantic match quality:** czy A vs B faktycznie odpowiada na semantyczny content query?
- **Register appropriateness:** czy odpowiedź jest stylistycznie / leksykalnie adekwatna do query register?

To rozdzielanie wymiarów pozwala diagnozować czy reranker miss-rankuje semantycznie (problem) czy stylistycznie (mniejszy problem, w kontekście cross-register).

**Walidacja jakości 4. protokołu (multi-stage):**
- **Stage 1 (Iteracja 0b — pilot):** kappa ranking na n=30 par × 4 candidate judges {Bielik 11B v3 / Gemma 3 27B / Qwen 3 32B / Claude Haiku 4.5} → **top-2 shortlist** (n=30 zbyt thin dla single-winner pick, expected CI ±0.15-0.20).
- **Stage 2 (Iteracja 2 — final):** head-to-head top-2 vs n=200 manual labels per H2 validation — single judge winner picked z defensible kappa CI ±0.05-0.08. Manual labels by autorka, próbka cross-register sprawdza czy judge rozróżnia semantic vs register dimensions.

---

## II.13 Out of scope / future work (DODAJE pkt II.13.X do v3 FINAL listy)

Punkty II.13.1 - II.13.7 z v3 FINAL — **bez zmian** (z drobnym update: medical → pharmaceutical correctness).

### II.13.8. Cross-language register transfer (NEW)

Czy lessons learned z PL ChPL↔Ulotka transferują do innych języków UE (EN SPC↔PIL, DE Fachinfo↔Beipackzettel, etc.)? Future work: multi-lingual cross-register evaluation na MIRACL multilingual benchmark lub własny mini-corpus 100 par per language.

### II.13.9. Domain transfer cross-register (NEW)

Czy methodology cross-register transferuje na inne PL domeny z dwoma rejestrami (np. prawo: kodeksy ↔ przewodniki dla obywateli; medycyna: wytyczne ↔ materiały edukacyjne pacjenta)? Future work: ablation na 1-2 dodatkowych domenach.

---

## II.15 Strategia rozmowy z promotorem (DODAJE do v3 FINAL argumentów)

II.15.1 - II.15.X z v3 FINAL — **bez zmian**.

### Nowe argumenty obronne (2026-05-15)

- **„Dlaczego farmakologia szeroka a nie psychiatria specyficzna?"** — szerszy korpus = lepsza pokrywająca długość-ogon terminologii, ChPL deterministycznie strukturyzowane (10 sekcji × 14k leków = 126k natural pairs), psych pozostaje aktywne jako eval testbed dzięki kompetencjom autorki na tej podgrupie. Decyzja DEC-001 ma pełny audit trail.

- **„Dlaczego ChPL+Ulotka pairing jako 5. RQ?"** — pierwsze publicznie udokumentowane Polish ChPL↔Ulotka aligned corpus (Grabowski 2017 ma EN-PL, nie intra-PL cross-register). Sub-contribution niezależnie publishable. Decyzja DEC-002 ma pełny audit trail.

- **„Czy 5 RQ to nie scope creep?"** — RQ5 używa tego samego pipeline'u, tego samego LLM-judge, tego samego rerankera. Dodatkowy koszt eksperymentalny: ~1 tydzień w cyklu 1 + ~3 dni R7 sekcji. Nie jest to nowy pipeline, jest to dodatkowa evaluation axis na istniejącym pipeline.

- **„Czy psychiatria w eval set to nie samolubność?"** — to leverage manual validation kompetencji autorki dla rygorystycznej walidacji RQ2/H2 (najsłabiej zabezpieczona hipoteza). Eval set wąski, training korpus szeroki — świadoma decyzja architektoniczna explicit zapisana w R5. Bez tego eval set 200 par byłby manualnie nie do zwalidowania.

---

## II.16 Iteration plan (ZASTĘPUJE II.16 + II.10 schedule z v3 FINAL)

Praca prowadzona w **iteration mode**, NIE w calendar-weeks. Każda iteracja ma input, output i done criterion. **Brak sztywnych deadline'ów per iteracja** — speed-run autorki diktuje kadencję. Brak scheduled email do promotora — promotor dostaje artefakty asynchronicznie gdy istnieją (DVC pull / repo state).

### Iteracja 0a — Feasibility (URPL probe)

**Input:** DEC-001 + DEC-002 + `sources_catalog.md` § Iteracja 0 — Feasibility pre-conditions

**Output (phase 1 — synchronous, ~4h):**
- 100 leków scraped (ChPL + Ulotka pairs z URPL RPL XML feed)
- Pre-conditions #2 (XML parse 100%), #3 (ChPL p95 <2s), #4 (Ulotka p95 <2s), #5 (alignment ≥90% z **competence-stratified spot-check** — 10/10 par z psych subset N05/N06), #6 (OCR <15%) measured
- AOTMiT 50 + NFZ Zarządzenia 50 sample (soft validation Strata 3-4)

**Output (phase 2 — async, +24h):**
- Pre-condition #1 (URPL uptime ≥99% w 24h) — background script `iter0_uptime_probe.py` tick co 1h, append-only JSONL log

**Done criterion:** dane na disku + DEC-001 kill criteria check passed (patrz `sources_catalog.md` § Kill criteria + Warning bands)

### Iteracja 0b — Judge pilot selection

**Input:** Iteracja 0a passed

**Output:**
- Pilot kappa ranking na **30 par cross-register pair scoring** dla {Bielik 11B v3 / Gemma 3 27B / Qwen 3 32B / Claude Haiku 4.5}
- **Top-2 shortlist** — NIE final winner. Powód: n=30 jest statystycznie thin dla 4-way comparison (kappa CI ±0.15-0.20 expected, ranking ambiguous w połowie przypadków).

**Done criterion:** top-2 judges short-listed + decision rationale dokumentowana w `thesis_research/iter0_feasibility/judge-pilot-ranking.md`

**Final judge winner** picked w Iteracji 2 (po n=200 manual labels per H2 validation — stabilna kappa CI ±0.05-0.08, single-winner decision defensible).

### Iteracja 1 — Corpus full + EDA + eval set ready

**Input:** Iteracja 0 success

**Output:**
- Full ~4100 docs scraped & indexed w Qdrant (BGE-M3 embeddings)
- EDA report (rozkłady długości, OCR quality, ATC distribution, paired ChPL↔Ulotka length ratio stats, terminology coverage)
- PostgreSQL schema set up (metadata, chunks, eval pairs, run logs)
- DVC versioning aktywny
- **200 par gold standard manualnie ranked by autorka** (psych subset, ATC N05/N06)

**Done criterion:** corpus on disk + indexed + eval set ready + EDA report written

### Iteracja 2 — Pipeline core + Cykl 1 + Ablations A1-A4

**Input:** Iteracja 1 complete

**Output:**
- `<judge_model>` validation vs manual labels — Cohen's kappa reported (**RQ2 H2 answered**)
- Generator queries pipeline working (Bielik 11B v3 few-shot)
- Pairwise preference dataset generated (~145k preference quadruplets z 4-level hard negatives — II.4.6)
- Cykl 1 reranker fine-tuned, MLflow tracked, 3 random seeds, Optuna hyperparam search
- Baselines done: BM25 (Pyserini) + dense BGE-M3 + base polish-reranker-roberta-v3
- **Ablations A1-A4 wykonane:** A1 random vs judge, A2 Bielik vs `<judge_model>`, A3 psych-only vs full corpus, A4 ChPL-only vs ChPL+Ulotka (Defense scaffolding pkt 1)

**Done criterion:** cycle 1 metrics in MLflow + ablation table + **RQ1 H1 partial answer** (single-cycle improvement vs baseline)

### Iteracja 3 — Cykle 2 + 3 + plateau analysis

**Input:** Iteracja 2 complete

**Output:**
- Cykl 2 retreningu (fresh synthetic queries, fresh judge labels)
- Cykl 3 retreningu (fresh synthetic queries, fresh judge labels)
- Plateau analysis: czy cykl 3 daje ≤2pp vs cykl 2 (**RQ3 H3 answered**)

**Done criterion:** cycle 3 metrics in MLflow + plateau confirmation/rejection

### Iteracja 4 — Cross-register RQ5

**Input:** Iteracje 1-3 complete (model trained, all cycles)

**Output:**
- Cross-register evaluation pipeline implemented
- 1800 par lay↔pro evaluated (per II.3.3 setup)
- **MRR + accuracy@10 per direction** (lay→pro vs pro→lay) reported osobno
- Direction asymmetry gap `Δ_dir` analyzed
- A4 (ChPL-only vs ChPL+Ulotka) compared specifically na cross-register test set
- **RQ5 H5 answered** (lub flagged if ambiguous → consider expand do 1500 par per direction)

**Done criterion:** RQ5 results in MLflow + direction-stratified report

### Iteracja 5 — Drift detection RQ4

**Input:** Iteracje 1-4 complete

**Output:**
- Drift detector implemented (Evidently + Alibi Detect — KS test + MMD na BGE-M3 embeddings)
- Simulated OOD experiment (in-distribution psych queries vs OOD neurology queries vs perturbed psych z paraphrasingiem)
- Precision/recall reported per threshold (**RQ4 H4 answered**)

**Done criterion:** RQ4 metrics in MLflow + simulated drift report

### Iteracja 6 — Kategoryczna error analysis (Defense scaffolding pkt 2)

**Input:** Iteracje 2-5 (wszystkie experimental results)

**Output:**
- 100 incorrect rankings per cycle (cykle 1, 2, 3) kategoryzowane wg 6-poziomowej taksonomii (terminology miss / ambiguous query / length mismatch / OOD chunk / register mismatch / OCR artifact)
- Distribution of error types per cycle
- Top 3 dominant error patterns z rekomendacjami dla future work

**Done criterion:** error analysis report + diagrams (Defense scaffolding pkt 2 satisfied)

### Iteracja 7 — Writing R1-R6 + outline R7+R8

**Input:** All experimental results + error analysis + ADR-y + sources_catalog + Writing rules (thesis_elements/CLAUDE.md)

**Output:**
- R1 (Wprowadzenie) draft — **classic intro structure** per Writing rules (background → motivation → aim → scope → outline → RQ na końcu)
- R2 (Literatura) draft — **explicit selection methodology** per Writing rules; ~30 cytacji
- R3 (Dane) draft — używa `sources_catalog.md` jako source of truth + Source selection methodology
- R4 (EDA) draft — z Iteracji 1 EDA report
- R5 (Architektura) draft — 5 z 7 figur diagramów
- R6 (Modele) draft — reranker + 4 judge protokoły szczegóły + ablations
- R7+R8 outline

**Done criterion:** R1-R6 at 70%+ completion (zachowuje Writing rules constraint!) + R7+R8 outlined

### Iteracja 8 — Finalization

**Input:** R1-R8 drafts + all experimental results

**Output:**
- R7 (Wyniki) finalized — wszystkie 5 RQ answered z error analysis + ablations
- R8 (Podsumowanie) finalized — **5-wymiarowa kontrybucja per Defense scaffolding pkt 3** (negative-result framing jeśli H1 odpada)
- PJATK formatting applied (TNR 12pt, 1.5 spacing, 2.5cm margins, footnotes IEEE 10pt, headings IEEE)
- Bibliografia kompletna ~30+ pozycji, alphabetical
- Abstract PL + EN (max 1000 znaków each)
- Lista tabel + lista rysunków
- Final self-check (Task 10 PRO-D, 0pkt — checklist)
- Task 11 PRO-D comprehensive summary

**Done criterion:** PDF ready do hardbound + Task 11 submitted

### Iteration transitions

- Iteracja N+1 starts when Iteracja N done criterion met
- **Re-iteration acceptable** w razie failure (np. Iteracja 2 może mieć sub-iteracje 2a, 2b jeśli judge validation fails initially i wymaga prompt rewriting)
- Promotor sees artifacts as they exist — **no scheduled email**, async share via repo/DVC when artefakt ready

---

## Zakończenie

Delta v3.1 jest konsolidacją decyzji projektowych z 2026-05-15: rotacja domeny psych → farma (DEC-001), dodanie RQ5 cross-register (DEC-002), defense scaffolding zaszyte w `thesis_elements/CLAUDE.md`, źródła ujednolicone w `sources_catalog.md`. Konspekt v3 FINAL .docx pozostaje historical record (sekcje niezmienione nadal w mocy), niniejsza delta jest source of truth dla sekcji superseded.
