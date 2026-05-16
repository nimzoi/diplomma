# R8. Podsumowanie

> **Status draftu:** v0.1 (2026-05-16) — markdown source dla `thesis_elements/R08_podsumowanie.docx`.
> **Cel długościowy:** ~3000–5000 słów (5–7 stron PJATK; R8 typowo krótszy niż R1/R5/R7).
> **Format docelowy:** PJATK — TNR 12pt, line 1.5, marginesy 2.5cm, footnotes IEEE 10pt. Cytacje `[N]` w markdownie konwertowane do footnotes po skopiowaniu do Worda.
> **Completion target:** sekcja 8.2 (5-wymiarowa kontrybucja) i sekcja 8.5 (future work) — 100%; sekcja 8.3 (status hipotez) — placeholder do wypełnienia po Iteracjach 2–6 zgodnie z konspektem II.16; pozostałe sekcje — defensible draft.
> **Notki dla autorki:** cytacje oznaczone 🟡 — do weryfikacji przez `citation-checker` przed final submission. Numeracja sekcji 8.1–8.6 zgodnie z planem zadania 08 (`assignments/plans/zadanie_08_plan.md` § 3) oraz wymogiem PRO-D Assignment 12 (Conclusions / Limitations / Future Work).

---

## 8.1. Podsumowanie pracy

Niniejsza praca zaprojektowała, zaimplementowała i poddała ewaluacji pipeline MLOps do iteracyjnego dotrenowywania komponentów retrievalu w polskojęzycznym systemie *Retrieval-Augmented Generation* (RAG) na podstawie sygnałów z warstwy *observability*, w studium przypadku domeny farmakologii klinicznej. Pipeline integruje sześć kluczowych komponentów: (1) generację syntetycznych zapytań przez otwarty polski model językowy Bielik 11B v3 [1], (2) anotację preferencyjną par *passage* przez sędziego LLM (`<judge_model>` wybrany w Iteracji 0b spośród czterech kandydatów: Bielik 11B v3, Gemma 3 27B, Qwen 3 32B, Claude Haiku 4.5) w czterech protokołach (pairwise, pointwise, faithfulness, cross-register pair scoring), (3) iteracyjny fine-tuning rerankera typu *cross-encoder* `polish-reranker-roberta-v3` [2] w trzech cyklach z preference loss i hyperparameter search przez Optunę, (4) ewaluację jakości retrievalu przeciw external benchmark proxy oraz manualnie zwalidowanej próbce 200 par *gold standard* z psychiatrycznej podgrupy ATC N05/N06, (5) detekcję *drift* na rozkładach embeddingów BGE-M3 [3] z trigger logic do retreningu (Evidently AI [4] + Alibi Detect [5]) oraz (6) eksperyment cross-register retrieval na *paired Polish ChPL↔Ulotka corpus* — pierwszej publicznie udokumentowanej polskiej parze profesjonalny↔laypersonowski rejestr w domenie farmaceutycznej.

Pięć pytań badawczych zostało zoperacjonalizowanych z falsyfikowalnymi progami statystycznymi: RQ1 (poprawa nDCG@10 rerankera o ≥10 punktów procentowych względem baseline), RQ2 (zgodność sędziego LLM z manualną anotacją na poziomie Cohen's kappa ≥0,50), RQ3 (plateau retreningu po cyklu 2 — cykl 3 daje ≤2 pp dodatkowej poprawy), RQ4 (precision drift detectora ≥0,80, recall ≥0,70 na symulowanym OOD) oraz RQ5 (cross-register accuracy@10 ≥70%, gap między kierunkami same-vs-cross register ≤5 pp). Wszystkie eksperymenty raportowane są na trzech *random seeds* (mean ± std), z document-level splits (eliminacja leakage), z *gating logic* przez próg nDCG@10 dla A/B testu w MLflow Model Registry [6].

Stack technologiczny pracy oparty jest w całości na otwartych narzędziach MLOps: Prefect 3 (orkiestracja), MLflow + Optuna (tracking i hyperparameter search), Langfuse + LGTM stack (observability LLM i metryk), DVC + MinIO (versioning danych), PostgreSQL + Qdrant (metadane i wektory), SGLang (serving LLM) oraz TEI — *Text Embeddings Inference* (serving embedder + reranker). Korpus liczy ~4100 dokumentów rozłożonych na sześć strata: ChPL profesjonalne (22%), Ulotki dla pacjenta paired (22%), HTA + refundation legal AOTMiT i Ministerstwa Zdrowia (17%), refundation operational Narodowego Funduszu Zdrowia (10%), open-access polskie czasopisma farmaceutyczne (22%) oraz adjacencies URPL DHPC i listy braków (7%) — pełna tabela z URL-ami, licencjami i scrape methods w `sources_catalog.md` (single source of truth dla Rozdziału 3 Dane).

System został zademonstrowany przez Gradio UI z trzema zakładkami (Demo, Compare, Annotate) z mandatory disclaimerem o niemedycznym charakterze artefaktu badawczego. Praca **nie pretenduje do oceny farmaceutycznej ani medycznej** — autorka nie jest farmaceutką ani lekarzem. Mierzona jest wyłącznie jakość retrievalu (czy reranker zwraca *passage'y* merytorycznie relewantne dla query) oraz *faithfulness* (czy odpowiedź LLM jest wsparta przez retrieved passages). Praca jest *research artefaktem* z pipeline'm ewaluacyjnym; domena farmaceutyczna pełni rolę testbedu dla precyzji retrievalu w dziedzinie regulowanej, gdzie tolerancja błędu jest niska. **Praca nie jest systemem doradztwa farmaceutycznego i nie może być takim wdrażana** — wymóg ten jest powtórzony w mandatory disclaimerze Gradio UI oraz w Rozdziale 5 (Architektura) sekcja "User-facing demo".

---

## 8.2. Pięć niezależnych wymiarów wkładu

Wkład pracy ma **pięć niezależnych wymiarów**. Empiryczna *magnitude* poprawy retrievalu (RQ1) jest tylko jednym z nich, a nie warunkiem koniecznym dla obrony pozostałych czterech.

**1. Wkład metodologiczny.** Praca dostarcza walidowany framework *LLM-as-judge* dla polskiej domeny specjalistycznej (RQ2 / H2) — pierwszy taki audit publicznie udokumentowany dla farmakologii polskiej. Framework obejmuje cztery protokoły sędziego: pairwise (główny sygnał treningowy dla preference loss rerankera), pointwise (sanity check spójności wewnętrznej oceny absolutnej), faithfulness (end-to-end metric jakości generacji RAG przez Bielik 11B v3) oraz cross-register pair scoring (4. protokół dodany dla RQ5, rozdzielający wymiar *semantic match quality* od wymiaru *register appropriateness*). Walidacja sędziego prowadzona jest dwustopniowo — pilot kappa ranking na próbie 30 par w Iteracji 0b dla shortlistowania top-2 kandydatów, head-to-head na próbie 200 par manualnych w Iteracji 2 dla finalnego wyboru z defensible kappa CI ±0,05–0,08. Metodologia ta jest reprodukowalna dla każdej innej polskiej domeny specjalistycznej (prawnej, technicznej, finansowej) wymagającej walidacji sędziego LLM przed użyciem go jako sygnału treningowego.

**2. Wkład inżynierski.** Praca dostarcza reprodukowalny pipeline MLOps retreningu komponentów RAG jako otwarty artefakt repozytorium kodu (DVC dla danych, MLflow Model Registry dla wersji modeli, Prefect 3 DAG-y dla orkiestracji, Hydra config dla parametryzacji ablacji, GitHub Actions CI/CD dla gating). Pipeline integruje sześć warstw (dane → indeksowanie → generacja queries → judge → training → ewaluacja → drift detection → A/B gating → deployment) w sposób umożliwiający przełączanie ablacji A1–A4 jako pojedynczych parametrów konfiguracyjnych. Stack jest w całości otwarty (Apache 2.0, MIT, CC-BY z świadomym wyjątkiem `<judge_model>` jeśli wybór padnie na CC-BY-NC PLLuM 12B-instruct lub komercyjne Claude Haiku 4.5 API, z explicite zapisanym fallbackiem do fully-open w sekcji 8.4 limitations). Pipeline jest *self-hosted ready* — nie wymaga zewnętrznych usług zarządzanych poza opcjonalnym `<judge_model>` API, co ma znaczenie dla przyszłej adaptacji w domenach z wymogami przetwarzania danych on-premise.

**3. Wkład artefaktowy.** Praca dostarcza dotrenowany `polish-reranker-roberta-v3` dla domeny farmakologii klinicznej — artefakt opublikowany na HuggingFace dostępny społeczności polskiego NLP. Domain adaptation modelu adresuje **polish-specific patterns wokół międzynarodowej terminologii** (polska fleksja DCI przez 7 przypadków, elastyczny szyk wyrazów, regulatorowa frazeologia ChPL/Ulotek, polskie ramy refundacyjne bez angielskiego ekwiwalentu) plus cross-register handling (per RQ5 / DEC-002) — międzynarodowa terminologia farmaceutyczna (DCI/INN/ATC) jest znana base model z pretrainingu, novel wkład artefaktu jest w polish-specific patternach (per `02b_konspekt_v3_updates.md` § II.2.1). Artefakt obejmuje wagi modelu po trzech cyklach retreningu, model card z dokumentacją hyperparametrów, evaluation metrics na hold-out test set oraz na manual gold standard (200 par psych subset), checkpoints poszczególnych cykli (umożliwiające reprodukcję eksperymentu plateau analysis dla RQ3) oraz preference dataset (~145 tysięcy quadrupletów *(query, positive, 3 hard negatives)* z 4-poziomowej strategii hard negative mining inspirowanej DPR Karpukhina i in. [7], rozszerzonej o L4 cross-register layer dla RQ5). Artefakt ten wypełnia konkretną lukę w polskim ekosystemie modeli retrievalowych — brak otwartego rerankera farmaceutycznego dla języka polskiego, walidowanego względem manualnie zanotowanych par.

**4. Wkład eksperymentalny.** Praca dostarcza framework *drift detection* z *simulated drift evaluation* (RQ4 / H4) — reprodukowalny benchmark dla polskiego specialized RAG. Framework obejmuje implementację dwóch testów statystycznych (Kolmogorov-Smirnov per-dimension oraz Maximum Mean Discrepancy multivariate) na rozkładach embeddingów BGE-M3 z rolling window vs reference set, eksperyment kontrolowany ze zmieniającą się proporcją OOD queries (0% → 100%) z dwóch źródeł symulacji (out-of-subdomain — neurologia zamiast psychiatrii; perturbed in-distribution — paraphrasing psych queries z zachowaniem semantyki) oraz raportowanie precision/recall przy różnych progach detekcji wraz z analizą trade-offu false positive rate / detection latency. Framework jest reprodukowalny dla każdej innej polskiej domeny specjalistycznej z zaadaptowanym reference setem; wynik eksperymentu (czy detector osiąga założone progi precision ≥0,80 i recall ≥0,70) ma wartość metodologiczną niezależnie od kierunku — zarówno potwierdzenie, jak i odrzucenie hipotezy informuje przyszłą pracę nad drift detection w polskim NLP.

**5. Wkład korpusowy / metodologiczny novel.** Praca dostarcza pierwszy publicznie udokumentowany *Polish ChPL↔Ulotka aligned corpus* wraz z *cross-register retrieval evaluation methodology* (RQ5 / H5). Luka literaturowa potwierdzona w sources research R2 (2026-05-15): Grabowski [8] opublikował comparable corpus EN-PL Patient Information Leaflets, lecz jest to korpus *cross-language* (angielski↔polski), a nie *intra-Polish cross-register* (polski profesjonalny ↔ polski laypersonowski). Prace anglojęzyczne nad *expertise style transfer* w domenie medycznej (Cao i in. [9]) oraz upraszczaniem tekstów medycznych (Devaraj i in. [10], van den Bercken i in. [11]) adresują przekształcanie rejestru w *generacji*, lecz nie odpowiadają na pytanie metodologiczne dotyczące *retrievalu*: czy reranker dotrenowany na korpusie zawierającym sparowane wersje pro/lay obsługuje zapytania w jednym rejestrze przeciw odpowiedziom w drugim, oraz w jakiej skali występuje asymetria gap między kierunkami lay→pro a pro→lay. Aligned corpus oparty jest na deterministycznym `productID` z URPL RPL XML feed (~900 par leków, 1800 cross-register par programatycznie wygenerowanych z headerów sekcji ChPL i Ulotek), z spot-check manualnym na 50 par (5% wielkości) dla walidacji jakości alignmentu.

**Każdy z pięciu wymiarów broni się niezależnie.** W przypadku odrzucenia H1 (retreningowy reranker nie osiąga założonej poprawy nDCG@10 o ≥10 pp względem baseline `polish-reranker-roberta-v3`), praca zachowuje wkład w wymiarach (2)–(5) — z szczególnym wyróżnieniem RQ5 jako wyróżnionej kontrybucji do polskiego *BioNLP* oraz aligned corpus jako standalone *publishable artifact* poza ramami pracy dyplomowej. Oznacza to, że framework metodologiczny (1), pipeline inżynierski (2), drift detection benchmark (4) oraz aligned corpus + cross-register methodology (5) pozostają wartościowe dla społeczności polskiego NLP niezależnie od końcowego empirycznego wyniku centralnego pomiaru retrievalu w cyklu 1 retreningu rerankera. Defense scaffolding tej pracy została zaprojektowana z świadomością ryzyka *negative result* (rzeczywiste eksperymenty z LLM-as-judge w specialistycznych domenach często ujawniają niższe agreement niż oczekiwane, a polski ekosystem otwartych modeli sędziowskich pozostaje słabiej walidowany niż angielskojęzyczny [12]) — i ten ryzyk jest *expectation managed* już w design phase, nie ad-hoc po empirycznym wyniku.

---

## 8.3. Status hipotez RQ1–RQ5

> **Notka:** Status hipotez wypełniany po Iteracjach 2–6 (zgodnie z konspektem II.16). Tabela 8.1 zawiera placeholder `🟡 Status TBD post-Iteracja N` z explicytnym progiem falsyfikowalnym dla każdej hipotezy. Po zamknięciu eksperymentów, status każdej hipotezy może przyjąć wartość: **PASSED** (próg spełniony), **FAILED** (próg nie spełniony), **PARTIAL** (próg spełniony jednoetapowo / w jednym wymiarze, nie spełniony w drugim), lub **INCONCLUSIVE** (wynik statystycznie nie różni się istotnie od progu — wymaga discussion w R7).

**Tabela 8.1.** Status pięciu hipotez badawczych z progami falsyfikowalnymi.

| RQ | Hipoteza H | Próg falsyfikowalny | Iteracja | Status | Odniesienie do R7 |
|----|------------|---------------------|----------|--------|-------------------|
| RQ1 | H1: reranker dotrenowany jednokrotnie poprawia nDCG@10 vs base polish-reranker | poprawa ≥10 punktów procentowych nDCG@10 na manual gold standard 200 par; mean ± std na 3 random seeds | Iteracja 2 | 🟡 TBD post-Iteracja 2 | R7.1 |
| RQ2 | H2: `<judge_model>` w protokole pairwise wykazuje agreement z manual labels autorki | accuracy ≥75% AND Cohen's kappa ≥0,50 (3-poziomowa skala A / B / tie) na próbie 200 par | Iteracja 2 | 🟡 TBD post-Iteracja 2 | R7.2 |
| RQ3 | H3: iteracyjny retrening plateauje po cyklu 2 | cykl 3 daje ≤2 pp dodatkowej poprawy nDCG@10 vs cykl 2; statystycznie nieistotna w 3-seed setup (p > 0,05) | Iteracja 3 | 🟡 TBD post-Iteracja 3 | R7.3 |
| RQ4 | H4: drift detector wykrywa simulated OOD queries | precision ≥0,80 AND recall ≥0,70 przy progu detekcji 95-percentile reference distribution | Iteracja 5 | 🟡 TBD post-Iteracja 5 | R7.4 |
| RQ5 | H5: reranker dotrenowany na ChPL+Ulotka pairs handluje cross-register queries | accuracy@10 ≥70% AND gap same-vs-cross ≤5 pp AND brak regresji na same-register baseline >2 pp | Iteracja 4 | 🟡 TBD post-Iteracja 4 | R7.5 |

**Sposób raportowania w finalnej wersji R8 (po wypełnieniu Iteracji 2–6):**

- **RQ1 H1:** [PASSED / FAILED / PARTIAL / INCONCLUSIVE] na podstawie sekcji R7.1. [Krótka jednolinijkowa interpretacja: empiryczna wartość poprawy nDCG@10 cykl 1 vs baseline.]
- **RQ2 H2:** [PASSED / FAILED / PARTIAL / INCONCLUSIVE] na podstawie sekcji R7.2. [Krótka jednolinijkowa interpretacja: empiryczna wartość Cohen's kappa dla finalnego `<judge_model>`.]
- **RQ3 H3:** [PASSED / FAILED / PARTIAL / INCONCLUSIVE] na podstawie sekcji R7.3. [Krótka jednolinijkowa interpretacja: empiryczna wartość delta nDCG@10 cykl 3 vs cykl 2 i p-value.]
- **RQ4 H4:** [PASSED / FAILED / PARTIAL / INCONCLUSIVE] na podstawie sekcji R7.4. [Krótka jednolinijkowa interpretacja: empiryczna wartość precision i recall na simulated OOD przy progu 95-percentile.]
- **RQ5 H5:** [PASSED / FAILED / PARTIAL / INCONCLUSIVE] na podstawie sekcji R7.5. [Krótka jednolinijkowa interpretacja: empiryczna wartość accuracy@10 per kierunek (lay→pro, pro→lay) i asymmetry gap.]

**Uwaga interpretacyjna.** Status `PARTIAL` jest świadomie dopuszczalną wartością — np. dla H5 możliwe jest spełnienie progu accuracy@10 ≥70% przy jednoczesnym przekroczeniu progu gap ≤5 pp (sytuacja: reranker handluje cross-register w sumie dobrze, ale z istotną asymetrią między kierunkami lay→pro a pro→lay). Taki wynik jest *informacyjnie wartościowy* — wskazuje na różną trudność dwóch kierunków cross-register retrieval, co ma implikacje dla projektowania interfejsów użytkownika systemów RAG (czy system wymaga osobnych ścieżek per rejestr). Status `INCONCLUSIVE` rezerwowany jest dla sytuacji statystycznej niejednoznaczności (np. delta między cyklem 2 a 3 wynosi 2,3 pp z szerokim 95% CI obejmującym 0 — formalnie próg ≤2 pp nie spełniony, ale efekt nie jest istotny).

---

## 8.4. Świadome ograniczenia pracy

Niniejsza sekcja prezentuje świadomie zaakceptowane ograniczenia pracy, w czterech kategoriach: (i) dataset, (ii) model, (iii) ewaluacja, (iv) external validity. Każde ograniczenie jest świadomą decyzją architektoniczną z udokumentowanym rationale, a nie *oversight*; każde ograniczenie ma odpowiednik w odpowiednim wcześniejszym rozdziale (R3 dataset bias, R5/R6 model constraints, R7 negative findings).

### 8.4.1. Ograniczenia datasetu

**Pięć świadomych biases korpusu**, dokumentowanych szczegółowo w `sources_catalog.md` § Biases oraz Rozdziale 3 sekcja 3.10:

1. **License bias.** Korpus obejmuje wyłącznie źródła open-access, urzędowe (Art. 4 ustawy o prawie autorskim) oraz CC BY/BY-NC/BY-SA/BY-NC-ND. Komercyjne (paywall) artykuły naukowe oraz proprietary databases farmakologiczne (np. Micromedex, Drugs.com Polish edition jeśli istnieją) — wyłączone. Konsekwencja: korpus reprezentuje *open-source pharmacology Poland*, nie *full pharmacology Poland landscape*.

2. **ATC bias.** Stratified sampling z over-representacją ATC N05 (Psycholeptica) i N06 (Psychoanaleptica) do ~30% próby (zamiast natural rate ~10% leków zarejestrowanych w URPL). Konsekwencja: korpus nadreprezentuje psychiatrię względem populacji wszystkich zarejestrowanych leków, dla wzmocnienia psych signal w training (zgodnie z eval set composition — sekcja 8.4.3).

3. **Recency bias.** Korpus pobierany w Iteracji 0a (Tydzień 0) z URPL feedu RPL XML — odzwierciedla stan rejestru w momencie scrape. Leki zarejestrowane lub deregistrowane po dniu scrape nie są reprezentowane. Konsekwencja: konkluzje pracy są time-stamped do okna scrape, nie generalizują na przyszłe stany URPL.

4. **Polish-only bias.** Wszystkie dokumenty w języku polskim natywnym — wyłączone tłumaczenia maszynowe oraz dokumenty wyłącznie anglojęzyczne. Konsekwencja: pracę nie generalizuje do *cross-language pharma RAG* (np. polski lekarz korzystający z angielskojęzycznego SmPC dla leków importowanych z innych państw UE).

5. **Source-type bias.** Korpus dominowany przez dokumenty regulatorowe (44% w stratach 1+2 ChPL+Ulotki) oraz HTA/legal (27% w stratach 3+4 AOTMiT/MZ/NFZ); dokumenty *scientific/educational* (czasopisma OA + adjacencies, 29% w stratach 5+6) stanowią mniejszość. Konsekwencja: reranker dotrenowany na tym korpusie może wykazywać niższą jakość retrievalu na queries z natury naukowej (mechanizmy działania, farmakokinetyka, randomized controlled trials) niż na queries regulatorowych (przeciwwskazania, dawkowanie, refundacja).

**Brand vs generic ambiguity.** Sampling po `productID` z URPL może produce duplikaty na poziomie DCI (np. dziesięć produktów handlowych zawierających sertralinę jako wspólną substancję czynną). Strategia deduplikacji oparta jest na DCI grouping z preferencją produktu z najnowszą datą rewizji ChPL — szczegóły w Rozdziale 3 sekcja 3.7. Brand vs generic effect na jakość retrievalu nie jest osobno mierzony w tej pracy (przyszła praca, sekcja 8.5).

**Iteracja 0 feasibility findings.** Konkretne metryki z feasibility test (OCR overhead actual %, alignment integrity rate ChPL↔Ulotka spot-check, URPL uptime ≥99% w 24h) są raportowane w Rozdziale 3 sekcja 3.9 — ich wartości empiryczne wpływają na finalną interpretację jakości korpusu i alignmentu.

**Dodatkowe biases zidentyfikowane post-EDA (R4 § 4.9.5).** Po przeprowadzeniu eksploracyjnej analizy danych zidentyfikowano dwa kolejne *świadome biases* uzupełniające pięcioskładnikowy zestaw powyżej:

6. **Encoding heterogeneity bias.** Pre-2015 ChPL z URPL feed wykazują nieregularne kodowanie polskich diakrytyków (sporadyczny drop znaków *ą/ę/ł*); post-processing pipeline stosuje `unicodedata.normalize('NFC', text)` jako mitygację, lecz pre-existing artefakty PDF text-layer pozostają niespójne. Konsekwencja: jakość embedding pre-2015 ChPL jest *systematically lower* niż post-2015; reranker może wykazywać niższą jakość dla starszych dokumentów.

7. **Single-annotator caveat.** Eval set 200 par gold standard jest *manually ranked* wyłącznie przez autorkę (single annotator), bez inter-annotator agreement statistics typowych dla manual gold standard medycznego. Mitygacja: intra-rater consistency check (re-rankowanie podzbioru 30 par po przerwie ≥7 dni — Cohen's kappa intra-rater ≥0,75 jako acceptance threshold). Konsekwencja: jakość eval set ograniczona kompetencjami pojedynczego annotatora; *external validity* eval set zależy od reprezentatywności decyzji autorki dla *consensus expert ranking*.

Biases #6 i #7 są dodatkami z R4 EDA findings — nie zastępują pięciu biases korpusu z `sources_catalog.md`, lecz uzupełniają je o aspekty technical processing (#6) i evaluation methodology (#7).

### 8.4.2. Ograniczenia modeli

**BGE-M3 frozen** — embedder pierwszego etapu retrievalu nie jest *fine-tunowany* w tej pracy. Hard negative mining dla embeddera (kontrastywne dotrenowanie embeddera na medical-specific positives/negatives) dawałoby potencjalnie większą poprawę całościowego retrievalu, ale jest *pain pointem* od strony danych (jakość negatives wymaga osobnego pipeline anotacji) i wymagałoby osobnej eksperymentalnej osi pracy. Świadoma decyzja: skupienie na rerankerze (drugi etap) jako modelu fine-tunowanym, przy pozostałych komponentach frozen (BGE-M3, Bielik, judge), dla zachowania zarządzalnego scope.

**polish-reranker-roberta-v3 base ~360M parametrów** — bez *scale-up* do większych rozmiarów (1B+ parametrów). Constraint *compute budget* — fine-tuning w trzech cyklach × trzy random seeds × Optuna hyperparameter search wymaga budżetu GPU akceptowalnego dla pojedynczego SP7 host w infrastrukturze ZAiAI@LAB. Większe rerankery (np. potencjalne polish-reranker-large-v4 jeśli takowy się pojawi) — przyszła praca.

**Judge model API vs local trade-off.** Wybór `<judge_model>` w Iteracji 0b między czterema kandydatami (Bielik 11B v3 / Gemma 3 27B / Qwen 3 32B / Claude Haiku 4.5) wprowadza świadomy trade-off: jeśli Claude Haiku 4.5 → API dependency (komercyjny endpoint Anthropic, opłaty per token, brak gwarancji długoterminowej dostępności wersji modelu); jeśli wybór padnie na model otwarty → local compute cost, ale pełna reprodukowalność i niezależność. Sekcja 8.5 future work obejmuje *judge model substitution audit* — czy zmiana sędziego pomiędzy cyklami retreningu degraduje jakość rerankera.

**Trzy random seeds** (nie pięć / dziesięć) — variance estimates conservative ze względu na *compute budget*. Konsekwencja: szerokie 95% CI dla raportowanych metryk; dla efektów blisko progu falsyfikowalności (np. delta cykl 3 vs cykl 2 ~2 pp) wynik może być INCONCLUSIVE zamiast PASSED/FAILED. Świadoma decyzja: lepiej trzy random seeds z pełną metodologią niż jeden seed z pseudo-pewnością.

### 8.4.3. Ograniczenia ewaluacji

**Eval set 200 par psych subset (ATC N05/N06)** — small N dla H2 Cohen's kappa confidence interval (oczekiwane CI ±0,05–0,08 dla finalnego pojedynczego sędziego po Iteracji 2 head-to-head). To jest **świadoma decyzja architektoniczna** zgodnie z DEC-001 (rotacja domeny), nie *oversight*. Rationale: leverage manual validation kompetencji autorki na poddomenie, którą zna (ATC N05/N06), dla rygorystycznej walidacji RQ2 / H2 — najsłabiej zabezpieczonej hipotezy, dla której nie istnieje external benchmark dla polskiej farmakologii. Eval set wąski (psych subset), training corpus szeroki (cała farmakologia) — to świadome rozdzielenie *eval scope ⊂ training scope*. Konsekwencja interpretacyjna: konkluzje pracy o jakości retrievalu są *strongest dla psych subdomain*, *moderately strong dla broad pharma* (extrapolation z manual validation na psych do całego training corpus). Eval set rozszerzony (~1500–2000 par) LLM-generated z spot-check 10% służy do hyperparameter tuning, nie do final reportingu.

**Simulated drift NIE real production traffic.** RQ4 / H4 conclusions ograniczone do warunków eksperymentu kontrolowanego: reference set = queries treningowe z cyklu N, OOD set = queries z innej subdomeny (neurologia zamiast psychiatrii) lub perturbed in-distribution (paraphrasing). Bez prawdziwych użytkowników nie ma real-time traffic; simulated drift jest kontrolowanym proxy. Generalizacja konkluzji RQ4 na *real production drift* w żywym RAG endpoint — przyszła praca (sekcja 8.5 II.13.4).

**Cross-register 1800 par programatycznie generated** — alignment integrity rate (Iteracja 0 pre-condition #5: ≥90% z competence-stratified spot-check 10/10 par z psych subset N05/N06) wpływa na quality cross-register evaluation. Spot-check manualny na 50 par (5% wielkości) jest jedyną manualną walidacją alignmentu; pełna manualna walidacja 1800 par jest *out of scope* dla pojedynczej autorki w okresie pracy dyplomowej.

**Wyłączona z scope: human evaluation końcowych odpowiedzi RAG** — końcowa odpowiedź wygenerowana przez Bielik 11B v3 na podstawie retrieved passages oceniana jest wyłącznie przez *automated faithfulness metric* (LLM-judge protocol 3) oraz przez RAGAS suite (`context_precision`, `context_recall`, `faithfulness`, `answer_relevancy`) [13]. Human evaluation odpowiedzi (np. *Likert 5-scale* per dimension przez panel ekspertów farmakologicznych) wymagałaby kohorty ekspertów + etyki badawczej + budżetu czasowego przekraczającego scope pracy dyplomowej. Konsekwencja: konkluzje o *answer quality* w sensie człowieczeństwie odbioru są ograniczone — mierzona jest *automated proxy* dla answer quality, nie sama answer quality.

### 8.4.4. External validity

**Pol-only — bez cross-language generalization claims.** Wszystkie eksperymenty na polskich dokumentach, polskich queries, polskim rerankerze, polskim sędzim LLM, polskim modelu generującym. Czy *lessons learned* z polskiej farmakologii cross-register (RQ5) transferują na inne języki UE (EN SPC↔PIL, DE Fachinfo↔Beipackzettel) — przyszła praca (sekcja 8.5 II.13.8). Niniejsza praca *nie* dostarcza dowodu na cross-language generalizability.

**Single domain (pharmacology) — bez cross-domain generalization claims.** Pracę trenuje i ewaluuje wyłącznie na farmakologii klinicznej (z psych eval subset). Czy reranker dotrenowany na pharmie generalizuje na inne polskie domeny specjalistyczne (prawo, finanse, technika, edukacja medyczna) — otwarte pytanie. Czy methodology cross-register (RQ5) transferuje na inne polskie domeny z dwoma rejestrami (np. prawo: kodeksy ↔ przewodniki dla obywateli; medycyna: wytyczne ↔ materiały edukacyjne pacjenta) — przyszła praca (sekcja 8.5 II.13.9).

**Single tooling stack** (SGLang dla LLM serving, TEI dla embedder/reranker, Prefect 3 dla orchestration, MLflow dla tracking, Langfuse dla observability) — alternative stacks (Ray Serve, Airflow, Kubeflow Pipelines, Weights & Biases, Arize AI) NIE compared. Konsekwencja: konkluzje o *engineering reproducibility* są związane z konkretnym wyborem stacku; przeniesienie pipeline'u na inny stack wymaga adaptacji (estymowany koszt: tygodnie do miesięcy w zależności od stopnia różnic).

**Wyłączona z scope: adversarial evaluation rerankera.** Czy atakujący znający dotrenowany reranker może wygenerować *adversarial passages*, które są wysoko rerankowane mimo niskiej rzeczywistej relewacji query — *not measured* w tej pracy. Powiązanie z wcześniejszą wersją tematu (v2 prompt injection — kontekst `decisions/DEC-001` historical audit trail) sugeruje naturalną kontynuację — przyszła praca (sekcja 8.5 II.13.6).

---

## 8.5. Future work

Niniejsza sekcja przedstawia dziesięć kierunków przyszłych prac, wszystkie świadomie wyłączone z aktualnego scope pracy z konkretnym uzasadnieniem (`02b_konspekt_v3_updates.md` § II.13). Punkty II.13.1–II.13.7 pochodzą z konspektu v3 FINAL (07.05.2026); punkty II.13.8–II.13.10 zostały dodane w delcie v3.1 (15.05.2026 i 16.05.2026) jako rezultat decyzji projektowych DEC-001 (rotacja domeny), DEC-002 (dodanie RQ5 cross-register) oraz decyzji Multi-turn chat scope z 16.05.2026.

### II.13.1. Walidacja farmaceutycznej poprawności merytorycznej

Autorka nie jest farmaceutką ani lekarzem. Praca mierzy *retrieval quality* i *faithfulness*, nie correctness odpowiedzi w sensie farmaceutyczno-klinicznym. Walidacja farmaceutyczna wymagałaby kohorty ekspertów farmaceutów / lekarzy + etyki badawczej + walidacji końcowych odpowiedzi RAG przez panel ekspertów na *Likert 5-scale* per dimension (factual correctness, completeness, safety advisory). Przyszła praca: deployment + walidacja kliniczna z partnerem instytucjonalnym (np. szpitalna apteka kliniczna, ośrodek doradztwa farmakologicznego), z formalnym protokołem zgodnym z wymogami etyki badawczej dla danych medycznych.

### II.13.2. Hard negative mining dla embeddera

BGE-M3 frozen — embedder nie jest fine-tunowany w tej pracy. Hard negative mining dla embeddera (kontrastywne dotrenowanie embeddera typu DPR na pharma-specific positives / negatives w stylu Karpukhina i in. [7]) dawałoby potencjalnie większą poprawę całościowego retrievalu niż sam fine-tuning rerankera, ale jest *pain pointem* od strony danych — wymaga jakości negatives na poziomie *human-curated* lub bardzo dobrze walidowanego LLM-judge w wymiarze *embedder-relevant negatives*, co w obecnym stanie jest osobnym wyzwaniem badawczym. Przyszła praca: contrastive embedder fine-tuning na medical-specific positives / negatives z 4-poziomową strategią negatives (analogicznie do hard negatives dla rerankera w Rozdziale 6).

### II.13.3. End-to-end clinical deployment

Praca jest *research artefaktem*; deployment w realnym klinicznym kontekście wymaga: (a) audytu farmaceutycznego końcowych odpowiedzi, (b) zgodności z RODO oraz Medical Device Regulation (MDR) UE jeśli system kwalifikuje się jako *medical device software*, (c) walidacji ekspertów farmaceutów / lekarzy z formalnym IRB approval, (d) audytu cyber-security pipeline'u, (e) infrastruktury High-Availability z SLA. Przyszła praca: pilot deployment z partnerem klinicznym (np. szpitalna apteka, ośrodek doradztwa) z protokołem wymaganym przez regulatora (URPL, EMA dla MDR jeśli aplikuje).

### II.13.4. Real-time drift detection na produkcyjnym ruchu

Bez prawdziwych użytkowników w ramach pracy dyplomowej nie ma *real-time traffic*. Simulated drift (RQ4) jest kontrolowanym proxy. Przyszła praca: integracja drift detectora z realnym RAG endpoint (np. wewnętrzny system instytucji partnerskiej, publiczny portal dla pacjentów) i monitoring drift na żywym ruchu z analizą rzeczywistych OOD events (nowe leki w rejestrze URPL, nowe wskazania, nowe interakcje, sezonowe wzrosty queries związane z konkretnymi schorzeniami). Wymaga partnera instytucjonalnego z istniejącym ruchem RAG.

### II.13.5. Cross-domain generalization

Praca trenuje i ewaluuje wyłącznie na farmakologii. Czy reranker dotrenowany na farmacji generalizuje na inne polskie domeny medyczne (kardiologia, onkologia, neurologia jako domeny pokrewne) lub na inne domeny specjalistyczne (prawo, finanse, technika) — otwarte pytanie. Przyszła praca: cross-domain evaluation na 2–3 dodatkowych polskich domenach specjalistycznych z manualnie walidowanymi mini-eval setami (50–100 par per domena), lub multi-task training rerankera na korpusach wielu domen z analizą *negative transfer* / *positive transfer* per domain pair.

### II.13.6. Adversarial robustness rerankera

Czy atakujący znający dotrenowany reranker może wygenerować *adversarial passages*, które są wysoko rerankowane mimo niskiej rzeczywistej relewacji query (*ranking attack*)? Naturalne powiązanie z wcześniejszą wersją tematu pracy (v2 prompt injection w polskim RAG, odrzucony 06.05.2026 — patrz `decisions/` historical audit trail). Przyszła praca: adversarial evaluation rerankera z wykorzystaniem narzędzi typu PyRIT / Garak adaptowanych do *retrieval attacks*, oraz adversarial training z augmentacją preference dataset o adversarial negatives.

### II.13.7. Cross-lingual transfer

Praca jest PL-only. Czy reranker dotrenowany na polskim transferuje na inne języki słowiańskie (czeski, słowacki, ukraiński, rosyjski) bez full retrainingu? Przyszła praca: cross-lingual eval na MIRACL multilingual benchmark [14] z fokusem na języki słowiańskie, lub *zero-shot transfer* dotrenowanego polskiego rerankera na czeski PIL corpus jako case study.

### II.13.8. Cross-language register transfer (NEW, dodane w delcie v3.1)

Czy *lessons learned* z polskiego ChPL↔Ulotka cross-register transferują do innych języków UE z analogiczną parą regulatorową? Każdy zarejestrowany lek w UE ma SPC (*Summary of Product Characteristics* — odpowiednik ChPL) oraz PIL (*Patient Information Leaflet* — odpowiednik Ulotki) w lokalnym języku zgodnie z wymogami EMA QRD. Naturalne pary: EN SPC↔PIL (UK / Ireland), DE Fachinfo↔Beipackzettel (Niemcy / Austria), FR RCP↔Notice (Francja / Belgia), ES Ficha Técnica↔Prospecto (Hiszpania). Przyszła praca: multi-lingual cross-register evaluation na MIRACL multilingual benchmark lub własny mini-corpus 100 par per language, z badaniem *transferability* metodologii cross-register pair scoring (4. protokół LLM-judge) między językami.

### II.13.9. Domain transfer cross-register (NEW, dodane w delcie v3.1)

Czy methodology cross-register transferuje na inne polskie domeny z dwoma rejestrami (profesjonalny ↔ laypersonowski / instruktażowy)? Kandydaci domenowi: prawo (kodeksy ↔ przewodniki dla obywateli — np. Kodeks pracy ↔ broszury PIP), medycyna educational (wytyczne PTPiN, wytyczne PTK ↔ materiały edukacyjne pacjenta z PoradnikZdrowia.pl), finanse (regulamin bankowy ↔ Q&A dla klientów), administracja (procedury KIO ↔ broszury obywatelskie). Przyszła praca: ablation cross-register methodology na 1–2 dodatkowych polskich domenach z dostępnym aligned corpus (lub konstrukcja takiego corpusu jako sub-contribution), z porównaniem direction asymmetry gap między domenami (czy gap lay→pro vs pro→lay jest stały *cross-domain*, czy domain-specific).

### II.13.10. Multi-turn chat evaluation (NEW, decyzja 2026-05-16)

**Implicit chat handling — IN scope.** Final RAG pipeline używa LlamaIndex `ChatEngine` z builtin *conversation memory* (rephrase follow-up jako standalone query przed retrieval). Reranker pipeline strukturalnie niezmieniony — uczy się single-turn query → passage relevance, conversation handling jest w upstream Query Construction layer (przepisanie follow-up *"a co z dawkowaniem dla niewydolności wątroby?"* na standalone *"dawkowanie sertraliny dla pacjentów z niewydolnością wątroby"* przed retrieval). Demo zakładka Gradio działa multi-turn out-of-the-box — pytanie + follow-up + follow-up obsługiwane bez modyfikacji rerankera.

**Multi-turn formal evaluation — OUT scope (future work).** 200 par gold standard są single-turn; RAGAS suite [13] (`context_precision`, `context_recall`, `faithfulness`, `answer_relevancy`) NIE testuje multi-turn coherence (czy follow-up rozumie kontekst poprzedniego turn-a, czy reranker zwraca passages spójne z całą historią konwersacji, czy odpowiedź jest *consistent* z poprzednią odpowiedzią). Przyszła praca: dodanie ~20 par multi-turn do eval set (z scenariuszami: clarification follow-up, deepening follow-up, lateral switch follow-up), RAGAS extension lub własne metryki *conversation coherence* (np. *context carry-over rate*, *follow-up resolution accuracy*, *consistency across turns*). Estymowany koszt: ~3–5 dni implementacji + walidacji. Decyzja podjęta 16.05.2026: implicit chat działa via LlamaIndex `ChatEngine`; formalne mierzenie multi-turn coherence dopisane jako future work w R8 po zamknięciu pięciu podstawowych RQ. Świadoma decyzja, nie *oversight* — odsuwane do *post-podstawowych-RQ scope* dla zachowania zarządzalnego scope pracy dyplomowej.

---

## 8.6. Wnioski końcowe

Niniejsza praca dostarcza kompletny, reprodukowalny pipeline MLOps do iteracyjnego dotrenowywania rerankera w polskojęzycznym systemie *Retrieval-Augmented Generation* w studium przypadku domeny farmakologii klinicznej. Wkład pracy obejmuje pięć niezależnych wymiarów (metodologiczny, inżynierski, artefaktowy, eksperymentalny, korpusowy / metodologiczny novel) — każdy z niezależnym artefaktem (framework LLM-as-judge dla polskiej farmakologii, otwarty pipeline DVC + MLflow + Prefect, dotrenowany reranker na HuggingFace, drift detection benchmark, aligned ChPL↔Ulotka corpus + cross-register methodology) i każdy z defensible self-standing value dla społeczności polskiego *Bio*NLP.

Pięć pytań badawczych zostało zoperacjonalizowanych z falsyfikowalnymi progami statystycznymi i raportowane będzie z pełną metodologią DS (3 random seeds, mean ± std, document-level splits, hyperparameter search Optuną, A/B gating w MLflow Model Registry). Wyniki empiryczne wszystkich pięciu hipotez raportowane są w Rozdziale 7 z odniesieniami do tabeli 8.1 w sekcji 8.3 niniejszego rozdziału.

Praca jasno deklaruje świadome ograniczenia (cztery kategorie: dataset, model, evaluation, external validity) — żadne ograniczenie nie jest *oversight*, każde jest udokumentowaną decyzją architektoniczną z konkretnym uzasadnieniem zwykle odsyłającym do ADR (`decisions/DEC-001`, `decisions/DEC-002`) lub do `02b_konspekt_v3_updates.md` § II.13. Sekcja future work obejmuje dziesięć konkretnych kierunków przyszłych prac, z których trzy (II.13.8–II.13.10) zostały dodane jako rezultat decyzji projektowych v3.1 (rotacja domeny, dodanie RQ5 cross-register, decyzja o multi-turn scope).

Niezależnie od końcowego empirycznego wyniku centralnego pomiaru retrievalu w cyklu 1 retreningu rerankera (RQ1 / H1), praca pozostaje wartościowa dla społeczności polskiego *BioNLP* — przede wszystkim w wymiarach metodologicznym (walidowany framework LLM-as-judge dla polskiej domeny specjalistycznej z falsyfikowalnym progiem Cohen's kappa), inżynierskim (reprodukowalny otwarty pipeline MLOps gotowy do adaptacji w innych polskich domenach specjalistycznych), korpusowym (pierwsza publicznie udokumentowana polska aligned ChPL↔Ulotka corpus jako standalone *publishable artifact*) oraz w wymiarze metodologii cross-register retrieval, która jest *novel* dla polskiego BioNLP nawet przy najbardziej konserwatywnym empirycznym wyniku rerankera.

Praca jest świadomie zaprojektowana z *defense scaffolding* dla negative-result scenarios (`thesis_elements/CLAUDE.md` § Defense scaffolding pkt 3) — pięć niezależnych wymiarów wkładu jest *expectation managed* już w design phase, nie ad-hoc po empirycznym wyniku eksperymentów. Ta świadoma redundancja kontrybucji jest *feature*, nie *bug* — odzwierciedla postawę *defensibility ponad novelty* z briefu autorki, zgodnie z preferencją promotora dla *engineering rigor* nad *over-claimed empirical magnitude*.

---

## Bibliografia (placeholder, ~5 referencji dla R8 future work)

> **Notka:** Bibliografia poniżej obejmuje wyłącznie referencje *unique do R8* — przede wszystkim cytacje literaturowe dla sekcji 8.5 future work (cross-language transfer, expertise style transfer, RAGAS) oraz baseline narzędzi MLOps powtarzające się z R5/R6. Pełna bibliografia ~30+ pozycji w rozdziale Bibliografia na końcu pracy. Wszystkie cytacje 🟡 do weryfikacji przez `citation-checker` przed final submission.

[1] SpeakLeash & AGH Cyfronet. (2024–2025). *Bielik 11B v3 — Polish open-weight instruction-tuned LLM*. Apache 2.0. HuggingFace: speakleash/Bielik-11B-v2.x lub successor v3. 🟡 Verify exact version + release date via citation-checker.

[2] Dadas S. (2024). *polish-reranker-roberta-v3*. HuggingFace model card sdadas/polish-reranker-roberta-v3. 🟡 Verify exact model identifier and release year via citation-checker.

[3] Chen J., Xiao S., Zhang P., Luo K., Lian D., Liu Z. (2024). *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*. arXiv:2402.03216. 🟡 Verify final venue.

[4] Evidently AI. (2022–2025). *Evidently — open-source ML monitoring and drift detection library*. Apache 2.0. https://github.com/evidentlyai/evidently. 🟡 Verify recommended citation format via citation-checker.

[5] Klaise J., Van Looveren A., Vacanti G., Coca A. (2021). *Alibi Detect: Algorithms for outlier, adversarial and drift detection*. Journal of Machine Learning Research, 22(181), 1–7. 🟡 Verify exact JMLR volume/page numbers via citation-checker.

[6] Chen A., Chow A., Davidson A., DCunha A., Ghodsi A., Hong S.A. et al. (2020). *Developments in MLflow: A System to Accelerate the Machine Learning Lifecycle*. DEEM '20: Proceedings of the Fourth International Workshop on Data Management for End-to-End Machine Learning. ACM. 🟡 Verify author list and venue via citation-checker.

[7] Karpukhin V., Oğuz B., Min S., Lewis P., Wu L., Edunov S., Chen D., Yih W. (2020). *Dense Passage Retrieval for Open-Domain Question Answering*. EMNLP 2020.

[8] Grabowski Ł. (2018). *On Identification of Bilingual Lexical Bundles for Translation Purposes: The Case of an English-Polish Comparable Corpus of Patient Information Leaflets*. In R. Mitkov, J. Monti, G. Corpas Pastor & V. Seretan (Eds.), *Multiword Units in Machine Translation and Translation Technology* (pp. 181–200). Current Issues in Linguistic Theory 341. John Benjamins. DOI: 10.1075/cilt.341.09gra. ✓ verified 2026-05-16.

[9] Cao Y., Shui R., Pan L., Kan M.Y., Liu Z., Chua T.S. (2020). *Expertise Style Transfer: A New Task Towards Better Communication Between Experts and Laymen*. ACL 2020.

[10] Devaraj A., Marshall I.J., Wallace B.C., Li J.J. (2021). *Paragraph-level Simplification of Medical Texts*. 🟡 Verify exact venue (NAACL 2021 vs EMNLP 2021) via citation-checker.

[11] van den Bercken L., Sips R.J., Lofi C. (2019). *Evaluating Neural Text Simplification in the Medical Domain*. WWW 2019. 🟡 Verify year (2019 vs 2020) via citation-checker.

[12] Zheng L., Chiang W.L., Sheng Y., Zhuang S., Wu Z., Zhuang Y. et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. NeurIPS 2023 Datasets and Benchmarks Track.

[13] Es S., James J., Espinosa-Anke L., Schockaert S. (2024). *RAGAS: Automated Evaluation of Retrieval Augmented Generation*. EACL 2024. 🟡 Verify exact venue (EACL 2024 vs arXiv preprint) via citation-checker.

[14] Zhang X., Thakur N., Ogundepo O., Kamalloo E., Alfonso-Hermelo D., Li X., Liu Q., Rezagholizadeh M., Lin J. (2023). *MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages*. Transactions of the Association for Computational Linguistics, vol. 11. 🟡 Verify exact volume and page range via citation-checker.

---

## Self-review checklist (per `thesis_elements/CLAUDE.md` § Workflow rozdziału krok 5)

- [ ] Wszystkie sekcje 8.1–8.6 zachowują academic style (3rd person, time-proofed, bez emoji w R8.docx, bez "obecnie" / "rosnące" / "brak" / "jedyny" / "żaden")
- [ ] Sekcja 8.2 (5-wymiarowa kontrybucja) zawiera explicit deklarację niezależności pięciu wymiarów oraz negative-result framing dla H1
- [ ] Sekcja 8.3 (status hipotez) zawiera placeholder z falsyfikowalnymi progami dla każdej z pięciu hipotez + sposób raportowania PASSED/FAILED/PARTIAL/INCONCLUSIVE
- [ ] Sekcja 8.4 (limitations) jest honest — explicit że eval set jest wąski (psych subset), świadoma decyzja architektoniczna z odniesieniem do DEC-001
- [ ] Sekcja 8.5 (future work) zawiera wszystkie 10 punktów II.13.X explicit (1-7 z v3 FINAL + 8-10 NEW z delty v3.1)
- [ ] Cite uncertainty flagging — 🟡 markery na cytacjach do weryfikacji (Bielik exact version, polish-reranker, BGE-M3 venue, Evidently citation format, Alibi Detect volume, MLflow author list, Grabowski exact title, Devaraj venue, van den Bercken year, RAGAS venue, MIRACL volume)
- [ ] Coherence z Defense scaffolding pkt 3 — paragraph minimalnie zaadaptowany do prose flow, zachowuje 5 wymiarów + niezależność oświadczenie
- [ ] Cross-references do R3 (limitations dataset bias § 3.10), R5 (architektura), R6 (modele), R7 (wyniki) — konsystentne
- [ ] Cross-references do `02b_konspekt_v3_updates.md` § II.13 dla future work
- [ ] Cross-references do `decisions/DEC-001` i `decisions/DEC-002` dla domain choice + RQ5 rationale
- [ ] PJATK format ready (nagłówki H1/H2/H3, tabela 8.1 numerowana, footnotes [N] gotowe do konwersji w Wordzie)

## Co dalej w tym rozdziale

1. **[Iteracja 8 — Finalization]** Po zamknięciu Iteracji 2–6 (eksperymenty rerankera + ablacje + cykle 2/3 + cross-register + drift + error analysis) wypełnić tabelę 8.1 status hipotez konkretnymi wynikami empirycznymi PASSED/FAILED/PARTIAL/INCONCLUSIVE.
2. **[Iteracja 8 — Finalization]** Uruchomić `/citations D:\diplomma\thesis_research\drafts\R8_podsumowanie.md` (deleguje do `citation-checker` subagent) dla weryfikacji wszystkich 14 referencji bibliografii — szczególnie phantom citations, błędne lata, błędne venue.
3. **[Iteracja 8 — Finalization]** Skopiować markdown do `thesis_elements/R08_podsumowanie.docx`, sformatować zgodnie z PJATK template (TNR 12pt, line 1.5, marginesy 2.5cm, footnotes IEEE 10pt, headings H1 bold 14pt / H2 bold 12pt — patrz Task 09 wymagania).
