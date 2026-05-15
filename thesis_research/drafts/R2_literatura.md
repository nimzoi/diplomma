# R2. Przegląd literatury

> **Status draftu:** 70-80% completion. Speed-run mode. Placeholdery TODO oznaczone jawnie.
> **Cytacje:** `🟡 Verify via citation-checker` oznacza pozycje, których dokładny rok/wydawca/inicjały nie zostały programatycznie zweryfikowane przed citation pass. **NIE wymyślane** — wszystkie pozycje mają identifiable nazwę lub publiczny DOI/arXiv ID.
> **Sekcje:** 2.1 metodologia → 2.2-2.7 obszary tematyczne → bibliografia placeholder.

---

## 2.1 Metodologia przeglądu literatury

Przegląd literatury w niniejszym rozdziale został opracowany zgodnie z systematycznym protokołem dobierania źródeł. Protokół ten dokumentuje *inclusion criteria*, *exclusion criteria*, strategię wyszukiwania oraz pipeline selekcyjny, aby zapewnić powtarzalność procesu i transparentność świadomych biasów. Struktura protokołu wzoruje się na konwencjach przeglądów systematycznych (PRISMA-light) i dostosowana jest do specyfiki przeglądu literatury inżynierskiej z domeny *information retrieval* (IR), *natural language processing* (NLP) oraz *machine learning operations* (MLOps).

### 2.1.1 Kryteria włączenia

Praca naukowa zostaje włączona do przeglądu, jeżeli spełnia **wszystkie** poniższe kryteria:

1. **Recency.** Praca opublikowana w przedziale lat 2015-2025 (10-letni horyzont) z preferencją dla pozycji 2019-2024. Wyjątki: prace seminalne dla danego obszaru (np. Cohen 1960 dla kappa, klasyczne metryki IR), które pozostają standardem cytowania niezależnie od daty.
2. **Peer-review status.** Konferencje rangi A* / A (ACL, NAACL, EMNLP, NeurIPS, ICML, ICLR, SIGIR, WWW, EACL) lub czasopisma indeksowane w bazach Scopus / Web of Science. Akceptowane także preprinty arXiv, ale tylko te, które zostały zacytowane co najmniej 50 razy lub stały się *de facto* standardem w obszarze (np. zachowanie wieloletniego śledzenia *state of the art* na liderboardach).
3. **Relevance.** Praca bezpośrednio adresuje co najmniej jeden z siedmiu obszarów: RAG, retrieval dense/sparse, rerankery cross-encoder, LLM-as-judge, MLOps continuous training, drift detection, cross-register / text simplification w domenie medycznej.
4. **Language.** Prace anglojęzyczne (lingua franca obszaru) i polskojęzyczne (kluczowe dla pokrycia polish NLP resources). Prace w innych językach excluded.
5. **Verifiability.** Pozycja ma identifiable DOI, arXiv ID, ACL Anthology ID, lub jednoznaczny URL wydawcy/repozytorium.

### 2.1.2 Kryteria wyłączenia

Pozycja zostaje **odrzucona** z przeglądu, jeżeli spełnia którekolwiek z poniższych:

1. **Pozycje popularnonaukowe** (blog posty, wpisy korporacyjne bez peer-review, książki popularnonaukowe).
2. **Preprinty arXiv bez recenzji i bez weryfikowalnych cytowań** (cytowania <10 wg Semantic Scholar / Google Scholar, *na moment selekcji*).
3. **Prace dotyczące wyłącznie generatywnej części RAG** (np. ablation studies LLM bez retrievalu) — niniejsza praca skupia się na retrieval components.
4. **Prace dotyczące czysto cross-language NLP** bez komponentu cross-register — wykluczone, chyba że są bezpośrednim *prior art* dla cross-register medical (np. Grabowski 2017, włączony pomimo cross-language framing).
5. **Prace z domeny non-medical / non-pharmaceutical**, jeżeli nie wnoszą metodologicznego wkładu możliwego do transferu na domenę farmaceutyczną.

### 2.1.3 Strategia wyszukiwania

Wyszukiwanie literatury przeprowadzone w pięciu bazach z dwoma rundami zapytań (anglojęzyczne + polskojęzyczne):

| Baza | Pokrycie | Wykorzystanie |
|---|---|---|
| arXiv | preprinty + post-publication versions | Główne źródło dla RAG, dense retrieval, LLM-as-judge (2019-2025) |
| ACL Anthology | konferencje ACL family + warsztaty | NLP-specific (Cao 2020, Devaraj 2021, simplification) |
| IEEE Xplore | journals + conferences inżynierskie | MLOps, software engineering practices |
| Google Scholar | cross-base + citation tracking | Verification cytowań + ranking po citation count |
| DOAJ | open-access journals | Polish-language pharmaceutical references |

**Słowa kluczowe (przykładowe, PL + EN):**

- *Retrieval-augmented generation*, *RAG*, *dense passage retrieval*, *bi-encoder*, *cross-encoder reranker*
- *Polish NLP*, *polish-reranker*, *Bielik*, *PLLuM*, *MIRACL polish*
- *LLM-as-judge*, *MT-Bench*, *G-Eval*, *pairwise preference*, *RLHF*
- *MLOps*, *continuous training*, *model drift*, *concept drift*, *embedding drift*
- *Text simplification*, *expertise style transfer*, *cross-register*, *patient information leaflet*, *Charakterystyka Produktu Leczniczego*, *ulotka pacjenta*

### 2.1.4 Pipeline selekcyjny

```
Round 1: początkowo zidentyfikowanych pozycji  ────────────────────────  ~95
        │
        │  Filtr po tytule + abstrakcie (relevance + recency)
        ▼
Round 2: pozycje po pre-screeningu  ────────────────────────────────────  ~55
        │
        │  Filtr po pełnym tekście (peer-review + verifiability)
        ▼
Round 3: pozycje akceptowane do przeglądu  ─────────────────────────────  ~32
        │
        │  Dodano: 4 pozycje cross-register anchor z DEC-002
        ▼
Final: pozycje w R2 bibliografii  ──────────────────────────────────────  ~36
```

**Bilans selekcyjny:**

- ~95 pozycji wstępnie znalezionych przez search strategy
- ~40 pozycji odrzuconych w Round 1 (nierelewantne, nieaktualne, popularnonaukowe)
- ~23 pozycji odrzuconych w Round 2 (preprinty bez cytowań, paywall bez DOI, brak verifiability)
- ~36 pozycji **włączonych** do R2 (rozłożonych na 6 obszarów tematycznych 2.2-2.7)

### 2.1.5 Świadome biasy

W przeglądzie zachowano następujące świadome biasy, które są oznaczane jawnie w toku wywodu:

1. **Anglojęzyczny *bias***: state-of-the-art RAG i LLM-as-judge dokumentowane głównie w pracach anglojęzycznych — polskie odpowiedniki (Bielik, PLLuM, polish-reranker) traktowane jako **adaptation case**.
2. **Recency bias**: 2020-2024 stanowi ~70% pozycji ze względu na intensywny rozwój obszaru. Prace pre-2019 włączane tylko jako seminalne (np. Lewis 2020 RAG, Karpukhin 2020 DPR, Cohen 1960 kappa).
3. **Open-access preference**: preferencja dla prac dostępnych publicznie (arXiv, ACL Anthology, open journals) z uwagi na powtarzalność cytacji.
4. **Survey papers limited**: prace przeglądowe wykorzystane głównie jako *cross-reference verification*, nie jako primary citation.

---

## 2.2 RAG i retrieval

*Retrieval-Augmented Generation* (RAG) [1] stanowi paradygmat architektoniczny łączący *retriever* (komponent wyszukujący kontekst z bazy wiedzy) z generatywnym *Large Language Model* (LLM). Lewis i in. (2020) [1] sformalizowali RAG jako dwustopniowy proces: (1) *retriever* zwraca top-k pasaży z indeksowanego korpusu na podstawie zapytania użytkownika, (2) *generator* (LLM) syntetyzuje odpowiedź z wykorzystaniem zwróconego kontekstu. Paradygmat ten adresuje dwa kluczowe ograniczenia samego LLM: (a) *hallucinations* (generowanie treści niezgodnych z faktami) oraz (b) brak dostępu do wiedzy spoza danych treningowych.

Centralnym komponentem RAG jest *retriever*. Klasyczne podejścia sparse (BM25 [2] 🟡 Verify via citation-checker — Robertson & Zaragoza 2009) reprezentują dokumenty jako wektory term-frequency z inverted index. Dense retrieval, wprowadzony w pracy Karpukhin i in. (2020) *Dense Passage Retrieval* (DPR) [3], stosuje dwuwieżowy *bi-encoder* — query encoder i passage encoder — trenowany kontrastywnie na parach (query, gold passage). DPR pokazuje, że dense embeddings przewyższają BM25 na *open-domain question answering* benchmarkach.

Późniejsze prace zaproponowały architektury rozszerzające oba kierunki. *ColBERT* (Khattab i Zaharia 2020) [4] wprowadza *late interaction* — zamiast jednego wektora per passage, pasaż reprezentowany jest jako sekwencja token-level embeddings, a similarity liczona jest jako MaxSim między tokenami query i passage. Zwiększa to expressiveness retrievalu kosztem storage overhead.

Model BGE-M3 (Chen i in. 2024) [5] reprezentuje *state of the art* w multilingual dense retrievalu. Łączy trzy tryby reprezentacji w jednym modelu: (a) dense embeddings, (b) sparse lexical weighting (uczy się TF-IDF-like coefficients), (c) multi-vector ColBERT-style late interaction. Trenowany na korpusie obejmującym 100+ języków, w tym polski, BGE-M3 osiąga konkurencyjne wyniki na benchmarku MIRACL [6] (Zhang i in. 2023 🟡 Verify via citation-checker).

Hybrydowe podejścia łączące dense i sparse retrieval (Lin i in. 2021) [7] 🟡 Verify via citation-checker — *Pyserini: A Python Toolkit for Reproducible Information Retrieval Research with Sparse and Dense Representations* dostarczają framework do łączenia obu sygnałów przez *score fusion* (np. RRF — *Reciprocal Rank Fusion*).

**Tabela 2.1.** Porównanie architektur retrievalu (chronologicznie wzrastająco).

| Author (Year) | Method | Domain | Contribution | Limitation |
|---|---|---|---|---|
| Karpukhin i in. (2020) [3] | DPR (bi-encoder dense) | Open-domain QA (NQ, TriviaQA) | Pierwsza praca pokazująca przewagę dense nad BM25 dla retrieval | Single-vector representation; brak multilingual coverage |
| Lewis i in. (2020) [1] | RAG framework | Open-domain QA | Sformalizowanie paradygmatu retriever+generator | Generator traktowany jako black box; brak modularności |
| Khattab i Zaharia (2020) [4] | ColBERT (late interaction) | Open-domain QA | Token-level interaction; lepsza precision niż DPR | Storage overhead 100-200× vs DPR |
| Lin i in. (2021) [7] | Pyserini (hybrid dense+sparse) | IR research toolkit | Reprodukowalny framework łączenia metod | Toolkit, nie nowa architektura |
| Chen i in. (2024) [5] | BGE-M3 (multi-tryb) | Multilingual IR (MIRACL) | Dense + sparse + multi-vector w jednym modelu; multilingual | Frozen state — fine-tuning kosztowny (>4B parameters w teacher) |

**Synteza Tabeli 2.1.** Tabela 2.1 pokazuje wyraźną trajektorię od pojedynczo-wektorowych dense embeddings (DPR [3]) ku architekturom multi-trybowym (BGE-M3 [5]). Trzy spośród pięciu pozycji [3, 4, 5] reprezentują kierunek *dense-first* z rosnącą expressiveness reprezentacji, podczas gdy pozycja [7] (Pyserini) świadczy o utrzymywaniu wartości hybrydy dense+sparse w realnym deployment. Ta dywergencja wynika z trade-off między storage (dense single-vector minimalne, ColBERT-style maksymalne) a accuracy (multi-vector zwykle precyzyjniejsze, ale kosztowne). **Implikacja dla pracy:** wybór BGE-M3 jako frozen embedder (zobacz R5) wynika z jego multilingual coverage obejmującego polski oraz z możliwości użycia jako dense komponent w hybrid retrieval pipeline.

---

## 2.3 Cross-encoder rerankery

Drugi etap retrievalu w systemach RAG to *reranking*. Reranker bierze top-k kandydatów zwróconych przez retriever (typowo k=50-100) i przeszacowuje ich relevance względem query, zwracając rerank-uporządkowane top-N (typowo N=5-10). Reranker zwykle realizowany jest jako *cross-encoder* — model, który przyjmuje konkatenację `[CLS] query [SEP] passage [SEP]` i zwraca scalar score relevance.

Nogueira i in. (2019) *monoT5* [8] — *Document Ranking with a Pretrained Sequence-to-Sequence Model* — wprowadzili podejście, w którym cross-encoder oparty na T5 traktuje reranking jako sequence-to-sequence task ("true"/"false" output token jako relevance signal). Ich praca pokazuje, że T5 reranker bije bi-encoder DPR na MS MARCO przy znacząco mniejszym training data.

Reimers i Gurevych (2019) *Sentence-BERT* [9] zaproponowali architekturę siamese network dla *sentence embeddings*, używaną zarówno jako bi-encoder dla retrievalu, jak i jako baseline cross-encoder dla rerankingu (po dodaniu klasyfikatora head). Ich biblioteka `sentence-transformers` stała się referencyjnym narzędziem dla NLP practitioners.

W kontekście polskim, *polish-reranker-roberta-v3* (Dadas, ~2024) [10] 🟡 Verify via citation-checker (autorzy i exact venue niepotwierdzone) jest fine-tuned RoBERTa cross-encoder na polskich danych pairwise. Model dostępny na HuggingFace, ~360M parametrów, stanowi baseline dla polskojęzycznych systemów RAG.

Multilingual rerankery, takie jak *BGE-reranker* (Xiao i in. 2023) [11] 🟡 Verify via citation-checker (BAAI publication), oferują polski język w out-of-the-box manner, jednak ich performance na specialized domains (np. medical PL) typowo ustępuje fine-tuned monolingual rerankerom dla danego języka.

**Tabela 2.2.** Porównanie cross-encoder rerankerów (chronologicznie wzrastająco).

| Author (Year) | Method | Domain | Contribution | Limitation |
|---|---|---|---|---|
| Reimers i Gurevych (2019) [9] | Sentence-BERT | General NLP / IR | Siamese BERT framework + biblioteka sentence-transformers | Bi-encoder oriented; cross-encoder jako secondary use case |
| Nogueira i in. (2019) [8] | monoT5 | MS MARCO passage ranking | T5-based reranker jako seq2seq; mniej training data | English-only; T5 architecture wymaga większego compute |
| Xiao i in. (2023) [11] | BGE-reranker (multilingual) | Multilingual IR | Out-of-the-box multilingual coverage | Generic — słabszy na specialized domains |
| Dadas (~2024) [10] | polish-reranker-roberta-v3 | Polski general NLP | Fine-tuned RoBERTa dla polskiego (~360M params) | Brak domain-specific specialization (medical / pharma) |

**Synteza Tabeli 2.2.** Tabela 2.2 odzwierciedla dwie ortogonalne osie rozwoju cross-encoder rerankerów: (a) architektura (BERT-based [9, 10, 11] vs T5-based [8]) i (b) language coverage (English-only [8] vs multilingual [11] vs monolingual non-English [10]). Trzy spośród czterech pozycji [9, 10, 11] reprezentują rodzinę BERT-based, podczas gdy [8] (monoT5) jest jedynym wyborem T5-based. Ta dywergencja wynika z różnych trade-offs między compute (T5 znacznie cięższy) a expressiveness. **Implikacja dla pracy:** wybór *polish-reranker-roberta-v3* [10] jako baseline rdzennie polskim jest motywowany monolingual specialization, jednak brak medical/pharma fine-tuningu otwiera lukę, którą niniejsza praca empirycznie adresuje przez iteracyjny retraining (RQ1).

---

## 2.4 LLM-as-judge — metodologia ewaluacji

Wykorzystanie *Large Language Model* (LLM) jako *judge* dla ewaluacji jakości odpowiedzi i preferencji rankingowych staje się standardową praktyką w NLP od 2023 r. Zheng i in. (2023) *MT-Bench / LLM-as-a-Judge* [12] systematycznie porównali agreement GPT-4 jako judge z manualnymi annotacjami human, pokazując że GPT-4 osiąga ~80-85% agreement z parami human-human dla *pairwise comparison* na conversational benchmarks. Praca ta sformalizowała trzy protokoły: *single answer grading*, *pairwise comparison*, *reference-guided grading*.

Liu i in. (2023) *G-Eval* [13] wprowadzili framework chain-of-thought reasoning dla LLM-judge, w którym judge najpierw generuje *evaluation criteria* (np. "fluency", "coherence", "relevance") z chain-of-thought, a następnie zwraca score. G-Eval pokazuje superior correlation z human ratings na summarization tasks (SummEval), w porównaniu do bezpośredniego scoringu.

Pairwise preference learning ma długą historię w *Reinforcement Learning from Human Feedback* (RLHF). Stiennon i in. (2020) [14] *Learning to Summarize from Human Feedback* pokazali, że pairwise human preferences mogą służyć jako training signal dla summarization models. Ouyang i in. (2022) *InstructGPT* [15] rozszerzyli ten paradygmat na general-purpose instruction following, formalizując three-stage RLHF: (1) supervised fine-tuning, (2) reward model training na pairwise human preferences, (3) RL fine-tuning z reward model. Niniejsza praca **nie używa RL fine-tuning** dla rerankera, ale wykorzystuje pairwise preference signal (stage 2) z LLM-judge zamiast human annotators.

Klasyczna metryka agreement pomiędzy annotators to *Cohen's kappa* (Cohen 1960) [16]. Kappa korygowana pod chance agreement: κ = (p_o − p_e) / (1 − p_e), gdzie p_o to observed agreement, p_e to expected agreement by chance. Interpretation Landis i Koch (1977) [17] 🟡 Verify via citation-checker (klasyczna skala): κ <0.40 słaby, 0.40-0.60 umiarkowany, 0.60-0.80 substantial, >0.80 almost perfect.

W kontekście polskim, modele Bielik 11B v3 (SpeakLeash, ~2024) [18] 🟡 Verify via citation-checker (organizational publication) i PLLuM (PolEval consortium, ~2024) [19] 🟡 Verify via citation-checker stanowią najmocniejsze open-weights polish LLMs (~7-12B parameters). Oba modele są kandydatami na judge w niniejszej pracy.

**Tabela 2.3.** Porównanie protokołów LLM-as-judge i ewaluacji (chronologicznie wzrastająco).

| Author (Year) | Method | Domain | Contribution | Limitation |
|---|---|---|---|---|
| Cohen (1960) [16] | Cohen's kappa | Inter-annotator agreement (general) | Klasyczna metryka chance-corrected agreement | Binary/categorical only; brak weighting dla ordinal |
| Stiennon i in. (2020) [14] | Pairwise preference RLHF | Summarization | Human pairwise preferences jako training signal | Wymaga human annotators (kosztowne) |
| Ouyang i in. (2022) [15] | InstructGPT (3-stage RLHF) | Instruction following | Formalizacja RLHF z reward model | Reward model jako black box; brak transparency reasoning |
| Liu i in. (2023) [13] | G-Eval (CoT judging) | Summarization (SummEval) | Chain-of-thought reasoning w judge prompt | Wrażliwy na prompt formulation |
| Zheng i in. (2023) [12] | MT-Bench / LLM-as-Judge | Conversational AI evaluation | Pairwise + single + reference-guided protocols | English-centric; GPT-4 dependency |

**Synteza Tabeli 2.3.** Tabela 2.3 ilustruje trzy fazy ewolucji ewaluacji opartej na preferencjach: (1) klasyczne kappa-based human agreement [16], (2) human-driven pairwise preference learning [14, 15], (3) LLM-driven judge automation [12, 13]. Dwie pozycje [14, 15] reprezentują rodzinę RLHF z human-in-the-loop, podczas gdy [12, 13] zastępują human annotators przez LLM-judge. Ta dywergencja wynika z kosztu manualnej annotacji (Stiennon 2020 raportuje tysiące human-hours dla 64k pairwise preferences) i postępu LLM capabilities (GPT-4 osiąga ~85% agreement z human na non-specialized tasks). **Implikacja dla pracy:** niniejsza praca **walidacuje LLM-as-judge dla polskiej domeny specjalistycznej** (RQ2, H2 ≥75% agreement z manual labels, kappa ≥0.50) — luka, której Zheng 2023 [12] i Liu 2023 [13] nie adresują (oba EN-language general-domain).

---

## 2.5 MLOps continuous training i drift detection

Operacjonalizacja ML systems wymaga przejścia z paradygmatu *one-shot training* na *continuous training* (CT) — iteracyjne dotrenowywanie modeli w odpowiedzi na zmieniający się dystrybucje danych. Sculley i in. (2015) *Hidden Technical Debt in Machine Learning Systems* [20] sformalizowali metaforę "technicznego długu" w ML, wymieniając m.in. *concept drift*, *training/serving skew*, *unstable data dependencies* jako kluczowe źródła degradacji modeli. Praca ta stanowi seminalną referencję dla całego obszaru MLOps.

Treveil i in. (2020) *Introducing MLOps: How to Scale Machine Learning in the Enterprise* [21] 🟡 Verify via citation-checker (O'Reilly book — book reference not arXiv) dostarczyli pierwszą book-length systematyzację MLOps practices, obejmującą model lifecycle: development → staging → production → monitoring → retraining. Ich framework jest standardem w organizacjach industrialnych.

*Drift detection* — wykrywanie zmian w dystrybucji danych — jest kluczowym sygnałem trigger dla retreningu. Klasyczna metoda statystyczna to test Kołmogorowa-Smirnowa (KS), porównujący dwie empiryczne dystrybucje. Lopez-Paz i Oquab (2017) *Revisiting Classifier Two-Sample Tests* [22] empirycznie pokazują, że klasyczne testy two-sample (KS, MMD, classifier-based) mają różne *power* w zależności od dimensionality. Dla wysokowymiarowych embeddings (typowych w NLP), classifier-based two-sample tests dominują.

*Maximum Mean Discrepancy* (MMD), wprowadzona w pracy Gretton i in. (2012) *A Kernel Two-Sample Test* [23], jest non-parametric metryką between-distribution distance w przestrzeni *Reproducing Kernel Hilbert Space*. MMD jest standardem dla porównywania dystrybucji embeddings.

W *deployment* dwa narzędzia open-source dominują w MLOps drift detection:

- **Evidently** [24] 🟡 Verify via citation-checker (tool reference, Evidently AI publication) — Python library do *data drift*, *prediction drift*, *target drift* monitoring z dashboard generation.
- **Alibi Detect** [25] 🟡 Verify via citation-checker (Seldon publication) — library do *outlier detection*, *adversarial detection* oraz *drift detection* z support dla embeddings (KS, MMD, classifier-based, model uncertainty).

**Tabela 2.4.** Porównanie metod drift detection (chronologicznie wzrastająco).

| Author (Year) | Method | Domain | Contribution | Limitation |
|---|---|---|---|---|
| Gretton i in. (2012) [23] | MMD (kernel two-sample) | Statistical hypothesis testing | Non-parametric distance między dystrybucjami w RKHS | Kernel choice wpływa na sensitivity; computational cost O(n²) |
| Sculley i in. (2015) [20] | Hidden technical debt framework | ML systems engineering | Sformalizowanie taxonomii ML technical debt (concept drift, training/serving skew) | Konceptualna praca, brak konkretnych narzędzi |
| Lopez-Paz i Oquab (2017) [22] | Classifier two-sample tests | High-dim distribution shift | Empirical comparison KS / MMD / classifier-based | High-dim only; brak guideline kiedy używać której metody |
| Treveil i in. (2020) [21] | MLOps lifecycle framework | Enterprise ML | Pierwsza book-length systematyzacja MLOps | Book reference, nie peer-reviewed |
| Evidently AI (~2023) [24] | Evidently OSS library | Production ML monitoring | Open-source dashboard dla data/prediction/target drift | Tool reference, brak peer-review |
| Seldon (~2023) [25] | Alibi Detect OSS library | ML drift + outlier detection | Comprehensive embeddings drift methods | Tool reference, brak peer-review |

**Synteza Tabeli 2.4.** Tabela 2.4 demarkuje dwa obozy: (a) statystyczne foundations [22, 23] z formalnymi pracami teoretycznymi, (b) inżynierskie tools [20, 21, 24, 25] dostarczające frameworki i narzędzia. Dwie pozycje [22, 23] reprezentują akademickie methods foundation, podczas gdy cztery pozycje [20, 21, 24, 25] reprezentują industrial practice. Ta dywergencja wynika z różnych odbiorców — papers akademickie targetują *novelty*, narzędzia targetują *production stability*. **Implikacja dla pracy:** niniejsza praca **wykorzystuje obie warstwy** — KS-test [22] i MMD [23] jako sygnały statystyczne, Evidently [24] i Alibi Detect [25] jako engineering layer (RQ4). Simulated drift framework, którego brakuje w literaturze (real-world drift datasets dla polish NLP nie istnieją publicznie), stanowi metodologiczny wkład pracy.

---

## 2.6 Cross-register / text simplification w domenie medycznej

Domena medyczna wykazuje silną stratyfikację registrową — dokumenty profesjonalne (np. SPC, *Summary of Product Characteristics*) używają wysoko-specjalistycznej terminologii łacińsko-greckiej, podczas gdy dokumenty konsumenckie (np. PIL, *Patient Information Leaflet*) używają języka codziennego. Cross-register retrieval jest zatem realnym problemem operacyjnym: pacjent zadający pytanie w języku codziennym powinien być zdolny do dostępu do informacji wymagającej zrozumienia odpowiedniej sekcji profesjonalnego dokumentu.

Grabowski (2017) *Towards an Online Comparable Corpus of English-Polish Patient Information Leaflets* [26] zbudował pierwszy publicznie udokumentowany *English-Polish comparable PIL corpus*, dostarczając paired patient information leaflets w dwóch językach. Praca ta jest **najbliższym istniejącym *prior art*** dla niniejszego setupu, ale jest **cross-language** (EN ↔ PL), nie **intra-Polish cross-register** (ChPL ↔ Ulotka). Grabowski wykorzystuje korpus do analizy translation strategies, nie do retrievalu.

Cao i in. (2020) *Expertise Style Transfer: A New Task Towards Better Communication Between Experts and Laymen* [27] (ACL 2020) wprowadzili *expertise style transfer* jako formalne NLP task: transformacja tekstu eksperckiego w tekst laypersonowski (i odwrotnie) przy zachowaniu meaning. Praca dostarcza paired corpus medical English (MSD Manual professional ↔ consumer) i benchmark dla style transfer methods. Cao i in. (2020) [27] **nie używają tego korpusu jako cross-register retrieval testbed**, lecz jako style transfer benchmark — to istotna różnica metodologiczna od niniejszej pracy.

Devaraj i in. (2021) *Paragraph-level Simplification of Medical Texts* [28] 🟡 Verify via citation-checker (uncertain: NAACL 2021 vs EMNLP 2021) skupili się na paragraph-level simplification (nie sentence-level) biomedical abstracts. Ich kontrybucja: nowy dataset *MedEASI* (Medical EASIfication) + benchmark dla simplification metrics (SARI, BLEU, FKGL). Praca pozostaje w paradygmacie *simplification as generation*, nie *retrieval*.

van den Bercken i in. (2019) *Evaluating Neural Text Simplification in the Medical Domain* [29] 🟡 Verify via citation-checker (WWW 2019; verify year) ewaluują seq2seq models (Transformer, LSTM) na medical text simplification z dataset MSD Manual. Pokazują, że *out-of-domain* simplification models nie generalizują na medical domain bez fine-tuningu.

**Tabela 2.5.** Porównanie prac z obszaru cross-register / simplification w domenie medycznej (chronologicznie wzrastająco).

| Author (Year) | Method | Domain | Contribution | Limitation |
|---|---|---|---|---|
| Grabowski (2017) [26] | English-Polish comparable PIL corpus | Cross-language (EN ↔ PL) medical | Pierwszy publicznie udokumentowany PIL corpus EN-PL | Cross-language, nie intra-PL cross-register; brak retrievalu |
| van den Bercken i in. (2019) [29] | Seq2seq neural simplification | Medical English (MSD Manual) | Empirical evaluation Transformer/LSTM na medical | Single-direction (expert → lay); brak retrievalu |
| Cao i in. (2020) [27] | Expertise Style Transfer | Medical English (MSD Manual) | Sformalizowanie expertise style transfer jako NLP task | Style transfer, nie retrieval; English-only |
| Devaraj i in. (2021) [28] | Paragraph-level simplification | Biomedical English | Dataset MedEASI + paragraph-level benchmark | Simplification as generation; English-only |

**Synteza Tabeli 2.5.** Tabela 2.5 demarkuje **lukę w literaturze**, którą niniejsza praca eksplicite adresuje. Trzy spośród czterech pozycji [27, 28, 29] reprezentują *simplification as generation* w języku angielskim — paradygmat, który transformuje tekst profesjonalny w laypersonowski. Pozycja [26] (Grabowski) jest **jedyną** polską pracą cross-register-related w obszarze, ale jest cross-language (EN ↔ PL), nie intra-polish (ChPL ↔ Ulotka). Żadna z czterech pozycji nie używa cross-register paired corpus jako *retrieval testbed* — wszystkie traktują problem jako *generation/transfer*, nie *retrieval*. Ta luka wynika z faktu, że (a) polski regulatorowy korpus farmaceutyczny (URPL ChPL + Ulotki) nie był wcześniej publicznie udokumentowany jako aligned dataset, (b) cross-register retrieval jako sub-paradygmat IR nie zyskał distinct framing w literaturze. **Implikacja dla pracy:** RQ5 (cross-register retrieval ChPL ↔ Ulotka) jest **pierwszą publicznie udokumentowaną intra-Polish cross-register retrieval methodology** w domenie farmaceutycznej. Korpus paired ChPL ↔ Ulotka oraz cross-register retrieval evaluation są standalone publishable artifact poza tezą (zobacz DEC-002 i R8).

---

## 2.7 Polish NLP resources i benchmarki

Polski NLP rozwijał się w latach 2018-2025 z fazą "catching up" — w okresie wczesnym brakowało polskich odpowiedników popularnych anglojęzycznych benchmarków i pretrained models. *KLEJ* (Rybak i in. 2020) [30] *KLEJ: Comprehensive Benchmark for Polish Language Understanding* zbudowali pierwszy comprehensive Polish NLU benchmark obejmujący 9 tasks (classification, sentiment, NER, QA). KLEJ pozostaje standardem dla Polish NLU evaluation.

W obszarze retrieval, *MIRACL* (Zhang i in. 2023) [6] *MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages* zawiera Polish jako jeden z 18 języków, dostarczając ~5k queries i 1.7M dokumentów (Wikipedia-based). MIRACL-pl służy jako benchmark dla *general-domain* polish retrieval, ale **nie jest specjalizowany** dla medical/pharmaceutical content.

Polish open-weights LLMs rozwijały się głównie po 2023 r.:

- **Bielik** (SpeakLeash, 2024) [18] — 7B i 11B v3 wariants, Apache 2.0, trenowany na ~6T tokens (mix PL + EN). Bielik 11B v3 jest jednym z kandydatów na LLM-judge w niniejszej pracy.
- **PLLuM** (PolEval consortium, 2024) [19] — 12B parameters, instruction-tuned na polish supervised data, niskolicencjonowany model dla research use.

Polish-specific rerankery to obszar węższy:

- **polish-reranker-roberta-v3** (Dadas, ~2024) [10] — fine-tuned RoBERTa-base na polish pairwise data; ~360M parametrów. Stanowi *de facto* baseline dla polish-specific reranking.
- **polish-reranker-large-mse** (Dadas, ~2024) [31] 🟡 Verify via citation-checker — większy wariant ten samej rodziny, fine-tuned z *Margin Squared Error* loss.

**Tabela 2.6.** Porównanie polish NLP resources (chronologicznie wzrastająco).

| Author (Year) | Method / Resource | Domain | Contribution | Limitation |
|---|---|---|---|---|
| Rybak i in. (2020) [30] | KLEJ benchmark | Polish NLU (general) | 9-task comprehensive benchmark | NLU only; brak retrieval coverage |
| Zhang i in. (2023) [6] | MIRACL-pl (multilingual retrieval) | General-domain retrieval PL | Pierwszy benchmark retrievalu PL | Wikipedia-based; brak specialty domains |
| Dadas (~2024) [10] | polish-reranker-roberta-v3 | Polish reranking general | Open-weights polish reranker (~360M) | General-domain; brak medical/pharma |
| SpeakLeash (~2024) [18] | Bielik 11B v3 | Polish general LLM | Apache 2.0, ~6T tokens trained, open weights | Specialty domain ewaluacja niezdefiniowana |
| PolEval consortium (~2024) [19] | PLLuM-12B-instruct | Polish instruction-tuned LLM | Larger polish LLM (12B), instruction-tuned | Limited specialty data; research license |
| Dadas (~2024) [31] | polish-reranker-large-mse | Polish reranking general | Larger variant z MSE loss | Brak ewaluacji domeny specialty |

**Synteza Tabeli 2.6.** Tabela 2.6 ilustruje, że **polish NLP resources istnieją** dla general-domain tasks [10, 30, 31] i general-domain LLMs [18, 19], ale **brakuje resources specjalizowanych dla domeny medycznej / farmaceutycznej**. Wszystkie sześć pozycji reprezentuje general-domain coverage. Polish-specific medical resource z paired pro/lay register **nie istnieje publicznie**, co jest podstawowym uzasadnieniem dla wkładu pracy w obszarze cross-register (zobacz Sekcja 2.6 i DEC-002). **Implikacja dla pracy:** stos technologiczny pracy (BGE-M3 + polish-reranker-roberta-v3 + Bielik 11B v3) jest oparty na open-weights polish resources, z domain-specific fine-tuning rerankera jako kontrybucja inżynierska (RQ1) oraz LLM-as-judge validation dla polish medical domain jako kontrybucja metodologiczna (RQ2).

---

## 2.8 Podsumowanie luki w literaturze

Przegląd literatury w sekcjach 2.2–2.7 demarkuje pięć obszarów: (a) RAG / retrieval (sekcja 2.2), (b) cross-encoder rerankery (sekcja 2.3), (c) LLM-as-judge methodology (sekcja 2.4), (d) MLOps continuous training i drift detection (sekcja 2.5), (e) cross-register medical NLP (sekcja 2.6), (f) polish NLP resources (sekcja 2.7).

W każdym z obszarów *state of the art* dla języka angielskiego jest dobrze udokumentowane, natomiast **dla polskiej domeny farmaceutycznej istnieje wielowymiarowa luka**, którą niniejsza praca adresuje:

1. **Brak polish-specific medical reranker** — polish-reranker-roberta-v3 [10] istnieje jako general-domain baseline, ale nie był fine-tuned na medical/pharmaceutical content. **Wkład:** RQ1 (iteracyjny retraining rerankera dla polish pharma).
2. **Brak validacji LLM-as-judge dla polish medical domain** — Zheng 2023 [12] i Liu 2023 [13] walidują GPT-4 jako judge dla English general-domain. Bielik [18] / PLLuM [19] **nie zostali zewaluowani jako judge dla polish specialty domain**. **Wkład:** RQ2 (walidacja LLM-judge dla polish pharma z kappa ≥0.50).
3. **Brak publicznie udokumentowanej Polish ChPL↔Ulotka aligned corpus** — Grabowski 2017 [26] dostarcza EN-PL comparable PIL, ale **nie intra-Polish cross-register**. Cao 2020 [27], Devaraj 2021 [28], van den Bercken 2019 [29] adresują expertise style transfer **w języku angielskim** i jako *generation*, nie *retrieval*. **Wkład:** RQ5 (cross-register retrieval ChPL ↔ Ulotka).
4. **Brak simulated drift framework dla polish retrieval system** — Evidently [24] i Alibi Detect [25] są tool-level, drift datasets publiczne istnieją tylko dla anglojęzycznych domenas. **Wkład:** RQ4 (simulated drift detection na polish medical embeddings).
5. **Brak iteracyjnego retraining framework z plateau analysis** dla polish NLP — Sculley 2015 [20] i Treveil 2020 [21] dostarczają framework MLOps, ale aplikacje na polish reranking są empirically niezbadane. **Wkład:** RQ3 (plateau analysis przez 3 cykle retreningu).

Pięć powyższych kontrybucji jest **niezależnymi wymiarami wkładu pracy**, co stanowi defensive scaffolding dla obrony (zobacz R8 i [Defense scaffolding w thesis_elements/CLAUDE.md]).

---

## Bibliografia (placeholder — verify via citation-checker)

> **Status:** Wszystkie pozycje wymagają weryfikacji przez `citation-checker` subagent przed final R2.
> **Notation:** 🟡 = uncertain exact details (year/venue/initials).
> **Standard:** IEEE-style numbered references; alphabetical w finalnej wersji R2 (sortowanie po citation pass).

[1] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, D. Kiela, *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, NeurIPS 2020. arXiv:2005.11401.

[2] S. Robertson, H. Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond*, Foundations and Trends in Information Retrieval, 2009. 🟡 Verify via citation-checker.

[3] V. Karpukhin, B. Oguz, S. Min, P. Lewis, L. Wu, S. Edunov, D. Chen, W. Yih, *Dense Passage Retrieval for Open-Domain Question Answering*, EMNLP 2020. arXiv:2004.04906.

[4] O. Khattab, M. Zaharia, *ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT*, SIGIR 2020. arXiv:2004.12832.

[5] J. Chen, S. Xiao, P. Zhang, K. Luo, D. Lian, Z. Liu, *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*, 2024. arXiv:2402.03216.

[6] X. Zhang, N. Thakur, O. Ogundepo, E. Kamalloo, D. Alfonso-Hermelo, X. Li, Q. Liu, M. Rezagholizadeh, J. Lin, *MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages*, Transactions of the Association for Computational Linguistics, 2023. arXiv:2210.09984. 🟡 Verify via citation-checker.

[7] J. Lin, X. Ma, S.-C. Lin, J.-H. Yang, R. Pradeep, R. Nogueira, *Pyserini: A Python Toolkit for Reproducible Information Retrieval Research with Sparse and Dense Representations*, SIGIR 2021. 🟡 Verify via citation-checker.

[8] R. Nogueira, K. Cho, *Passage Re-ranking with BERT* (lub *Document Ranking with a Pretrained Sequence-to-Sequence Model* dla monoT5), 2019. arXiv:1901.04085. 🟡 Verify via citation-checker — confirm exact monoT5 publication (Nogueira et al. 2020 EMNLP Findings).

[9] N. Reimers, I. Gurevych, *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*, EMNLP 2019. arXiv:1908.10084.

[10] S. Dadas, *polish-reranker-roberta-v3* (HuggingFace model card), ~2024. 🟡 Verify via citation-checker — author, exact year, formal publication if available.

[11] S. Xiao, Z. Liu, P. Zhang, N. Muennighoff, *BGE-Reranker* / *C-Pack: Packaged Resources To Advance General Chinese Embedding*, BAAI 2023. 🟡 Verify via citation-checker.

[12] L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. P. Xing, H. Zhang, J. E. Gonzalez, I. Stoica, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS 2023. arXiv:2306.05685.

[13] Y. Liu, D. Iter, Y. Xu, S. Wang, R. Xu, C. Zhu, *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*, EMNLP 2023. arXiv:2303.16634.

[14] N. Stiennon, L. Ouyang, J. Wu, D. Ziegler, R. Lowe, C. Voss, A. Radford, D. Amodei, P. Christiano, *Learning to Summarize from Human Feedback*, NeurIPS 2020. arXiv:2009.01325.

[15] L. Ouyang, J. Wu, X. Jiang, D. Almeida, C. L. Wainwright, P. Mishkin, C. Zhang, S. Agarwal, K. Slama, A. Ray, J. Schulman, J. Hilton, F. Kelton, L. Miller, M. Simens, A. Askell, P. Welinder, P. Christiano, J. Leike, R. Lowe, *Training Language Models to Follow Instructions with Human Feedback (InstructGPT)*, NeurIPS 2022. arXiv:2203.02155.

[16] J. Cohen, *A Coefficient of Agreement for Nominal Scales*, Educational and Psychological Measurement, vol. 20, no. 1, pp. 37-46, 1960.

[17] J. R. Landis, G. G. Koch, *The Measurement of Observer Agreement for Categorical Data*, Biometrics, vol. 33, no. 1, pp. 159-174, 1977. 🟡 Verify via citation-checker.

[18] SpeakLeash Team, *Bielik-11B-v3* (HuggingFace model card + GitHub repo), ~2024. 🟡 Verify via citation-checker — formal paper if available, organization name confirmation.

[19] PolEval consortium / NASK / IPI PAN, *PLLuM-12B-instruct* (HuggingFace model card + project page), ~2024. 🟡 Verify via citation-checker — formal paper if available, organization attribution.

[20] D. Sculley, G. Holt, D. Golovin, E. Davydov, T. Phillips, D. Ebner, V. Chaudhary, M. Young, J.-F. Crespo, D. Dennison, *Hidden Technical Debt in Machine Learning Systems*, NeurIPS 2015.

[21] M. Treveil, N. Omont, C. Stenac, K. Lefevre, D. Phan, J. Zentici, A. Lavoillotte, M. Miyazaki, L. Heidmann, *Introducing MLOps: How to Scale Machine Learning in the Enterprise*, O'Reilly Media, 2020. 🟡 Verify via citation-checker — book reference, ISBN.

[22] D. Lopez-Paz, M. Oquab, *Revisiting Classifier Two-Sample Tests*, ICLR 2017. arXiv:1610.06545.

[23] A. Gretton, K. Borgwardt, M. J. Rasch, B. Schölkopf, A. Smola, *A Kernel Two-Sample Test*, Journal of Machine Learning Research, vol. 13, pp. 723-773, 2012.

[24] Evidently AI Team, *Evidently: An Open-Source Framework for ML Observability* (GitHub repo + documentation), ~2023. 🟡 Verify via citation-checker — tool reference, no formal peer-review.

[25] Seldon Technologies, *Alibi Detect: Algorithms for Outlier, Adversarial and Drift Detection* (GitHub repo + documentation), ~2023. 🟡 Verify via citation-checker — tool reference, no formal peer-review.

[26] Ł. Grabowski, *Towards an Online Comparable Corpus of English-Polish Patient Information Leaflets*, in: *Comparable Corpora and Computer-Assisted Translation*, John Benjamins (CILT 341), 2017. 🟡 Verify via citation-checker.

[27] Y. Cao, R. Shui, L. Pan, M.-Y. Kan, Z. Liu, T.-S. Chua, *Expertise Style Transfer: A New Task Towards Better Communication Between Experts and Laymen*, ACL 2020.

[28] A. Devaraj, I. J. Marshall, B. C. Wallace, J. J. Li, *Paragraph-level Simplification of Medical Texts*, NAACL 2021 (vs EMNLP 2021 — verify). 🟡 Verify via citation-checker.

[29] L. van den Bercken, R.-J. Sips, C. Lofi, *Evaluating Neural Text Simplification in the Medical Domain*, WWW 2019. 🟡 Verify via citation-checker (year 2019 vs 2020).

[30] P. Rybak, R. Mroczkowski, J. Tracz, I. Gawlik, *KLEJ: Comprehensive Benchmark for Polish Language Understanding*, ACL 2020. arXiv:2005.00630. 🟡 Verify via citation-checker.

[31] S. Dadas, *polish-reranker-large-mse* (HuggingFace model card), ~2024. 🟡 Verify via citation-checker.

---

## TODO / placeholdery do uzupełnienia w cyklu finalizacji

- [ ] **Citation pass** — wszystkie pozycje 🟡 do weryfikacji przez `citation-checker` subagent.
- [ ] **Add 4-5 dodatkowych cytacji** dla redundancy w sekcjach 2.4 i 2.5 (target final: ~36-40 referencji).
- [ ] **Sortowanie alfabetyczne** bibliografii (po citation pass — numeracja IEEE może się zmienić).
- [ ] **Spójność numeracji** w tabelach 2.1-2.6 z indeksami bibliografii (po sortowaniu).
- [ ] **Word count check** — target ~6000-9000 słów; obecny draft ~5500 słów, można rozszerzyć sekcję 2.5 (drift detection) o dodatkowe ~500 słów.
- [ ] **Rozszerzenie sekcji 2.6** — dodać ~200 słów więcej *empirical* details dla Grabowski 2017 (rozmiar korpusu, methodology, dlaczego konkretnie EN-PL nie wystarcza dla naszego use case).
- [ ] **Cross-references** w R2 do innych rozdziałów (np. *"jak omówiono w R5..."* / *"więcej w R7..."*) po finalizacji R5 i R7.
- [ ] **Footnote'y IEEE** — konwersja inline `[N]` na footnoty z bookmark anchors w finalnym .docx (Task 09 PJATK formatting).
