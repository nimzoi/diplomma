# R6. Konfiguracja modeli i ewaluacja

> **Status draftu:** methodology + ablations design 100% napisane. Wartości liczbowe (hyperparameters z Optuny, Cohen's kappa, accuracy@10) oznaczone `🟡 Final values from Optuna search post-Iteracja 2` lub analogicznie i będą uzupełnione po cyklach 1-3 (Iteracje 2-3) oraz końcowej walidacji judge'a (Iteracja 2). Cytacje z `🟡 Verify via citation-checker` nie zostały programatycznie zweryfikowane przed citation pass — wszystkie pozycje mają identifiable nazwę i publiczny DOI/arXiv ID, **żadna nie jest wymyślona**.
>
> **Source of truth:** `02b_konspekt_v3_updates.md` § II.7 (LLM-as-judge), § II.4.6 (hard negatives), § II.16 (iteracje); `decisions/DEC-002_chpl-ulotka-pairing.md` (cross-register RQ5); `assignments/plans/zadanie_06_plan.md` (Task 06 8-element struktura per model).
>
> **Defense scaffolding zaszyte:** ablacje A0-A4 (sekcja 6.4), kategoryczna error analysis (zapowiedź w 6.5; rozwinięcie w R7), 5-wymiarowa kontrybucja (zapowiedź w 6.6; pełen zapis w R8).

---

## 6.1 Architektura modeli

Pipeline retrievalu wykorzystuje **cztery role modelowe**, z których jedna (reranker) jest dotrenowywana, trzy pozostałe są zamrożone (`frozen`) w trakcie eksperymentów. Tabela 6.1 podsumowuje konfigurację.

**Tabela 6.1.** Konfiguracja modeli pipeline'u.

| Komponent | Model | Liczba parametrów | Status | Rola w pipeline |
|---|---|---|---|---|
| Embedder | BGE-M3 [1] | ~568 mln | frozen | Wstępny *dense retrieval* top-k (k=50) |
| Reranker | polish-reranker-roberta-v3 [2] | ~360 mln | **fine-tunable (RDZEŃ)** | Reranking top-k → top-n (n=10) |
| Generator (RAG) | Bielik 11B v3 [3] | ~11 mld | frozen | End-to-end odpowiedź dla *faithfulness* eval |
| LLM-as-judge | `<judge_model>` 🟡 *(top-1 z {Bielik 11B v3 / Gemma 3 27B / Qwen 3 32B / Claude Haiku 4.5} — finalny wybór po Iteracji 2)* | 11-32 mld | frozen | Pairwise / pointwise / faithfulness / cross-register scoring |

Sekcje 6.1.1-6.1.4 omawiają każdy z komponentów w konwencji 8-elementowej Task 06 (formuła problemu → reprezentacja → architektura → hiperparametry → setup treningowy → ewaluacja → interpretacja). Komponenty `frozen` opisano krócej (problem + reprezentacja + uzasadnienie wyboru); pełna ośmioelementowa struktura jest zarezerwowana dla rerankera (sekcja 6.2) jako rdzenia metodologicznego pracy.

### 6.1.1 Embedder BGE-M3 (frozen)

**Sformułowanie problemu.** Wstępny *retrieval* w pipeline RAG wymaga gęstej reprezentacji wektorowej zarówno dla zapytania, jak i dla każdego *passage* w korpusie. Embedder pełni rolę *recall-oriented* — celem jest pull-back nadmiernie szerokiego zbioru kandydatów (k=50), z którego *reranker* dokonuje precyzyjnej selekcji.

**Reprezentacja danych.** BGE-M3 generuje trzy równoległe reprezentacje per *chunk* tekstu [1]:

- *dense embedding* (1024-wymiarowy wektor zmiennoprzecinkowy),
- *sparse lexical weighting* (uczona reprezentacja TF-IDF-like — wagi przypisane tokenom),
- *multi-vector ColBERT-style* (sekwencja embeddingów per token, użyteczna dla *late interaction*).

W niniejszej pracy wykorzystywane są pierwsze dwie modalności (*dense + sparse*) z hybrydowym scoringiem przez Reciprocal Rank Fusion w Qdrant. Reprezentacja *multi-vector* nie jest wykorzystana ze względu na narzut storage (~3-5× większy index) bez dostatecznego marginalnego zysku w ewaluacjach pilotażowych autorki.

**Uzasadnienie wyboru.** Decyzja o wyborze BGE-M3 jako embeddera została podjęta po analizie alternatyw (`05_stack_techniczny.docx` § 1.1):

1. **Multimodalność reprezentacji w jednym modelu** — eliminuje konieczność równoległego utrzymywania osobnego encodera *sparse* (np. SPLADE) i *dense*.
2. **Konkurencyjne wyniki na MIRACL multilingual benchmark** [4] dla języka polskiego (proxy dla polish IR quality).
3. **Licencja MIT** — bez ograniczeń ani komercyjnych, ani badawczych.
4. **Frozen pozostawienie embeddera** — świadoma decyzja zakresu pracy: hard negative mining dla embeddera jest *out of scope* (`02b_konspekt_v3_updates.md` § II.3.4) — eliminuje pain point danych (jakość *negatives* dla *contrastive learning*) i utrzymuje fokus pracy na rerankerze.

### 6.1.2 Reranker polish-reranker-roberta-v3 (fine-tunable)

**Rationale domain adaptation (per `02b_konspekt_v3_updates.md` § II.2.1 update 2026-05-16).** Międzynarodowa terminologia farmaceutyczna (DCI / INN / kody ATC) jest **znana** przez polish-reranker-roberta-v3 base z pretrainingu (np. *sertralina* PL ≈ *sertraline* EN ≈ *sertralinum* INN; ATC `N06AB06` identyczny cross-language). Argument *„model nie zna farmaceutycznej terminologii"* jest overstated — łatwo obalony kontrprzykładem. Domain adaptation rerankera adresuje **polish-specific patterns wokół międzynarodowej terminologii**: (a) polska fleksja gramatyczna DCI przez 7 przypadków (*sertralina / sertralinę / sertraliny / sertralinie / sertraliną*) — reranker musi rozpoznać że to ten sam lek niezależnie od formy; (b) polski elastyczny szyk + złożona fleksja w zapytaniach (*„Czy sertralinę można brać z alkoholem"* vs *„Czy z alkoholem można brać sertralinę"*); (c) regulatorowa frazeologia PL specyficzna dla ChPL/Ulotek (*„Należy zachować szczególną ostrożność..."*, *„Nie zaleca się stosowania..."*); (d) polskie ramy regulacyjne bez angielskiego ekwiwalentu (*„ryczałt 30%"*, *„katalog leków refundowanych"*, programy lekowe B.xx); (e) polskie dosage instructions (*„dwa razy dziennie po posiłku"*, *„nie kruszyć tabletek"*). Plus **RQ5 cross-register** (DEC-002) jako genuinely novel piece — pacjent pisze *„zaszkodzi"*, ChPL mówi *„działanie niepożądane"* — unique to Polish PIL/SPC pair, brak w global literature (Grabowski [19] = EN-PL, NIE intra-PL). Pełen 8-elementowy opis rerankera w sekcji 6.2 opisuje **jak** te patterns są adresowane przez preference learning na corpus 6 strata.

### 6.1.3 Generator RAG Bielik 11B v3 (frozen)

**Sformułowanie problemu.** Generator pełni rolę *downstream* w pipeline RAG: na podstawie *retrieved* przez reranker top-n *passages* (n=10) syntetyzuje odpowiedź w języku polskim. Wykorzystany **wyłącznie** dla ewaluacji *faithfulness* (pomiar czy odpowiedź jest wsparta przez kontekst retrievalu, bez halucynacji wykraczających poza dostarczone *passages*) — generator NIE jest fine-tunowany w niniejszej pracy.

**Uzasadnienie wyboru.** Bielik 11B v3 [3] wybrany ze względu na (1) licencję Apache 2.0 (brak ograniczeń), (2) natywną obsługę języka polskiego, (3) okno kontekstu rozszerzone do ~131k tokenów przez YaRN scaling [5] — wystarczające dla typowego kontekstu RAG (~5-10k tokenów per zapytanie), (4) różność modelu względem `<judge_model>` (eliminacja *circular reasoning* — judge i generator powinny być różnymi modelami, aby uniknąć sztucznej wysokiej zgodności *self-evaluation*).

### 6.1.4 LLM-as-judge `<judge_model>` (frozen)

Pełen opis 4 protokołów judge'a, multi-stage walidacji oraz uzasadnienie wyboru zawarto w sekcji 6.3.

---

## 6.2 Reranker fine-tuning methodology

### 6.2.1 Sformułowanie problemu

**Zadanie ML.** Reranker `polish-reranker-roberta-v3` jest trenowany jako *cross-encoder* z **preference learning** w protokole *quadruplet* (jeden *positive* + trzy *negatives* per próbka treningowa). Zadanie sformułowane jako:

> Dla zapytania $q$, *passage'a positive* $p^+$ oraz trzech *passages negative* $p^-_1, p^-_2, p^-_3$, model uczy się przypisywać wyższy *relevance score* do $p^+$ niż do każdego z $p^-_i$:
> $$\text{score}(q, p^+) > \text{score}(q, p^-_i) \quad \forall i \in \{1, 2, 3\}.$$

**Reprezentacja wejścia.** Każda para $(q, p)$ jest tokenizowana wspólnie (`[CLS] q [SEP] p [SEP]`) i przepuszczana przez pojedynczy *forward pass* RoBERTa-large (cross-encoder, w przeciwieństwie do bi-encoderów typu BGE-M3 które kodują $q$ i $p$ niezależnie). Maksymalna długość sekwencji: parametr w siatce Optuny (kandydaci `{512, 768}` tokenów). Tekst dłuższy niż max_length jest obcinany od końca (`truncation=longest_first`).

**Funkcja straty.** Zastosowano *margin ranking loss* (alternatywa Plackett-Luce rozważana, ale margin ranking jest standardowym wyborem dla quadruplet preference [6]):

$$\mathcal{L} = \sum_{i=1}^{3} \max\left(0,\ \text{margin} - \text{score}(q, p^+) + \text{score}(q, p^-_i)\right)$$

z parametrem `margin` w siatce Optuny (kandydaci `{0.1, 0.3, 0.5}`).

**Uzasadnienie preference loss vs pointwise:** *Cross-encoder reranker* operacyjnie porównuje pary *passages* podczas inference (sortowanie top-k). Trening na preferencjach (czyli **względnym** porównaniu, nie absolutnym scoringu) jest bardziej spójny z faktycznym zadaniem inference niż *pointwise regression* na *relevance score* w skali kontynualnej. Argumentację metodologiczną wspierają wyniki Zheng i in. (2023) [7] dla LLM-as-judge: porównania *pairwise* są bardziej wiarygodne niż *pointwise* skalowanie absolutne.

### 6.2.2 Reprezentacja danych post-preprocessing

Dataset preferencji generowany w pipeline opisanym w `training_dataset_spec.md`:

- **Per cykl ~50 tys. *positives*** (z deterministycznym alignmentem section-aware ChPL/Ulotka i section-based OA journals — zobacz Tabela 3.X w R3),
- **Per *positive* — 3 *hard negatives*** (4-poziomowa strategia, sekcja 6.2.3),
- **Po deduplication i quality filter:** ~145 tys. preference samples kumulatywnie po 3 cyklach.

Każda próbka ma format JSONL:

```json
{
  "query": "Jakie są przeciwwskazania do sertraliny?",
  "positive": {"text": "...", "doc_id": "EU/1/06/.../001", "section": "4.3", "register": "professional"},
  "negatives": [
    {"text": "...", "level": "L2", "doc_id": "...", "section": "4.3", "register": "professional"},
    {"text": "...", "level": "L3", "doc_id": "...", "section": "4.4", "register": "professional"},
    {"text": "...", "level": "L1", "doc_id": "...", "section": "4.3", "register": "professional"}
  ],
  "metadata": {"query_type": "factual", "atc_class": "N06AB", "cycle": 1, "user_profile": "lekarz"}
}
```

Każdy `negative` ma poziom trudności `L1`-`L4` zgodnie z 4-poziomową strategią.

### 6.2.3 Hard negatives — 4-poziomowa strategia próbkowania

Strategia *hard negative mining* dla rerankera została zaprojektowana z **czterema poziomami trudności**, aby model uczył się fine-grained distinctions zamiast wyłącznie coarse separation. Strategia inspirowana DPR Karpukhin i in. (2020) [8]; rozszerzona o czwarty poziom (`L4 — cross-register confusion`) specyficzny dla RQ5.

**Tabela 6.2.** Strategia *hard negatives* — 4 poziomy trudności (per `02b_konspekt_v3_updates.md` § II.4.6).

| Poziom | Definicja | Proporcja w datasecie | Przykład (sertralina jako *positive*) | Trudność |
|---|---|---|---|---|
| **L1** (easy anchor) | Inna klasa ATC | 15% | Negative: ChPL metforminy (A10BA antidiabetic), sekcja 4.3 | niska |
| **L2** (medium standard) | Ta sama klasa ATC, inny lek | 50% | Negative: ChPL fluoksetyny (N06AB SSRI), sekcja 4.3 | średnia |
| **L3** (hard, core challenge) | Ten sam lek, inna sekcja | 30% | Negative: ChPL sertraliny sekcja 4.4 (specjalne ostrzeżenia — overlap leksykalny z 4.3) | wysoka |
| **L4** (very hard, RQ5-specific) | Ten sam lek, *cross-register confusion* | 5% | Query lay (Ulotka), negative: ChPL sekcja 4.4 (wspomina ten sam *concept* w innym kontekście) | bardzo wysoka |

**Uzasadnienie proporcji:** L1 (15%) pełni rolę *anchor* (sanity check, że model utrzymuje coarse separation między klasami farmaceutycznymi). L2 (50%) odpowiada najczęstszemu realnemu scenariuszowi *query → distinguish między lekami w obrębie klasy ATC*. L3 (30%) jest **rdzeniem ML challenge** — testuje czy reranker rozróżnia *intent* sekcji ChPL (przeciwwskazania ≠ specjalne ostrzeżenia ≠ działania niepożądane ≠ interakcje) nawet dla tego samego leku. L4 (5%) jest *specialty* dla RQ5; mała proporcja celowa — zbyt wysoki udział L4 ryzykuje, że model uczyłby się wyłącznie unikać pomyłek register'owych zamiast distinguish semantyki.

**Walidacja jakości hard negatives:** spot-check 100 quadrupletów (positive + 3 negatives) jest manualnie zweryfikowany przez autorkę przed startem pierwszego cyklu treningu — sprawdzane jest (a) czy proporcje L1/L2/L3/L4 utrzymują się w docelowym rozkładzie, (b) czy *negatives* są faktycznie negatywne (a nie *tied/synonymous* z *positive*). Acceptance threshold: ≥85% poprawnych klasyfikacji w spot-check.

### 6.2.4 Hiperparametry — Optuna search space

Hiperparametry treningu zostaną zoptymalizowane w cyklu 1 przez **Bayesian search w Optunie** [9] (TPE sampler). Każdy *trial* zostanie zarejestrowany jako osobny *MLflow run* (parent run = study, child runs = trials), z kategoryzacją tagiem `study=cycle_N`.

**Tabela 6.3.** Hiperparametry rerankera — siatka Optuny (Iteracja 2 cykl 1).

| Hiperparametr | Search space | Rozkład | Best (cycle 1) | Best (cycle 2) | Best (cycle 3) |
|---|---|---|---|---|---|
| Learning rate | `{1e-5, 3e-5, 5e-5}` | log-uniform | 🟡 *Final values from Optuna search post-Iteracja 2* | 🟡 *post-Iteracja 3* | 🟡 *post-Iteracja 3* |
| Batch size | `{16, 32}` | categorical | 🟡 *post-Iteracja 2* | 🟡 *post-Iteracja 3* | 🟡 *post-Iteracja 3* |
| Epochs | `{2, 3, 4}` | categorical | 🟡 *post-Iteracja 2* | 🟡 *post-Iteracja 3* | 🟡 *post-Iteracja 3* |
| Max sequence length | `{512, 768}` | categorical | 🟡 *post-Iteracja 2* | 🟡 *post-Iteracja 3* | 🟡 *post-Iteracja 3* |
| Warmup ratio | `{0.06, 0.1}` | categorical | 🟡 *post-Iteracja 2* | 🟡 *post-Iteracja 3* | 🟡 *post-Iteracja 3* |
| Margin | `{0.1, 0.3, 0.5}` | categorical | 🟡 *post-Iteracja 2* | 🟡 *post-Iteracja 3* | 🟡 *post-Iteracja 3* |
| Weight decay | `{0.01, 0.1}` | categorical | 🟡 *post-Iteracja 2* | 🟡 *post-Iteracja 3* | 🟡 *post-Iteracja 3* |

**Search budget:** 30 trials per cykl × 3 cykle × 3 random seeds = **270 *MLflow runs* total**. Liczba ograniczona przepustowością SP7 H200 GPU (estymowane ~30-60 min per epoch dla ~50k preference samples na batch_size=32).

**Wybór najlepszego trialu:** według metryki `nDCG@10` na *validation split* (15% korpusu document-level, NIE chunk-level — zobacz sekcja 6.6).

### 6.2.5 Setup treningowy

**Optimizer:** AdamW [10] — standardowy wybór dla fine-tuning modeli RoBERTa, z hiperparametrami `betas=(0.9, 0.999)` (default), `eps=1e-8`, `weight_decay` w siatce Optuny.

**Learning rate schedule:** *cosine schedule with warmup* — `warmup_ratio` w siatce Optuny, decay liniowy do 0 po końcu treningu. Schedule wybrany ze względu na empiryczną stabilność dla fine-tuning *cross-encoders* [11].

**Mixed precision:** `bf16` (BFloat16) na SP7 H200 GPU — kompromis między stabilnością numeryczną (vs `fp16`, ryzyko *NaN* dla małych gradientów) a oszczędnością pamięci (vs `fp32`).

**Early stopping:** monitoring `nDCG@10` na *validation split* z `patience=2` epok i `min_delta=0.005` (0.5pp). Wczesne zatrzymanie zapobiega *overfittingu* przy małych zbiorach treningowych — szczególnie istotne w cyklach 2-3, gdy model jest już zaawansowany w fine-tuning.

**3 random seeds:** każdy trial Optuny jest powtarzany dla `seeds = {42, 1337, 2026}`. Final reporting: **mean ± std** dla każdej metryki. Spójne z protokołem ewaluacji przyjętym dla całej pracy (sekcja 6.6) i z `02b_konspekt_v3_updates.md` § II.4.5.

**Hardware:** SP7 GPU H200 80GB (transfer infrastrukturalny z poprzedniej wersji pracy — `04_dev_environment.docx`). Estymowany koszt obliczeniowy całego cyklu treningu (30 trials × 3 seeds × ~3 epoch × ~30 min/epoch) ~135 godzin GPU per cykl, czyli ~5-6 dni *wall clock time* przy SP7 dedicated.

**Reprodukowalność:** wszystkie *seeds* zafiksowane (`torch.manual_seed`, `numpy.random.seed`, `random.seed`, `transformers.set_seed`). Wszystkie konfiguracje zapisane jako pliki YAML (Hydra) i zwersjonowane przez DVC. Każdy *MLflow run* zawiera *fingerprint* hashe datasetu (`positives + negatives JSONL`) oraz commit hash kodu.

### 6.2.6 Setup ewaluacji

Pełen opis procedury ewaluacyjnej — sekcja 6.6. Streszczenie:

- **Document-level split** (NIE chunk-level — przeciwdziała leakage chunków z tego samego dokumentu między train/val/test).
- **Primary eval set:** 200 par *gold standard* manualnie ranked przez autorkę z psychiatrycznej podgrupy ATC N05/N06 (`02b_konspekt_v3_updates.md` § II.4.3).
- **Secondary eval set:** 1800 par *cross-register* dla RQ5 (sekcja 6.5).
- **Baselines:** BM25 (Pyserini) [12], dense BGE-M3 alone, base polish-reranker bez fine-tune, chunking variants — opisane w R7 jako *comparative evaluation*.

### 6.2.7 Interpretacja modelu i diagnostics

Element 8 z 8-elementowej struktury Task 06 (interpretacja + diagnostics) jest realizowany w R7 jako:

- **Categorical error analysis** na próbce ≥100 niepoprawnych rankingów per cykl (zapowiedź w sekcji 6.5; pełna 6-poziomowa taksonomia w R7 sekcja 7.X — *Defense scaffolding pkt 2*).
- **Attention heatmaps** na ~10 reprezentatywnych przykładach (top-K heads × token positions) — opcjonalne, jeśli czas pozwoli.
- **Comparison qualitative** przez Gradio `Compare` zakładkę (`02b_konspekt_v3_updates.md` § II.5) — side-by-side base reranker vs dotrenowany na 5-10 przypadkach reprezentatywnych.

---

## 6.3 LLM-as-judge — 4 protokoły i multi-stage walidacja

### 6.3.1 Sformułowanie problemu i 4 protokoły

LLM-as-judge jest **centralnym komponentem metodologicznym pracy** — jakość sygnału treningowego rerankera (preference labels generowane przez judge) determinuje sufit jakości fine-tuningu. Zastosowano **cztery protokoły** wykorzystania jednego modelu sędziowskiego (`<judge_model>`), każdy w innej roli, każdy z inną definicją operacyjną. Tabela 6.4 podsumowuje protokoły.

**Tabela 6.4.** Cztery protokoły LLM-as-judge (per `02b_konspekt_v3_updates.md` § II.7).

| # | Protokół | Format wejścia | Format wyjścia | Rola |
|---|---|---|---|---|
| 1 | **Pairwise** | (query, passage_A, passage_B) | `{preferred: A|B|tie, reasoning}` | **Główny sygnał treningowy** dla preference learning rerankera |
| 2 | **Pointwise** | (query, passage) | `{score: 0-5, reasoning}` | Sanity check spójności (na próbce ~500 par) |
| 3 | **Faithfulness** | (query, retrieved_passages, generated_answer) | `{faithful: bool, unsupported_claims: [...], reasoning}` | End-to-end metric — czy odpowiedź Bielika jest wsparta przez kontekst |
| 4 | **Cross-register pair scoring** (NEW dla RQ5) | (query_lay, passage_pro_A, passage_pro_B) | `{preferred: A|B|tie, semantic_match_quality: 0-5, register_appropriateness: 0-5, reasoning}` | Ocena cross-register par dla RQ5 |

**Protokół 1 — Pairwise** jako główny: cross-encoder reranker dokładnie tak działa (porównuje *passages*). Empirycznie *pairwise* jest wiarygodniejsze niż *pointwise* — LLM-y są dowodnie lepsze w porównywaniu niż w skalowaniu absolutnym (Zheng i in. 2023 [7]).

**Protokół 2 — Pointwise** jako sanity check spójności: dla próbki ~500 par sprawdzane jest, czy jeśli judge ocenił *passage* A jako 5 i B jako 2 w *pointwise*, to powinien też w *pairwise* wybrać A. **Niespójność > 20%** jest sygnałem alarmowym wymagającym rewizji prompt template.

**Protokół 3 — Faithfulness** jako end-to-end metric: ocena czy cała odpowiedź RAG (po retreningu rerankera) jest *faithful* — wszystkie stwierdzenia są wsparte przez retrieved context, brak halucynacji wykraczających poza kontekst. Wpada do R7 jako *downstream impact metric* — pokazuje czy lepszy retrieval przekłada się na lepszą jakość odpowiedzi.

**Protokół 4 — Cross-register pair scoring** (NEW dla RQ5, per `decisions/DEC-002_chpl-ulotka-pairing.md`): judge dostaje *query* w rejestrze laypersonowskim (z Ulotki) + *passage* A w rejestrze profesjonalnym (z ChPL) + *passage* B w rejestrze profesjonalnym (z innego ChPL tej samej klasy ATC, *hard negative* L2). Wyjście JSON zawiera **dwa wymiary scoringu**:

- *semantic_match_quality* (0-5): czy A vs B faktycznie odpowiada na semantyczny *content* zapytania (niezależnie od stylu),
- *register_appropriateness* (0-5): czy odpowiedź jest stylistycznie/leksykalnie adekwatna do rejestru zapytania.

Rozdzielenie wymiarów pozwala diagnozować, czy reranker miss-rankuje **semantycznie** (poważny problem) czy wyłącznie **stylistycznie** (mniejszy problem w kontekście cross-register, gdzie z definicji oczekuje się asymetrii rejestrów).

### 6.3.2 Wybór modelu judge'a — multi-stage walidacja

Wybór modelu judge'a (`<judge_model>` w niniejszym dokumencie) jest dwuetapowy zgodnie z `02b_konspekt_v3_updates.md` § II.7 (multi-stage validation):

**Stage 1 — Pilot (Iteracja 0b):**

Cztery kandydaci modeli sędziowskich oceniani na **n=30 par cross-register** (protokół 4):

- **Bielik 11B v3** (Apache 2.0, polski natywny generator),
- **Gemma 3 27B** (Apache 2.0, multilingual, większy),
- **Qwen 3 32B** (Apache 2.0, multilingual, największy w shortliście),
- **Claude Haiku 4.5** (paid API, niezależny ekosystem komercyjny — cross-validation argument).

**Output etapu 1 — top-2 shortlist** (NIE single winner). Powód metodologiczny: n=30 jest statystycznie *thin* dla *4-way comparison*. Spodziewany **Cohen's kappa CI ±0.15-0.20** (Landis i Koch 1977 [13] dla agreement strength interpretation; szczegółowy CI calculator dla kappa np. Cantor 1996 [14]) — ranking ambiguous w połowie przypadków. Decyzja na podstawie n=30 jest *premature*.

**Stage 2 — Final winner pick (Iteracja 2):**

Top-2 z etapu 1 są ewaluowane *head-to-head* na **n=200 manualnych labels** autorki (RQ2/H2 validation). Single winner pick'ed z defensible **Cohen's kappa CI ±0.05-0.08**. Manualne labels by autorka, próbka cross-register sprawdza również, czy judge rozróżnia *semantic* vs *register* dimensions (protokół 4).

**Tabela 6.5.** Multi-stage walidacja judge'a — wyniki kappa.

| Stage | Iteracja | n | Bielik 11B v3 | Gemma 3 27B | Qwen 3 32B | Claude Haiku 4.5 |
|---|---|---|---|---|---|---|
| **1: Pilot** | 0b | 30 | 🟡 κ=*pilot post-Iter. 0b* | 🟡 κ=*pilot post-Iter. 0b* | 🟡 κ=*pilot post-Iter. 0b* | 🟡 κ=*pilot post-Iter. 0b* |
| **2: Final** | 2 | 200 | 🟡 κ=*final post-Iter. 2* (jeśli w top-2) | 🟡 κ=*final post-Iter. 2* (jeśli w top-2) | 🟡 κ=*final post-Iter. 2* (jeśli w top-2) | 🟡 κ=*final post-Iter. 2* (jeśli w top-2) |

**Interpretacja kappa** (Landis i Koch 1977 [13]):

- κ < 0.20 — *poor agreement* (judge nieprzydatny → eskalacja)
- 0.20 ≤ κ < 0.40 — *fair* (judge prawdopodobnie nieprzydatny — wymaga rewizji prompt'a)
- 0.40 ≤ κ < 0.60 — *moderate* (acceptable, ale flag)
- 0.60 ≤ κ < 0.80 — *substantial* (target dla H2)
- κ ≥ 0.80 — *almost perfect* (idealny; target stretch)

**Threshold dla H2:** κ ≥ 0.50 = acceptable agreement (RQ2 H2 hipoteza warunkowa). Jeżeli κ < 0.50 → eskalacja: rewizja prompt template, ewaluacja chain-of-thought wariantu, ewentualne porównanie z większym modelem (np. Qwen 3 72B przez HF Inference API), flag w R8 limitations.

### 6.3.3 Prompt templates — wzorzec budowy

Prompt templates dla 4 protokołów następują wzorcowi:

```
[ROLA / SYSTEM]
Jesteś ekspertem oceniającym jakość rankingu pasaży w polskim systemie RAG dla
domeny farmakologii klinicznej. Twoje oceny są używane jako sygnał treningowy
dla rerankera. Bądź precyzyjny, krótki i konsekwentny.

[INSTRUKCJA]
{TASK_DESCRIPTION}

[FEW-SHOT EXAMPLES]
{2-3 in-context examples z domain-specific cases}

[ZADANIE]
Query: {QUERY}
{INPUT_FIELDS specyficzne dla protokołu}

[FORMAT WYJŚCIA]
Odpowiedź WYŁĄCZNIE w formacie JSON:
{JSON_SCHEMA specyficzny dla protokołu}
```

Każda wersja prompt template jest **wersjonowana w Langfuse** (`05_stack_techniczny.docx` § 5.1) — dla auditability i ewentualnego A/B testowania wersji prompt'a w cyklach 2-3.

### 6.3.4 Quality assurance dla judge'a w produkcyjnym pipeline

W każdym cyklu treningu (1, 2, 3) na próbce **100 losowych preference labels generated by judge** wykonywany jest **secondary spot-check** autorki (~30-60 min wysiłku per cykl). Cel: detekcja *drift'u* judge'a (czy jakość labels nie spada między cyklami z powodu np. zmian w typach query) i ewentualna *escalation* (rewizja prompt, regeneracja labels).

---

## 6.4 Ablations A1-A4 — Defense scaffolding pkt 1

Cykl 1 retreningu rerankera uwzględnia **cztery ablacje** (A1-A4), z których każda jest osobnym *MLflow run* i osobnym wynikiem do dyskusji w R7. Ablacje zostały zaprojektowane jako *Defense scaffolding* (per `thesis_elements/CLAUDE.md` Defense scaffolding pkt 1) — adresują pytania, które komisja egzaminacyjna może zadać, przed tym, jak je zada.

**Tabela 6.6.** Ablacje A0-A4 — design eksperymentalny.

| # | Ablacja | Wariant treningowy | Cel diagnostyczny | Oczekiwana interpretacja |
|---|---|---|---|---|
| **A0** | baseline (default) | polish-reranker-roberta-v3 + `<judge_model>` + 4-level hard negatives + full pharma corpus + ChPL+Ulotka | Pełen pipeline reference (RQ1 H1 primary answer) | nDCG@10 ≥ baseline+10pp (RQ1 success criterion) |
| **A1** | judge → random preference labels | `<judge_model>` zastąpiony losowym samplowaniem `{A, B, tie}` | **Czy improvement wynika z signal quality, czy z domain exposure?** Random labels eliminują semantyczny sygnał z judge'a, pozostawiając tylko exposure modelu na *domain corpus*. | Jeśli A1 daje gain ≥50% A0 — judge nic nie wnosi (sygnał alarmowy dla RQ2). Jeśli A1 daje gain < 30% A0 — judge jest źródłem improvement'u. |
| **A2** | judge → Bielik (cross-model) | `<judge_model>` zastąpiony Bielik 11B v3 (jako alternatywny judge) | **Cross-model robustness — czy konkluzje H2 trzymają się dla innego polskiego LLM-a?** Mitygacja ryzyka, że obserwowany improvement jest specyficzny dla idiosynkrazji jednego konkretnego judge'a. | Jeśli A2 ≈ A0 (delta < 3pp) — cross-model robustness potwierdzona. Jeśli A2 << A0 — judge selection matters znacznie, raportować w R8 limitations. |
| **A3** | corpus → psych-only | Trening tylko na ATC N05-N06 (psych subset, ~30% korpusu) | **Domain breadth effect — czy szeroki pharma corpus pomaga, czy psych-only już wystarcza?** Adresuje obawę, że szeroka domena rozprasza fine-tuning sygnał. | Jeśli A3 ≥ A0 — szeroka domena nie pomaga (rozważyć refokus na psych). Jeśli A3 << A0 — szeroka domena daje *transfer learning* benefit. |
| **A4** | ChPL-only training (kontrast vs A0 default ChPL+Ulotka) | training corpus → tylko ChPL bez Ulotek (A0 default = ChPL+Ulotka) | **Effect of register diversity — kluczowe dla RQ5.** Czy obecność Ulotek w training set pomaga rerankerowi handlować *cross-register* queries? | Jeśli A4 < A0 znacznie na *cross-register test set* — Ulotki w training są **niezbędne** dla RQ5. Jeśli A4 ≈ A0 — Ulotki marginalnie pomocne (nadal pozytywne dla RQ5, ale słabszy argument). |

### 6.4.1 Setup eksperymentalny każdej ablacji

Wszystkie ablacje (A0-A4) używają **identycznych** ustawień dla:

- *splits* (document-level train/val/test, 70/15/15),
- *random seeds* (`{42, 1337, 2026}`),
- *hyperparameter search* (siatka Optuny z sekcji 6.2.4 — top-K=3 *trials* per ablacja w cyklu 1, full search 30 *trials* dla A0),
- *eval set* (200 par gold standard primary + 1800 par cross-register secondary).

Różni się **wyłącznie**: dla A1 — judge → random labels, dla A2 — judge → Bielik, dla A3 — training corpus → psych-only subset, dla A4 — training corpus → ChPL-only (bez Ulotek).

### 6.4.2 Statistical significance i raportowanie

Każda ablacja vs A0 jest testowana **paired bootstrap test** [15] na 3 random seeds (mean ± std raportowane w R7 sekcja 7.X). Significance threshold: **p < 0.05** dla per-ablation conclusion. Effect size: **Cohen's d** dla odróżnienia statystycznej istotności od praktycznej istotności.

**Per ablation MLflow tags:**

```yaml
mlflow.tag.ablation: A1 | A2 | A3 | A4 | A0
mlflow.tag.cycle: 1 | 2 | 3
mlflow.tag.seed: 42 | 1337 | 2026
mlflow.tag.judge_model: <judge_model> | random | bielik-11b-v3
mlflow.tag.training_corpus: full_pharma | psych_only_n05_n06 | chpl_only
mlflow.tag.eval_set: gold_standard_200 | cross_register_1800
```

### 6.4.3 Decyzja w R6 (formalny zapis)

Niniejsza sekcja stanowi *de facto* zobowiązanie do wykonania ablacji A1-A4. Dla R7 obowiązuje sformułowanie:

> "W cyklu 1 wykonano cztery ablacje (A1-A4) służące diagnostyce źródła poprawy retrieval quality. Wyniki ablacji raportowane w sekcji 7.X (Tabela 7.X) wraz z interpretacją per RQ1, RQ2, RQ5."

Brak wykonanej którejś z ablacji A1-A4 w R7 traktowane jako *spec violation* niniejszego rozdziału.

---

## 6.5 Metryki ewaluacji

Niniejsza sekcja definiuje wszystkie metryki używane w niniejszej pracy. Metryki podzielone są na cztery rodziny: (a) retrieval-side classical IR, (b) cross-register specific (RQ5), (c) judge quality (RQ2), (d) end-to-end RAG (RAGAS).

### 6.5.1 Retrieval-side classical IR

**nDCG@10 (Normalized Discounted Cumulative Gain at rank 10).** Standardowa metryka jakości rankingu uwzględniająca **graduated relevance** (Järvelin i Kekäläinen 2002 [16]):

$$\text{nDCG@10} = \frac{1}{\text{IDCG@10}} \sum_{i=1}^{10} \frac{2^{\text{rel}_i} - 1}{\log_2(i+1)}$$

gdzie $\text{rel}_i \in \{0, 1, 2\}$ to graduated relevance (irrelevant / partially relevant / relevant) na position $i$, a IDCG@10 to ideal DCG dla danego *gold ranking*. Zakres: $[0, 1]$. **Primary metric** dla RQ1 H1.

**MRR@10 (Mean Reciprocal Rank at rank 10).** Średnia odwrotna pozycja pierwszego *relevant passage'a* w top-10 [17]:

$$\text{MRR@10} = \frac{1}{|Q|} \sum_{q \in Q} \frac{1}{\text{rank}_q}$$

gdzie $\text{rank}_q$ to pozycja pierwszego *relevant passage'a* dla zapytania $q$ (jeżeli wśród top-10 nie znajduje się relevant passage, to $1/\text{rank}_q = 0$). Zakres: $[0, 1]$.

**accuracy@10.** Proporcja zapytań, dla których *gold passage* znalazł się w top-10 (binary, hit/miss):

$$\text{accuracy@10} = \frac{|\{q \in Q : \text{gold}_q \in \text{top-10}_q\}|}{|Q|}$$

Używana **przede wszystkim w cross-register** evaluation (sekcja 6.5.2), gdzie graduated relevance nie jest dostępne (alignment deterministyczny przez `productID` daje binary gold/non-gold).

### 6.5.2 Cross-register metrics (RQ5)

Z `02b_konspekt_v3_updates.md` § II.3.3 RQ5 setup:

- **accuracy@10 lay→pro** — query z Ulotki, gold = ChPL sekcja tego samego leku.
- **accuracy@10 pro→lay** — query z ChPL, gold = Ulotka sekcja tego samego leku.
- **MRR@10 lay→pro** i **MRR@10 pro→lay** osobno — *cross-register* może być asymetryczny: lay queries zwykle krótsze, mniej technical; pro queries dłuższe, bogatsze terminologicznie → różny *ranking difficulty*.
- **Aggregate accuracy@10 i MRR@10** (mean obu directions) jako single-number reporting.
- **Direction asymmetry gap:**
  $$\Delta_{\text{dir}} = |\text{MRR}_{\text{lay}\to\text{pro}} - \text{MRR}_{\text{pro}\to\text{lay}}|$$
  measure czy reranker jest stronniczy ze względu na directionality. $\Delta_{\text{dir}} > 0.10$ flagowane jako concern dla *register bias*.
- **Same-register baseline** (in-distribution training set) jako reference — porównanie *gap same-vs-cross* (RQ5 H5: gap ≤ 5pp poniżej same-register).

### 6.5.3 Judge quality (RQ2)

**Cohen's kappa (Cohen 1960) [18]:**

$$\kappa = \frac{p_o - p_e}{1 - p_e}$$

gdzie $p_o$ to obserwowana zgodność (raw agreement %), $p_e$ to oczekiwana zgodność losowa. Stosowane w trzy-poziomowej skali ordinal (preferred A / B / tie). **Threshold dla H2:** κ ≥ 0.50 acceptable, κ ≥ 0.75 strong.

**Pairwise agreement %** (raw):

$$\text{agreement\%} = \frac{|\{(q, p_A, p_B) : \text{judge}(q, p_A, p_B) = \text{author}(q, p_A, p_B)\}|}{|\text{validation set}|}$$

Reportowane jako secondary obok kappy (kappa jest bardziej rygorystyczna, agreement % jest bardziej intuicyjne).

**Pointwise-pairwise consistency** (sanity check spójności judge'a):

$$\text{consistency\%} = \frac{|\{q : \text{pointwise rank} = \text{pairwise preferred}\}|}{|\text{sample}|}$$

Threshold: > 80% (poniżej = sygnał alarmowy o jakości judge'a).

### 6.5.4 End-to-end RAG (RAGAS framework)

Z RAGAS (Es i in. 2024) [19]:

- **context_precision:** czy retrieved *passages* są relewantne dla zapytania (ranking-side, niezależnie od generation),
- **context_recall:** czy retrieved *passages* pokrywają wszystkie wymagane informacje dla *gold answer*,
- **faithfulness:** czy generated answer jest wsparta przez retrieved context (brak halucynacji),
- **answer_relevancy:** czy generated answer faktycznie odpowiada na zapytanie.

**Evaluator:** Claude Haiku 4.5 przez API (per `05_stack_techniczny.docx` § X.2 — niezależny commercial reasoning model dla cross-validation, neutralizuje argument *shared bias* polskiego open-source ekosystemu).

Reportowane w R7 jako **secondary metrics** obok primary nDCG@10/MRR@10. Rola: pokazują czy lepszy retrieval przekłada się na lepszą jakość odpowiedzi *downstream* (faithfulness), oraz dostarczają drugiego punktu widzenia na *retrieval quality* (context_precision/recall, niezależne od ranking-aware nDCG).

### 6.5.5 Statistical reporting protocol

Wszystkie metryki raportowane jako **mean ± std** z 3 random seeds (`{42, 1337, 2026}`). Significance test: **paired bootstrap** [15] dla porównań *model vs baseline*. Effect size: **Cohen's d** dla magnitude poprawy.

**Confidence intervals:** 95% CI dla każdej metryki w final R7 tables, calculated z 3 seeds × bootstrap 1000 resamples.

**Categorical error analysis** (zapowiedź — pełna implementacja w R7 sekcja 7.X per *Defense scaffolding pkt 2*): po każdym cyklu retreningu, **kategoryzacja błędów** na próbce ≥100 niepoprawnych rankingów (pozycja gold passage > 5 w top-10) wg 6-poziomowej taksonomii: *terminology miss / ambiguous query / length mismatch / OOD chunk / register mismatch / OCR artifact*. Decyzja: nawet jeżeli nDCG@10 nie poprawia się dramatically, **rozkład błędów to wartościowy wynik metodologiczny**.

---

## 6.6 Procedura ewaluacyjna

### 6.6.1 Document-level split — przeciw leakage

Wszystkie eksperymenty stosują **document-level split** (NIE chunk-level):

- *Train:* ~70% korpusu document-level (wszystkie *chunki* z dokumentu trafiają do *train*).
- *Validation:* ~15% korpusu, do tuningu hiperparametrów Optuna.
- *Test:* ~15% korpusu + 200-par manual gold standard set jako *held-out*.

**Uzasadnienie document-level (a nie chunk-level):** chunki z tego samego dokumentu są semantycznie powiązane (ten sam *concept context*). Przy chunk-level split ryzyko leakage jest wysokie — model może uczyć się rozpoznawać chunki z tego samego dokumentu po cross-chunk lexical overlap, zamiast uczyć się generalizable retrieval signal. Document-level split eliminuje tę klasy leakage.

**Stratyfikacja:** split jest **stratyfikowany po klasie ATC** (`02b_konspekt_v3_updates.md` § II.4.5) — utrzymuje proporcje N05/N06/inne ATC w każdym splicie. Stratyfikacja chroni przed przypadkowym przesunięciem rozkładu klas między splitami przy małym N (~4100 dokumentów).

### 6.6.2 Eval sets — strategia

**Primary: 200 par gold standard (psych subset, manual ranked):**

- Próbkowane z **psychiatrycznej podgrupy** korpusu (ATC N05 *Psycholeptica* + N06 *Psychoanaleptica*) zgodnie z `02b_konspekt_v3_updates.md` § II.4.3.
- Manual relevance labels (relevant / partially relevant / irrelevant) by autorka.
- **Świadoma decyzja architektoniczna** (NIE *cherry-picking*): leverage manual validation kompetencji autorki na poddomenie którą autorka zna, dla rygorystycznej walidacji LLM-as-judge agreement (RQ2/H2 — najsłabiej zabezpieczona hipoteza). Eval set wąski (psych), training corpus szeroki (cała farmakologia).
- Decyzja explicit zapisana w R5 sekcja "Eval set strategy" + `decisions/DEC-001_wybor-domeny.md`.

**Secondary: 1800 par cross-register (RQ5):**

- 900 par lay→pro + 900 par pro→lay.
- Programatycznie wygenerowane z 900 paired par leków (per `decisions/DEC-002_chpl-ulotka-pairing.md`).
- Gold standard implicite przez **deterministyczny `productID` alignment** z URPL RPL feed.
- Spot-check manual na 50 par (5% wielkości) — autorka weryfikuje, czy alignment jest poprawny i czy brak ewidentnych mismatch'ów.

**Tertiary: ~1500-2000 par LLM-generated rozszerzony eval set:**

- Generowane przez Bielik / `<judge_model>` z few-shot prompt template.
- Walidacja spot-check 10% (~150-200 par manualnie).
- Używany do **hyperparameter tuning** na *validation split*, NIE do final reportingu w R7.
- Rationale: rozszerzony eval set zapewnia wystarczająco dużą próbę dla wiarygodnego *signal* przy hyperparameter search; final reporting trzyma się primary 200 par + secondary 1800 par jako rygorystycznego baseline.

### 6.6.3 Cykle 1, 2, 3 — plateau analysis (RQ3)

Per `02b_konspekt_v3_updates.md` § II.16 (iteracje 2-3):

- **Cykl 1** (Iteracja 2): pierwsza instancja fine-tuningu na cumulative 50k preference samples (wraz z A1-A4 ablacjami).
- **Cykl 2** (Iteracja 3): fresh synthetic queries generated by Bielik, fresh judge labels generated by `<judge_model>`, retrening na cumulative ~95k preference samples (cykl 1 + cykl 2 fresh).
- **Cykl 3** (Iteracja 3): kolejna iteracja, cumulative ~145k preference samples.

**Plateau analysis dla RQ3 H3:** czy cykl 3 daje ≤2pp dodatkowej poprawy nDCG@10 vs cykl 2 (statystycznie nieistotna w 3-seed setup, p > 0.05). Hipoteza: **plateau po cyklu 2** — dodatkowy cykl daje marginalny gain, kosztu kompletnego retreningu nie uzasadnia.

### 6.6.4 A/B test gating (deployment workflow)

Dla każdego cyklu w MLflow Model Registry stosowane jest **automated A/B testing**:

1. Cykl N completes → reranker zarejestrowany jako `Staging`.
2. A/B test: nowy reranker vs poprzedni vs base na *held-out test set*.
3. **Wins** (Δ nDCG@10 ≥ 0.5pp + p < 0.05 paired bootstrap): promote → `Production` → CI/CD build → deploy do TEI → smoke test → traffic switch.
4. **Loss/draw:** keep poprzednią wersję, alert user (Grafana dashboard), investigation flag.

A/B test gating jest zarówno *MLOps narrative element* (R5 architektura), jak i *defensive evaluation framework* — deployment każdego cyklu retreningu wymaga statystycznej weryfikacji lepszości.

### 6.6.5 Cross-cycle dataset versioning

Każdy cykl ma osobne **DVC-versioned datasets:**

- `preferences_cycle_1.jsonl` (~50k samples, hash `sha256:...`)
- `preferences_cycle_2.jsonl` (~50k fresh + cumulative)
- `preferences_cycle_3.jsonl` (~50k fresh + cumulative)

Dataset hashes są częścią *MLflow run fingerprint* — pełna *reproducibility chain*: model checkpoint → hyperparams → dataset hash → corpus version → code commit.

---

## 6.7 Podsumowanie rozdziału

Niniejszy rozdział sformalizował **konfigurację modeli i protokół ewaluacyjny** pracy. Centralnym komponentem ML jest reranker `polish-reranker-roberta-v3` (~360 mln parametrów) dotrenowywany w trzech cyklach iteracyjnego retreningu z preference learning na *quadrupletach* z 4-poziomową strategią *hard negative mining* (L1 easy / L2 medium / L3 hard / L4 cross-register). Pozostałe komponenty (BGE-M3 embedder, Bielik 11B v3 generator, `<judge_model>` LLM-as-judge) pozostają zamrożone w ramach scope pracy.

LLM-as-judge wykorzystuje **cztery protokoły** (pairwise / pointwise / faithfulness / cross-register pair scoring), z których trzy pierwsze są standardowe w literaturze [7], a czwarty (cross-register pair scoring z dwuwymiarowym scoringiem *semantic match* + *register appropriateness*) jest **methodological novelty** specyficzną dla RQ5. Wybór modelu judge'a jest dwuetapowy: pilot na n=30 par (Iteracja 0b — top-2 shortlist), final on n=200 manual labels (Iteracja 2 — single winner).

**Cztery ablacje A1-A4** (sekcja 6.4) stanowią *Defense scaffolding* pracy: A1 (judge → random) testuje signal quality, A2 (judge → Bielik) testuje cross-model robustness, A3 (corpus → psych-only) testuje domain breadth effect, A4 (ChPL-only vs ChPL+Ulotka) testuje register diversity dla RQ5. Każda ablacja jest osobnym *MLflow run* z pełną *reproducibility chain*.

Procedura ewaluacyjna stosuje **document-level split** (przeciw chunk-level leakage), **3 random seeds** dla statystycznej istotności, **Optuna Bayesian search** dla hyperparams, **A/B test gating** w MLflow Model Registry dla deployment'u. Primary eval set: 200 par gold standard manualnie ranked z psychiatrycznej podgrupy ATC N05/N06; secondary eval set: 1800 par cross-register dla RQ5; tertiary: ~1500-2000 par LLM-generated dla hyperparameter tuning.

Wartości liczbowe (best hyperparams z Optuny, kappa values dla judge'a, accuracy@10 dla cross-register) zostaną wprowadzone po realizacji Iteracji 2 (cykl 1 + ablacje A1-A4 + judge final winner pick) i Iteracji 3 (cykle 2 + 3 + plateau analysis).

**Multi-turn chat handling — poza scope niniejszego rozdziału.** Inference-time multi-turn conversation handling jest implementowany przez warstwę RAG (LlamaIndex `ChatEngine` z built-in conversation memory — rephrase follow-up jako standalone query przed retrieval) i nie wymaga modyfikacji rerankera ani judge'a opisywanych w R6. Formalna ewaluacja multi-turn coherence jest *out of scope* tej pracy per `02b_konspekt_v3_updates.md` § II.13.10 (decyzja 16.05.2026 — implicit chat IN scope via LlamaIndex, formalne metryki conversation coherence dopisane do future work).

---

## Bibliografia (placeholder)

> **Status:** ~16 pozycji. Pozycje z `🟡 Verify via citation-checker` wymagają programatycznej weryfikacji DOI/inicjałów/roku przed final submission. Spójność z R2 (sekcja 2.X — *Pretrenowane modele PL*, *LLM-as-judge methodology*, *Hard negative mining*, *MLOps continuous training*, *Statistical methodology*) — patrz `R2_literatura.md`.

[1] Chen J., Xiao S., Zhang P., Luo K., Lian D., Liu Z. (2024). *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*. arXiv:2402.03216. 🟡 Verify via citation-checker.

[2] Dadas S. (2023). *Polish Reranker RoBERTa v3*. HuggingFace Hub: `sdadas/polish-reranker-roberta-v3`. 🟡 Verify exact citation format (model card vs paper) via citation-checker.

[3] Ociepa K., Flis Ł., Kinas P., Wróbel K., Gwoździej A. i in. (2025). *Bielik 11B v3 Technical Report*. SpeakLeash. 🟡 Verify exact author list + venue via citation-checker (poprawione 2026-05-16 — wcześniej phantom authors per R1 [13] verified).

[4] Zhang X., Thakur N., Ogundepo O., Kamalloo E., Alfonso-Hermelo D., Li X., Liu Q., Rezagholizadeh M., Lin J. (2023). *MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages*. TACL. 🟡 Verify via citation-checker.

[5] Peng B., Quesnelle J., Fan H., Shippole E. (2023). *YaRN: Efficient Context Window Extension of Large Language Models*. arXiv:2309.00071. 🟡 Verify via citation-checker.

[6] Reimers N., Gurevych I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP 2019. 🟡 Verify via citation-checker.

[7] Zheng L., Chiang W.-L., Sheng Y. i in. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. NeurIPS 2023 Datasets and Benchmarks. 🟡 Verify exact venue via citation-checker.

[8] Karpukhin V., Oguz B., Min S., Lewis P., Wu L., Edunov S., Chen D., Yih W. (2020). *Dense Passage Retrieval for Open-Domain Question Answering*. EMNLP 2020.

[9] Akiba T., Sano S., Yanase T., Ohta T., Koyama M. (2019). *Optuna: A Next-generation Hyperparameter Optimization Framework*. KDD 2019.

[10] Loshchilov I., Hutter F. (2019). *Decoupled Weight Decay Regularization (AdamW)*. ICLR 2019. 🟡 Verify via citation-checker.

[11] Mosbach M., Andriushchenko M., Klakow D. (2021). *On the Stability of Fine-tuning BERT: Misconceptions, Explanations, and Strong Baselines*. ICLR 2021. 🟡 Verify via citation-checker.

[12] Lin J., Ma X., Lin S.-C., Yang J.-H., Pradeep R., Nogueira R. (2021). *Pyserini: A Python Toolkit for Reproducible Information Retrieval Research with Sparse and Dense Representations*. SIGIR 2021. 🟡 Verify via citation-checker.

[13] Landis J.R., Koch G.G. (1977). *The Measurement of Observer Agreement for Categorical Data*. Biometrics 33(1):159-174.

[14] Cantor A.B. (1996). *Sample-size calculations for Cohen's kappa*. Psychological Methods 1(2):150-153. 🟡 Verify via citation-checker.

[15] Efron B., Tibshirani R.J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall/CRC Monographs on Statistics and Applied Probability 57.

[16] Järvelin K., Kekäläinen J. (2002). *Cumulated Gain-based Evaluation of IR Techniques*. ACM Transactions on Information Systems 20(4):422-446.

[17] Voorhees E.M. (1999). *The TREC-8 Question Answering Track Report*. TREC-8 Proceedings. 🟡 Verify via citation-checker.

[18] Cohen J. (1960). *A Coefficient of Agreement for Nominal Scales*. Educational and Psychological Measurement 20(1):37-46.

[19] Es S., James J., Espinosa-Anke L., Schockaert S. (2024). *RAGAS: Automated Evaluation of Retrieval Augmented Generation*. EACL 2024 (Demo Track). 🟡 Verify exact venue (EACL 2024 Demo vs main) via citation-checker.

---

> **Co dalej w tym rozdziale:**
>
> 1. **Iteracja 0b** (judge pilot): zaktualizować Tabelę 6.5 (Stage 1 pilot kappa) o wyniki ranking 4 kandydatów na n=30.
> 2. **Iteracja 2** (cykl 1 + A1-A4): wypełnić Tabelę 6.3 (best hyperparams cykl 1), Tabelę 6.5 (Stage 2 final kappa winner), Tabelę 6.6 (ablations results — przeniesienie do R7 sekcji 7.X). Final winner pick dla `<judge_model>`.
> 3. **Iteracja 3** (cykle 2-3 + plateau): wypełnić kolumny "Best (cycle 2)" i "Best (cycle 3)" w Tabeli 6.3. Rozwinięcie sekcji 6.6.3 (RQ3 plateau analysis) z konkretnymi wynikami.
> 4. **Citation pass:** uruchomić `/citations R6_modele.md` po Iteracji 2 — 🟡 markery do weryfikacji.
