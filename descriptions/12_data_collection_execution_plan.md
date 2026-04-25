# Plan podejścia — zbieranie danych PDF/DOCX/HTML dla projektu JDG Chatbot

> Dokument roboczy: praktyczny plan realizacji `discover → fetch → save raw + metadata`, oparty o `descriptions/data_collection_spec.md`, ale rozszerzony o priorytetyzację, kontrolę jakości i zarządzanie ryzykiem.

---

## 1) Cel operacyjny (co dowozimy)

W pierwszym przebiegu zbierania danych celem nie jest „wszystko naraz”, tylko **stabilny, audytowalny baseline**:

1. minimum **60 dokumentów** (przekroczenie minimum 50),
2. pełne pokrycie warstwy **L1 (legislacja MUST)**,
3. co najmniej **1 dokument na każdy z 51 tematów** (na start: mapowanie temat→źródło),
4. komplet metadanych pobrania dla każdego pliku,
5. gotowość do kolejnych iteracji (L2/L3) bez przebudowy struktury projektu.

---

## 2) Zakres i zasada priorytetów

### P0 — obowiązkowe (Sprint 1)
- 8 aktów prawnych MUST (ELI/EUR-Lex) w PDF.
- Manifest i metadane dla każdego pliku.
- Matryca pokrycia 51 tematów (nawet jeśli część tematów chwilowo pokryta 1 dokumentem).

### P1 — bardzo zalecane (Sprint 2)
- Rozporządzenia wykonawcze (KPiR, ewidencja ryczałtu, JPK, faktury, ZUS zgłoszenia).
- Broszury PDF z podatki.gov.pl.
- Poradniki PDF z ZUS/PIP/UODO.

### P2 — rozszerzenia jakościowe (Sprint 3)
- Wzory DOCX z biznes.gov.pl.
- Tabele stawek i kalendarze terminów.
- Selektywne interpretacje KIS (tylko dobrze opisane i aktualne).

---

## 3) Struktura katalogów (docelowa)

```text
project-root/
  data/
    raw/
      legislation/
      government_portals/
      templates_docx/
      tables_calendars/
    manifests/
      dataset_manifest.csv
      coverage_51_topics.csv
    logs/
      fetch_log.ndjson
      rejected_files.ndjson
```

### Konwencja nazw plików
- PDF ustaw: `eli_<publisher>_<year>_<position>.pdf` lub `celex_<id>.pdf`
- DOCX wzory: `bizgov_<slug>_<yyyy-mm-dd>.docx`
- Artykuły HTML: `portal_<domain>_<slug>_<yyyy-mm-dd>.html`

---

## 4) Model metadanych (minimalny, wymagany)

Każdy plik musi mieć rekord w `dataset_manifest.csv` i JSON sidecar.

### Kolumny manifestu CSV
- `doc_id`
- `topic_ids` (lista, np. `vat_rejestracja;vat_zwolnienie_200k`)
- `layer` (`L1|L2|L3`)
- `source_domain`
- `source_title`
- `source_url`
- `retrieved_at_utc`
- `http_status`
- `content_type`
- `file_ext`
- `language`
- `jurisdiction`
- `sha256`
- `file_size_bytes`
- `local_path`
- `license_or_terms`
- `quality_flag` (`accepted|rejected|needs_review`)
- `notes`

### Sidecar JSON (`*.json`)
- surowe nagłówki HTTP,
- informacje o retry,
- detekcja typu pliku (magic bytes),
- powód odrzucenia (jeśli odrzucony).

---

## 5) Plan wykonania krok po kroku

## Krok A — przygotowanie mapy tematów (51)
1. Zbudować `coverage_51_topics.csv` z listą tematów z `data_collection_spec.md`.
2. Dla każdego tematu przypisać:
   - 1 źródło L1 (ustawa/rozporządzenie),
   - 1 źródło L2 (poradnik/portal) — jeśli dostępne.
3. Oznaczyć luki jako `gap`.

**Efekt:** od początku widać, czego realnie brakuje.

## Krok B — zbiór L1 (najwyższy priorytet)
1. Pobranie 8 aktów MUST przez ELI/EUR-Lex jako PDF.
2. Walidacja `%PDF` i kontrola anty-patternu `Request Rejected`.
3. Retry z backoff (1s/4s/16s).
4. Zapis plik + sidecar + wpis w manifeście.

**Exit criteria:** 8/8 aktów poprawnych i audytowalnych.

## Krok C — L1 rozszerzone (rozporządzenia)
1. Odkrywanie aktów wykonawczych przez endpoint referencji ELI.
2. Filtrowanie po tematach 51 (unikamy śmieci).
3. Pobranie i deduplikacja po `sha256`.

**Exit criteria:** min. 10 rozporządzeń przydatnych dla JDG.

## Krok D — L2 portale rządowe
1. Priorytet źródeł bez ciężkiego WAF: podatki.gov.pl, pip.gov.pl, uodo.gov.pl.
2. Potem ZUS i biznes.gov.pl (bardziej wymagające).
3. Zachowanie PDF, HTML i DOCX bez parsowania treści na tym etapie.

**Exit criteria:** min. 30 dokumentów L2 + przypisanie do tematów.

## Krok E — kontrola jakości i pokrycia
1. Deduplikacja hash + URL canonical.
2. Kontrola aktualności (preferencja publikacji <24 mies. dla poradników).
3. Raport pokrycia 51 tematów: `covered / uncovered / weakly_covered`.

**Exit criteria:** 51 tematów ma co najmniej po 1 źródle.

---

## 6) Reguły akceptacji plików

### Akceptuj
- PDF z poprawnym nagłówkiem `%PDF`.
- DOCX z poprawnym ZIP magic bytes (`PK`).
- HTML z treścią merytoryczną (nie strona blokady/WAF).

### Odrzuć
- Plik blokady (`Request Rejected`, CAPTCHA walls, puste HTML).
- Dublikat o tym samym hashu i gorszych metadanych.
- Treść niepowiązaną z zakresem JDG.

---

## 7) KPI i Definition of Done

### KPI operacyjne
- `>= 60` dokumentów łącznie po Sprint 2.
- `100%` pokrycia 8 aktów MUST.
- `>= 95%` rekordów z pełnym metadanymi (braki tylko uzasadnione).
- `>= 51/51` tematów pokrytych min. 1 dokumentem.

### DoD (pierwsza wersja datasetu)
- manifest CSV gotowy do re-run,
- komplet sidecar JSON,
- log błędów i odrzuceń,
- raport pokrycia tematów,
- zero „martwych” wpisów (manifest wskazuje istniejące pliki).

---

## 8) Ryzyka i mitygacje

1. **WAF / blokady portali**
   - zaczynać od źródeł bez WAF,
   - utrzymywać kolejkę URL do ponowienia,
   - rozdzielić discovery i download (łatwiejszy retry).

2. **Niejednoznaczna aktualność dokumentów**
   - trzymać `retrieved_at_utc` i datę publikacji źródła,
   - oznaczać `needs_review`, gdy data nieczytelna.

3. **Nadmiar dokumentów niskiej jakości**
   - scoring źródła (L1 > L2 > L3),
   - priorytet jakości nad wolumenem.

4. **Brak pokrycia części tematów 51**
   - tygodniowy przegląd luk,
   - osobna lista „targeted fetch” dla niepokrytych tematów.

---

## 9) Harmonogram (propozycja 10 dni roboczych)

- **D1–D2:** przygotowanie struktury, mapy 51 tematów, manifestu.
- **D3–D4:** pełne L1 MUST + walidacja.
- **D5–D6:** rozporządzenia wykonawcze.
- **D7–D8:** L2 (podatki/pip/uodo, potem ZUS/biznes.gov).
- **D9:** deduplikacja, QA, raport pokrycia.
- **D10:** finalny freeze datasetu v1 + checklista DoD.

---

## 10) Co dalej po zebraniu danych (poza obecnym zakresem)

1. Konwersja/parsowanie (PDF/DOCX/HTML -> tekst).
2. Chunking + wzbogacone metadane semantyczne.
3. Indeksacja wektorowa + BM25 hybrid.
4. Testy retrieval i ewaluacja odpowiedzi.

To są kroki następnego etapu; ten plan kończy się na stabilnym, powtarzalnym i audytowalnym pozyskaniu danych.
