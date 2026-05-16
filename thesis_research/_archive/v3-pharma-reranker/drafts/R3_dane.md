# R3. Dane

> **Status draftu:** v0.1 (2026-05-16) — markdown source dla `thesis_elements/R03_dane.docx`.
> **Cel długościowy:** 5000–7000 słów (7–10 stron PJATK).
> **Format docelowy:** PJATK — TNR 12pt, line 1.5, marginesy 2.5cm, footnotes IEEE 10pt. Cytacje `[N]` w markdownie konwertowane do footnotes po skopiowaniu do Worda.
> **Completion target:** metodologia 100% (sekcje 3.1–3.10 napisane kompletnie); liczby końcowe oznaczone `[TBD post-Iteracja N]` zgodnie z harmonogramem iteracyjnym (konspekt II.16) i uzupełniane po Iteracji 1 (corpus + EDA) oraz Iteracji 0a (feasibility).
> **Single source of truth dla treści:** `thesis_research/sources_catalog.md`. Decyzje domenowe: DEC-001 (rotacja na farmakologię szeroką), DEC-002 (ChPL↔Ulotka pairing jako RQ5).
> **Notki dla autorki:** cytacje oznaczone 🟡 — do weryfikacji przez `citation-checker` przed final submission. Sekcje numerowane 3.1–3.10 zgodnie z planem `assignments/plans/zadanie_03_plan.md`.

---

## 3.1. Modalności danych w pracy

W pracy wykorzystano dwie modalności danych: *tekstową* oraz *tabularną*. Pierwsza obejmuje dokumenty regulacyjne i naukowe z polskiej farmakologii klinicznej, stanowiące korpus do indeksowania, treningu rerankera oraz ewaluacji jakości retrievalu. Druga obejmuje metadane korpusu (kody anatomiczno-terapeutyczno-chemiczne ATC, identyfikatory rejestracyjne `productID`, daty modyfikacji rekordów `data_modyfikacji`), metryki ewaluacji eksperymentów zapisywane w MLflow, logi przebiegów pipeline'u Prefect oraz tabele kontrolne procesu (`sample-list`, `eval-pairs`, `judge-labels`, `preference-quadruplets`).

Modalności obrazowa, audio oraz wideo zostały **świadomie wyłączone z zakresu pracy**. Uzasadnienie wynika bezpośrednio z natury problemu badawczego: ewaluowany jest pipeline retrievalu *tekstowego* w polskojęzycznym systemie *Retrieval-Augmented Generation*, w którym ranking par *zapytanie → passage* operuje na embeddingach tekstowych BGE-M3 [1] oraz preferencjach generowanych przez model językowy. Dane wizualne — w szczególności skany starszych Charakterystyk Produktu Leczniczego pochodzące z PDF-ów rastrowych — są w tym ujęciu traktowane wyłącznie jako wejście do warstwy *Optical Character Recognition* (Tesseract w trybie polskim `-l pol`), której wyjściem jest tekst. Nie są one analizowane jako modalność samodzielna i nie są przechowywane jako zasoby graficzne. Analogicznie modalności audio i wideo nie występują w żadnym z analizowanych źródeł — dokumenty regulacyjne URPL, raporty Agencji Oceny Technologii Medycznych i Taryfikacji, zarządzenia Narodowego Funduszu Zdrowia oraz artykuły z otwartych czasopism farmaceutycznych dystrybuowane są wyłącznie w formatach tekstowych (PDF z warstwą tekstową, XML, HTML, JATS).

Niniejsze rozróżnienie modalności jest podstawą organizacji folderów (sekcja 3.6) oraz dalszych decyzji metodologicznych dotyczących preprocessingu, w szczególności *świadomych biasów* korpusu (sekcja 3.10). Wyłączenie modalności pozatekstowych nie jest przypadkową luką lecz decyzją scope pracy, zgodną z definicją problemu badawczego sformułowaną w rozdziale 1.

## 3.2. Metodologia doboru źródeł

W tym podrozdziale opisano formalną procedurę selekcji źródeł korpusu, zgodnie z wymogiem rygorystycznej dokumentacji doboru materiału. Sources research przeprowadzono w dwóch rundach (R1 + R2) w dniu 2026-05-15, na podstawie wcześniejszej decyzji domenowej DEC-001 (rotacja na farmakologię szeroką jako testbed). Procedura ta została wzorowana na konwencjach przeglądów systematycznych typu PRISMA-light oraz dostosowana do specyfiki doboru *materiałów źródłowych* (a nie literatury naukowej) dla korpusu domeny specjalistycznej.

### 3.2.1. Kryteria włączenia

Źródło zostało **włączone do korpusu** wyłącznie, gdy spełniało wszystkie pięć poniższych kryteriów:

1. **Język.** Polski natywny, nie tłumaczenie maszynowe ani redagowane EN→PL. Źródła wyłącznie anglojęzyczne — wykluczone bez wyjątku.
2. **Licencja.** Open-access lub *permitted research use*. Akceptowane statusy licencyjne to licencje *Creative Commons* w wariantach BY, BY-NC, BY-SA, BY-NC-ND [2], domena publiczna oraz materiały urzędowe wyłączone spod ochrony prawnoautorskiej na mocy Art. 4 ustawy z dnia 4 lutego 1994 r. o prawie autorskim i prawach pokrewnych [3]. Treści zza paywall lub o nieokreślonym statusie licencyjnym — wykluczone.
3. **Specjalizacja.** Obecność terminologii farmakologicznej w treści: międzynarodowe nazwy substancji czynnych (*Denominationes Communes Internationales*, DCI), kody klasyfikacji anatomiczno-terapeutyczno-chemicznej (ATC) wg WHO [4] 🟡 *Verify via citation-checker*, terminologia łacińsko-polska, nomenklatura farmakokinetyczna, opisy mechanizmów działania, interakcji oraz działań niepożądanych. Źródła o ogólnym charakterze medycznym lub poziomie *encyklopedycznym* — wykluczone.
4. **Scrapowalność.** Dostępność programatyczna, rozumiana jako: API REST z dokumentacją, *Open Archives Initiative – Protocol for Metadata Harvesting* (OAI-PMH), przewidywalny wzorzec URL umożliwiający masowe pobieranie lub strukturalny PDF z warstwą tekstową. Źródła wymagające manualnego pobierania per dokument lub systemy wymagające kapcza/sesji uwierzytelnionej — wykluczone.
5. **Verifiability.** Istnienie oraz status licencyjny zweryfikowane przez co najmniej trzy niezależne zapytania w wyszukiwarce internetowej w trakcie sources research R1+R2 (2026-05-15) z polskojęzycznymi słowami kluczowymi. Kandydaci, dla których weryfikacja zwracała sprzeczne sygnały lub nie zwracała wyników jednoznacznie potwierdzających istnienie zasobu, oznaczani byli statusem `UNVERIFIED` i wykluczani z dalszej selekcji.

### 3.2.2. Kryteria wyłączenia

Źródło zostało **odrzucone z korpusu**, jeśli spełniało którekolwiek z poniższych kryteriów:

1. **Paywall lub subskrypcja.** Źródła o pełnotekstowym dostępie wymagającym opłaty subskrypcyjnej, m.in. Farmakopea Polska XII/XIII (wydawca CONGNO MEDICAL), Czasopismo Aptekarskie, większość pozycji wydawnictwa Medycyna Praktyczna.
2. **Treść dominująco anglojęzyczna.** Acta Poloniae Pharmaceutica — czasopismo wydawane przez Polskie Towarzystwo Farmaceutyczne, publikujące w języku angielskim od 1974 r., wartość dla treningu polskiego rerankera niska niezależnie od wartości naukowej.
3. **Brak treści strukturalnej.** Formularze zgłoszeń działań niepożądanych ADR — formularze, nie tekst nadający się do rerankingu jako samodzielne *passage*.
4. **Zaprzestanie publikacji lub brak aktualizacji.** Postępy Farmacji — wydawca potwierdził zaprzestanie publikacji, archiwum legacy minimalne.
5. **Niejednoznaczność licencyjna.** Sytuacje, w których brak jest *explicit* przyzwolenia na wykorzystanie zasobu w pracy badawczej, a jednocześnie nie kwalifikuje się on jako materiał urzędowy w rozumieniu Art. 4.
6. **Wyłącznie dane tabularne.** Publiczne API statystyk Narodowego Funduszu Zdrowia (datasety 1601 i 1676 na `dane.gov.pl`) — surowe tabele rozliczeniowe z kosztami refundacji per kod EAN i ICD-10, bez tekstu nadającego się jako *passage* dla rerankera. Włączane jako metadata, nie jako korpus.

### 3.2.3. Strategia wyszukiwania

Wyszukiwanie kandydatów do korpusu przeprowadzono w dwóch rundach z eksplicytnie różnymi celami:

- **Runda 1 — farmakologia szeroka (~16 kandydatów).** Punktem wyjścia była lista źródeł zidentyfikowanych w raporcie feasibility psychiatrii (`thesis_research/06_raport_feasibility_psychiatria.docx`), rozszerzona po decyzji DEC-001 o źródła pokrywające pełny przekrój farmakologii klinicznej. Lista kandydatów obejmowała: Urząd Rejestracji Produktów Leczniczych, Wyrobów Medycznych i Produktów Biobójczych (URPL), Agencję Oceny Technologii Medycznych i Taryfikacji (AOTMiT), Ministerstwo Zdrowia, czasopisma Polskiego Towarzystwa Farmaceutycznego (PTFarm), uczelnie medyczne (Uniwersytet Medyczny w Poznaniu, Gdański Uniwersytet Medyczny, Warszawski Uniwersytet Medyczny, Collegium Medicum Uniwersytetu Jagiellońskiego), Farmakopea Polska, Aptekarz Polski (Naczelna Izba Aptekarska), Postępy Fitoterapii.
- **Runda 2 — Ulotki, refundacja operacyjna i adjacencies (~12 kandydatów).** Po zidentyfikowaniu strukturalnej parowalności ChPL z Ulotką dla pacjenta (zob. DEC-002), uruchomiono drugą rundę poszerzającą o źródła refundacji operacyjnej oraz dokumenty pokrewne. Lista kandydatów obejmowała: URPL Ulotki dla pacjenta (jako odrębny strumień obok ChPL), zarządzenia Prezesa NFZ, komunikaty BIP NFZ (centrala), dla lekarzy oraz dla świadczeniodawców (16 oddziałów wojewódzkich), MZ lista leków zagrożonych dostępnością, URPL komunikaty bezpieczeństwa (*Direct Healthcare Professional Communication*, DHPC), formularze pharmacovigilance.

Każdego kandydata weryfikowano niezależnymi zapytaniami w wyszukiwarce internetowej z polskimi słowami kluczowymi. Polskie zasoby specjalistyczne bywają słabo indeksowane w anglojęzycznych wyszukiwarkach — zastosowano łagodną ewaluację z explicit oznaczaniem kandydatów statusem `UNVERIFIED` w sytuacjach niepewności. Wszystkie zweryfikowane URL-e znajdują się w `thesis_research/sources_catalog.md` w sekcji *Linki źródłowe*.

### 3.2.4. Pipeline selekcji

Pipeline selekcji kandydatów na finalne źródła korpusu przebiegał w pięciu etapach sekwencyjnych. Każdy etap odsiewał kandydatów niespełniających odpowiedniego kryterium:

```
Kandydaci zidentyfikowani (28 łącznie w 2 rundach)
       │
       ▼
Weryfikacja w wyszukiwarce (≥3 zapytania per źródło, PL keywords)
       │
       ▼
Audyt licencji (explicit license OR status urzędowy Art. 4)
       │
       ▼
Test feasibility scrape (API / OAI-PMH / structured URL / parseable PDF)
       │
       ▼
Test specjalizacji treści (terminologia farmaceutyczna obecna)
       │
       ▼
Akceptacja: 13 źródeł / odrzucenie: 6 / weryfikacja-bez-włączenia: 9
```

Kategoria *weryfikacja-bez-włączenia* (9 źródeł) obejmuje przypadki, w których zasób istnieje i jest legalnie dostępny, ale jego włączenie do korpusu nie wnosiłoby wartości metodologicznej. Przykłady:

- *Dataset 397* na `dane.gov.pl` — mirror feedu RPL XML URPL. Włączenie obu duplikowałoby treść i wymuszało dodatkowy etap deduplikacji; wybrano źródło pierwotne URPL.
- Komunikaty 16 oddziałów wojewódzkich NFZ — wysoki poziom redundancji z komunikatami centrali (te same regulacje, regionalne variants formatowania); wybrano centralę, oddziały wykluczone.
- Czasopismo Aptekarskie — częściowy dostęp do fragmentów bez warunków permissive license; włączenie wymuszałoby manualną kuratorską selekcję per artykuł.

Pełne uzasadnienia per pozycja oraz lista wszystkich 28 kandydatów dostępne są w `thesis_research/sources_catalog.md` w sekcji *Selection pipeline*.

### 3.2.5. Skład finalny korpusu

Tabela 3.1 przedstawia skład finalny korpusu po selekcji w sześciu strata, opisanych szczegółowo w sekcji 3.3. Kolumna *Target docs* zawiera planowane wielkości próby per strata; kolumna *Pary header→body* zawiera szacunek liczby naturalnych par *zapytanie → passage* możliwych do wyodrębnienia z deterministycznych nagłówków sekcji bez kosztu LLM-paraphrased query generation.

**Tabela 3.1.** Skład korpusu po selekcji źródeł.

| Strata | Źródło | Target docs | % korpusu | Licencja | Scrape | Pary header→body |
|---|---|---:|---:|---|---|---:|
| 1. Regulatory professional | ChPL (URPL RPL) | 900 | 22% | Art. 4 urzędowe | XML feed + API + PDF | ~8 100 |
| 2. Regulatory consumer | Ulotki (URPL RPL, *paired*) | 900 | 22% | Art. 4 urzędowe | API leaflet endpoint | ~5 400 |
| 3. HTA + refundation legal | AOTMiT + MZ obwieszczenia + programy B.xx | 700 | 17% | Art. 4 urzędowe | BIP HTML + PDF | ~2 200 |
| 4. Refundation operational | Zarządzenia Prezesa NFZ + BIP komunikaty | 400 | 10% | Art. 4 urzędowe | HTML index + PDF | ~1 500 |
| 5. OA PL journals | Farmacja Polska + Lek w Polsce + AAMS + CIPMS | 900 | 22% | CC BY-NC / NC-ND / SA | OAI-PMH + JATS | ~2 700 |
| 6. Adjacencies | URPL DHPC + MZ lista braków | 300 | 7% | Art. 4 urzędowe | HTML + PDF | ~300 |
| **Razem** | | **~4 100** | **100%** | | | **~20 200** |

> 🟡 **Numbers TBD post-Iteracja 1.** Wartości kolumn *Target docs* oraz *Pary header→body* są wartościami **planowanymi**. Wartości faktyczne (post-scrape, po deduplikacji, po filtrowaniu OCR quality, po wykluczeniu rekordów uszkodzonych) raportowane w R4 *Eksploracyjna analiza danych*, sekcja 4.1 *Szumy i jakość*.

Skład finalny obejmuje ponadto:

- **6 źródeł odrzuconych explicit:** Farmakopea Polska, Czasopismo Aptekarskie, Medycyna Praktyczna, Acta Poloniae Pharmaceutica (jako źródło PL training; jako PL-EN literature anchor pozostaje cytowana w R2), Postępy Farmacji, API statystyki NFZ.
- **9 źródeł zweryfikowanych, ale nie włączonych:** dataset 397 dane.gov.pl, regionalne komunikaty 16 oddziałów wojewódzkich NFZ, fragmenty Czasopisma Aptekarskiego oraz pozostałe pozycje wymienione w `sources_catalog.md`.

Powyższa metodologia jest **bezpośrednią odpowiedzią na uwagi promotora z poprzedniej iteracji pracy**, w której zarzucone zostało *brak rygorystycznej metodologii doboru źródeł*. Sekcje 3.2.1–3.2.5 dokumentują wszystkie wymagane komponenty: kryteria inkluzji, kryteria ekskluzji, strategię wyszukiwania, pipeline selekcyjny oraz statystykę selekcji.

## 3.3. Strata korpusu — opis szczegółowy

W tej sekcji opisano szczegółowo każdą z sześciu strata wskazanych w Tabeli 3.1: źródło, charakterystykę treści, sample target oraz mapowanie na sygnał treningowy dla rerankera. Pełne URL-e oraz parametry scrape per źródło dostępne są w `sources_catalog.md`.

### 3.3.1. Strata 1: Regulatory professional (ChPL)

Strata pierwsza zawiera *Charakterystyki Produktu Leczniczego* (ChPL) z Rejestru Produktów Leczniczych prowadzonego przez URPL. ChPL jest dokumentem profesjonalnym kierowanym do lekarzy i farmaceutów, o standaryzowanej strukturze dziesięciu sekcji zgodnej z wytycznymi *Quality Review of Documents* (QRD) Europejskiej Agencji Leków [5]. Struktura ta jest deterministyczna na poziomie wytycznych URPL i w rezultacie identyczna dla wszystkich produktów leczniczych zarejestrowanych w polskim rejestrze:

1. Nazwa produktu leczniczego
2. Skład jakościowy i ilościowy
3. Postać farmaceutyczna
4.1. Wskazania do stosowania
4.2. Dawkowanie i sposób podawania
4.3. Przeciwwskazania
4.4. Specjalne ostrzeżenia i środki ostrożności
4.5. Interakcje z innymi produktami leczniczymi
4.6. Wpływ na płodność, ciążę i laktację
4.7. Wpływ na zdolność prowadzenia pojazdów
4.8. Działania niepożądane
4.9. Przedawkowanie
5. Właściwości farmakologiczne
6. Dane farmaceutyczne

Deterministyczna struktura sekcji umożliwia naturalne mapowanie nagłówka sekcji jako *zapytanie* a treści sekcji jako *passage* dla rerankera, bez konieczności manualnej anotacji ani LLM-paraphrased query generation. Sample target wynosi 900 produktów leczniczych próbkowanych stratyfikowanie z populacji ~10 000–14 000 unikalnych rekordów aktywnych w RPL (algorytm — sekcja 3.5).

Źródło danych: feed XML z `https://rejestry.ezdrowie.gov.pl/registry/rpl` z dziennym snapshot (`https://rejestry.ezdrowie.gov.pl/api/rpl/medicinal-products/public-pl-report/6.0.0/overall.xml`) oraz schemat XSD (`https://rejestry.ezdrowie.gov.pl/api/rpl/medicinal-products/public-pl-report/6.0.0/xml-schema-definition.xsd`). URL-e ChPL i Ulotki per produkt zawarte są w atrybutach `charakterystyka` i `ulotka` na elemencie `<produktLeczniczy>` (URL-e nie są generowane wg szablonu — wymaga to parsowania feedu XML, nie URL building). Większość PDF-ów jest tekstowych; szacowany odsetek skanowanych PDF-ów wymagających OCR wynosi 5–10% (Tesseract w trybie polskim `-l pol`). Faktyczny odsetek scanned PDFs zostanie zweryfikowany w Iteracji 0a feasibility (pre-condition #6, sekcja 3.4.3).

### 3.3.2. Strata 2: Regulatory consumer (Ulotki dla pacjenta) — paired z ChPL

Strata druga zawiera *Ulotki dla pacjenta* pochodzące z tego samego rejestru URPL, w pełnej parze z ChPL ze Strata 1 (definicja operacyjna pojęcia *paired* w sekcji 3.4). Ulotka jest dokumentem laypersonowskim kierowanym do pacjenta, o strukturze sześciu sekcji zgodnej z wytycznymi QRD:

1. Co to jest lek X i w jakim celu się go stosuje
2. Informacje ważne przed przyjęciem/zastosowaniem leku X
3. Jak przyjmować/stosować lek X
4. Możliwe działania niepożądane
5. Jak przechowywać lek X
6. Zawartość opakowania i inne informacje

Ulotka i ChPL opisują ten sam lek w dwóch rejestrach językowych — profesjonalnym i laypersonowskim — co stanowi materiał empiryczny dla eksperymentu *cross-register retrieval* (RQ5/H5, decyzja DEC-002). Sample target: 900 par (dokładnie te same `productID` co w Strata 1, gwarantujące pełen alignment przez identyfikator decyzji administracyjnej). Endpoint API ulotki: `https://rejestry.ezdrowie.gov.pl/api/rpl/medicinal-products/{N}/leaflet`, gdzie `N` jest identyfikatorem sekwencyjnym różnym od atrybutu `id` na elemencie `<produktLeczniczy>`.

### 3.3.3. Strata 3: HTA + refundation legal (AOTMiT + MZ)

Strata trzecia łączy dokumenty oceny technologii medycznych oraz akty refundacyjne. Strata ta podzielona jest na dwie sub-strata:

- **3a. AOTMiT** — Agencja Oceny Technologii Medycznych i Taryfikacji wytwarza raporty *Health Technology Assessment* (HTA), rekomendacje Prezesa Agencji oraz raporty taryfikacyjne. Adresy: `https://bip.aotm.gov.pl/` (CMS aktualny) oraz `https://bipold.aotm.gov.pl/` (archiwum legacy z PDF-ami sprzed migracji CMS). Struktura raportów obejmuje stałe sekcje: *Problem decyzyjny / Skuteczność kliniczna / Bezpieczeństwo / Analiza ekonomiczna / Wpływ na budżet / Rekomendacje innych agencji*. Skala: ~2000+ raportów od 2012 r., ~200/rok dodawanych.
- **3b. MZ obwieszczenia oraz programy lekowe B.xx** — listy refundacyjne (publikowane co dwa miesiące jako obwieszczenia Ministra Zdrowia) oraz ok. 120 aktywnych programów lekowych B.01–B.XX. Adresy: `https://www.gov.pl/web/zdrowie/obwieszczenia-ministra-zdrowia-lista-lekow-refundowanych` oraz Dziennik Urzędowy Ministra Zdrowia `https://dziennikmz.mz.gov.pl/`. Programy lekowe są mini-specyfikacjami klinicznymi per indykacja, zawierającymi kryteria włączenia, schematy dawkowania, kryteria wyłączenia oraz wymagania monitorowania.

Sample target Strata 3: ~700 dokumentów (z czego ~300 raportów AOTMiT mix specialty classes oraz ~400 dokumentów MZ — programy B.xx + ostatnie 30 obwieszczeń refundacyjnych).

### 3.3.4. Strata 4: Refundation operational (NFZ)

Strata czwarta zawiera dokumenty operacjonalizujące programy lekowe po stronie płatnika publicznego — Narodowego Funduszu Zdrowia. Dwa główne strumienie:

- **Zarządzenia Prezesa NFZ** — operacjonalizacja programów lekowych z kodami ICD-10, kryteriami kwalifikacji, schematami dawkowania, badaniami monitorującymi, katalogiem ryczałtów. Adres: `https://www.nfz.gov.pl/zarzadzenia-prezesa/zarzadzenia-prezesa-nfz/`. Treści te są inną klasą *query type* niż AOTMiT (medical) i MZ (legal) — operacyjne, regulacyjne na poziomie billing płatnika.
- **BIP NFZ komunikaty centralne** oraz **komunikaty dla lekarzy**. Adresy: `https://www.nfz.gov.pl/bip/komunikaty/` oraz `https://www.nfz.gov.pl/dla-lekarzy/komunikaty/`. Treści dotyczące zmian regulacyjnych, harmonogramów wdrożeń programów, *clinical guidance* dotyczących programów aktywnych.

Świadomie pominięto komunikaty 16 regionalnych oddziałów wojewódzkich NFZ ze względu na wysoki poziom redundancji z treściami centrali (decyzja udokumentowana w sekcji 3.2.4). Sample target Strata 4: ~400 dokumentów.

### 3.3.5. Strata 5: Open-access PL journals

Strata piąta obejmuje cztery polskojęzyczne czasopisma open-access o profilu farmaceutycznym i farmakologicznym. Wszystkie cztery posiadają explicit licencje *Creative Commons*, co zapewnia czystą *license story* korpusu. Tabela 3.2 przedstawia szczegóły per czasopismo.

**Tabela 3.2.** Strata 5 — czasopisma open-access wraz z licencjami i metodami scrape.

| Czasopismo | Wydawca | Licencja | URL źródłowy | Mirror / metoda scrape |
|---|---|---|---|---|
| Farmacja Polska | Polskie Towarzystwo Farmaceutyczne | CC BY-NC 4.0 | `ptfarm.pl/.../farmacja-polska/` | `bibliotekanauki.pl/journals/1109` (OAI-PMH przez ICM UW) |
| Lek w Polsce | Wydawnictwo Medyk | CC BY-NC-ND 4.0 | `lekwpolsce.pl/` | Biblioteka Cyfrowa UŁ (dLibra, OAI-PMH) |
| AAMS (*Annales Academiae Medicae Silesiensis*) | Śląski Uniwersytet Medyczny | CC BY-SA 4.0 | `annales.sum.edu.pl/` | DOAJ ToC |
| CIPMS (*Current Issues in Pharmacy and Medical Sciences*) | Uniwersytet Medyczny w Lublinie | CC BY-NC-ND | `czasopisma.umlub.pl/curipms` | Sciendo JATS XML |

Sample target Strata 5: ~900 artykułów (mix wszystkich czterech tytułów z preferencją dla artykułów typu *review* i *original research* nad commentary/editorial, ze względu na większą gęstość terminologii farmakologicznej). Strategia scrape preferuje OAI-PMH oraz JATS XML nad bezpośrednim crawl HTML wydawcy ze względu na czystszą strukturę metadata oraz jednoznaczność identyfikatorów (DOI, *issue ID*, daty publikacji).

### 3.3.6. Strata 6: Adjacencies

Strata szósta uzupełnia korpus dokumentami niskoobjętościowymi o wysokiej wartości informacyjnej:

- **URPL komunikaty bezpieczeństwa** (*Direct Healthcare Professional Communications*, DHPC): `https://www.gov.pl/web/urpl/komunikaty-bezpieczenstwa`. Krótkie alerty bezpieczeństwa skoordynowane z Europejską Agencją Leków, dotyczące nowych ostrzeżeń, modyfikacji wskazań, wycofań partii.
- **MZ lista leków zagrożonych brakiem dostępności**: `https://dziennikmz.mz.gov.pl/keywords/55`. Obwieszczenia o niedoborach publikowane co ~2 miesiące, dokumentujące brak dostępności wybranych produktów na rynku polskim.

Sample target Strata 6: ~300 dokumentów. Dokumenty te są krótkie, ale generują naturalne *zapytania* typu *„Czy są nowe ostrzeżenia dla leku X?"* lub *„Czy lek X jest dostępny w aptekach?"* — *passage* tworzą bezpośrednio treść alertu lub wpisu listy braków.

## 3.4. Paired ChPL↔Ulotka — definicja operacyjna i walidacja integrity

W tej sekcji zdefiniowano operacyjnie pojęcie *paired ChPL↔Ulotka* dla potrzeb eksperymentu RQ5 (decyzja DEC-002) oraz opisano procedurę walidacji integrity par realizowaną w Iteracji 0a feasibility.

### 3.4.1. Co znaczy "paired"

Dwa dokumenty (jeden ChPL, jedna Ulotka) są **paired** wtedy i tylko wtedy, gdy spełnione są wszystkie trzy warunki konstytutywne:

1. **Identyczny `productID` w rejestrze RPL URPL.** `productID` jest jednoznacznym identyfikatorem decyzji administracyjnej (pozwolenia na obrót). Oba dokumenty muszą być dokumentami wyjściowymi tego samego pozwolenia.
2. **Synchronizowana `data_modyfikacji`.** Wartości pól `data_modyfikacji` ChPL i Ulotki muszą być identyczne lub mieścić się w tolerancji ±1 dzień. Zmiany regulacyjne (rozszerzenie wskazań, modyfikacja przeciwwskazań, dodanie nowych działań niepożądanych) są aplikowane do obu dokumentów równolegle w jednym cyklu URPL; rozjazd ich dat sygnalizuje desinkronizację.
3. **Zgodny zakres semantyczny.** Oba dokumenty muszą opisywać tę samą wersję leku (te same wskazania, dawkowanie, przeciwwskazania, działania niepożądane, zatwierdzone w tym samym cyklu rejestracji). Warunek ten jest weryfikowany na próbie spot-check w Iteracji 0a (sekcja 3.4.3).

### 3.4.2. Co NIE znaczy "paired"

Dla uniknięcia ambiwalencji, poniższe sytuacje **nie są** kwalifikowane jako pary:

1. **Różne wersje czasowe tego samego leku.** Archiwalna ChPL z 2020 r. i aktualna Ulotka z 2024 r. tego samego leku nie tworzą pary — wymagana jest najnowsza wersja obu dokumentów z tego samego cyklu administracyjnego.
2. **Różne formy farmaceutyczne tego samego API.** Tabletki 50 mg vs roztwór do wstrzykiwań 100 mg/ml mają osobne `productID` w rejestrze RPL — są traktowane jako niezależne produkty.
3. **Generic + brand-name dla tej samej DCI.** Generyk i preparat oryginalny tej samej substancji czynnej są wynikiem osobnych decyzji administracyjnych URPL, mają osobne `productID` i nie są agregowane w jeden produkt na poziomie sampling (zob. sekcja 3.5 *bias acknowledgment*).

### 3.4.3. Walidacja integrity par

Walidacja integrity par realizowana jest w fazie *Iteracji 0a feasibility* (zob. konspekt II.16 oraz `sources_catalog.md` § *Iteracja 0 — Feasibility pre-conditions*) na próbie 100 leków losowanych z RPL feed. Procedura walidacji obejmuje sprawdzenie pre-condition #5 — *ChPL↔Ulotka alignment rate*:

1. **Resolution endpointów.** Dla każdego z 100 `productID` URL-e w atrybutach `charakterystyka` i `ulotka` musi zwrócić HTTP 200 oraz valid PDF. Paired URL-e są generowane razem przez tę samą decyzję URPL — *semantic equivalence by construction* na poziomie technicznym.
2. **Date alignment.** Pole per-product `data_modyfikacji` **nie istnieje** w XML feedzie URPL na poziomie pojedynczego leku — w feedzie znajduje się jedynie snapshot-level `stanNaDzien` na elemencie root `<produktyLecznicze>`. Alignment dat musi zatem być sprawdzany przez nagłówek HTTP `Last-Modified` z odpowiedzi PDF (jeśli serwer go ustawia), z fallbackiem na *both endpoints OK* (akceptowalne na podstawie strukturalnej parowalności URL-i).
3. **Competence-stratified spot-check semantycznej zgodności.** Manualna weryfikacja zgodności semantycznej na próbie 100 par przebiegła wg następującej procedury:
   - 10 par z 100 — wszystkie wybrane z **psychiatrycznej podgrupy ATC N05/N06**, gdzie autorka posiada kompetencje semantyczne pozwalające zweryfikować zgodność (uzasadnienie spójne z DEC-001 *eval set design*).
   - Pozostałe 90 par non-psych — wyłącznie sygnał proxy (`productID` match + `Last-Modified` ±1 dzień jeśli dostępne) **bez weryfikacji semantycznej**. Ograniczenie to jest jawnie oznaczone w sekcji 3.10 (*świadome biases*) oraz w R8 (*limitations*).

Próg akceptacji: ≥90% par o pełnym pairing integrity (technicznym + temporalnym + semantycznym dla psych subset). Spadek poniżej 90% w *warning band* (80–89%) wymusza zacieśnienie tolerancji `data_modyfikacji` z ±1 dzień na 0 dni i ponowny pomiar; spadek poniżej 80% uruchamia kill criteria DEC-001.

**Tabela 3.3.** Pre-conditions feasibility Iteracji 0a (warunki konieczne dla wejścia w Iterację 1).

| # | Pre-condition | Próg akceptacji | Metryka | Wynik | Status |
|---|---|---|---|---|---|
| 1 | URPL RPL XML uptime | ≥99% w oknie 24h | probe co 1h, `status_code == 200` | `[TBD post-Iteracja 0a]`% | `[TBD]` |
| 2 | URPL XML feed parse-ability | 100% valid XML | `xml.etree.parse()` bez exceptions | `[TBD]`% | `[TBD]` |
| 3 | ChPL endpoint response time | p95 < 2s | wall-clock difference per request | `[TBD]` s | `[TBD]` |
| 4 | Ulotka endpoint response time | p95 < 2s | wall-clock difference per request | `[TBD]` s | `[TBD]` |
| 5 | ChPL↔Ulotka alignment rate | ≥90% par (10/10 psych spot-check) | both endpoints valid + competence-stratified spot-check | `[TBD]`% | `[TBD]` |
| 6 | OCR overhead | <15% korpusu | text-layer detection `pdfplumber.extract_text()` non-empty | `[TBD]`% | `[TBD]` |

Wynik walidacji raportowany w `thesis_research/iteration-0-feasibility-report.md` i przeniesiony do tabeli 3.3 po zakończeniu Iteracji 0a.

## 3.5. Algorytm próbkowania stratyfikowanego

### 3.5.1. Cel i strategia

Próbkowanie 900 leków z populacji ~10 000–14 000 unikalnych produktów aktywnych w RPL musi pogodzić dwa cele równoważne na poziomie projektowania korpusu:

- **(a) Over-representacja psychiatrycznej podgrupy ATC N05 (Psycholeptica) i N06 (Psychoanaleptica)** — aby umożliwić leverage manualnej walidacji *eval setu* przez autorkę (DEC-001 § *Uzasadnienie* pkt 1). Manualna walidacja 200 par gold standard wymaga, aby autorka semantycznie rozumiała treść *passages* — wybór psychiatrycznej podgrupy umożliwia rygorystyczną walidację RQ2/H2 bez konieczności angażowania zewnętrznych ekspertów farmaceutycznych.
- **(b) Szerokość pokrycia farmakologicznego** — aby trening rerankera nie był zawężony do jednej klasy ATC, lecz pokrywał różne klasy farmaceutyczne (przeciwbólowe, kardiologiczne, antyinfekcyjne, dermatologiczne i inne).

Wybrana strategia łączy oba cele: 30% próby z N05/N06 + 70% równowagi przez 14 klas ATC Level 1. Klasy ATC Level 1 wg WHOCC obejmują: A (*Alimentary tract and metabolism*), B (*Blood and blood forming organs*), C (*Cardiovascular system*), D (*Dermatologicals*), G (*Genito-urinary system and sex hormones*), H (*Systemic hormonal preparations*), J (*Antiinfectives for systemic use*), L (*Antineoplastic and immunomodulating agents*), M (*Musculo-skeletal system*), N (*Nervous system*), P (*Antiparasitic products*), R (*Respiratory system*), S (*Sensory organs*), V (*Various*).

### 3.5.2. Pseudokod algorytmu

Algorytm 3.1 przedstawia pseudokod implementacji próbkowania stratyfikowanego. Pełna implementacja produkcyjna znajduje się w `main_project/src/ingest/sampling.py`.

**Algorytm 3.1.** Stratified sampling 900 leków z populacji URPL.

```python
import random

RANDOM_SEED = 42                # zafiksowany w configs/sampling.yaml
TARGET_TOTAL = 900
PSYCH_OVERREP_PROP = 0.30       # 30% z N05+N06

def stratified_sample(all_drugs):
    # Split do dwoch pul
    psych_pool = [d for d in all_drugs if d.atc_code[:3] in ("N05", "N06")]
    other_pool = [d for d in all_drugs if d.atc_code[:3] not in ("N05", "N06")]

    psych_n = int(TARGET_TOTAL * PSYCH_OVERREP_PROP)   # 270
    other_n = TARGET_TOTAL - psych_n                   # 630

    random.seed(RANDOM_SEED)

    # Psych: equal split N05 vs N06
    n05 = [d for d in psych_pool if d.atc_code[:3] == "N05"]
    n06 = [d for d in psych_pool if d.atc_code[:3] == "N06"]
    psych_sample = (
        random.sample(n05, min(psych_n // 2, len(n05))) +
        random.sample(n06, min(psych_n - psych_n // 2, len(n06)))
    )

    # Other: stratified by ATC Level 1 (14 broad classes)
    classes_lvl1 = sorted(set(d.atc_code[0] for d in other_pool))
    per_class = other_n // len(classes_lvl1)           # ~45 per class
    other_sample = []
    for cls in classes_lvl1:
        pool = [d for d in other_pool if d.atc_code[0] == cls]
        other_sample.extend(random.sample(pool, min(per_class, len(pool))))

    # Fill remainder gdy niektore klasy ATC < per_class (np. rzadkie ATC P)
    remaining = TARGET_TOTAL - len(psych_sample) - len(other_sample)
    if remaining > 0:
        picked = {d.product_id for d in psych_sample + other_sample}
        extra_pool = [d for d in other_pool if d.product_id not in picked]
        other_sample.extend(random.sample(extra_pool, min(remaining, len(extra_pool))))

    return psych_sample + other_sample
```

### 3.5.3. Gwarancje reprodukowalności

Reprodukowalność próbkowania jest zagwarantowana przez trzy mechanizmy:

1. **Random seed.** Wartość `42` zafiksowana w pliku `main_project/configs/sampling.yaml`. Recenzent uruchamiający algorytm na tej samej migawce RPL XML uzyska identyczny zestaw 900 `productID` (z dokładnością do kolejności elementów w listach generowanych przez `random.sample`, która jest deterministyczna dla zafiksowanego seed).
2. **Snapshot listy próby.** Lista wybranych `productID` zapisywana w `data/raw/sample-list-YYYY-MM-DD.csv` i wersjonowana przez DVC (sekcja 3.6 + 3.9). Plik snapshot jest immutable po wygenerowaniu.
3. **Reprodukcja zewnętrzna.** Możliwa przez `dvc pull data/raw/sample-list-<date>.csv` (pobranie konkretnego snapshot) lub re-run skryptu `sampling.py` na zafiksowanym snapshot RPL XML.

Faktyczna kompozycja próby (post-sampling): liczebność per klasa ATC Level 1 oraz Level 4 N05/N06 — `[TBD post-Iteracja 1]`. Raportowana w R4 (*Eksploracyjna analiza danych*) jako *Figura 4.X — rozkład klas ATC w spróbkowanym korpusie*.

### 3.5.4. Trade-off: equal-weight vs natural distribution

Wybrano strategię *equal-weight* w obrębie 14 klas ATC Level 1 zamiast próbkowania zachowującego naturalną dystrybucję URPL. Uzasadnienie tego wyboru opiera się na celu pracy:

- Cel pracy stanowi test rerankera na **zróżnicowanych domenach farmaceutycznych** (Cardio, Anti-infectives, Dermatologicals, Nervous system, i in.), nie symulacja realnej dystrybucji apteki ani realnego ruchu zapytań pacjenckich.
- Próbkowanie zgodne z naturalną dystrybucją URPL nadreprezentowałoby leki *Cardiovascular* (klasa C, dominująca w naturalnym rejestrze ze względu na liczbę dostępnych preparatów na nadciśnienie i hipercholesterolemię) oraz pod-reprezentowałoby klasy rzadkie (P *Antiparasitic*, V *Various*). Tracimy na *diversity* sygnału treningowego, zyskujemy na realizmie populacyjnym — wybór preferuje *diversity*.

Wybór ten jest świadomą decyzją metodologiczną mającą konsekwencję w postaci *biasu ATC* (sekcja 3.10 pkt 2).

### 3.5.5. Bias acknowledgment

Algorytm próbkowania wprowadza trzy świadome biasy, jawnie odnotowane w sekcji 3.10:

- **N05/N06 over-representation** — 3-krotne over-rep psych vs naturalna proporcja URPL (~10%).
- **Rzadkie klasy ATC** — klasy P (*Antiparasitic*) i V (*Various*) mogą być pod-sampled, jeśli ich populacja w URPL jest mniejsza niż 45 leków per klasa (target *per-class* dla 70% próby równoważnej). W tym przypadku algorytm wypełnia brakującą próbę z klasy *other_pool* w sposób losowy.
- **Brand vs generic** — sampling po `productID` traktuje preparaty generyczne i brand-name jako osobne produkty (osobne decyzje administracyjne URPL, osobne `productID`). Generyk i preparat oryginalny tej samej DCI mogą zatem oba trafić w próbę. Brak deduplikacji na poziomie DCI jest świadomy — różnice w treści ChPL między generykiem a preparatem oryginalnym (np. różne profile działań niepożądanych, różne przeciwwskazania w zależności od formy) są sygnałem potencjalnie wartościowym dla rerankera.

## 3.6. Struktura folderów, naming conventions, versioning

Struktura katalogowa repozytorium dla danych jest zorganizowana zgodnie z konwencją *raw / processed / docs* wg wymogów Task 03 oraz dobrych praktyk reproducible research:

```
main_project/
├── data/
│   ├── raw/                     # read-only po snapshocie
│   │   ├── chpl/                # Strata 1 (PDF + XML metadata)
│   │   ├── ulotki/              # Strata 2 (PDF + XML metadata)
│   │   ├── aotmit/              # Strata 3a (PDF)
│   │   ├── mz/                  # Strata 3b (PDF + HTML)
│   │   ├── nfz/                 # Strata 4 (PDF + HTML)
│   │   ├── journals/            # Strata 5 (JATS XML + PDF)
│   │   ├── adjacencies/         # Strata 6 (PDF)
│   │   └── sample-list-YYYY-MM-DD.csv      # snapshot listy proby
│   ├── processed/
│   │   ├── chunks/              # po chunkowaniu section-aware
│   │   ├── embeddings/          # BGE-M3 1024-dim per chunk
│   │   ├── eval_pairs/          # 200 par gold standard + 1800 cross-register
│   │   └── preference_dataset/  # ~145k preference quadruplets
│   └── docs/
│       ├── codebook_chpl.md
│       ├── codebook_ulotki.md
│       ├── codebook_aotmit.md
│       ├── codebook_mz.md
│       ├── codebook_nfz.md
│       ├── codebook_journals.md
│       └── codebook_adjacencies.md
└── configs/
    └── sampling.yaml             # RANDOM_SEED = 42, TARGET_TOTAL = 900
```

**Konwencje nazewnictwa plików** (zgodnie z Task 03 § 1.1):

- Pliki raw: `<strata>_<productID lub doc_id>_<YYYYMMDD>.<ext>`. Przykład: `chpl_39257_20250612.pdf`.
- Chunks: `<strata>_<productID>_<section_id>_chunk_<NNN>.json`. Przykład: `chpl_39257_4.3_chunk_001.json`.
- Eval pairs: `eval_<set>_<NNN>.json`, gdzie `<set>` ∈ `{gold_psych_200, cross_register_1800}`.
- Snapshoty: `<artifact>-YYYY-MM-DD.<ext>`. Przykład: `corpus-2026-05-21.tar.zst`.

**Versioning danych:**

- `data/raw/` — *read-only* po snapshocie. Każda modyfikacja źródła (re-scrape po update URPL, dodanie nowego źródła) wymaga nowego snapshot date i tworzy nowy katalog snapshot-aware.
- DVC (*Data Version Control*) jako warstwa wersjonowania binarnych artefaktów (PDF, embeddings, preference quadruplets) z backendem MinIO (S3-compatible object storage). Plik `dvc.lock` w katalogu głównym repozytorium fixuje hash SHA-256 wszystkich artefaktów.
- Każdy commit kodu, który zmienia processing pipeline (chunking, embedding, generation queries), kojarzony z konkretnym snapshot date przez `dvc.lock`.
- `git` śledzi kod, configs, codebooks oraz pliki `.dvc` wskazujące na artefakty (sam artefakt nie jest w `git`, w `git` jest tylko jego hash i ścieżka w MinIO).

## 3.7. Codebooks (data dictionaries)

Dla każdej strata przygotowano *codebook* (data dictionary) w formacie markdown, przechowywany w `data/docs/codebook_<strata>.md`. Codebook zawiera definicje wszystkich pól metadanych oraz pól ekstrahowanych z dokumentów: typ danych, zakres dopuszczalnych wartości, jednostki (gdy dotyczy), pochodzenie pola (parsing PDF, XML feed, derived). Poniżej przedstawiono wycinki dla dwóch kluczowych strata; pełne codebooks znajdują się w katalogu `main_project/data/docs/`.

### 3.7.1. Codebook ChPL (wycinek)

**Tabela 3.4.** Wycinek codebook'a Strata 1 (ChPL).

| Pole | Typ | Znaczenie | Wartości / format | Pochodzenie |
|---|---|---|---|---|
| `product_id` | int | Identyfikator decyzji administracyjnej URPL | unique, np. `39257` | RPL XML feed |
| `atc_code` | string | Klasyfikacja ATC | format `[A-V][0-9]{2}[A-Z][A-Z][0-9]{2}`, np. `N06AB06` | RPL XML feed (jeśli obecne) |
| `data_modyfikacji` | date | Data ostatniej modyfikacji rejestru | ISO 8601 (`YYYY-MM-DD`) | snapshot-level `stanNaDzien` |
| `section_id` | string | Identyfikator sekcji ChPL | enum `{1, 2, 3, 4.1, 4.2, …, 4.9, 5, 6}` | parsing PDF |
| `section_header` | string | Nagłówek sekcji | tekst PL | parsing PDF |
| `body_text` | string | Treść sekcji | tekst PL, normalizacja Unicode NFC | parsing PDF + OCR fallback |
| `register` | categorical | Rejestr językowy | const `{professional}` | const |
| `text_source_method` | categorical | Metoda ekstrakcji tekstu | enum `{text-layer, ocr_tesseract_pol}` | parsing pipeline |
| `ocr_confidence` | float | Confidence OCR (null gdy text-layer) | `[0.0, 1.0]` | Tesseract output |
| `scrape_date` | date | Data pobrania ze źródła | ISO 8601 | scrape script |
| `license` | string | Status licencyjny | const `Art. 4 ustawy o prawie autorskim` | const |

Pełna lista pól oraz weryfikacja obecności pola `atc_code` w faktycznych rekordach RPL — `[TBD post-Iteracja 1]`. Wstępna analiza schematu XSD URPL sugeruje, że pole `atc_code` może wymagać enrichment z zewnętrznego źródła ATC WHOCC dla części rekordów; weryfikacja w Iteracji 1 określi proporcję rekordów wymagających uzupełnienia.

### 3.7.2. Codebook Ulotki (wycinek)

**Tabela 3.5.** Wycinek codebook'a Strata 2 (Ulotki dla pacjenta).

| Pole | Typ | Znaczenie | Wartości / format | Pochodzenie |
|---|---|---|---|---|
| `product_id` | int | Identyfikator decyzji administracyjnej URPL (paired z ChPL) | unique, paired key | RPL XML feed |
| `paired_chpl_id` | int | FK do `chpl.product_id` | musi mieć match w Strata 1 | derived |
| `section_id` | string | Identyfikator sekcji Ulotki | enum `{1, 2, 3, 4, 5, 6}` | parsing PDF |
| `section_header` | string | Nagłówek sekcji (QRD) | tekst PL | parsing PDF |
| `body_text` | string | Treść sekcji | tekst PL, normalizacja Unicode NFC | parsing PDF |
| `register` | categorical | Rejestr językowy | const `{lay}` | const |
| `data_modyfikacji_inferred` | date | Data modyfikacji (inferred via HTTP `Last-Modified`) | ISO 8601 lub null | HTTP header |
| `pairing_status` | categorical | Wynik walidacji pairing (Iteracja 0a) | enum `{ok, date_drift, missing_chpl, semantic_mismatch}` | derived |
| `scrape_date` | date | Data pobrania | ISO 8601 | scrape script |
| `license` | string | Status licencyjny | const `Art. 4 ustawy o prawie autorskim` | const |

### 3.7.3. Pozostałe codebooks

Lokalizacja pełnych codebooks pozostałych strata przedstawiona jest w Tabeli 3.6.

**Tabela 3.6.** Lokalizacja pełnych codebooks per strata oraz specyficzne pola.

| Strata | Plik codebook | Specyficzne pola |
|---|---|---|
| 3a AOTMiT | `data/docs/codebook_aotmit.md` | `report_type`, `decision_class`, `indication`, `recommendation` |
| 3b MZ | `data/docs/codebook_mz.md` | `obwieszczenie_id`, `program_id` (B.01–B.XX), `effective_date` |
| 4 NFZ | `data/docs/codebook_nfz.md` | `zarzadzenie_id`, `program_id`, `category` (Zarządzenie / Komunikat / Dla lekarzy) |
| 5 OA Journals | `data/docs/codebook_journals.md` | `journal`, `issue`, `year`, `doi`, `license_per_article` |
| 6 Adjacencies | `data/docs/codebook_adjacencies.md` | `alert_id`, `alert_type` (DHPC vs shortage), `effective_date` |

Pełne wartości i przedziały `[TBD post-Iteracja 1]` — finalizowane wraz z pełnym scrape pipeline.

## 3.8. Aspekty etyczne i licencyjne

### 3.8.1. Status urzędowy źródeł regulatorowych

Wszystkie cztery strata regulatorowe (1 ChPL, 2 Ulotki, 3 AOTMiT/MZ, 4 NFZ) oraz strata 6 (URPL DHPC, MZ braki) korzystają z **wyłączenia spod ochrony prawa autorskiego** na mocy Art. 4 ustawy z dnia 4 lutego 1994 r. o prawie autorskim i prawach pokrewnych [3]. Przepis ten stanowi:

> *„Nie stanowią przedmiotu prawa autorskiego: 1) akty normatywne lub ich urzędowe projekty; 2) urzędowe dokumenty, materiały, znaki i symbole; 3) opublikowane opisy patentowe lub ochronne; 4) proste informacje prasowe."*

ChPL, Ulotki dla pacjenta, raporty AOTMiT, obwieszczenia Ministra Zdrowia, programy lekowe B.xx oraz zarządzenia Prezesa Narodowego Funduszu Zdrowia kwalifikują się jako *urzędowe dokumenty i materiały* w rozumieniu Art. 4 pkt 2 i są **zwolnione z ochrony prawnoautorskiej**. Wykorzystanie ich w pracy badawczej oraz dystrybucja w ramach reprodukowalnego korpusu pracy badawczej są dozwolone bez konieczności uzyskiwania zgody MAH (Marketing Authorization Holder), agencji wystawiających ani Ministerstwa Zdrowia.

### 3.8.2. Licencje CC OA czasopism (Strata 5)

Tabela 3.7 prezentuje audyt licencji per strata, łącząc statusy urzędowe (Art. 4) oraz licencje *Creative Commons* dla strata 5 (open-access journals).

**Tabela 3.7.** Audyt licencji per strata.

| Strata | Źródło | Licencja | Permitted use |
|---|---|---|---|
| 1 | ChPL (URPL) | Art. 4 urzędowe | research + redistribution + modification |
| 2 | Ulotki (URPL) | Art. 4 urzędowe | research + redistribution + modification |
| 3a | AOTMiT | Art. 4 urzędowe | research + redistribution + modification |
| 3b | MZ obwieszczenia + programy B.xx | Art. 4 urzędowe (akty prawne) | research + redistribution + modification |
| 4 | NFZ zarządzenia + BIP | Art. 4 urzędowe | research + redistribution + modification |
| 5a | Farmacja Polska (PTFarm) | CC BY-NC 4.0 | research (non-commercial), attribution required |
| 5b | Lek w Polsce (Medyk) | CC BY-NC-ND 4.0 | research (non-commercial, no derivatives), attribution required |
| 5c | AAMS (SUM) | CC BY-SA 4.0 | research + redistribution (share-alike), attribution required |
| 5d | CIPMS (UM Lublin) | CC BY-NC-ND | research (non-commercial, no derivatives), attribution required |
| 6a | URPL DHPC | Art. 4 urzędowe | research + redistribution + modification |
| 6b | MZ braki list | Art. 4 urzędowe | research + redistribution + modification |

**Konsekwencje licencji CC BY-NC-ND** (Lek w Polsce, CIPMS) — klauzula *no derivatives*: w pipeline'ie chunking dzieli artykuły na fragmenty, co technicznie może być interpretowane jako utwór pochodny. *Mitigation*: chunki przechowywane wewnętrznie do treningu rerankera, **bez redistribution chunked content**; redystrybucja korpusu po opublikowaniu pracy ograniczona do metadanych + linków do oryginałów dla tych dwóch źródeł. *Attribution* per artykuł zachowywana w polu `doi` codebook'a journals.

### 3.8.3. Brak danych osobowych — uzasadnienie braku komitetu etycznego

Korpus pracy zawiera **wyłącznie dokumenty regulacyjne, akty prawne i artykuły naukowe** publicznie udostępnione. Eksplicytnie nie zawiera:

- Danych pacjentów (rekordów medycznych, wyników badań klinicznych z identyfikatorami).
- Danych personalnych autorów ulotek lub MAH (treści są opracowywane korporacyjnie, podpisywane na poziomie podmiotu odpowiedzialnego, nie indywidualnych autorów).
- Treści generowanych przez użytkowników (forum, komentarze, social media, materiały *user-generated*).
- Identyfikowalnych danych o specjalistach medycznych pracujących nad rejestracją produktów.

W konsekwencji praca **nie wymaga zgody komisji bioetycznej** ani zgodności z RODO (rozporządzenie GDPR Unii Europejskiej) w zakresie danych osobowych — nie ma danych osobowych w korpusie. Zgodność z RODO ogranicza się do warstwy infrastrukturalnej (logi, metadane operacyjne pipeline'u), która nie jest częścią danych źródłowych.

### 3.8.4. Eval set: 200 par psych subset — etyka wyboru

Manualnie zwalidowany *eval set* (200 par gold standard) jest próbkowany z psychiatrycznej podgrupy korpusu (ATC N05 + N06). Wybór ten jest świadomą decyzją architektoniczną, uzasadnioną w DEC-001 § *Uzasadnienie* pkt 1: leverage manualnej walidacji kompetencji autorki w psychiatrycznej podgrupie ATC pozwala na rygorystyczną walidację LLM-as-judge agreement (RQ2/H2) bez konieczności angażowania zewnętrznych ekspertów farmaceutycznych.

Trening pozostaje na szerokim korpusie farmakologii; *eval set* jest wąski w podgrupie, którą autorka faktycznie zna semantycznie. Wybór wąskiego *eval set* nie wprowadza problemu etycznego — decyzja jest *transparent disclosed* w R3, R5 oraz w *limitations* R8, zgodnie z zasadą *transparent disclosure of design choices*. Świadome ujawnienie wyboru pozwala czytelnikom oraz recenzentom zrozumieć zakres, na jakim raportowane *kappa* dla LLM-as-judge jest *fair* (psych subset), a na jakim wymagana byłaby ekstrapolacja (cała farmakologia, gdzie autorka nie jest ekspertką).

## 3.9. Reproducibility statement

Pełna reprodukowalność korpusu zapewniona jest przez czterowarstwową strukturę:

1. **Kod scrape.** Katalog `main_project/src/ingest/` zawiera skrypty per strata: `ingest_chpl.py`, `ingest_ulotki.py`, `ingest_aotmit.py`, `ingest_mz.py`, `ingest_nfz.py`, `ingest_journals.py`, `ingest_adjacencies.py`. Każdy skrypt ma idempotentne semantyki — wielokrotne uruchomienie na tym samym snapshot date daje identyczny output (modulo non-deterministic timing artifacts w nazwach plików tymczasowych). Skrypty używają wyłącznie publicznych endpointów wymienionych w sekcji 3.3 oraz w `sources_catalog.md`.

2. **Snapshot date.** Każda pełna scrape produkcyjna jest oznaczona datą snapshot (`YYYY-MM-DD`) i traktowana jako *immutable*. Modyfikacje korpusu (np. dodanie nowych źródeł, re-scrape po update URPL feedu, dodanie nowych obwieszczeń MZ) tworzą nowy snapshot date z osobnym katalogiem.

3. **DVC tracking.** Binarne artefakty (PDF, embeddings, eval pairs, preference quadruplets) tracked przez DVC z backendem MinIO (S3-compatible). Plik `dvc.lock` w katalogu głównym repozytorium fixuje hash SHA-256 wszystkich artefaktów. Plik `.dvc` per artefakt znajduje się w katalogu właściwym dla artefaktu i jest częścią repozytorium git (sam binarny artefakt — nie).

4. **Configs versioning.** Plik `main_project/configs/sampling.yaml` zawiera `RANDOM_SEED = 42` oraz `TARGET_TOTAL = 900` i jest częścią repozytorium git. Recenzent uruchamiający algorytm próbkowania na tej samej migawce RPL XML otrzyma identyczny zestaw 900 `productID`.

**Reprodukcja snapshot z external machine:**

```bash
git clone <repo_url>
cd main_project
uv sync                                              # ustawienie srodowiska (Python 3.13, deps z pyproject.toml + uv.lock)
uv run python -m ingest.snapshot --date 2026-05-21   # reprodukcja snapshot (jesli RPL feed dostepny historycznie)
dvc pull data/raw/corpus-2026-05-21.tar.zst         # pobranie binariow z MinIO
```

Faktyczna data snapshot użytego w eksperymentach: `[TBD post-Iteracja 1]`.

**Ograniczenia reprodukowalności.** Pełna reprodukcja wymaga dostępu do MinIO backend autorki (nie publiczny) lub re-scrape z URPL na nowym snapshot date. Re-scrape może dać minimalnie różne wyniki, jeśli URPL między datami snapshot zaktualizował dokumenty (jest to *normal-case* dla rejestru live). Dla pełnej reproducibility eksperymentów, recenzentom udostępniana jest paczka `corpus-<date>.tar.zst` z uzgodnionego snapshot date przez DVC pull (klucze API udostępniane na żądanie).

## 3.10. Świadome biases korpusu

W tej sekcji jawnie nazwano pięć typów biasów obecnych w korpusie. Nazywanie biasów *ex ante* — przed eksperymentami — jest świadomą decyzją: pozwala na właściwą interpretację wyników w R7 oraz przygotowuje grunt pod sekcję *Limitations* w R8. Każdy z pięciu biasów jest następnie linkowany do propozycji kierunku przyszłej pracy (sekcja R8 *Future work*).

1. **License bias.** Preferencja dla źródeł urzędowych (Art. 4) oraz CC-permissive prowadzi do potencjalnego niedoreprezentowania źródeł komercyjnych z paywall (m.in. Farmakopea Polska, Czasopismo Aptekarskie, Medycyna Praktyczna). Treści specjalistyczne dostępne tylko płatnie (np. monografie producentów hostowane na prywatnych stronach producentów) są poza korpusem. *Wpływ na wyniki:* potencjalne pod-pokrycie najnowszych monografii prywatnych ChPL niektórych producentów oraz literatury edukacyjnej z wydawnictw subskrypcyjnych. *Mitigation:* dla najpopularniejszych leków jest wysokie prawdopodobieństwo, że ChPL w URPL jest aktualna (URPL aktualizuje codziennie); dla rzadkich leków paywall'owany content może być realnym brakiem.

2. **ATC bias (N05/N06 over-representation).** Próbkowanie stratyfikowane nadreprezentuje N05 (*Psycholeptica*) i N06 (*Psychoanaleptica*) trzykrotnie względem naturalnej dystrybucji URPL (30% próby vs ~10% naturalnej populacji). Decyzja świadoma (DEC-001, sekcja 3.5.4). *Wpływ na wyniki:* reranker dotrenowany na takim korpusie może wykazywać lepsze wyniki na zapytaniach psychiatrycznych niż na zapytaniach kardiologicznych lub dermatologicznych. Jest to **akceptowalne** w kontekście pracy — *eval set* gold standard jest również skoncentrowany na podgrupie psych (200 par ATC N05/N06), więc metryka *manual validation* jest *fair* w obrębie tego subzakresu. Ekstrapolacja na całą farmakologię wymagałaby drugiej rundy *eval set* z udziałem zewnętrznego eksperta farmaceutycznego — wskazana jako future work.

3. **Recency bias.** Strata 5 (open-access journals) ma archiwa w większości obejmujące ostatnie 10–12 lat (limit pokrycia OA archive). Treści sprzed 2015 r. są pod-reprezentowane w stratach naukowych. *Wpływ na wyniki:* reranker może być mniej skuteczny dla zapytań dotyczących leków rejestrowanych przed 2010 r. Ten bias jest **częściowo kompensowany** przez Strata 1 (ChPL z URPL), która zawiera wszystkie aktywne rejestracje niezależnie od ich daty pierwszej rejestracji — produkty zarejestrowane w latach 90. są w korpusie, jeśli pozostają aktywne. Niedostatek dotyczy więc głównie literatury naukowej *historycznej*, nie samych leków.

4. **Polish-only bias.** Eksplicytnie wyłączono źródła anglojęzyczne (m.in. Acta Poloniae Pharmaceutica od 1974 r.). Decyzja świadoma — praca dotyczy rerankera dla języka polskiego. *Wpływ na wyniki:* lessons learned mogą nie generalizować na polskie pipeline'y RAG operujące na hybrydowych korporach PL+EN (powszechne w środowisku akademickim, gdzie część literatury referencyjnej jest wyłącznie anglojęzyczna). Ograniczenie jawnie oznaczone w R8 *limitations* + R8 *future work* jako kandydat do *cross-language register transfer* (zob. konspekt II.13.8).

5. **Source type bias (regulatory dominance).** Strata 1+2+3+4+6 (źródła regulatorowe i urzędowe) stanowią łącznie ~78% korpusu (3 200 z 4 100 dokumentów). Strata 5 (czasopisma naukowe) stanowi ~22%. *Wpływ na wyniki:* reranker pre-eksponowany na strukturalne treści regulacyjne (ChPL, programy B.xx, zarządzenia NFZ); może być mniej skuteczny dla zapytań o najnowszą literaturę kliniczną (state-of-the-art research). Trade-off świadomy: strukturalne dane regulatorowe mają znacznie wyższą wartość dla *preference learning* dzięki deterministycznym sekcjom (~8 100 natural pairs z samych nagłówków ChPL — niemożliwe do uzyskania z artykułów naukowych bez kosztownej manualnej anotacji).

**Linkowanie do limitations.** Każdy z pięciu biasów jest przeniesiony do R8 § *Limitations* jako osobna pozycja, z propozycją kierunku przyszłej pracy:

- License bias → włączenie strata licencjonowanych pod kontraktem komercyjnym (np. Farmakopea Polska na warunkach edukacyjnych).
- ATC bias → druga runda *eval set* z udziałem eksperta farmaceutycznego pokrywająca pozostałe klasy ATC.
- Recency bias → archiwum długoterminowe dla strata journals (kontakt z PTFarm w celu uzyskania pre-2015 archive).
- Polish-only bias → cross-language register transfer (PL ChPL ↔ EN SPC) jako future work.
- Source type bias → dodatkowa strata *scientific* z preprintami farmaceutycznymi (medRxiv, F1000Research) z filtracją PL-language.

Dodatkowo, świadome ujawnienie biasów *ex ante* przygotowuje *defensive shield* dla obrony pracy: w przypadku, gdy hipoteza retreningowa H1 nie zostanie potwierdzona (reranker nie osiąga założonej poprawy nDCG@10), pozostałe wymiary wkładu pracy (walidowany framework LLM-as-judge, drift detection framework, aligned ChPL↔Ulotka corpus, cross-register methodology) bronią się niezależnie od magnitudy poprawy retrievalu (zob. R8 *negative-result publishability framing*).

---

## Bibliografia (placeholder)

Pełna bibliografia rozdziału 3 zostanie sfinalizowana po przejściu *citation pass* przez `citation-checker`. Poniższa lista zawiera pozycje cytowane explicit w tym rozdziale; pozostałe pozycje (m.in. dla Strata 5 OA journals jako *prior art*) dodawane w trakcie weryfikacji.

[1] Chen J., Xiao S., Zhang P., Luo K., Lian D., Liu Z. (2024). *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*. arXiv:2402.03216. 🟡 *Verify exact venue (preprint vs published) via citation-checker.*

[2] Creative Commons (n.d.). *Creative Commons License Spectrum*. URL: `https://creativecommons.org/licenses/`. 🟡 *Verify access date.*

[3] Ustawa z dnia 4 lutego 1994 r. o prawie autorskim i prawach pokrewnych (Dz. U. 1994 nr 24 poz. 83 z późn. zm.), Art. 4. URL: `https://arslege.pl/wylaczenie-ochrony-prawa-autorskiego/k442/a36714/`. 🟡 *Verify aktualnego tekstu jednolitego przez `citation-checker`.*

[4] WHO Collaborating Centre for Drug Statistics Methodology. *ATC/DDD Index*. URL: `https://www.whocc.no/atc_ddd_index/`. 🟡 *Verify access date oraz current publication year via citation-checker.*

[5] European Medicines Agency. *Quality Review of Documents (QRD) templates and guidance*. URL: `https://www.ema.europa.eu/en/human-regulatory/marketing-authorisation/product-information/product-information-templates-human`. 🟡 *Verify exact title oraz versioning template via citation-checker.*

[6] Karpukhin V., Oğuz B., Min S. i in. (2020). *Dense Passage Retrieval for Open-Domain Question Answering*. EMNLP 2020. 🟡 *Verify pełnej listy autorów via citation-checker.*

[7] Sculley D. i in. (2015). *Hidden Technical Debt in Machine Learning Systems*. NeurIPS 2015. 🟡 *Verify (powtórzony cite z R1).*

[8] Grabowski Ł. (2018). *On Identification of Bilingual Lexical Bundles for Translation Purposes: The Case of an English-Polish Comparable Corpus of Patient Information Leaflets*. In R. Mitkov, J. Monti, G. Corpas Pastor & V. Seretan (Eds.), *Multiword Units in Machine Translation and Translation Technology* (pp. 181–200). Current Issues in Linguistic Theory 341. John Benjamins. DOI: 10.1075/cilt.341.09gra. ✓ verified 2026-05-16 (rok skorygowany 2017→2018, phantom title zastąpiony).

[9] Polskie Towarzystwo Farmaceutyczne. *Farmacja Polska — informacje dla autorów i licencja*. URL: `https://www.ptfarm.pl/en/wydawnictwa/czasopisma/farmacja-polska/`. 🟡 *Verify access date.*

[10] Wydawnictwo Medyk. *Lek w Polsce — informacje wydawnicze*. URL: `https://lekwpolsce.pl/`. 🟡 *Verify access date oraz licencja CC BY-NC-ND 4.0.*

> **Notka metodologiczna do citation pass:** Cytacje [1]–[10] obejmują pozycje powołane w sekcjach 3.1–3.10. Citation pass przez `citation-checker` przed final submission obowiązkowy — promotor v1 dla R1 zwracał uwagę na wagę *citation hygiene* (phantom citations, błędne lata, błędne inicjały). Pozycje [3] (Art. 4 ustawy) oraz [4] (ATC/DDD WHOCC) i [5] (EMA QRD) są kluczowe dla ethics + licensing — szczególnie *high-priority* w citation pass.

---

> **End-of-chapter checklist (writing rules + Task 03 + PRO-D Assignment 5):**
>
> - [x] Sekcja 3.1 explicit deklaruje text + tabular only, pozostałe modalności out-of-scope z uzasadnieniem
> - [x] Sekcja 3.2 *Source selection methodology* explicit (inclusion/exclusion/search/pipeline/composition) — bezpośrednia odpowiedź na promotor v1 feedback 6/10
> - [x] Sekcje 3.3.1–3.3.6 — wszystkie sześć strata opisane (źródło, URL, skala, licencja, scrape)
> - [x] Sekcja 3.4 — paired ChPL↔Ulotka definicja + walidacja integrity
> - [x] Sekcja 3.5 — Algorithm 3.1 stratified sampling + RANDOM_SEED + trade-off
> - [x] Sekcja 3.6 — folder structure + naming + DVC versioning
> - [x] Sekcja 3.7 — codebooks per strata (Tab. 3.4, 3.5, 3.6 + lokalizacja pełnych)
> - [x] Sekcja 3.8 — licensing (Art. 4 + CC), ethics (brak danych osobowych), eval set ethics
> - [x] Sekcja 3.9 — reproducibility (DVC + seed + snapshot date)
> - [x] Sekcja 3.10 — 5 świadomych biases explicit z linkowaniem do R8 limitations
> - [x] Wszystkie tabele numbered + captioned (Tab. 3.1 – 3.7)
> - [x] Algorithm 3.1 numbered + captioned
> - [x] Academic style (3-os/bierna, bez time-proofing zakazanych słów, bez emoji)
> - [x] Spójność terminologii z konspekt v3.1 delta
> - [ ] Citation pass (Art. 4 link, CC licenses references, EMA QRD reference, BGE-M3 paper) — uruchomić po sign-off treści
