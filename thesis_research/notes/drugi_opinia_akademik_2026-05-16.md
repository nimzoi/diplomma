# Druga opinia akademicka — drafty R3 / R4 / R5 (F1+F2)

**Data:** 2026-05-16
**Recenzent:** starszy pracownik naukowy PJATK (perspektywa komisji egzaminacyjnej obron inżynierskich)
**Drafty oceniane:**
- `thesis_research/drafts/R03_dane.md` (253 wiersze)
- `thesis_research/drafts/R04_eda.md` (290 wierszy)
- `thesis_research/drafts/R05_architektura.md` (297 wierszy, fragmenty 1–2 z 5)
**Konwencja:** 48-godzinny draft z placeholderami `{{...}}` i cytacjami roboczymi `[CYT: ...]`. Recenzja uwzględnia tę umowną niegotowość, ale ocenia również tę warstwę pracy, którą autorka zadeklarowała jako wpisaną z DATASET_CARD v0.6 bez placeholderów.

---

## 1. Streszczenie recenzenta

Trzy drafty świadczą o uporządkowanej koncepcji rozdziałów i o autentycznym pokryciu kanonicznych elementów Task 03–05; struktura R3 i R4 jest klasyczna, R5 zachowuje pełną hierarchię C4. Jednocześnie żaden z trzech rozdziałów nie nadaje się do oddania komisji w obecnym stanie. R3 zawiera nominalną sprzeczność arytmetyczną w pierwszej tabeli rozdziału, niezgodność rozmiaru gold-standardu z konspektem v3.2 oraz nieudokumentowane źródło dla 373 chunków `qa_gold`. R4 jest najlepiej skomponowany metodologicznie, lecz operuje na placeholderach w tabelach 4.3, 4.6 i 4.8, bez których odpowiedzi na pytania o pokrycie ekstrakcji cytacji, walidację taksonomii i dystrybucję długości tokenów nie istnieją. R5, z dwoma niedokończonymi fragmentami spośród pięciu, deklaruje proporcję 33,3 % i 37,5 % w obrębie tego samego rozdziału, a tabela 5.1 nie zgadza się ze szkieletem rysunku 5.2 co do liczby kontenerów. Wszystkie trzy rozdziały zawierają systematyczny codemix angielsko-polski naruszający dyrektywę „czysty polski akademicki" z `thesis_elements/CLAUDE.md`. Najsłabszym ogniwem obrony pozostaje brak inter-annotator agreement dla 200 par gold-standardu — pojedyncza anotatorka bez kappy nie wytrzyma rygorystycznego pytania promotora o procedurę walidacji benchmarku.

---

## 2. R3 — ocena szczegółowa

Rozdział wpisuje się w klasyczną strukturę Task 03: sekcje 3.1–3.6 odpowiadają kolejno celom i charakterystyce danych, źródłom, schematowi i strukturze plików, preprocessingowi, definicjom etykiet oraz aspektom prawnym i etycznym. Sekcja 3.7 pełni funkcję podsumowania reprodukowalności i wprowadzenia do R4. Pokrycie wymagań zadania jest pełne pod względem kategorialnym; redakcyjnie tekst utrzymuje formalny rejestr, choć z systematyczną interferencją angielszczyzny technicznej (terminy „scope creep", „garbage-in-garbage-out", „load", „post-hoc", „fair-use", „spot-check", „single-chunk"), z których część jest dopuszczalna jako *terminus technicus*, lecz dwadzieścia kilka wystąpień w jednym rozdziale przekracza próg redakcyjny przyjęty dla pracy obronnej.

Pierwsza tabela rozdziału (R03:21) deklaruje retrieval corpus liczący 8 022 chunki, podczas gdy suma siedmiu typów źródłowych wymienionych w tej samej komórce wynosi 7 622 (2 541 + 1 360 + 29 + 534 + 26 + 1 965 + 1 167). Po stronie metodologicznej jest to drobny błąd arytmetyczny, lecz po stronie obrony przed promotorem o mentalności MLOps — jest to *pierwsza liczba w pierwszej tabeli pierwszego rozdziału po wstępie*, czyli nominalny test sumienności edytorskiej, którego draft nie przechodzi. Fix nie zmienia tezy rozdziału, lecz pozostawienie tej rozbieżności jest nie do obrony.

Sekcja 3.5.3 zapowiada 200 par gold-standardu jako podstawę walidacji RQ1–RQ4, co stoi w wyraźnej sprzeczności z konspektem v3.2 (sekcja II.4.3, linie 21, 118 i 194: 110–160 par) oraz z operacyjnym dokumentem `PLAN_cele_i_kroki.md` (linia 138: 50–100 par). Z 60 par gotowych (UOKiK) i 50–100 manualnych autorka zadeklarowała 140 ręcznie anotowanych przez siebie, co stanowi 40-procentowy wzrost zakresu pracy manualnej w stosunku do konspektu. Brak adekwatnego ADR uzasadniającego tę zmianę. Z perspektywy obrony stwarza to dwa zagrożenia: (a) komisja porówna konspekt v3.2 (źródło prawdy w repozytorium) z draftem i dostrzeże rozbieżność, (b) realizm wykonania 140 par w trybie „weekend hyperfocus" jest bardziej napięty niż konspektowych 50–100. Rekomendacja akademicka — albo przyjąć MVP eval set 110 par i 200 jako stretch goal w R3, albo wydać DEC-005 dokumentujący ekspansję zakresu.

Sekcja 3.2 opisuje rodzinę UOKiK jako trzy komponenty: 60 par Q&A, 26 decyzji, osiem poradników PDF. Jednocześnie tabela 4.1 z R4 (wiersz `qa_gold`) deklaruje 433 chunki opisane jako „UOKiK Q&A FAQ + ekspansja RF FAQ". Różnica 373 chunków pochodzi z nieopisanego źródła. Termin „RF FAQ" pojawia się jedynie w tabeli licencji R3 (R03:211) bez metodyki pozyskania, definicji granic, opisu skali i licencji. Dla zadania, które explicit wymaga „How it was collected" (assignments/03.md, sekcja 7.1), jest to luka dokumentacyjna o charakterze blokującym. Audytor nie ma sposobu zweryfikowania pochodzenia 86 % tego, co rozdział nazywa zbiorem gold-standardu, bez zaglądania w kod.

Sekcja 3.5.3 opisuje wytyczne anotacji manualnej, lecz nie wspomina o agreement między anotatorami. To celowy wybór — pojedyncza anotatorka — który powinien być explicit oznaczony jako *known limitation* zgodnie z taxonomy 5-wymiarowej kontrybucji w R8. W obecnym kształcie rozdziału nie ma żadnej wzmianki o tej decyzji. Komisja egzaminacyjna o profilu MLOps zapyta: „jak walidujesz gold-standard bez kappy?", i odpowiedź „weekend hyperfocus" nie wystarczy. Zalecam dodać jedno zdanie: *„Anotacja wykonana przez pojedynczego anotatora (autorka); brak inter-annotator agreement świadomie raportowany jako znane ograniczenie w R8.2."*

Pozytywnie należy ocenić sekcję 3.4.2 (Wariant B), która stanowi rzeczowy i obroniony audit decyzyjny: arytmetyka 6 862 = 38,4 % zgadza się z DATASET_CARD, decyzje per-source są klasyfikowane, kategorie wykluczeń mają uzasadnienie. Sekcja 3.6 (etyka, PII, TDM exception) jest pełna i porządna w argumentacji prawnej; rozdział dot. TDM exception po nowelizacji z września 2024 jest wzorcowo udokumentowany. Sekcja 3.3.1 (codebook schemy `Chunk`) odpowiada wymaganiom „data dictionary" z Task 03 sekcja 1.3.

---

## 3. R4 — ocena szczegółowa

Rozdział R4 najlepiej z trzech wpisuje się w wymagania zadania — assignments/04.md eksplicytnie wymaga sekcji „Exploration", „Standardization", „Normalization", „Integration of Different Data Types" i „Documentation and Reproducibility", a tekst posiada wszystkie pięć (sekcje 4.2, 4.4, 4.5, częściowo 4.4.2, 4.6). Pod względem warsztatu analitycznego R4 jest najbardziej rzeczowy: sekcja 4.2.6 wprowadza BERTopic + UMAP + HDBSCAN jako *empiryczną walidację* taksonomii `Category`, co jest doskonałym argumentem defensywnym ([„walidujesz założenie danymi, nie z literatury"](thesis_elements/CLAUDE.md)). Sekcja 4.5.3 wprowadza TF-IDF jako *naive baseline*, świadomie odpowiadając na krytykę z *„Mirage of Halu Detection"*, co jest wzorowym przykładem zaszycia defense scaffolding już na poziomie EDA. Te dwa elementy zasługują na podkreślenie — komisja PJATK zauważy je jako oznakę naukowej dyscypliny autorki.

Niestety, znaczna część tej dyscypliny istnieje w trybie deklaratywnym. Tabela 4.3 (pokrycie ekstrakcji cytacji per `source_type`) ma osiem placeholderów na dziewięć wierszy. Tabela 4.6 (Top 10 klastrów BERTopic) ma czterdzieści placeholderów (10 klastrów × 4 pola). Tabela 4.8 (rozkład długości tokenów APT4) ma 27 placeholderów. Dodatkowo: mediana długości chunka (4.2.2), liczba kategorii per chunk (4.2.4), liczba klastrów BERTopic, silhouette score i alignment z `Category` enum (4.2.6) — wszystkie pozostają w postaci `{{}}`. Skutek dla obrony: rozdział w 40 % zależy od uruchomienia notebooka `eda_v0.ipynb`. Bez tego notebooka nie ma R4. To realistyczny ryzyk — 4–6 godzin pracy minimum, w tym debugowanie BERTopic + HDBSCAN dla 11 000 chunków na CPU autorki.

W sekcji 4.4.4 (harmonizacja etykiet kategorii) i 4.2.4 (rozkład multi-label) tekst trafnie identyfikuje dominację kategorii `finance_adjacent` (82,5 %) jako konsekwencję agresywnego tagowania słowami kluczowymi, a nie merytorycznej przewagi finansów w korpusie. Ten *bias* jest raportowany świadomie. Komisja może jednak zapytać: skoro 82,5 % chunków zawiera słownictwo finansowe, czy klasyfikator probe nie nauczy się detekcji „bag of finance words" zamiast detekcji halucynacji? Sekcja 4.5.3 (TF-IDF baseline) odpowiada częściowo na to pytanie, lecz nie wprost — zalecam dodać w 4.4.4 jedno zdanie wiążące tę obserwację z A1.5 ablation.

Sekcja 4.5.1 (BGE-M3 + L2 normalization) jest poprawna formalnie — wzór L2 normalizacji jest prawidłowy, uzasadnienie wyboru cosine similarity przez dot product na unit vectors jest standardowe. Sekcja 4.5.2 (APT4 token length) cytuje cytację `[CYT: Ociepa 2025 Bielik v3 APT4 arXiv:2604.10799]`. Notatka: arXiv 2604.10799 odpowiada kwietniowi 2026 r., a obecna data to 16 maja 2026; identyfikator jest *valid* per `notes/sources_z_v3.1_do_reuse_w_v3.2.md` linia 79 (verified 2026-05-16). Poprzedni recenzent oznaczył ją błędnie jako phantom „bo 2604 = future date" — tę diagnozę należy uznać za nieaktualną i wycofać. *Realne* phantom citations w R4 nie zostały zidentyfikowane.

Sekcja 4.6 wspomina kluczowe biblioteki (`pandas`, `matplotlib`, `seaborn`, `BERTopic`, `umap-learn`, `hdbscan`, `sklearn.feature_extraction.text`), lecz bez numerów wersji. Task 04 sekcja 6 jednoznacznie wymaga: „Clearly indicate software and library versions". Zalecam dodać krótki paragraf: *„Notebook EDA uruchomiony z `pandas` 2.2, `matplotlib` 3.9, `seaborn` 0.13, `BERTopic` 0.16, `umap-learn` 0.5, `hdbscan` 0.8, `scikit-learn` 1.5. Pełna lista pinów w `pyproject.toml` (lockfile via `uv lock`)."* Codemix angielsko-polski jest tu cięższy niż w R3 — terminy „right-skewed", „naive baseline", „single-chunk", „topic modeling", „back-end" pojawiają się bez kursywy lub bez odpowiednika polskiego.

Drobny błąd ortograficzny: R04:201 — „diakrityk" zamiast „diakrytyk". Plus drugi: R04:233 — *„warto rozważyć w przypadku H1 INCONCLUSIVE"* — termin „INCONCLUSIVE" pisany kapitalikami angielskimi w polskim akademickim zdaniu jest nieelegancki; zastąpić *„niejednoznaczny wynik"* lub całkowicie wykursywić jako termin techniczny.

---

## 4. R5 — ocena fragmentów 1–2

Fragmenty 1 i 2 R5 (sekcje 5.1 i 5.2) są poprawnie zorganizowane wedle metody C4. Sekcja 5.1 wprowadza uzasadnienie wyboru C4 jako standardu dokumentacji architektonicznej — argumentacja (industry standard, hierarchical zoom, technology-agnostic) jest racjonalna i wpisuje się w mentalność MLOps promotora. Sekcja 5.2 dostarcza poziomy Context, Container i Component, z trzema zoom-in'ami w 5.2.3 — to *minimalna kompletność* dokumentacji architektonicznej dla pracy inżynierskiej i jest defensible. Pozytywnie należy ocenić rozróżnienie *kontener C4* od *Docker container* w linii 74 — autorka dostrzega potencjalne nieporozumienie semantyczne. Niestety, samo to rozróżnienie nie ratuje dalszej spójności.

Tekst zawiera dwie wewnętrzne sprzeczności o charakterze blokującym. Po pierwsze (R05:9), sekcja 5.1 stwierdza: *„Z dziewięciu sekcji rozdziału trzy (5.4, 5.5, 5.6) opisują warstwę treningową i MLOps"* — co daje 3/9 = 33,3 %. Sekcja 5.9.3 (R05:285) deklaruje natomiast *„MLOps stanowi 37,5 % rozdziału (sekcje 5.4 + 5.5 + 5.6)"* — co implikuje 3/8 = 37,5 %, czyli rozdział ośmiosekcyjny. Liczba sekcji nie może być jednocześnie 9 i 8. Wybór jest binarny: albo zniknie sekcja (np. konsolidacja 5.7 do 5.6), albo skoryguje się procent. Po drugie (R05:76), tekst deklaruje *„jedenastu kontenerów w czterech logicznych grupach"*, podczas gdy poniżej wymienia *pięć* grup (Serving, Storage, Orchestration+Tracking, Observability, Application+UI), o sumie elementów 3+2+2+3+1 = 11. Liczba kontenerów (11) zgadza się z tabelą 5.1 (jedenaście wierszy), lecz szkielet rysunku 5.2 (R05:105–121) zawiera *MinIO* jako dwunasty kontener w grupie Storage, którego nie ma w tabeli. Konsekwencja: tabela i wykres dokumentują różną architekturę. Promotor MLOps zauważy to natychmiast — MinIO jako warstwa obiektowa S3-compat dla artefaktów MLflow *powinno* być policzone jako odrębny kontener; brak go w tabeli świadczy o niezsynchronizowaniu redakcyjnym.

Najpoważniejszą obciążeniem fragmentów 1–2 jest jednak rozdźwięk między obietnicą a realizacją MLOps. Sekcja 5.1 deklaruje 33,3 % rozdziału jako warstwę treningową i MLOps. W obecnym kształcie tekstu (F1+F2) MLOps istnieje w postaci sześciu jednoakapitowych blockquote'ów (sekcje 5.3–5.8), z czterema do sześciu zdaniami każda. To są wyraźne *placeholders*, nie pełne sekcje. Faktyczna obecność MLOps w obecnej wersji R5 wynosi około 5 %, nie 33 %. Jeśli draft zostanie oddany jako kompletny R5, recenzent natychmiast zauważy lukę. Honest framing wymaga dodania w *opening note* informacji: *„Fragmenty 1–2 z 5; sekcje 5.4–5.6 (MLOps part 1–3) zostaną rozwinięte w fragmentach 3–5."* — co autorka już zrobiła w linii 3, lecz w sposób umiarkowany. Należy to wzmocnić.

Codemix angielsko-polski osiąga w R5 swoje maksimum w tych trzech draftach. Terminy „blackbox", „boundary", „deployable services", „production-ready", „single-machine deployment", „high-throughput LLM serving", „cross-container", „orchestration", „runtime", „artifact storage" pojawiają się bez polskich odpowiedników. Dla rozdziału centralnego pracy, który stanowi *vitrine* obrony, jest to redakcyjnie nieakceptowalne — Magda w innym wątku konwersacji wyraziła wprost „piszesz jak na haju" w odniesieniu do podobnych fragmentów. Rekomenduję głęboki run-through polonizacyjny przed oddaniem.

Cytacje robocze w R5 są w większości weryfikowalne (Brown 2018 C4, Chen 2024 BGE-M3 arXiv:2402.03216, mDeBERTa HF, Uğur 2025 Guided Decoding arXiv:2509.06631, Liang & Wang Dec 2025, Dubanowska EMNLP 2025). Cytacja Ociepa 2025 Bielik v3 APT4 arXiv:2604.10799 jest *valid* per source-of-truth `sources_z_v3.1_do_reuse_w_v3.2.md` — poprzednia diagnoza o phantomowości tej cytacji była błędna i należy ją wycofać.

---

## 5. Cross-chapter consistency

Pomiędzy trzema draftami zachodzi pojedyncza istotna niezgodność liczbowa: rozmiar eval set 200 par (R3 sekcja 3.5.3, R5 sekcja 5.2.1 linia 29 oraz 5.2.3 linia 168) versus 110–160 par w konspekcie v3.2 (sekcja II.4.3) versus 50–100 par hand-annotated w `PLAN_cele_i_kroki.md` (linia 138). Trzy źródła prawdy konkurujące w obrębie tego samego repozytorium, bez ADR rozstrzygającego rozbieżność. Niezgodność ta naraża pracę na ambush przez komisję — promotor, czytając konspekt v3.2 zatwierdzony ostatnim ADR, oczekuje 110–160 par i nie zaakceptuje cichego skoku do 200 bez uzasadnienia w trybie *decision before output*.

Druga niezgodność dotyczy klasyfikacji `qa_gold`: R3 sekcja 3.2 opisuje UOKiK Q&A jako 60 par, podczas gdy R4 tabela 4.1 deklaruje 433 chunki jako „UOKiK Q&A FAQ + ekspansja RF FAQ" bez metodologii ekspansji. Brakuje sekcji w R3 dokumentującej źródło, skalę i licencję 373 chunków dodanych do `qa_gold`. To gap dokumentacyjny na poziomie blokującym dla obrony Task 03.

Pozytywnie należy odnotować spójność terminologii między R3 i R4 w zakresie trzech kluczowych konceptów: trójdzielnej roli korpusu (retrieval / training / eval), nomenklatury `source_type` (9 typów spójnie wymienianych), oraz arytmetyki Wariant B (6 862 dropniętych = 38,4 % z 17 862 → 11 000). Oba rozdziały odwołują się do tego samego źródła prawdy (DATASET_CARD v0.6) i zachowują liczby — pojedyncza wyrwa w R3 Tab 3.1 (8 022 vs 7 622) jest izolowana, nie systemowa. Konsekwencja: po fixie tej jednej liczby, spójność matematyczna R3↔R4 jest zachowana.

---

## 6. Top 5 RED FLAGS dla obrony

1. **Brak inter-annotator agreement dla gold-standardu (severity: KRYTYCZNA).** Pojedyncza anotatorka (autorka) bez kappy lub jakiejkolwiek innej miary inter-annotator reliability dla 140 par manualnie anotowanych. R3 sekcja 3.5.3 milczy o tej decyzji. Promotor MLOps zapyta: *„Skąd wiesz, że twoje etykiety są poprawne? Czy validujesz operacjonalne wytyczne?"* — i brak odpowiedzi jest defensively fatal. Minimum: explicit acknowledgment + flag w R8 limitations + mitygacja (np. self-rev po tygodniu na 30 par jako quasi-test re-test reliability).

2. **Niezgodność rozmiaru eval set 200 par vs konspekt 110–160 par bez ADR (severity: WYSOKA — scope creep, decision protocol violation).** 40-procentowy wzrost zakresu pracy manualnej bez zalogowania decyzji w `decisions/`. Narusza wzorzec *Decision before output* z `CLAUDE.md`. Komisja, porównując dokumenty repozytorium, dostrzeże rozbieżność i zapyta o uzasadnienie. Fix: albo cofnąć draft do 110 par + 200 stretch, albo wydać DEC-005.

3. **Nieudokumentowane źródło 373 chunków `qa_gold` (RF FAQ ekspansja) (severity: WYSOKA — Task 03 documentation gap).** Tabela R04:31 deklaruje 433 chunki w `qa_gold` ze wskazaniem „UOKiK Q&A FAQ + ekspansja RF FAQ", podczas gdy R3 sekcja 3.2 dokumentuje tylko 60 par UOKiK. Brak opisu metodologii pozyskania, granic zbioru, licencji i sposobu walidacji 86 % chunków `qa_gold`. Task 03 wymaga explicit „How it was collected" — to wymóg blokujący.

4. **Arytmetyczna sprzeczność R3 Tab 3.1: 8 022 vs 7 622 (severity: ŚREDNIA-WYSOKA — sumienność edytorska).** Pierwsza tabela rozdziału po wstępie, dotyczy kluczowej liczby (retrieval corpus). Sumowanie siedmiu typów daje 7 622, deklaracja: 8 022, off-by-400. Drobny matematyczny błąd, lecz w pierwszej linii pierwszej tabeli pierwszego rozdziału metodologicznego — to test sumienności, którego draft nie przechodzi.

5. **R5 podwójna sprzeczność: 33,3 % vs 37,5 % MLOps + 11 vs 12 kontenerów (severity: ŚREDNIA — coherence within central chapter).** Wewnętrzna sprzeczność procentowa (sekcja 5.1 vs 5.9.3) oraz niezsynchronizowanie tabeli 5.1 (11 kontenerów) z rysunkiem 5.2 (12 kontenerów z MinIO). Rozdział centralny pracy nie może zawierać podstawowych sprzeczności liczbowych — jest *vitrine* obrony i bezpośrednio testowany przez komisję. Plus: MLOps zadeklarowane jako 33,3 % rozdziału jest w obecnym tekście niemal nieobecne (1-akapitowe placeholdery sekcji 5.3–5.8).

---

## 7. Rekomendacja per rozdział

**R3 — NEEDS WORK (estymata fix: 2–3 h).**
Drobne, lecz cumulatively blokujące poprawki: (a) korekta tabeli 3.1 (8 022 → 7 622), (b) dodanie paragrafu RF FAQ ekspansja w sekcji 3.2 z metodologią pozyskania, (c) eksplicytne zdanie o braku inter-annotator agreement w sekcji 3.5.3 z flagą do R8, (d) reconciliacja eval set (200 vs 110–160) przez ADR lub korektę draftu, (e) polonizacja codemixu (run-through 30–45 min). Po tych poprawkach R3 będzie obronny dla Task 03. Bez nich — komisja zatrzyma się na Tab 3.1.

**R4 — NEEDS WORK (estymata fix: 5–7 h).**
Krytyczna ścieżka to uruchomienie notebooka `eda_v0.ipynb` przed oddaniem — bez wartości w tabelach 4.3, 4.6, 4.8 rozdział nie istnieje materialnie. Drugorzędne: (a) wersje bibliotek w sekcji 4.6 (5 min), (b) ortografia „diakrityk" → „diakrytyk" (5 sek), (c) polonizacja codemixu (45 min), (d) jedno zdanie wiążące dominację `finance_adjacent` (82,5 %) z A1.5 TF-IDF baseline (5 min). Pod względem warsztatu analitycznego R4 jest najlepszy z trzech — sekcja 4.2.6 BERTopic walidacja taksonomii to wzorzec defense scaffolding.

**R5 (fragmenty 1+2) — NEEDS WORK z elementami REWRITE (estymata fix F1+F2: 2 h; pełna realizacja F3-F5: dodatkowe 8–12 h).**
Konieczne fixy F1+F2: (a) zharmonizować liczbę sekcji i procent MLOps (9 sekcji → 33,3 % lub 8 sekcji → 37,5 %, jednoznacznie), (b) zharmonizować tabelę 5.1 i rysunek 5.2 co do liczby kontenerów (11 lub 12, jednoznacznie), (c) wzmocnić *opening note* o jasne oznaczenie „F1+F2 only — F3-F5 in progress", (d) głęboka polonizacja codemixu (warianty: „blackbox" → „czarna skrzynka", „boundary" → „granica systemu", „runtime" → kursywa, „deployable services" → „samodzielnie wdrażalne usługi"). Realizacja F3-F5 to oddzielny milestone — bez niej R5 jest niekompletny do oddania jako centralny rozdział pracy. Task 05 wymaga explicit dyskusji „common types of IT architectures" (monolith vs microservices vs cloud-native), która znajdzie się w 5.9.2 i obecnie istnieje jako blockquote.

---

## 8. Trzy killer questions, których nie obronimy teraz

**Pytanie 1 (promotor o profilu MLOps): „Pani Magdo, opisuje pani 200 par gold-standard jako podstawę walidacji RQ1–RQ4. Czy mogę zobaczyć protocol anotacji, inter-annotator agreement i procedurę adjudikacji?"**
Obecnie nie ma odpowiedzi. R3 sekcja 3.5.3 wymienia trzy wytyczne operacyjne (entailment / contradiction / neutral), lecz nie ma procedury adjudikacji, nie ma drugiego anotatora, nie ma kappy. Single-annotator gold-standard 200 par bez self-rev test-retest reliability jest defensywnie słaby. Mitygacja na chwilę obrony: explicit acknowledgment + 30-par self-rev po tygodniu (Cohen's kappa intra-rater ≥ 0.70) + flag w R8.2 limitations. Bez tej procedury — pytanie ułożone w ten sposób jest fatalne.

**Pytanie 2 (komisja egzaminacyjna, mentalność konserwatywna): „Konspekt v3.2 deklaruje 110–160 par jako eval set. Tutaj widzę 200. Skąd ta zmiana, kiedy została zalogowana, i czy mieści się w timeframe oddania pracy?"**
Obecnie nie ma odpowiedzi w postaci ADR. Należy albo cofnąć liczbę w drafcie, albo wydać DEC-005 retrofitting zmianę z uzasadnieniem (np. „60 UOKiK + 140 hand-annotated by autorka pokrywa lepiej rare halu types — paragraph_mis_citation oraz temporal_drift w domenach RODO/telekom — niedoreprezentowanych w UOKiK distribution"). Bez ADR — komisja ma podstawę do zarzutu o nierzetelność audit trail.

**Pytanie 3 (promotor o MLOps mindset, czytając R4): „Pani Magdo, tabela 4.4 pokazuje że 82,5 % chunków jest oznaczonych jako `finance_adjacent`. Czy probe nie nauczy się klasyfikacji domeny zamiast detekcji halucynacji?"**
Obecnie odpowiedź jest pośrednia — sekcja 4.5.3 wprowadza TF-IDF jako naive baseline, ale linkowanie *„82,5 % finance_adjacent → A1.5 TF-IDF baseline jako kontrola spurious correlation"* nie jest wprost zapisane. Promotor MLOps natychmiast zobaczy to jako *„label leakage przez tagowanie heurystyczne"*. Mitygacja: explicit jedno zdanie w 4.4.4 wiążące tę obserwację z A1.5 ablation w R7. Plus drugi argument: BERTopic empirical alignment (4.2.6) pokaże czy klastry semantyczne korespondują z `Category` enum — jeśli tak, taksonomia jest *post-hoc walidowana* danymi (per 4.2.6 ostatni paragraf). Ten argument jest dobry, lecz uzależniony od wyników notebooka, które obecnie są placeholdery.

---

## Konkluzja recenzenta

Trzy drafty są w stanie *zaawansowanej szkicowości* — struktura jest poprawna, źródła prawdy są wyraźne (DATASET_CARD v0.6, konspekt v3.2, decisions/DEC-003), istnieje defense scaffolding (BERTopic walidacja, TF-IDF baseline, Wariant B audit, 5-wymiarowa kontrybucja). Lecz każdy z trzech rozdziałów ma blokujące lukę przed oddaniem komisji: R3 sprzeczność arytmetyczna i RF FAQ gap, R4 placeholders w trzech tabelach krytycznych dla głównych roszczeń, R5 wewnętrzne sprzeczności liczbowe i nieobecność MLOps w obecnym tekście pomimo zadeklarowanego 33 %. Najwyższym priorytetem do fixu pozostaje uruchomienie notebooka EDA (R4 nie istnieje bez tego), reconciliacja eval set 200 vs 110–160 (decyzja organizacyjna), oraz wprowadzenie zwięzłej deklaracji *„single-annotator gold standard, brak inter-annotator agreement, flag w R8"* w R3.

Pozytywnym wnioskiem jest, że żaden z draftów nie wymaga *rewrite* od zera. Wszystkie fixy mieszczą się w 8–12 godzinach pracy redakcyjnej + 4–6 godzin pracy obliczeniowej (notebook EDA). Po tych nakładach trzy rozdziały będą obronne dla Task 03–05. Recenzja niniejsza nie zastępuje peer-review promotora, lecz wskazuje na specyficzne zarzuty, których komisja egzaminacyjna PJATK z perspektywy konserwatywnej i rygorystycznej najpewniej postawi.
