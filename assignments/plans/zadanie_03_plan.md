# Plan zadania 03 — Dane (R3 Data Types and Documentation)

**Institutional source:** `assignments/03.md` (Task 03, 10 pkt)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/05-Data-Preparation-and-Exploratory-Data-Analysis.md` (Assignment 5, częściowe pokrycie data structure)
**Mapuje na rozdział:** R3 Dane
**Iteracja realizacji:** 1 (corpus scrape + 200 par gold standard) + 7 (writing)

## 1. Czego instytucjonalnie wymaga Task 03

Dla każdego typu danych dokumentacja:
- Struktura folderów (data/raw/, data/processed/, data/docs/)
- Naming conventions
- Versioning (raw read-only)
- Metadata + codebooks
- Ethics + licensing
- Reproducibility (scripts)
- Tables/figures referenced w text

Task wymienia 6 modalności (tabular/text/image/audio/video/etc.) — w naszej pracy używamy **tylko text + tabular**, świadomie wyłączamy pozostałe.

## 2. Czego wymaga PRO-D-THESIS Assignment 5 (data prep część)

- **A. Dataset Structure and Integrity** — formal description
- **B. Statistical Characterization** — descriptive stats
- **C. Correlation/Dependency** — dla relevantnych przypadków
- **D. Outlier and Noise Assessment**
- **E. Bias and Limitation Analysis**
- **F. Implications for Experimental Design**

(A, E, F głównie do R3; B, C, D do R4 EDA — patrz `zadanie_04_plan.md`)

## 3. Jak to wygląda w naszym v3.1

### Sekcja 3.1: Modalności danych

**Single source of truth:** `thesis_research/sources_catalog.md` (skopiować strukturę 6 strata).

> *„Niniejsza praca operuje na danych **tekstowych** (regulatorowe + naukowe dokumenty farmakologiczne) i **tabularnych** (metryki ewaluacji, logi eksperymentalne, metadata corpus). Pozostałe modalności (image, audio, video) pozostają poza zakresem ze względu na charakter problemu retrievalu tekstowego."*

### Sekcja 3.2: Metodologia doboru źródeł

**Skopiować bezpośrednio** z `sources_catalog.md` sekcja "Source selection methodology":
- Inclusion criteria (5 kryteriów)
- Exclusion criteria (6 powodów)
- Search strategy (R1 + R2 sources research)
- Selection pipeline
- Final corpus composition (13 accepted / 6 rejected / 9 verified-but-not-included)

⚠ Promotor v1 6/10 wytknął "brak rygorystycznej metodologii" — **tu się to ratuje explicit**.

### Sekcja 3.3: 6 strata szczegółowo

Dla każdej strata (z `sources_catalog.md`):
- Źródło + URL
- Licencja (urzędowe Art. 4 vs CC) — license audit
- Skala + sample size
- Scrape method
- Mapping na training data dla rerankera

| Strata | % korpusu | Skala | Mapping |
|---|---|---|---|
| 1 ChPL | 22% | 900 | 8100 natural section pairs |
| 2 Ulotki (paired) | 22% | 900 | 5400 cross-register pairs |
| 3 HTA + MZ | 17% | 700 | 2200 section pairs |
| 4 NFZ operational | 10% | 400 | 1500 section pairs |
| 5 OA PL journals | 22% | 900 | 2700 section pairs |
| 6 Adjacencies | 7% | 300 | 300 doc-level pairs |
| **TOTAL** | 100% | ~4100 | ~20k natural / ~145k z hard negatives |

### Sekcja 3.4: ChPL↔Ulotka pairing

**Skopiować z `sources_catalog.md` Strata 2** sekcję "Definicja paired ChPL↔Ulotka":
- Co znaczy "paired" (3 punkty)
- Co NIE znaczy "paired" (3 punkty)
- Pairing integrity validation (Iteracja 0 procedura)

### Sekcja 3.5: Stratified sampling algorithm

**Skopiować z `sources_catalog.md` Strata 1** sekcję "Stratified sampling algorithm":
- Python pseudocode (RANDOM_SEED=42)
- Trade-off equal-weight vs natural distribution
- Bias acknowledgment

### Sekcja 3.6: Codebooks per strata

Per source — codebook w formie tabeli:
- Field name
- Type (string/int/date/categorical)
- Meaning
- Allowed values
- Source provenance
- License notes

Codebooks zapisywane w `data/docs/codebook_<strata>.md`, referenced w R3.

### Sekcja 3.7: Ethics + licensing

- Wszystkie regulatorowe (URPL/AOTMiT/MZ/NFZ) — urzędowe materiały, Art. 4 ustawy o prawie autorskim
- CC journals — explicit license per source
- DHPC, MZ braki list — urzędowe
- **Brak danych osobowych** — praca operuje na regulatorowych dokumentach publicznie dostępnych
- Brak komitetu etycznego required (nie ma badań z udziałem ludzi)

### Sekcja 3.8: Reproducibility statement

**Skopiować z `sources_catalog.md`** sekcję "Reproducibility statement":
- Scrape scripts w `main_project/src/ingest/`
- DVC versioning
- Snapshot command example
- RANDOM_SEED locked w configs

### Sekcja 3.9: Świadome biases (do limitations)

**Skopiować z `sources_catalog.md`** sekcję "Świadome biases" — 5 typów:
1. License bias
2. ATC bias (N05/N06 over-rep 30% vs natural ~10%)
3. Recency bias (OA ~10-12 lat)
4. Polish-only bias
5. Source type bias (regulatory 66% vs scientific 29%)

## 4. Co musimy znaleźć / przygotować

### Cytacje
- License laws (Art. 4 ustawy o prawie autorskim — link)
- 4 CC journal license references
- Polish medical regulatory framework (URPL/AOTMiT — krótki opis)

### Artefakty (tabele i figury)
- **Tab. 3.1:** 6 strata × 5 attributów (skala, licencja, scrape, % korpusu, mapping)
- **Tab. 3.2:** Codebook ChPL (przykład, full w appendix)
- **Tab. 3.3:** Codebook Ulotki (przykład, full w appendix)
- **Tab. 3.4:** License audit per strata
- **Fig. 3.1:** ATC class distribution w sampled corpus (bar chart)
- **Fig. 3.2:** ChPL↔Ulotka pairing diagram (paired structure)
- **Algorithm 3.1:** Stratified sampling pseudocode

### Pre-conditions z Iteracji 1
- ✅ Corpus scraped + indexed
- ✅ EDA report wygenerowany
- ✅ License audit per source completed
- ✅ Codebooks utworzone
- ✅ 200 par gold standard manualnie ranked (psych subset)

## 5. Writing rules application

- **Source selection methodology explicit** w 3.2 (CRITICAL z promotor v1 feedback)
- Konsystentne tabele
- Evidence-to-conclusion w sekcji 3.9 biases

## 6. Defense scaffolding application

- **Świadome biases (5 typów)** explicit w R3 → przygotowuje grunt pod R8 limitations sekcję
- **Eval set z psych subset** — uzasadnienie *"leverage manual validation kompetencji autorki w psychiatrycznej podgrupie ATC N05/N06"* — wprowadza Defense pkt 3 (negative-result framing): nawet jeśli H1 odpada, H2 (judge kappa walidowane przeciw twardym manual labels) stoi niezależnie

## 7. Acceptance checklist

- [ ] Sekcja 3.1 explicit deklaruje text+tabular only, pozostałe out of scope
- [ ] Sekcja 3.2 Source selection methodology skopiowana z `sources_catalog.md`
- [ ] 6 strata szczegółowo (tabele + opis)
- [ ] ChPL↔Ulotka pairing definicja + integrity validation
- [ ] Stratified sampling algorithm z pseudocode + RANDOM_SEED
- [ ] Codebooks per strata (w appendix lub `data/docs/`)
- [ ] License audit
- [ ] Ethics statement
- [ ] Reproducibility statement
- [ ] Świadome biases (5 typów) — explicit
- [ ] Wszystkie tabele numbered + captioned + referenced w text
- [ ] Length: 5-8 stron

## 8. Risks / common pitfalls

- ❌ Promotor v1 wytknął słabą selection methodology — **NIE powtarzać**. Sekcja 3.2 to defense.
- ❌ Generic statements typu "data jest ważna" — używaj konkretów z sources_catalog
- ❌ Zapomnienie świadomych biases — explicit przed R8 limitations
- ❌ Codebooks niekompletne — sprawdź każdy field per source
- ❌ Mieszanie raw/processed data w opisie — clear separation

## 9. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Outline R3 | Proponuje strukturę: typy danych → sources catalog → paired definition → sampling → folder structure → codebooks → license → ethics → reproducibility → biases | Sign-off na strukturę |
| 2 | Sekcja 3.1 Data types | Drafts explicit: text + tabular only, image/audio/video wyłączone z uzasadnieniem (problem = retrieval task na tekście) | Reviews jasność |
| 3 | Sekcja 3.2 Source selection methodology | Kopia z `sources_catalog.md` (inclusion + exclusion criteria + search strategy + selection pipeline + final composition) | Reviews completeness |
| 4 | Sekcja 3.3 6 strata corpus catalog | Kopia z `sources_catalog.md` Strata 1-6 (URL/scale/license/scrape per source) | Reviews accuracy |
| 5 | Sekcja 3.4 Paired ChPL↔Ulotka definition | Drafts: explicit definicja paired (productID alignment + data_modyfikacji + semantic scope) + integrity validation procedure z Iteracji 0 | Reviews |
| 6 | Sekcja 3.5 Stratified sampling algorithm | Drafts pseudocode z `sources_catalog.md` (RANDOM_SEED=42, 30% N05/N06 + equal-weight ATC Level 1) + reproducibility guarantees | Reviews reproducibility |
| 7 | Sekcja 3.6 Folder structure + versioning | Drafts `data/raw/`, `data/processed/`, `data/codebooks/`, DVC tracking conventions, naming conventions | Reviews convention |
| 8 | Sekcja 3.7 Codebooks per strata | Drafts codebook ChPL (10 sekcji × pola) + Ulotka (6 sekcji × pola) jako tabele 3.2 + 3.3 | Reviews |
| 9 | Sekcja 3.8 License + ethics | Art. 4 ustawy o prawie autorskim audit + CC licenses per OA journal + brak danych osobowych statement | Reviews compliance |
| 10 | Sekcja 3.9 Reproducibility statement | Scripts location `main_project/src/ingest/`, sample-list snapshot, `dvc pull` commands example | Reviews |
| 11 | Sekcja 3.10 Świadome biases | 5 świadomych biases z sources_catalog (license/ATC/recency/PL-only/source-type) explicit | Reviews honesty |
| 12 | Citation pass | `/citations` audit (Art. 4 link, CC license refs, BGE-M3 paper) | Reviews findings |
| 13 | Writing rules check | **Source selection methodology explicit w 3.2** (CRITICAL z promotor v1 feedback) + consistent tables + interpretation after each table | Final read-through |

**Workflow note:** iteracje 3-7 (kopiowanie z `sources_catalog.md`) są mechaniczne i mogą iść równolegle. Iteracje 8-11 (ethics/reproducibility/biases) wymagają refleksji. **Obowiązkowa** iteracja 13 — to właśnie ratuje promotor feedback 6/10 z v1.
