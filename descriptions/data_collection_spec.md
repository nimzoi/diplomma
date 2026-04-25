# Specyfikacja zbioru danych — JDG Chatbot Knowledge Base

> **Dokument operacyjny dla wykonawcy (człowiek lub agent LLM).**
> Cel: zebrać minimalny, ale kompletny zbiór dokumentów źródłowych potrzebny do zbudowania bazy wiedzy chatbota dla jednoosobowej działalności gospodarczej (JDG) w Polsce, w architekturze Cache-Augmented RAG.
>
> Zakres odpowiedzialności wykonawcy: **discover → fetch → save raw + metadata**. Parsowanie, chunking, embeddingi, ingest do vector store są **poza scope** tego dokumentu.

---

## 1. Kontekst pracy

| Pole | Wartość |
|---|---|
| Tytuł pracy | Projekt i ewaluacja spersonalizowanego chatbota wiedzy dla JDG opartego na architekturze Cache-Augmented RAG |
| Stopień / uczelnia | Praca inżynierska, PJATK |
| Domena | Polskie prawo gospodarcze, podatkowe, ubezpieczeniowe i pracy — w aspekcie JDG |
| Architektura systemu docelowego | Cache-Augmented RAG (Lewis 2020 + Chan 2024) z personalizacją przez polskie rejestry publiczne (CEIDG/REGON/VAT/KRS) |
| Tryby działania chatbota | (a) ogólny RAG po pytaniu; (b) personalizowany po podaniu NIP-u; (c) cache-first dla powtarzalnych pytań |
| Persona docelowa | Osoba fizyczna prowadząca lub zakładająca JDG; zadaje pytania w języku naturalnym; nie czyta ustaw |
| Język bazy wiedzy | **Polski** (wyjątek: RODO — wersja PL z EUR-Lex) |
| Kraj jurysdykcji | Polska, prawo stanu na 2025–2026 |

---

## 2. Cele zbioru danych

| Cel | Mierzalny rezultat |
|---|---|
| Pokrycie tematyczne | 51 tematów katalogowych zgrupowanych w 6 obszarach (sekcja 4) — każdy temat musi mieć ≥1 dokument źródłowy |
| Wielkość minimalna | **≥ 50 dokumentów** (60–80 zalecane) |
| Wielkość docelowa (pełny RAG) | 200–400 dokumentów po dedup; ≥ 1 mln tokenów po parsowaniu |
| Aktualność | Tekst prawny: jednolite wersje obowiązujące na dzień zbiorowania; poradniki: najnowsze publikacje z portali rządowych (preferencja < 24 mies.) |
| Audytowalność | Każdy plik ma zachowane: oryginalny URL, timestamp pobrania, HTTP status, content-type, hash treści |
| Reprodukowalność | Manifest (CSV) wystarcza, by powtórzyć pobranie 1:1 |

---

## 3. Hierarchia jakości źródeł (3 warstwy)

System przyjmuje hierarchię ważności źródeł. Wykonawca powinien wypełnić warstwy **w kolejności** — Warstwa 1 jest obowiązkowa, Warstwa 2 zalecana, Warstwa 3 opcjonalna.

| Warstwa | Klasa źródła | Autorytet | Priorytet |
|---|---|---|---|
| **L1** | Akty prawne (ustawy, rozporządzenia obowiązujące) | Najwyższy — jedyne źródło wiążące | **MUST** |
| **L2** | Portale rządowe — poradniki interpretujące prawo | Wysoki — oficjalna interpretacja administracji | **SHOULD** |
| **L3** | Interpretacje indywidualne KIS, wzory dokumentów, tabele stawek, kalendarze | Średni — kontekst praktyczny | **MAY** |

**Konflikt rozstrzygany na rzecz wyższej warstwy.** Jeśli poradnik biznes.gov.pl mówi co innego niż ustawa — chatbot musi cytować ustawę. Dlatego L1 musi być pełna i poprawna.

---

## 4. Zakres tematyczny (51 tematów w 6 grupach)

Każdy temat = pytanie, które użytkownik może realnie zadać chatbotowi. Temat = ID + opis + przykładowe keywordy.

### 4.1 Grupa **ZUS** (10 tematów)

| ID | Temat | Keywordy do wyszukiwania |
|---|---|---|
| `zus_ulga_na_start` | Ulga na start (6 mies. bez ZUS społecznego) | "ulga na start", "art. 18 prawo przedsiębiorców" |
| `zus_preferencyjny` | ZUS preferencyjny (24 mies. niższe składki) | "preferencyjny ZUS", "obniżone składki nowy przedsiębiorca" |
| `zus_maly_zus_plus` | Mały ZUS Plus (proporcjonalny do dochodu) | "Mały ZUS Plus", "MZP", "ustawa o systemie ubezpieczeń społecznych art. 18c" |
| `zus_wakacje_skladkowe` | Wakacje składkowe (1 mies./rok od 2024) | "wakacje składkowe", "RWS" |
| `zus_skladka_zdrowotna_jdg` | Składka zdrowotna JDG (zależna od formy opodatkowania) | "składka zdrowotna ryczałt", "składka zdrowotna skala", "składka zdrowotna liniowy" |
| `zus_zua_zwua_dra` | Zgłoszenia ZUA/ZWUA/DRA | "ZUS ZUA", "ZUS ZWUA", "ZUS DRA", "deklaracja rozliczeniowa" |
| `zus_zasilek_chorobowy_jdg` | Zasiłek chorobowy / dobrowolne ubezp. chorobowe | "ubezpieczenie chorobowe przedsiębiorca", "zasiłek chorobowy JDG" |
| `zus_podstawa_wymiaru` | Podstawa wymiaru składek (60% / 30% / 75%) | "podstawa wymiaru składek ZUS 2026" |
| `zus_zawieszenie_dzialalnosci` | ZUS przy zawieszeniu działalności | "zawieszenie działalności ZUS", "wyrejestrowanie ZUA" |
| `zus_emerytura_jdg` | Emerytura przy JDG, zbieg ubezpieczeń | "emerytura JDG", "zbieg tytułów ubezpieczeń" |

### 4.2 Grupa **PIT i formy opodatkowania** (11 tematów)

| ID | Temat | Keywordy |
|---|---|---|
| `pit_skala` | Skala podatkowa (12% / 32%) | "skala podatkowa JDG", "PIT-36" |
| `pit_liniowy` | Podatek liniowy 19% | "podatek liniowy", "PIT-36L", "art. 30c ustawy PIT" |
| `pit_ryczalt` | Ryczałt od przychodów ewidencjonowanych | "ryczałt od przychodów", "ustawa o ryczałcie", "PIT-28" |
| `pit_stawki_ryczalt_pkd` | Stawki ryczałtu per PKD (2/3/5,5/8,5/10/12/12,5/14/15/17%) | "stawka ryczałtu PKD", "załącznik do ustawy o ryczałcie" |
| `pit_karta_podatkowa` | Karta podatkowa (forma wycofywana) | "karta podatkowa 2026", "PIT-16A" |
| `pit_ip_box` | IP Box 5% (programiści) | "IP Box", "5% kwalifikowane prawo własności intelektualnej" |
| `pit_kup` | KUP — koszty uzyskania przychodu | "koszty uzyskania przychodu JDG", "art. 22 PIT" |
| `pit_amortyzacja` | Amortyzacja środków trwałych, KŚT | "amortyzacja", "KŚT", "wykaz rocznych stawek amortyzacyjnych" |
| `pit_kpir` | KPiR — prowadzenie podatkowej księgi przychodów i rozchodów | "KPiR", "rozporządzenie w sprawie prowadzenia podatkowej księgi" |
| `pit_ewidencja_ryczalt` | Ewidencja przychodów (ryczałt) | "ewidencja przychodów ryczałt", "rozporządzenie ewidencja ryczałtu" |
| `pit_roczny` | Rozliczenie roczne PIT-36/PIT-36L/PIT-28 | "PIT roczny JDG", "termin PIT", "kalendarz PIT" |

### 4.3 Grupa **VAT + JPK + KSeF** (8 tematów)

| ID | Temat | Keywordy |
|---|---|---|
| `vat_rejestracja` | Rejestracja VAT-R | "rejestracja VAT", "VAT-R", "obowiązek rejestracji VAT" |
| `vat_zwolnienie_200k` | Zwolnienie podmiotowe (próg 200 tys.) | "zwolnienie z VAT 200 tys", "art. 113 ustawy VAT" |
| `vat_jpk` | JPK_V7M / JPK_V7K | "JPK_VAT", "jednolity plik kontrolny" |
| `vat_ksef` | KSeF — Krajowy System e-Faktur (od 2026/2027) | "KSeF", "faktury ustrukturyzowane", "obowiązek KSeF" |
| `vat_stawki` | Stawki VAT (23/8/5/0%, zwolnienia) | "stawki VAT", "matryca VAT" |
| `vat_ue` | VAT-UE, transakcje wewnątrzwspólnotowe | "VAT-UE", "WDT", "WNT" |
| `vat_marza` | VAT marża (usługi turystyczne, second-hand) | "VAT marża" |
| `vat_biala_lista` | Biała lista VAT, weryfikacja kontrahenta | "biała lista VAT", "wykaz podatników VAT" |

### 4.4 Grupa **CEIDG i formalności** (7 tematów)

| ID | Temat | Keywordy |
|---|---|---|
| `ceidg_rejestracja` | Rejestracja JDG przez CEIDG-1 | "rejestracja CEIDG", "wniosek CEIDG-1" |
| `ceidg_pkd` | Kody PKD — wybór głównego i dodatkowych | "kody PKD", "klasyfikacja PKD 2007" |
| `ceidg_zawieszenie` | Zawieszenie działalności | "zawieszenie działalności CEIDG", "art. 22-25 prawo przedsiębiorców" |
| `ceidg_wznowienie` | Wznowienie działalności | "wznowienie działalności" |
| `ceidg_zamkniecie` | Zamknięcie / wykreślenie z CEIDG | "zamknięcie działalności", "wykreślenie CEIDG" |
| `ceidg_zmiana_wpisu` | Zmiana wpisu (adres, PKD, nazwa) | "zmiana wpisu CEIDG" |
| `ceidg_dzialalnosc_nierejestrowana` | Działalność nierejestrowana (próg 75% min. wynagr.) | "działalność nierejestrowana", "art. 5 prawo przedsiębiorców" |

### 4.5 Grupa **Prawo pracy** (8 tematów — gdy JDG zatrudnia)

| ID | Temat | Keywordy |
|---|---|---|
| `kp_umowa_o_prace` | Umowa o pracę | "umowa o pracę wzór", "Kodeks pracy art. 25" |
| `kp_umowa_zlecenie` | Umowa zlecenie | "umowa zlecenie", "art. 734 Kodeks cywilny" |
| `kp_umowa_o_dzielo` | Umowa o dzieło | "umowa o dzieło" |
| `kp_czas_pracy` | Czas pracy, nadgodziny, ewidencja | "czas pracy", "ewidencja czasu pracy", "nadgodziny" |
| `kp_urlop` | Urlop wypoczynkowy, macierzyński, opiekuńczy | "urlop wypoczynkowy", "wymiar urlopu" |
| `kp_wypowiedzenie` | Wypowiedzenie umowy o pracę | "wypowiedzenie umowy o pracę", "okres wypowiedzenia" |
| `kp_swiadectwo_pracy` | Świadectwo pracy | "świadectwo pracy wzór" |
| `kp_bhp_biuro` | BHP (zakres dla pracy biurowej / zdalnej) | "BHP biuro", "BHP praca zdalna", "szkolenie wstępne BHP" |

### 4.6 Grupa **RODO** (7 tematów)

| ID | Temat | Keywordy |
|---|---|---|
| `rodo_mala_firma` | RODO w małej firmie — przegląd obowiązków | "RODO mała firma", "RODO przedsiębiorca" |
| `rodo_rejestr_czynnosci` | Rejestr czynności przetwarzania (RCP) | "rejestr czynności przetwarzania", "art. 30 RODO" |
| `rodo_iod` | IOD — inspektor ochrony danych (kiedy wymagany) | "IOD obowiązek", "inspektor ochrony danych" |
| `rodo_klauzula_informacyjna` | Klauzula informacyjna (art. 13 RODO) | "klauzula informacyjna RODO", "art. 13 RODO" |
| `rodo_monitoring` | Monitoring pracowników | "monitoring pracowników RODO", "art. 22^2 Kodeksu pracy" |
| `rodo_naruszenie` | Naruszenie ochrony danych — zgłoszenie 72h | "naruszenie ochrony danych", "zgłoszenie do UODO" |
| `rodo_rekrutacja` | RODO w rekrutacji | "RODO rekrutacja", "klauzula CV" |

**Łącznie: 51 tematów.** Pełne pokrycie = każdy temat ma ≥1 dokument w bazie.

---

## 5. Katalog źródeł — Warstwa 1 (Legislacja)

> Pobierać w formie **tekstu jednolitego** (wersji obowiązującej, skonsolidowanej). Nie wersji historycznych. Format docelowy: **PDF** (bezpośrednio z ELI / ISAP) — daje stabilną typografię i jest oficjalnym artefaktem.

### 5.1 Akty MUST (8 ustaw bazowych)

| Akt | Identyfikator ELI/ISAP | Direct URL (PDF tekstu jednolitego) |
|---|---|---|
| Kodeks pracy | `WDU19740240141` | `https://api.sejm.gov.pl/eli/acts/DU/1974/24/text.pdf` |
| Ustawa o PIT | `WDU19910800350` | `https://api.sejm.gov.pl/eli/acts/DU/1991/80/text.pdf` |
| Ustawa o zryczałtowanym podatku dochodowym (ryczałt) | `WDU19981440930` | `https://api.sejm.gov.pl/eli/acts/DU/1998/144/text.pdf` |
| Ustawa o VAT | `WDU20040540535` | `https://api.sejm.gov.pl/eli/acts/DU/2004/54/text.pdf` |
| Prawo przedsiębiorców | `WDU20180000646` | `https://api.sejm.gov.pl/eli/acts/DU/2018/646/text.pdf` |
| Ustawa o systemie ubezpieczeń społecznych | `WDU19981370887` | `https://api.sejm.gov.pl/eli/acts/DU/1998/137/text.pdf` |
| Ustawa o ochronie danych osobowych | `WDU20180001000` | `https://api.sejm.gov.pl/eli/acts/DU/2018/1000/text.pdf` |
| RODO (rozporządzenie 2016/679) — wersja PL skonsolidowana | CELEX:`02016R0679-20160504` | `https://eur-lex.europa.eu/legal-content/PL/TXT/PDF/?uri=CELEX:02016R0679-20160504` |

### 5.2 Rozporządzenia wykonawcze SHOULD (~10–15 aktów)

| Rozporządzenie | Hasło wyszukiwania w ISAP/ELI |
|---|---|
| W sprawie prowadzenia podatkowej księgi przychodów i rozchodów (KPiR) | `rozporządzenie w sprawie prowadzenia podatkowej księgi` |
| W sprawie wykazu rocznych stawek amortyzacyjnych | `wykaz rocznych stawek amortyzacyjnych` |
| W sprawie prowadzenia ewidencji przychodów (ryczałt) | `rozporządzenie w sprawie prowadzenia ewidencji przychodów` |
| W sprawie szczegółowego zakresu danych zawartych w deklaracjach VAT (JPK_V7) | `JPK_V7M JPK_V7K rozporządzenie` |
| W sprawie wystawiania faktur (KSeF, faktury elektroniczne) | `rozporządzenie wystawianie faktur` |
| W sprawie szczegółowego trybu i warunków zgłaszania do ubezpieczeń (ZUA/ZWUA/DRA) | `rozporządzenie zgłaszanie do ubezpieczeń społecznych` |

**Sposób odkrycia:** ELI API endpoint `GET /eli/acts/{publisher}/{year}/{position}/references` zwraca listę aktów wykonawczych dla każdej ustawy z 5.1.

### 5.3 Specyfikacja techniczna pobierania L1

| Parametr | Wartość |
|---|---|
| Endpoint bazowy | `https://api.sejm.gov.pl/eli/` |
| Dokumentacja | `https://api.sejm.gov.pl/eli_pl.html` |
| Header obowiązkowy | `Accept: application/pdf` (bez tego można dostać HTML "Request Rejected" z WAF) |
| Walidacja po pobraniu | Pierwsze 4 bajty pliku muszą być `%PDF` |
| Anty-pattern do wykrycia | String "Request Rejected" w pierwszych 2 KB pliku → reject + retry z innym User-Agent |
| Retry policy | 3 próby z exponential backoff (1s, 4s, 16s) |
| User-Agent | `Mozilla/5.0 (compatible; AcademicResearch/1.0; +mailto:youremail)` |
| Rate limit | 5 req/s (ELI nie publikuje limitu, ale to bezpieczne) |
| Format zapisu | `data/raw/legislation/{eli_id}.pdf` + `data/raw/legislation/{eli_id}.json` (metadata) |

---

## 6. Katalog źródeł — Warstwa 2 (Portale rządowe)

| # | Portal | Sekcje docelowe (URL) | Format dominujący | Szac. liczba dok. | Tier WAF |
|---|---|---|---|---|---|
| 1 | **biznes.gov.pl** | `/pl/portal/0516`, `/pl/portal/00235`, `/pl/opisy-procedur/`, `/pl/portal/{4-cyfrowy-id}` | HTML + DOCX (wzory) | 80–120 | Cloudflare — wymaga undetected browser lub residential proxy |
| 2 | **zus.pl** | `/baza-wiedzy/biblioteka-zus/poradniki/firmy`, `/baza-wiedzy/skladki-wskazniki-odsetki`, `/baza-wiedzy/biezace-wyjasnienia-komorek-merytorycznych` | HTML + PDF | 30–50 | F5 ASM — analogicznie wymaga browser fingerprinting |
| 3 | **podatki.gov.pl** | `/abc-podatkow/broszury-informacyjne/broszury-pit/`, `/broszury-vat/`, `/podatki-firmowe/jednolity-plik-kontrolny/`, `/podatki-firmowe/ksef/`, `/podatki-firmowe/ewidencje-i-sprawozdawczosc/`, `/podatki-firmowe/dzialalnosc-gospodarcza/`, `/kalendarz-pit/` | PDF (broszury) + HTML | 20–40 | Brak — czysty httpx wystarczy |
| 4 | **pip.gov.pl** | `/publikacje/publikacje-dla-pracodawcow?start={N}` (paginacja: 0, 9, 18, …, 126) | PDF | 15–25 (po filtrze tematycznym) | Brak |
| 5 | **uodo.gov.pl** | `/pl/138` (wydawnictwa UODO) | PDF | 10–15 | Brak |

### 6.1 Specyfikacja techniczna L2 — szczegóły per portal

#### 6.1.1 biznes.gov.pl
- **Discovery 1**: pobierz `https://www.biznes.gov.pl/sitemap_pl.xml` przez headless Chrome z trybem undetected.
- **Discovery 2 (fallback)**: jeśli sitemap zablokowany → BFS od `https://www.biznes.gov.pl/pl/portal/0516` (firma), max depth=3, follow tylko linki na `/pl/portal/`, `/pl/opisy-procedur/`.
- **Filtr URL**: zachowaj URL-e zawierające w tytule strony którykolwiek z keywordów: `ZUS`, `składk`, `podatek`, `VAT`, `ryczałt`, `działalność`, `CEIDG`, `zawiesz`, `RODO`, `pracown`, `umowa`, `urlop`, `JPK`, `KSeF`, `amortyzacj`, `IP Box`, `nierejestrowan`.
- **Wzory DOCX**: linki kończące się na `.docx` na stronach typu "Wzór umowy o pracę", "Wzór klauzuli informacyjnej" — pobrać binarnie, **nie parsować** (w tym etapie).
- **Headers wymagane**: realistic User-Agent, `Accept-Language: pl-PL,pl;q=0.9`, JS rendering = TAK.
- **Delay**: 2–5 s między requestami.

#### 6.1.2 zus.pl
- **Seed URLs**:
  - `https://www.zus.pl/baza-wiedzy/biblioteka-zus/poradniki/firmy`
  - `https://www.zus.pl/baza-wiedzy/biblioteka-zus/poradniki/archiwum-poradnikow`
  - `https://www.zus.pl/baza-wiedzy/skladki-wskazniki-odsetki`
  - `https://www.zus.pl/baza-wiedzy/biezace-wyjasnienia-komorek-merytorycznych`
- **Strategia**: BFS z URL scorerem favoryzującym `/poradnik/`, `/baza-wiedzy/`, `.pdf` (waga 1.0); `.aspx?id=` (0.3); reszta (0).
- **Paginacja**: parametr `?p=N` lub `?page=N`, auto-detect przez parsowanie containera klasy `pagination`.
- **Wzory ZUS** (ZUA, ZWUA, DRA, RCA, RZA): `https://www.zus.pl/documents/10182/167567/{KOD}.pdf`.

#### 6.1.3 podatki.gov.pl
- **Sitemap**: `https://www.podatki.gov.pl/sitemap.xml` — bez WAF, czysty `httpx.get()`.
- **Strategia**: dla każdej z 7 sekcji (lista wyżej) → scrape listing → wyekstrahuj wszystkie `<a href="*.pdf">` → batch download.
- **Dodatkowo HTML**: artykuły podlinkowane z listingu (nie tylko PDF) — często mają tabelarne podsumowania.

#### 6.1.4 pip.gov.pl
- **Walker po paginacji**: iteruj `?start=N` od 0 z krokiem 9, aż listing będzie pusty (sentinel: brak elementów `<div class="publikacja">`).
- **Filtr kategorii (whitelist)**: `Prawo pracy`, `Legalność zatrudnienia`, `Umowy`, `Czas pracy`, `Urlopy`, `BHP w biurze`, `Praca zdalna`.
- **Dropuj**: `BHP w rolnictwie`, `BHP na żurawiach`, `BHP w budownictwie` itp. — niezwiązane z JDG biurową.

#### 6.1.5 uodo.gov.pl
- **Listing**: `https://uodo.gov.pl/pl/138` → wyekstrahuj `<a href="/pl/file/NNNN">` → batch download.
- **Filtr title (whitelist)**: `pracodawc`, `przedsiębiorc`, `małych firm`, `monitoring`, `naruszen`, `administrator`, `rejestr czynności`, `rekrutacj`, `IOD`.

---

## 7. Katalog źródeł — Warstwa 3 (Materiały praktyczne, opcjonalne)

### 7.1 Interpretacje indywidualne KIS

| Parametr | Wartość |
|---|---|
| Portal | `https://sip.mf.gov.pl/` |
| Charakterystyka | JS-heavy (React); wymaga headless browser |
| Strategia | Wpisuj kolejno 10 zapytań typowych dla JDG, dla każdego pobierz top 20 wyników, filtr `typ=indywidualna AND rok>=2022` |
| Lista zapytań | `ryczałt programista`, `KUP samochód`, `IP Box`, `amortyzacja laptop`, `ZUS preferencyjny`, `KPiR wydatki`, `VAT zwolnienie podmiotowe`, `JPK błąd`, `działalność nierejestrowana`, `zawieszenie działalności` |
| Oczekiwana liczba | 80–100 unikalnych po dedup z 200 surowych |
| Czas | ~30 min |
| Fallback | Jeśli Cloudflare blokuje Playwright → skompletuj 50 ręcznie wybranych z najpopularniejszych |

### 7.2 Tabele stawek i kalendarze

| Element | Skąd pozyskać |
|---|---|
| Stawki ryczałtu per PKD | Załącznik do **ustawy o ryczałcie** (już w L1 — wyciągnąć w parserze) |
| Stawki amortyzacji (Wykaz KŚT) | Załącznik do **rozporządzenia w sprawie wykazu rocznych stawek amortyzacyjnych** (L1.5.2) |
| Stawki ZUS na rok bieżący | `zus.pl/baza-wiedzy/skladki-wskazniki-odsetki` (L2.6.1.2) |
| Kalendarz PIT | `https://www.podatki.gov.pl/kalendarz-pit/` (L2.6.1.3) |
| Kalendarz przedsiębiorcy | `biznes.gov.pl` strony "Kalendarz" (L2.6.1.1) |

### 7.3 Wzory dokumentów (DOCX)
- Z biznes.gov.pl: `https://pliki.biznes.gov.pl/...` — sekcja "Wzory" przy każdej procedurze.
- Z ZUS: druki `.pdf` + `.docx` z `https://www.zus.pl/wzory-formularzy`.

---

## 8. API rejestrów (poza scope DOC, ale wymienione dla kompletności)

> Te API są używane w **runtime** chatbota (personalizacja po NIP), nie w fazie zbierania dokumentów. Wymienione, by wykonawca rozumiał, że chatbot ma **dwa źródła danych**: (a) statyczna baza wiedzy z tego dokumentu; (b) dynamiczne odpytania API w czasie rozmowy.

| Rejestr | Endpoint | Auth | Użycie w chatbocie |
|---|---|---|---|
| CEIDG v3 | `https://dane.biznes.gov.pl/api/ceidg/v3/firmy` | Token (darmowy po rejestracji na biznes.gov.pl) | Status JDG, data rozpoczęcia, PKD, adres |
| Biała Lista VAT | `https://wl-api.mf.gov.pl/` | Brak | Status VAT kontrahenta, numer rachunku, daty zmian |
| KRS Open API | `https://api-krs.ms.gov.pl/` | Brak | Wpisy spółek (kontrahenci JDG) |
| REGON BIR1 | `https://api.stat.gov.pl/Home/RegonApi` (SOAP) | Klucz testowy darmowy / produkcyjny po wniosku | Pełna lista PKD (CEIDG zwraca tylko główne) |
| TERYT WS1 | `https://api.stat.gov.pl/TERYT/` (SOAP) | Klucz | Walidacja adresów, słowniki miejscowości |
| SUDOP | `https://sudop.uokik.gov.pl/` | Niezweryfikowane | Pomoc publiczna otrzymana przez przedsiębiorcę |

---

## 9. Schemat metadanych (per dokument)

Każdy pobrany plik **musi** mieć sidecar JSON z metadanymi. Rekomendowany format zapisu: `{filename}.meta.json` obok pliku raw.

### 9.1 Pola obowiązkowe

| Pole | Typ | Opis | Przykład |
|---|---|---|---|
| `id` | string (16 znaków hex) | sha256(content)[:16] | `f7bf0acd264a99b7` |
| `url` | string | Oryginalny URL pobrania | `https://api.sejm.gov.pl/eli/acts/DU/2025/1294/text.pdf` |
| `source` | enum | Symbol źródła | `eli` / `biznes_gov` / `zus` / `podatki` / `pip` / `uodo` / `kis` / `eurlex` |
| `topic_id` | string | ID tematu z sekcji 4 | `pit_ryczalt` |
| `format` | enum | Rozszerzenie pliku | `pdf` / `html` / `docx` / `xlsx` |
| `fetched_at` | ISO 8601 | Timestamp pobrania | `2026-04-25T10:30:00Z` |
| `http_status` | int | Kod HTTP odpowiedzi | `200` |
| `content_type` | string | Header Content-Type z odpowiedzi | `application/pdf` |
| `bytes` | int | Wielkość pliku w bajtach | `617949` |

### 9.2 Pola zalecane

| Pole | Typ | Opis |
|---|---|---|
| `title` | string | Tytuł dokumentu (z `<title>` HTML albo z metadanych PDF) |
| `last_modified` | ISO 8601 | Z headera `Last-Modified` lub PDF metadata |
| `parent_url` | string | Strona, z której wziął się link (audyt) |
| `discovery_source` | enum | `seed` / `sitemap` / `bfs` / `paginacja` / `attachment` / `references_api` |
| `is_official` | bool | Czy domena jest rządowa (`.gov.pl` / `eur-lex.europa.eu`) |
| `eli_id` | string | Identyfikator ELI dla aktów (`DU/2025/1294`) |

### 9.3 Pola opcjonalne (wypełniane przez kolejne etapy pipeline'u)

`token_count`, `is_relevant`, `is_duplicate`, `canonical_id`, `relevance_score` — **nie wypełniaj** w fazie zbierania.

---

## 10. Kryteria jakości (filtr po pobraniu)

Filtr stosowany po fetch + przed zapisaniem do manifestu. Plik **odrzucony** = nie zapisuj go do indeksu (możesz pozostawić binary na dysku w `quarantine/` dla audytu).

| Kryterium | Próg | Akcja przy naruszeniu |
|---|---|---|
| Wielkość minimalna | 2 KB | Reject (zwykle to jest 404/error page) |
| Wielkość maksymalna | 50 MB | Reject (broszura > 50 MB to prawie na pewno OCR-skan ze zbędnymi załącznikami) |
| Język dominujący | PL (≥ 80% tekstu w detektorze) | Reject (np. wersje EN-only) |
| Sygnatura pliku | Zgodna z deklarowanym MIME | Reject (PDF musi zaczynać się od `%PDF`) |
| Zawartość WAF-error | Brak frazy "Request Rejected", "Access Denied", "Cloudflare" w pierwszych 2 KB | Reject + retry |
| Tekst po parsowaniu (jeśli dostępne) | ≥ 200 słów | Mark `low_content`, ale zapisz |

---

## 11. Czarna lista — czego **nie** pobierać

### 11.1 Domeny śmieciowe (paywall, reklamy, agregatory bez wartości dodanej)

```
gofin.pl              — paywall, ucięte treści
infor.pl              — reklamy + paywall
e-pity.pl             — narzędzie komercyjne, marketing
fmleasing.pl          — wycieki PDF interpretacji KIS, lepiej pobrać z sip.mf.gov.pl
pkd.com.pl            — agregator bez wartości dodanej nad PKD oficjalnym
sip.lex.pl            — paywall Wolters Kluwer
przepisy.gofin.pl     — agregator + paywall
poradnikprzedsiebiorcy.pl  — content farm
poradnik.wfirma.pl    — content farm
ksiegowosc.infor.pl   — paywall
```

### 11.2 Wzorce URL do odrzucenia

```
*?login=*             — paywall trigger
*/cookie-policy/*     — strony bez wartości
*/regulamin/*
*/polityka-prywatnosci/*  (chyba że to UODO publikuje wzorce)
*?download=*token=*   — często wymaga sesji
*?utm_*               — kampanie marketingowe (URL param noise — strip ich z linka)
```

### 11.3 Treści do odrzucenia po parsowaniu

- Strony błędów 404/500 zwracające 200 OK (typowy bug CMS-ów rządowych)
- Strony "W trakcie aktualizacji"
- Listy linków bez własnej treści (sitemapy w formie HTML)

---

## 12. Deduplication

Wykonawca nie musi robić pełnego dedupu, ale **musi** zaznaczyć potencjalne kolizje:

### 12.1 Dedup poziomu URL
Normalizuj URL przed zapisem: lowercase host, drop fragment (`#...`), drop tracking params (`utm_*`, `fbclid`, `gclid`), trailing slash consistency.

### 12.2 Dedup poziomu pliku
Hashuj treść (sha256) → jeśli ten sam hash dla 2 URL-i, oznacz jeden jako `canonical_id` drugiego (preferuj URL z domeny `.gov.pl`).

### 12.3 Dedup semantyczny (poza scope tego dokumentu)
Robi go kolejny etap (TF-IDF cosine ≥ 0.85 = duplikat). Dla wykonawcy wystarczy URL + content hash.

### 12.4 Reguły kanonikalizacji aktów prawnych
Ten sam akt często występuje w 3 miejscach: ISAP, dziennikustaw.gov.pl, eli/api.sejm.gov.pl. **Wybór kanonikalny: ELI**, bo daje stabilny PDF + metadata API.

---

## 13. Struktura plików wyjściowych

```
data/
├── manifest.csv                          # główny indeks (sekcja 14)
├── raw/
│   ├── legislation/
│   │   ├── DU_2024_1234.pdf
│   │   ├── DU_2024_1234.meta.json
│   │   └── ...
│   ├── biznes_gov/
│   │   ├── 0516_zakladanie_firmy.html
│   │   ├── 0516_zakladanie_firmy.meta.json
│   │   ├── 0516_zakladanie_firmy.assets/
│   │   │   └── wzor_umowy.docx
│   │   └── ...
│   ├── zus/
│   ├── podatki/
│   ├── pip/
│   ├── uodo/
│   ├── kis/
│   └── eurlex/
└── quarantine/                          # pliki odrzucone (do audytu)
    ├── _waf_blocked/
    └── _too_small/
```

### 13.1 Konwencja nazewnictwa

| Źródło | Pattern nazwy pliku |
|---|---|
| ELI / ISAP | `{publisher}_{year}_{position}.pdf` (np. `DU_2024_1234.pdf`) |
| biznes.gov.pl | `{portal_id}_{slug}.html` (np. `0516_zakladanie_firmy.html`) |
| zus.pl | `{section}_{slug}.{ext}` |
| podatki.gov.pl | `{section}_{slug}.{ext}` |
| pip / uodo | `{publication_id}.pdf` |
| KIS | `interp_{rok}_{nr}.html` |

Dopuszczalna alternatywa: nazwa = `sha256(content)[:16].{ext}` jeśli wykonawca nie chce parsować slugów. Wtedy mapowanie URL ↔ plik jest **tylko** w manifeście.

---

## 14. Manifest CSV (główny indeks)

Plik `data/manifest.csv` z kolumnami:

```csv
id,url,source,topic_id,format,fetched_at,http_status,content_type,bytes,relative_path,title,last_modified,is_official,eli_id,parent_url,discovery_source
```

### 14.1 Przykładowe wiersze

```csv
f7bf0acd264a99b7,https://api.sejm.gov.pl/eli/acts/DU/2024/1234/text.pdf,eli,pit_kpir,pdf,2026-04-25T10:00:00Z,200,application/pdf,617949,raw/legislation/DU_2024_1234.pdf,"Rozporządzenie MF w sprawie KPiR",2024-12-30T00:00:00Z,true,DU/2024/1234,,references_api
b9e10cc296f70428,https://www.biznes.gov.pl/pl/portal/00235,biznes_gov,pit_skala,html,2026-04-25T10:01:00Z,200,text/html;charset=utf-8,142318,raw/biznes_gov/00235_pit.html,"PIT — przewodnik dla przedsiębiorców",2025-11-15T00:00:00Z,true,,https://www.biznes.gov.pl/sitemap_pl.xml,sitemap
```

---

## 15. Workflow operacyjny (dla wykonawcy)

### Faza 1 — Setup (1 h)
1. Załóż katalog projektu zgodnie z sekcją 13.
2. Zainstaluj narzędzia: `httpx`, `playwright` (chromium), `pymupdf` (do walidacji PDF), `chardet` (detekcja kodowania).
3. Zarejestruj się na `dane.biznes.gov.pl` i wygeneruj token CEIDG (do późniejszego użycia, **nie** dla zbierania).
4. Stwórz `.env` z `USER_AGENT="..."` i opcjonalnie `PROXY_URL="..."` (jeśli planujesz residential proxy).

### Faza 2 — Warstwa 1 (1–2 h)
1. Pobierz 8 ustaw bazowych z 5.1 (proste GET + walidacja `%PDF`).
2. Dla każdej ustawy odpytaj `/eli/acts/{p}/{y}/{pos}/references` → pobierz wszystkie rozporządzenia z `type=Rozporządzenie AND status=obowiązujący`.
3. Dodatkowo wyszukaj 6 rozporządzeń z 5.2 po nazwie.
4. Zapisz manifest dla L1 (~25–35 plików, ~80–150 MB).

**Akceptacja Fazy 2:** Każda z 8 ustaw bazowych obecna w `data/raw/legislation/`, każda otwiera się w czytniku PDF, każda ma sidecar JSON. **Bez tego nie idź dalej.**

### Faza 3 — Warstwa 2, źródła bez WAF (2–3 h)
Kolejność: `podatki.gov.pl` → `pip.gov.pl` → `uodo.gov.pl`.
1. Discovery (sitemap / paginacja / listing) per portal.
2. Filtruj po sekcji 4 keywordów + sekcji 11 czarnej liście.
3. Batch download (httpx async, 5 concurrent).
4. Walidacja per plik (sekcja 10).

**Akceptacja Fazy 3:** ~50 nowych plików, manifest poszerzony.

### Faza 4 — Warstwa 2, WAF-protected (3–6 h, ryzykowne)
Kolejność: `biznes.gov.pl` → `zus.pl`.
1. Tier 1: undetected-chromedriver, realistic User-Agent, JS rendering.
2. Tier 2 (jeśli 403): dodaj residential proxy.
3. Akceptowalny rate: 2 req/s, delay 3 s.
4. Smoke test 5 URL-i przed pełnym crawlem.

**Akceptacja Fazy 4:** ≥ 100 nowych plików, brak 403 w sample 20 ostatnich.

### Faza 5 — Warstwa 3 (opcjonalne, 1–4 h)
1. KIS: 10 zapytań × 20 wyników → ~80 interpretacji.
2. Wzory dokumentów: oddzielnie z biznes.gov.pl (DOCX).

### Faza 6 — Walidacja końcowa (30 min)
1. `manifest.csv` ma ≥ 50 wierszy.
2. Wszystkie 51 tematów z sekcji 4 mają ≥ 1 dokument (`SELECT topic_id, COUNT(*) FROM manifest GROUP BY topic_id`).
3. Każdy `relative_path` istnieje na dysku.
4. Brak duplikatów `id` (sha256).
5. Pokrycie warstw: L1 ≥ 8, L2 ≥ 30 — nieprzekraczalny minimum.
6. Wygeneruj `data/coverage_report.md` z:
   - Liczba dokumentów per `source`
   - Liczba dokumentów per `topic_id`
   - Lista tematów BEZ pokrycia (jeśli puste — sukces)
   - Total MB na dysku

---

## 16. Kryteria akceptacji końcowej

| Kryterium | Próg minimalny | Próg docelowy |
|---|---|---|
| Liczba dokumentów (po dedup) | 50 | 200 |
| Pokrycie tematyczne | 51/51 tematów ≥ 1 dok | 51/51 ≥ 3 dok |
| Warstwa L1 | 8/8 ustaw bazowych | 8 ustaw + 10 rozporządzeń |
| Warstwa L2 | 30 dokumentów | 80–100 |
| Warstwa L3 | 0 (opcjonalne) | 50 |
| Manifest kompletny | 100 % pól obowiązkowych | + 80 % pól zalecanych |
| Stosunek `.gov.pl` w sources | ≥ 80 % | ≥ 95 % |
| Walidacja sygnatur plików | 100 % | 100 % |
| Czas potrzebny | 8 h | 16 h |

---

## 17. Czego wykonawca **nie** robi (out of scope)

1. **Parsowanie do markdown** — to robi kolejny etap (PyMuPDF4LLM, Trafilatura, MinerU jako fallback).
2. **Chunking** — Chonkie / RecursiveChunker, osobny etap.
3. **Embeddingi** — sdadas/polish, BGE-M3, osobny etap.
4. **Indeks wektorowy** — Qdrant, osobny etap.
5. **Klasyfikacja przez LLM** — relevance/topic judge, osobny etap.
6. **Dedup semantyczny** — TF-IDF/SemHash, osobny etap.
7. **Cytowanie i ocena LLM** — RAGAS, osobny etap.
8. **Frontend / runtime** — out of scope całkowicie.

Zadanie wykonawcy kończy się na **manifeście + raw plikach + sidecar metadanych**.

---

## 18. Czytelnictwo / referencje (dla pracy)

W bibliografii pracy inżynierskiej źródła pierwotne (URL-e z manifestu) cytujemy formułą:
> *Ustawa z dnia 26 lipca 1991 r. o podatku dochodowym od osób fizycznych*, tekst jednolity Dz.U. 1991 nr 80 poz. 350, dostęp przez ELI API Sejmu RP, [api.sejm.gov.pl/eli/acts/DU/1991/80](https://api.sejm.gov.pl/eli/acts/DU/1991/80) (pobrano: 25.04.2026).

Poradniki rządowe:
> Ministerstwo Finansów, *Broszura informacyjna do PIT-36 za 2025 rok*, podatki.gov.pl, [link] (pobrano: 25.04.2026).

Opcjonalnie warto wykorzystać prace odniesieniowe:
- Lewis et al. (2020) — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*
- Chan et al. (2024) — *Don't Do RAG: When Cache-Augmented Generation is All You Need*
- Mroczkowski et al. (2021) — *HerBERT: Efficiently Pretrained Transformer-based Language Model for Polish*
- Bryłkowski & Klikowski (2025) — *LLM in Polish Legislative Content Analysis*, arXiv:2503.12100

---

## 19. Rozszerzenia (dla agenta LLM, jeśli realizuje zadanie autonomicznie)

Jeśli wykonawcą jest agent LLM:
1. Po każdej Fazie zapisz **stan postępu** do `data/progress.json` (które URL-e gotowe, które failed, które retry).
2. Jeśli napotkasz nieoczekiwany błąd (HTTP 5xx, timeout, sygnatura niezgodna) — **nie powtarzaj infinitely**. Maks. 3 retry z exponential backoff, potem zapisz do `data/quarantine/_failed.csv` i kontynuuj.
3. Trzymaj się rate limitów. Lepiej iść wolniej niż dostać IP ban.
4. Nie wymyślaj URL-i. Wszystkie URL-e do pobrania albo są wymienione tutaj wprost, albo pochodzą z discovery (sitemap/listing/API). **Halucynacja URL-a = strata czasu.**
5. Jeśli ZUS/biznes.gov.pl odrzuca Twoje requesty mimo Tier 1+2, zatrzymaj się i zaraportuj do operatora — nie próbuj omijać WAF kreatywnymi metodami (możesz złamać ToS).

---

## 20. Wersjonowanie tego dokumentu

| Wersja | Data | Zmiany |
|---|---|---|
| 1.0 | 2026-04-25 | Wersja początkowa, stworzona po wyczyszczeniu pierwotnego pipeline'u v2 |

---

**Koniec specyfikacji.** Powyższy dokument jest samowystarczalny — nie wymaga znajomości wcześniejszego kodu repozytorium.
