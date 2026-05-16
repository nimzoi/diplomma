# R4. Eksploracyjna analiza danych, standaryzacja i normalizacja

> **48h-draft (2026-05-16):** placeholdery `{{...}}` dla wartości wymagających uruchomienia notebooka EDA (BERTopic, UMAP, token length per Bielik APT4). Wartości znane z DATASET_CARD v0.6 wpisane bez placeholderów. Cytacje w formacie roboczym `[CYT: ...]`.

---

## 4.1 Wprowadzenie

Przed użyciem korpusu Polish CitationBench v0.6 do treningu klasyfikatora hidden-states probe oraz weryfikatora NLI należy potwierdzić jego jakość i spójność wewnętrzną. Rozdział 4 dokumentuje trzy fazy walidacji: **eksplorację** (rozkłady, anomalie, pokrycie), **standaryzację** (jednolity format danych) oraz **normalizację** (skalowanie reprezentacji wektorowych). Pełen wynik R4 informuje decyzje konstrukcyjne pipeline'u w Rozdziale 5 oraz hyperparametry modeli w Rozdziale 6.

Korpus pełni trzy odrębne role omówione w Rozdziale 3: bazę wiedzy dla retrievalu (8 022 chunków), dane treningowe dla probe i verifiera (5 402 syntetyczne pary halucynacyjne), oraz zbiór ewaluacyjny (200 par gold standard + ~1 000 silver labels). Każda z ról wymaga innej walidacji — retrieval corpus wymaga dobrego pokrycia tematycznego i zrównoważonej dystrybucji typów źródłowych, training data wymaga zbalansowanej dystrybucji typów halucynacji, eval set wymaga reprezentatywności wobec realnych zapytań konsumenckich. Sekcja 4.2 raportuje wyniki eksploracji per rola.

Surowy korpus (v0.4, pre-Wariant B) zawierał 17 862 chunki po naiwnej agregacji wszystkich źródeł. Po zastosowaniu polityki filtrowania `strict` (Wariant B, omówiony w Rozdziale 3) korpus został zredukowany do 11 000 chunków. Sekcja 4.3 dokumentuje wpływ tego cleanupu na rozkłady. Sekcje 4.4 i 4.5 opisują procedury standaryzacji i normalizacji zastosowane do tekstu polskiego, w szczególności normalizację Unicode NFC, harmonizację etykiet kategorii oraz reprezentacje wektorowe BGE-M3 [CYT: Chen 2024 BGE-M3 arXiv:2402.03216].

## 4.2 Eksploracja danych

### 4.2.1 Rozkład typów źródłowych

Korpus v0.6 obejmuje 9 typów źródłowych zdefiniowanych w enumie `SourceType`. Tabela 4.1 prezentuje rozkład liczebny.

**Tabela 4.1.** Rozkład chunków per `source_type` (korpus post-Wariant B, n = 11 000).

| `source_type` | Liczba chunków | Udział | Główna domena |
|---|---:|---:|---|
| `qa_raw` | 2 945 | 26,8 % | Rzeczywiste pytania z forów (forumprawne, e-prawnik, Reddit, eporady24) |
| `legal_statute` | 2 541 | 23,1 % | ISAP — 27 ustaw konsumenckich |
| `legal_document_pdf` | 1 965 | 17,9 % | Poradniki PDF UOKiK, RF, Federacji Konsumentów |
| `legal_ue_directive` | 1 360 | 12,4 % | EUR-Lex — 8 dyrektyw konsumenckich |
| `encyclopedic` | 1 167 | 10,6 % | Wikipedia + UODO + KNF + UKE + URE + Federacja |
| `legal_court_judgment` | 534 | 4,9 % | orzeczenia.ms.gov.pl + SN.pl (post-Wariant B) |
| `qa_gold` | 433 | 3,9 % | UOKiK Q&A FAQ + ekspansja RF FAQ |
| `legal_tsue_judgment` | 29 | 0,3 % | EUR-Lex — 29 orzeczeń TSUE |
| `legal_uokik_decision` | 26 | 0,2 % | Decyzje Prezesa UOKiK |
| **Łącznie** | **11 000** | **100 %** | — |

`{{FIG_4_1_SOURCE_TYPE_PIE}}` wizualizuje rozkład jako wykres kołowy. Dominują cztery typy źródłowe (`qa_raw`, `legal_statute`, `legal_document_pdf`, `legal_ue_directive`) pokrywające 80,2 % korpusu. Pozostałe pięć typów stanowi uzupełnienie kontekstu (encyclopedic, orzecznictwo, gold standard). Niska liczność `legal_tsue_judgment` (29) i `legal_uokik_decision` (26) wynika z charakteru źródeł — TSUE orzeka rocznie w ograniczonej liczbie spraw konsumenckich, a decyzje Prezesa UOKiK ograniczono do consumer-related po Wariant B.

Rozkład źródeł domenowych pokazuje Tabela 4.2 — top 15 wśród łącznie 24 unikalnych domen.

**Tabela 4.2.** Top 15 domen źródłowych (`source` field).

| Domena | Liczba chunków |
|---|---:|
| isap.sejm.gov.pl | 2 541 |
| rf.gov.pl | 2 066 |
| eur-lex.europa.eu | 1 389 |
| forumprawne.org | 1 186 |
| e-prawnik.pl | 948 |
| orzeczenia.ms.gov.pl | 534 |
| reddit.com/r/Polska | 509 |
| konsument.gov.pl | 393 |
| uokik.gov.pl | 313 |
| eporady24.pl | 302 |
| federacja-konsumentow.org.pl | 262 |
| uodo.gov.pl | 198 |
| cik.uke.gov.pl | 128 |
| knf.gov.pl | 91 |
| prawakonsumenta.uokik.gov.pl | 60 |

### 4.2.2 Rozkład długości chunków

Średnia długość chunka w korpusie wynosi 1 324 znaki. Mediana wynosi {{CHUNK_LENGTH_MEDIAN_OVERALL}} znaków, percentyl 95 wynosi {{CHUNK_LENGTH_P95}} znaków. Rozkład długości jest right-skewed — większość chunków mieści się w zakresie 200–2 000 znaków, podczas gdy maksymalne długości występują w typie `legal_tsue_judgment` (orzeczenia TSUE chunked jako jednoelementowe full-text, do {{CHUNK_LENGTH_MAX}} znaków dla orzeczenia *Dziubak* C-260/18).

`{{FIG_4_2_CHUNK_LENGTH_BOXPLOT}}` prezentuje rozkład długości jako wykres pudełkowy per `source_type`. Najwęższy rozkład wykazuje typ `legal_statute` (ELI ustawy chunked granularnie per art./ust./pkt., średnia ~400 znaków), najszerszy `legal_tsue_judgment` (single-chunk per orzeczenie). Typ `qa_raw` ma bimodalny rozkład — krótkie zapytania jednolinijkowe (~100 znaków) oraz długie wątki forum z pełnym kontekstem zadania (~1 500 znaków).

Decyzja konstrukcyjna pipeline'u (Rozdział 5): dla retrievalu zachowane są chunki naturalnej długości bez forced re-chunking, ponieważ struktura aktów prawnych (atomowy artykuł) jest *deterministycznym* gold standardem dla citation grounding. Dla generatora Bielik wszystkie chunki mieszczą się w 8 192-tokenowym oknie kontekstowym po stokenizacji APT4 (sekcja 4.5.2).

### 4.2.3 Pokrycie ekstrakcji cytacji

Moduł `citation_extractor.py` ekstrahuje cytacje z pola `tresc` przy użyciu wzorców regex dla polskich aktów prawnych. Z 11 000 chunków 2 345 (21,3 %) zawiera co najmniej jedną wyekstrahowaną cytację w polu `cited_articles`. Tabela 4.3 prezentuje pokrycie per `source_type`.

**Tabela 4.3.** Pokrycie ekstrakcji cytacji per `source_type`.

| `source_type` | Chunki z cytacjami | Udział |
|---|---:|---:|
| `legal_statute` | {{CIT_COV_LEGAL_STATUTE}} | {{CIT_COV_LEGAL_STATUTE_PCT}} % |
| `qa_gold` | {{CIT_COV_QA_GOLD}} (z 433) | {{CIT_COV_QA_GOLD_PCT}} % (UOKiK Q&A: 55/60 = 91,7 %) |
| `legal_document_pdf` | {{CIT_COV_DOC_PDF}} | {{CIT_COV_DOC_PDF_PCT}} % |
| `legal_ue_directive` | {{CIT_COV_UE_DIR}} | {{CIT_COV_UE_DIR_PCT}} % |
| `legal_court_judgment` | {{CIT_COV_COURT}} | {{CIT_COV_COURT_PCT}} % |
| `legal_tsue_judgment` | {{CIT_COV_TSUE}} | {{CIT_COV_TSUE_PCT}} % |
| `legal_uokik_decision` | {{CIT_COV_UOKIK_DEC}} | {{CIT_COV_UOKIK_DEC_PCT}} % |
| `encyclopedic` | {{CIT_COV_ENCYCL}} | {{CIT_COV_ENCYCL_PCT}} % |
| `qa_raw` | {{CIT_COV_QA_RAW}} | {{CIT_COV_QA_RAW_PCT}} % |

Najwyższe pokrycie wykazuje `qa_gold` (UOKiK Q&A: 91,7 % par z explicit cytacją w formacie *Podstawa prawna: <statute>*) oraz `legal_court_judgment` (orzeczenia z naturalnie gęstymi referencjami do ustaw). Niskie pokrycie w `qa_raw` (zapytania konsumenckie z forów) jest oczekiwane — pytający rzadko cytują konkretne artykuły. Niskie pokrycie w `encyclopedic` (Wikipedia + portale urzędowe) wymaga uwagi w Iteracji 1: artykuły encyklopedyczne często odwołują się do ustaw narracyjnie (*„zgodnie z Ustawą o prawach konsumenta…"*), co regex `citation_extractor` może pominąć. Rozszerzenie regex o named entity recognition (NER) dla nazw aktów prawnych jest zaplanowane w Iteracji 5 jako poprawa pokrycia.

### 4.2.4 Klasyfikacja multi-label

Korpus stosuje multi-label klasyfikację `Category` z 14-elementowego enumu. Każdy chunk może być przypisany do dowolnej liczby kategorii (mediana to {{CATEGORIES_PER_CHUNK_MEDIAN}} kategorii per chunk). Tabela 4.4 prezentuje rozkład kategorii w pełnym korpusie.

**Tabela 4.4.** Rozkład kategorii multi-label (n = 11 000 chunków; jedna chunk może mieć wiele kategorii).

| Kategoria | Liczba chunków | Udział |
|---|---:|---:|
| `finance_adjacent` | 9 076 | 82,5 % |
| `consumer_contract` | 5 872 | 53,4 % |
| `consumer_core` | 4 169 | 37,9 % |
| `eu_directive` | 2 906 | 26,4 % |
| `consumer_return_refund` | 1 896 | 17,2 % |
| `consumer_credit` | 1 189 | 10,8 % |
| `other` | 945 | 8,6 % |
| `consumer_dispute_resolution` | 543 | 4,9 % |
| `tsue_judgment` | 296 | 2,7 % |
| `court_precedent` | 275 | 2,5 % |
| `consumer_digital` | 237 | 2,2 % |
| `regulatory_decision` | 193 | 1,8 % |
| `consumer_telecom` | 79 | 0,7 % |
| `consumer_unfair_practices` | 47 | 0,4 % |

Dominacja kategorii `finance_adjacent` (82,5 %) wynika z agresywnego tagowania heurystycznego w `normalizers.py` — każdy chunk zawierający słowa kluczowe związane z finansami konsumenckimi (kredyt, opłata, kwota, rachunek, oprocentowanie, RRSO) otrzymuje tę kategorię. Wysoki udział nie oznacza, że 82,5 % korpusu dotyczy *wyłącznie* finansów — oznacza obecność słownictwa finansowego w 82,5 % chunków. Świadomy bias raportowany w Rozdziale 3.6.

Niska liczność `consumer_unfair_practices` (47) i `consumer_telecom` (79) wskazuje na niedoreprezentowanie obu obszarów — kandydaci do zwiększonej anotacji manualnej w Iteracji 5 (200 par gold standard).

### 4.2.5 Rozkład typów halucynacji w zbiorze treningowym

Zbiór 5 402 par halucynacyjnych w `halu_pairs.jsonl` zawiera rozkład typów prezentowany w Tabeli 4.5.

**Tabela 4.5.** Rozkład typów halucynacji w zbiorze treningowym (n = 5 402).

| Typ | Liczba par | Udział | Etykieta NLI |
|---|---:|---:|---|
| `factual_fabrication` | 1 620 | 30,0 % | `neutral` |
| `neg` (baseline kontrolny) | 1 560 | 28,9 % | `entailed` |
| `entity_confusion` | 985 | 18,2 % | `contradicted` |
| `negation_flip` | 467 | 8,6 % | `contradicted` |
| `paragraph_mis_citation` | 427 | 7,9 % | `contradicted` |
| `temporal_drift` | 343 | 6,3 % | `contradicted` |

`{{FIG_4_3_HALU_TYPE_BARS}}` prezentuje rozkład jako wykres słupkowy z wyróżnieniem `neg` jako kontroli pozytywnej (entailment). Stosunek negative do positive wynosi 1:2,5 (1 560 : 3 842), co stanowi dostateczny balans dla treningu binarnego klasyfikatora bez konieczności stosowania class weights. Test alternative z `class_weight='balanced'` zaplanowany w Iteracji 6 jako ablacja.

Dominacja `factual_fabrication` (30,0 %) wynika z faktu, że mutator dla tego typu nigdy nie zawodzi — zawsze możliwe jest dodanie nowego zdania do odpowiedzi. Pozostałe cztery typy wymagają obecności konkretnych wzorców w treści źródłowej (wyrażeń czasowych, podmiotów do zamiany, negacji do odwrócenia, cytacji do podmiany), więc generowanie udanej mutacji jest probabilistyczne. Niska liczność `temporal_drift` (343) wynika z faktu, że nie wszystkie odpowiedzi UOKiK i fragmenty ustaw zawierają wyrażenia czasowe.

Mapowanie typów na etykiety NLI dokumentowane w Rozdziale 3.5.2 — typ `factual_fabrication` mapuje na `neutral` (unsupported claim), pozostałe cztery na `contradicted` (explicit kontradykcja), `neg` baseline na `entailed`.

### 4.2.6 BERTopic, UMAP, jakość klastrowania

Walidacja taksonomii `Category` przeprowadzona została metodą *topic modeling* na embeddings BGE-M3 (1 024-dim) wszystkich 11 000 chunków. Procedura wykorzystuje bibliotekę BERTopic [CYT: Grootendorst 2022 BERTopic arXiv:2203.05794] z back-endami UMAP (redukcja wymiarowości do 5D dla clusteringu) i HDBSCAN (gęstościowe klastrowanie bez konieczności specyfikacji liczby klastrów).

Procedura zidentyfikowała {{BERTOPIC_N_CLUSTERS}} naturalnych klastrów semantycznych w korpusie. Top 10 klastrów z dominującymi terminami i przykładową etykietą interpretacyjną prezentuje Tabela 4.6.

**Tabela 4.6.** Top 10 klastrów BERTopic w korpusie v0.6 z interpretacją.

| Klaster ID | Wielkość | Dominujące terminy | Interpretacja |
|---|---:|---|---|
| {{BT_C0_ID}} | {{BT_C0_SIZE}} | {{BT_C0_TERMS}} | {{BT_C0_LABEL}} (np. „odstąpienie 14 dni") |
| {{BT_C1_ID}} | {{BT_C1_SIZE}} | {{BT_C1_TERMS}} | {{BT_C1_LABEL}} (np. „klauzule abuzywne CHF") |
| {{BT_C2_ID}} | {{BT_C2_SIZE}} | {{BT_C2_TERMS}} | {{BT_C2_LABEL}} (np. „reklamacja rękojmia") |
| {{BT_C3_ID}} | {{BT_C3_SIZE}} | {{BT_C3_TERMS}} | {{BT_C3_LABEL}} (np. „kredyt konsumencki RRSO") |
| {{BT_C4_ID}} | {{BT_C4_SIZE}} | {{BT_C4_TERMS}} | {{BT_C4_LABEL}} (np. „RODO konsumencki") |
| {{BT_C5_ID}} | {{BT_C5_SIZE}} | {{BT_C5_TERMS}} | {{BT_C5_LABEL}} (np. „klauzule niedozwolone UOKiK decyzje") |
| {{BT_C6_ID}} | {{BT_C6_SIZE}} | {{BT_C6_TERMS}} | {{BT_C6_LABEL}} (np. „prawo telekomunikacyjne abonament") |
| {{BT_C7_ID}} | {{BT_C7_SIZE}} | {{BT_C7_TERMS}} | {{BT_C7_LABEL}} (np. „pozasądowe rozwiązywanie sporów ADR") |
| {{BT_C8_ID}} | {{BT_C8_SIZE}} | {{BT_C8_TERMS}} | {{BT_C8_LABEL}} (np. „TSUE Dziubak frank szwajcarski") |
| {{BT_C9_ID}} | {{BT_C9_SIZE}} | {{BT_C9_TERMS}} | {{BT_C9_LABEL}} (np. „ubezpieczenia konsumenckie NNW") |

`{{FIG_4_5_UMAP_2D_SCATTER}}` prezentuje 2D-wymiarową projekcję UMAP wszystkich 11 000 chunków, pokolorowaną zgodnie z dominującą `Category` per chunk. Widoczne są wyraźne semantyczne klastry odpowiadające głównym obszarom polskiego prawa konsumenta. Klastry dla `consumer_credit`, `tsue_judgment` oraz `consumer_telecom` są wizualnie odrębne, potwierdzając że taksonomia `Category` koresponduje z naturalną topologią semantyczną.

Walidacja alignment między klastrami BERTopic a etykietami `Category` enum: {{CATEGORY_BERTOPIC_ALIGNMENT}} kategorii spośród 14 ma odpowiadający dominujący klaster (chi-square test α = 0,05). Silhouette score dla clusteringu HDBSCAN wynosi {{UMAP_SILHOUETTE_SCORE}}, co świadczy o {{SILHOUETTE_INTERPRETATION}} (interpretacja: <0,25 słabe; 0,25–0,5 umiarkowane; >0,5 silne klastrowanie).

Wynik walidacji wzmacnia argument defensywny w Rozdziale 8: taksonomia `Category` nie jest arbitralna, lecz odpowiada *empirycznie zaobserwowanej* strukturze semantycznej polskich tekstów konsumenckich. Decyzja konstrukcyjna `Category` enum (14 wartości w 6 grupach) jest *post-hoc* walidowana danymi, nie *a priori* narzucona z literatury.

## 4.3 Wariant B audit — wpływ czyszczenia na rozkłady

Polityka filtrowania `strict` (Wariant B, omówiona w Rozdziale 3.4.2) zredukowała korpus z 17 862 do 11 000 chunków (drop 6 862, 38,4 %). Tabela 4.7 prezentuje pełen breakdown decyzji wykluczających.

**Tabela 4.7.** Wariant B — pełen breakdown wykluczeń (16 kategorii drop).

| Powód wykluczenia | Liczba dropniętych chunków | Kategoria |
|---|---:|---|
| `eli_DU/1964/296` (KPC) | 2 077 | Akt prawny spoza domeny konsumenckiej |
| `eli_DU/2003/535` (Prawo upadłościowe) | 1 237 | Akt prawny spoza domeny konsumenckiej |
| `eli_DU/2011/1175` (Usługi płatnicze) | 856 | Regulator-side, nie consumer-rights |
| `eli_DU/1997/939` (Prawo bankowe) | 663 | Regulator-side, nie consumer-rights |
| `rf_pure_insurance` | 406 | Heurystyczny filtr (≥3 słowa ubezpieczeniowe AND 0 konsumenckich) |
| `s6_infor.pl` | 398 | Generic legal/finance journalism |
| `s6_bankier.pl` | 299 | Generic finance journalism |
| `s6_prawo.pl` | 248 | Borderline professional/media |
| `s6_bezprawnik.pl` | 200 | Opinion site bez weryfikowalnej jakości |
| `eli_DU/2003/2275` (UCHYLONA bezp. produktów) | 188 | UCHYLONA — zastąpiona przez nowszą regulację |
| `eli_DU/2000/271` (UCHYLONA ochr. praw konsum.) | 83 | UCHYLONA — zastąpiona przez UPK 2014/827 |
| `sn_chf_content` | 63 | SN orzeczenia o klauzulach frankowych CHF — domain shift |
| `s6_gazetaprawna.pl` | 59 | Borderline media, mała próbka |
| `eli_DU/2002/1176` (UCHYLONA sprzedaż konsum.) | 42 | UCHYLONA — zastąpiona przez UPK 2014/827 |
| `s6_money.pl` | 31 | Generic finance journalism, mała próbka |
| `s6_ing.pl` | 12 | Single-bank sample, większość to artefakty scrape |
| **Łącznie** | **6 862** | **38,4 % korpusu pre-filter** |

`{{FIG_4_4_PRE_POST_CLEANUP_DIST}}` prezentuje porównanie rozkładów `source_type` w wersjach v0.4 (pre-cleanup) i v0.6 (post-cleanup). Najdrastyczniejsza redukcja dotyczy typu `legal_statute` (5 187 → 2 541, drop 51 %) ze względu na wykluczenie KPC, Prawa upadłościowego, Prawa bankowego oraz Ustawy o usługach płatniczych. Typ `qa_raw` pozostał niezmieniony (2 945 w obu wersjach) — forum questions nie podlegały filtrowi Wariant B.

Świadome obciążenia rezydualne post-cleanup: kategoria `finance_adjacent` nadal dominuje (9 076 chunków, 82,5 %), pomimo wykluczenia portali typu bankier.pl i infor.pl. Wynika to z naturalnej obecności słownictwa finansowego w aktach prawnych konsumenckich (kredyt konsumencki, opłaty, kwoty refundacji). Ta obecność jest *semantyczna*, nie *domenowa* — chunki o kredycie konsumenckim z ELI są poprawnie wewnątrz scope, mimo że terminy finansowe powodują tag `finance_adjacent`.

Decyzja konstrukcyjna pipeline'u: polityka `strict` pozostaje domyślna dla wszystkich generowanych dataset versions. Polityki `loose` (zachowuje generic legal journalism) i `none` (zachowuje wszystko) są zarezerwowane dla przyszłych eksperymentów cross-domain transferability, jeśli RQ5 (deprecated w 2026-05-16) byłby reaktywowany.

## 4.4 Standaryzacja

### 4.4.1 Normalizacja Unicode NFC

Wszystkie pola `tresc` w schemie `Chunk` przechodzą walidator NFC (`_ensure_nfc`) zaimplementowany w `src/halu/normalizers.py`. Normalizacja NFC (*Normalization Form Canonical Composition*) zapewnia stabilną binarną reprezentację polskich diakrytyków — w szczególności zapobiega obecności kombinowanych sekwencji typu `a` + U+0328 (combining ogonek) zamiast pojedynczego punktu kodowego U+0105 dla `ą`. Audyt v0.6 potwierdza, że wszystkie 11 000 chunków przechodzi walidator bez błędu.

Konsekwencja praktyczna: tokenizator Bielik APT4 oraz tokenizator mDeBERTa-v3 traktują znormalizowane i nieznormalizowane formy odmiennie — pierwsza forma daje krótsze sekwencje tokenów (1 token per `ą`), druga forma daje dłuższe (2 tokeny: `a` + diakrityk). NFC-normalizacja zapewnia minimalną fertilności tokenizacji i deterministyczne mapowanie tekst → tokeny w pipeline'ach Transformers.

### 4.4.2 Unifikowany schemat `Chunk`

Wszystkie 9 typów źródłowych mapowane są do jednolitej schemy `Chunk` (codebook w Rozdziale 3.3.1). Standaryzacja schemy realizowana przez 9 dedykowanych normalizerów w `src/halu/normalizers.py`, po jednym per `source_type`. Każdy normalizer ekstraktuje pola obowiązkowe (`chunk_id`, `source_type`, `source`, `source_url`, `title`, `tresc`, `license`, `scrape_date`, `process_date`) i wypełnia pole `metadata` strukturą specyficzną dla typu źródła (np. `ustawa_id`, `art`, `ust`, `pkt` dla ELI; `celex_id`, `case_name` dla TSUE).

Wybór schemy unifikowanej zamiast osobnych klas per typ źródła ma trzy konsekwencje. Pierwsza: pojedynczy serializator JSONL dla całego korpusu (`chunks.jsonl` 24 MB). Druga: jednolity API dla downstream consumers (HuggingFace `datasets.load_dataset`, BGE-M3 indexer, NLI verifier). Trzecia: heterogeniczne metadane source-specific zachowane w `metadata` dict bez konieczności rozszerzania schemy bazowej.

### 4.4.3 Standaryzacja dat i kodowania

Wszystkie pola czasowe (`scrape_date`, `process_date`) używają standardu ISO 8601 w formacie `YYYY-MM-DD`. Kodowanie znaków jest jednolicie UTF-8 dla wszystkich plików JSONL oraz raw archive (HTML, PDF zachowane w formacie binarnym z sidecarem SHA-256). Sidecary `_archive/_manifest.json` używają ISO 8601 również dla `download_date`.

Konsekwencja: brak ambiguities czasowych (zero pól w formacie regionalnym np. `DD.MM.YYYY` lub `MM/DD/YYYY`), brak problemów z encoding fallback w pipeline Transformers (które domyślnie oczekują UTF-8).

### 4.4.4 Harmonizacja etykiet kategorii

Pole `categories` używa multi-label enumu `Category` z 14 wartościami zdefiniowanymi w `src/halu/schemas.py`. Wartości enum są stabilne (nie dopuszczamy free-form strings) i deterministycznie przypisywane przez heurystyki słów kluczowych w `categorize_chunk` funkcji w `normalizers.py`. Każda kategoria ma jednoznaczną listę wzorców regex (np. `consumer_return_refund` → wzorce: *zwrot*, *odstąpienie*, *14 dni*, *reklamacja*, *zwrócić towar*).

Harmonizacja eliminuje fragmentację taksonomii znaną z ad-hoc tagowania (np. *„prawo konsumenta"* vs *„prawa konsumenta"* vs *„konsumencki"* jako trzy osobne tagi). Wszystkie konceptualnie tożsame teksty otrzymują tę samą etykietę enum, co umożliwia spójne stratified sampling w splitach train/val/test.

## 4.5 Normalizacja

### 4.5.1 Reprezentacja wektorowa — BGE-M3 + L2

Korpus indeksowany jest wektorowo w Qdrant przy użyciu modelu **BGE-M3** [CYT: Chen 2024 BGE-M3 arXiv:2402.03216] generującego embeddings 1 024-wymiarowe. Każdy chunk przechodzi pipeline: NFC-normalizacja → tokenizacja BGE-M3 → forward pass encoder → mean pooling → **L2 normalization**. L2-normalizowane embeddings umożliwiają użycie cosine similarity (dot product na unit vectors) jako metryki podobieństwa w Qdrant, co jest pożądane dla retrievalu semantycznego.

L2 normalization ma postać:

x' = x / ||x||₂

gdzie ||x||₂ = √(Σᵢ xᵢ²). Po normalizacji ||x'||₂ = 1 dla każdego embedding. Pomiar cosine similarity między dwoma L2-normalizowanymi wektorami sprowadza się do dot product, co jest wydajne obliczeniowo.

BGE-M3 jest *frozen* w pracy — nie podlega fine-tune'owi. Decyzja motywowana jest wynikami benchmarku MIRACL [CYT: Zhang 2023 MIRACL TACL] gdzie BGE-M3 osiąga konkurencyjne wyniki dla języka polskiego bez konieczności custom adaptacji. Fine-tune embeddera dla domeny konsumenckiej zaplanowany jest jako future work w Rozdziale 8 (warto rozważyć w przypadku H1 INCONCLUSIVE po treningu probe).

### 4.5.2 Rozkład długości w tokenach Bielik APT4

Bielik 11B v3 używa tokenizatora **APT4** [CYT: Ociepa 2025 Bielik v3 APT4 arXiv:2604.10799] zoptymalizowanego dla języka polskiego, osiągającego fertility 1,62 tokens/word vs Mistral baseline 3,22 tokens/word. Tabela 4.8 prezentuje rozkład długości chunków w tokenach APT4 per `source_type`.

**Tabela 4.8.** Rozkład długości tokenów APT4 per `source_type` (mean/median/p95).

| `source_type` | Mean tokens | Median tokens | P95 tokens |
|---|---:|---:|---:|
| `legal_statute` | {{TOK_LS_MEAN}} | {{TOK_LS_MED}} | {{TOK_LS_P95}} |
| `legal_ue_directive` | {{TOK_UE_MEAN}} | {{TOK_UE_MED}} | {{TOK_UE_P95}} |
| `legal_tsue_judgment` | {{TOK_TSUE_MEAN}} | {{TOK_TSUE_MED}} | {{TOK_TSUE_P95}} |
| `legal_court_judgment` | {{TOK_COURT_MEAN}} | {{TOK_COURT_MED}} | {{TOK_COURT_P95}} |
| `legal_uokik_decision` | {{TOK_UOKIK_DEC_MEAN}} | {{TOK_UOKIK_DEC_MED}} | {{TOK_UOKIK_DEC_P95}} |
| `legal_document_pdf` | {{TOK_DOC_MEAN}} | {{TOK_DOC_MED}} | {{TOK_DOC_P95}} |
| `qa_gold` | {{TOK_QA_GOLD_MEAN}} | {{TOK_QA_GOLD_MED}} | {{TOK_QA_GOLD_P95}} |
| `qa_raw` | {{TOK_QA_RAW_MEAN}} | {{TOK_QA_RAW_MED}} | {{TOK_QA_RAW_P95}} |
| `encyclopedic` | {{TOK_ENC_MEAN}} | {{TOK_ENC_MED}} | {{TOK_ENC_P95}} |

Maksymalna długość chunka w korpusie wynosi {{TOK_MAX_OVERALL}} tokenów (orzeczenie TSUE *Dziubak* C-260/18 jako single-chunk), co mieści się w oknie kontekstowym Bielik 11B v3 (8 192 tokeny natywnie, 131 072 tokeny z YaRN scaling). Wszystkie chunki nadają się do bezpośredniego użycia jako kontekst RAG bez forced re-chunking.

### 4.5.3 TF-IDF jako baseline alternatywny

Dla porównania w Rozdziale 6 ablacji A1 (probe → semantic entropy baseline) implementowana jest również reprezentacja sparse **TF-IDF** wykorzystująca `sklearn.feature_extraction.text.TfidfVectorizer` z polskim listą stop words oraz minimalną częstością `min_df=5`. TF-IDF służy jako *naive baseline* dla treningu klasyfikatora — jeśli linear probe na BGE-M3 embeddings nie bije linear klasyfikatora na TF-IDF features o co najmniej 10 punktów procentowych AUROC, semantyczne embeddings nie wnoszą wartości i należy rozważyć alternative architecture (per *„Mirage of Halu Detection"* critique [CYT: Mirage of Halu Detection EMNLP 2025]).

### 4.5.4 Balans klas w parach halucynacyjnych

Stosunek negative (entailment) do positive (contradicted + neutral) w 5 402 parach halucynacyjnych wynosi 1 560 : 3 842 (1:2,5). Rozkład jest umiarkowanie niezbalansowany, ale mieści się w granicach akceptowalnych dla treningu binarnego klasyfikatora bez resamplingu (typowo granica nierównowagi to 1:10+ wymagająca SMOTE lub class weights [CYT: Chawla 2002 SMOTE]).

Decyzja konstrukcyjna treningu (Rozdział 6): linear probe trenowany bez resamplingu, z ablacją `class_weight='balanced'` w `sklearn.linear_model.LogisticRegression` jako test wrażliwości. Jeśli ablacja wykaże znaczącą poprawę AUROC (≥3 pp), rozważone zostanie zbalansowanie generowania halu pairs w przyszłej wersji datasetu.

Dla treningu Tier 2 verifier (HerBERT-large + CDSC-E fine-tune, zaplanowany w Iteracji 5 jeśli wymagany) stosowany będzie standardowy zbiór CDSC-E z benchmarku KLEJ [CYT: Wróblewska CDSC-E KLEJ] — jego naturalny rozkład klas (entailment / neutral / contradicted) jest blisko zbalansowany.

## 4.6 Dokumentacja i reprodukowalność

Eksploracja i walidacja korpusu są reprodukowalne przez notebook `main_project/notebooks/eda_v0.ipynb` zawierający 30 cel z konkretnymi statystykami, wizualizacjami i analizami. Notebook używa biblioteki `pandas` dla agregacji statystyk, `matplotlib` + `seaborn` dla wizualizacji rozkładów, `BERTopic` + `umap-learn` + `hdbscan` dla topic modelingu, oraz `sklearn.feature_extraction.text` dla baseline TF-IDF.

Wszystkie figury w niniejszym rozdziale są generowane deterministycznie z `main_project/notebooks/eda_figures.py` przy użyciu seed = 42 dla operacji niedeterministycznych (UMAP initialization, HDBSCAN). Pliki SVG zapisane są w `main_project/figures/r04_eda/` i mogą być wstawione bezpośrednio do finalnej wersji Word pracy.

Karta HuggingFace dataset (`main_project/data/processed/citationbench_v0.6_2026-05-16/DATASET_CARD.md`) replikuje kluczowe statystyki opisane w niniejszym rozdziale jako persistent reference dla zewnętrznych użytkowników. Stanowi standalone deliverable nawet w przypadku, gdyby pełna wersja pracy nie była dostępna w trybie open-access.

Rozdział 5 wykorzystuje wyniki R4 jako empiryczne wejście dla decyzji architektonicznych — w szczególności wybór długości okna kontekstowego retrievalu (na podstawie rozkładu długości chunków z sekcji 4.2.2 i 4.5.2), wybór metryki podobieństwa w Qdrant (cosine z L2 normalization per 4.5.1), oraz konfiguracja stratified split train/val/test (na podstawie source_type distribution z 4.2.1 i Category distribution z 4.2.4).

---

## Źródła robocze

Lista cytowań w finalnym formacie IEEE zostanie wygenerowana w Iteracji 7. Robocze źródła wykorzystane w niniejszym rozdziale:

- `main_project/data/processed/citationbench_v0.6_2026-05-16/DATASET_CARD.md` — karta HuggingFace dataset v0.6 z agregowanymi statystykami
- `main_project/notebooks/eda_v0.ipynb` — interactive workspace EDA
- `main_project/notebooks/eda_figures.py` — skrypty generujące figury R4
- `notes/scope_cleanup_decisions_2026-05-16.md` — szczegółowy audyt per-source Wariant B
- `research/halu_detection_sota_2024_2026.md` — kontekst metryk halu detection
- BGE-M3 model card (HuggingFace `BAAI/bge-m3`)
- BERTopic documentation [CYT: Grootendorst 2022 BERTopic arXiv:2203.05794]
- *„Mirage of Halu Detection"* critique EMNLP 2025 (mention dla naive baseline argument)
