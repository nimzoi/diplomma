# Rozdział 1. Wprowadzenie

> **Status draftu:** v0.1 (2026-05-15) — markdown source dla `thesis_elements/R01_wprowadzenie.docx`.
> **Cel długościowy:** 1000–1500 słów (5–8 stron PJATK).
> **Format docelowy:** PJATK — TNR 12pt, line 1.5, marginesy 2.5cm, footnotes IEEE 10pt. Cytacje `[N]` w markdownie konwertowane do footnotes po skopiowaniu do Worda.
> **Notki dla autorki:** Cytacje oznaczone 🟡 — do weryfikacji przez `citation-checker` przed final submission. Sekcje numerowane 1.1–1.6 zgodnie z klasycznym układem intro.

---

## 1.1. Tło i kontekst

Generatywne modele językowe operują na statycznej, parametrycznej pamięci zamrożonej w momencie pretreningu. Paradygmat *Retrieval-Augmented Generation* (RAG), wprowadzony przez Lewisa i in. [1], adresuje to ograniczenie poprzez dynamiczne łączenie modelu generatywnego z zewnętrznym indeksem wyszukiwawczym. Rozszerzenia tego paradygmatu dotyczą zarówno warstwy orkiestracji — *Agentic RAG* z dekompozycją zapytań i wieloetapowym planowaniem [2] — jak i warstwy cachowania kontekstu — *Cache-Augmented Generation* (CAG) wykorzystujące długi kontekst współczesnych modeli jako alternatywę dla wyszukiwania [3]. Optymalizacje na poziomie infrastruktury, takie jak współdzielenie cache klucz–wartość przez warstwy systemu [4], oraz aktualne przeglądy literatury [5] dokumentują dojrzewanie ekosystemu RAG.

W typowej architekturze dwuetapowej, *bi-encoder* (model embeddingowy, taki jak BGE-M3 [6]) zwraca kandydatów semantycznie podobnych do zapytania, a *cross-encoder* (reranker) wykonuje precyzyjny scoring par zapytanie–passage. Reranker decyduje o ostatecznej kolejności top-*k* i tym samym o jakości kontekstu dostarczanego do modelu generatywnego. Dla języka polskiego dostępny jest model `polish-reranker-roberta-v3` [7], trenowany na tłumaczeniach MSMARCO — co czyni go modelem ogólnodomenowym, a nie zaadaptowanym do żadnej domeny specjalistycznej.

Operacjonalizacja cyklu życia modeli uczenia maszynowego ewoluowała od koncepcji *hidden technical debt* [8] poprzez sformalizowane architektury MLOps [9] aż do wyspecjalizowanej dyscypliny LLMOps [10], adresującej specyfikę dużych modeli językowych: ich rozmiar, koszty inferencji, ewaluację przez LLM oraz orkiestrację wielokomponentowych systemów RAG.

Polski ekosystem otwartych modeli językowych dostarczył kilka znaczących artefaktów istotnych dla pracy: Bielik 11B v3 jako open-source generator z licencją Apache 2.0 [11], model embeddingowy BGE-M3 z wielojęzycznym pokryciem [6] oraz wspomniany reranker `polish-reranker-roberta-v3` [7]. Modele te umożliwiają zbudowanie stacku RAG w całości on-premise bez zależności od zamkniętych API.

Wykorzystanie modeli językowych jako automatycznych sędziów relewancji (*LLM-as-judge*) zostało wprowadzone do mainstreamu przez prace Zheng i in. [12] oraz Chianga i Lee [13]. Walidacja zgodności takiego sędziego z anotacją ekspercką (Cohen's kappa, accuracy) pozostaje otwartym zagadnieniem dla domen specjalistycznych w języku polskim, dla których audit trail w literaturze jest skąpy.

Wreszcie, niestacjonarność rozkładu danych — *concept drift* — wymaga osobnej warstwy monitoringu w systemach produkcyjnych [14]. Empiryczne studia metod detekcji *dataset shift* [15] pokazują, że detekcja na rozkładzie embeddingów (zamiast surowych danych) bywa bardziej czuła i interpretowalna w kontekście RAG.

## 1.2. Motywacja i sformułowanie problemu

Trzy luki badawcze motywują niniejszą pracę.

**Pierwsza luka** dotyczy operacjonalizacji retreningu polskiego rerankera dla domeny specjalistycznej. Baseline `polish-reranker-roberta-v3` jest modelem ogólnodomenowym; specjalistyczna terminologia farmaceutyczna (międzynarodowe nazwy DCI, kody ATC, terminologia łacińsko-polska, nazewnictwo postaci leku) jest słabo reprezentowana w jego pretraining corpus. Domain adaptation rerankera dla polskiej farmakologii wymaga pełnego pipeline'u MLOps — generacji syntetycznych zapytań, anotacji preferencyjnej, fine-tuningu z preferencjami, A/B gating oraz monitoringu — a publiczna implementacja takiego pipeline'u w literaturze polskiej nie została udokumentowana.

**Druga luka** dotyczy walidacji LLM-as-judge dla polskiej domeny specjalistycznej. Mimo szerokiego stosowania sędziów LLM w preferencyjnym treningu rerankerów [12], audit zgodności sędziego z manualnymi labelami ekspertów dla polskich domen specjalistycznych jest rzadko raportowany, a jeszcze rzadziej falsyfikowany konkretnymi progami kappa.

**Trzecia luka** dotyczy aligned corpus *Charakterystyka Produktu Leczniczego ↔ Ulotka dla pacjenta* (ChPL↔Ulotka) jako zasobu do badań nad cross-register retrieval. Grabowski [16] opublikował comparable corpus EN-PL Patient Information Leaflets, lecz jest to korpus *cross-language*, nie *intra-language cross-register*. Prace nad *expertise style transfer* [17] i upraszczaniem tekstów medycznych [18] adresują przekształcanie rejestru, lecz nie odpowiadają na pytanie czy reranker dotrenowany na parach pro/lay obsługuje zapytania w jednym rejestrze przeciw odpowiedziom w drugim — co stanowi kluczową kompetencję dla systemu RAG mającego obsługiwać zarówno specjalistów (lekarzy, farmaceutów), jak i pacjentów.

**Formalne sformułowanie problemu.** Niniejsza praca rozważa problem zaprojektowania pipeline'u MLOps, który dla zadanego wejściowego korpusu polskich dokumentów farmaceutycznych $X$ (ChPL professional + Ulotki layperson + dokumenty HTA, refundacyjne i OA-journals), zapytań w języku polskim w dwóch rejestrach (lay i professional) oraz iteracyjnych sygnałów z observability, generuje rerankowane fragmenty $Y$ pod ograniczeniami $Z$ (stack open-source, on-premise deployment, polski język, niska tolerancja błędu w domenie regulowanej), optymalizując zestaw metryk $M$: retrieval quality (nDCG@10, MRR@10), judge agreement (Cohen's kappa), drift detection (precision/recall), cross-register retrieval (accuracy@10 per direction). Wszystkie progi kwantyfikatorów dla $M$ definiowane szczegółowo w Rozdz. 6 (Modele) i Rozdz. 7 (Wyniki).

## 1.3. Cel i zadania

Głównym celem pracy jest zaprojektowanie, implementacja i ewaluacja pipeline'u MLOps do iteracyjnego dotrenowywania komponentów retrievalu w polskojęzycznym systemie RAG na podstawie sygnałów z observability, w studium przypadku domeny farmakologii klinicznej, z dodatkowym eksperymentem cross-register retrieval na paired Polish ChPL↔Ulotka corpus.

Praca dostarcza pięć niezależnie bronionych wymiarów wkładu inżynierskiego:

1. **Wymiar metodologiczny:** walidowany framework LLM-as-judge dla polskiej farmaceutycznej domeny specjalistycznej, z protokołami pairwise, pointwise, faithfulness oraz cross-register pair scoring.
2. **Wymiar inżynierski:** reprodukowalny pipeline MLOps do iteracyjnego retreningu komponentów RAG (open-source artefakt: Prefect orchestration, MLflow tracking, DVC versioning, Langfuse + OpenTelemetry observability, Evidently + Alibi Detect drift detection).
3. **Wymiar artefaktowy:** dotrenowany cross-encoder reranker dla polskiej farmakologii, udostępniany jako artefakt HuggingFace z model card.
4. **Wymiar eksperymentalny:** framework detekcji drift na rozkładzie embeddingów BGE-M3 z ewaluacją na symulowanym OOD (out-of-distribution).
5. **Wymiar korpusowy:** pierwszy publicznie udokumentowany Polish ChPL↔Ulotka aligned corpus oraz metodologia cross-register retrieval evaluation jako *standalone* artefakt naukowy.

Każdy z pięciu wymiarów stanowi samodzielny rezultat inżynierski. Kryteria sukcesu i konkretne progi metryczne dla każdego z wymiarów definiowane w Rozdz. 6 i Rozdz. 7.

## 1.4. Zakres pracy

W zakresie pracy znajdują się: jakość retrievalu (nDCG@10, MRR@10) mierzona przeciwko external benchmarkowi proxy i manualnie zwalidowanej próbce 200 par próbkowanej z psychiatrycznej podgrupy korpusu (kody ATC N05/N06) jako gold standard; walidacja sędziego LLM przeciwko manualnym labelom autorki; inżynieria pipeline'u retreningu w trzech cyklach z analizą plateau; detekcja drift na rozkładach embeddingów z ewaluacją na symulowanym OOD; oraz eksperyment cross-register retrieval na 1800 paired ChPL↔Ulotka par.

Poza zakresem pracy znajdują się: walidacja poprawności medycznej i farmaceutycznej zwracanych fragmentów (autorka nie jest farmaceutką ani lekarzem; praca nie jest systemem doradztwa farmaceutycznego i nie może być takim wdrażana); fine-tuning embeddera (BGE-M3 pozostaje frozen); hard negative mining dla embeddera; detekcja drift na produkcyjnym ruchu w czasie rzeczywistym; generalizacja cross-domain (poza farmakologią); oraz transfer cross-register na inne języki UE (np. EN SPC↔PIL, DE Fachinfo↔Beipackzettel) — wskazany jako przyszła praca.

Decyzje architektoniczne dotyczące wyboru domeny oraz dodania komponentu cross-register opisane są w dwóch ADR-ach: DEC-001 (rotacja domeny z psychiatrii klinicznej na farmakologię szeroką z psychiatrycznym eval subsetem) oraz DEC-002 (włączenie ChPL↔Ulotka pairing jako piątego pytania badawczego). Pełny audit trail decyzji dostępny w `thesis_research/decisions/`.

## 1.5. Struktura pracy

Praca składa się z ośmiu rozdziałów. Rozdz. 2 prezentuje przegląd literatury z formalną metodologią selekcji źródeł, obejmując prace nad RAG, MLOps continuous training, LLM-as-judge, drift detection oraz cross-register medical NLP. Rozdz. 3 dokumentuje sześcioskładnikową strategię korpusu farmakologicznego (ChPL, Ulotki, AOTMiT, NFZ, OA journals, adjacencies) wraz z licencjami i metodologią scrape. Rozdz. 4 przedstawia eksploracyjną analizę danych: rozkłady długości, klastry embeddingów BGE-M3 w przestrzeni UMAP, jakość OCR oraz analizę alignmentu paired ChPL↔Ulotka. Rozdz. 5, *centralny rozdział pracy*, opisuje architekturę pipeline'u w siedmiu diagramach, w tym branch cross-register retrieval. Rozdz. 6 dokumentuje szczegóły komponentów modelowych: fine-tuning rerankera z czteropoziomową strategią hard negatives [19] oraz cztery protokoły LLM-as-judge, wraz z ablacjami A1–A4. Rozdz. 7 raportuje wyniki: baselines (BM25 + dense + base reranker) przeciwko trzem cyklom retreningu, kategoryczną analizę błędów na sześciopoziomowej taksonomii, ewaluację detekcji drift na symulowanym OOD oraz wyniki cross-register per kierunek (lay→pro vs pro→lay). Rozdz. 8 syntetyzuje wkład pracy w pięciu wymiarach, omawia ograniczenia oraz wskazuje kierunki przyszłych prac, w tym transfer cross-register na inne języki UE i inne polskie domeny dwurejestrowe.

## 1.6. Pytania badawcze i hipotezy

Praca formułuje pięć pytań badawczych. Każdemu pytaniu odpowiada falsyfikowalna hipoteza. Operacyjne progi metryczne, protokoły testowania istotności statystycznej oraz analiza falsyfikowalności hipotez są szczegółowo zdefiniowane w Rozdz. 6 (Modele) i Rozdz. 7 (Wyniki).

**RQ1.** Czy iteracyjny retrening cross-encoder rerankera na preferencjach generowanych przez LLM-as-judge prowadzi do istotnej poprawy jakości retrievalu względem baseline `polish-reranker-roberta-v3` dla polskiej farmakologii klinicznej?
**H1.** Retrening rerankera prowadzi do poprawy nDCG@10 o co najmniej dziesięć punktów procentowych względem baseline, mierzonej na manualnie zwalidowanej próbce ewaluacyjnej z psychiatrycznej podgrupy ATC N05/N06.

**RQ2.** W jakim stopniu LLM-as-judge oparty na otwartych polskich modelach osiąga zgodność z manualną relewancyjną anotacją autorki dla domeny farmaceutycznej?
**H2.** Wybrany sędzia LLM osiąga zgodność z manualnymi labelami na poziomie co najmniej 75% accuracy oraz Cohen's kappa co najmniej 0,50.

**RQ3.** Po ilu cyklach iteracyjnego retreningu obserwuje się efekt plateau w metrykach retrieval quality?
**H3.** Trzeci cykl retreningu daje poprawę nDCG@10 nie większą niż dwa punkty procentowe względem cyklu drugiego, przy braku istotności statystycznej różnicy.

**RQ4.** Czy detektor drift na rozkładzie embeddingów BGE-M3 rozpoznaje syntetyczny out-of-distribution z odpowiednią precyzją i pełnością?
**H4.** Detektor drift osiąga precyzję co najmniej 0,80 i pełność co najmniej 0,70 na zestawie symulowanego OOD obejmującym zapytania spoza klas farmaceutycznych korpusu treningowego.

**RQ5.** Czy reranker dotrenowany na korpusie zawierającym paired ChPL↔Ulotka obsługuje cross-register queries (lay query → professional answer i odwrotnie) z akceptowalną dokładnością i niewielkim spadkiem względem same-register baseline?
**H5.** Reranker dotrenowany na korpusie z paired pro/lay versions osiąga cross-register accuracy@10 na poziomie co najmniej 70%, z różnicą nie większą niż pięć punktów procentowych względem same-register accuracy.

Praca przyjmuje 5-wymiarowy model wkładu opisany w §1.3. Sukces inżynierski mierzony jest niezależnie w każdym z wymiarów: pipeline jako artefakt, walidowany sędzia LLM jako framework, dotrenowany reranker jako artefakt HuggingFace, framework drift jako komponent eksperymentalny oraz aligned ChPL↔Ulotka corpus jako wkład korpusowy. Magnituda empirycznej poprawy retrievalu (RQ1) jest jednym z wymiarów, ale nie jedynym warunkiem sukcesu pracy.

---

## Bibliografia (placeholder do konwersji na footnotes IEEE)

🟡 = do weryfikacji przez `citation-checker` przed final submission.

[1] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., Kiela, D. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020.

[2] Singh, A., et al. (2025). *Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG*. arXiv:2501.09136. 🟡 verify exact author list

[3] Chan, B. J., Chen, C.-T., Cheng, J.-H., Huang, H.-H. (2025). *Don't Do RAG: When Cache-Augmented Generation is All You Need for Knowledge Tasks*. WWW '25 (Companion). 🟡 verify

[4] Jin, C., Zhang, Z., Jiang, X., Liu, F., Liu, X., Liu, X., Jin, X. (2024). *RAGCache: Efficient Knowledge Caching for Retrieval-Augmented Generation*. arXiv:2404.12457.

[5] Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Guo, Q., Wang, M., Wang, H. (2024). *Retrieval-Augmented Generation for Large Language Models: A Survey*. arXiv:2312.10997 (v5).

[6] Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., Liu, Z. (2024). *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*. arXiv:2402.03216. 🟡 verify

[7] Dadas, S. (n.d.). *polish-reranker-roberta-v3* [Model card]. HuggingFace. 🟡 verify exact citation format

[8] Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., Young, M., Crespo, J.-F., Dennison, D. (2015). *Hidden Technical Debt in Machine Learning Systems*. NeurIPS 2015.

[9] Kreuzberger, D., Kühl, N., Hirschl, S. (2023). *Machine Learning Operations (MLOps): Overview, Definition, and Architecture*. IEEE Access, vol. 11.

[10] Pahune, S., Akhtar, Z. (2025). *Transitioning from MLOps to LLMOps: Navigating the Unique Challenges of Large Language Models*. Information, 16(2). 🟡 verify

[11] Ociepa, K., et al. (2025). *Bielik 11B v3: A Polish Large Language Model*. Computer Science (AGH), 26(4). 🟡 verify exact venue/year

[12] Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., Stoica, I. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. NeurIPS 2023 Datasets and Benchmarks Track.

[13] Chiang, C.-H., Lee, H.-Y. (2023). *Can Large Language Models Be an Alternative to Human Evaluations?*. ACL 2023.

[14] Gama, J., Žliobaitė, I., Bifet, A., Pechenizkiy, M., Bouchachia, A. (2014). *A Survey on Concept Drift Adaptation*. ACM Computing Surveys, 46(4).

[15] Rabanser, S., Günnemann, S., Lipton, Z. C. (2019). *Failing Loudly: An Empirical Study of Methods for Detecting Dataset Shift*. NeurIPS 2019.

[16] Grabowski, Ł. (2017). *Constructing an English-Polish Patient Information Leaflet Corpus*. 🟡 verify exact venue/journal/page numbers

[17] Cao, Y., Shui, R., Pan, L., Kan, M.-Y., Liu, Z., Chua, T.-S. (2020). *Expertise Style Transfer: A New Task Towards Better Communication between Experts and Laymen*. ACL 2020. 🟡 verify

[18] Devaraj, A., Marshall, I. J., Wallace, B. C., Li, J. J. (2021). *Paragraph-level Simplification of Medical Texts*. NAACL 2021. 🟡 verify

[19] Karpukhin, V., Oğuz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., Yih, W. (2020). *Dense Passage Retrieval for Open-Domain Question Answering*. EMNLP 2020.

---

## Notki do self-review (do usunięcia przed finalizacją)

- **Cytacje:** 19 pozycji, w celu 15–25 ✓
- **Klastry tematyczne pokryte:**
  - LLMOps × MLOps: [8] [9] [10] ✓
  - RAG / CAG / Agentic: [1] [2] [3] [4] [5] ✓
  - Polish LLM: [6] [7] [11] ✓
  - LLM-as-judge: [12] [13] ✓
  - Drift: [14] [15] ✓
  - Cross-register medical NLP: [16] [17] [18] ✓
  - Domain context / DPR: [19] (Karpukhin do hard negatives w R6) ✓
- **Klasyczny układ:** Tło → Motywacja+Problem → Cel → Zakres → Struktura → RQ ✓ (RQ na końcu)
- **Time-proofing audit:** brak "obecnie", "rosnące", "brak" (zastąpione: "literatura nie udokumentowała", "audit trail jest skąpy", "luka badawcza"), brak "jedyny", brak "żaden" ✓
- **Academic style:** strona bierna/3 osoba ("Praca rozważa…", "Pipeline dostarcza…"), bez 1 os., bez potoczyzmów ✓
- **Bez emoji** w treści ✓
- **5 wymiarów kontrybucji** w §1.3 ✓
- **5 RQ + 5 H falsyfikowalne** z progami zdaniowo (NIE tabela) ✓
- **Powołanie DEC-001/DEC-002** w §1.4 ✓
- **Length estimate:** ok. 1450 słów (do zweryfikowania po formatowaniu w Wordzie) — w celu 1000–1500 ✓
