# Iteracja 0a — Feasibility Report

**Status:** **Phase 1 COMPLETED** (synchronous probe) | Phase 2 pending (24h uptime probe — needs to be started)
**Date run:** 2026-05-16
**Author:** Magdalena Sochacka
**Domain:** farmakologia kliniczna (po DEC-001 rotacji)
**Related ADRs:** [DEC-001](../decisions/DEC-001_wybor-domeny.md), [DEC-002](../decisions/DEC-002_chpl-ulotka-pairing.md)
**Source of truth:** [`sources_catalog.md`](../sources_catalog.md) § Iteracja 0 — Feasibility pre-conditions
**Konspekt reference:** [`02b_konspekt_v3_updates.md`](../02b_konspekt_v3_updates.md) § II.16 Iteracja 0a

---

## Streszczenie

Phase 1 feasibility probe (synchronous, pre-conditions #2-#6) zakończony **4/5 PASS, 1 WARN**, **kill criteria NOT activated**. Probowano 100 random productIDs z effective scrape pool 12,973 complete-pair produktów (URPL universe 22,750 → filter complete pair ChPL+Ulotka URL + ATC code, retention 57%). Endpoint response times w pełni przekroczyły threshold success (ChPL p95 0.687s, Ulotka p95 0.528s vs threshold <2s). Alignment rate 100% na complete-pair pool — paired URLs strukturalnie aligned przez URPL XML metadata. OCR overhead 17% w warning band 15-24% (kill >25% nie activated) — wymaga Tesseract `-l pol` w scrape pipeline + flag w R4 EDA + R8 limitations. **Decyzja: PROCEED do Iteracji 0b (judge pilot selection) z methodology adjustment OCR pipeline.**

Phase 2 (URPL uptime 24h SLA, pre-condition #1) — do uruchomienia jako background script.

---

## Pre-conditions results

| # | Pre-condition | Threshold | Result | Pass/Warn/Fail | Action |
|---|---|---|---|---|---|
| 1 | URPL RPL XML uptime ≥99% w 24h | 24 probes co 1h, status_code == 200 | **TBD — phase 2 background** | TBD | Uruchom `iter0_uptime_probe.py` w background |
| 2 | URPL XML feed parse-ability | 100% valid (xml.etree, no exceptions) | True (22,750 entries parsed) | ✅ PASS | — |
| 3 | ChPL endpoint response time p95 | <2s (warn band 2-5s) | **0.687s** (p50 0.442s) | ✅ PASS | — |
| 4 | Ulotka endpoint response time p95 | <2s (warn band 2-5s) | **0.528s** (p50 0.425s) | ✅ PASS | — |
| 5 | ChPL↔Ulotka alignment rate | ≥90% (warn band 80-89%, kill <80%) | **100.0%** (na filtered complete-pair pool) | ✅ PASS | URL-e z XML metadata; HTTP Last-Modified header NIE dostępny (server nie ustawia) — 100/100 date check SKIPPED, fallback na status+pdf working as designed |
| 6 | OCR overhead (scanned PDFs) | <15% (warn band 15-24%, kill >25%) | **17.0%** (text-layer rate 83%) | ⚠ WARN | Add Tesseract `-l pol` w scrape pipeline (Iter. 1); flag w R4 EDA + R8 § 8.4.1 |

**Warning bands triggered:** 1 (pre-condition #6 OCR overhead 17% w warn band 15-24%; pipeline methodology adjustment per `sources_catalog.md` § Warning bands)

**Kill criteria check:** **NOT ACTIVATED**
- 0 z 5 phase-1 pre-conditions FAIL (próg ≥2 → kill)
- OCR overhead 17% < 25% kill threshold
- Alignment 100% > 80% kill threshold

---

## Sample details

- **URPL universe (XML total):** **22,750** produktów (snapshot stanNaDzien=2026-05-15, RPL v6.0.0)
- **Filtered effective pool (complete pair: ChPL+Ulotka URL + ATC code):** **12,973** (57% retention)
  - Excluded no-URL (EU-centralized via EMA / legacy nie-digitalized): 9,469 (42%)
  - Excluded no-ATC (zioła, gazy medyczne, special preparations): 1,148 (5%)
- **Random sample size:** **100** (seed=42, locked w `configs/sampling.yaml`)
- **Psych subset spot-check sample:** **10** (ATC N05/N06, dla competence-stratified manual review)
- **Sample list snapshot:** [`sample-list-2026-05-16.csv`](sample-list-2026-05-16.csv) — DVC tracked
- **Spot-check list:** [`spot-check-psych-N05N06-2026-05-16.csv`](spot-check-psych-N05N06-2026-05-16.csv)

### ATC distribution w sample 100

| ATC Level 1 | Count | % | Comment |
|---|---|---|---|
| A — Alimentary tract and metabolism | 11 | 11% | |
| B — Blood and blood forming organs | 9 | 9% | |
| C — Cardiovascular system | 12 | 12% | dominant w naturalnym sample |
| D — Dermatologicals | 3 | 3% | |
| G — Genito-urinary system | 5 | 5% | |
| H — Systemic hormones | 1 | 1% | under-sample |
| J — Anti-infectives | 5 | 5% | |
| L — Antineoplastic | 10 | 10% | |
| M — Musculo-skeletal | 3 | 3% | |
| **N — Nervous system (incl. N05/N06)** | **18** | **18%** | **10/18 = N05/N06 psych subset** (over-sample tutaj naturalny per seed) |
| Q — Veterinary | 9 | 9% | **flag: veterinary products w URPL feed** — rozważ filter w Iter. 1 corpus design |
| R — Respiratory | 8 | 8% | |
| V — Various | 6 | 6% | rare ATC |
| S — Sensory organs | `{}` | `{}` | |
| V — Various | `{}` | `{}` | rare ATC |

---

## Manual spot-check results (10 par psych N05/N06)

**Methodology** (per `sources_catalog.md` § Strata 2 "Sprawdzanie pairing integrity", competence-stratified): autorka semantycznie porównuje ChPL sekcja 4.1 (Wskazania) vs Ulotka sekcja 1 (Co to jest lek X) — czy opisują tę samą indykację?

| # | productID | Lek (DCI/Brand) | ATC | Alignment OK? | Notes |
|---|---|---|---|---|---|
| 1 | `{}` | `{}` | N05/N06 | `{yes/no}` | `{}` |
| 2 | `{}` | `{}` | | `{}` | `{}` |
| 3 | `{}` | `{}` | | `{}` | `{}` |
| 4 | `{}` | `{}` | | `{}` | `{}` |
| 5 | `{}` | `{}` | | `{}` | `{}` |
| 6 | `{}` | `{}` | | `{}` | `{}` |
| 7 | `{}` | `{}` | | `{}` | `{}` |
| 8 | `{}` | `{}` | | `{}` | `{}` |
| 9 | `{}` | `{}` | | `{}` | `{}` |
| 10 | `{}` | `{}` | | `{}` | `{}` |

**Manual spot-check rate:** `{X}/10 — PENDING Magda's manual review` (10 par psych N05/N06 z `spot-check-psych-N05N06-2026-05-16.csv`).

**Non-psych proxy signal validation (90 par sample):** alignment_ok rate w skrypcie = **100.0%** (100/100 par na complete-pair filtered pool), bez semantic verification — limitation flagged w R3 § 3.9 Świadome biases + R8 limitations (sources_catalog.md § Strata 2 explicit).

---

## XML schema (RPL v6.0.0 — confirmed 2026-05-15)

- **Namespace:** `http://rejestry.ezdrowie.gov.pl/rpl/eksport-danych-v6.0.0`
- **Root:** `<produktyLecznicze stanNaDzien="YYYY-MM-DD">` — `stanNaDzien` to **snapshot date całego feeda**, NIE per-product
- **Per-product:** `<produktLeczniczy id="..." nazwaProduktu="..." nazwaPowszechnieStosowana="..." numerPozwolenia="..." charakterystyka="<URL>" ulotka="<URL>" ...>` (atrybuty)
- **ATC codes:** zagnieżdżone `<kodyATC><kodATC>X01XX01</kodATC></kodyATC>` (multiple kodATC możliwe per produkt — używamy `[0]` dla stratification)
- **Direct URLs w XML:** `charakterystyka` (ChPL) i `ulotka` (Ulotka) jako attributes — używamy bezpośrednio, NIE template
- **`id` attribute (np. `100000014`) ≠ ID w URL** (np. `/medicinal-products/1/leaflet`) — sequential URL counter osobny od internal product ID

Per-product `data_modyfikacji` **NIE istnieje** w feed XML. Konsekwencja dla pre-condition #5: alignment date check via HTTP `Last-Modified` header (supplemental), fallback na "both endpoints OK + valid PDF".

API gotcha: requests bez header `Accept: application/xml, text/xml, */*` zwracają `BIND_VALIDATION_ERROR` JSON. Skrypt `iter0_urpl_probe.py` ma to ustawione w `DEFAULT_HEADERS`.

---

## Implementation notes / gotchas observed (2026-05-16 phase 1 run)

- **Tesseract OCR potrzebny dla ~17% PDFs** (warn band 15-24%): text-layer rate 83% na 100 sample → 17/100 ChPL PDFs są scanned (pdfplumber.extract_text zwraca pusty string lub <100 znaków). Language pack: `-l pol`. Iter. 1 corpus scrape musi mieć Tesseract w pipeline jako fallback dla scanned PDFs.
- **`data_modyfikacji` Ulotki NIE w XML metadata** — XML feed ma snapshot-level `stanNaDzien` (single value dla całego feed), per-product `data_modyfikacji` nie istnieje. **HTTP `Last-Modified` header też NIE dostępny** (100/100 probes — server nie ustawia). Konsekwencja: alignment via URL pair existence + valid PDFs (semantic equivalence by URPL workflow construction).
- **Encoding NFC:** sample probe nie testował (probe nie ekstraktuje pełnego tekstu, tylko detection 100 znaków na first 3 stronach). Per `sources_catalog.md` § Implementation note #4: pre-2015 ChPL droppuje ą/ę encoding; Iter. 1 musi mieć `unicodedata.normalize('NFC', text)` w pipeline post-extraction.
- **Throttling NIE zaobserwowane:** 100 sequential GET-y w ~50s, brak 429/503. Ale dla Iter. 1 (900 par × 2 endpointów = 1800 GET-y) zalecane throttling + retry/backoff jako defensive measure.
- **ChPL endpoint URL pattern CONFIRMED:** atrybut `charakterystyka` w XML zawiera direct URL z suffixem `/characteristic` (NIE `/chpl` ani `/spc`). Hostname `rejestry.ezdrowie.gov.pl` (NIE `rejestrymedyczne` — errata fix w `sources_catalog.md`).
- **NEW FINDING — Veterinary products w URPL feed:** ~9% sample miało ATC prefix `Q` (veterinary, np. QJ01AA02 Doxi SP). Filter decision dla Iter. 1: include lub exclude `Q` codes? Recommend: exclude jeśli scope = human pharmacy; include jeśli scope = pharmaceutical retrieval broadly. **Należy rozstrzygnąć przed Iter. 1 corpus scrape** (sources_catalog.md update wymagany).
- **NEW FINDING — Effective scrape pool 12,973 vs URPL universe 22,750:** 42% produktów nie ma digital ChPL/Ulotka URL (EU centralized procedure rejestrowane przez EMA, stare nie-zdigitalizowane). Sample target 900 leków z 12,973 effective pool = **7% pokrycia** — komfortowy headroom.

---

## Decision

**(B) PROCEED z methodology adjustments.** Pre-condition #6 (OCR overhead 17%) w warning band 15-24% — applied adjustment: **add Tesseract `-l pol` do scrape pipeline w Iter. 1**, flag w R4 EDA + R8 § 8.4.1 limitations.

Pozostałe 4 pre-conditions phase-1 (#2-#5) ✅ PASS bez adjustments. Pre-condition #1 (24h uptime SLA) — phase 2 background, do uruchomienia. Kill criteria NOT activated.

---

## Następne kroki

1. **Uruchom phase 2 uptime probe** (`iter0_uptime_probe.py`) w background — 24h SLA test dla pre-condition #1. Wyniki review dnia 2026-05-17.
2. **Manual spot-check 10 par psych N05/N06** z `spot-check-psych-N05N06-2026-05-16.csv` — autorka semantycznie porównuje ChPL sekcja 4.1 vs Ulotka sekcja 1 dla 10 par (competence-stratified per `sources_catalog.md` § Strata 2 pkt 3). Update tabeli powyżej.
3. **Decyzja dla Iter. 1 corpus design:** veterinary `Q` codes IN lub OUT scope? Update `sources_catalog.md` § Strata 1 z explicit filter logic + Stratified sampling algorithm update jeśli zmiana.
4. **Po complete pre-condition #1 PASS:** PROCEED do **Iteracji 0b** (judge pilot selection per `02b_konspekt_v3_updates.md` § II.16).

---

## Artefakty

| Plik | Opis | Track |
|---|---|---|
| `results.json` | pełne metryki + per-product per-endpoint results | DVC |
| `sample-list-{date}.csv` | 100 random productID sample | DVC |
| `spot-check-psych-N05N06-{date}.csv` | 10 psych pair (manual review) | DVC |
| `rpl-snapshot-{date}.xml` | URPL XML download (input) | DVC |
| `uptime.jsonl` | phase 2 background probe log | DVC (append-only) |
| `uptime.summary.json` | pre-condition #1 aggregate | DVC |

---

## Cross-references

- Po passing 0a → proceed Iteracja 0b (`02b_konspekt_v3_updates.md` § II.16 Iteracja 0b)
- Po passing 0a+0b → Iteracja 1 (full corpus scrape ~4100 docs, EDA, 200 par gold standard)
- Po activation kill criteria → krytyczna re-evaluation per `DEC-001_wybor-domeny.md` § Kill criteria
