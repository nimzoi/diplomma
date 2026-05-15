# Sources catalog — polska farmakologia (single source of truth dla R3)

**Status:** ACTIVE (2026-05-15)
**Domena:** farmakologia kliniczna szeroka (psychiatryczny eval subset ATC N05-N06)
**Target corpus size:** ~4100 dokumentów po dedup
**Related:** DEC-001 (rotacja domeny), DEC-002 (ChPL+Ulotka pairing)

Pełny audit źródeł na podstawie sources research R1 (2026-05-15, pharma broad) i R2 (2026-05-15, Ulotki + NFZ + adjacencies). Wszystkie URL-e zweryfikowane.

## Source selection methodology

> **Constraint dla R3 (Dane):** tę metodologię trzeba explicit zapisać w rozdziale R3 sekcja "Metodologia doboru źródeł" oraz w R2 sekcja "Metodologia przeglądu". Promotor feedback v1 wytykał brak rygorystycznej selekcji — bez tej sekcji ryzyko powtórki oceny.

### Inclusion criteria (kryteria włączenia)

Źródło zostaje **włączone do corpus** jeśli spełnia WSZYSTKIE poniższe:

1. **Język:** polski (native, nie tłumaczenie maszynowe). EN-only excluded.
2. **Licencja:** open-access lub permitted-research-use — CC (BY/BY-NC/BY-SA/BY-NC-ND), public domain, urzędowe materiały (Art. 4 ustawy o prawie autorskim). Paywall excluded.
3. **Specjalizacja:** terminologia farmakologiczna (DCI nazwy międzynarodowe, kody ATC, łacińskie nazwy, terminologia farmakokinetyczna, mechanizmy działania, interakcje). Generic medical Wikipedia-level excluded.
4. **Scrapowalność:** dostępność programatyczna (API, OAI-PMH, predictable URL pattern, structured PDF). Manual-only download na żądanie excluded.
5. **Verifiability:** istnienie zweryfikowane przez web search w trakcie sources research R1+R2 (2026-05-15). Phantom/UNVERIFIED sources excluded.

### Exclusion criteria (kryteria wyłączenia)

Źródło **odrzucone z corpus** jeśli spełnia którekolwiek:

1. **Pay-wall / subscription** (Farmakopea Polska, Czasopismo Aptekarskie, większość Medycyna Praktyczna)
2. **Mostly English content** (Acta Poloniae Pharmaceutica — EN since 1974)
3. **Brak strukturalnego content** (forms reporting ADR — formularze, nie tekst)
4. **Cessation / unmaintained publisher** (Postępy Farmacji — publisher confirmed cessation)
5. **License ambiguity** (severe, gdy brak explicit OK na use w research thesis)
6. **Tabular-only data** (API Statystyki NFZ — raw tables, nie tekst do rerankera)

### Search strategy

Sources research wykonany w dwóch rundach (2026-05-15):

- **Round 1 (pharma broad, ~16 kandydatów):** URPL, AOTMiT, MZ, PTFarm journals, uczelnie medyczne (UMP/GUMed/WUM/CMUJ), Farmakopea Polska, Aptekarz Polski, Postępy Fitoterapii
- **Round 2 (Ulotki + NFZ + adjacencies, ~12 kandydatów):** URPL Ulotki, NFZ zarządzenia, NFZ komunikaty, MZ leki zagrożone dostępnością, URPL DHPC, pharmacovigilance forms

Każdy kandydat zwerifikowany przez ≥3 niezależne zapytania web search z polskojęzycznymi keywordami. Polish sources mogą być poorly indexed w english search engines — lenient evaluation z transparent flagging UNVERIFIED.

### Selection pipeline

```
Candidate sources identified (28 across 2 rounds)
       ↓
Web search verification (3+ queries per source, PL keywords)
       ↓
License check (explicit license OR urzędowe status)
       ↓
Scrape feasibility check (API / OAI-PMH / structured URL / parseable PDF)
       ↓
Content specialization check (pharma terminology presence)
       ↓
Final acceptance: 13 sources accepted / 6 rejected (paywall/EN/cessation) / 9 verified-but-not-included
```

### Final corpus composition

- **13 accepted sources** organized w 6 strata (zobacz tabele niżej)
- **6 explicitly rejected** (Farmakopea, Czasopismo Aptekarskie, Medycyna Praktyczna, Acta Poloniae Pharmaceutica jako PL-training source, Postępy Farmacji, API Statystyki NFZ jako corpus)
- **9 verified-but-not-included** (np. `dane.gov.pl` dataset 397 jako mirror RPL XML — dedup overhead; regional NFZ OW komunikaty — noisy duplicates centralnych; Czasopismo Aptekarskie subscription tylko fragments etc.)

### Świadome biases (do uznania w R3)

1. **License bias:** preferencja dla urzędowe + CC-permissive — szansa na underrepresentation komercyjnych źródeł zawierających specjalistyczne content (np. ChPL prywatnych producentów hosted on private sites — pomijane)
2. **ATC bias:** over-representation N05/N06 (psychiatria) w stratified sample ChPL — **świadoma decyzja** dla leverage'u manual validation kompetencji autorki (DEC-001 explicit uzasadnienie); konsekwencja w eval set (200 par gold standard psych subset)
3. **Recency bias:** OA czasopisma głównie ostatnie 10-12 lat (limit OA archive coverage); pre-2015 pharma content under-reprezentowany
4. **Polish-only bias:** EN-language pharma literature (mocniejsza globalnie) excluded — **świadoma decyzja**, bo praca jest o polskim rerankerze; flag w R8 limitations
5. **Source type bias:** silna preferencja dla regulatory (URPL + AOTMiT + MZ + NFZ ~66% korpusu) vs scientific (29%) — odzwierciedla wartość structural data dla rerankingu, ale niedoreprezentowuje state-of-the-art clinical research

### Update cadence

| Strata | Update frequency | Tracking field |
|---|---|---|
| URPL RPL XML (ChPL + Ulotki) | **daily** | `data_modyfikacji` |
| AOTMiT | **monthly** | ~200 raportów/rok |
| MZ obwieszczenia | **co 2 miesiące** | regularne cykle |
| NFZ zarządzenia | **as needed** | sporadyczne |
| OA czasopisma | **monthly** | per-journal issue |

Final corpus snapshot taken w Tygodniu 1-2 (12-25.05.2026); subsequent refresh w cyklach retreningu (cykl 2 — sierpień, cykl 3 — listopad).

### Reproducibility statement

Wszystkie scrape scripts będą w `main_project/src/ingest/` z explicit run commands. Każdy snapshot corpus snapshot timestamped i versioned przez DVC. Promotorzy/recenzenci mogą reprodukować corpus snapshot przez:
```
cd main_project
uv run python -m ingest.snapshot --date 2026-05-21  # przykład
dvc pull data/raw/corpus-2026-05-21.tar.zst
```

## Iteracja 0 — Feasibility pre-conditions

Przed pełnym scrape (Iteracja 1), Iteracja 0 musi zwerifikować **6 quantitative pre-conditions** dla głównego źródła (URPL ChPL/Ulotki). Każda ma threshold acceptance/rejection. **Jeśli ≥2 fail → DEC-001 kill criteria activated** → zatrzymanie scrape, re-evaluation per ADR (bez pre-committed fallback plan — decyzja na moment ewentualnej aktywacji).

| # | Pre-condition | Threshold acceptance | Metryka | Sample do testu |
|---|---|---|---|---|
| 1 | URPL RPL XML uptime | ≥99% w 24h test window | `requests.get().status_code == 200` probe co 1h | 24 probe requests |
| 2 | URPL XML feed parse-ability | 100% valid XML | `xml.etree.parse()` success bez exceptions | full daily snapshot |
| 3 | ChPL endpoint response time | <2s p95 | wall-clock difference per request | 100 random `productID` |
| 4 | Ulotka endpoint response time | <2s p95 | wall-clock difference per request | 100 random `productID` |
| 5 | **ChPL↔Ulotka alignment rate** | **≥90% par** | both endpoints return valid PDF + `data_modyfikacji` ±1 day | 100 random `productID` |
| 6 | OCR overhead (scanned PDFs) | <15% korpusu | text-layer detection — `pdfplumber.extract_text()` returns non-empty | 100 ChPL PDFs |

**Implementation note — pre-condition #1 (uptime SLA):** wymaga 24h time horizon — runs async w background (osobny skrypt `iter0_uptime_probe.py`, tick co 1h, append-only JSONL log). Wyniki review next-day; synchronous part Iteracji 0a (#2–#6) NIE czeka na ukończenie #1. Per Iteracja 0a split (konspekt II.16): phase 1 = synchronous probe (~4h), phase 2 = uptime results review (+24h).

**Dla Strata 3-5 (AOTMiT, NFZ, OA journals) — sample 50 dokumentów per source:**
- HTTP 200 response rate ≥95%
- Predictable URL structure (parseable bez manual intervention dla 90% dokumentów)
- License explicit (urzędowe Art. 4 lub CC) — verify w sample 10 dokumentów per source

**Output Iteracji 0:** `thesis_research/iteration-0-feasibility-report.md` z tabelą **Pre-condition × Result × Pass/Fail × Action**.

**Kill criteria DEC-001 activation:**
- ≥2 z 6 ChPL/Ulotka pre-conditions fail, **LUB**
- OCR overhead >25%, **LUB**
- Alignment rate <80%

**Warning bands (pre-condition fails ALE kill criteria NIE aktywuje):**
- **Alignment rate 80-89%:** methodology adjustment required. Action: tighten `data_modyfikacji` tolerance z ±1 day na 0 days, re-run pre-condition #5. Jeśli persisting <90% — escalate per DEC-001 manual review (nie automatyczny kill).
- **OCR overhead 15-24%:** korpus usable ale wymaga OCR pipeline. Action: add Tesseract `-l pol` do scrape pipeline, flag w R4 EDA + R8 limitations. Monitor jakość OCR post-Iteracja 1.
- **Pre-condition #3/#4 response time 2-5s p95:** usable ale slower scrape. Action: throttle scrape rate + retry/backoff, no kill.
- **1 z 6 pre-conditions fail (NIE ≥2):** single-case methodology adjustment, document w report z explicit rationale, no kill.

W razie kill activation: zatrzymanie scrape, krytyczna re-evaluation domeny per DEC-001 kill criteria section + opcja rotacji.

## Strata 1: Regulatory professional (ChPL)

| Pole | Wartość |
|---|---|
| Source | URPL Rejestr Produktów Leczniczych — ChPL |
| URL feed | `https://rejestry.ezdrowie.gov.pl/registry/rpl` (daily XML/XLSX/CSV) |
| URL API | `https://rejestrymedyczne.ezdrowie.gov.pl/api/rpl/medicinal-products/{ID}/...` |
| Content | Charakterystyka Produktu Leczniczego — standaryzowane 10 sekcji per lek |
| Skala | ~10-14k unikalnych PDF (multi-strength SKUs współdzielą ChPL) |
| Sample target | 900 (stratified by ATC class, N05/N06 over-represented) |
| Licencja | Public — urzędowe materiały, Art. 4 ust. 2 ustawy o prawie autorskim |
| Scraping | Medium — text-layer PDF dla większości; ~5-10% scanned (Tesseract `-l pol`) |
| Updates | Tracker `data_modyfikacji` z RPL XML — każdy lek może być reissued |

**Stratified sampling algorithm (900 leków z URPL universe ~10-14k):**

Cel: zrównoważyć (a) over-rep psychiatrycznej podgrupy dla leverage manual validation kompetencji autorki (DEC-001) z (b) szerokością farmakologiczną korpusu.

**Strategia:** 30% z N05/N06 ATC + 70% równowaga przez ATC Level 1 (14 broad classes: A/B/C/D/G/H/J/L/M/N/P/R/S/V).

```python
# main_project/src/ingest/sampling.py — pseudocode
import random

RANDOM_SEED = 42                # locked in configs/sampling.yaml
TARGET_TOTAL = 900
PSYCH_OVERREP_PROP = 0.30       # 30% z N05+N06

def stratified_sample(all_drugs):
    # Split do dwóch pul
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

    # Fill do TARGET_TOTAL jeśli niektóre classes < per_class (e.g. rare ATC P)
    remaining = TARGET_TOTAL - len(psych_sample) - len(other_sample)
    if remaining > 0:
        picked = {d.product_id for d in psych_sample + other_sample}
        extra_pool = [d for d in other_pool if d.product_id not in picked]
        other_sample.extend(random.sample(extra_pool, min(remaining, len(extra_pool))))

    return psych_sample + other_sample
```

**Reproducibility guarantees:**
- `RANDOM_SEED = 42` zafiksowane w `main_project/configs/sampling.yaml`
- Snapshot finalnej listy `productID` zapisany w `data/raw/sample-list-YYYY-MM-DD.csv` z DVC tracking
- Recenzent może odtworzyć identyczną próbę przez `dvc pull` + re-run scriptu

**Trade-off — equal-weight non-psych vs natural distribution:**
- ✅ **Wybór: equal-weight** — cel pracy = test rerankera na **diverse pharmaceutical domains**, nie real-world distribution simulation
- ❌ Natural-distribution sampling odtwarzałoby real pharmacy mix (over-rep C cardiovascular, under-rep V various), ale tracimy domain coverage diversity
- Decyzja explicit w R3 (Dane) jako świadomy methodological choice

**Bias acknowledgment (do R3 limitations):**
- N05/N06 over-rep 3× vs natural URPL rate (~10%)
- Rzadkie ATC classes (np. P antiparasitic, V various) mogą być pod-sampled jeśli ich populacja w URPL <45 leków
- Brand vs generic — sampling po `productID` traktuje je jako osobne, więc generic+brand tego samego DCI mogą oba trafić w próbę (no de-duplication na DCI level)

**Struktura ChPL (canonical 10 sekcji):**
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

**Mapping na training data:**
- **Direct query-passage:** sekcja header → body (np. *"Jakie są przeciwwskazania do bupropionu?"* → 4.3 body)
- **Hard negatives:** sekcja 4.3 leku A vs sekcja 4.5 leku A (ten sam lek, inna sekcja); sekcja 4.3 leku A vs sekcja 4.3 leku B (tej samej klasy ATC, inny lek)
- **Triplety preference learning:** (query, gold_passage, hard_negative) — naturalne
- **Scale:** 900 leków × 9 użytecznych sekcji = **~8100 natural pairs** bezpośrednio z headerów. Z LLM-generated paraphrased queries (Bielik few-shot) → 30-50k par.

## Strata 2: Regulatory consumer (Ulotki dla pacjenta) — paired z ChPL

| Pole | Wartość |
|---|---|
| Source | URPL Rejestr Produktów Leczniczych — Ulotka dla pacjenta |
| URL API | `https://rejestrymedyczne.ezdrowie.gov.pl/api/rpl/medicinal-products/{ID}/leaflet` |
| Content | Laypersonowski odpowiednik ChPL — QRD-aligned 6 sekcji |
| Skala | ~10-14k (1:1 z ChPL — każdy produkt ma obydwa dokumenty) |
| Sample target | 900 (paired z tymi samymi 900 ChPL ze Strata 1) |
| Licencja | Public — urzędowe materiały, Art. 4 |
| Scraping | Medium — text-layer PDF, mostly OCR-free |
| Updates | Synchronized z ChPL (ta sama decyzja administracyjna URPL) |

**Definicja "paired ChPL↔Ulotka":**

"Paired" w tym kontekście oznacza **dwa dokumenty z tej samej decyzji administracyjnej URPL** (tego samego pozwolenia na obrót), dla tej samej wersji leku, generowane przez tego samego MAH (Marketing Authorization Holder), zatwierdzone w ramach tego samego procesu rejestracji.

**Praktycznie:**
- Ten sam `productID` w RPL feed (jednoznaczny identyfikator decyzji)
- Synchronizowana `data_modyfikacji` (gdy ChPL zmienia się po update wskazań, Ulotka aktualizuje się równolegle w tym samym cyklu URPL)
- Ten sam zakres semantyczny (wskazania, dawkowanie, przeciwwskazania, działania niepożądane — opisane w obu dokumentach, w różnych rejestrach językowych)

**To NIE jest "paired":**
- ❌ Różne wersje czasowe tego samego leku (np. archiwalna ChPL 2020 + aktualna Ulotka 2024 — wymagamy najnowszej wersji obu z tego samego cyklu)
- ❌ Różne formy farmaceutyczne tego samego API (tabletki 50mg vs roztwór 100mg/ml — osobne `productID`)
- ❌ Generic + brand-name dla tego samego DCI (osobne decyzje administracyjne, osobne `productID`)

**Sprawdzanie pairing integrity** w Iteracji 0a (alignment validation, 100 sample leków):
1. `productID` resolution działa dla obu endpoints (`/medicinal-products/{ID}/leaflet` i parallel ChPL endpoint)
2. `data_modyfikacji` identyczna lub w obrębie ±1 day tolerance
3. ChPL sekcja 4.1 (Wskazania) i Ulotka sekcja 1 (Co to jest lek X) opisują tę samą indykację — **competence-stratified manual spot-check**:
   - 10/10 par **wybranych z psych subset N05/N06** (autorka ma semantic competence dla tej podgrupy ATC — patrz DEC-001 uzasadnienie eval set design)
   - Pozostałe 90/100 par non-psych: tylko proxy signal (productID match + `data_modyfikacji` ±1 day), **bez semantic verification** — limitation flagged explicit w R3 § 3.9 "Świadome biases" + R8 limitations

**Acceptance threshold:** ≥90% par z pełnym pairing integrity. Poniżej tego progu → DEC-001 kill criteria activated.

**Struktura Ulotki (QRD-aligned 6 sekcji):**
1. Co to jest lek X i w jakim celu się go stosuje
2. Informacje ważne przed przyjęciem/zastosowaniem leku X
3. Jak przyjmować/stosować lek X
4. Możliwe działania niepożądane
5. Jak przechowywać lek X
6. Zawartość opakowania i inne informacje (skład, podmiot odpowiedzialny, wytwórca, data ostatniej aktualizacji)

**Mapping na training data — STRATEGIC:**
- **Same-register pairs:** sekcja Ulotki header → body (jak ChPL)
- **CROSS-REGISTER pairs (kluczowe dla RQ5):**
  - Lay query (z Ulotki) → Professional answer (z ChPL): *"Co zrobić jak zapomniałem o dawce?"* (Ulotka 3) → ChPL 4.2 Dawkowanie body
  - Professional query (z ChPL) → Lay answer (z Ulotka): *"Dawkowanie X u pacjentów z niewydolnością nerek"* → Ulotka 3 body (gdzie jest powiedziane "jeśli masz problemy z nerkami, lekarz może zmienić dawkę")
- **Alignment deterministyczny przez `productID`** — zero cost manualnej anotacji
- **Scale:** 900 paired × 6 cross-register pair types per drug ≈ **5400 cross-register pairs** dla RQ5 eval set

## Strata 3: HTA + refundation legal

### 3a. AOTMiT (Agencja Oceny Technologii Medycznych i Taryfikacji)

| Pole | Wartość |
|---|---|
| URL current | `https://bip.aotm.gov.pl/` |
| URL archive | `https://bipold.aotm.gov.pl/assets/files/zlecenia_mz/YYYY/NNN/REK/*.pdf` |
| Content | HTA reports, rekomendacje Prezesa, raporty taryfikacyjne |
| Skala | ~2000+ PDF od 2012, ~200/rok dodawanych |
| Sample target | ~300 raportów (mix specialty classes) |
| Licencja | Public — BIP urzędowy |
| Scraping | Medium — split URL (current CMS vs legacy asset host) |

**Mapping training data:** Każdy raport ma named sections: *Problem decyzyjny / Skuteczność kliniczna / Bezpieczeństwo / Analiza ekonomiczna / Wpływ na budżet / Rekomendacje innych agencji*. Section→body pairs. ~300 × 5 sekcji = ~1500 par.

### 3b. MZ obwieszczenia + programy lekowe B.xx

| Pole | Wartość |
|---|---|
| URL | `https://www.gov.pl/web/zdrowie/obwieszczenia-ministra-zdrowia-lista-lekow-refundowanych` |
| URL Dziennik MZ | `https://dziennikmz.mz.gov.pl/` |
| Content | Refundation lists + ~120 programów lekowych B.xx |
| Skala | ~120 aktywnych programów; obwieszczenia co 2 miesiące |
| Sample target | ~400 dokumentów (programy + ostatnie 30 obwieszczeń) |
| Licencja | Public — akty prawne, Art. 4 |
| Scraping | Low-Medium — predictable URL |

**Mapping training data:** Programy lekowe są mini-spec per indication. *"Kryteria włączenia do programu B.X"* → body; *"Schemat dawkowania w programie X"* → body. ~120 × 6 sekcji = ~700 par wysokiej jakości clinical-decision phrasing.

**Total Strata 3:** ~700 dokumentów, ~2200 natural pairs.

## Strata 4: Refundation operational (NFZ)

| Source | URL | Content | Skala | Scrape |
|---|---|---|---|---|
| **🥇 Zarządzenia Prezesa NFZ** | `https://www.nfz.gov.pl/zarzadzenia-prezesa/zarzadzenia-prezesa-nfz/` | **Operacjonalizacja programów lekowych** — ICD-10, kryteria kwalifikacji, schemat dawkowania, badania monitorujące, katalog ryczałtów | Setki w archiwum, ~kilkadziesiąt/rok | HTML index + PDF attachments, predictable URL |
| BIP NFZ komunikaty | `https://www.nfz.gov.pl/bip/komunikaty/` | Centralne komunikaty | ~10s/rok | HTML, predictable pattern |
| NFZ dla lekarzy | `https://www.nfz.gov.pl/dla-lekarzy/komunikaty/` | Clinical guidance, programs ops | ~50-150/rok | HTML |
| ~~Komunikaty dla świadczeniodawców (16 OW)~~ | regional sites | Billing, drug programs, shortages | high noise | SKIP — noisy duplicates |
| ~~API Statystyki NFZ~~ | `dane.gov.pl/dataset/1601 + 1676` | Tabular drug data | live API | SKIP as corpus, use as metadata only |

**Sample target:** ~400 dokumentów (głównie Zarządzenia Prezesa NFZ programy lekowe + selected BIP).

**Licencja:** Public — urzędowe (Art. 4).

**Mapping training data:** Zarządzenia mają **operational sections** różne od MZ obwieszczeń: *"Wymagane badania monitorujące"*, *"Zasady billing programu"*, *"Wyłączenia z programu"*. To inny query type niż legal (MZ) i medical (AOTMiT). Total Strata 4: ~700 par.

## Strata 5: Open-access PL journals

| Source | URL | Licencja | Skala | Per year |
|---|---|---|---|---|
| **Farmacja Polska (PTFarm)** | `https://www.ptfarm.pl/en/wydawnictwa/czasopisma/farmacja-polska/` + `bibliotekanauki.pl/journals/1109` mirror | **CC BY-NC 4.0** | ~700-1000 artykułów (10 lat OA) | ~70-100 |
| **Lek w Polsce (Medyk)** | `https://lekwpolsce.pl/` + Biblioteka Cyfrowa UŁ mirror | **CC BY-NC-ND 4.0** | ~1000+ artykułów (archiwum od 1991) | ~120+ |
| **AAMS (Annales Academiae Medicae Silesiensis)** | `https://annales.sum.edu.pl/` + DOAJ | **CC BY-SA 4.0** (najpermisywniejsza) | ~60-80/rok OA od 2021 | ~60-80 |
| **CIPMS (UM Lublin)** | `https://czasopisma.umlub.pl/curipms` + Sciendo JATS XML | **CC BY-NC-ND** | ~500-700 artykułów (12 lat) | ~40-60 |
| ~~Acta Poloniae Pharmaceutica~~ | `https://www.ptfarm.pl/.../acta-poloniae-pharmaceutica/` | CC BY-NC | ~3000+ artykułów | ~EN-only since 1974 — **SKIP** dla PL training |

**Sample target:** ~900 artykułów PL-language (mix wszystkich 4 active journals).

**Scrape methods:**
- **Farmacja Polska:** OAI-PMH przez ICM UW (`bibliotekanauki.pl`) — preferowane nad direct PTFarm
- **Lek w Polsce:** Biblioteka Cyfrowa UŁ dLibra (OAI-PMH, IIIF available)
- **AAMS:** OJS / DOAJ (clean XML/JATS)
- **CIPMS:** OJS / Sciendo JATS XML

**Mapping training data:** Article structure (Wstęp / Metody / Wyniki / Dyskusja). Heading-based chunking. Title+abstract → body pairs. **Review articles dominują** — good query diversity. ~900 × ~3 useful sections = ~2700 par.

## Strata 6: Adjacencies (bonus)

| Source | URL | Content | Skala | Licencja |
|---|---|---|---|---|
| **URPL Komunikaty bezpieczeństwa (DHPC)** | `https://www.gov.pl/web/urpl/komunikaty-bezpieczenstwa` | Dear Doctor letters, EMA-coordinated safety updates | ~30-80/rok | Urzędowe |
| **MZ Lista leków zagrożonych brakiem dostępności** | `https://dziennikmz.mz.gov.pl/keywords/55` | Drug shortage announcements (lista co ~2 mies.) | ~30 historycznych obwieszczeń | Urzędowe |
| ~~Pharmacovigilance reporting forms ADR~~ | URPL section | NOT text content (forms) | n/a | SKIP |

**Sample target:** ~300 dokumentów (większość DHPC + selected shortage lists).

**Mapping training data:** DHPC są krótkie, focused alerty — natural query: *"Czy są nowe ostrzeżenia dla leku X?"* → DHPC body. ~300 par.

## Łączny szacunek

| Strata | ~docs | % korpusu | Natural pairs (header→body) | Z LLM paraphrasing |
|---|---|---|---|---|
| 1. ChPL | 900 | 22% | ~8,100 | ~30-50k |
| 2. Ulotki (paired) | 900 | 22% | ~5,400 | ~20-30k + **5,400 cross-register** |
| 3. AOTMiT + MZ | 700 | 17% | ~2,200 | ~10k |
| 4. NFZ operational | 400 | 10% | ~1,500 | ~6k |
| 5. OA PL journals | 900 | 22% | ~2,700 | ~10k |
| 6. Adjacencies | 300 | 7% | ~300 | ~1k |
| **TOTAL** | **~4,100** | **100%** | **~20,200** | **~80-100k + 5.4k cross-register** |

## Sources rejected (paywall / scope)

| Source | Powód odrzucenia |
|---|---|
| **Farmakopea Polska XII/XIII** | Odpłatna prenumerata (COGNO MEDICAL) |
| **Czasopismo Aptekarskie** | Subscription-only |
| **Medycyna Praktyczna / Indeks leków MP** | Mostly paywalled, no CC |
| **Polski Przegląd Farmaceutyczny** | UNVERIFIED — nazwa plausible ale brak ewidencji online; możliwa konflagracja z Farmaceutyczny Przegląd Naukowy (subscription) |
| **Postępy Farmacji / Postępy Farmakoterapii** | Publisher confirmed cessation; legacy archive minimalny |
| **Acta Poloniae Pharmaceutica (EN content)** | PL training value niska — publikuje EN od 1974 |
| **API Statystyki NFZ (Refundacja Apteczna + Programy Lekowe)** | Tabular data, nie text corpus — używać jako metadata only |

## Implementation notes / gotchas

1. **Stare ChPL** (pre-2010) ~5-10% są scanned → Tesseract `-l pol` w pipeline. Bypass: filter scanned z RPL XML metadata jeśli pole jest dostępne, lub na podstawie OCR confidence.
2. **ChPL updates** — RPL XML daje *current* per produkt; track `data_modyfikacji` żeby nie mieć duplikatów wersji.
3. **AOTMiT split URL** — `bip.aotm.gov.pl` (new CMS) vs `bipold.aotm.gov.pl/assets/...` (legacy gdzie siedzą realne PDF-y). Follow redirects.
4. **Polskie diakrytyki** — czasem ChPL droppuje ą/ę encoding; normalize `unicodedata.normalize('NFC', ...)` post-extraction.
5. **`dane.gov.pl` dataset 397** to mirror RPL XML — wybierz jedno źródło, **NIE scrape'uj obu**.
6. **NFZ Zarządzenia Prezesa** — split na centrala vs 16 oddziałów wojewódzkich. **Skip OW komunikaty** (high noise, duplicate central content).
7. **Aptekarz Polski (NIA)** — licencja explicit nie podana (free downloadable). OK do research-internal, ale flag "nieredystrybuowalne" w R3.
8. **Postępy Fitoterapii (Borgis)** — licencja unclear. Niche (fitoterapia), wartościowe dla interakcji V03/N05. Treat z ostrożnością.
9. **Bielik/PLLuM tokenizery** handluje polskie diakrytyki — sprawdź proporcję dziwnych unicode w sample 100 ChPL przed scrape.
10. **Bibliotekanauki.pl** vs PTFarm direct — preferuj OAI-PMH (cleaner XML).

## Linki źródłowe (do cytowania w R3)

- [URPL RPL XML feed](https://rejestry.ezdrowie.gov.pl/registry/rpl)
- [URPL RPL search public UI](https://rejestry.ezdrowie.gov.pl/rpl/search/public)
- [URPL leaflet API endpoint example](https://rejestrymedyczne.ezdrowie.gov.pl/api/rpl/medicinal-products/39257/leaflet)
- [RPL na dane.gov.pl (mirror — skip)](https://dane.gov.pl/pl/dataset/397,rejestr-produktow-leczniczych)
- [BIP AOTMiT (current)](https://bip.aotm.gov.pl/)
- [BIPold AOTMiT (asset archive)](https://bipold.aotm.gov.pl/)
- [MZ obwieszczenia leków refundowanych](https://www.gov.pl/web/zdrowie/obwieszczenia-ministra-zdrowia-lista-lekow-refundowanych)
- [Dziennik Urzędowy MZ](https://dziennikmz.mz.gov.pl/)
- [NFZ Zarządzenia Prezesa](https://www.nfz.gov.pl/zarzadzenia-prezesa/zarzadzenia-prezesa-nfz/)
- [NFZ BIP komunikaty](https://www.nfz.gov.pl/bip/komunikaty/)
- [Farmacja Polska PTFarm](https://www.ptfarm.pl/en/wydawnictwa/czasopisma/farmacja-polska/) + [bibliotekanauki.pl mirror](https://bibliotekanauki.pl/journals/1109)
- [Lek w Polsce (Medyk)](https://lekwpolsce.pl/) + [Biblioteka Cyfrowa UŁ mirror](https://bcul.lib.uni.lodz.pl/)
- [AAMS](https://annales.sum.edu.pl/) + [DOAJ ToC](https://doaj.org/toc/1734-025X)
- [CIPMS UM Lublin](https://czasopisma.umlub.pl/curipms) + [DOAJ ToC](https://doaj.org/toc/2300-6676)
- [URPL komunikaty bezpieczeństwa (DHPC)](https://www.gov.pl/web/urpl/komunikaty-bezpieczenstwa)
- [Dziennik MZ — lista leków zagrożonych dostępnością](https://dziennikmz.mz.gov.pl/keywords/55)
- [Art. 4 ustawy o prawie autorskim — wyłączenie ochrony urzędowych](https://arslege.pl/wylaczenie-ochrony-prawa-autorskiego/k442/a36714/)
- [Grabowski 2017 EN-PL PIL corpus (closest prior art)](https://benjamins.com/catalog/cilt.341.09gra)
