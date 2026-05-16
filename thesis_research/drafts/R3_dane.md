# R3. Dane

> **Status dokumentu:** *skeleton* po Iteracji 1a (2026-05-16). Metodologia w sekcjach 3.1–3.10 napisana w pełni; liczby pochodzące z eksperymentów oznaczone jako `[TBD post-Iteracja N]`. Pełen *prose draft* powstaje w Iteracji 7 zgodnie z konwencją *build-first, finalize-last* (`02_konspekt_v3.2_skeleton.md`, sekcja II.11).
> **Wersja konspektu źródłowego:** v3.2 (post-DEC-003 pivot, *citation-grounded RAG* + *hallucination detection* w domenie praw konsumenta).
> **Zgodność z wymaganiami formalnymi:** Task 03 PJATK (10 pkt) oraz PRO-D Assignment 5 (Data Preparation and EDA) — patrz mapowanie sekcji w 3.11.

---

## 3.0 Wprowadzenie do rozdziału

Rozdział opisuje **korpus danych** wykorzystany do projektowania, trenowania i ewaluacji trzykomponentowego potoku *citation-grounded* polskiego *retrieval-augmented generation* (RAG) z wykrywaniem halucynacji metodą *hidden-states probe* (sondy aktywacji wewnętrznych modelu językowego). Dziedziną testową są **polskie prawa konsumenta** — wybór uzasadniony deterministyczną strukturą cytowań prawnych (*European Legislation Identifier*, ELI) oraz dostępnością publicznego eksperckiego korpusu pytań i odpowiedzi (UOKiK).

Struktura rozdziału realizuje dziesięć podsekcji wymaganych przez Task 03 PJATK (sekcje 3.1–3.10), uzupełnionych o mapowanie do PRO-D Assignment 5 (sekcja 3.11). Sekcja 3.2 (Metodologia doboru źródeł) ma charakter rozbudowany, zgodnie z uwagą krytyczną promotora do wcześniejszej wersji pracy (ocena 6/10 za przegląd literatury), w której wytknięto słabość *source selection methodology*.

---

## 3.1 Modalności danych

### 3.1.1 Zakres modalności

Praca operuje wyłącznie na dwóch modalnościach:

1. **Tekst** (*text*) — akty prawne, eksperckie pary pytanie–odpowiedź, autentyczne pytania konsumenckie z portali prawniczych. Stanowi rdzeń korpusu (≈99% objętości).
2. **Dane tabelaryczne** (*tabular*) — metadane towarzyszące (kategorie, daty publikacji, identyfikatory aktów, etykiety wieloznakowe tematów, identyfikatory cytowań). Reprezentowane w JSONL oraz Parquet jako pola strukturalne.

### 3.1.2 Modalności wyłączone (*out of scope*)

| Modalność | Uzasadnienie wykluczenia |
|---|---|
| Obraz (*image*) | Brak ekwiwalentu wizualnego dla aktów prawnych; rysunki w decyzjach UOKiK nie są nośnikami informacji prawnej. |
| Dźwięk (*audio*) | Brak źródeł audio w domenie praw konsumenta o jakości pozwalającej na fine-tuning. |
| Wideo (*video*) | Jak wyżej. |
| Dane sensoryczne (*sensor*) | Niezwiązane z dziedziną. |

Decyzja ograniczenia do dwóch modalności została podjęta w DEC-003 jako konsekwencja przeniesienia akcentu pracy z *cross-modal retrieval* na *citation grounding* w pojedynczej modalności tekstowej.

### 3.1.3 Skala korpusu

Stan po Iteracji 1a (2026-05-16):

| Komponent | Liczba elementów | Status |
|---|---:|---|
| Akty prawne (chunks ELI) | 2 123 | ✅ scraped |
| Eksperckie pary Q&A (UOKiK) | 60 | ✅ scraped |
| Autentyczne pytania konsumenckie | 2 967 | ✅ scraped |
| **Razem (Iteracja 1a)** | **5 150** | |
| Pary z ręcznymi adnotacjami autorki | 50–100 | ⏳ planowane (Iteracja 1b) |
| Syntetyczne pary z wstrzykniętą halucynacją | 5 000 – 10 000 | ⏳ planowane (Iteracja 1b) |
| **Cel docelowy korpusu** | **≈10 000 – 15 000 par** | |

Tabela 3.1.1 podsumowuje aktualne i planowane wolumeny korpusu.

---

## 3.2 Metodologia doboru źródeł

Niniejsza sekcja stanowi *substantive expansion* w odpowiedzi na uwagę promotora z poprzedniej pracy dyplomowej autorki: *„Potrzebna bardziej rygorystyczna metodologia selekcji źródeł"*. Sekcja przedstawia cztery elementy: kryteria włączenia, kryteria wykluczenia, strategię wyszukiwania oraz potok selekcji wraz z liczbami źródeł testowanych i przyjętych.

### 3.2.1 Kryteria włączenia (*inclusion criteria*)

Każde źródło zakwalifikowane do korpusu musi spełniać **pięć** kryteriów łącznie:

| # | Kryterium | Uzasadnienie |
|---|---|---|
| W1 | **Treść w języku polskim** | Praca dotyczy polskiego RAG; *cross-lingual transfer* poza zakresem (DEC-003, sekcja II.10 konspektu v3.2). |
| W2 | **Status: domena publiczna lub licencja zgodna z badaniami naukowymi** | Wymogi prawno-etyczne (art. 4 PrAut, *Text and Data Mining exception* z września 2024). |
| W3 | **Bezpośrednia relewancja dla praw konsumenta** | Zawężenie domeny pozwala na *deterministic citation grounding* (sekcja 3.4). |
| W4 | **Programatyczna dostępność do pobrania** (REST API, statyczny HTML, kanał *bulk download*) | Wymóg reprodukowalności (sekcja 3.9) oraz iteracyjnego *re-scrape*. |
| W5 | **Możliwość weryfikacji integralności** (*deterministic identifier*, np. URL kanoniczny, ID aktu, ID wątku) | Wymóg dla detekcji duplikatów oraz dla śledzenia zmian źródła w czasie. |

### 3.2.2 Kryteria wykluczenia (*exclusion criteria*)

Sześć powodów odrzucenia źródła rozpoznawanych w trakcie *selection pipeline*:

| # | Powód | Przykład |
|---|---|---|
| Wy1 | **Treść za *paywallem* lub wymaga logowania** | Komercyjne bazy prawne (Lex, LegalisOnline). |
| Wy2 | **Licencja zabrania *scrape* lub redystrybucji** | eporady24.pl — opłata licencyjna 25 zł / 1000 znaków (patrz sekcja 3.8). |
| Wy3 | **Domena martwa lub nieosiągalna** | `poradnik-konsumenta.pl` (DNS resolution failed), `lexlege.pl` (404). |
| Wy4 | **False positive na nazwie domeny** | `legalny.pl` — bukmacher, nie serwis prawny. |
| Wy5 | **Brak realnej sekcji Q&A** | `infor.pl/prawo/konsument` — redirekt do strony głównej. |
| Wy6 | **Treść poza dziedziną praw konsumenta** | Sekcje pracy, prawa karnego, prawa rodzinnego na ogólnych forach. |

### 3.2.3 Strategia wyszukiwania (*search strategy*)

Wyszukiwanie źródeł przeprowadzono w **trzech rundach** o rosnącej selektywności:

1. **Runda 1 — akty prawne (źródła pierwotne).** Identyfikacja aktów prawa konsumenckiego z wykorzystaniem rejestru ISAP (*Internetowy System Aktów Prawnych*) Sejmu RP. Kryterium operacyjne: akt regulujący relację B2C lub mechanizmy ochrony konsumenta. Pełny tekst pobierany przez ELI API (`api.sejm.gov.pl/eli`).
2. **Runda 2 — eksperckie pary Q&A (gold standard).** Identyfikacja źródeł zawierających pytania konsumenckie z eksperckimi odpowiedziami oraz **explicit cytowanie aktu prawnego**. Kluczowe odkrycie: portal `prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/` zawiera *ready-made* pary Q&A z polem *Podstawa prawna*. Stanowi to gotowy *gold standard* eliminujący konieczność ręcznej anotacji 60 par.
3. **Runda 3 — autentyczne pytania konsumenckie (*real questions*).** Identyfikacja źródeł autentycznych pytań użytkowników w celu uzyskania realnej dystrybucji form zapytań (nie wystylizowanych eksperckich). Cztery równoległe podźródła: portale prawnicze (e-prawnik.pl, forumprawne.org), *legacy fallback* (eporady24.pl) oraz *social* (Reddit r/Polska + r/Polska_wpz).

### 3.2.4 Potok selekcji (*selection pipeline*) — liczby

Tabela 3.2.1 przedstawia faktyczne wyniki selekcji.

**Tabela 3.2.1.** Wyniki *selection pipeline* (stan na 2026-05-16).

| Etap | Liczba źródeł testowanych | Liczba przyjętych | Liczba odrzuconych | Główne powody odrzucenia |
|---|---:|---:|---:|---|
| Runda 1 (akty prawne) | 9 aktów rozważanych | 6 | 3 | Wy6 (poza dziedziną) |
| Runda 2 (Q&A z cytowaniami) | 4 portale rozważane | 1 (UOKiK) | 3 | Wy1, Wy3 |
| Runda 3 (autentyczne pytania) | 12 portali rozważanych | 4 | 8 | Wy3 (5×), Wy4 (1×), Wy5 (2×) |
| **Razem** | **25 źródeł** | **11** | **14** | — |

Szczegółowy audyt 14 odrzuconych źródeł znajduje się w pliku `thesis_research/research/domain_A_feasibility.md` (sekcja 2 oraz 3.3).

### 3.2.5 Finalna kompozycja korpusu — trzy strata

Korpus składa się z **trzech strat** o komplementarnej charakterystyce:

1. **Stratum A — akty prawne (źródła pierwotne).** Deterministyczna struktura cytowań, *public domain* (art. 4 PrAut). Funkcja w potoku: **baza wiedzy retrievera** (indeks Qdrant).
2. **Stratum B — eksperckie pary Q&A (UOKiK).** Para *(pytanie, odpowiedź, cytowane artykuły)* w jednostce atomowej. Funkcja w potoku: **gold standard ewaluacyjny** dla RQ2 (*citation grounding faithfulness/correctness*) oraz RQ4 (*verifier quality*).
3. **Stratum C — autentyczne pytania konsumenckie.** Realna dystrybucja form zapytań. Funkcja w potoku: **distribution dla syntetycznej generacji halucynacji** (sekcja 3.5) oraz *stress test set* dla RQ1 (*probe quality*).

Wybór trzech strat (a nie pojedynczego źródła) jest świadomą decyzją w odpowiedzi na *single-source bias risk* dyskutowany w sekcji 3.10.

---

## 3.3 Trzy strata szczegółowo

### 3.3.1 Stratum A — akty prawne (ELI ISAP)

Stratum A zawiera **2 123 chunks** z **sześciu aktów prawa konsumenckiego**, pobranych z oficjalnego API ELI Sejmu RP w dniu 2026-05-16. Tabela 3.3.1 przedstawia rozkład chunks per akt.

**Tabela 3.3.1.** Stratum A — akty prawne (rozkład chunks).

| ID ELI | Krótki tytuł | Data uchwalenia | Chunks | Udział |
|---|---|---|---:|---:|
| DU/2014/827 | Ustawa o prawach konsumenta | 30.05.2014 | 240 | 11,3% |
| DU/1964/93 | Kodeks cywilny (art. 384–385, 535–581) | 23.04.1964 | 92 | 4,3% |
| DU/2007/1206 | Ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym | 23.08.2007 | 113 | 5,3% |
| DU/2007/331 | Ustawa o ochronie konkurencji i konsumentów | 16.02.2007 | 500 | 23,6% |
| DU/2011/1175 | Ustawa o usługach płatniczych | 19.08.2011 | 888 | 41,8% |
| DU/2016/1823 | Ustawa o pozasądowym rozwiązywaniu sporów konsumenckich | 23.09.2016 | 290 | 13,7% |
| **Razem** | | | **2 123** | **100%** |

**Wybór sześciu aktów (a nie pełnej *core 4*):** uzasadniony pokryciem typowych ścieżek konsumenckich: zawarcie umowy (DU/2014/827), wady i rękojmia (DU/1964/93), nieuczciwe praktyki (DU/2007/1206, DU/2007/331), płatności (DU/2011/1175), spór pozasądowy (DU/2016/1823). Kodeks cywilny ograniczono do artykułów dotyczących wzorców umownych i sprzedaży konsumenckiej (art. 384–385, 535–581) zgodnie z zakresem pracy.

**Strategia *chunkowania*** opiera się na hierarchii ELI: chunk = najgłębsza ważna jednostka w strukturze aktu (artykuł → paragraf → ustęp → punkt → litera), z polem `lead_in` zachowującym kontekst jednostki nadrzędnej. Decyzja motywowana wymogiem *deterministic 1:1 mapping art → chunk* dla *citation grounding* (sekcja 3.4).

**Walidacja struktury** odbywa się przez porównanie ścieżki każdego chunku z autoritatywnym dokumentem `struct` ELI; ścieżki niezgodne (np. *amending provisions* wstawione w HTML) są odrzucane. Liczba chunks odrzuconych: 0 błędów (wszystkie 6 aktów: `0 missing, 0 extra` względem `struct`).

### 3.3.2 Stratum B — eksperckie pary Q&A (UOKiK)

Stratum B zawiera **60 par Q&A** z portalu `prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/`. Tabela 3.3.2 przedstawia rozkład per kategoria.

**Tabela 3.3.2.** Stratum B — eksperckie pary Q&A UOKiK (rozkład per kategoria).

| Kategoria | Pary | Udział | Średnia liczba cytowań |
|---|---:|---:|---:|
| Prawo do informacji (*obowiazki-informacyjne*) | 20 | 33,3% | [TBD post-Iteracja 1b] |
| Odstąpienie od umowy | 19 | 31,7% | [TBD post-Iteracja 1b] |
| Zagadnienia ogólne | 12 | 20,0% | [TBD post-Iteracja 1b] |
| Reklamacja | 6 | 10,0% | [TBD post-Iteracja 1b] |
| Telemarketing | 3 | 5,0% | [TBD post-Iteracja 1b] |
| **Razem** | **60** | **100%** | **1,07** |

**Cechy *gold standardu*:** 55 z 60 par (92%) zawiera pole `cited_articles` z co najmniej jedną referencją do aktu prawnego; łącznie 52 unikalne referencje legalne. Pięć par bez cytowań to pytania definicyjne/orientacyjne, w których UOKiK genuinely nie podaje *Podstawy prawnej* w HTML źródłowym (nie błąd parsera).

**Wartość metodologiczna:** dostępność 60 *ready-made* par eksperckich z autorytatywnego źródła (UOKiK jako urząd) **eliminuje koszt ręcznej anotacji 60 par przez autorkę**, pozwalając na alokację czasu na **50–100 dodatkowych par hand-annotated** pokrywających typy halucynacji nieobecne w dystrybucji UOKiK (m.in. *paragraph mis-citation*, *temporal drift* — patrz sekcja 3.5).

### 3.3.3 Stratum C — autentyczne pytania konsumenckie

Stratum C zawiera **2 967 unikalnych pytań konsumenckich** z czterech podźródeł. Tabela 3.3.3 przedstawia rozkład.

**Tabela 3.3.3.** Stratum C — autentyczne pytania konsumenckie (rozkład per podźródło).

| Podźródło | Pytania | Udział | Strategia *scrape* |
|---|---:|---:|---|
| e-prawnik.pl | 954 | 32,2% | 9 kategorii × paginacja, *whitelist relewancji konsumenckiej* w tytule |
| forumprawne.org | 1 202 | 40,5% | Subforum `prawa-konsumenta.33` × 60 stron, *keep-all* (subforum-level filtr) |
| eporady24.pl | 302 | 10,2% | 4 podkategorie + post-filtr (`postfilter_eporady24.py`); tylko *meta description* (mitygacja licencji — sekcja 3.8) |
| Reddit (r/Polska + r/Polska_wpz) | 509 | 17,2% | 30 zapytań × 3 subreddity × 2 sortowania (*search.json* bez OAuth) |
| **Razem** | **2 967** | **100%** | — |

**Top 5 tematów** (tagowanie wieloznakowe metodą *substring-match*): *reklamacja* (610), *zwrot* (549), *odszkodowanie* (416), *sklep* (347), *pojazd-auto* (317). Pełna taksonomia 28 tematów dostępna w pliku `data/raw/consumer_questions_polish_2026-05-16/README.md`.

**Dedup rate:** 0,7% (dedup po znormalizowanym prefixie pytania). Niski wskaźnik świadczy o komplementarności podźródeł.

**Świadome ograniczenia stratum C:** (1) tagowanie wieloznakowe ma charakter *substring-match* i generuje *false positives* (~5–10% wątków bez prawdziwego dopasowania tematu); (2) Reddit ma najwyższy *noise rate* (~10–15% *false positives* na poziomie wątku); (3) eporady24 zawiera tylko *meta description* (~150–300 znaków), nie pełne treści (mitygacja licencyjna). Szczegóły w sekcji 3.10.

---

## 3.4 Deterministyczna struktura *citation grounding*

Niniejsza sekcja stanowi **kluczową kontrybucję metodologiczną v3.2** (nieobecna w wersji v3.1 pracy). Wprowadza formalny model cytowania prawnego pozwalający na **algorytmiczną weryfikację cytowań generowanych przez model językowy**.

### 3.4.1 Format cytowania (*citation string*)

Każdy chunk Stratum A posiada deterministycznie generowane pole `citation_string` zgodne z formalnym wzorcem:

```
art. {N}[ § {P}][ ust. {U}][ pkt {K}][ lit. {L}] {short_title} z dnia {DD miesiąca YYYY} r. (Dz.U. {YYYY} poz. {NNNN})
```

gdzie pola w nawiasach kwadratowych są opcjonalne (wstawiane wyłącznie gdy chunk zlokalizowany jest na danym poziomie hierarchii ELI). Przykład pełnej formy:

> *art. 12 ust. 1 pkt 1 Ustawy o prawach konsumenta z dnia 30 maja 2014 r. (Dz.U. 2014 poz. 827)*

### 3.4.2 Mapowanie *artykuł → chunk* (1:1)

Każda jednostka *(art, para, ust, pkt, lit)* mapuje się na dokładnie jeden chunk w korpusie. Mapowanie odwrotne (*chunk → identyfikator*) jest również jednoznaczne. Konsekwencja: każde cytowanie wygenerowane przez model językowy może być **deterministycznie zweryfikowane** względem korpusu — jeśli `citation_string` modelu nie istnieje w zbiorze `citation_string` wszystkich chunks, cytowanie jest **fałszywe (*fabricated citation*)**.

### 3.4.3 Rozróżnienie *faithfulness* vs *correctness* (Wallat ICTIR 2025)

Zgodnie z 🟡 *Verify [Wallat et al., ICTIR 2025 / arXiv 2412.18004]*, *citation quality* w systemach RAG dekomponuje się na dwie niezależne metryki:

| Metryka | Definicja | Pytanie weryfikacyjne |
|---|---|---|
| **Faithfulness** | Cytowanie odsyła do realnie pobranego fragmentu kontekstu (nie wymyślone). | *Czy cytat istnieje w retrieved context?* |
| **Correctness** | Pobrany fragment **rzeczywiście wspiera** *claim* modelu (nie jest *post-hoc rationalization*). | *Czy cytat naprawdę uzasadnia tezę?* |

Rozróżnienie istotne metodologicznie: w realnych systemach RAG do **57% cytowań** stanowi *post-rationalization* (cytowanie istnieje, ale nie wspiera *claim*). Praca raportuje **obie metryki osobno** w R7 (RQ2/H2a faithfulness ≥85%, H2b correctness ≥75%).

### 3.4.4 Implikacja dla protokołu ewaluacji

Powyższa struktura uzasadnia protokół ewaluacji opisany w sekcji 3.7 (codebooks) oraz w R5 (potok inferencji + *citation alignment*).

---

## 3.5 Metodologia wstrzykiwania halucynacji (*hallucination injection*)

Niniejsza sekcja stanowi **drugą kluczową kontrybucję metodologiczną v3.2**. Wprowadza programatyczną generację par *(odpowiedź faithful, odpowiedź z halucynacją)* służących trenowaniu *hidden-states halu probe* (RQ1) oraz *citation verifier* (RQ4).

### 3.5.1 Pięć typów halucynacji

Tabela 3.5.1 przedstawia taksonomię pięciu typów halucynacji wraz z definicjami operacyjnymi.

**Tabela 3.5.1.** Taksonomia pięciu typów halucynacji generowanych programatycznie.

| Typ | Definicja operacyjna | Przykład (z domeny praw konsumenta) |
|---|---|---|
| **Factual fabrication** | Model dodaje *claim*, którego brak w pobranym kontekście. | „Ustawa daje **60 dni** na zwrot" przy faktycznych 14 dniach (art. 27 DU/2014/827). |
| **Entity confusion** | Model myli podmioty/instytucje odpowiedzialne. | „**UOKiK** rozpatruje reklamacje", podczas gdy reklamacje rozpatruje sprzedawca. |
| **Temporal drift** | Model podaje błędną datę uchwalenia/wejścia w życie aktu. | „Zgodnie z ustawą **z 2020 r.**", podczas gdy ustawa pochodzi z 2014 r. |
| **Negation flip** | Model odwraca sens — zamienia twierdzenie pozytywne na negatywne (lub odwrotnie). | „Konsument **nie ma** prawa do zwrotu", podczas gdy ma. |
| **Paragraph mis-citation** | Cytowany artykuł istnieje, ale jego treść nie wspiera *claim* (cytat *post-hoc rationalizing*). | „Per art. 27 — masz 14 dni", podczas gdy art. 27 mówi o czymś innym (lub: prawidłowy termin, błędny artykuł). |

### 3.5.2 Programatyczny *generator* halucynacji — szkielet algorytmu

Algorytm 3.5.1 przedstawia szkielet generatora w pseudokodzie.

**Algorytm 3.5.1.** *Hallucination injection generator* (pseudokod).

```
INPUT:  korpus chunks C (Stratum A), pytania Q (Stratum C subset),
        generator LLM G (Bielik 11B v3), liczba par N_target
OUTPUT: zbiór par (q, a_faithful, a_halu, halu_type, evidence) o liczności N_target

for i in 1 .. N_target:
    q          <- sample(Q)                              # autentyczne pytanie
    retrieved  <- retrieve_top_k(q, C, k=10)             # BGE-M3 + reranker
    a_faithful <- G.generate(q, retrieved)               # faithful odpowiedź
    t          <- sample({fabrication, entity_conf,
                          temporal_drift, negation_flip,
                          mis_citation})                  # typ halucynacji
    a_halu     <- inject_halu(a_faithful, t, retrieved)  # transformacja typo-specyficzna
    label      <- nli_label(a_halu, retrieved)           # mDeBERTa-XNLI
    if label != "entailment":
        emit (q, a_faithful, a_halu, t, retrieved)
```

Funkcja `inject_halu` realizuje **pięć transformacji typo-specyficznych**, każda wykorzystująca odrębną strategię (np. *date substitution* dla *temporal drift*, *negation insertion* dla *negation flip*, *article-id swap* dla *mis-citation*).

### 3.5.3 Etykietowanie *silver labels* przez NLI

Generator wykorzystuje *Natural Language Inference* (NLI) — model `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (licencja MIT, ≈300M parametrów, polski obecny w korpusie treningowym) — jako *silver label* dla wygenerowanych par. Strategia trzypoziomowa (Tier 1 mDeBERTa-XNLI, Tier 2 HerBERT-large fine-tune na CDSC-E, Tier 3 LLM-as-judge Bielik 11B *few-shot* jako *oracle baseline*) opisana w konspekcie v3.2 sekcja II.4.3.

### 3.5.4 Walidacja jakości generatora — *spot-check* przez autorkę

Próbka **5% wygenerowanych par** podlega ręcznemu *spot-check* przez autorkę w celu walidacji *silver labels*. Próg akceptacji potoku generacji: ≥90% zgodności *spot-check* z etykietą NLI. Liczba par syntetycznych docelowo: **5 000 – 10 000** (Iteracja 1b).

`[TBD post-Iteracja 1b]`: dokładna liczba wygenerowanych par, *spot-check accuracy*, rozkład typów halucynacji.

---

## 3.6 Struktura katalogów, nazewnictwo, wersjonowanie DVC

### 3.6.1 Struktura katalogów

```
main_project/
├── data/
│   ├── raw/                      # read-only, kanoniczne źródła
│   │   ├── eli_ustawy_konsumenckie_2026-05-16/
│   │   ├── uokik_qa_2026-05-16/
│   │   └── consumer_questions_polish_2026-05-16/
│   ├── processed/                # po preprocesingu (NFC, dedup, chunking)
│   ├── eval/                     # zbiory ewaluacyjne (gold standard mix)
│   └── synthetic/                # syntetyczne pary halucynacji (Iteracja 1b)
└── src/scrape/                   # skrypty scrape (deterministyczna reprodukcja)
```

Struktura zgodna z wymogiem Task 03 sekcja 1.1 (*„clear folder structure"*) oraz z dobrymi praktykami *raw vs processed separation*.

### 3.6.2 Konwencja nazewnictwa

Format ogólny:

```
{source}_{date}_{type}.{ext}
```

Przykłady realne (Iteracja 1a):

- `eli_ustawy_konsumenckie_2026-05-16/DU_2014_827.jsonl` — chunks ELI dla aktu DU/2014/827.
- `uokik_qa_2026-05-16/uokik_qa.jsonl` — eksperckie pary Q&A.
- `consumer_questions_polish_2026-05-16/forumprawne_consumer.jsonl` — pytania z forumprawne.org.

Daty w formacie ISO 8601 (`YYYY-MM-DD`) zapewniają sortowanie alfabetyczne równoważne chronologicznemu — istotne dla zarządzania *snapshotami*.

### 3.6.3 Wersjonowanie *Data Version Control* (DVC)

Korpus podlega kontroli wersji przez DVC (`dvc.org`) — narzędzie *git-friendly* dla dużych zbiorów danych. Każdy *snapshot* korpusu generuje plik `*.dvc` z hashem (commitowanym do git) oraz kopię w *remote storage* (MinIO).

Polityka tagowania *snapshotów*:

| Tag DVC | Punkt cyklu pracy | Zawartość |
|---|---|---|
| `corpus-iter-1a-raw` | Po Iteracji 1a | 5 150 elementów (3 strata) |
| `corpus-iter-1b-syn` | Po Iteracji 1b | + 5–10 tys. syntetycznych par + 50–100 par manual gold |
| `corpus-iter-2-eval` | Po Iteracji 2 | + dodatkowy *eval split* z *hold-out* |

`[TBD post-Iteracja 1b]`: hashe DVC dla każdego *snapshot*; URL *remote storage*.

---

## 3.7 *Codebooks* (księgi kodowe) per źródło

Sekcja zgodna z wymogiem Task 03 sekcja 1.3 (*„data dictionary / codebook"*). Każde stratum posiada formalny *codebook* dokumentujący pola, typy, znaczenia i wartości dozwolone.

### 3.7.1 *Codebook* Stratum A (akty prawne ELI)

**Tabela 3.7.1.** *Codebook* dla `eli_ustawy_konsumenckie_2026-05-16/*.jsonl`.

| Pole | Typ | Znaczenie | Wartości dozwolone |
|---|---|---|---|
| `ustawa_id` | string | Identyfikator ELI aktu | `{publisher}/{year}/{num}`, np. `DU/2014/827` |
| `ustawa_title` | string | Pełen tytuł aktu | tekst dowolny |
| `art` | string | Numer artykułu | liczba lub liczba z dopiskiem (np. `22^1`) |
| `para` | string \| null | Numer paragrafu (§) — używane głównie w KC | liczba lub null |
| `ust` | string \| null | Numer ustępu | liczba lub null |
| `pkt` | string \| null | Numer punktu | liczba lub null |
| `lit` | string \| null | Numer litery | litera lub null |
| `tresc` | string | Treść jednostki (po normalizacji NFC) | tekst polski |
| `citation_string` | string | Deterministyczny ciąg cytowania (sekcja 3.4.1) | tekst |
| `scrape_date` | string (ISO) | Data scrape | `YYYY-MM-DD` |
| `source_url` | string (URL) | Kanoniczny URL ELI | URL |
| `metadata` | object | Metadane aktu (daty, status, rozdział) | obiekt |

### 3.7.2 *Codebook* Stratum B (UOKiK Q&A)

**Tabela 3.7.2.** *Codebook* dla `uokik_qa_2026-05-16/uokik_qa.jsonl`.

| Pole | Typ | Znaczenie | Wartości dozwolone |
|---|---|---|---|
| `qa_id` | string | Stabilny identyfikator pary | `uokik_<slug-kategorii>_<numer>` |
| `question` | string | Pytanie konsumenta (znormalizowane) | tekst polski |
| `answer` | string | Odpowiedź ekspercka (znormalizowana) | tekst polski |
| `cited_articles` | array[string] | Lista referencji do aktów prawnych | każda referencja w postaci `art. N {akt}` |
| `category` | string (kat.) | Kategoria UOKiK | 5 wartości: `Ogolne`, `Prawo do informacji`, `Odstapienie od umowy`, `Reklamacja`, `Telemarketing` |
| `source_url` | string (URL) | URL kategorii UOKiK | URL |
| `scrape_date` | string (ISO) | Data scrape | `YYYY-MM-DD` |
| `anchor` | string | Slug akordeonu (`data-anchor` z HTML) | `faqNNN` |

### 3.7.3 *Codebook* Stratum C (autentyczne pytania)

**Tabela 3.7.3.** *Codebook* dla `consumer_questions_polish_2026-05-16/*.jsonl`.

| Pole | Typ | Znaczenie | Wartości dozwolone |
|---|---|---|---|
| `question_id` | string | Stabilny identyfikator pytania | `{source-prefix}_NNNNN` |
| `question` | string | Pytanie (tytuł wątku, znormalizowane) | tekst polski |
| `context` | string \| null | Pierwszy post / opis (opcjonalny, anonimizowany) | tekst lub null |
| `source` | string (kat.) | Nazwa źródła | 4 wartości: `e-prawnik.pl`, `forumprawne.org`, `eporady24.pl`, `reddit.com/r/Polska`, `reddit.com/r/Polska_wpz` |
| `source_url` | string (URL) | Kanoniczny URL wątku | URL |
| `category` | string | Kategoria źródłowa (per podźródło) | tekst |
| `thread_responses_count` | int \| null | Liczba odpowiedzi w wątku (semantyka różni się per źródło) | ≥0 lub null |
| `scrape_date` | string (ISO) | Data scrape | `YYYY-MM-DD` |
| `extracted_topics` | array[string] | Tagowanie wieloznakowe tematów (28 wartości w słowniku) | podzbiór taksonomii |

**Pola dodatkowe dla Reddit:** `reddit_score`, `reddit_subreddit`, `reddit_author_hash` (SHA1 prefix — anonimizacja), `reddit_created_utc`.

---

## 3.8 Licencjonowanie i etyka

### 3.8.1 Licencje per źródło

**Tabela 3.8.1.** Analiza licencji per źródło wraz z zastosowanymi mitygacjami.

| Źródło | Status licencyjny | Mitygacja w pracy |
|---|---|---|
| ISAP / ELI (akty prawne) | **Domena publiczna *de facto*** (art. 4 pkt 1 ustawy o prawie autorskim i prawach pokrewnych z dnia 4 lutego 1994 r., Dz.U. 1994 poz. 83 — akty normatywne nie stanowią przedmiotu prawa autorskiego) | Atrybucja źródła w cytowaniach. |
| UOKiK Q&A | **Materiały urzędowe** (art. 4 pkt 2 PrAut) — *public domain de facto* | Atrybucja: *„Źródło: UOKiK, prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/, scrape 2026-05-16"*. |
| e-prawnik.pl | `robots.txt` zezwala na `/forum/`; ToS bez explicit *copyright transfer*; posty użytkowników objęte prawem autorskim autora | *Dozwolony użytek* art. 27 (cel dydaktyczny) + art. 29 (prawo cytatu) PrAut. Pobierane wyłącznie tytuły wątków (krótkie cytaty); brak redystrybucji publicznej. |
| forumprawne.org | `robots.txt` zezwala na `/forum/`, `/watek/`; ToS §12 (przechowywanie informacji) | *Dozwolony użytek* art. 27 + 29 PrAut. Pobierane tytuły wątków (`--no-bodies` flag); `context` puste w wersji produkcyjnej. |
| eporady24.pl | **🟡 Licencja restrykcyjna:** *Regulamin §1* — opłata 25 zł rocznie / 1000 znaków bez spacji (powołanie art. 79 ust. 1 pkt 3 lit. b PrAut) | **Mitygacja podwyższona:** pobierane wyłącznie `meta description` (~150–300 znaków, fragment marketingowy indeksowalny w wyszukiwarkach). Storage wyłącznie lokalny. *Dozwolony użytek* art. 27 + 29 PrAut przy łącznej objętości ~20–60 tys. znaków (potencjalna opłata 0,5–1,5 zł rocznie — *de minimis*). **Plik traktowany jako *legacy fallback*; prymarne źródła to e-prawnik, forumprawne, Reddit.** |
| Reddit (r/Polska, r/Polska_wpz) | Reddit User Agreement §5 (licencja perpetual dla Reddit + third-party academic use); Reddit Data API Terms §2,5 (academic/non-commercial use explicitly permitted) | Anonimizacja `usernames` (SHA1 prefix 10 znaków); rate limit 2,5 s/request; brak DM-ów ani profili. |

**Podstawa prawna dla *Text and Data Mining*:** dodatkowo, polski **wyjątek TDM (wrzesień 2024)** w prawie autorskim stanowi równoległe *legal grounding* dla scrape ISAP i UOKiK. Dwie niezależne podstawy prawne zapewniają *defense-in-depth*.

### 3.8.2 Brak danych osobowych

Korpus **nie zawiera danych osobowych** w rozumieniu RODO. Procedury anonimizacji:

- **Stratum A** (akty prawne): treść aktów normatywnych, brak danych osobowych z natury.
- **Stratum B** (UOKiK Q&A): treść redagowana przez urząd, brak imion/nazwisk/danych adresowych. *Pytania zawierają przykład „Jan jest konsumentem"* — pseudonim ilustracyjny, nie identyfikujący osobę realną.
- **Stratum C** (autentyczne pytania): trzy mechanizmy anonimizacji w skryptach scrape:
  - `anonymize()` — regex zastępujący e-maile (`[EMAIL]`), numery telefonów (`[PHONE]`), nazwy użytkowników Reddit (`[USER]`).
  - SHA1-hashed `usernames` Reddit (10 znaków prefiksu — niemożliwe do *reverse* bez tablicy *rainbow* na 500 000+ subskrybentów).
  - Brak pobierania profili (display name, karma, data utworzenia konta).

### 3.8.3 Brak komitetu etycznego

Praca **nie wymaga zgody komitetu etycznego**, ponieważ:

1. Nie obejmuje badań na ludziach (*no human subjects research*).
2. Nie zbiera danych osobowych ani wrażliwych.
3. Korzysta wyłącznie z publicznie dostępnych źródeł (domena publiczna lub *dozwolony użytek*).

Zgodnie z wytycznymi PJATK dla pracy inżynierskiej w obszarze przetwarzania języka naturalnego: scrape publicznych źródeł webowych pod *dozwolony użytek* nie wymaga formalnej zgody.

---

## 3.9 *Reproducibility statement*

Niniejsza sekcja realizuje wymóg Task 03 sekcja 1.5 (*„automate data preparation with scripts"*) oraz dobre praktyki *reproducible research*.

### 3.9.1 Skrypty scrape (lokalizacje w repozytorium)

| Stratum | Skrypt | Typ |
|---|---|---|
| A (ELI) | `main_project/src/scrape/isap/scrape_eli.py` | stdlib only (urllib, html.parser) |
| B (UOKiK) | `main_project/src/scrape/uokik/scrape_qa.py` | stdlib + BeautifulSoup |
| C (e-prawnik, forumprawne, eporady24) | `main_project/src/scrape/legal_fora/scrape.py` | BeautifulSoup + lxml |
| C (Reddit) | `main_project/src/scrape/reddit/scrape_consumer.py` | urllib + json (search.json bez OAuth) |

### 3.9.2 Komendy uruchamiające (przykład Stratum A)

```powershell
# Pełen scrape (wszystkie 6 ustaw):
uv run python -m src.scrape.isap.scrape_eli

# Pojedynczy akt:
uv run python -m src.scrape.isap.scrape_eli --ustawa DU/2014/827

# Dry-run (parse bez zapisu):
uv run python -m src.scrape.isap.scrape_eli --dry-run
```

Pełne komendy dla wszystkich strata znajdują się w plikach `README.md` w katalogach `data/raw/{stratum}_2026-05-16/`.

### 3.9.3 Pobieranie *snapshot* przez DVC

```powershell
uv run dvc pull corpus-iter-1a-raw
```

### 3.9.4 Determinizm

- **`RANDOM_SEED = 2026`** zablokowany dla wszystkich operacji wymagających próbkowania (split *train/eval*, *spot-check*, *bootstrap CI*).
- **Czas wykonania *full scrape*:** ~30 minut łącznie (z *rate limiting* 1–2,5 s/request per źródło).
- **Wymagane zależności:** Python 3.13 + uv (NIE pip). Pełna lista w `pyproject.toml`.

`[TBD post-Iteracja 1b]`: hashe SHA-256 *snapshotów* `corpus-iter-1a-raw` i `corpus-iter-1b-syn` dla weryfikacji integralności.

---

## 3.10 Świadome *biases* (analiza ograniczeń korpusu)

Niniejsza sekcja realizuje **defense scaffolding punkt 3** (negative-result publishability framing — `thesis_elements/CLAUDE.md` sekcja "Defense scaffolding") oraz wymóg PRO-D Assignment 5 sekcja E (*Bias and Limitation Analysis*). Stanowi *audit trail* dla obrony — każde ograniczenie jest **świadome**, **udokumentowane** i **uzasadnione**.

### 3.10.1 *Source-type bias* (nierównowaga typów źródeł)

Korpus jest **strukturalnie niezbalansowany** ze względu na typ źródła:

| Typ | Liczność | Udział | Funkcja w potoku |
|---|---:|---:|---|
| Akty prawne (Stratum A) | 2 123 | 41,2% | baza wiedzy retrievera |
| Eksperckie pary Q&A (Stratum B) | 60 | 1,2% | gold standard ewaluacyjny |
| Autentyczne pytania (Stratum C) | 2 967 | 57,6% | distribution dla generacji halucynacji + *stress test* |

**Świadoma decyzja:** każde stratum pełni **odmienną funkcję** w potoku; nierównowaga nie jest błędem, lecz konsekwencją architektury (np. 60 par UOKiK jako *gold standard* to ekspercka kuracja, niemożliwa do skalowania bez utraty jakości). **Mitygacja:** *gold standard* augmentowany o 50–100 par hand-annotated przez autorkę w Iteracji 1b (sekcja 3.10.5).

### 3.10.2 *Recency bias* (świeżość źródeł)

Różne strata mają różne profile czasowe:

- **Stratum A** (akty prawne): aktualne (consolidated state per 2026-05-16), z najstarszym aktem z 1964 r. (Kodeks cywilny). Stabilność wysoka — akty zmieniane sporadycznie.
- **Stratum B** (UOKiK Q&A): aktualizowane sporadycznie po zmianach ustawowych.
- **Stratum C** (autentyczne pytania): mocny *recency bias* w stronę współczesnych tematów (np. e-prawnik luty 2022 – sierpień 2025, Reddit/fora ostatnie miesiące).

**Implikacja:** dystrybucja Stratum C nie reprezentuje równomiernie historii praw konsumenta — jest *snapshot* aktualnych zainteresowań. **Mitygacja:** *Stratum C* służy wyłącznie generacji syntetycznych pytań dla *stress testu*, nie jest indeksowane w finalnym vector store (zgodnie z `consumer_questions_polish_2026-05-16/README.md` sekcja *Downstream usage*).

### 3.10.3 *Language bias* (wyłącznie polski)

Korpus jest **wyłącznie polskojęzyczny**. Świadoma decyzja — praca dotyczy polskiego RAG, *cross-lingual transfer* poza zakresem (DEC-003, sekcja II.10 konspektu v3.2). **Konsekwencja:** wnioski pracy **nie generalizują** poza język polski; każde rozszerzenie wymaga osobnej walidacji.

### 3.10.4 *Topic distribution bias* (nierównowaga tematyczna w Stratum C)

Tagowanie tematów w Stratum C ujawnia silny *long tail*:

- **Top 5 tematów** (*reklamacja* 610, *zwrot* 549, *odszkodowanie* 416, *sklep* 347, *pojazd-auto* 317) stanowi ≈75% wszystkich tagów.
- **Tematy *under-represented*:** *klauzule-niedozwolone*, *nieuczciwe-praktyki* — istotne dla obrony konsumenta, lecz słabo reprezentowane w autentycznych pytaniach.

**Implikacja:** generator halucynacji (sekcja 3.5) trenowany na Stratum C może produkować zbyt mało par dla *long-tail* tematów. **Mitygacja:** *stratified sampling* w generatorze (próbkowanie proporcjonalne do *inverse frequency* tematu w docelowej dystrybucji RQ1).

### 3.10.5 *Single-annotator caveat* (jeden anotator dla *manual gold*)

Planowane **50–100 par hand-annotated** w Iteracji 1b adnotowane są **wyłącznie przez autorkę pracy** (Magdalena Sochacka, s25508, PJATK Data Science). Brak *inter-annotator agreement*.

**Świadome uzasadnienie:** Praca inżynierska z budżetem czasowym ≤10 tygodni; pozyskanie drugiego anotatora dla 100 par to ≥40 godzin pracy eksperta prawnego (autorka **nie pretenduje do statusu eksperta prawnego** — informational only, nie *legal advice*, sekcja II.2.1 konspektu v3.2).

**Mitygacja:** (1) Stratum B (60 par UOKiK) stanowi **niezależny *gold standard* o autorytecie urzędu**, eliminując ryzyko *single-annotator bias* dla ≥37,5% *eval setu* (60 z 160 par). (2) Iteracja 0b POC sanity-check 5 par UOKiK porównany manualnie przez autorkę z etykietą NLI — jeśli zgodność <70%, decyzja o eskalacji do Tier 2 (HerBERT-large fine-tune). (3) *Flag w R8 limitations* jako *future work* — *open call* na dodatkową walidację społeczności (przy publikacji datasetu na HuggingFace).

### 3.10.6 *Domain-restriction bias* (wąska dziedzina)

Korpus dotyczy **wyłącznie praw konsumenta**. Wnioski pracy nie generalizują na inne dziedziny prawa (karne, rodzinne, administracyjne) bez osobnej walidacji.

**Świadome uzasadnienie:** wąska dziedzina = większa wewnętrzna spójność dystrybucji = wyższa *deterministic citation grounding* (sekcja 3.4). Generalizacja *cross-domain* jest jawnie poza zakresem (DEC-003, RQ5 *deprecated* zgodnie z literaturą Dubanowska EMNLP 2025 + Vaddi 2026-03 — sondy halucynacji mają OOD AUROC ≈ random).

### 3.10.7 Podsumowanie ograniczeń

Tabela 3.10.1 podsumowuje siedem świadomych *biases* korpusu wraz z ich statusami mitygacji.

**Tabela 3.10.1.** Podsumowanie świadomych *biases* korpusu.

| # | *Bias* | Status mitygacji | Wpływ na wnioski |
|---|---|---|---|
| 3.10.1 | Source-type | Mitygowany (manual gold augmentation) | Niski |
| 3.10.2 | Recency (Stratum C) | Mitygowany (*stress test only*, nie indeks) | Niski |
| 3.10.3 | Language (polski) | Świadoma decyzja (poza zakresem) | Wnioski nie generalizują *cross-lingual* |
| 3.10.4 | Topic distribution | Mitygowany (*stratified sampling*) | Średni — *long-tail* under-served |
| 3.10.5 | Single-annotator | Częściowo mitygowany (UOKiK *cross-check*) | Średni — *flag* w R8 |
| 3.10.6 | Domain-restriction | Świadoma decyzja (poza zakresem) | Wnioski nie generalizują *cross-domain* |

---

## 3.11 Mapowanie sekcji na wymogi Task 03 i PRO-D Assignment 5

Tabela 3.11.1 mapuje sekcje 3.1–3.10 na wymogi instytucjonalne, potwierdzając kompletność rozdziału.

**Tabela 3.11.1.** Mapowanie sekcji R3 na wymogi formalne.

| Sekcja R3 | Task 03 PJATK | PRO-D Assignment 5 |
|---|---|---|
| 3.1 Modalności danych | §1 (general principles) | §A (Dataset Structure) |
| 3.2 Metodologia doboru źródeł | §1.3 (metadata) + §7.1 (data sources) | §A + §E |
| 3.3 Trzy strata szczegółowo | §3 (text data) + §7.1 | §A |
| 3.4 *Citation grounding* | §1.6 (presentation) — innowacja v3.2 | §F (implications for design) |
| 3.5 *Hallucination injection* | §3.1 (preparation) — innowacja v3.2 | §F |
| 3.6 Struktura katalogów + DVC | §1.1 (consistency) + §1.2 (versioning) | §A (storage) |
| 3.7 *Codebooks* | §1.3 (data dictionary) + §3.1 | §A |
| 3.8 Licencjonowanie + etyka | §1.4 (ethics) + §7.5 | §E (ethical implications) |
| 3.9 *Reproducibility* | §1.5 (reproducibility) | §F |
| 3.10 Świadome *biases* | §7.5 | §E + §F |

---

## 3.12 *Placeholdery* dla post-eksperymentalnych liczb

Następujące liczby wymagają uzupełnienia po kolejnych iteracjach:

| Symbol | Lokalizacja | Iteracja | Opis |
|---|---|---|---|
| `[TBD post-Iteracja 1b]` | 3.3.2 (UOKiK średnia cit/pair per kategoria) | 1b | Rozkład cytowań per kategoria |
| `[TBD post-Iteracja 1b]` | 3.5.4 (generator validation) | 1b | Liczba syntetycznych par, *spot-check accuracy*, rozkład typów |
| `[TBD post-Iteracja 1b]` | 3.6.3 (DVC hashes) | 1b | Hashe SHA-256 dla *snapshotów* DVC |
| `[TBD post-Iteracja 1b]` | 3.9.4 (DVC hashes) | 1b | Hashe SHA-256 dla weryfikacji integralności |
| `[TBD post-Iteracja 2]` | (sekcja przeniesiona do R4 EDA) | 2 | Statystyki rozkładu długości chunks, UMAP embedding clusters |
| `[TBD post-Iteracja 2]` | (sekcja przeniesiona do R7) | 2+ | Wyniki *citation grounding faithfulness/correctness* na UOKiK gold |

---

## 3.13 Bibliografia rozdziału (*placeholder*)

🟡 *Verify all references via citation-checker subagent before final draft (Iteracja 7).*

- 🟡 *Verify* Wallat et al., *„Faithfulness vs Correctness in RAG Citations"*, ICTIR 2025 (arXiv 2412.18004) — kluczowe rozróżnienie dla sekcji 3.4.3.
- 🟡 *Verify* Dubanowska et al., *„OOD Generalization of Hallucination Probes"*, EMNLP 2025 — uzasadnienie *deprecation* RQ5 (sekcja 3.10.6).
- 🟡 *Verify* Mu-SHROOM 2025 SemEval Task 3 — *„Multilingual Hallucination Detection"* — referencja dla *polish gap* w sekcji 3.2.5 (i szerzej w R2).
- 🟡 *Verify* Vaddi 2026-03, OOD probe critique — uzupełnienie dla sekcji 3.10.6.
- 🟡 *Verify* Liang & Wang, Dec 2025 — linear vs nonlinear probes — kontekst dla sekcji 3.5.
- ELI API documentation, Sejm RP — `https://api.sejm.gov.pl/eli` (oficjalna dokumentacja OpenAPI).
- Kodeks cywilny — Ustawa z dnia 23 kwietnia 1964 r. — Kodeks cywilny (Dz.U. 1964 poz. 93, tekst jednolity).
- Ustawa o prawach konsumenta — Ustawa z dnia 30 maja 2014 r. o prawach konsumenta (Dz.U. 2014 poz. 827, tekst jednolity Dz.U. 2020 poz. 287).
- Ustawa o prawie autorskim i prawach pokrewnych z dnia 4 lutego 1994 r. (Dz.U. 1994 poz. 83) — art. 4 (akty normatywne, materiały urzędowe) + art. 27 (cel dydaktyczny) + art. 29 (prawo cytatu).
- *Text and Data Mining exception* — nowelizacja PrAut z września 2024 r. (🟡 *Verify dokładną sygnaturę Dz.U.*).
- Polish CitationBench dataset card (HuggingFace, w przygotowaniu — Iteracja 6).
- MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 — HuggingFace model card (MIT license, 27 języków w *training set*).

---

## 3.14 Co dalej w tym rozdziale

1. Iteracja 1b (~1 tydzień): uzupełnienie sekcji 3.5 o rzeczywiste liczby syntetycznych par + *spot-check accuracy*; uzupełnienie *codebook* dla `data/synthetic/` (nowe pole `halu_type`).
2. Iteracja 1b (~weekend hyperfocus): 50–100 par hand-annotated przez autorkę — rozszerzenie sekcji 3.10.5 o protokół anotacji (czas/parę, kryteria akceptacji).
3. Iteracja 2: walidacja `citation_string` deterministycznego (sekcja 3.4.2) na *hold-out* z UOKiK — raportowanie *exact match rate* `citation_string` modelu vs korpus.
