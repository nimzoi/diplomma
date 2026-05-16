# R4. Eksploracyjna analiza danych

> **Status drafu:** Metodologia + standaryzacja + chunking strategies (sekcje 4.1, 4.3, 4.4, 4.7) napisane w pełni; wartości empiryczne (rozkłady, OCR rate, UMAP, length statistics) oznaczone `🟡 TBD post-Iteracja 1` z gotowymi szablonami interpretacyjnymi do wypełnienia po wykonaniu pełnego scrape (Iteracja 1, konspekt II.16). Source of truth dla treści: `thesis_research/sources_catalog.md`, decyzje domenowe DEC-001 oraz DEC-002.

## 4.1 Cele eksploracyjnej analizy danych i metodologia

### 4.1.1 Cele rozdziału

Eksploracyjna analiza danych (EDA) jest wykonywana w ramach niniejszej pracy w trzech rolach. Po pierwsze, *diagnostyczna* — weryfikacja jakości i kompletności korpusu zebranego w Iteracji 1 (zgodnie z planem iteracyjnym z konspektu II.16) względem pre-conditions zdefiniowanych w Iteracji 0a (sekcja 4.6 niniejszego rozdziału oraz `sources_catalog.md` § Iteracja 0). Po drugie, *projektowa* — informowanie wyborów architektonicznych dotyczących chunkingu, hard negative mining oraz cross-register evaluation, które są szczegółowo opisane w R5 (Architektura) oraz R6 (Modele). Po trzecie, *defensywna* — udokumentowanie świadomych biases korpusu (kontynuacja rozdziału R3 sekcja 3.10) z mapowaniem na konsekwencje dla wyników w R7 oraz na strukturę limitations w R8.

Trzy role są celowo rozdzielone: diagnostyka odpowiada na pytanie *„czy korpus spełnia założenia"*, projektowa na *„co z tego wynika dla pipeline'u"*, defensywna na *„które wnioski empiryczne są warunkowane biasami"*.

### 4.1.2 Metodologia analizy

Analiza wykorzystuje wyłącznie statystyki *opisowe* (mean, median, std, percentyle, rozkłady częstości) oraz wizualizacje (histogramy, boxploty, scatter ploty, projekcje 2D). **Statystyki inferencyjne** (testy hipotez, p-values, przedziały ufności) **nie są stosowane w R4**, zgodnie z preferencją promotora wyrażoną w feedbacku do wcześniejszej wersji pracy (*„promotor preferuje engineering rigor nad over-statistical testing"* — `thesis_research/02b_konspekt_v3_updates.md` § II.3.3 przy omawianiu power analysis dla RQ5). Statystyki inferencyjne pozostają zarezerwowane dla rozdziału R7 (Wyniki), gdzie służą weryfikacji hipotez H1–H5.

Pipeline analityczny EDA jest podzielony na pięć faz:

1. **Charakterystyka korpusu** — rozkłady długości dokumentów per strata, dystrybucja kodów ATC w sample ChPL, pokrycie czasowe (rok publikacji / data ostatniej modyfikacji).
2. **Standaryzacja i normalizacja tekstu** — Unicode NFC, polskie diakrytyki, segmentacja zdań, gotchas specyficzne dla ChPL.
3. **Chunking** — implementacja czterech strategii z `02b_konspekt II.4.1` na pełnym korpusie + walidacja granic.
4. **Embedding-space analysis** — projekcja UMAP na embeddingach BGE-M3, walidacja klastrów względem kodów ATC.
5. **Paired ChPL↔Ulotka analysis** (kluczowa dla RQ5 / DEC-002) — length ratio, lexical divergence professional/lay, sentence complexity, section-level alignment.

Każda faza generuje artefakty raportowe (tabele + figury) zapisywane do `main_project/reports/eda/` z numeracją zgodną z niniejszym rozdziałem oraz z wersjonowaniem przez DVC. Reprodukowalność: każdy artefakt jest produkowany przez deterministyczny skrypt z fixed `RANDOM_SEED=42` (zgodnie z konwencją z `sources_catalog.md` § Reproducibility statement).

### 4.1.3 Stack narzędziowy EDA

Implementacja analizy korzysta z otwartych narzędzi zgodnych ze stackiem pracy (`thesis_research/05_stack_techniczny.docx` jest źródłem prawdy dla decyzji technologicznych):

- **pandas + polars** — operacje na tabelach metadanych korpusu (chunks, eval pairs, statystyki agregowane).
- **pdfplumber** — ekstrakcja tekstu z text-layer PDF (ChPL, Ulotki, AOTMiT, NFZ); detekcja braku text-layer jako sygnał do OCR.
- **Tesseract `-l pol`** — OCR dla zeskanowanych ChPL (~5–10% korpusu wg sources research, walidacja w sekcji 4.6) [^tesseract].
- **spaCy 3.x z modelem `pl_core_news_sm`** — tokenizacja i segmentacja zdań dla polszczyzny [^spacy_polish].
- **UMAP** (Uniform Manifold Approximation and Projection) — redukcja wymiarowości embeddingów BGE-M3 (1024-D → 2-D) dla wizualizacji klastrów [^umap].
- **scikit-learn** — silhouette score, k-means dla diagnostyki klastrów.
- **matplotlib + seaborn** — figury statyczne do osadzenia w pracy.

[^tesseract]: Smith R. (2007). *An Overview of the Tesseract OCR Engine*. ICDAR. 🟡 Verify via citation-checker.
[^spacy_polish]: Honnibal M., Montani I. (2017). *spaCy 2: Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing*. 🟡 Verify version + Polish model release year via citation-checker.
[^umap]: McInnes L., Healy J., Melville J. (2018). *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*. arXiv:1802.03426. 🟡 Verify via citation-checker.

### 4.1.4 Cross-reference do innych rozdziałów

Niniejszy rozdział systematycznie odwołuje się do trzech sąsiadujących:

- **R3 (Dane)** — provenance źródeł (które dokumenty, jakie licencje, jaki scrape), świadome biases korpusu (sekcja 3.10) — kontynuowane i pogłębiane w sekcji 4.7 (paired analysis) oraz 4.8 (eval set).
- **R5 (Architektura)** — implikacje EDA dla pipeline'u: chunking strategies (4.4) ⇒ implementacja w `main_project/src/chunking/`, embedding analysis (4.5) ⇒ uzasadnienie BGE-M3 jako frozen embedder.
- **R6 (Modele)** — implikacje EDA dla treningu: lexical divergence professional/lay (4.7) ⇒ kalibracja hard negatives L4 z 4-poziomowej taksonomii (`02b_konspekt II.4.6`); rozkład długości (4.2) ⇒ length-balanced batch sampling.

## 4.2 Charakterystyka korpusu — dystrybucje

> **Placeholder data flag:** wartości w tej sekcji są wartościami **docelowymi** wynikającymi z planu próbkowania (sources_catalog.md § Strata 1 § Stratified sampling algorithm). Wartości faktyczne — post-scrape, po deduplikacji, po filtrowaniu OCR quality — `🟡 TBD post-Iteracja 1`. Interpretacje są szablonami warunkowymi typu *„jeśli X > Y, to wniosek architektoniczny Z"*.

### 4.2.1 Rozkład długości dokumentów per strata

Tabela 4.1 podsumowuje rozkład długości dokumentów (mierzony w tokenach BGE-M3 SentencePiece) per strata korpusu.

**Tabela 4.1.** Rozkład długości dokumentów per strata (placeholder data — wartości docelowe).

| Strata | n docs | mean tokens | median | std | p5 | p95 | min | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. ChPL | 900 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| 2. Ulotki | 900 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| 3. AOTMiT + MZ | 700 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| 4. NFZ Zarządzenia | 400 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| 5. OA journals | 900 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| 6. Adjacencies (DHPC + braki) | 300 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |

**Szablon interpretacyjny (do wypełnienia post-Iteracja 1):**

> *Tabela 4.1 pokazuje, że [strata X] ma znacząco wyższą medianę długości niż [strata Y] (różnica `[delta]` tokenów, ratio `[ratio]`×). Konsekwencje dla chunkingu: [jeśli mediana ChPL > 8000 tokenów ⇒ chunking ChPL musi rozbijać dokument na ≥3 segmenty per dokument; jeśli mediana < 4000 tokenów ⇒ section-aware split z 10 sekcji canonical wystarczy]. Konsekwencje dla rerankera: maksymalny passage length musi przekraczać [p95 z najdłuższej strata], czyli `[p95]` tokenów — co [mieści się / nie mieści się] w 512-token kontekście standardowego polish-reranker-roberta-v3, [bez modyfikacji / wymaga truncation strategy].*

**Figura 4.1: Boxplot długości dokumentów per strata (TBD post-Iteracja 1).**

Planowana figura: 6 boxplotów (po jednym per strata) na wspólnej osi x (tokens, log-scale). Cel: szybka wizualna identyfikacja strata o ekstremalnej długości oraz outliers.

### 4.2.2 Dystrybucja kodów ATC w sampled ChPL

Strata 1 (ChPL) jest *stratified sampled* z over-representacją psychiatrycznej podgrupy (ATC N05 Psycholeptica, ATC N06 Psychoanaleptica) do 30% próby zgodnie ze świadomą decyzją z DEC-001 (uzasadnienie: leverage manual validation kompetencji autorki w psychiatrycznej podgrupie dla rygorystycznej walidacji LLM-as-judge w RQ2/H2). Pełen algorytm próbkowania w `sources_catalog.md` § Strata 1 § Stratified sampling algorithm.

Tabela 4.2 raportuje dystrybucję ATC Level 1 w sampled corpus 900 leków vs natural URPL distribution.

**Tabela 4.2.** Dystrybucja ATC Level 1 w sampled ChPL vs natural URPL distribution (placeholder data).

| ATC L1 | Klasa terapeutyczna | n in sample | % sample | % natural URPL | Over-/Under-rep |
|---|---|---:|---:|---:|---:|
| A | Przewód pokarmowy + metabolizm | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| B | Krew + układ krwiotwórczy | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| C | Układ sercowo-naczyniowy | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| D | Dermatologia | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| G | Układ moczowo-płciowy + hormony płciowe | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| H | Hormony układowe | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| J | Leki przeciwzakaźne układowe | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| L | Leki przeciwnowotworowe + immunomodulacyjne | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| M | Układ mięśniowo-szkieletowy | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| **N (N01–N04, N07)** | OUN — pozostałe (anestetyki, p-bólowe, p-padaczkowe, p-parkinsonowskie) | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| **N05** | **Psycholeptica (target ~15%)** | **~135** | **~15%** | **~5%** | **~3× over-rep** |
| **N06** | **Psychoanaleptica (target ~15%)** | **~135** | **~15%** | **~5%** | **~3× over-rep** |
| P | Leki przeciwpasożytnicze | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| R | Układ oddechowy | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| S | Narządy zmysłów | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| V | Różne | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |

**Szablon interpretacyjny (do wypełnienia post-Iteracja 1):**

> *Tabela 4.2 potwierdza realizację stratified sampling design (DEC-001): N05 i N06 stanowią łącznie [TBD]% sample ChPL, z target 30% (rozkład [równomierny / nierównomierny] między N05 i N06). Klasy [TBD: rzadkie ATC takie jak P, V] są pod-sampled w stosunku do per-class target ~45 leków, ze względu na ograniczoną populację w URPL — flagging w R8 limitations. Konsekwencje dla rerankera: [psych-dominated training może prowadzić do better performance on N05/N06 queries, gorszego na rzadkich klasach; weryfikacja w R7 ablation A3 (corpus → psych-only)].*

### 4.2.3 Pokrycie czasowe — `data_modyfikacji`

Pole `data_modyfikacji` z URPL RPL XML feed pozwala śledzić aktualność każdego ChPL. Hipoteza eksploracyjna: nowsze ChPL (post-2020) mają lepszą jakość text-layer (mniej OCR), aktualną terminologię, kompletniejsze sekcje 4.4–4.5 (interakcje, ostrzeżenia).

**Figura 4.2: Histogram `data_modyfikacji` ChPL w sample (TBD post-Iteracja 1).**

Planowana figura: histogram per rok (2010–2026) z annotated medianą oraz percentyle p10 i p90. Cel: weryfikacja hipotezy o recency bias korpusu (świadomy bias #3 z R3 sekcja 3.10).

## 4.3 Standaryzacja i normalizacja tekstu

Ta sekcja opisuje pełną procedurę standaryzacji tekstu zastosowaną do każdego dokumentu korpusu **przed** chunkingiem (sekcja 4.4) i **przed** wygenerowaniem embeddingów BGE-M3. Standaryzacja zapewnia (a) determinizm pipeline'u (ten sam dokument źródłowy → ten sam tekst po standaryzacji niezależnie od środowiska wykonania), (b) zgodność z założeniami tokenizera SentencePiece używanego przez BGE-M3, (c) eliminację artefaktów typowych dla polskich PDF-ów regulacyjnych.

### 4.3.1 Unicode normalization (NFC)

Polski tekst regulacyjny w PDF jest często reprezentowany w postaci kanonicznie *zdekomponowanej* — znaki diakrytyczne `ą`, `ę`, `ć`, `ż`, `ź`, `ń`, `ó`, `ś`, `ł` zapisywane są jako combining sequences (np. `a` + combining ogonek U+0328) zamiast pojedynczych code points. Tokenizer SentencePiece traktuje zdekomponowane sekwencje i pojedyncze code points jako **różne tokeny**, co prowadzi do (i) duplikacji vocabulary, (ii) niższej jakości embeddingu dla wyrażeń z diakrytykami, (iii) nieprzewidywalnego zachowania w retrievalu (query z `ą` jako pojedynczym znakiem nie matchuje passage z `a`+combining).

Rozwiązanie zastosowane w pipeline:

```python
# main_project/src/preprocess/normalize.py
import unicodedata

def normalize_unicode(text: str) -> str:
    """Apply Unicode NFC (Canonical Composition) normalization."""
    return unicodedata.normalize("NFC", text)
```

NFC (Normalization Form Canonical Composition) konsoliduje wszystkie zdekomponowane sekwencje do pojedynczych precomposed code points — `a`+U+0328 → `ą` (U+0105). Procedura jest deterministyczna i odwracalna.

**Sanity check w EDA:** zliczenie proporcji combining marks (Unicode category `Mn`) w sample 100 ChPL **przed** i **po** NFC. Oczekiwany wynik post-NFC: ≤ 0.5% combining marks (residual = uzasadnione użycia, np. matematyczne notacje w sekcji 4.5 Właściwości farmakologiczne).

### 4.3.2 Polskie diakrytyki — gotcha specyficzna dla ChPL

Sources research (R2, 2026-05-15) ujawnił, że **podzbiór ChPL** (głównie pre-2015, wytworzonych przez specyficznych MAH-ów na nieaktualnych szablonach) **droppuje encoding diakrytyków** w PDF — `ą`, `ę` są reprezentowane jako `a`, `e` lub jako *replacement character* `?` / U+FFFD. Mechanizm: PDF generated z Worda używającego non-Unicode font, kopiowanie tekstu rejestruje glyph fallback.

Konsekwencja dla pipeline'u: dokumenty z droppingiem diakrytyków mają (i) zniekształcone embeddings (BGE-M3 widzi *„dawkowanie u pacjentow z niewydolnoscia"* zamiast *„dawkowanie u pacjentów z niewydolnością"*), (ii) niższy jaccard z queries normalnie zapisanymi.

Strategia detekcji w EDA (sekcja 4.6):

1. Per dokument: zliczenie ratio diakrytyków do liczby liter alfabetu polskiego w tekście. Polski tekst medyczny ma typowo 8–14% liter z diakrytykami.
2. Dokumenty z ratio < 3% są flagowane jako *prawdopodobnie dropped diacritics* — wymagana inspekcja manualna na sample 20.
3. Dokumenty potwierdzone jako dropped (przez inspekcję) są (a) flagowane w metadata (`metadata.diacritic_quality = "dropped"`), (b) **NIE** są reconstructed automatycznie (re-akcentowanie wymaga modelu lub słownika DCI — out of scope), (c) używane w training z zaznaczonym flag — reranker uczy się, że oba warianty pisowni są ekwiwalentne.

**Konsekwencja dla świadomych biases:** ten bias jest dodawany do listy z R3 sekcja 3.10 jako bias #6 (encoding heterogeneity).

### 4.3.3 Lowercase strategy

W standardowym NLP pipeline lowercase jest często stosowany jako default. **W niniejszej pracy lowercase NIE jest stosowany** z trzech powodów:

1. **Międzynarodowe nazwy DCI** (np. *Sertraline*, *Risperidone*, *Quetiapine*) są w ChPL pisane z wielkiej litery, podczas gdy laypersonowski synonim w Ulotce — z małej. Lowercase tracilby ten sygnał register difference.
2. **Skróty kodów ATC** (N05AB, A10BD) są case-sensitive — niektóre subkody używają małych liter dla wariantu (konkretnego przykładu w ATC nie wskazano, lecz analogicznie *iv* vs *IV* w drug administration). Lowercase byłby bezpieczny dla ATC, ale lossy dla terminologii ogólnej.
3. **BGE-M3 jako multilingual encoder** jest pretrenowany **case-sensitive** — preserving case matchuje pretraining distribution.

Decyzja: **case preserved throughout** dla ChPL, Ulotek, AOTMiT, NFZ. Wyjątek dla lowercase: **search index BM25 baseline** (Pyserini) w R6 — case-insensitive search jako baseline reference.

### 4.3.4 Sentence segmentation

Segmentacja zdań jest wymagana dla (a) chunkingu z respektowaniem granic zdań w sekcji 4.4, (b) obliczeń sentence complexity w sekcji 4.7 (paired analysis).

Polski tekst medyczny ma kilka *gotcha* dla naive sentence segmentation:

- **Skróty z kropką** — *„np."*, *„m.in."*, *„tj."*, *„ok."*, *„hr."* są często mylnie traktowane jako koniec zdania.
- **Jednostki dawki** — *„5 mg/kg m.c."* (mass corporis) zawiera trzy kropki, z których żadna nie jest końcem zdania.
- **Numerowane sekcje ChPL** — *„4.1 Wskazania"*, *„4.2 Dawkowanie"* — kropki w numeracji sekcji NIE są końcem zdania.
- **Bibliografia** — *„Smith J. et al. (2020)."* — *„et al."* zawiera kropkę.

Strategia: **spaCy** z modelem `pl_core_news_sm` jako baseline segmentator + **post-processing rules** dla powyższych gotcha:

```python
# main_project/src/preprocess/segment.py — pseudocode
import spacy

nlp = spacy.load("pl_core_news_sm")

POLISH_ABBREVIATIONS = {"np.", "m.in.", "tj.", "ok.", "hr.", "p.o.", "i.v.", "i.m.", "s.c.", "et al."}

def segment_sentences(text: str) -> list[str]:
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    # Post-processing: merge sentences that ended on known abbreviation
    merged = []
    buffer = ""
    for sent in sentences:
        if buffer:
            sent = buffer + " " + sent
            buffer = ""
        # Check if last token is known abbreviation
        last_token = sent.rsplit(maxsplit=1)[-1] if sent else ""
        if last_token in POLISH_ABBREVIATIONS:
            buffer = sent
        else:
            merged.append(sent)
    if buffer:
        merged.append(buffer)
    return merged
```

Walidacja segmentacji: na sample 50 zdań ChPL manualnie sprawdzonych przez autorkę, target precision ≥ 95%, recall ≥ 95%. Wyniki — sekcja 4.6.

**Alternatywa rozważana: stanza** (Stanford NLP) z polskim modelem. Decyzja: spaCy ze względu na (a) lżejszą integrację z resztą pipeline'u Python, (b) szybsze inference (ważne dla pełnego korpusu ~4100 dokumentów), (c) wystarczającą jakość po post-processing rules. Stanza pozostaje jako fallback jeśli spaCy precision < 90% w walidacji [^stanza].

[^stanza]: Qi P., Zhang Y., Zhang Y., Bolton J., Manning C.D. (2020). *Stanza: A Python natural language processing toolkit for many human languages*. ACL 2020 demo. 🟡 Verify via citation-checker.

### 4.3.5 Pozostałe artefakty PDF

Trzy klasy artefaktów typowych dla PDF-ów regulacyjnych:

1. **Soft hyphens (U+00AD)** — używane do justowania tekstu, są niewidoczne w renderingu PDF, ale obecne w ekstraktowanym tekście. Strategia: usunięcie via `text.replace("­", "")`.
2. **Form feed (U+000C)** — separator strony, w ekstraktowanym tekście pojawia się między stronami. Strategia: zachować jako page boundary marker (przydatne dla bibliographic citations w sekcji 4.7), ale **NIE** włączać do tokenizacji (tokenizer ignoruje).
3. **Hard line breaks w środku zdań** — PDF rozbija zdanie na linie wizualne, ekstraktowany tekst zawiera `\n` w środku zdania. Strategia: heurystyka — `\n` poprzedzony lowercase + następujący lowercase ⇒ usunięcie (kontynuacja zdania); `\n` poprzedzony kropką + następujący wielką literą ⇒ zachowanie (granica zdania).

### 4.3.6 Naming convention dla chunków

Po standaryzacji i chunkingu, każdy chunk jest identyfikowany przez deterministyczny naming pattern:

```
<strata>_<source_id>_<section>_<chunk_idx>.md
```

Przykłady:
- `chpl_PL12345_4.3_001.md` — ChPL produkt PL/12345/00, sekcja 4.3 Przeciwwskazania, pierwszy chunk
- `ulotka_PL12345_3_002.md` — Ulotka tego samego produktu, sekcja 3 Jak przyjmować, drugi chunk
- `aotmit_REK_2023_45_problem.md` — rekomendacja AOTMiT 45/2023, sekcja Problem decyzyjny
- `nfz_zarz_18_2024_kryteria.md` — Zarządzenie Prezesa NFZ 18/2024, sekcja Kryteria kwalifikacji
- `journal_farmpol_2022_3_98_intro.md` — Farmacja Polska 2022, vol. 78 nr 3 s. 98, Wstęp

Mapping pomiędzy chunkami a metadata jest utrzymywany w PostgreSQL tabeli `chunks` (schema definiowana w R5 sekcja Architektura danych).

## 4.4 Strategie chunkingu

Chunking jest jednym z najbardziej wpływowych wyborów architektonicznych w RAG — granica chunku determinuje, co retriever może zwrócić jako passage, a tym samym co generator może zacytować. Naive chunking (np. fixed 512-token sliding window) ignoruje strukturę dokumentu i prowadzi do passage'y rozcinających semantycznie spójne sekcje. W niniejszej pracy zastosowano **cztery różne strategie chunkingu**, dobrane do struktury każdej grupy źródeł, zgodnie z `02b_konspekt_v3_updates.md` § II.4.1 oraz `sources_catalog.md` § Mapping na training data.

Tabela 4.3 podsumowuje cztery strategie z mapping na strata.

**Tabela 4.3.** Cztery strategie chunkingu per strata (deterministyczna konfiguracja).

| Strategia | Strata | Boundary type | Chunk size | Overlap | Liczba sekcji canonical |
|---|---|---|---:|---:|---:|
| **A. Section-aware ChPL** | 1 (ChPL) | Heading regex (deterministic) | per-section | n/a | 10 |
| **B. Section-aware Ulotka** | 2 (Ulotki) | Heading regex (QRD-aligned) | per-section | n/a | 6 |
| **C. Named-section + legal fallback** | 3, 4 (HTA/NFZ) | Named section regex + 1024-token fallback | ≤ 1024 tokens | 64 tokens | 3–8 (per source) |
| **D. Recursive markdown / heading-based** | 5, 6 (journals + adjacencies) | Markdown heading hierarchy + recursive split | 512 tokens | 50 tokens | varies |

### 4.4.1 Strategia A — Section-aware ChPL (10 sekcji canonical)

ChPL jest ustandaryzowany w **10 sekcji deterministycznych** zgodnie z wytycznymi EMA QRD (Quality Review of Documents):

1. Nazwa produktu leczniczego
2. Skład jakościowy i ilościowy
3. Postać farmaceutyczna
4. Szczegółowe dane kliniczne (z podsekcjami 4.1–4.9)
5. Właściwości farmakologiczne
6. Dane farmaceutyczne

W praktyce sekcja 4 jest rozbita na 9 podsekcji (4.1 Wskazania, 4.2 Dawkowanie, 4.3 Przeciwwskazania, 4.4 Specjalne ostrzeżenia, 4.5 Interakcje, 4.6 Wpływ na płodność/ciążę/laktację, 4.7 Wpływ na zdolność prowadzenia pojazdów, 4.8 Działania niepożądane, 4.9 Przedawkowanie). Pełna lista sekcji w `sources_catalog.md` § Strata 1 § Struktura ChPL.

**Implementacja:** regex-based section header detection. Wzorce dla głównych sekcji:

```python
# main_project/src/chunking/chpl.py — pseudocode
import re

CHPL_SECTION_PATTERNS = {
    "1":   r"^\s*1\.\s+NAZWA PRODUKTU LECZNICZEGO\s*$",
    "2":   r"^\s*2\.\s+SK[ŁL]AD JAKO[ŚS]CIOWY I ILO[ŚS]CIOWY\s*$",
    "3":   r"^\s*3\.\s+POSTA[ĆC] FARMACEUTYCZNA\s*$",
    "4.1": r"^\s*4\.1\.?\s+WSKAZANIA DO STOSOWANIA\s*$",
    "4.2": r"^\s*4\.2\.?\s+DAWKOWANIE I SPOS[ÓO]B PODAWANIA\s*$",
    "4.3": r"^\s*4\.3\.?\s+PRZECIWWSKAZANIA\s*$",
    "4.4": r"^\s*4\.4\.?\s+SPECJALNE OSTRZE[ŻZ]ENIA",  # truncated header tolerated
    "4.5": r"^\s*4\.5\.?\s+INTERAKCJE",
    "4.6": r"^\s*4\.6\.?\s+WP[ŁL]YW NA P[ŁL]ODNO[ŚS][ĆC]",
    "4.7": r"^\s*4\.7\.?\s+WP[ŁL]YW NA ZDOLNO[ŚS][ĆC] PROWADZENIA",
    "4.8": r"^\s*4\.8\.?\s+DZIA[ŁL]ANIA NIEPO[ŻZ][ĄA]DANE\s*$",
    "4.9": r"^\s*4\.9\.?\s+PRZEDAWKOWANIE\s*$",
    "5":   r"^\s*5\.\s+W[ŁL]A[ŚS]CIWO[ŚS]CI FARMAKOLOGICZNE\s*$",
    "6":   r"^\s*6\.\s+DANE FARMACEUTYCZNE\s*$",
}
```

**Tolerance dla heterogeneity:** wzorce akceptują (a) opcjonalną kropkę po numerze sekcji (`4.1` vs `4.1.`), (b) variation w diakrytykach (`Ł` vs `L`, dla dokumentów z dropped encoding sekcja 4.3.2), (c) truncated headers (długie tytuły 4.4 czasem są zawijane).

**Walidacja section detection** w EDA (sekcja 4.6): na sample 100 ChPL, target detection rate ≥ 95% per sekcja. Sekcje rzadkie (4.6 Wpływ na płodność — pomijane dla leków OTC bez tej indykacji) mogą mieć niższy detection rate, co jest **acceptable** (brak sekcji ≠ błąd parsingu).

**Output chunkingu:** każda detected sekcja jest **jednym chunkiem** (no further splitting per default), nawet jeśli sekcja ma > 1024 tokenów. Powód: section-level chunking maksymalizuje semantic coherence, a polish-reranker-roberta-v3 ma context window 512 tokens — long sections są obsługiwane przez **truncation w training** (truncate query + passage do max 512 łącznie) z documented degradation flagged w R6.

**Edge case — sekcja 5 Właściwości farmakologiczne** często jest > 2000 tokenów (zawiera sub-sekcje 5.1 Farmakodynamika, 5.2 Farmakokinetyka, 5.3 Dane przedkliniczne). Dla tej sekcji jako wyjątek: dodatkowy split na sub-sekcje 5.1/5.2/5.3 jeśli detected, fallback na recursive split z 512-token chunks z 50-token overlap.

### 4.4.2 Strategia B — Section-aware Ulotka (6 sekcji QRD)

Ulotka dla pacjenta jest QRD-aligned w **6 sekcjach deterministycznych** (`sources_catalog.md` § Strata 2 § Struktura Ulotki):

1. Co to jest lek X i w jakim celu się go stosuje
2. Informacje ważne przed przyjęciem/zastosowaniem leku X
3. Jak przyjmować/stosować lek X
4. Możliwe działania niepożądane
5. Jak przechowywać lek X
6. Zawartość opakowania i inne informacje

**Implementacja:** analogiczna do ChPL, regex-based detection z tolerance dla wariantów *„przyjmować"* vs *„stosować"* (zależne od formy leku).

```python
ULOTKA_SECTION_PATTERNS = {
    "1": r"^\s*1\.?\s+Co to jest (?:lek|le[kc]z[er][nt]i[ke])",
    "2": r"^\s*2\.?\s+Informacje wa[żz]ne przed",
    "3": r"^\s*3\.?\s+Jak (?:przyjmowa[ćc]|stosowa[ćc])",
    "4": r"^\s*4\.?\s+Mo[żz]liwe dzia[łl]ania niepo[żz][ąa]dane",
    "5": r"^\s*5\.?\s+Jak przechowywa[ćc]",
    "6": r"^\s*6\.?\s+Zawarto[śs][ćc] opakowania",
}
```

**Output:** 6 chunków per Ulotka, average chunk size znacznie mniejszy niż ChPL (zgodnie z hipotezą length ratio 0.4–0.6 weryfikowaną w sekcji 4.7).

**Section semantic mapping ChPL ↔ Ulotka** (kluczowe dla RQ5 cross-register, sekcja 4.7):

| ChPL sekcja | Semantyczna treść | Ulotka sekcja | Komentarz |
|---|---|---|---|
| 4.1 Wskazania | Co leczy | 1 Co to jest lek | Direct mapping |
| 4.2 Dawkowanie | Schemat podawania | 3 Jak przyjmować | Direct mapping |
| 4.3 Przeciwwskazania + 4.4 Ostrzeżenia + 4.5 Interakcje + 4.6 Ciąża/laktacja | Bezpieczeństwo | 2 Informacje ważne przed | **Many-to-one** (4 ChPL → 1 Ulotka) |
| 4.8 Działania niepożądane | Side effects | 4 Możliwe działania niepożądane | Direct mapping |
| 6 Dane farmaceutyczne (warunki przechowywania) | Storage | 5 Jak przechowywać | Direct mapping |
| 2 Skład + 6 Dane farmaceutyczne (wytwórca, nr pozwolenia) | Identyfikacja produktu | 6 Zawartość opakowania | Many-to-one |

Ten mapping jest podstawą generacji cross-register pairs dla RQ5 (sekcja 4.7).

### 4.4.3 Strategia C — Named-section split z legal fallback (HTA + NFZ)

Strata 3 (AOTMiT + MZ) i Strata 4 (NFZ Zarządzenia) używają **różnych nagłówków sekcji per source**, nie ma wspólnego canonical. Rozwiązanie: **per-source registry** named sections + legal-aware fallback.

**AOTMiT raporty** mają standardowo następujące sekcje:
- Problem decyzyjny
- Skuteczność kliniczna
- Bezpieczeństwo
- Analiza ekonomiczna
- Wpływ na budżet
- Rekomendacje innych agencji (HTA)

**MZ obwieszczenia + programy lekowe B.xx** mają sekcje:
- Kryteria włączenia do programu
- Schemat dawkowania w programie
- Badania monitorujące
- Wyłączenia z programu
- Katalog ryczałtów (jeśli applicable)

**NFZ Zarządzenia Prezesa** mają operacjonalne sekcje:
- Zakres świadczeń
- Wymagane badania monitorujące
- Zasady billing programu
- Wyłączenia z programu

**Implementacja named-section detection:** per-source dictionary regex patterns w `main_project/src/chunking/legal.py`. Wzorce z (a) tolerance dla wariantów typografii (np. *„§ 1"* vs *„§ 1."* vs *„§1"*), (b) opcjonalnymi labels (*„I. Wymagane badania"* vs *„Wymagane badania"*).

**Legal-aware fallback:** dla dokumentów, w których named sections nie są detected (lub są partial — np. tylko 2 z 6 expected), fallback chunking respektuje **legal structural markers**:

- **Paragrafy** (§) — najwyższy priorytet boundary
- **Punkty** (1., 2., 3., …) — średni priorytet
- **Litery** (a), b), c), …) — niski priorytet
- **Maximum chunk size 1024 tokenów** z 64-token overlap

To respektuje konwencję polskiego prawa, gdzie semantyczna integralność jest na poziomie paragrafu (§) i wewnątrz paragrafu — punktu numerowanego.

### 4.4.4 Strategia D — Recursive markdown / heading-based (journals + adjacencies)

Strata 5 (OA journals) zawiera artykuły naukowe ze strukturą **Wstęp / Metody / Wyniki / Dyskusja / Wnioski / Bibliografia** (IMRAD). Strata 6 (DHPC, lista braków) zawiera krótkie focused alerty.

**Implementacja:** recursive markdown splitter z LangChain / LlamaIndex `MarkdownTextSplitter` lub własną prostą implementacją z trzema poziomami split:

1. Heading H1 (`# Wstęp`) — primary boundary
2. Heading H2 (`## Materiał i metody`) — secondary
3. Paragrafy + sentence boundaries — fallback

**Chunk size:** 512 tokenów z 50-token overlap (standard RAG default, sweet spot dla polish-reranker-roberta-v3 context window).

**Edge case dla DHPC i list braków:** dokumenty są typowo krótkie (≤ 500 tokenów), więc tworzą **jeden chunk** = cały dokument. Nie ma splittingu.

### 4.4.5 Walidacja chunkingu na pełnym korpusie

Po implementacji wszystkich czterech strategii w Iteracji 1, walidacja:

1. **Coverage** — % oryginalnego tekstu który trafił do jakiegoś chunku. Target: ≥ 99% (residual = preamble PDF, footer page numbers — celowo dropped).
2. **Section detection rate** — per ChPL i Ulotka, % sekcji canonical wykrytych. Target: ≥ 95% dla sekcji obowiązkowych (1, 4.1, 4.2, 4.3, 4.4, 4.5, 4.8 dla ChPL; 1, 2, 3, 4 dla Ulotki).
3. **Chunk size distribution** per strategia — verify że średnia mieści się w expected range.
4. **Manual spot-check** — 50 random chunków sprawdzonych przez autorkę pod kątem semantic coherence (czy chunk nie jest rozcięty w środku zdania, czy nie miesza dwóch sekcji).

**Tabela 4.4** (placeholder): Walidacja chunkingu post-Iteracja 1.

| Metryka | Target | Wartość obserwowana | Pass/Fail |
|---|---:|---:|---|
| Coverage (% tekstu w chunkach) | ≥ 99% | 🟡 TBD | 🟡 |
| ChPL section detection rate | ≥ 95% | 🟡 TBD | 🟡 |
| Ulotka section detection rate | ≥ 95% | 🟡 TBD | 🟡 |
| AOTMiT section detection rate | ≥ 80% | 🟡 TBD | 🟡 |
| NFZ section detection rate | ≥ 80% | 🟡 TBD | 🟡 |
| Manual semantic coherence (50 chunks) | ≥ 90% | 🟡 TBD | 🟡 |

## 4.5 Embedding-space analysis (UMAP)

> **Placeholder data flag:** ta sekcja zawiera wyłącznie methodology; figury i statystyki (silhouette score, cluster cohesion) — `🟡 TBD post-Iteracja 1`.

### 4.5.1 Cele analizy

Wizualizacja embedding-space ma trzy cele:

1. **Walidacja BGE-M3 jako frozen embedder** — czy out-of-the-box BGE-M3 generuje semantycznie sensowne embeddings dla polskiej farmakologii? Hipoteza: **tak**, ale z domain-specific weak spots (np. terminologia łacińsko-polska, kody ATC).
2. **Diagnostyka klastrów per ATC class** — czy chunki ChPL z tej samej klasy ATC tworzą wizualnie zwarte klastry? Jeśli tak, BGE-M3 capturuje pharmacology semantics; jeśli nie, retrieval bazujący wyłącznie na BGE-M3 ma problem precision i tym ważniejszy jest reranker downstream.
3. **Cross-register cluster overlap** — kluczowa preview RQ5: czy chunki ChPL i Ulotka tego samego leku są **blisko siebie** w embedding space? Jeśli już są blisko, cross-register retrieval może być łatwiejsze niż oczekiwane (marginal gain z retreningu); jeśli daleko, więcej do uczenia (significant gain expected).

### 4.5.2 Methodology UMAP

UMAP (Uniform Manifold Approximation and Projection) jest wybrany jako primary dimension reduction technique zamiast t-SNE z trzech powodów [^umap2]:

[^umap2]: McInnes L., Healy J., Saul N., Großberger L. (2018). *UMAP: Uniform Manifold Approximation and Projection*. Journal of Open Source Software 3(29), 861. 🟡 Verify via citation-checker.

1. **Preserve global structure** — UMAP zachowuje zarówno local jak i global topology, t-SNE preserves głównie local.
2. **Computational efficiency** — UMAP scaling lepiej dla n > 5000 punktów (planowany dataset: ~20k chunks).
3. **Reproducibility** — UMAP jest deterministic z fixed random_state, t-SNE ma stochastic behavior między runs.

**Hyperparameters UMAP** (zafiksowane w `configs/umap.yaml`):

```yaml
n_neighbors: 30          # local vs global trade-off; 30 = moderate
min_dist: 0.1            # cluster separation; 0.1 = tight clusters
n_components: 2          # 2-D for visualization
metric: "cosine"         # appropriate for L2-normalized BGE-M3 embeddings
random_state: 42         # reproducibility
```

**Sample size:** 5000 chunków (random sample, stratified by strata) — pełen 20k jest computationally feasible ale figura staje się nieczytelna.

**Color encoding:** w 3 wariantach figury 4.3 (osobne sub-figures):
- (a) ATC Level 1 — 14 kolorów (A, B, C, …, V) — diagnostyka per-class clustering
- (b) Strata — 6 kolorów — diagnostyka per-source clustering
- (c) Register (professional / lay) — 2 kolory — preview RQ5

### 4.5.3 Quantitative cluster quality

Obok wizualizacji, quantitative metrics:

- **Silhouette score** per cluster definition (ATC class, strata, register) — wartości w `[-1, 1]`, > 0.5 = good clustering, 0.25–0.5 = moderate, < 0.25 = weak.
- **Intra-class vs inter-class cosine distance** ratio — średnia distance między chunkami tej samej ATC class vs między różnymi ATC classes.

**Tabela 4.5** (placeholder): Quantitative cluster quality.

| Cluster definition | Silhouette score | Intra/inter ratio | Interpretacja |
|---|---:|---:|---|
| ATC Level 1 (14 classes) | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| Strata (6 sources) | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| Register (professional / lay) | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| Paired ChPL↔Ulotka (per drug) | 🟡 TBD | 🟡 TBD | 🟡 TBD |

**Szablon interpretacyjny (do wypełnienia post-Iteracja 1):**

> *Silhouette score dla ATC Level 1 = [TBD]; jeśli > 0.4 ⇒ BGE-M3 capturuje pharmacology semantics out-of-the-box, reranker poprawia precision na top-k bez fundamentalnej zmiany ranking; jeśli 0.2–0.4 ⇒ moderate clustering, reranker fine-tuning ma zadanie distinguish między bliskimi semantically klasami; jeśli < 0.2 ⇒ słabe out-of-the-box semantics, reranker fine-tuning critical dla przyzwoitej jakości retrievalu.*

> *Silhouette score dla Register = [TBD]; jeśli high (> 0.5) ⇒ embeddings ChPL i Ulotki wyraźnie separowane → cross-register retrieval (RQ5) wymaga znaczącej intervention treningowej (model musi uczyć się traktować różne registers jako semantically equivalent); jeśli low (< 0.2) ⇒ register difference jest słaby w embedding space, RQ5 baseline może już działać dobrze, marginal gain z retreningu cross-register.*

**Figura 4.3 (a–c): Projekcja UMAP embeddings BGE-M3 (TBD post-Iteracja 1).**

## 4.6 OCR quality assessment

> **Placeholder data flag:** rate OCR jest pre-condition Iteracji 0 z target < 15% (kill criteria > 25% — `sources_catalog.md` § Iteracja 0 pre-condition #6). Wartości empiryczne — `🟡 TBD post-Iteracja 1`.

### 4.6.1 Methodology detekcji OCR vs text-layer

Każdy PDF w korpusie jest klasyfikowany jako **text-layer** lub **scanned-only** przez:

```python
# main_project/src/preprocess/ocr_detect.py — pseudocode
import pdfplumber

def has_text_layer(pdf_path: str, min_chars_per_page: int = 100) -> bool:
    """Detect if PDF has extractable text layer."""
    with pdfplumber.open(pdf_path) as pdf:
        total_chars = sum(len(page.extract_text() or "") for page in pdf.pages)
        avg_chars_per_page = total_chars / max(len(pdf.pages), 1)
        return avg_chars_per_page >= min_chars_per_page
```

**Threshold:** średnio ≥ 100 znaków per strona. Niższe wartości typowo sygnalizują (a) PDF skanowany bez OCR, (b) PDF z text-layer ale bardzo krótki dokument, (c) PDF z corrupted text-layer (encoding issues).

**Klasyfikacja trzy-poziomowa:**

| Klasa | Definicja | Akcja w pipeline |
|---|---|---|
| **TEXT** | ≥ 100 chars/page average | Direct extraction via pdfplumber |
| **SCANNED** | < 100 chars/page, ale > 0 stron | OCR via Tesseract `-l pol` |
| **EMPTY** | 0 stron lub PDF corrupted | Skip + flag w error log |

### 4.6.2 OCR pipeline dla scanned

Dla dokumentów klasy SCANNED, pipeline OCR:

1. **Konwersja PDF → PNG** per strona (pdf2image, dpi=300 — sweet spot dla pol OCR)
2. **Tesseract `-l pol --psm 1`** — `--psm 1` (page segmentation mode 1) wykonuje automatic page segmentation z OSD (orientation and script detection)
3. **Post-processing** — (a) usuwanie noise characters typowych dla OCR (`|`, `~`, replacement of `0` ↔ `O`, `1` ↔ `l` ↔ `I` w kontekście wymaganym przez słownik DCI), (b) re-application Unicode NFC z sekcji 4.3.1.
4. **Quality scoring** — ratio detected polish words (z słownika ~300k polskich form) do total words. Ratio < 0.7 ⇒ flag `ocr_quality_low`.

### 4.6.3 Walidacja OCR rate w sample

W Iteracji 0a, pre-condition #6 wymaga zmierzenia OCR rate na sample 100 ChPL PDF.

**Tabela 4.6** (placeholder): OCR quality per strata.

| Strata | n PDFs sampled | TEXT | SCANNED | EMPTY | OCR rate |
|---|---:|---:|---:|---:|---:|
| 1. ChPL | 100 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD% |
| 2. Ulotki | 100 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD% |
| 3. AOTMiT + MZ | 100 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD% |
| 4. NFZ | 100 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD% |
| **Razem** | 400 | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD% |

**Szablon interpretacyjny:**

> *Tabela 4.6 pokazuje OCR rate ogólny [X]%. Pre-condition #6 z Iteracji 0 wymagała < 15% (acceptance), z kill criteria > 25%. Wynik [X]% [mieści się w target / mieści się w warning band 15–24% / przekracza kill criteria]. [Jeśli warning band: pipeline aktywuje Tesseract z flagging w R8 limitations + monitoring jakości OCR; jeśli kill criteria: re-evaluation per DEC-001].*

> *Per-strata: najwyższa OCR rate w [strata] ([X]%), co jest spójne z [hipoteza: starsze ChPL pre-2010 / oryginalnie scanowane AOTMiT raporty z bipold]. Najniższa OCR rate w [strata Ulotek] (oczekiwane near-zero) — Ulotki są generowane elektronicznie przez MAH-ów z text-layer.*

### 4.6.4 Wpływ OCR na jakość retrievalu (do walidacji w R7)

Otwarte pytanie: czy chunki z `ocr_quality_low` flag mają systematycznie gorsze ranking score? Hipoteza: tak, ale efekt jest marginal (większość OCR jest acceptable jakości dzięki Tesseract + Polish dictionary). Walidacja w R7 sekcja Error analysis (Defense scaffolding pkt 2 — kategoria błędu *„OCR artifact"* z 6-poziomowej taksonomii).

## 4.7 Paired ChPL↔Ulotka analysis (kluczowa dla RQ5 / DEC-002)

Ta sekcja jest **kluczowa dla RQ5** zgodnie z DEC-002. Paired analysis dostarcza grunt empiryczny pod (a) generację cross-register pairs do training, (b) preview difficulty cross-register retrievalu (sekcja 4.5.3), (c) defensję scope DEC-002 w R5 i obronie. Methodology pełna; wartości empiryczne — `🟡 TBD post-Iteracja 1`.

### 4.7.1 Definicja "paired" + alignment integrity

Pełna definicja "paired ChPL↔Ulotka" w `sources_catalog.md` § Strata 2 § Definicja "paired ChPL↔Ulotka". W skrócie: dwa dokumenty z **tej samej decyzji administracyjnej URPL** dla tego samego `productID`, w synchronizowanej `data_modyfikacji`, opisujące ten sam zakres semantyczny w różnych rejestrach językowych.

**Alignment integrity** weryfikowana w Iteracji 0a (pre-condition #5) na sample 100 par leków, z **competence-stratified spot-check** — 10 par z psychiatrycznej podgrupy ATC N05/N06 sprawdzonych manualnie przez autorkę (semantic verification), 90 par non-psych weryfikowanych proxy signal (URL-e w XML attributes oba zwracają HTTP 200 + valid PDF).

**Acceptance threshold:** ≥ 90% par z full pairing integrity. Wartość obserwowana — `🟡 TBD post-Iteracja 0`.

### 4.7.2 Length ratio statistics

Hipoteza eksploracyjna (z literatury cross-register medical NLP — Cao 2020, Devaraj 2021): **Ulotki są systematycznie krótsze niż odpowiadające ChPL**, ratio Ulotka:ChPL ~ 0.30–0.50. Powód: (a) Ulotka pomija sekcje 5 (Właściwości farmakologiczne) i 6 (Dane farmaceutyczne) — głęboko techniczne; (b) Ulotka konsoliduje 4 sekcje ChPL (4.3 + 4.4 + 4.5 + 4.6) w pojedynczą sekcję 2 (Informacje ważne przed); (c) Ulotka używa krótszych zdań, prostszego vocabulary.

**Methodology:**

```python
# main_project/src/eda/paired.py — pseudocode
def length_ratio_per_pair(chpl_text: str, ulotka_text: str) -> dict:
    chpl_tokens = bge_m3_tokenizer.tokenize(chpl_text)
    ulotka_tokens = bge_m3_tokenizer.tokenize(ulotka_text)
    return {
        "chpl_n_tokens": len(chpl_tokens),
        "ulotka_n_tokens": len(ulotka_tokens),
        "ratio": len(ulotka_tokens) / max(len(chpl_tokens), 1),
    }

# Aggregate over 900 paired pairs
ratios = [length_ratio_per_pair(chpl, ulotka)["ratio"] for chpl, ulotka in paired_corpus]
stats = {
    "mean": np.mean(ratios), "median": np.median(ratios),
    "std": np.std(ratios), "p5": np.percentile(ratios, 5),
    "p95": np.percentile(ratios, 95),
}
```

**Tabela 4.7** (placeholder): Length ratio Ulotka:ChPL statistics na 900 paired pairs.

| Metryka | Wartość | Hipoteza H_length |
|---|---:|---|
| Mean ratio | 🟡 TBD | ~0.40 |
| Median ratio | 🟡 TBD | ~0.40 |
| Std ratio | 🟡 TBD | ~0.10 |
| p5 ratio | 🟡 TBD | ~0.25 |
| p95 ratio | 🟡 TBD | ~0.60 |
| % par z ratio < 0.20 | 🟡 TBD | < 5% (outliers) |
| % par z ratio > 0.80 | 🟡 TBD | < 5% (outliers — krótkie ChPL OTC) |

**Szablon interpretacyjny:**

> *Tabela 4.7 wskazuje średni length ratio Ulotka:ChPL = [TBD], median [TBD]. Hipoteza H_length (ratio ~ 0.30–0.50) [potwierdzona / odrzucona]. Konsekwencje dla cross-register pairs (RQ5): typowy lay query (z Ulotki) jest [N]× krótszy niż gold professional passage (z ChPL), co implikuje length asymmetry dla rerankera. Length-balanced batch sampling w trainingu (R6) musi adresować to asymmetry — strategia: zarejestrowane pairs używają full passage length z padding, NIE truncation passage do długości query.*

> *Outliers (ratio > 0.80) to typowo ChPL leków OTC o ograniczonych wskazaniach (np. preparaty witaminowe), gdzie ChPL i Ulotka są zbliżone długością. Outliers (ratio < 0.20) to typowo ChPL leków onkologicznych z bardzo długą sekcją 4.4 i 4.5. Oba typy outliers są retained w korpusie z flag w metadata.*

**Figura 4.4: Histogram length ratio Ulotka:ChPL z annotated medianą + percentyle (TBD post-Iteracja 1).**

### 4.7.3 Lexical divergence professional/lay

Hipoteza: ChPL używa systematycznie więcej **terminologii łacińskiej** (DCI nazwy, łacińskie nazwy struktur anatomicznych, *„per os"*, *„intramuscularis"*, *„contraindicationes"*) niż Ulotka, która preferuje polskie ekwiwalenty (*„doustnie"*, *„domięśniowo"*, *„przeciwwskazania"*).

**Methodology — proste measures (NIE sophisticated NLP):**

1. **Łacińska terminologia indicator** — zliczenie wystąpień:
   - Końcówek typowo łacińskich (`-tio`, `-ans`, `-um`, `-ica`, `-icus`, `-osus`)
   - Zlatynizowanych zwrotów (lista ~100 form: *„per os"*, *„i.v."*, *„i.m."*, *„p.o."*, *„s.c."*, *„q.d."*, *„b.i.d."*, *„in vitro"*, *„in vivo"*, …)
   - Międzynarodowych nazw substancji DCI (lista z Indeks DCI)

2. **Lay vocabulary indicator** — zliczenie wystąpień:
   - Form imperatywnych w 2. osobie (*„weź"*, *„zażyj"*, *„nie stosuj"*, *„zapytaj"*) — typowe dla Ulotek
   - Słów potocznych (*„zwykle"*, *„czasami"*, *„rzadko"*, *„może"*, *„ważne"*) — high frequency w Ulotkach
   - Pierwszej osoby liczby pojedynczej (*„zapomniałem"*, *„mam"*, *„mogę"*) — wyłącznie Ulotki

**Tabela 4.8** (placeholder): Lexical indicators ChPL vs Ulotka (sample 900 par).

| Indicator | ChPL mean per doc | Ulotka mean per doc | Ratio ChPL:Ulotka |
|---|---:|---:|---:|
| Łacińskie końcówki (`-tio`, `-um`, …) | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| Zlatynizowane zwroty (*per os*, *i.v.*) | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| Międzynarodowe nazwy DCI | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| Imperatyw 2. osoby | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| Słowa potoczne (*zwykle*, *czasami*) | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| 1. osoba liczby pojedynczej | 🟡 TBD | 🟡 TBD | 🟡 TBD |

**Szablon interpretacyjny:**

> *Tabela 4.8 dokumentuje wyraźne lexical divergence: ChPL ma [N]× więcej zlatynizowanych zwrotów per dokument niż Ulotka, podczas gdy Ulotka ma [M]× więcej form imperatywnych. To potwierdza, że register difference jest **leksykalnie znaczący** — co przekłada się na expectation, że BGE-M3 (case-sensitive, multilingual) będzie reprezentować te same semantyczne treści jako odległe punkty w embedding space. Jest to bezpośredni preview sekcji 4.5.3 (cross-register cluster overlap) oraz uzasadnienie dla hard negative L4 (cross-register confusion) z `02b_konspekt II.4.6`.*

### 4.7.4 Sentence complexity

Hipoteza: zdania w ChPL są systematycznie **dłuższe** i bardziej **złożone** syntaktycznie niż w Ulotce.

**Methodology — proste approximations dla polszczyzny:**

1. **Mean sentence length** (w słowach) — średnia z wszystkich zdań w dokumencie po segmentacji (sekcja 4.3.4).
2. **Median sentence length** — bardziej robust niż mean wobec outliers (długie zdania bibliograficzne).
3. **Polish syllable count proxy** — Polish syllable count ≈ count of vowels (a, e, i, o, u, y, ą, ę), z corrections dla *„ia"*, *„io"* itp. **NIE używamy** klasycznych readability indices (Flesch) — są kalibrowane dla angielskiego. **Używamy** Pisarek Index (polish-specific) jako proxy [^pisarek]:

[^pisarek]: Pisarek W. (1969). *Jak mierzyć zrozumiałość tekstu?*. Zeszyty Prasoznawcze 4. 🟡 Verify exact bibliographic details via citation-checker.

```
Pisarek_Index = (mean_sentence_length_words + percent_long_words) / 2
```

gdzie `percent_long_words` = % słów o ≥ 4 sylabach. Wyższy Pisarek_Index = trudniejszy tekst.

**Tabela 4.9** (placeholder): Sentence complexity ChPL vs Ulotka.

| Metryka | ChPL | Ulotka | Ratio | Interpretacja |
|---|---:|---:|---:|---|
| Mean sentence length (words) | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| Median sentence length (words) | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| % słów ≥ 4 sylaby | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| Pisarek Index | 🟡 TBD | 🟡 TBD | 🟡 TBD | 🟡 TBD |

**Szablon interpretacyjny:**

> *Tabela 4.9 dokumentuje, że ChPL ma mean sentence length = [N] słów vs Ulotka [M] słów ([ratio]× dłuższe), oraz Pisarek Index [PI_chpl] vs [PI_ulotka]. To potwierdza hipotezę o systematycznym difference w sentence complexity. Konsekwencje dla rerankera: lay queries (z Ulotki) są krótkie i prostą syntaktycznie, podczas gdy gold professional passages (z ChPL) są długie i złożone — model musi nauczyć się **abstrahować od długości i złożoności** jako sygnał (NIE używać ich jako proxy dla relevance), bo cross-register relevance jest semantyczne, nie stylistyczne.*

### 4.7.5 Section-level alignment

Pełen mapping ChPL ↔ Ulotka per sekcja jest w sekcji 4.4.2 (tabela end-of-section). Tutaj weryfikacja, **czy faktyczna treść w mapped sekcjach faktycznie odpowiada semantycznie**.

**Methodology — semantic similarity między mapped sekcjami:**

1. Per para leków (900 par), per pair (ChPL_section, Ulotka_section) z mapping z sekcji 4.4.2:
   - Compute BGE-M3 embedding obu sekcji
   - Compute cosine similarity
2. Aggregate per typ mapping (direct vs many-to-one)

**Tabela 4.10** (placeholder): Section-level cosine similarity per mapping type.

| ChPL → Ulotka mapping | Mapping type | Mean cosine sim | Median | Interpretation |
|---|---|---:|---:|---|
| 4.1 Wskazania → 1 Co to jest lek | Direct | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| 4.2 Dawkowanie → 3 Jak przyjmować | Direct | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| {4.3 + 4.4 + 4.5 + 4.6} → 2 Informacje ważne przed | Many-to-one | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| 4.8 Działania niepożądane → 4 Możliwe działania niepożądane | Direct | 🟡 TBD | 🟡 TBD | 🟡 TBD |
| 6 Storage → 5 Jak przechowywać | Direct | 🟡 TBD | 🟡 TBD | 🟡 TBD |

**Szablon interpretacyjny:**

> *Tabela 4.10 pokazuje, że mapping {4.3+4.4+4.5+4.6 ChPL} → {2 Ulotka} ma najniższą cosine similarity (= [TBD]), co jest spójne z faktem, że Ulotka konsoliduje 4 sekcje ChPL — many-to-one mapping zawsze będzie miał lower semantic similarity niż direct one-to-one. Direct mapping (4.1 → 1, 4.2 → 3) ma cosine sim [TBD] — wartość [moderate / high] sugeruje, że BGE-M3 captures cross-register equivalence dla tych prostych mapping. Konsekwencje dla cross-register pairs w training (RQ5): pairs z direct mapping są **łatwiejszym sygnałem** dla rerankera, pairs z many-to-one (ChPL 4.3 jako gold dla query "co zrobić jak mam alergię" z Ulotki 2) są **trudniejszym** — potrzebny strategy do balanced sampling typów mapping w training.*

**Figura 4.5: Boxplot cosine similarity per typ mapping (TBD post-Iteracja 1).**

### 4.7.6 Generacja cross-register pairs do training i evaluation

Output sekcji 4.7 jest **direct input** do generacji 1800 cross-register pairs dla evaluation RQ5 (zgodnie z `02b_konspekt II.3.3` § Setup ewaluacyjny):

- 900 lay→pro pairs: lay query = pierwsze zdanie sekcji Ulotki, gold = mapped sekcja ChPL
- 900 pro→lay pairs: pro query = pierwsze zdanie sekcji ChPL, gold = mapped sekcja Ulotki

Plus **5400 cross-register training pairs** dla rerankera (zgodnie z `sources_catalog.md` § Strata 2 § Mapping na training data) z hard negatives 4-poziomowych (II.4.6).

## 4.8 Eval set sampling validation — 200 par psych subset

> **Placeholder data flag:** eval set 200 par jest budowany w Iteracji 1 manualnie przez autorkę. Statystyki eval set — `🟡 TBD post-Iteracja 1`.

### 4.8.1 Recapitulation świadomej decyzji

Eval set podstawowy (200 par gold standard) jest próbkowany **wyłącznie z psychiatrycznej podgrupy korpusu** (ATC N05/N06), zgodnie ze świadomą decyzją z DEC-001 oraz `02b_konspekt II.4.3`. Uzasadnienie: leverage manual validation kompetencji autorki dla rygorystycznej walidacji LLM-as-judge w RQ2/H2 (najsłabiej zabezpieczona hipoteza).

**Eval set wąski (psych)**, **training corpus szeroki (cała farmakologia)** — explicit in R5 sekcja Architektura danych.

### 4.8.2 Distribution analysis eval set

Po wygenerowaniu eval set w Iteracji 1, walidacja distribution:

**Tabela 4.11** (placeholder): Distribution eval set 200 par.

| Wymiar | Sub-kategoria | n | % |
|---|---|---:|---:|
| **ATC** | N05A (Antipsychotica) | 🟡 TBD | 🟡 TBD |
|  | N05B (Anxiolytica) | 🟡 TBD | 🟡 TBD |
|  | N05C (Hypnotica + Sedativa) | 🟡 TBD | 🟡 TBD |
|  | N06A (Antidepressiva) | 🟡 TBD | 🟡 TBD |
|  | N06B (Psychostimulantia) | 🟡 TBD | 🟡 TBD |
|  | N06D (Anti-dementia) | 🟡 TBD | 🟡 TBD |
| **ChPL section** | 4.1 Wskazania | 🟡 TBD | 🟡 TBD |
|  | 4.2 Dawkowanie | 🟡 TBD | 🟡 TBD |
|  | 4.3 Przeciwwskazania | 🟡 TBD | 🟡 TBD |
|  | 4.4 Ostrzeżenia | 🟡 TBD | 🟡 TBD |
|  | 4.5 Interakcje | 🟡 TBD | 🟡 TBD |
|  | 4.8 Działania niepożądane | 🟡 TBD | 🟡 TBD |
| **Query type** | Faktoidalne ("jaka jest dawka") | 🟡 TBD | 🟡 TBD |
|  | Diagnostyczne ("jakie są przeciwwskazania") | 🟡 TBD | 🟡 TBD |
|  | Decyzyjne ("czy mogę X w Y sytuacji") | 🟡 TBD | 🟡 TBD |
| **Query length** | Mean tokens | 🟡 TBD | n/a |
|  | Median tokens | 🟡 TBD | n/a |

**Szablon interpretacyjny:**

> *Tabela 4.11 pokazuje, że eval set 200 par jest [zbalansowany / niezrównoważony] między subkategoriami ATC w obrębie N05/N06 ([dominacja N05A jeśli > 40%; balanced jeśli każda subkategoria 10–25%]). Distribution po sekcji ChPL: [najliczniejsze 4.X i 4.Y, marginalne 4.Z]. To distribution informuje o **zewnętrznej validity** wyników H1 (RQ1) — wyniki obowiązują dla [tych ATC subkategorii i tych typów query], ekstrapolacja na inne subkategorie wymaga oddzielnej walidacji. Limitation explicit w R8.*

### 4.8.3 Inter-annotator agreement (single annotator caveat)

**Caveat metodologiczny:** eval set jest annotated przez **jednego annotatora** (autorkę). Inter-annotator agreement statistics typowe dla manual gold standard nie są dostępne dla single-annotator setup. Mitygacja:

1. **Re-annotation 50 par po 7 dniach** — intra-annotator consistency check. Target: agreement ≥ 85% (Cohen's kappa proxy dla single annotator).
2. **Wynik zgłoszony explicit w R7** — niska intra-annotator consistency = sygnał ambiguity w eval set, który flag w analizie.

**Tabela 4.12** (placeholder): Intra-annotator consistency.

| Metryka | Wartość |
|---|---:|
| n par re-annotated | 50 |
| Strict agreement (same label) | 🟡 TBD |
| Cohen's kappa proxy | 🟡 TBD |
| Pairs flagged dla disagreement | 🟡 TBD |

## 4.9 Wnioski dla architektury pipeline'u

Synteza implikacji EDA dla decyzji architektonicznych w R5 (Architektura) i R6 (Modele).

### 4.9.1 Implikacje dla chunkingu (R5)

- **Section-aware chunking** dla ChPL i Ulotki (strategie A, B z sekcji 4.4) jest uzasadnione przez **deterministyczną strukturę QRD** — bez tego naive 512-token sliding window rozcina logiczne sekcje (np. 4.3 Przeciwwskazania w środku numerowanej listy).
- **Per-source named-section** dla HTA i NFZ (strategia C) jest preferowane nad uniwersalny chunker, ponieważ **strukturalne nagłówki zawierają semantyczny sygnał** (*„Wymagane badania monitorujące"* jest naturalnym query — chunk granica per nagłówek = naturalny passage).
- **Recursive markdown** dla journals (strategia D) jest fallback — IMRAD structure jest mniej standardyzowana między czasopismami, recursive split z 512-token window jest pragmatyczny.

### 4.9.2 Implikacje dla rerankera (R6)

- **Length asymmetry** lay queries vs professional passages (sekcja 4.7.2) ⇒ length-balanced batch sampling w training, NIE truncation passages.
- **Lexical divergence** professional/lay (sekcja 4.7.3) ⇒ **uzasadnienie hard negatives L4** (cross-register confusion) z 4-poziomowej taksonomii (`02b_konspekt II.4.6`). Bez L4 model nie uczy się rozróżniać semantic relevance od stylistic appropriateness.
- **Section-level alignment** ChPL ↔ Ulotka (sekcja 4.7.5) ⇒ kalibracja proporcji direct vs many-to-one mapping w cross-register training pairs (np. 70% direct, 30% many-to-one).

### 4.9.3 Implikacje dla embedderingu (R5)

- **Cluster cohesion silhouette score** per ATC class (sekcja 4.5.3) jest decyzją baseline-or-fine-tune dla embeddera. **W niniejszej pracy embedder pozostaje frozen** (BGE-M3, decyzja w R5 sekcja 5.X) — silhouette > 0.3 jest minimum acceptable. Niżej ⇒ R8 future work *„embedder fine-tuning"*.

### 4.9.4 Implikacje dla evaluation (R6, R7)

- **Eval set distribution** (sekcja 4.8.2) ogranicza external validity wyników H1 do subkategorii ATC reprezentowanych w eval set. Explicit w R8 limitations.
- **Cross-register difficulty preview** (sekcja 4.5.3 cross-register cluster overlap) jest **early signal** dla expected magnitude H5. Jeśli klastry ChPL i Ulotka tego samego leku są blisko ⇒ H5 może być satisfied marginal gain z retreningu; jeśli daleko ⇒ significant gain expected.

### 4.9.5 Implikacje dla świadomych biases (R3 + R8)

EDA dodaje do listy z R3 sekcja 3.10 dwa nowe biases:

- **Bias #6 (encoding heterogeneity)** — pre-2015 ChPL z dropped diakrytykami (sekcja 4.3.2), reprezentacja jako separate flag w metadata, retained w korpusie z note. Konsekwencja: training reranker uczy się pisowni z + bez diakrytyków jako equivalent, ale embedder BGE-M3 może treats je differently.
- **Bias #7 (single annotator eval set)** — eval set 200 par by single annotator (sekcja 4.8.3). Mitygacja: intra-annotator consistency check. Konsekwencja: H2 (LLM-judge agreement) musi być interpretowane z caveat single-rater proxy.

### 4.9.6 Mapowanie wniosków na rozdziały dalsze

| Wniosek z EDA (sekcja) | Implikacja w R5/R6/R7/R8 | Lokalizacja |
|---|---|---|
| Section-aware chunking ChPL+Ulotka uzasadniony (4.4.1, 4.4.2) | Implementation w `main_project/src/chunking/` + Diagram 5.X (data ingestion) | R5 sekcja 5.X |
| Length asymmetry (4.7.2) | Length-balanced batch sampling | R6 sekcja 6.X |
| Lexical divergence (4.7.3) | Uzasadnienie hard negatives L4 | R6 sekcja 6.X |
| Section-level alignment (4.7.5) | Kalibracja direct vs many-to-one cross-register pairs | R6 sekcja 6.X |
| Cross-register cluster preview (4.5.3) | Early signal H5 magnitude | R7 sekcja 7.X (RQ5 results) |
| Eval set distribution (4.8.2) | External validity bounds | R8 limitations |
| Encoding heterogeneity bias (4.3.2 + 4.9.5) | Bias #6 dodany do listy | R8 limitations |
| Single annotator caveat (4.8.3 + 4.9.5) | Bias #7 dodany do listy | R8 limitations |

## Bibliografia (placeholder, do uzupełnienia w citation pass)

[^tesseract] Smith R. (2007). *An Overview of the Tesseract OCR Engine*. ICDAR. 🟡 Verify via citation-checker.
[^spacy_polish] Honnibal M., Montani I. (2017). *spaCy 2: Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing*. 🟡 Verify version + Polish model release year via citation-checker.
[^umap] McInnes L., Healy J., Melville J. (2018). *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*. arXiv:1802.03426. 🟡 Verify via citation-checker.
[^stanza] Qi P., Zhang Y., Zhang Y., Bolton J., Manning C.D. (2020). *Stanza: A Python natural language processing toolkit for many human languages*. ACL 2020 demo. 🟡 Verify via citation-checker.
[^umap2] McInnes L., Healy J., Saul N., Großberger L. (2018). *UMAP: Uniform Manifold Approximation and Projection*. Journal of Open Source Software 3(29), 861. 🟡 Verify via citation-checker.
[^pisarek] Pisarek W. (1969). *Jak mierzyć zrozumiałość tekstu?*. Zeszyty Prasoznawcze 4. 🟡 Verify exact bibliographic details via citation-checker.

**Dodatkowe pozycje do weryfikacji w citation pass (post-Iteracja 1):**

- BGE-M3 paper — Chen J. et al. (2024). *M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings*. arXiv:2402.03216. 🟡 Verify via citation-checker.
- pdfplumber — Singer-Vine J. (2015). *pdfplumber*. GitHub. 🟡 Verify via citation-checker.
- Cao Y. et al. (2020). *Expertise Style Transfer*. ACL 2020. (cytowana w DEC-002, do reuse w R2 i R4)
- Devaraj A. et al. (2021). *Paragraph-level Simplification of Medical Texts*. 🟡 Verify venue.
- Grabowski Ł. (2017). *English-Polish comparable PIL corpus*. (closest prior art dla DEC-002 / RQ5)
- Karpukhin V. et al. (2020). *Dense Passage Retrieval for Open-Domain Question Answering*. EMNLP 2020. (DPR — origin hard negative mining methodology)
- Schwarz E. (1958) *FOG Index* lub equivalent dla polish readability. 🟡 Niepewne. Pisarek 1969 jako primary polish-specific.

---

**Status drafu:** outline + methodology + standaryzacja + chunking 100% napisane. Sekcje 4.2, 4.5, 4.6, 4.8 mają placeholder tabele i figury z explicit `🟡 TBD post-Iteracja 1` + szablony interpretacyjne typu *„jeśli X, to Z"*. Sekcja 4.7 (paired analysis dla RQ5) — methodology pełna, wartości po Iteracji 1.

**Co dalej w tym rozdziale:**
1. Sign-off autorki na outline + methodology (≤ 1h)
2. Po Iteracji 1: wypełnienie placeholderów numerami z `main_project/reports/eda/` (≤ 4h)
3. Citation pass via `/citations` na finalnej wersji (≤ 1h)
