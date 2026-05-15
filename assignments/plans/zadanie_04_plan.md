# Plan zadania 04 — EDA, Standardization, Normalization (R4)

**Institutional source:** `assignments/04.md` (Task 04, 10 pkt)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/05-Data-Preparation-and-Exploratory-Data-Analysis.md` + `06-Feature-Engineering-and-Preprocessing.md` (Assignments 5+6)
**Mapuje na rozdział:** R4 EDA / Standaryzacja / Normalizacja
**Iteracja realizacji:** 1 (EDA report) + 7 (writing)

## 1. Czego instytucjonalnie wymaga Task 04

3 podsekcje:
- **Exploration (EDA)** — distributions, missing, outliers, correlations
- **Standardization** — formats, units, encoding, naming
- **Normalization** — scaling (Min-Max, Z-score, L2), TF-IDF/embeddings

Dla każdej modalności (tabular/text/image/audio/video) — different methods. U nas TEXT + TABULAR.

## 2. Czego wymaga PRO-D-THESIS Assignment 5 (EDA) + 6 (Feature Engineering)

**Assignment 5 (4-6 stron):**
- A. Dataset Structure and Integrity Analysis
- B. Statistical Characterization
- C. Correlation/Dependency Analysis
- D. Outlier and Noise Assessment
- E. Bias and Limitation Analysis (już w R3)
- F. Implications for Experimental Design

**Assignment 6 (4-6 stron):**
- A. Preprocessing Strategy Overview
- B. Data Cleaning and Missing Value Strategy
- C. Scaling, Normalization, Encoding (← N/A dla tekstu w klasycznym sensie)
- D. Feature Engineering / Transformation (← chunking strategies)
- E. Feature Selection (← nie aplikuje dla retrievalu)
- F. Pipeline Formalization (← integrated w main_project/src/)
- G. Impact on Experimental Design

## 3. Jak to wygląda w naszym v3.1

### Sekcja 4.1: EDA tekstowa (rozkłady i struktura)

**Per strata z `sources_catalog.md`:**

#### 4.1.1 ChPL
- **Rozkład długości** dokumentu (mean / median / std) per ATC class
- **Rozkład długości sekcji** (10 sekcji canonical) — pokazuje że sekcje 4.1 / 4.2 / 4.8 są długie, 4.7 / 4.9 krótsze
- **Terminology coverage** — count DCI nazw, kodów ATC, łacińskich terminów per dokument
- **OCR quality** — % text-layer vs scanned (target: <15% scanned per DEC-001 kill criteria)
- **Aktualności** — `data_modyfikacji` distribution

#### 4.1.2 Ulotki (paired analysis)
- **Length ratio Ulotka:ChPL** per para — typowo ~0.4-0.6 (Ulotki krótsze)
- **Section count match** — 6 sekcji Ulotka vs 10 sekcji ChPL semantic mapping
- **Vocabulary diff** — który vocabulary jest w obu, który tylko w ChPL (terminologia łacińska), który tylko w Ulotce (lay language)
- **Alignment quality** — `productID` resolution success rate w sample (target: ≥90% per DEC-001)

#### 4.1.3 AOTMiT raporty
- Section structure (Problem decyzyjny / Skuteczność / Bezpieczeństwo / Analiza ekonomiczna / Rekomendacje)
- Length distribution
- Year distribution

#### 4.1.4 NFZ Zarządzenia
- ICD-10 indications distribution
- Length distribution
- Updates per year

#### 4.1.5 OA journals (Farmacja Polska + Lek w Polsce + AAMS + CIPMS)
- Articles per year per journal
- Vocabulary diversity vs ChPL (more research-oriented language)
- Section structure (Wstęp / Metody / Wyniki / Dyskusja)

#### 4.1.6 Adjacencies (DHPC + braki list)
- Length distribution (short, focused)

### Sekcja 4.2: Embedding-space analysis

- **BGE-M3 embeddings** dla 1000 sampled chunks
- **UMAP visualization** — czy klastry odpowiadają ATC classes? (validation że BGE-M3 łapie semantykę)
- **Silhouette score** per ATC class — quantitative cluster quality
- **Cross-register cluster overlap** — czy pary ChPL+Ulotka są **blisko siebie** w embedding space? (preview RQ5 — jeśli już są blisko, retrieval może być łatwiejszy; jeśli daleko, więcej do uczenia)

### Sekcja 4.3: Outlier and noise

- **OCR artefakty** — dokumenty z OCR confidence < 80%
- **Encoding issues** — Polish diakrytyki dropped (ą, ę, ż, ć) — flag dokumenty
- **Duplicates** — `productID` collisions, version conflicts (różne `data_modyfikacji` dla tego samego produktu)
- **Decision:** which to remove vs flag vs retain

### Sekcja 4.4: Standardization

- **Unicode normalization** — `unicodedata.normalize('NFC', ...)` post-extraction
- **Encoding** — UTF-8 throughout
- **Date format** — ISO 8601 dla `data_modyfikacji`
- **Section headers** — standaryzowane (per ChPL canonical 10 / Ulotka QRD 6)
- **Naming convention** — `<strata>_<productID>_<section>.md` per chunk

### Sekcja 4.5: Normalization (text-specific)

W kontekście retrievalu / rerankingu **klasyczna normalizacja numerical NIE aplikuje** dla tekstu. Zamiast tego:

- **Tokenization** (BGE-M3 native tokenizer, SentencePiece)
- **Embedding generation** (BGE-M3, 1024-dim, hybrid dense + sparse)
- **L2 normalization** of embeddings (cosine similarity ready)

### Sekcja 4.6: Chunking strategies (z `02b II.4.1`)

Trzy strategie chunkingu per content type:
- **ChPL:** section-aware split (10 sekcji jak deterministic boundary)
- **Ulotki:** section-aware split (6 sekcji QRD)
- **AOTMiT/NFZ:** legal-aware split (named sections per source)
- **OA journals:** recursive markdown 512+50 / heading-based

### Sekcja 4.7: Pipeline formalization (do R5 architektura, krótko)

Reference do `main_project/src/chunking/` i `main_project/src/embed/`.

### Sekcja 4.8: Implications for Experimental Design

- Sample ChPL+Ulotka length ratios → wpływa na length-balanced hard negatives (II.4.6 L4)
- OCR quality → filtering kryteria
- Embedding clusters → walidacja BGE-M3 jako baseline (jeśli klastry są clean, embedder już dobrze działa; reranker poprawia precision na top-k, nie recall)
- Cross-register embedding overlap → predicts RQ5 difficulty

## 4. Co musimy znaleźć / przygotować

### Artefakty (tabele i figury)
- **Tab. 4.1:** Rozkład długości per strata (mean, median, std, min, max)
- **Tab. 4.2:** OCR quality per strata (% text-layer)
- **Tab. 4.3:** ChPL↔Ulotka length ratio statistics
- **Tab. 4.4:** ATC class distribution w sampled corpus
- **Tab. 4.5:** Chunking strategies per content type
- **Fig. 4.1:** UMAP embedding visualization (kolory = ATC class)
- **Fig. 4.2:** ChPL vs Ulotka length distribution (overlaid histograms)
- **Fig. 4.3:** Top-50 frequent terms per strata (word clouds optional, or bar charts)
- **Fig. 4.4:** ChPL+Ulotka cluster proximity (per paired-pair distance histogram)

### Pre-conditions z Iteracji 1
- Corpus scraped (Iteracja 1 output)
- BGE-M3 indexed in Qdrant
- EDA scripts uruchomione

## 5. Writing rules application

- **Konsystentne tabele** — identyczne kolumny per analogous tables (e.g., wszystkie length tabele mają takie same statistics columns)
- **Evidence-to-conclusion** — po każdej Fig./Tab. interpretacja (Tabela 4.1 pokazuje, że ChPL ma X razy więcej tokens niż Ulotki, co implikuje Y dla chunking strategy)
- **Academic style** — bez "obecnie", "rosnące"

## 6. Defense scaffolding application

- **Cross-register cluster overlap analysis (Sekcja 4.2)** — preview RQ5, predicts wynik retreningu cross-register, wprowadza Defense pkt 3 (negative-result framing): jeśli klastry są daleko od siebie, training cross-register pomaga dużo; jeśli już blisko, marginal gain — flaging early.
- **Bias and limitation continuation z R3** — Sekcja 4.8 Implications powiązane z biases (limitations growing organically)

## 7. Acceptance checklist

- [ ] EDA per strata (6 podsekcji) z statistics
- [ ] Paired ChPL↔Ulotka analysis (length ratio, alignment quality)
- [ ] Embedding-space analysis (UMAP, silhouette, cross-register proximity)
- [ ] Outlier/noise z decisions
- [ ] Standardization explicit (unicode, encoding, dates, naming)
- [ ] Normalization (BGE-M3 embedding + L2)
- [ ] 4 chunking strategies opisane
- [ ] Pipeline formalization reference do main_project/
- [ ] Implications for Experimental Design (4.8)
- [ ] Wszystkie 5 figur + 5 tabel
- [ ] Length: 6-10 stron

## 8. Risks / common pitfalls

- ❌ Mieszanie EDA z modeling (model training nie tutaj — tu tylko data understanding)
- ❌ Brak interpretacji tabel/figur — KAŻDA tabela/figura potrzebuje syntezy
- ❌ Statistical overkill (per promotor v1: "promotor preferuje engineering rigor nad over-statistical testing") — keep statistics descriptive, not inferential
- ❌ Zapomnienie cross-register angle w embedding analysis — to early preview RQ5
- ❌ OCR overhead nie sprawdzony przed scrape — pre-condition Iteracji 0 kill criteria

## 9. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Outline R4 | Proponuje strukturę: doc-level EDA per strata → ATC distribution → paired analysis → eval set characterization → embedding UMAP → standaryzacja → normalizacja → chunking → pipeline → implications | Sign-off |
| 2 | Sekcja 4.1 EDA per strata | Drafts rozkłady długości per strata 1-6 (boxplot z mean/median/std), OCR rate, missing/corrupted documents rate | Reviews + interpretation |
| 3 | Sekcja 4.2 ATC distribution | Drafts histogram target (30% N05/N06) vs actual + commentary o bias propagation | Reviews |
| 4 | Sekcja 4.3 Paired ChPL↔Ulotka analysis | Drafts length ratio scatter (typowo 0.4-0.6 Ulotka:ChPL), section count comparison (6 vs 10), alignment integrity rate (z Iteracji 0 pre-condition) | Reviews accuracy |
| 5 | Sekcja 4.4 Embedding UMAP | Drafts BGE-M3 2D projection całego corpus, color by ATC class level 1, cluster cohesion analysis (intra-class vs inter-class) | Reviews wizualizacja |
| 6 | Sekcja 4.5 Eval set 200 par characterization | Drafts rozkład typów leków N05/N06, sekcji query, query length distribution | Reviews |
| 7 | Sekcja 4.6 Standaryzacja text | Drafts diakrytyki NFC normalization, lowercase decision (NIE — zachowujemy case dla DCI), special chars cleanup (form-feed, soft hyphens) | Reviews choices |
| 8 | Sekcja 4.7 Chunking 4 strategies | Drafts tabela z konspekt II.4: ChPL section-aware (10 sekcji) / Ulotka section-aware (6 sekcji) / HTA-NFZ legal-aware / journals recursive markdown 512+50 | Reviews |
| 9 | Sekcja 4.8 Normalization embeddings | Drafts BGE-M3 default L2 + sanity check norm distribution histogram | Reviews |
| 10 | Sekcja 4.9 Pipeline formalization | Reference do `main_project/src/chunking/` + `main_project/src/embed/` + Hydra configs | Reviews |
| 11 | Sekcja 4.10 Bias section (kontynuacja z R3) | 5 biases z R3 + EDA-derived (np. ATC P under-sampled jeśli pool < 45) | Reviews honesty |
| 12 | Sekcja 4.11 Implications for Experimental Design | Drafts co EDA mówi dla R5 (architektura) i R6 (modele): length ratio → hard negatives L4 calibration, embedding clusters → predict RQ5 difficulty, OCR threshold → filtering | Reviews coherence |
| 13 | Citation pass | `/citations` audit (BGE-M3, UMAP, statistics references) | Reviews |
| 14 | Writing rules check | Tabele consistency + **interpretation paragraph po każdej tabeli/figurze** (Writing rule 6 evidence-conclusion) + no over-statistical formalism | Final read-through |

**Workflow note:** iteracje 2-6 (EDA components) mogą iść równolegle po sign-off na outline. Sekcja 4.11 implications wymaga ukończenia pozostałych sekcji + linkuje do R5/R6. **Reguła promotor v1:** statistics keep descriptive (mean ± std, distributions), unikaj inferential overkill (per "keep statistics descriptive, not inferential").
