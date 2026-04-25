# Rekomendacja zakresu pracy inżynierskiej — JDG Chatbot
## „Projekt i ewaluacja spersonalizowanego chatbota wiedzy dla jednoosobowej działalności gospodarczej opartego na architekturze Cache-Augmented RAG z integracją rejestrów publicznych, obserwowalnością i testami bezpieczeństwa"

---

## 1. Koncepcja systemu

### Persona użytkownika
Osoba fizyczna prowadząca (lub zakładająca) jednoosobową działalność gospodarczą w Polsce. Potrzebuje odpowiedzi na codzienne pytania o ZUS, podatki, formalności, obowiązki prawne — bez czytania ustaw i rozporządzeń.

### Trzy tryby pracy chatbota

**Tryb ogólny (RAG)**: użytkownik pyta bez podawania NIP-u. Chatbot odpowiada na podstawie bazy wiedzy. "Jakie są formy opodatkowania JDG?", "Kiedy muszę zarejestrować się jako VAT-owiec?", "Ile wynosi ZUS preferencyjny?"

**Tryb spersonalizowany (RAG + rejestry)**: użytkownik podaje NIP. Chatbot odpytuje CEIDG/REGON/VAT i personalizuje odpowiedzi. "Twoje PKD 62.01.Z kwalifikuje się do ryczałtu 12%. Działalność od 15.03.2024 — jesteś na preferencyjnym ZUS, mija Ci w marcu 2026. Nie jesteś zarejestrowany jako VAT-owiec."

**Tryb cache-first**: powtarzające się pytania (ZUS 2026, terminy JPK, stawki ryczałtu) obsługiwane z semantic cache bez pełnego retrieval. Cel: latency <1s dla cache hits vs ~3–5s dla full RAG.

---

## 2. Dane — źródła bazy wiedzy

Baza wiedzy obejmuje trzy warstwy: legislację (ustawy i rozporządzenia z ELI/EUR-Lex), poradniki rządowe (biznes.gov.pl, zus.pl, podatki.gov.pl, pip.gov.pl, uodo.gov.pl) oraz materiały praktyczne (interpretacje indywidualne KIS, wzory dokumentów, tabele stawek). Szczegółowy plan zbierania: zob. `data_collection_spec.md` i `12_data_collection_execution_plan.md`.

---

## 3. Rejestry publiczne — 3 API

### 3.1 CEIDG API v3 — PRIMARY

| Cecha | Wartość |
|-------|---------|
| **Endpoint** | `https://dane.biznes.gov.pl/api/ceidg/v3/firmy` |
| **Protokół** | REST (JSON), JWT Token |
| **Autoryzacja** | Bezpłatna rejestracja na biznes.gov.pl |
| **Zakres** | Status (AKTYWNY/ZAWIESZONY/WYKREŚLONY), NIP, REGON, data rozpoczęcia, kody PKD, adres, pełnomocnictwa |
| **Rola w chatbocie** | Core rejestr dla JDG. Data rozpoczęcia → obliczenie "na jakiej uldze ZUS jesteś". PKD → stawka ryczałtu. Status → czy firma jest aktywna. |
| **Link** | [dane.biznes.gov.pl](https://dane.biznes.gov.pl/) · [Dokumentacja API v3](https://pliki.biznes.gov.pl/akademia/Hurtownia_danych/HD%20CEIDG%20-%20API%20v3%20HD%20-%20Dokumentacja%20dla%20integrator%C3%B3w%20v1.0.pdf) |

### 3.2 GUS REGON BIR1 API

| Cecha | Wartość |
|-------|---------|
| **Endpoint** | SOAP/REST: `api.stat.gov.pl/Home/RegonApi` |
| **Autoryzacja** | Klucz API (bezpłatny, wniosek mailowy) |
| **Zakres** | REGON, NIP, pełna lista PKD (główny + dodatkowe), forma prawna, adres |
| **Rola** | Pełna lista PKD → mapowanie na stawki ryczałtu (ustawa o ryczałcie, załącznik). CEIDG daje PKD główne, REGON daje WSZYSTKIE. |
| **Link** | [api.stat.gov.pl](https://api.stat.gov.pl/Home/RegonApi) |

### 3.3 Biała Lista VAT — Ministerstwo Finansów

| Cecha | Wartość |
|-------|---------|
| **Endpoint** | `https://wl-api.mf.gov.pl/` |
| **Autoryzacja** | Brak |
| **Zakres** | Status VAT (czynny/zwolniony/niezarejestrowany), rachunki bankowe, data rejestracji VAT |
| **Rola** | Status VAT → personalizacja: "musisz wystawiać faktury z VAT" vs "korzystasz ze zwolnienia podmiotowego". Rachunki → "Twój rachunek jest na Białej Liście". |
| **Link** | [gov.pl/web/kas/api-wykazu-podatnikow-vat](https://www.gov.pl/web/kas/api-wykazu-podatnikow-vat) |

### 3.4 ELI API Sejmu — rejestry legislacyjne (freshness + direct lookup)

| Cecha | Wartość |
|-------|---------|
| **Endpoint** | `https://api.sejm.gov.pl/eli/` |
| **Protokół** | REST (JSON), OpenAPI 3.0 spec dostępny |
| **Autoryzacja** | Brak — w pełni otwarte |
| **Dokumentacja** | [api.sejm.gov.pl/eli_pl.html](https://api.sejm.gov.pl/eli_pl.html) · [OpenAPI spec](https://api.sejm.gov.pl/eli/openapi/) |
| **Kluczowe endpointy** | `/eli/acts/{publisher}/{year}` — lista aktów per rok. `/eli/acts/search?title=...&status=...` — wyszukiwanie. `/eli/acts/{publisher}/{year}/{pos}` — metadane aktu (status, data zmian, relacje). Tekst aktu w PDF/HTML. |
| **Zakres** | Wszystkie akty prawne z Dziennika Ustaw i Monitora Polskiego od 1918 do teraz. Status (obowiązujący/uchylony/zmieniony), daty, tekst jednolity, relacje między aktami. |

**Rola w systemie — 4 zastosowania:**

**A) Automatyzacja pobierania legislacji (pipeline)**: zamiast ręcznie ściągać PDFy ustaw, skrypt odpytuje ELI API → pobiera tekst jednolity najnowszej wersji → parsuje → chunkuje → indeksuje. Pełna automatyzacja warstwy 1 bazy wiedzy.

```python
# Przykład: pobranie aktualnej wersji ustawy o PIT
import httpx

# Szukaj ustawy o PIT
resp = httpx.get("https://api.sejm.gov.pl/eli/acts/search", params={
    "title": "podatek dochodowy od osób fizycznych",
    "status": "obowiązujący",
    "publisher": "DU",
})
acts = resp.json()["items"]
# → znajdzie Dz.U. 1991 poz. 350 (ustawa o PIT) z aktualnym statusem

# Pobranie metadanych + linku do tekstu
act_url = f"https://api.sejm.gov.pl/eli/acts/DU/1991/350"
act_meta = httpx.get(act_url).json()
# act_meta["status"] → "obowiązujący"
# act_meta["textHTML"] → true/false
# act_meta["changeDate"] → data ostatniej zmiany
```

**B) Legislation drift detection (observability)**: cron job codziennie sprawdza `/eli/acts/DU/{current_year}` → czy pojawiły się nowe akty zmieniające ustawy w bazie wiedzy. Jeśli tak → alert + oznaczenie chunków jako potentially_stale. Nikt tego nie robi w RAG-ach — oryginalny wkład.

**C) Status aktu w odpowiedzi (guardrail)**: gdy chatbot cytuje "art. 22 ustawy o PIT" → w tle ELI API potwierdza status "obowiązujący" i datę ostatniej zmiany. Jeśli zmiana <30 dni → disclaimer: "Uwaga: ten przepis mógł zostać niedawno zmieniony."

**D) Direct lookup referencji prawnych**: NER wyciąga "art. 52 §1 KP" z zapytania → ELI API: pobierz tekst Kodeksu pracy → direct lookup artykułu → precyzyjniejsze niż embedding search.

### 3.5 EUR-Lex API (opcjonalny)

| Cecha | Wartość |
|-------|---------|
| **Endpoint** | `https://eur-lex.europa.eu/eurlex-ws/` (REST) + SPARQL endpoint CELLAR |
| **Autoryzacja** | Brak (publiczny) |
| **Zakres** | Legislacja UE w 24 językach, w tym polskim |
| **Rola** | Pobieranie RODO (Rozporządzenie 2016/679) po polsku — jedyny akt UE relevantny dla JDG chatbota. Opcjonalny — RODO można też pobrać raz z EUR-Lex ręcznie. |
| **Link** | [eur-lex.europa.eu/content/help/eurlex-content/technical](https://eur-lex.europa.eu/content/help/eurlex-content/technical-information.html) |

**Uzasadnienie jako opcjonalny**: dla JDG chatbota jedynym aktem UE jest RODO. Nie warto budować pełnej integracji z EUR-Lex dla jednego dokumentu. Ale: samo wspomnienie EUR-Lex w architekturze jako "rozszerzalność na legislację UE" wygląda dobrze w pracy. Implementacja: jednorazowe pobranie RODO w PDF/HTML, nie ciągła integracja.

---

### Architektura API — dwa typy, dwie role

```
═══════════════════════════════════════════════════════
  REJESTRY GOSPODARCZE (personalizacja, per-session)
═══════════════════════════════════════════════════════

Użytkownik podaje NIP
        │
        ▼
[1] CEIDG → status, data rozpoczęcia, PKD główne, adres
        │
        ├── data rozpoczęcia → oblicz: ulga na start (6 mies.) / preferencyjny (24 mies.) / duży ZUS
        ├── PKD → stawka ryczałtu (jeśli wybrano ryczałt)
        └── adres → właściwy US
        │
        ▼
[2] REGON → pełna lista PKD (dodatkowe kody → dodatkowe stawki ryczałtu)
        │
        ▼
[3] Biała Lista VAT → status VAT
        │
        ├── niezarejestrowany → "Korzystasz ze zwolnienia podmiotowego (do 200k PLN/rok)"
        ├── czynny → "Jesteś VAT-owcem. Obowiązek JPK_V7 do 25. dnia miesiąca."
        └── wykreślony → "⚠️ Zostałeś wykreślony z rejestru VAT. Sprawdź powód w US."
        │
        ▼
[Chatbot] → spersonalizowana odpowiedź z konkretnymi kwotami i terminami

═══════════════════════════════════════════════════════
  REJESTRY LEGISLACYJNE (freshness, pipeline, guardrails)
═══════════════════════════════════════════════════════

[4] ELI API (api.sejm.gov.pl)
        │
        ├── Pipeline: automatyczne pobieranie/aktualizacja tekstów ustaw
        ├── Drift detection: cron → czy pojawiły się zmiany w ustawach z bazy?
        ├── Guardrail: potwierdzenie statusu cytowanego aktu ("obowiązujący")
        └── Direct lookup: NER → "art. 22 ustawy o PIT" → ELI → tekst artykułu
        │
[5] EUR-Lex (opcjonalny) → RODO po polsku
```

---
