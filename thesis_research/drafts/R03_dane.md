# R3. Dane

> **48h-draft (2026-05-16):** placeholdery `{{...}}` dla wartości oczekiwanych z Iteracji 1–6. Wartości znane na dziś (Polish CitationBench v0.6) wpisane bez placeholderów. Cytacje w formacie roboczym `[CYT: ...]` — finalny IEEE pass w Iteracji 7.

---

## 3.1 Cele i charakter danych

Korpus pracy nazywa się **Polish CitationBench v0.6** i pełni w pipeline trzy odrębne role. Po pierwsze stanowi **bazę wiedzy dla retrievalu** — fragmenty aktów prawnych, dyrektyw UE, orzeczeń i poradników urzędowych są indeksowane wektorowo i pobierane jako kontekst dla każdego zapytania użytkownika. Po drugie służy jako **dane treningowe** dla klasyfikatora hidden-states probe oraz weryfikatora NLI — pary halucynacyjne z etykietami uczą model rozpoznawać niezgodność między claimem a źródłem. Po trzecie obejmuje **zbiór ewaluacyjny** — gold standard 200 par manualnie anotowanych przez autorkę oraz silver labels do walidacji na większej skali.

Korpus jest jednomodalny: zawiera wyłącznie teksty w języku polskim. Nie obejmuje danych audio, wideo ani obrazów rastrowych w sensie surowych danych badawczych. Diagramy architektoniczne z Rozdziału 5 są generowane programatycznie z notacji Mermaid i nie stanowią danych w rozumieniu Task 03. Konsekwencją jednomodalności jest możliwość zastosowania jednego pipeline preprocessingu i jednej schemy `Chunk` dla wszystkich źródeł, niezależnie od ich pierwotnej struktury (XML, HTML, PDF).

Łącznie korpus zawiera 11 000 fragmentów unifikowanych w schemie `Chunk` oraz 5 402 syntetyczne pary halucynacyjne uzupełnione 200 parami gold standard. Korpus jest publikowany jako standalone dataset na platformie HuggingFace w Iteracji 6 z DOI Zenodo zapewniającym cytowalność.

Tabela 3.1 prezentuje trzy role korpusu wraz z mapowaniem na komponenty pipeline.

**Tabela 3.1.** Trzy role korpusu Polish CitationBench v0.6.

| Rola | Wykorzystanie | Materiał źródłowy | Pojemność |
|---|---|---|---|
| Retrieval corpus | Indeks wektorowy Qdrant dla RAG | `legal_statute` + `legal_ue_directive` + `legal_tsue_judgment` + `legal_court_judgment` + `legal_uokik_decision` + `legal_document_pdf` + `encyclopedic` | 7 622 chunków |
| Training data | Probe + verifier (uczenie nadzorowane) | `halu_pairs.jsonl` (syntetyczne) | 5 402 par |
| Eval set | Walidacja RQ1–RQ4 | Gold standard manual + silver labels | 200 par gold + ~1 000 par silver |
| Query distribution | Stres-test pipeline'u (real consumer questions) | `qa_raw` + `qa_gold` | 3 378 zapytań |

Rozdziały R4 (eksploracyjna analiza danych) oraz R6 (modele) wykorzystują korpus opisany tutaj jako bezpośrednie wejście empiryczne. R4 raportuje rozkłady i statystyki opisowe. R6 dokumentuje wybór i parametryzację modeli (probe, verifier, generator). R7 raportuje metryki obliczone na zbiorze testowym.

## 3.2 Źródła danych

Korpus pochodzi z sześciu rodzin źródeł. Każda ma odrębną metodykę pozyskiwania i licencję. Tabela 3.2 zestawia rodziny po cleanupie Wariant B (sekcja 3.4).

**Tabela 3.2.** Rodziny źródeł korpusu — domena, licencja, metoda pozyskania.

| Rodzina | Domena | Licencja | Metoda scrape |
|---|---|---|---|
| ISAP | Polskie ustawy konsumenckie (27 aktów, w tym UPK, KC art. 535–581, Konstytucja art. 76) | Urzędowe (Art. 4 PrAut + TDM exception 2024) | Sejm ELI API (XML + PDF cross-format) |
| EUR-Lex | UE dyrektywy konsumenckie (8) + orzeczenia TSUE (29) | © Unia Europejska, reuse per Decyzja 2011/833/UE | EUR-Lex HTML + PDF per CELEX ID |
| UOKiK | Q&A FAQ + decyzje Prezesa UOKiK + poradniki PDF | Urzędowe (Art. 4 PrAut) | httpx (Q&A), Playwright (decyzje, F5 WAF bypass), pdfplumber (poradniki) |
| Orzeczenia sądowe | ms.gov.pl (38 wyroków) + SN.pl (filtrowane consumer-related) | Urzędowe (Art. 4 PrAut) | Playwright z bypass dla Apache Tapestry (ms.gov.pl) i SharePoint (SN.pl) |
| Real consumer questions | e-prawnik, forumprawne, Reddit r/Polska, eporady24 | Fair-use Art. 29 PrAut (academic) | httpx + brotli decode; anonimizacja Reddit sha1:10 |
| Encyclopedic + supplementary | Wikipedia + federacja-konsumentow + UODO + KNF + UKE + URE | CC BY-SA 4.0 (Wiki) / urzędowe (gov.pl) / fair-use NGO | httpx + per-source adaptery |

ISAP wybrano jako główne źródło prawne ze względu na deterministyczną strukturę aktów. Jednostka redakcyjna *art. X ust. Y pkt Z lit. l* mapuje jednoznacznie na chunk korpusu. Cytacja staje się gold standardem dla pipeline citation grounding. Każda z 27 ustaw konsumenckich jest zachowana w dwóch komplementarnych formatach: strukturalnym XML/HTML z Sejm ELI API oraz oryginalnym PDF z Dziennika Ustaw (z weryfikacją SHA-256 dla audytu integralności).

EUR-Lex dostarcza kontekst legislacyjny, którego polskie ustawy są implementacją krajową. Korpus obejmuje osiem dyrektyw konsumenckich (m.in. Consumer Rights Directive 2011/83/UE, Unfair Contract Terms 93/13/EWG, Consumer Credit Directive II 2023/2225) oraz 29 orzeczeń Trybunału Sprawiedliwości UE istotnych dla polskiej praktyki konsumenckiej. Wśród orzeczeń znajduje się *Dziubak* (C-260/18) [CYT: TSUE C-260/18 Dziubak 2019], fundament polskiego orzecznictwa w sprawach kredytów hipotecznych indeksowanych do walut obcych.

UOKiK obejmuje trzy źródła komplementarne. Pierwsze to 60 par pytanie–odpowiedź z portalu *prawakonsumenta.uokik.gov.pl*, z których 55 zawiera explicit cytację prawną w formacie *Podstawa prawna: <statute>*. Drugie to 26 decyzji Prezesa UOKiK z portalu decyzyjnego. Pobranie wymagało bypass dla zabezpieczenia F5 BIG-IP ASM przy użyciu playwright-stealth. Trzecie to osiem poradników PDF wydanych przez UOKiK, przetworzonych narzędziem pdfplumber z heurystyczną detekcją sekcji.

Orzecznictwo sądowe obejmuje 38 wyroków z portalu *orzeczenia.ms.gov.pl* oraz wybór orzeczeń Sądu Najwyższego z bazy *sn.pl*. Z 121 pobranych orzeczeń SN po filtrze Wariant B zachowano 58 — wykluczono specjalistyczne orzeczenia o klauzulach frankowych CHF jako zbyt wąsko bankowe wobec ogólnej domeny konsumenckiej.

Rzeczywiste pytania konsumentów (2 945 rekordów) pełnią funkcję rozkładu zapytań dla pipeline'u retrievalu. Pochodzą z czterech źródeł: forum prawnego *forumprawne.org* (1 186 wątków), portalu *e-prawnik.pl* (948 pytań), subredditu *r/Polska* (509 wątków z anonimizacją SHA-1:10) oraz *eporady24.pl* (302 zapytania). Świadomie nie pobierano odpowiedzi z forów. Odpowiedzi pochodzą od losowych użytkowników bez weryfikowalnych kwalifikacji prawnych, więc nie mogą stanowić ground truth.

Rodzina uzupełniająca obejmuje materiały o niższym priorytecie ewaluacyjnym, lecz wartościowe jako kontekst: Wikipedia (34 artykuły konsumenckie, licencja CC BY-SA 4.0), federacja-konsumentow.org.pl (192 artykuły), portale urzędowe UODO (198 materiałów o ochronie danych konsumenta), KNF (107 artykułów konsumencko-finansowych), UKE (200 z prawa telekomunikacyjnego) oraz URE (15 z energetyki konsumenckiej).

## 3.3 Schemat danych i struktura plików

### 3.3.1 Unifikowany schemat `Chunk`

Wszystkie rekordy w warstwie przetworzonej odpowiadają jednolitej schemie `Chunk` zdefiniowanej w `main_project/src/halu/schemas.py` przy użyciu Pydantic v2 w trybie strict. Tabela 3.3 dokumentuje pełen codebook.

**Tabela 3.3.** Codebook schemy `Chunk`.

| Pole | Typ | Obowiązkowe | Opis |
|---|---|:-:|---|
| `chunk_id` | str | tak | Globalnie unikatowy identyfikator (np. `eli_DU_2014_827_art_27_ust_1`) |
| `source_type` | `SourceType` enum | tak | Klasyfikacja źródła (9 wartości) |
| `source` | str | tak | Domena źródła (np. `isap.sejm.gov.pl`) |
| `source_url` | str | tak | Pełen URL dla audytu |
| `title` | str (≥2) | tak | Tytuł dokumentu lub artykułu |
| `tresc` | str (≥10) | tak | Główna treść chunka, NFC-normalized |
| `citation_string` | str \| None | nie | Cytacja kanoniczna (np. `art. 27 ust. 1 UPK z 2014/827`) |
| `cited_articles` | list[str] | tak | Cytacje wyekstrahowane regexem z `tresc` |
| `categories` | list[`Category`] | tak | Multi-label klasyfikacja semantyczna (14 wartości) |
| `language` | str | tak | ISO 639-1 (domyślnie `"pl"`) |
| `license` | str | tak | Licencja per chunk |
| `scrape_date` | date | tak | Data pozyskania |
| `process_date` | date | tak | Data ostatniego przetworzenia |
| `metadata` | dict[str, Any] | tak | Pola specyficzne dla typu źródła |

Pole `source_type` przyjmuje jedną z dziewięciu wartości enumu: `legal_statute`, `legal_ue_directive`, `legal_tsue_judgment`, `legal_court_judgment`, `legal_uokik_decision`, `legal_document_pdf`, `encyclopedic`, `qa_gold`, `qa_raw`. Pole `categories` jest multi-label i przyjmuje wartości z 14-elementowego enumu `Category` obejmującego sześć głównych grup: `consumer_*` (core, contract, credit, digital, telecom, return_refund, unfair_practices, dispute_resolution), `finance_adjacent`, `eu_directive`, `tsue_judgment`, `court_precedent`, `regulatory_decision`, `other`.

Pole `metadata` przechowuje informacje specyficzne dla typu źródła bez konieczności rozszerzania schemy bazowej. Dla aktów ISAP zawiera `ustawa_id`, `art`, `ust`, `pkt`, `lit`. Dla orzeczeń TSUE zawiera `celex_id`, `case_name`, `sklad`, `data_orzeczenia`. Walidator NFC-normalizacji na polu `tresc` zapewnia stabilną reprezentację polskich diakrytyków przy tokenizacji w pipeline'ach Transformers.

### 3.3.2 Struktura katalogów i konwencja nazewnictwa

Katalog `main_project/data/` zachowuje rozdział między warstwą surową (read-only) a przetworzoną:

```
main_project/data/
├── raw/                                          # surowe dane scrape (read-only)
│   ├── eli_ustawy_konsumenckie_2026-05-16/      # 27 ustaw w JSONL + meta
│   ├── eli_pdf_2026-05-16/                       # PDFy Dz.U. (sha256 verified)
│   ├── ue_dyrektywy_2026-05-16/                  # 8 dyrektyw + manifests
│   ├── tsue_orzeczenia_2026-05-16/               # 29 orzeczeń TSUE
│   ├── uokik_qa_2026-05-16/                      # 60 par Q&A
│   ├── uokik_decyzje_2026-05-16/                 # 26 decyzji
│   ├── consumer_documents_2026-05-16/            # poradniki PDF
│   ├── consumer_questions_polish_2026-05-16/     # 4 fora + _archive z raw HTML
│   ├── sn_orzeczenia_2026-05-16/                 # 121 SN
│   ├── extended_consumer_2026-05-16/             # encyclopedic + RF FAQ
│   └── {bankier_pl, infor_pl, ...}_2026-05-16/   # 12 portali
└── processed/
    └── citationbench_v0.6_2026-05-16/
        ├── chunks.jsonl                           # 11 000 rekordów Chunk
        ├── halu_pairs.jsonl                      # 5 402 par HaluPair
        ├── splits/                                # train/val/test (stratified)
        └── DATASET_CARD.md                       # karta HuggingFace
```

Identyfikatory `chunk_id` generowane są deterministycznie z metadanych źródłowych. Dla aktów ISAP stosowany jest wzorzec `eli_{ustawa_id}_art_{N}_ust_{N}_pkt_{N}` z opcjonalnymi suffiksami dla paragrafów i liter. Dla orzeczeń TSUE używany jest CELEX ID (np. `celex_62018CJ0260` dla *Dziubak*). Dla materiałów z forów identyfikator zawiera prefiks źródła oraz numeryczny seria-id.

Surowe pliki PDF i HTML zachowane są w podkatalogach `_archive/` per źródło, z sidecarami `_manifest.json` zawierającymi hash SHA-256, datę pobrania, kod statusu HTTP oraz mapowanie `chunk_id → archive_file`. Ta struktura zapewnia pełen audyt integralności i możliwość wsadowego ponowienia ekstrakcji z surowych źródeł bez konieczności ponownego scrape.

## 3.4 Preprocessing i czyszczenie zakresu

### 3.4.1 Pipeline preprocessingu

Pipeline transformacji surowych źródeł do unifikowanej schemy `Chunk` jest zaimplementowany w `main_project/src/halu/dataset_builder.py`. Wykonuje go polecenie:

```bash
uv run python -m src.halu.dataset_builder \
    --raw-dir data/raw \
    --output-dir data/processed \
    --version v0.6 \
    --filter-policy strict \
    --halu-injection-per-pair 10 \
    --halu-legal-chunks-sample 1500 \
    --seed 42
```

Pipeline składa się z czterech etapów. Pierwszy etap to load wszystkich rekordów z dziewięciu rodzin źródeł przez dedykowane normalizery w `src/halu/normalizers.py`. Każdy normalizer mapuje pierwotną strukturę źródła na schemat `Chunk`. Drugi etap to NFC-normalizacja oraz ekstrakcja cytacji w polu `cited_articles` przy użyciu `src/halu/citation_extractor.py`. Regex parsuje wzorce dla polskich aktów prawnych (`art. X ust. Y pkt Z lit. l`), referencje Dz.U. w obu formatach (pre-2012 i post-2012), skróty kodyfikacyjne (KC, KPC, UPK) oraz cytacje UE (`Dyrektywa {rok}/{nr}/UE`, sprawy TSUE `C-{nr}/{rok}`). Trzeci etap to deduplikacja po `chunk_id` oraz po hashu pierwszych 500 znaków treści. Czwarty etap to zastosowanie polityki filtrowania `chunk_filter.py` opisanej w sekcji 3.4.2.

Generowanie syntetycznych par halucynacyjnych odbywa się równolegle przy użyciu `src/halu/halu_injector.py`. Generator pobiera 60 par UOKiK Q&A oraz losowo próbkuje 1 500 chunków z typów `legal_statute`, `legal_ue_directive`, `legal_court_judgment`, `legal_uokik_decision` i `legal_tsue_judgment`. Dla każdego źródła próbuje wygenerować jedną parę negatywną (entailment) oraz do dziesięciu (dla UOKiK) lub pięciu (dla legal chunks) par pozytywnych rozdzielonych w pięć typów halucynacji (definicje w sekcji 3.5). RNG seed = 42 zapewnia bit-identical reprodukcję między uruchomieniami.

### 3.4.2 Wariant B — selekcja zakresu korpusu

Wstępna wersja korpusu (v0.4) zawierała 17 862 chunki po naiwnej agregacji wszystkich pobranych źródeł. Krytyczny audyt zakresu przeprowadzony 2026-05-16 [CYT: notes/KRYTYCZNA_ocena_scope_2026-05-16.md] wskazał trzy główne niezgodności z deklarowanym zakresem domeny konsumenckiej. Po pierwsze wzrost objętości korpusu o 247 % w jednym dniu jako sygnał scope creep. Po drugie 80 % chunków oznaczonych jako `FINANCE_ADJACENT` w klasyfikacji multi-label przy zaledwie 27 % oznaczonych jako `CONSUMER_CORE`. Po trzecie włączenie ustaw spoza domeny konsumenckiej (Kodeks postępowania cywilnego, Prawo upadłościowe, Prawo bankowe) o łącznym wolumenie 21 % korpusu.

W odpowiedzi przyjęto **Wariant B cleanup** zaimplementowany jako polityka `strict` w module `chunk_filter.py`. Filtr stosuje deterministyczne reguły per-source z uzasadnieniem zachowanym w `notes/scope_cleanup_decisions_2026-05-16.md`. Główne kategorie wykluczeń:

- **Akty prawne spoza domeny konsumenckiej** — Kodeks postępowania cywilnego, Prawo upadłościowe, Prawo bankowe, Ustawa o usługach płatniczych. Procedural law oraz regulacja strony bankowej, nie konsumenckiej.
- **UCHYLONE ustawy konsumenckie** — Ustawa o szczególnych warunkach sprzedaży konsumenckiej (Dz.U. 2002/1176), Ochrona niektórych praw konsumentów (Dz.U. 2000/271), Ogólne bezpieczeństwo produktów (Dz.U. 2003/2275). Zastąpione przez UPK 2014/827.
- **Generic legal/finance journalism** — bankier.pl, infor.pl, prawo.pl, money.pl, gazeta-prawna.pl. Niska jakość dla treningu probe, ryzyko garbage-in-garbage-out.
- **bezprawnik.pl** — opinion site bez weryfikowalnej jakości redakcyjnej.
- **Pure-insurance RF chunks** — fragmenty z portalu Rzecznika Finansowego zawierające wyłącznie content ubezpieczeniowy bez relewancji konsumenckiej (mierzone heurystyką: ≥3 słowa kluczowe ubezpieczeniowe AND 0 słów kluczowych konsumenckich).
- **SN orzeczenia frankowe (CHF)** — specjalistyczne orzecznictwo bankowe stanowiące domain shift wobec ogólnych praw konsumenta.

Łącznie dropnięto 6 862 chunki (38,4 % korpusu pre-filter). Filtr policy nie jest hard-coded — `chunk_filter.py` udostępnia trzy poziomy (`strict` / `loose` / `none`), umożliwiając przyszłe re-eksperymenty na pełnej dystrybucji v0.4 jeśli badanie cross-domain transferability byłoby reaktywowane.

Pełne liczby dystrybucji per source_type oraz wpływ Wariant B na rozkłady kategorii prezentowane są w Rozdziale 4 (Tabela 4.1 i 4.2).

## 3.5 Definicje etykiet

Korpus posiada dwa zestawy etykiet: **5-elementową taksonomię typów halucynacji** stosowaną w syntetycznych parach treningowych oraz **3-elementowy zbiór etykiet NLI** stosowany w weryfikacji per-claim w pipeline citation grounding.

### 3.5.1 Taksonomia 5 typów halucynacji

Tabela 3.4 dokumentuje pięcioelementową taksonomię halucynacji z definicjami operacyjnymi i przykładami mutacji. Taksonomia została zdefiniowana 2026-05-16 i zatwierdzona jako stała struktura projektu w DEC-003.

**Tabela 3.4.** Taksonomia pięciu typów halucynacji.

| Typ | Definicja operacyjna | Przykład mutacji |
|---|---|---|
| `factual_fabrication` | Dodanie do odpowiedzi claimu, którego nie ma w retrieved context | Dodanie zdania *„Termin może zostać przedłużony o 21 dni za zgodą stron"* |
| `entity_confusion` | Zamiana podmiotów lub instytucji w odpowiedzi | *„konsument"* → *„przedsiębiorca"*, *„UOKiK"* → *„KNF"* |
| `temporal_drift` | Modyfikacja daty lub okresu | *„14 dni"* → *„30 dni"*, *„2014"* → *„2024"* |
| `negation_flip` | Odwrócenie sensu twierdzenia | *„konsument może odstąpić"* → *„konsument nie może odstąpić"* |
| `paragraph_mis_citation` | Cytacja niewłaściwego artykułu w odniesieniu do treści | *„zgodnie z art. 27"* → *„zgodnie z art. 28"* (treść z art. 27) |

Taksonomia pokrywa cztery klasy błędów semantycznych (entity, temporal, negation, mis-citation) oraz jedną klasę błędów uzupełnienia (factual_fabrication). Wybór taksonomii motywowany był analizą realnych przypadków halucynacji w generowanych odpowiedziach polskich LLM na pytania konsumenckie w fazie research [CYT: research/halu_detection_sota_2024_2026.md]. Inne taksonomie w literaturze (RAGTruth, HalluLens) obejmują pokrewne kategorie pod różnymi nazwami; piątka przyjęta w niniejszej pracy jest minimalna a zarazem wystarczająca do pokrycia obserwowanych klas błędów w domenie konsumenckiej.

### 3.5.2 Zbiór etykiet NLI

Weryfikacja per-claim w pipeline citation grounding stosuje standardowy 3-elementowy zbiór etykiet NLI: `entailed`, `neutral`, `contradicted`. Zbiór ten jest zgodny ze standardową interpretacją SNLI/MultiNLI [CYT: Bowman 2015 SNLI] oraz polskiej wersji CDSC-E w benchmarku KLEJ [CYT: Wróblewska CDSC-E KLEJ].

Mapowanie typów halucynacji na etykiety NLI nie jest jednoznaczne. Typ `factual_fabrication` polega na dodaniu *unsupported claim* — claim, który ani nie jest wsparty, ani nie zaprzecza retrieved context. Standardowa interpretacja NLI klasyfikuje taki przypadek jako `NEUTRAL`. Pozostałe cztery typy (`entity_confusion`, `temporal_drift`, `negation_flip`, `paragraph_mis_citation`) generują claim wprost sprzeczny z retrieved context, więc mapują na `CONTRADICTED`. Pary negatywne kontrolne (oryginalna odpowiedź UOKiK lub oryginalna treść chunka) mapują na `ENTAILED`.

To rozróżnienie zostało wprowadzone do generatora `halu_injector.py` jako mapa `_HALU_TYPE_NLI_LABEL` w iteracji 2026-05-16. Wcześniejsza wersja etykietowała wszystkie pięć typów halucynacji jednolicie jako `CONTRADICTED`, co prowadziło do mismatch z behavior modeli NLI — szczegóły walidacji w Rozdziale 6.

### 3.5.3 Zbiór `qa_gold` — kompozycja

Typ `qa_gold` w korpusie v0.6 obejmuje 433 chunki z dwóch źródeł komplementarnych. **Pierwsze źródło** — 60 par pytanie-odpowiedź pobranych z portalu UOKiK *prawakonsumenta.uokik.gov.pl*, z których 55 (91,7 %) zawiera explicit cytację prawną w formacie *Podstawa prawna: <statute>*. **Drugie źródło** — 373 par pytanie-odpowiedź pochodzących z ekspansji RF FAQ portalu *rf.gov.pl* (FAQ Rzecznika Finansowego), pobranych w ramach E1 extended scrape. Para RF FAQ zachowuje strukturę pytanie + pełna odpowiedź podobnie do UOKiK Q&A, lecz dotyczy ubezpieczeń i bankowości konsumenckiej (kategoria `FINANCE_ADJACENT` w klasyfikacji multi-label).

Decyzja o włączeniu RF FAQ do typu `qa_gold` zamiast typu `encyclopedic` lub `legal_document_pdf` motywowana jest strukturą danych — RF FAQ ma natywny format Q&A z explicit pytaniem i autorytatywną odpowiedzią ekspercką, podobnie do UOKiK Q&A. Z perspektywy treningu probe i verifiera obie podrodziny są wykorzystywane jednolicie jako wysokojakościowe źródło par claim-evidence.

### 3.5.4 Manual annotation — 200 par gold standard ewaluacyjnych

Zbiór ewaluacyjny gold standard 200 par stanowi podstawę walidacji RQ1–RQ4. Jest *odrębny* od 433-elementowego typu `qa_gold` w korpusie — gold standard ewaluacyjny służy *wyłącznie* do pomiaru metryk modeli (probe + verifier), nie do treningu. Składa się z dwóch komponentów. **Pierwszy** to 60 par UOKiK Q&A z portalu *prawakonsumenta.uokik.gov.pl* (te same 60 par co w `qa_gold` typu korpusowego). **Drugi** to **140 par hand-annotated przez autorkę** w trakcie weekend hyperfocus burst w Iteracji 5 — celem jest pokrycie typów halucynacji niedoreprezentowanych w dystrybucji UOKiK, w szczególności `paragraph_mis_citation` w aktach wymagających cross-references między ustawami oraz `temporal_drift` w obszarach takich jak prawo telekomunikacyjne konsumenckie i RODO w kontekście praw konsumenta.

Wytyczne anotacji manualnej obejmują trzy reguły operacyjne:

1. **Entailment** wymaga, że całość claimu jest *bezpośrednio* wsparta przez retrieved chunk, włącznie z wartościami liczbowymi i nazwami podmiotów.
2. **Contradiction** wymaga, że co najmniej jeden element claimu jest *wprost zaprzeczony* przez retrieved chunk.
3. **Neutral** stosuje się w pozostałych przypadkach, w tym dla unsupported additions, gdzie claim wykracza poza retrieved context bez bezpośredniego konfliktu.

Te zasady są zgodne ze standardową interpretacją SNLI/MultiNLI przyjętą również dla polskich datasetów (CDSC-E).

**Ograniczenie: brak inter-annotator agreement (IAA).** Gold standard 200 par jest produktem *pojedynczego anotatora* — autorki pracy. Brak wtórnego anotatora wyklucza obliczenie Cohen's kappa dla walidacji subiektywności decyzji anotacyjnych. Jest to świadome ograniczenie metodologiczne wymuszone przez zakres pracy inżynierskiej (jedna autorka + ograniczony budżet ekspertów dziedzinowych). Mitygacja obejmuje trzy elementy: (a) explicit pisemne wytyczne anotacji w protokole (powyżej, reguły 1-3), (b) self-review 10 % próby (20 par) po 48-godzinnej przerwie dla wykrycia drift w decyzjach, (c) cross-validation z Tier 1 mDeBERTa NLI na całej próbie 200 par — duże rozbieżności (>20 %) wskazują pary do reanalizy. Pełne raportowanie IAA jako future work zaplanowane jest w Iteracji 8+ (post-defense, jeśli secondary anotator dostępny przez kontakt z UOKiK lub Federacją Konsumentów).

Zbiór wtórny `~1 000` par silver labels generowany jest automatycznie z syntetycznych par halucynacyjnych przy użyciu Tier 1 verifier'a (mDeBERTa) jako auto-anotatora, z manualnym spot-check 5 % próby (50 par) przez autorkę dla walidacji silver-gold agreement.

## 3.6 Aspekty prawne, licencje, etyka

### 3.6.1 Macierz licencji

Korpus jest *mixed-license* z explicit attribution per chunk w polu `license` schemy `Chunk`. Tabela 3.5 prezentuje macierz licencji.

**Tabela 3.5.** Licencje per rodzina źródła + warunki dystrybucji.

| Rodzina źródła | Licencja | Warunki | Compatibility z HF dataset |
|---|---|---|---|
| ISAP — polskie ustawy | Urzędowe (Art. 4 PrAut + TDM exception 2024) | Bez restrykcji dla użytku badawczego | ✓ pełne |
| EUR-Lex | © European Union, Decyzja 2011/833/UE | Wymagane attribution z linkiem do EUR-Lex źródła | ✓ z attribution |
| UOKiK | Urzędowe (Art. 4 PrAut) | Bez restrykcji | ✓ pełne |
| Orzeczenia sądowe | Urzędowe (Art. 4 PrAut) | Bez restrykcji | ✓ pełne |
| Wikipedia | CC BY-SA 4.0 | Share-alike przy dystrybucji pochodnej | ⚠ filter `source_type != "encyclopedic"` jeśli SA problematyczne |
| Forum prawne (e-prawnik, forumprawne, eporady24) | Fair-use (Art. 29 PrAut, academic) | Krótki cytat dla celów badawczych | ✓ z anonimizacją PII |
| Reddit r/Polska | Fair-use (academic) | Anonimizacja nazw użytkowników | ✓ z sha1:10 hash |
| RF FAQ + portale urzędowe | Urzędowe | Bez restrykcji | ✓ pełne |
| Federacja Konsumentów + NGO | Fair-use (academic small excerpts) | Krótki cytat | ✓ |
| CDSC-E (Tier 2 fine-tune dataset) | CC-BY-NC-SA-4.0 | NonCommercial — wyłącznie badawcze | ⚠ klauzula NC raportowana w model card |

Karta HuggingFace dataset zawiera ostrzeżenie dotyczące Wikipedii: downstream users muszą dziedziczyć licencję CC BY-SA lub odfiltrować komponent encyclopedic. Klauzula NC dla CDSC-E nie dotyczy korpusu bezpośrednio — CDSC-E używany jest wyłącznie do potencjalnego fine-tune'u Tier 2 verifier, nie do publikacji datasetu.

### 3.6.2 Anonimizacja i PII

Anonimizacja dotyczy dwóch typów źródeł zawierających potencjalnie identyfikowalne informacje. **Reddit r/Polska**: nazwy użytkowników (`u/example`) zastąpiono skrótem SHA-1 obciętym do dziesięciu pierwszych znaków (np. `u/a3f8b9c2d1`). Mapowanie zachowano w lokalnym hashmap dla potencjalnej re-identyfikacji w przypadku żądania usunięcia danych zgodnie z RODO art. 17.

**Fora prawne**: pre-processing sprawdza wzorce regex dla numerów telefonu (polski format +48), adresów e-mail oraz numerów PESEL/NIP/REGON. Wykryte instancje są maskowane jako `[REDACTED-PHONE]`, `[REDACTED-EMAIL]`, `[REDACTED-ID]` przed włączeniem do korpusu. Audyt PII przeprowadzony w trakcie konstrukcji v0.6 nie wykrył przypadków pozostawionych w pole `tresc` po passie redakcji.

### 3.6.3 Polish TDM exception

Podstawą prawną dla scrape danych z polskich źródeł konsumenckich jest **wyjątek TDM (text and data mining)** wprowadzony do polskiej Ustawy o prawie autorskim w nowelizacji z września 2024 r. Nowelizacja implementuje Dyrektywę DSM 2019/790/UE w zakresie art. 3 dotyczącego TDM dla celów badań naukowych. Wyjątek pozwala na zwielokrotnianie utworów oraz reprodukcję baz danych w celach badań naukowych bez zgody uprawnionych, pod warunkiem zachowania legalnego dostępu do treści źródłowej oraz braku explicit opt-out (machine-readable, np. `robots.txt` directive `noai` lub `ai-bot`).

Wszystkie źródła użyte w korpusie zostały zweryfikowane pod kątem opt-out signals przed pobraniem. Żadne nie zawierało relevant directive w trakcie scrape. Audit zachowano w `_archive/_manifest.json` per source.

## 3.7 Reprodukowalność i dokumentacja

Pełna reprodukcja korpusu wymaga trzech komponentów: (a) repozytorium kodu z bieżącą wersją modułów `dataset_builder.py`, `chunk_filter.py`, `halu_injector.py`, `normalizers.py`, `citation_extractor.py` (commit hash `{{REPO_COMMIT_HASH}}`), (b) surowych danych z katalogu `data/raw/` (~1,4 GB, commitowanych do git dla pełnej audytowalności), (c) deterministycznego RNG seeda (`--seed 42`). Polecenie reprodukcji bit-identical wersji v0.6 podane w sekcji 3.4.1.

Dla każdego scrape'u zachowano sidecar `_archive/_manifest.json` z hashem SHA-256 surowych plików (PDF, HTML, JSONL), datą pozyskania, kodem statusu HTTP oraz mapowaniem `chunk_id → archive_file`. Pełen test integralności kompletny dla wszystkich źródeł w v0.6.

Karta HuggingFace dataset (`main_project/data/processed/citationbench_v0.6_2026-05-16/DATASET_CARD.md`) stanowi główny dokument referencyjny dla zewnętrznych użytkowników. Zawiera kompletne statystyki, licencje, biases, instrukcje cytowania (BibTeX entry) oraz przykłady użycia.

Rozdział 4 wykorzystuje dane opisane w niniejszym rozdziale jako bezpośrednie wejście dla eksploracyjnej analizy statystycznej. Koncentruje się na rozkładach długości chunków, pokryciu citation extractor, korelacji między source_type a klasami category, audycie post-Wariant B oraz dystrybucji typów halucynacji w zbiorze treningowym.

---

## Źródła robocze

Lista cytowań w finalnym formacie IEEE zostanie wygenerowana w Iteracji 7. Robocze źródła wykorzystane w niniejszym rozdziale:

- `main_project/data/processed/citationbench_v0.6_2026-05-16/DATASET_CARD.md` — karta HuggingFace dataset v0.6
- `notes/scope_cleanup_decisions_2026-05-16.md` — szczegółowy audyt per-source Wariant B
- `notes/KRYTYCZNA_ocena_scope_2026-05-16.md` — krytyka prowadząca do Wariant B
- `decisions/DEC-003_pivot-na-halu-detection.md` — pivot na obecny scope
- `decisions/DEC-004_iter0b_poc_results.md` — wyniki POC T1 PASS
- `research/halu_detection_sota_2024_2026.md` — przegląd SOTA halu detection
- `research/nli_models_2026_update.md` — szczegółowa analiza modeli NLI
- Polish TDM exception (Wrzesień 2024) — Ustawa o prawie autorskim
- ISAP API documentation; EUR-Lex SPARQL endpoint
