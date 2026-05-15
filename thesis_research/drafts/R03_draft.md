# 3. Dane

> **Status drafu:** methodology + structure, liczby empiryczne oznaczone `[TBD post-Iteracja N]` zgodnie z harmonogramem iteracyjnym (konspekt II.16). Source of truth dla treści: `thesis_research/sources_catalog.md`. Decyzje domenowe: DEC-001 (rotacja na farmakologię szeroką), DEC-002 (ChPL↔Ulotka pairing jako RQ5).

## 3.1 Modalności danych w pracy

W pracy wykorzystano dwie modalności danych: **tekstową** oraz **tabularną**. Pierwsza obejmuje dokumenty regulacyjne i naukowe z polskiej farmakologii klinicznej, stanowiące korpus do indeksowania, treningu rerankera oraz ewaluacji retrievalu. Druga obejmuje metadane korpusu (kody ATC, identyfikatory rejestracyjne, daty modyfikacji), metryki ewaluacji eksperymentów (zapisywane w MLflow), logi przebiegów pipeline'u Prefect oraz tabele kontrolne procesu (`sample-list`, `eval-pairs`, `judge-labels`).

Modalności obrazowa, audio i wideo zostały **świadomie wyłączone z zakresu**. Uzasadnienie wynika z natury problemu: ewaluowany jest pipeline retrievalu tekstowego w polskojęzycznym systemie RAG, w którym ranking par *query → passage* operuje na embeddingach tekstu i preferencjach generowanych przez model językowy. Dane wizualne (skany ChPL z PDF-ów scanowanych) są w tym ujęciu traktowane wyłącznie jako wejście do warstwy OCR (Tesseract `pol`), której wyjściem jest tekst — nie są analizowane jako modality samodzielne. Analogicznie audio i wideo nie występują w żadnym z analizowanych źródeł.

Niniejsze rozróżnienie modalności jest podstawą organizacji folderów (sekcja 3.6) i dalszych decyzji metodologicznych (sekcja 3.10 — świadome biases korpusu).

## 3.2 Metodologia doboru źródeł

W tym rozdziale opisano formalną procedurę selekcji źródeł, zgodnie z wymogiem rygorystycznej metodologii doboru materiału. Sources research przeprowadzono w dwóch rundach (R1 + R2) w dniu 2026-05-15, na podstawie wcześniejszej decyzji domenowej DEC-001.

### 3.2.1 Kryteria włączenia

Źródło zostało **włączone do korpusu** wyłącznie gdy spełniało wszystkie pięć kryteriów:

1. **Język:** polski natywny. Tłumaczenia maszynowe oraz źródła wyłącznie anglojęzyczne — wykluczone.
2. **Licencja:** open-access lub *permitted research use*. Akceptowane: licencje Creative Commons (BY, BY-NC, BY-SA, BY-NC-ND), domena publiczna oraz materiały urzędowe (Art. 4 ustawy o prawie autorskim i prawach pokrewnych). Treści zza paywall — wykluczone.
3. **Specjalizacja:** obecność terminologii farmakologicznej (międzynarodowe nazwy DCI, kody ATC, terminologia łacińska, nomenklatura farmakokinetyczna, opisy mechanizmów działania i interakcji). Treści o ogólnym charakterze medycznym (poziom Wikipedii) — wykluczone.
4. **Scrapowalność:** dostępność programatyczna — API, OAI-PMH, przewidywalny wzorzec URL lub strukturalny PDF. Źródła wymagające manualnego pobierania per dokument — wykluczone.
5. **Verifiability:** istnienie zweryfikowane przez co najmniej trzy niezależne zapytania w wyszukiwarce internetowej w trakcie sources research R1+R2 (2026-05-15) z polskojęzycznymi słowami kluczowymi.

### 3.2.2 Kryteria wyłączenia

Źródło zostało **odrzucone z korpusu** jeśli spełniało którekolwiek z poniższych:

1. **Paywall / subskrypcja** (m.in. Farmakopea Polska XII/XIII, Czasopismo Aptekarskie, większość pozycji Medycyna Praktyczna).
2. **Treść dominująco anglojęzyczna** (Acta Poloniae Pharmaceutica — publikuje w języku angielskim od 1974 roku).
3. **Brak treści strukturalnej** (formularze zgłoszeń działań niepożądanych ADR — formularze, nie tekst nadający się do rerankingu).
4. **Zaprzestanie publikacji / brak aktualizacji** (Postępy Farmacji — wydawca potwierdził zaprzestanie publikacji, archiwum minimalne).
5. **Niejednoznaczność licencyjna** w sytuacjach, gdy brak explicit przyzwolenia na wykorzystanie w pracy badawczej.
6. **Wyłącznie dane tabularne** (publiczne API statystyk NFZ — surowe tabele rozliczeniowe bez tekstu nadającego się jako passage dla rerankera).

### 3.2.3 Strategia wyszukiwania

Sources research przeprowadzono w dwóch rundach:

- **Runda 1 — farmakologia szeroka** (~16 kandydatów): URPL, AOTMiT, MZ, czasopisma PTFarm, uczelnie medyczne (UMP, GUMed, WUM, CMUJ), Farmakopea Polska, Aptekarz Polski, Postępy Fitoterapii.
- **Runda 2 — Ulotki + NFZ + adjacencies** (~12 kandydatów): URPL Ulotki dla pacjenta, NFZ zarządzenia Prezesa, NFZ BIP komunikaty, MZ lista leków zagrożonych dostępnością, URPL komunikaty bezpieczeństwa (DHPC), formularze pharmacovigilance.

Każdego kandydata weryfikowano niezależnymi zapytaniami w wyszukiwarce internetowej z polskimi słowami kluczowymi. Polskie zasoby specjalistyczne bywają słabo indeksowane w anglojęzycznych wyszukiwarkach — zastosowano łagodną ewaluację z explicit oznaczeniem kandydatów statusem `UNVERIFIED` w sytuacjach niepewności.

### 3.2.4 Pipeline selekcji

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

Kategoria **weryfikacja-bez-włączenia** (9 źródeł) obejmuje przypadki, w których zasób istnieje i jest legalnie dostępny, ale wnosi do korpusu wartość redundantną (np. dataset 397 na `dane.gov.pl` to mirror RPL XML — wybrano źródło pierwotne URPL, by uniknąć dedup overhead), regionalne (16 oddziałów wojewódzkich NFZ — duplikaty centralnych komunikatów), lub strukturalnie niespójne z resztą korpusu (Czasopismo Aptekarskie — dostęp tylko do fragmentów).

### 3.2.5 Skład finalny korpusu

Tabela 3.1 przedstawia skład finalny korpusu w sześciu strata (rozszerzone w sekcji 3.3).

**Tabela 3.1.** Skład korpusu po selekcji źródeł.

| Strata | Źródło | Target docs | % korpusu | Licencja | Scrape | Pary header→body |
|---|---|---:|---:|---|---|---:|
| 1. Regulatory professional | ChPL (URPL RPL) | 900 | 22% | Art. 4 urzędowe | XML feed + API + PDF | ~8 100 |
| 2. Regulatory consumer | Ulotki (URPL RPL, paired) | 900 | 22% | Art. 4 urzędowe | API leaflet endpoint | ~5 400 |
| 3. HTA + refundation legal | AOTMiT + MZ obwieszczenia + programy B.xx | 700 | 17% | Art. 4 urzędowe | BIP HTML + PDF | ~2 200 |
| 4. Refundation operational | Zarządzenia Prezesa NFZ + BIP komunikaty | 400 | 10% | Art. 4 urzędowe | HTML index + PDF | ~1 500 |
| 5. OA PL journals | Farmacja Polska + Lek w Polsce + AAMS + CIPMS | 900 | 22% | CC BY-NC / NC-ND / SA | OAI-PMH + JATS | ~2 700 |
| 6. Adjacencies | URPL DHPC + MZ lista braków | 300 | 7% | Art. 4 urzędowe | HTML + PDF | ~300 |
| **Razem** |  | **~4 100** | **100%** |  |  | **~20 200** |

> **Placeholder:** wszystkie wartości w kolumnach *Target docs* oraz *Pary header→body* są **wartościami docelowymi** (planowanymi). Wartości faktyczne (post-scrape, po deduplikacji, po filtrowaniu OCR quality) — `[TBD post-Iteracja 1]`, raportowane w R4 EDA.

Dodatkowo:

- **6 źródeł odrzuconych explicit:** Farmakopea Polska, Czasopismo Aptekarskie, Medycyna Praktyczna, Acta Poloniae Pharmaceutica (jako źródło PL training), Postępy Farmacji, API statystyki NFZ.
- **9 źródeł zweryfikowanych, ale nie włączonych:** dataset 397 dane.gov.pl, regionalne komunikaty 16 oddziałów wojewódzkich NFZ, fragmenty Czasopisma Aptekarskiego i inne (pełna lista w `sources_catalog.md`).

## 3.3 Strata korpusu — opis szczegółowy

### 3.3.1 Strata 1: Regulatory professional (ChPL)

Strata pierwsza zawiera **Charakterystyki Produktu Leczniczego (ChPL)** z Rejestru Produktów Leczniczych URPL. ChPL jest dokumentem profesjonalnym dla lekarzy i farmaceutów, o standaryzowanej strukturze dziesięciu sekcji:

1. Nazwa produktu leczniczego
2. Skład jakościowy i ilościowy
3. Postać farmaceutyczna
4.1 Wskazania do stosowania
4.2 Dawkowanie i sposób podawania
4.3 Przeciwwskazania
4.4 Specjalne ostrzeżenia i środki ostrożności
4.5 Interakcje z innymi produktami leczniczymi
4.6 Wpływ na płodność, ciążę i laktację
4.7 Wpływ na zdolność prowadzenia pojazdów
4.8 Działania niepożądane
4.9 Przedawkowanie
5. Właściwości farmakologiczne
6. Dane farmaceutyczne

Struktura ta jest deterministyczna na poziomie wytycznych EMA QRD i URPL, co umożliwia naturalne mapowanie sekcji jako *query* a treści sekcji jako *passage* dla rerankera. Sample target wynosi **900 produktów leczniczych** (próbka stratyfikowana — sekcja 3.5).

Źródło, URL feed (`https://rejestry.ezdrowie.gov.pl/registry/rpl`), API endpoint (`/api/rpl/medicinal-products/{ID}/...`) oraz parametry scrape są opisane w `sources_catalog.md` Strata 1.

### 3.3.2 Strata 2: Regulatory consumer (Ulotki dla pacjenta) — paired z ChPL

Strata druga zawiera **Ulotki dla pacjenta** pochodzące z tego samego rejestru URPL, w pełnej parze z ChPL ze Strata 1 (definicja operacyjna pairing — sekcja 3.4). Ulotka jest dokumentem skierowanym do pacjenta, o strukturze sześciu sekcji zgodnie z wytycznymi QRD:

1. Co to jest lek X i w jakim celu się go stosuje
2. Informacje ważne przed przyjęciem/zastosowaniem leku X
3. Jak przyjmować/stosować lek X
4. Możliwe działania niepożądane
5. Jak przechowywać lek X
6. Zawartość opakowania i inne informacje

Ulotka i ChPL opisują ten sam lek w dwóch rejestrach językowych — profesjonalnym i laypersonowskim — co stanowi materiał dla eksperymentu cross-register retrieval (RQ5, DEC-002). Sample target: **900 par** (dokładnie te same `productID` co w Strata 1).

### 3.3.3 Strata 3: HTA + refundation legal (AOTMiT + MZ)

Strata trzecia łączy dokumenty oceny technologii medycznych oraz akty refundacyjne:

- **AOTMiT** (Agencja Oceny Technologii Medycznych i Taryfikacji) — raporty HTA, rekomendacje Prezesa, taryfikacje. Source URL: `https://bip.aotm.gov.pl/` (CMS aktualny) oraz `https://bipold.aotm.gov.pl/` (archiwum legacy PDF). Struktura raportów obejmuje stałe sekcje: *Problem decyzyjny / Skuteczność kliniczna / Bezpieczeństwo / Analiza ekonomiczna / Wpływ na budżet / Rekomendacje innych agencji*.
- **MZ obwieszczenia oraz programy lekowe B.xx** — listy refundacyjne (co dwa miesiące) oraz ok. 120 aktywnych programów lekowych. Source URL: `https://www.gov.pl/web/zdrowie/obwieszczenia-ministra-zdrowia-lista-lekow-refundowanych` + `https://dziennikmz.mz.gov.pl/`.

Sample target: **~700 dokumentów** (300 AOTMiT + 400 programy/obwieszczenia).

### 3.3.4 Strata 4: Refundation operational (NFZ)

Strata czwarta zawiera operacjonalizację programów lekowych po stronie płatnika:

- **Zarządzenia Prezesa NFZ** — operacjonalizacja programów lekowych, ICD-10, kryteria kwalifikacji, schemat dawkowania, badania monitorujące, katalog ryczałtów. URL: `https://www.nfz.gov.pl/zarzadzenia-prezesa/zarzadzenia-prezesa-nfz/`.
- **BIP NFZ komunikaty centralne** + **komunikaty dla lekarzy**. URL: `https://www.nfz.gov.pl/bip/komunikaty/` + `https://www.nfz.gov.pl/dla-lekarzy/komunikaty/`.

Świadomie pominięto komunikaty 16 regionalnych oddziałów wojewódzkich NFZ ze względu na wysoki poziom redundancji z treściami centrali (zob. sekcja 3.2.4).

Sample target: **~400 dokumentów**.

### 3.3.5 Strata 5: Open-access PL journals

Strata piąta obejmuje cztery polskojęzyczne czasopisma open-access o profilu farmaceutycznym:

| Czasopismo | Licencja | URL źródłowy | Mirror / archiwum |
|---|---|---|---|
| Farmacja Polska (PTFarm) | CC BY-NC 4.0 | `ptfarm.pl/.../farmacja-polska/` | `bibliotekanauki.pl/journals/1109` (OAI-PMH przez ICM UW) |
| Lek w Polsce (Medyk) | CC BY-NC-ND 4.0 | `lekwpolsce.pl/` | Biblioteka Cyfrowa UŁ (dLibra, OAI-PMH) |
| AAMS (Annales Acad. Med. Silesiensis) | CC BY-SA 4.0 | `annales.sum.edu.pl/` | DOAJ ToC |
| CIPMS (UM Lublin) | CC BY-NC-ND | `czasopisma.umlub.pl/curipms` | Sciendo JATS XML |

Sample target: **~900 artykułów** (mix wszystkich czterech tytułów, preferencja dla artykułów typu *review* i *original research*).

### 3.3.6 Strata 6: Adjacencies

Strata szósta uzupełnia korpus dokumentami niskoobjętościowymi o wysokiej wartości informacyjnej:

- **URPL komunikaty bezpieczeństwa (DHPC — Dear Healthcare Professional Communications)**: `https://www.gov.pl/web/urpl/komunikaty-bezpieczenstwa`. Krótkie alerty bezpieczeństwa, skoordynowane z EMA.
- **MZ lista leków zagrożonych brakiem dostępności**: `https://dziennikmz.mz.gov.pl/keywords/55`. Obwieszczenia o niedoborach.

Sample target: **~300 dokumentów**.

## 3.4 Paired ChPL↔Ulotka — definicja operacyjna

Sekcja ta definiuje pojęcie *paired ChPL↔Ulotka* dla potrzeb eksperymentu RQ5 (DEC-002).

### 3.4.1 Co znaczy "paired"

Dwa dokumenty (jeden ChPL, jedna Ulotka) są **paired** wtedy i tylko wtedy, gdy spełnione są wszystkie trzy warunki:

1. **Identyczny `productID` w rejestrze RPL URPL** — jednoznaczny identyfikator decyzji administracyjnej. Oba dokumenty muszą być wyjściem tego samego pozwolenia na obrót.
2. **Synchronizowana `data_modyfikacji`** — wartości pól `data_modyfikacji` ChPL i Ulotki muszą być identyczne lub mieścić się w tolerancji ±1 dzień (zob. walidacja w sekcji 3.4.3).
3. **Zgodny zakres semantyczny** — oba dokumenty muszą opisywać tę samą wersję leku (wskazania, dawkowanie, przeciwwskazania, działania niepożądane), zatwierdzoną w tym samym cyklu rejestracji.

### 3.4.2 Co NIE znaczy "paired"

W szczególności **nie są paired**:

1. Różne wersje czasowe tego samego leku (np. archiwalna ChPL 2020 i aktualna Ulotka 2024) — wymagana jest najnowsza wersja obu dokumentów z tego samego cyklu administracyjnego.
2. Różne formy farmaceutyczne tego samego API (tabletki 50 mg vs roztwór 100 mg/ml mają osobne `productID`).
3. Generic + brand-name dla tej samej DCI — osobne decyzje administracyjne, osobne `productID`.

### 3.4.3 Walidacja integrity

Walidacja par realizowana jest w Iteracji 0a feasibility (konspekt II.16) na próbce 100 leków losowanych z RPL feed. Kryteria akceptacji (z `sources_catalog.md` § Iteracja 0):

1. `productID` resolution działa dla obu endpointów (`/medicinal-products/{ID}/leaflet` oraz parallel ChPL endpoint) — kryterium kompletności technicznej.
2. `data_modyfikacji` zgodna w tolerancji ±1 dzień — kryterium synchronizacji czasowej.
3. **Competence-stratified spot-check** semantycznej zgodności:
   - 10 par z 100 — wszystkie wybrane z psychiatrycznej podgrupy ATC N05/N06, gdzie autorka posiada kompetencję semantyczną pozwalającą zweryfikować zgodność (zgodnie z DEC-001 uzasadnieniem eval set design).
   - Pozostałe 90 par — wyłącznie sygnał proxy (`productID` match + `data_modyfikacji` ±1 dzień) **bez weryfikacji semantycznej**. Ograniczenie to jest jawnie oznaczone w sekcji 3.10 oraz w limitations R8.

**Próg akceptacji:** ≥90% par o pełnym pairing integrity. Spadek poniżej progu uruchamia kill criteria DEC-001.

**Wynik walidacji:** `[TBD post-Iteracja 0a]` — raportowany w `thesis_research/iteration-0-feasibility-report.md` i przeniesiony do Tabeli 3.5.

**Tabela 3.5.** Wyniki feasibility pre-conditions Iteracji 0a (warunki konieczne dla wejścia w Iterację 1).

| # | Pre-condition | Próg akceptacji | Metryka | Wynik | Status |
|---|---|---|---|---|---|
| 1 | URPL RPL XML uptime | ≥99% w oknie 24h | probe co 1h, `status_code == 200` | `[TBD post-Iteracja 0a]`% | `[TBD]` |
| 2 | URPL XML feed parse-ability | 100% valid XML | `xml.etree.parse()` bez exceptions | `[TBD]`% | `[TBD]` |
| 3 | ChPL endpoint response time | p95 < 2s | wall-clock difference per request | `[TBD]` s | `[TBD]` |
| 4 | Ulotka endpoint response time | p95 < 2s | wall-clock difference per request | `[TBD]` s | `[TBD]` |
| 5 | ChPL↔Ulotka alignment rate | ≥90% par | both endpoints valid + `data_modyfikacji` ±1 day | `[TBD]`% | `[TBD]` |
| 6 | OCR overhead | <15% korpusu | text-layer detection `pdfplumber.extract_text()` non-empty | `[TBD]`% | `[TBD]` |

**Figura 3.2.** Diagram struktury *paired* ChPL↔Ulotka — wspólny `productID` jako klucz alignment, dwie ścieżki dokumentów regulacyjnych (professional vs lay register), wspólne pola metadata, rozdzielne treści tekstowe per rejestr. *(Diagram do narysowania — może być wyrenderowany z definitive specification bez czekania na liczby Iteracji.)*

## 3.5 Stratified sampling algorithm

### 3.5.1 Cel i strategia

Próbkowanie 900 leków z populacji ChPL URPL (~10 000-14 000 unikalnych produktów) musi zrównoważyć dwa cele:

- **(a)** Over-representację psychiatrycznej podgrupy ATC N05 (Psycholeptica) i N06 (Psychoanaleptica) — aby umożliwić leverage manualnej walidacji eval setu przez autorkę (DEC-001 § Uzasadnienie pkt 1).
- **(b)** Szerokość pokrycia farmakologicznego — aby trening rerankera nie był zawężony do jednej klasy ATC.

Strategia: **30% próby z N05/N06** (vs naturalny udział ~10% w URPL) + **70% równowagi przez 14 klas ATC Level 1** (`A` Alimentary, `B` Blood, `C` Cardiovascular, `D` Dermatologicals, `G` Genito-urinary, `H` Hormonal, `J` Anti-infectives, `L` Antineoplastic, `M` Musculo-skeletal, `N` Nervous system, `P` Antiparasitic, `R` Respiratory, `S` Sensory organs, `V` Various) z równym udziałem per klasa.

### 3.5.2 Pseudokod algorytmu

**Algorytm 3.1.** Stratified sampling 900 leków z populacji URPL (`main_project/src/ingest/sampling.py`).

```python
import random

RANDOM_SEED = 42                # zafiksowany w configs/sampling.yaml
TARGET_TOTAL = 900
PSYCH_OVERREP_PROP = 0.30       # 30% z N05+N06

def stratified_sample(all_drugs):
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

    # Fill remainder gdy niektóre klasy ATC < per_class
    remaining = TARGET_TOTAL - len(psych_sample) - len(other_sample)
    if remaining > 0:
        picked = {d.product_id for d in psych_sample + other_sample}
        extra_pool = [d for d in other_pool if d.product_id not in picked]
        other_sample.extend(random.sample(extra_pool, min(remaining, len(extra_pool))))

    return psych_sample + other_sample
```

### 3.5.3 Gwarancje reprodukowalności

1. **Random seed:** wartość `42` zafiksowana w `main_project/configs/sampling.yaml`. Recenzent uruchamiający algorytm na tej samej migawce RPL XML uzyska identyczny zestaw 900 `productID`.
2. **Snapshot listy próby:** zapisywany w `data/raw/sample-list-YYYY-MM-DD.csv` i wersjonowany przez DVC (sekcja 3.6 + 3.9).
3. **Reproducja:** możliwa przez `dvc pull data/raw/sample-list-<date>.csv` lub re-run algorytmu na zafiksowanym snapshotcie RPL.

**Faktyczna kompozycja próby (post-sampling):** `[TBD post-Iteracja 1]` — raportowana w R4 EDA Figura 4.X (rozkład ATC Level 1 + Level 4 N05/N06 w spróbkowanym korpusie).

**Figura 3.1.** Rozkład klas ATC w spróbkowanym korpusie — bar chart 14 klas Level 1 + insert dla N05/N06 Level 4. *(Placeholder — do wyrenderowania `[TBD post-Iteracja 1]` z faktycznej listy próby.)*

### 3.5.4 Trade-off: equal-weight vs natural distribution

Wybrano strategię **equal-weight** w obrębie 14 klas ATC Level 1 zamiast próbkowania zachowującego naturalną dystrybucję URPL. Uzasadnienie:

- **Cel pracy:** test rerankera na **zróżnicowanych domenach farmaceutycznych** (Cardio vs Anti-infectives vs Dermatologicals vs ...), a nie symulacja realnej dystrybucji apteki.
- **Alternatywa odrzucona:** próbkowanie zgodne z naturalną dystrybucją URPL nadreprezentowałoby leki Cardiovascular (`C`), pod-reprezentowałoby klasy rzadkie (`P` Antiparasitic, `V` Various) — kosztem diversity training signal.

Wybór ten jest świadomą decyzją metodologiczną i ma konsekwencję w postaci biasu ATC (sekcja 3.10 pkt 2).

## 3.6 Struktura folderów + naming + versioning

Struktura katalogowa repozytorium dla danych:

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
│   │   └── sample-list-YYYY-MM-DD.csv      # snapshot listy próby
│   ├── processed/
│   │   ├── chunks/              # po chunkowaniu section-aware
│   │   ├── embeddings/          # BGE-M3 768-dim per chunk
│   │   ├── eval_pairs/          # 200 par gold standard + 1800 cross-register
│   │   └── preference_dataset/  # ~145k preference quadruplets
│   └── docs/
│       ├── codebook_chpl.md
│       ├── codebook_ulotki.md
│       ├── codebook_aotmit.md
│       ├── codebook_nfz.md
│       ├── codebook_journals.md
│       └── codebook_adjacencies.md
└── configs/
    └── sampling.yaml             # RANDOM_SEED = 42, TARGET_TOTAL = 900
```

**Konwencje nazewnictwa:**

- Pliki raw: `<strata>_<productID lub doc_id>_<YYYYMMDD>.<ext>` (np. `chpl_39257_20250612.pdf`).
- Chunks: `<strata>_<productID>_<section_id>_chunk_<NNN>.json`.
- Eval pairs: `eval_<set>_<NNN>.json` (sets: `gold_psych_200`, `cross_register_1800`).
- Snapshoty: `<artifact>-YYYY-MM-DD.<ext>`.

**Versioning:**

- `data/raw/` — read-only po snapshocie. Każda modyfikacja wymaga nowego snapshot date.
- DVC (Data Version Control) jako warstwa wersjonowania binarnych artefaktów (PDF, embeddings) z backendem MinIO.
- Każdy commit kodu, który zmienia processing pipeline, kojarzony z konkretnym snapshot date przez `dvc.lock` w katalogu głównym repozytorium.
- `git` śledzi kod, configs, codebooks oraz `.dvc` pliki wskazujące na artefakty.

## 3.7 Codebooks (data dictionaries)

Dla każdej Strata przygotowano codebook (data dictionary) w formacie markdown, przechowywany w `data/docs/codebook_<strata>.md`. Codebook zawiera definicje wszystkich pól metadata oraz pól ekstrahowanych z dokumentów. Poniżej przedstawiono wycinki dla dwóch kluczowych Strata; pełne codebooks znajdują się w appendiksie A.

### 3.7.1 Codebook ChPL (wycinek)

**Tabela 3.2.** Wycinek codebook'a Strata 1 (ChPL).

| Pole | Typ | Znaczenie | Wartości / format | Pochodzenie |
|---|---|---|---|---|
| `product_id` | int | Identyfikator decyzji administracyjnej URPL | unique, np. `39257` | RPL XML feed |
| `atc_code` | string | Klasyfikacja ATC | format `[A-V][0-9]{2}[A-Z][A-Z][0-9]{2}`, np. `N06AB06` | RPL XML feed (jeśli obecne) |
| `data_modyfikacji` | date | Data ostatniej modyfikacji rejestru | ISO 8601 (`YYYY-MM-DD`) | RPL XML feed |
| `section_id` | string | Identyfikator sekcji ChPL | enum `{1, 2, 3, 4.1, 4.2, ..., 4.9, 5, 6}` | parsing PDF |
| `section_header` | string | Nagłówek sekcji | tekst PL | parsing PDF |
| `body_text` | string | Treść sekcji | tekst PL, normalizacja NFC | parsing PDF + OCR fallback |
| `register` | categorical | Rejestr językowy | enum `{professional}` | const |
| `text_source_method` | categorical | Metoda ekstrakcji tekstu | enum `{text-layer, ocr_tesseract_pol}` | parsing PDF |
| `ocr_confidence` | float | Confidence OCR (null gdy text-layer) | [0.0, 1.0] | Tesseract output |
| `scrape_date` | date | Data pobrania ze źródła | ISO 8601 | scrape script |
| `license` | string | Status licencyjny | const `Art. 4 ustawy o prawie autorskim` | const |

Pełna lista pól: `data/docs/codebook_chpl.md` (`[TBD post-Iteracja 1]` w zakresie liczebności faktycznej oraz weryfikacji obecności pola `atc_code` w XML — niektóre rekordy mogą wymagać enrichment z zewnętrznego źródła ATC WHOCC).

### 3.7.2 Codebook Ulotki (wycinek)

**Tabela 3.3.** Wycinek codebook'a Strata 2 (Ulotki dla pacjenta).

| Pole | Typ | Znaczenie | Wartości / format | Pochodzenie |
|---|---|---|---|---|
| `product_id` | int | Identyfikator decyzji administracyjnej URPL (paired z ChPL) | unique, paired key | RPL XML feed |
| `paired_chpl_id` | int | FK do `chpl.product_id` | musi mieć match w Strata 1 | derived |
| `section_id` | string | Identyfikator sekcji Ulotki | enum `{1, 2, 3, 4, 5, 6}` | parsing PDF |
| `section_header` | string | Nagłówek sekcji (QRD) | tekst PL | parsing PDF |
| `body_text` | string | Treść sekcji | tekst PL, normalizacja NFC | parsing PDF |
| `register` | categorical | Rejestr językowy | const `lay` | const |
| `data_modyfikacji` | date | Data modyfikacji (powinna być zgodna z paired ChPL ±1 day) | ISO 8601 | RPL XML feed |
| `pairing_status` | categorical | Wynik walidacji pairing | enum `{ok, date_drift, missing_chpl}` | derived (Iteracja 0a) |
| `scrape_date` | date | Data pobrania | ISO 8601 | scrape script |
| `license` | string | Status licencyjny | const `Art. 4 ustawy o prawie autorskim` | const |

### 3.7.3 Pozostałe codebooks

Lokalizacja pełnych codebooks pozostałych Strata:

| Strata | Plik codebook | Specyficzne pola |
|---|---|---|
| 3a AOTMiT | `data/docs/codebook_aotmit.md` | `report_type`, `decision_class`, `indication`, `recommendation` |
| 3b MZ | `data/docs/codebook_mz.md` | `obwieszczenie_id`, `program_id` (B.01–B.XX), `effective_date` |
| 4 NFZ | `data/docs/codebook_nfz.md` | `zarzadzenie_id`, `program_id`, `category` |
| 5 OA Journals | `data/docs/codebook_journals.md` | `journal`, `issue`, `year`, `doi`, `license_per_article` |
| 6 Adjacencies | `data/docs/codebook_adjacencies.md` | `alert_id`, `alert_type` (DHPC vs shortage) |

Pełne wartości i przedziały `[TBD post-Iteracja 1]` — finalizowane wraz z scrape pipeline.

## 3.8 Aspekty etyczne i licencyjne

### 3.8.1 Status urzędowy źródeł regulatorowych

Wszystkie cztery Strata regulatorowe (1 ChPL, 2 Ulotki, 3 AOTMiT/MZ, 4 NFZ) oraz Strata 6 (URPL DHPC, MZ braki) korzystają z **wyłączenia spod ochrony prawa autorskiego** na mocy Art. 4 ustawy z dnia 4 lutego 1994 r. o prawie autorskim i prawach pokrewnych. Artykuł 4 stanowi, że *„nie stanowią przedmiotu prawa autorskiego: akty normatywne lub ich urzędowe projekty; urzędowe dokumenty, materiały, znaki i symbole; opublikowane opisy patentowe lub ochronne; proste informacje prasowe"*.

ChPL, Ulotki dla pacjenta, raporty AOTMiT, obwieszczenia MZ oraz zarządzenia Prezesa NFZ kwalifikują się jako *urzędowe dokumenty i materiały* w rozumieniu Art. 4 pkt 2 i są **zwolnione z ochrony prawnoautorskiej**. Wykorzystanie ich w pracy badawczej oraz dystrybucja w ramach reprodukowalnego korpusu pracy badawczej są dozwolone bez konieczności uzyskiwania zgody MAH lub organów wystawiających.

### 3.8.2 Licencje CC OA czasopism (Strata 5)

**Tabela 3.4.** Audyt licencji per Strata.

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

**Konsekwencje licencji CC BY-NC-ND** (Lek w Polsce, CIPMS) — *no derivatives*: w pipeline'ie chunking dzieli artykuły na fragmenty, co technicznie może być interpretowane jako utwór pochodny. Mitigation: chunki przechowywane wewnętrznie do treningu rerankera, **bez redistribution chunked content**; redystrybucja korpusu po opublikowaniu pracy ograniczona do metadanych + linków do oryginałów dla tych dwóch źródeł.

### 3.8.3 Brak danych osobowych — uzasadnienie braku komitetu etycznego

Korpus pracy zawiera **wyłącznie dokumenty regulacyjne, akty prawne i artykuły naukowe** publicznie udostępnione. Nie zawiera:

- Danych pacjentów (rekordów medycznych, wyników badań klinicznych z identyfikatorami).
- Danych personalnych autorów ulotek lub MAH (treści są opracowywane korporacyjnie).
- Treści generowanych przez użytkowników (forum / komentarze / social media).

W konsekwencji praca **nie wymaga zgody komisji bioetycznej** ani zgodności z RODO w zakresie danych osobowych (brak danych osobowych w korpusie).

### 3.8.4 Eval set: 200 par psych subset — etyka wyboru

Manualnie zwalidowany eval set (200 par gold standard) jest próbkowany z psychiatrycznej podgrupy korpusu (ATC N05 + N06). Wybór ten jest **świadomą decyzją architektoniczną**, uzasadnioną w DEC-001 pkt 1:

> Leverage manualnej walidacji kompetencji autorki w psychiatrycznej podgrupie ATC pozwala na rygorystyczną walidację LLM-as-judge agreement (RQ2/H2) bez konieczności angażowania zewnętrznych ekspertów farmaceutycznych. Trening pozostaje na szerokim korpusie farmakologii; eval set wąski w podgrupie, którą autorka faktycznie zna.

Wybór wąskiego eval setu nie wprowadza problemu etycznego — decyzja jest jawna w R3, R5 oraz w limitations R8, zgodnie z zasadą *transparent disclosure of design choices*.

## 3.9 Reproducibility statement

Pełna reprodukowalność korpusu zapewniona jest przez czterowarstwową strukturę:

1. **Kod scrape:** `main_project/src/ingest/` zawiera skrypty per Strata (`ingest_chpl.py`, `ingest_ulotki.py`, `ingest_aotmit.py`, `ingest_mz.py`, `ingest_nfz.py`, `ingest_journals.py`, `ingest_adjacencies.py`). Każdy skrypt ma idempotentne semantyki — wielokrotne uruchomienie na tym samym snapshot date daje identyczny output.
2. **Snapshot date:** każda pełna scrape produkcyjna jest oznaczona datą snapshot (`YYYY-MM-DD`) i traktowana jako immutable. Modyfikacje korpusu (np. dodanie nowych źródeł, re-scrape) tworzą nowy snapshot date.
3. **DVC tracking:** binarne artefakty (PDF, embeddings, eval pairs) tracked przez DVC z backendem MinIO. Plik `dvc.lock` w katalogu głównym repozytorium fixuje hash'e wszystkich artefaktów.
4. **Configs versioning:** plik `main_project/configs/sampling.yaml` zawiera `RANDOM_SEED = 42` i jest częścią repozytorium git. Recenzent uruchamiający algorytm próbkowania na tej samej migawce RPL XML otrzyma identyczny zestaw 900 `productID`.

**Reproducja snapshot z external machine:**

```bash
git clone <repo_url>
cd main_project
uv sync                                              # ustawienie środowiska
uv run python -m ingest.snapshot --date 2026-05-21   # reproducja snapshot
dvc pull data/raw/corpus-2026-05-21.tar.zst          # pobranie binariów
```

Faktyczna data snapshot użytego w eksperymentach: `[TBD post-Iteracja 1]`.

## 3.10 Świadome biases korpusu

Sekcja ta jawnie nazywa pięć typów biasów obecnych w korpusie, aby umożliwić właściwą interpretację wyników w R7 oraz uzasadnić ograniczenia w R8.

1. **License bias.** Preferencja dla źródeł urzędowych (Art. 4) oraz CC-permissive. Konsekwencja: pod-reprezentacja źródeł komercyjnych z paywall (m.in. Farmakopea Polska, Czasopismo Aptekarskie, Medycyna Praktyczna). Treści specjalistyczne tylko płatne (np. monografie producentów hostowane na prywatnych stronach) są poza korpusem. *Wpływ na wyniki:* potencjalne pod-pokrycie najnowszych monografii prywatnych ChPL niektórych producentów.

2. **ATC bias (N05/N06 over-representation).** Próbkowanie stratyfikowane nadreprezentuje N05 (Psycholeptica) i N06 (Psychoanaleptica) trzykrotnie względem naturalnej dystrybucji URPL (30% vs ~10%). Decyzja świadoma (DEC-001, sekcja 3.5.4). *Wpływ na wyniki:* reranker dotrenowany na takim korpusie może wykazywać lepsze wyniki na zapytaniach psychiatrycznych niż na zapytaniach kardiologicznych lub dermatologicznych. Jest to **akceptowalne** — eval set jest również skoncentrowany na podgrupie psych (200 par gold standard ATC N05/N06), więc metryka manual validation jest *fair* w obrębie tego subzakresu.

3. **Recency bias.** Strata 5 (OA journals) ma archiwa w większości obejmujące ostatnie 10-12 lat (limit pokrycia OA). Treści sprzed 2015 roku są pod-reprezentowane. *Wpływ na wyniki:* reranker może być mniej skuteczny dla zapytań dotyczących leków rejestrowanych przed 2010 r. — jednak Strata 1 ChPL (URPL) zawiera wszystkie aktywne rejestracje niezależnie od ich daty pierwszej rejestracji, co częściowo kompensuje ten bias.

4. **Polish-only bias.** Eksplicytnie wyłączono źródła anglojęzyczne (m.in. Acta Poloniae Pharmaceutica od 1974 r.). Decyzja świadoma — praca dotyczy rerankera dla języka polskiego. *Wpływ na wyniki:* lessons learned mogą nie generalizować na polskie pipeline'y RAG operujące na hybrydowych PL+EN corporach. Ograniczenie jawnie oznaczone w R8 limitations + R8 future work jako kandydat do cross-language register transfer (II.13.8 konspektu).

5. **Source type bias (regulatory dominance).** Strata 1+2+3+4+6 (źródła regulatorowe i urzędowe) stanowią łącznie ~78% korpusu (3 200 z 4 100 dokumentów). Strata 5 (czasopisma naukowe) stanowi ~22%. *Wpływ na wyniki:* reranker pre-eksponowany na strukturalne treści regulacyjne (ChPL, programy B.xx, zarządzenia NFZ); reranker może być mniej skuteczny dla zapytań o najnowszą literaturę kliniczną (state-of-the-art). Trade-off świadomy: strukturalne dane regulatorowe mają znacznie wyższą wartość dla preference learning dzięki deterministycznym sekcjom (~8 100 natural pairs z samych nagłówków ChPL).

**Linkowanie do limitations:** każdy z pięciu biasów jest przeniesiony do R8 § Limitations jako osobna pozycja, z propozycją kierunku przyszłej pracy (Strata licensowane / domena pełna ATC bez over-rep / archiwum długoterminowe / cross-language / dodatkowe Strata scientific).

---

> **End-of-chapter checklist (writing rules + Task 03 + PRO-D Assignment 5):**
>
> - [x] Sekcja 3.1 explicit deklaruje text + tabular only, pozostałe modalności out-of-scope z uzasadnieniem
> - [x] Sekcja 3.2 Source selection methodology explicit (inclusion/exclusion/search/pipeline/composition) — bezpośrednia odpowiedź na promotor v1 feedback 6/10
> - [x] Sekcje 3.3.1–3.3.6 — wszystkie sześć Strata opisane (źródło, URL, skala, licencja, scrape)
> - [x] Sekcja 3.4 — paired ChPL↔Ulotka definicja + walidacja integrity
> - [x] Sekcja 3.5 — Algorithm 3.1 stratified sampling + RANDOM_SEED + trade-off
> - [x] Sekcja 3.6 — folder structure + naming + DVC versioning
> - [x] Sekcja 3.7 — codebooks per Strata (Tab. 3.2, 3.3 + lokalizacja pełnych)
> - [x] Sekcja 3.8 — licensing (Art. 4 + CC), ethics (brak danych osobowych), eval set ethics
> - [x] Sekcja 3.9 — reproducibility (DVC + seed + snapshot date)
> - [x] Sekcja 3.10 — 5 świadomych biases explicit z linkowaniem do R8 limitations
> - [x] Wszystkie tabele numbered + captioned (Tab. 3.1 – 3.5)
> - [x] Wszystkie figury numbered + captioned (Fig. 3.1, 3.2) + Algorithm 3.1
> - [x] Academic style (3-os/bierna, bez time-proofing zakazanych słów, bez emoji)
> - [x] Spójność terminologii z konspekt v3.1 delta
> - [ ] Citation pass (Art. 4 link, CC licenses references, EMA QRD reference) — uruchomić po sign-off treści
