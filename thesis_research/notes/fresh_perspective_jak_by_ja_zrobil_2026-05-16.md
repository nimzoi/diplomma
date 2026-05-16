# Fresh perspective — jak BY ja zrobił R3 + R4 + R5

**Reviewer:** doświadczony promotor PJATK Wydziału Informatyki (Data Science, NLP/MLOps), 10+ lat, fresh look bez bias do istniejących draftów
**Data:** 2026-05-16
**Adresat:** Magdalena Sochacka (autorka)
**Charakter dokumentu:** *„gdybym ja brał ten temat dziś — jak BY zaprojektował R3/R4/R5"* (NIE krytyka istniejących draftów)

---

## 1. Pierwsze wrażenie (5 zdań)

Temat zawiera unikalny *moat* — wąską niszę z czterema definitywnymi ograniczeniami (polski + citation-grounded + consumer rights + hidden-states probe na polish LLM) oraz defensible audit trail trzech pivotów udokumentowanych w decisions/. Skala pracy plasuje się jednak na pograniczu *inżynierki rozwiniętej do magisterki* — trzy artefakty HuggingFace, pełen stack MLOps, 3-tier verifier, continuous improvement loop i 200 par manual gold to materiał na zespół, nie na jedną osobę w jednym semestrze. Gdybym BY pisał ten temat z czystą kartką, R3-R4-R5 traktowałbym jako *trzy warstwy jednej narracji* (źródła → reprezentacje → architektura), z konsekwentnymi forward refs między nimi i jednolitą terminologią. R5 BY uczynił *kontraktem z czytelnikiem* — co rzeczywiście musi działać do obrony, oddzielonym od *technologicznego katalogu ambicji*. Największa szansa na 30/30 punktów łącznie leży w spójnej narracji warstwowej z jednym motywem przewodnim: *„semantyczna struktura korpusu implikuje decyzje architektoniczne pipeline'u, a continuous improvement loop zamyka pętlę feedback do danych"*.

---

## 2. R3 Dane — jak ja BY zrobił

### 2.1 Outline (jak BY) — 6 sekcji

Sześć sekcji, każda 8-12 stron Worda, sumarycznie ~50-60 stron:

1. **3.1 Cele rozdziału i mapa danych** (2-3 strony) — krótka roadmap rozdziału + Tabela 3.1 *trzy role korpusu (retrieval / training / eval)* + Figura 3.1 *„mapa danych"* (diagram blokowy: 6 rodzin źródłowych → unifikowany Chunk → 3 role w pipeline'ie)
2. **3.2 Źródła danych — pochodzenie i uzasadnienie wyboru** (10-12 stron) — sześć rodzin źródeł (ustawy PL / dyrektywy UE / orzecznictwo / decyzje UOKiK / poradniki PDF / real questions z forów) z osobnymi paragrafami uzasadnienia *dlaczego TO źródło* (nie tylko *co* w nim jest); macierz licencji jako Tabela 3.2; dla każdej rodziny: domena, rozmiar, metoda scrape, dwa-trzy reprezentatywne przykłady chunków jako bloki tekstu
3. **3.3 Schemat danych, format plików, struktura repozytorium** (6-8 stron) — codebook `Chunk` (Tabela 3.3); enum `SourceType` + `Category` jako odrębne podsekcje; struktura katalogów; konwencja `chunk_id`; audit trail przez sidecary `_manifest.json`
4. **3.4 Pipeline pozyskania i preprocessing** (8-10 stron) — *narracyjny* opis pipeline'u, NIE tylko polecenie CLI: load → normalize → extract citations → deduplicate → filter → halu inject; każdy etap z motywacją + alternative considered; Wariant B cleanup jako osobna podsekcja z *empirical evidence triggerem*
5. **3.5 Etykiety, anotacja, jakość gold standard** (10-12 stron) — definicje 5 typów halu + 3-klasowego NLI + ich mapowanie (po co dwa zestawy etykiet?); 200 par gold protokół anotacyjny (wytyczne, sesje, self-review, IAA jako known limitation); silver labels metodyka; sample/stratifikacja train/val/test
6. **3.6 Etyka, prawo, reprodukowalność** (4-6 stron) — TDM exception Wrzesień 2024, RODO art. 17, anonimizacja PII, mandatory disclaimer (forward ref do R5), checklist reprodukowalności (commit hash + seed + sidecary)

### 2.2 Co BY dodał (nieobecne w current)

1. **Reprezentatywne listings chunków per typ źródłowy (Listings 3.1-3.6).** Komisja egzaminacyjna ZAWSZE pyta *„pokaż mi jeden chunk"*. Sześć bloków po 5-12 linii (ELI ustawa z `art. X ust. Y`, EUR-Lex dyrektywa z preambułą, orzeczenie TSUE z sentencją, decyzja UOKiK z numerem RPZ, poradnik PDF z extracted section, real consumer question z forum) zamyka 80% pytań komisji o jakość danych zanim padną. Listings ZNACZNIE skuteczniejsze niż tabela statystyczna.
2. **Mini case study jednego pytania end-to-end (sekcja 3.7 jako *spina rozdziału*).** Wybór jednego konkretnego pytania UOKiK Q&A (np. *„Ile mam dni na odstąpienie od umowy zawartej przez Internet?"*) z pełną ekspozycją: surowy HTML z portalu → po normalizacji → wycięty `Chunk` ze schemą → przykładowa mutacja halu *factual_fabrication* → przykładowa mutacja *negation_flip* → linkowane evidence chunk z ISAP art. 27 UPK. Daje czytelnikowi *namacalne* zrozumienie wszystkich abstrakcji rozdziału w jednym przykładzie — to jest *spina* rozdziału.
3. **Tabela „Decyzje konstrukcyjne korpusu" (Tabela 3.X, 4-5 wierszy).** Format: *Decyzja → Alternatywa rozważana → Rationale → Trade-off*. Wiersze: (a) *Wariant B strict policy* vs *zachowanie pełnego v0.4*; (b) *6 rodzin / 9 source_types* vs *flat structure*; (c) *unifikowany Chunk schema* vs *per-source classes*; (d) *5-type halu taxonomy* vs *RAGTruth 4-type*; (e) *200 par single-annotator gold* vs *multi-annotator IAA*. Komisja widzi *autorski proces myślenia*, nie tylko wynik.
4. **Honest limitation paragraph (zamykający 3.5).** Eksplicytne: *„Korpus jest single-annotator gold standard ograniczony do 200 par. Brak IAA wyklucza standardowy inter-annotator reliability metric. Zbiór jest reprezentatywny dla domeny consumer-core, ale niedoreprezentowany w sub-domenach telekom (n=79) oraz unfair practices (n=47)."* Sam *zgłaszasz* limitację — promotor czuje że masz świadomość, nie musi tego wyciągać przy obronie.
5. **„Prior art datasetów" paragraf w 3.2.** *„Korpus jest pierwszym publicznie udokumentowanym polskim citation-grounded RAG benchmarkiem; jest komplementarny wobec PIRB (retrieval) oraz AggTruth (halu English-only) i różnicuje się od UOKiK ARBUZ AI (closed-source operational tool)."* Pozycjonuje korpus w polish landscape *zanim* czytelnik zapyta *„czy to nie powtarza..."*.

### 2.3 Co BY usunął/uciął (over-engineering)

1. **Powtarzanie pełnych statystyk DATASET_CARD.md w treści R3.** Korpus *jest* tym data card — w R3 wystarczy referencja + 1-2 zsumowane liczby (11k chunks, 5,4k halu pairs, 200 par gold). Pełen breakdown per source_type BY przeniósł do R4 (gdzie *jest* eksploracja), w R3 zostawił jedną *summary* tabelę bez per-source liczb.
2. **Drobiazgowe wyjaśnienia narzędzi scrape (playwright-stealth, F5 BIG-IP ASM bypass, brotli decode).** Ciekawe inżyniersko, ale w R3 *przeszkadza w narracji*. Skróciłbym do: *„dla części źródeł wymagana była konfiguracja headless browser z user-agent rotation ze względu na zabezpieczenia WAF; szczegóły implementacyjne w Załączniku A"*. Sekcja techniczna do appendix.
3. **Sekcja „pivot history" / „obecny stan po DEC-003".** Pivot history należy do `decisions/`. W rozdziale akademickim wystarczy: *„Korpus został zbudowany dla niniejszej pracy w okresie maj 2026, w domenie polskie prawa konsumenta wybranej z motywacji opisanych w R1.2"*. Komisja NIE chce czytać o pivotach jako triumfie procesu — chce zobaczyć *gotowy korpus*.
4. **Pełna dokumentacja zawartości `metadata` dict per source_type.** Wystarczy *„pole metadata zawiera source-specific atrybuty; pełna lista w `schemas.py`"*. Reszta to engineering noise.

### 2.4 Top 3 różnice vs current draft

1. **Narracja przed tabelami.** BY zmienił układ: każda sekcja zaczyna 2-3 paragrafy *narracji* wyjaśniającej *po co* i *jak*, dopiero potem tabela z faktami. Tabele BY traktował jako referencyjne uzupełnienie, NIE jako primary content channel.
2. **Mini case-study jako *spina* rozdziału.** Jedno konkretne pytanie konsumenckie przeprowadzone przez WSZYSTKIE elementy korpusu (źródło → chunk → mutacja → ground truth) — daje komisji jeden ukonkretniony obraz całości i zamyka 80% pytań *„a jak to wygląda w praktyce?"*.
3. **Six rodzin źródeł zamiast dziewięciu typów źródłowych.** To NIE jest semantyczna redukcja — to *redukcja kognitywna* dla czytelnika. Komisja Data Science łatwiej zapamięta sześć kategorii niż dziewięć. Grupowanie: ustawy PL / dyrektywy UE / orzecznictwo / decyzje UOKiK / poradniki PDF / real questions z forów (encyclopedic i qa_gold/qa_raw mieszczą się w pierwszym i ostatnim grupowaniu z explicit notą o sub-kategoriach).

---

## 3. R4 EDA — jak ja BY zrobił

### 3.1 Outline (jak BY) — 6 sekcji

Sześć sekcji, ~25-35 stron Worda:

1. **4.1 Wprowadzenie + cele eksploracji** (1-2 strony) — krótkie postawienie: *po co eksplorujemy?* Odpowiedź na trzy pytania kluczowe: (a) czy korpus jest *reprezentatywny* dla domeny? (b) czy *zbalansowany* dla treningu probe? (c) czy Wariant B cleanup *nie zniekształcił* dystrybucji?
2. **4.2 Eksploracja struktury źródeł i rozkładów** (8-10 stron) — rozkłady source_type + długości chunków + pokrycia cytacji; każda podsekcja z 1 figurą + 1 tabelą + *empirical findings* explicit (nie tylko liczby)
3. **4.3 Walidacja taksonomii przez topic modeling** (6-8 stron) — BERTopic + UMAP + HDBSCAN; *post-hoc walidacja* etykiet Category. **To ma być centralna sekcja R4 z największym intellectualnym wkładem** — nie tylko statystyki, ale dowód, że taksonomia odpowiada semantyce danych
4. **4.4 Wariant B audit — wpływ czyszczenia na rozkłady** (4-5 stron) — before/after rozkłady; argumentacja świadomego stronniczości; *honest paragraf* o utracie ~7k chunków i konsekwencjach dla generalizacji
5. **4.5 Standaryzacja danych** (4-5 stron) — NFC normalizacja + unifikowany schemat + ISO 8601 + harmonizacja Category
6. **4.6 Normalizacja reprezentacji wektorowych** (4-6 stron) — BGE-M3 + L2 + cosine similarity uzasadnienie; balans klas w halu pairs; krótka nota o TF-IDF jako naive baseline

### 3.2 Co BY dodał (wizualizacje + clustering)

1. **BERTopic jako CENTRALNY argument walidacyjny (sekcja 4.3, NIE placeholdered podsekcja).** *Post-hoc* walidacja taksonomii Category przez clustering to *jeden z najmocniejszych intellectualnych argumentów* dla R4 — bez tego R4 to *deskrypcyjny EDA*, z tym to *walidacyjny EDA*. Konkretnie: BERTopic na BGE-M3 embeddings → top 10-15 klastrów z dominującymi terminami → mapping klaster → dominująca Category → chi-square test alignment. Komisja Data Science *uwielbia* topic modeling jako evidence-based walidację taksonomii.
2. **Heatmap korelacji source_type × Category (14×9 matrix).** Jedno wykres pokazuje *dwa wymiary* korpusu jednocześnie i pokazuje semantyczne związki *empirycznie* — czy `legal_statute` koreluje z `consumer_contract`? Czy `qa_raw` z `consumer_return_refund`? To poziom analizy oczekiwany w pracy DS.
3. **Violin plot długości chunków per source_type (zamiast boxplot).** Violin plot pokazuje *kształt* rozkładu (bimodal/unimodal). Dla source_type `qa_raw` (bimodal: krótkie pytania + długie wątki forum) violin plot daje natychmiastową diagnozę, której boxplot nie zapewnia.
4. **UMAP 2D scatter z overlay decyzji Wariant B.** Standardowy UMAP scatter dobry, ale dodanie overlay *„te ~7k chunków zostały odrzucone przez Wariant B"* (kolor inny) pokazuje wizualnie *gdzie* w przestrzeni semantycznej leżały odrzucone elementy. Empiryczny argument *„cleanup nie usunął losowych chunków, tylko odrębne sub-klastry"*.
5. **Sekcja „Anomalie i edge cases" (2-3 strony, w 4.2).** *„W trakcie eksploracji zidentyfikowano N anomalii: K chunków z długością <50 znaków (artefakty scrape), M chunków z >5000 znaków (długie orzeczenia, fragmentation strategy reconsidered), P chunków z duplicate citations (chunked ustawy z redundant headers)."* Daje *forensic feel* — komisja czuje że nie ufasz danym blindly.
6. **Stratifikacja train/val/test JAKO osobna podsekcja z testem chi-square.** Stratifikacja jest istotną konstrukcyjną decyzją. Pokazać: train/val/test rozkład per source_type + per category + chi-square test że splity są statystycznie homogenne. Komisja Data Science zaczyna od pytania *„czy split nie wycieka?"* — lepiej preempt.
7. **Word clouds per Category (jako 6-figurowy grid w appendix).** Niski koszt produkcji (matplotlib + wordcloud), wysoki visual impact. `consumer_credit` zdominowany przez kredyt/RRSO/oprocentowanie, `consumer_dispute_resolution` przez ADR/mediacja/Rzecznik. Komisja DS uwielbia word clouds dla NLP.

### 3.3 Co BY usunął

1. **Sekcja tokenizator APT4.** APT4 to wybór *modelu* (R6), nie *danych* (R4). W R4 wystarczy *„rozkład długości w tokenach BGE-M3 (tokenizator retrieval) — szczegóły tokenizera Bielik APT4 w R6"*. Mieszanie tokenizatorów embeddera i generatora w R4 myli czytelnika.
2. **TF-IDF baseline jako dedykowana podsekcja.** TF-IDF jest *baseline modelu* (R6), nie *normalizacji danych* (R4). Wystarczy jedna nota *„embeddings BGE-M3 są normalizowane L2; dla porównania w R6 implementowana jest reprezentacja sparse TF-IDF jako naive baseline per Mirage of Halu Detection critique"*.
3. **Powtarzanie tabel z R3.** R4 może powtarzać tabelę source_type + citation coverage — te liczby należą do *jednego* miejsca. W R4 ma być *interpretacja* + *wizualizacja*, NIE re-listing tabeli z R3.
4. **„Decyzje konstrukcyjne pipeline'u" w treści sekcji 4.2.** Te wnioski należą do R5. R4 BY rozdzielił czystą eksplorację (*„zaobserwowano X"*) od decyzji architektonicznych (*„dlatego w R5 zdecydowano Y"*).

### 3.4 Top 3 różnice vs current draft

1. **BERTopic jako *centralny* element walidacji jakości, NIE jedna sekcja z placeholderami.** Obecny 4.2.6 jest zarysowany ale placeholdered. BY wybudował to *pierwsze* w sprincie — to *najmocniejszy* intellectualny argument dla rozdziału.
2. **Heatmap source_type × Category zamiast osobnych tabel.** Dwa wymiary korpusu w jednej wizualizacji = lepsza ROI dla czytelnika.
3. **Sekcja „anomalie i edge cases".** *Forensic mindset* w pracy DS jest wysoko ceniony. Pokazać że *patrzysz* na dane, nie tylko *agregujesz*.

---

## 4. R5 Architektura — jak ja BY zrobił (CENTRALNY)

### 4.1 Outline (jak BY) — 7 sekcji, NIE 9

Centralny rozdział: 50-70 stron Worda, ~25-30% objętości całej pracy.

1. **5.1 Wprowadzenie + wymagania architektoniczne** (4-5 stron) — *przed metodą C4* postawić listę wymagań niefunkcjonalnych (latency, dostępność, observability, reprodukowalność, single-machine constraint, license compliance, fail-closed dla legal advice); macierz *wymagań × kontenerów* pokazująca jak architektura *odpowiada* na każde wymaganie
2. **5.2 Trzy widoki statyczne — C4 Context / Container / Component** (12-15 stron) — sekcja jak obecna, ale z naciskiem na *interpretacje strzałek* i odpowiedzialności, NIE samo listing nodów
3. **5.3 Dwa widoki dynamiczne — inference flow + training flow** (10-12 stron) — sequence diagrams z latency budget per komponent; UI mockup Gradio wmontowany jako finalny krok inference flow (NIE osobna sekcja)
4. **5.4 Continuous improvement loop jako pętla MLOps** (8-10 stron) — *centralna kontrybucja MLOps*; cykle retreningu + drift triggers + A/B gating + warunki promotion/rollback; *to* jest „Pana sweet spot" promotora Kojałowicza
5. **5.5 Observability stack i drift detection** (5-6 stron) — Langfuse + LGTM + Alertmanager z konkretnymi alert rules + escalation paths + Evidently + Alibi Detect
6. **5.6 Bezpieczeństwo, prywatność, compliance** (3-4 strony) — anonimizacja, TDM exception, RODO, EU AI Act note, mandatory disclaimer fail-closed pattern
7. **5.7 Decyzje konstrukcyjne, kompromisy, podsumowanie** (8-10 stron) — **najmocniejsza sekcja R5**; tabela 12-15 decyzji architektonicznych w formacie *Decyzja → Alternatywa → Rationale → Trade-off → Status*; trzy kluczowe kompromisy w narracji; deployment scenarios; recap + transition do R6

### 4.2 Co BY dodał (perspektywy, view'y, security)

1. **Sekcja „Wymagania architektoniczne" PRZED widokami C4.** Najbardziej brakująca rzecz. Czytelnik widzi widoki C4 *bez kontekstu* po co tych 12 kontenerów. BY zaczął od listy 6-8 wymagań niefunkcjonalnych: (a) end-to-end latency <3s; (b) per-claim observability dla audit; (c) reprodukowalność deterministyczna (seed); (d) single-machine deploy (constraint pracy); (e) Apache 2.0/MIT compliance dla publishable; (f) fail-closed dla legal advice attempts; (g) graceful degradation jeśli Tier 1 verifier niedostępny; (h) drift detection auto-trigger retraining. Każde wymaganie *kommentowane jednym zdaniem* z forward ref *„adresowane przez X w sekcji 5.Y"*. To daje czytelnikowi *kontrakt* — wie czego oczekiwać i jak weryfikować spełnienie.
2. **Latency budget table w 5.3.** Per komponent: query embedding (50ms TEI BGE-M3), Qdrant search (10ms top-5), prompt assembly (5ms), Bielik generation (1500ms SGLang bf16), probe extraction (30ms PyTorch hooks parallel), claim extraction (200ms), NLI verifier (100ms × 5 claims = 500ms), citation alignment (50ms), response assembly (10ms). Suma ~2355ms. To *jedna* tabela ale pokazuje że *naprawdę* myślałeś o systemie produkcyjnym. Komisja DS to wynagrodzi.
3. **Failure modes table w 5.4 lub 5.7.** Per Tier 1/2/3 verifier + per kontener: co się dzieje gdy Tier 1 wraca low confidence? Co gdy Tier 2 niedostępny? Co gdy LLM judge timeout? Co gdy Qdrant connection drop? Co gdy SGLang OOM? Eksplicit *fail-closed vs fail-open* decisions per failure mode. To pokazuje *systemowe myślenie*, NIE tylko *technologiczny wybór*.
4. **RACI matrix w 5.2.** 12 kontenerów × 4-5 kategorii odpowiedzialności (retrieval, generation, verification, observability, training). R=responsible, A=accountable, C=consulted, I=informed. Komisja MLOps lubi RACI. Pokazuje że wiesz *kto co robi* w systemie.
5. **Deployment scenarios w 5.7.** Trzy scenariusze: (a) local dev (laptop Magdy, no GPU, mDeBERTa CPU only); (b) lab GPU SP7 H200 (training run + Bielik probe extraction); (c) hipotetyczny production (single VM z GPU, NIE Kubernetes). Pokazuje że *świadomie* wybrałaś single-machine z konkretnym uzasadnieniem (single-author scope), NIE z ignorancji.
6. **Forward refs table jako mapowanie R5 → R6 → R7.** *„Sekcja R5.X opisuje *co*; R6.Y parametryzuje *jak*; R7.Z mierzy *z jakim skutkiem*."* Macierz 10-12 wierszy. Daje komisji *nawigację* w pracy.
7. **Security threat model (krótka subsekcja w 5.6).** Trzy klasy zagrożeń: (a) *prompt injection attempting legal advice elicitation* → fail-closed pattern z disclaimer; (b) *PII leak through forum scrapes* → regex + sha1 anonymization audit; (c) *adversarial halucination examples* → future work z reference do cybersec angle w R8. To pokazuje że *myślisz security-first*, NIE tylko *functionality-first*.

### 4.3 Co BY usunął

1. **Status oznaczeń 🚧 Iter. X w tabeli komponentów.** Status implementacji NIE należy do tekstu akademickiego pracy. Komisja egzaminacyjna patrzy *po* obronie — wszystko ma być zaimplementowane. Statusy BY wyniósł do osobnego dokumentu projektowego (`STATUS.md` w repo).
2. **Polishing notes („48h-draft", „Mermaid polish w Iteracji 7").** Te uwagi metodologiczne należą do CLAUDE.md, NIE do finalnej pracy.
3. **Lista 12 kontenerów wyświetlana w pełnej tabeli i wtórnie w szkielecie Mermaid Container view.** Redundancja. Tabela 5.1 z 12 kontenerami WYSTARCZY; Mermaid figura ma pokazać *przepływy*, NIE wyliczyć ponownie wszystkie nazwy kontenerów.
4. **Osobna sekcja 5.8 Gradio mockup.** UI mockup BY wpleciłem do 5.3 (inference flow) jako final step. UI nie zasługuje na własną sekcję — to *jeden z kontenerów* opisanych w 5.2.
5. **Powielanie informacji między 5.4 (training) i 5.5 (continuous loop).** Training jest częścią pętli — BY skonsolidował obie sekcje w jedną *5.4 Continuous improvement loop* z trzema podsekcjami: jednorazowy training cykl 1, retraining cykl N+1, A/B gating.

### 4.4 Sample paragraf (mój styl pisania o decyzjach konstrukcyjnych, polski akademicki, 8 zdań)

> Decyzja o przyjęciu architektury monolitycznej z modułami w obrębie pojedynczej aplikacji FastAPI zamiast topologii mikroserwisów jest świadomym kompromisem wynikającym z zakresu pracy inżynierskiej. Architektura mikroserwisowa, w której każdy komponent pipeline'u — retriever, generator, weryfikator NLI, klasyfikator probe — stanowi odrębny deployable service komunikujący się przez REST lub gRPC, jest powszechnie rekomendowanym wzorcem dla systemów MLOps w warunkach produkcyjnych. W kontekście niniejszej pracy adopcja mikroserwisów wiązałaby się jednak z trzema znaczącymi kosztami: narzutem operacyjnym orkiestracji Kubernetes lub Docker Swarm, którego utrzymanie wykraczałoby poza kompetencje single-author project; zwiększeniem złożoności obserwowalności wymagającym konfiguracji service mesh; oraz przede wszystkim ryzykiem, że uwaga autorki przesunęłaby się z naukowego pytania (czy probe na ukrytych stanach Bielika wykrywa halucynacje) na problem inżynierski utrzymania kontenerów w sieci. Z tych powodów architektura niniejszej pracy organizuje wszystkie komponenty pipeline'u w obrębie jednej aplikacji FastAPI z modułami w osobnych pakietach Pythona (`src/halu/`, `src/probe/`, `src/verifier/`, `src/citation/`), zachowując rozdział odpowiedzialności na poziomie kodu źródłowego bez przenoszenia go na warstwę infrastruktury. Granica między monolitem a mikroserwisami jest natomiast *jawna w kodzie* — każdy moduł komunikuje się z pozostałymi przez stabilny interfejs Pythona, który w przyszłej iteracji może zostać podniesiony do interfejsu HTTP bez refaktoringu logiki biznesowej. Migracja monolitu do mikroserwisów jest zatem zachowanym trade-offem, nie zaproponowanym — oczekiwana jest dopiero w hipotetycznej fazie produkcyjnego deploymentu omówionej w sekcji 5.7.3 jako future work. Honest acknowledgment alternatywy oraz zaprojektowana ścieżka migracji to dwa elementy, które zdaniem autorki *każda* decyzja architektoniczna w pracy inżynierskiej powinna posiadać — bez nich decyzje stają się dogmatyczne, a praca traci wymiar *systemowego myślenia*.

(Charakterystyka stylu: deklaratywne pierwsze zdanie + trzy konkretne koszty wyliczone narracyjnie (NIE bulletami) + honest acknowledgment alternatywy + pokazanie świadomości trade-offu + forward path dla przyszłej migracji + meta-komentarz o wymiarze systemowego myślenia. Brak code-mixu EN-PL, brak nazw narzędzi w tytułach (Kubernetes, Docker — tylko w przykładzie), brak time-proofing ("obecnie", "nowoczesny").)

### 4.5 Top 3 różnice vs current draft

1. **Sekcja „Wymagania architektoniczne" PRZED widokami C4.** Najbardziej brakująca rzecz. C4 odpowiada na pytanie *jak*, ale bez uprzedniej odpowiedzi na *po co*. BY dodał 4-5 stron z 6-8 wymaganiami niefunkcjonalnymi + macierzą *wymagania × kontenery*.
2. **Sekcja 5.7 (decyzje konstrukcyjne) jako *najmocniejsza* sekcja R5.** Current szkic ma 10 decyzji jako jeden paragraf w 5.9.1. BY rozbudował do 8-10 stron z osobnym uzasadnieniem każdej decyzji w formacie *Decyzja → Alternatywa → Rationale → Trade-off*. To miejsce gdzie pokazuje się *autorska wartość intelektualna* — komisja czyta sekcję *„decyzje konstrukcyjne"* najuważniej.
3. **Latency budget + Failure modes + RACI matrix.** Trzy konkretne *systemowe* artefakty, których brakuje. Każdy ~1 strona, razem ~3 strony. Skok jakości percepcji *systemowego myślenia* jest nieproporcjonalnie wysoki w stosunku do kosztu napisania.

---

## 5. Cross-cutting + priorytety 48h-sprint

### 5.1 Spójność narracji R3 → R4 → R5

**Jeden motyw przewodni:** *„semantyczna struktura korpusu *implikuje* decyzje architektoniczne pipeline'u, a continuous improvement loop zamyka pętlę feedback od inference do danych"*.

- R3 zbiera 11 000 chunków z 6 rodzin źródłowych w 9 typach źródłowych
- R4 *empirycznie* waliduje że taksonomia jest dobrze dobrana (BERTopic clustering + Category × source_type heatmap + UMAP scatter)
- R5 *wykorzystuje* wynik walidacji R4 do uzasadnienia decyzji architektonicznych (np. stratifikacja train/val/test per source_type w 5.X uzasadniona empirycznym brakiem leakage z 4.X)

Trzy forward refs w obu kierunkach: w R3 §3.4 paragraf zamykający → R4 §4.3; w R4 §4.3 ostatni paragraf → R5 §5.X; w R5 §5.X eksplicytne *„decyzja umotywowana wynikami R4 §4.3"*.

**Terminology consistency (critical):**

- `chunk` (NIE *fragment*, NIE *rekord*, NIE *unit*)
- `pipeline retrievalu` / `pipeline inferencji` / `pipeline treningu` (NIE *procesos*, NIE *flow*)
- `klasyfikator probe` / `weryfikator NLI` (NIE *probe model*, NIE *NLI model*)
- `gold standard` jako standalone term (NIE tłumaczyć na *złoty standard*)
- `ukryte stany` (wybór polski — bardziej akademickie niż EN *hidden states*; trzymać konsekwentnie)
- `halucynacja` (NIE *hallucination*, NIE *halu*)
- `citation-grounded` → polski *„z ugruntowaniem cytacyjnym"* lub zachować EN konsekwentnie (decyzja terminologiczna)

### 5.2 Priorytety dla 48h-sprint (deadline 18.05.2026)

**MUST be in submitted version (P0):**

R3:
- Pełne sekcje 3.1-3.6 z prozą (NIE samymi tabelami)
- Mini case study jednego pytania end-to-end (np. *„14 dni na odstąpienie"*) — *spina rozdziału*
- 6 reprezentatywnych listings chunków per typ źródłowy
- Tabela decyzji konstrukcyjnych korpusu (4-5 wierszy)
- Honest limitation paragraph zamykający 3.5 (single-annotator IAA limitation)

R4:
- Sekcje 4.1-4.4 (eksploracja + Wariant B audit) z REAL wartościami zamiast placeholderów dla statystyk *które już są w DATASET_CARD.md*
- Figura 4.1 (source_type pie + bar side-by-side) + Figura 4.2 (violin plot długości per source_type) jako minimum
- Sekcja 4.6 (BGE-M3 L2 normalization) krótka ale kompletna
- Heatmap source_type × Category (1 figura, prosta do wygenerowania z DATASET_CARD)

R5:
- Sekcje 5.1 (z wymaganiami architektonicznymi) + 5.2 (Context + Container, BEZ Component zoom-in jeśli czas nagli) z prozą
- Sekcja 5.7 (decyzje konstrukcyjne) z 8-10 decyzjami w formacie tabelarnym z konkretnym rationale per decyzja
- Krótka sekcja 5.6 (security/disclaimer)
- Mermaid figury 5.1 + 5.2 jako PEŁNE (NIE szkielety tekstowe)
- Sample paragraf z sekcji 4.4 powyżej jako template dla 3-4 kolejnych decyzji

**Can be added post-sprint (P1):**

- BERTopic full execution (uruchomienie BERTopic na 11k chunków zajmuje 2-4h, plus interpretacja klastrów)
- Word clouds per Category (appendix)
- Pełne diagramy Mermaid dla 5.3 + 5.4 + 5.5 (sequence diagrams + flowcharts)
- Latency budget table, Failure modes table, RACI matrix (3 osobne tabele po 1 stronie)
- Stratifikacja train/val/test chi-square test

**Out of sprint scope:**

- BERTopic w pełnej formie (placeholder + plan wystarczy w sprincie)
- Empirical training metrics (R6/R7 territory)
- Pełne deployment scenarios (skrócony jeden scenariusz wystarczy w sprincie)

### 5.3 Trzy metafory/frame'y dla komisji

1. **„Korpus jako trzy biblioteki w jednej"** (R3 + cross-ref). Pipeline pracuje z korpusem w trzech rolach: jako baza wiedzy (retrieval), jako materiał treningowy (probe + verifier), jako sędzia (eval). Komisja zapamięta *„trzy biblioteki"* lepiej niż abstrakcyjne *„three roles"*.
2. **„Architektura jako pętla, nie linia"** (R5). System NIE jest *linear pipeline* (query → retrieve → generate → verify → respond), tylko *closed loop* z continuous improvement (production traces → failure detection → preference dataset → retrain → A/B gate → production). Pętla, nie linia — to *kluczowa* metafora dla MLOps mindset. Promotor Kojałowicz zna pojęcie *continuous improvement loop* z Six Sigma — refer to it explicitly.
3. **„Trzypoziomowy weryfikator jako sąd trzech instancji"** (R3 + R5 + R6). Tier 1 mDeBERTa = sąd pierwszej instancji (szybki, większość spraw); Tier 2 HerBERT-large = apelacja (wolniejsza, dokładniejsza, reserved); Tier 3 LLM judge = sąd najwyższy (oracle, najdroższy, ablation only). Polish-friendly metafora z tematem prawnym, intuicyjna dla każdej komisji.

---

## 6. Co standardowo dodać dla PJATK Data Science (3 elementy)

Trzy elementy które typowo są w pracach DS PJATK, a których obecne drafty *nie mają* (lub mają placeholder):

1. **Proof of concept demo — screen recordings GIF z Gradio app (R5 lub osobny appendix).** Trzy konkretne pytania end-to-end pokazane wizualnie: pytanie wpisane → odpowiedź wygenerowana → citation badges per claim → halu scores per claim → linkowany evidence chunk. Magdzie zajmie 30-60 min nagrać 3 GIFy z aktualnego Gradio MVP (jeśli MVP istnieje) lub mockup wireframes (jeśli nie). Komisja DS *uwielbia* visual demonstrations — to *jedyny* sposób żeby pokazać że *coś działa* w pracy o systemie. ROI najlepszy ze wszystkich „nice to have" elementów.

2. **Performance benchmarks (sekcja R5 lub R7).** Tabela: latency per komponent + throughput total + memory footprint per kontener + cold-start time. Liczby muszą być realne (nie wymyślone), choćby z preliminary runs na laptopie. Komisja DS *oczekuje* że *patrzysz na metryki systemowe*, nie tylko model metrics (AUROC). To częściowo pokrywa się z propozycją „latency budget table" w R5.7, ale Performance benchmarks BY rozbudowal o memory + throughput + cold-start jako *osobny* artefakt systemowy.

3. **Lessons learned section (część R8, *anchor* w R3-R5 z forward ref).** *„Decyzje podjęte w niniejszej pracy nie zawsze były pierwszymi rozważanymi. W szczególności: (a) początkowo wybrano farmakologię + reranker fine-tuning, refined to consumer rights + hidden-states probe po feasibility evidence z Iteracji 0a; (b) podejście monolithic single-token labeling halu okazało się nieproduktywne, zastąpione przez 5-typową taxonomy z NLI mapping; (c) inițjalny 5-RQ scope zredukowany do 3 main + 1 supporting po Dubanowska EMNLP 2025 OOD evidence."* To *honest* retrospective od autora pokazujący *growth mindset*. W R3-R5 można zaszyć po jednym paragrafie *„initial approach was X, refined to Y after Z"* z forward ref do R8 lessons. Komisja PJATK DS wysoko ocenia *retrospective honesty* — wyróżnia pracę od „all-knew-from-start" prac inżynierskich.

---

## TLDR (5 zdań)

Po pierwsze: temat ma niszę i defensible audit trail, ale skala pracy plasuje się na granicy magisterki — R5 BY uczynił *kontraktem z czytelnikiem* (sekcja „Wymagania architektoniczne" + macierz wymagań × kontenerów) zamiast *technologicznym katalogiem ambicji*. Po drugie: R3 BY zorganizował wokół *sześciu rodzin źródeł* (zamiast dziewięciu typów) z mini-case-study jednego pytania end-to-end i 6 listings reprezentatywnych chunków — to zamknie 80% pytań komisji o jakość danych. Po trzecie: R4 BY uczynił BERTopic *centralnym* elementem walidacji taksonomii (zamiast jednej placeholderowanej sekcji), plus heatmap source_type × Category, violin plots, UMAP z overlay Wariant B i sekcję anomalii. Po czwarte: R5 BY dodał *Wymagania architektoniczne PRZED C4*, rozbudował *Decyzje konstrukcyjne* do najmocniejszej sekcji (8-10 stron, 12 decyzji w formacie *Decyzja → Alternatywa → Rationale → Trade-off*) oraz dodał *Latency budget + Failure modes + RACI matrix* jako trzy konkretne artefakty systemowego myślenia. Po piąte: brakujące standardowo dla PJATK DS to (a) Proof-of-concept GIFy z Gradio (30-60 min nagrania, najwyższe ROI), (b) Performance benchmarks (latency + memory + throughput + cold-start) oraz (c) Lessons learned z honest retrospective anchored w R3-R5 z forward ref do R8.

---

## Top 3 BY-ADD per rozdział (szybka referencja)

### R3 BY-ADD
1. Mini-case study jednego pytania end-to-end (*spina* rozdziału)
2. 6 reprezentatywnych listings chunków per typ źródłowy
3. Tabela decyzji konstrukcyjnych korpusu (4-5 wierszy, format *Decyzja → Alternatywa → Rationale → Trade-off*)

### R4 BY-ADD
1. BERTopic jako CENTRALNY element walidacji taksonomii (sekcja 4.3 rozbudowana)
2. Heatmap source_type × Category (1 wykres pokazuje 2 wymiary korpusu)
3. Sekcja „Anomalie i edge cases" (*forensic mindset*, 2-3 strony)

### R5 BY-ADD
1. Sekcja „Wymagania architektoniczne" PRZED widokami C4 (kontrakt z czytelnikiem)
2. Sekcja 5.7 *Decyzje konstrukcyjne* rozbudowana do 8-10 stron z 12 decyzjami (najmocniejsza sekcja R5)
3. Latency budget table + Failure modes table + RACI matrix (3 systemowe artefakty)

## Top 3 BY-REMOVE per rozdział (szybka referencja)

### R3 BY-REMOVE
1. Powtarzanie pełnych statystyk DATASET_CARD.md (przenieść per-source breakdown do R4)
2. Drobiazgowe wyjaśnienia narzędzi scrape (playwright-stealth, F5 bypass) — do appendix
3. Sekcja „obecny stan / status pivotów" (pivots należą do `decisions/`, nie do pracy akademickiej)

### R4 BY-REMOVE
1. Sekcja tokenizator APT4 (należy do R6, NIE do R4)
2. TF-IDF baseline jako dedykowana podsekcja (krótkie wspomnienie wystarczy)
3. Powtarzanie tabel source_type z R3 (jedno miejsce dla każdej statystyki, R4 ma być *interpretacją* + *wizualizacją*)

### R5 BY-REMOVE
1. Status oznaczeń 🚧 Iter. X w treści (do osobnego `STATUS.md` w repo)
2. Polishing notes („48h-draft", „Mermaid polish w Iter. 7") — należy do CLAUDE.md
3. Osobna sekcja 5.8 Gradio mockup (wmontowane w 5.3 inference flow jako finalny krok)

---

**Pełen dokument:** `D:\diplomma\thesis_research\notes\fresh_perspective_jak_by_ja_zrobil_2026-05-16.md`
