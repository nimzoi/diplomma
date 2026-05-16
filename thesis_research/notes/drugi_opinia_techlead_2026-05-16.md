# Code Review (tech lead) — drafty R3/R4/R5 vs `src/halu/`

**Data:** 2026-05-16
**Reviewer:** Claude (senior tech lead persona, 20+ y ML/MLOps)
**Scope:** R3 (253 LOC), R4 (290 LOC), R5 F1+F2 (297 LOC)
**Cross-ref:** `main_project/src/halu/` (10 modułów, ~3,7k LOC), `data/processed/citationbench_v0.6_2026-05-16/`, `iter0b_poc/results/`
**Today:** 2026-05-16 → arXiv ID `2604.10799` (Apr 2026) jest **valid past date**, NIE phantom (poprawiam błąd poprzedniego reviewera).

---

## TL;DR

Dane są realne (11 000 chunków, 5 402 par halu — zweryfikowane bit-identical w `chunks.jsonl`/`halu_pairs.jsonl`). R3/R4 to wiarygodny opis tego, co JEST. R5 to "specka mieszana z aspiracją" — opisuje 11 kontenerów + 3-tier verifier + probe + citation aligner, podczas gdy `src/probe/`, `src/verifier/`, `src/citation/` to puste foldery z samym `__init__.py`. Najgorszy single issue: drift między fig 5.2 (12 kontenerów z MinIO), tabelą 5.1 (11 kontenerów bez MinIO) i tekstem ("jedenaście w 4 grupach", a grup naprawdę jest 5 = 3+2+2+3+1). Drugi w kolejności: R3 Tab 3.1 deklaruje 8 022 chunków dla "Retrieval corpus" — suma typów = 7 622 (off-by-400). Reszta to numbers-consistency cleanup w 4-6 godzin.

---

## R3 — issues

### Numbers / consistency
- **BLOCKER R3-1:** Tab 3.1 (line 21): `Retrieval corpus = 8 022 chunków`. Realna suma `legal_statute (2541) + legal_ue_directive (1360) + legal_tsue_judgment (29) + legal_court_judgment (534) + legal_uokik_decision (26) + legal_document_pdf (1965) + encyclopedic (1167) = 7 622`. Off-by-400 typo. **Fix:** podmień `8 022` → `7 622` (verified `chunks.jsonl`).
- **WARN R3-2:** Tab 3.1 (line 23): `200 par gold + ~1 000 par silver`. Nigdzie w `src/` ani `data/processed/` nie istnieje gold/silver eval set. `find -name "*gold*"` = 0 wyników. To plan, NIE stan obecny. Konspekt v3.2 mówi ~110-160. **Fix:** dopisz status "Iteracja 5 (planowane)" lub przejdź na 110-160 (defendable scope).
- **WARN R3-3:** §3.4.1 (line 131): `wszystkich rekordów z dziewięciu rodzin źródeł przez dedykowane normalizery`. `grep -c "^def normalize_" normalizers.py` = **10**. 10. normalizer to `normalize_new_source_article` (S6 → ENCYCLOPEDIC). 9 source_types ✓, ale 10 normalizers. **Fix:** "9 typów źródłowych przez 10 normalizerów (typ ENCYCLOPEDIC ma 2 ścieżki: standardowa + S6 articles)".
- **WARN R3-4:** §3.2 (line 47): `UOKiK obejmuje trzy źródła komplementarne. Pierwsze to 60 par...`. Brak ujawnienia że `qa_gold = 60 UOKiK + 373 RF FAQ = 433` (zweryfikowane bezpośrednio z `chunks.jsonl`). RF FAQ jest dorzucone do `qa_gold` w `normalize_encyclopedic()` (linia 295-300 normalizers.py: "Q&A-like shape: source_type=QA_GOLD"). Czytelnik tego nie dowie się z R3. **Fix:** w §3.2 lub §3.3.1 jawnie powiedz: "Pole `qa_gold` zawiera 60 par UOKiK + 373 par RF FAQ ekspansji = łącznie 433 par".

### Schema/code mismatch
- **WARN R3-5:** §3.3.2 (line 106): struktura katalogów deklaruje `splits/   # train/val/test (stratified)`. Realny `ls data/processed/citationbench_v0.6_2026-05-16/` = `DATASET_CARD.md`, `chunks.jsonl`, `halu_pairs.jsonl`. **`splits/` nie istnieje.** Też DATASET_CARD.md §Files też kłamie. **Fix:** usuń `splits/` z drzewka albo dodaj "(zaplanowane w Iteracji 1)".
- **OK R3-6:** §3.3.1 Tab 3.3 codebook `Chunk` schema — zweryfikowane bit-by-bit z `schemas.py:115-165`. Wszystkie 14 pól + typy + opcjonalność matchują. NFC validator (linia 158-165 schemas.py) faktycznie istnieje. ✓
- **OK R3-7:** §3.4.2 Wariant B drop list — zweryfikowane z `chunk_filter.py:STRICT_DROP_ELI_USTAWY` + `STRICT_DROP_S6_SOURCES`. 16 reasons w R3 Tab 4.7 = 7 ELI + 7 S6 + 2 content-based (sn_chf, rf_pure_insurance) = 16. ✓ Implementacja kompletnie zgodna z dokumentacją.
- **OK R3-8:** §3.5.1 Tab 3.4 (5 typów halucynacji) — zweryfikowane z `HaluType` enum w `schemas.py:31-38`. 5 typów ✓, nazwy ✓.

### Eval set scope creep
- **WARN R3-9:** §3.5.3 (line 182): "**140 par hand-annotated przez autorkę** w trakcie weekend hyperfocus burst" + 60 UOKiK = 200 par. Konspekt mówi ~110-160. **Engineering reality check:** 140 par anotacji manualnej z 3-poziomową NLI (entailed/contradicted/neutral) + cross-check evidence = ~2-3 min/para = 5-7 godzin pełnej koncentracji. Weekend hyperfocus to defendable ALE jest twardy plan, NIE plug-in option. **Fix:** zmniejsz target do 100-120 par (defendable: 60 UOKiK + 40-60 manual). Każde +20 par to +1h burnout-risk.

---

## R4 — issues

### Placeholders bloat
- **BLOCKER R4-1:** Liczba placeholderów `{{...}}`:
  - Tab 4.3 (citation coverage) — 18 placeholderów, **całkowicie pusta** (jedna komórka 91,7% wstawiona manualnie). Bez tych liczb sekcja jest content-free.
  - Tab 4.6 (BERTopic 10 klastrów) — **30 placeholderów**. Bez tego sekcja 4.2.6 to vapor.
  - Tab 4.8 (token APT4) — 27 placeholderów. Bez tego sekcja 4.5.2 to placeholder farm.
  - **Quick win:** Tab 4.3 możesz wypełnić w 5 min: `python -c "<...>"` po `chunks.jsonl` + `cited_articles`. Załączam recipe na końcu raportu.
  - BERTopic + UMAP = realny notebook run, 30-60 min compute. Nie do dzisiaj, ale do oddania **musi** być.
  - Token APT4 = wymaga załadowania tokenizera Bielika; 5-15 min compute.

### Internal arithmetic
- **OK R4-2:** Tab 4.5 (halu types) — zweryfikowane bezpośrednio z `halu_pairs.jsonl`:
  ```
  Halu type counts: {'neg': 1560, 'factual_fabrication': 1620,
                     'entity_confusion': 985, 'negation_flip': 467,
                     'temporal_drift': 343, 'paragraph_mis_citation': 427}
  NLI label counts: {'entailed': 1560, 'neutral': 1620, 'contradicted': 2222}
  ```
  Tab 4.5 dokładnie matchuje. Mapping `factual_fabrication → neutral` ✓ z `halu_injector.py:_HALU_TYPE_NLI_LABEL` (linia 271-277). ✓
- **OK R4-3:** Tab 4.4 (categories) — sumuje 27,723 dla multi-label, 14 kategorii ✓ z `Category` enum (`schemas.py:91-112`). Wszystkie 14 wartości ✓.
- **WARN R4-4:** §4.2.1 footnote po Tab 4.1: `Niska liczność legal_tsue_judgment (29) i legal_uokik_decision (26) wynika z charakteru źródeł — TSUE orzeka rocznie w ograniczonej liczbie spraw konsumenckich`. To wymówka — w iter 0 zwykle scrape był zoptymalizowany pod consumer-related, więc ograniczona liczba to scope decision, nie ograniczenie systemu źródłowego. **Fix:** "wynika z świadomego ograniczenia scrape do consumer-related spraw (29 z ~12k TSUE rocznie)".
- **WARN R4-5:** Tab 4.1 (line 31): `qa_gold | 433 | 3.9% | UOKiK Q&A FAQ + ekspansja RF FAQ`. To single-line gest. R4 nie dokumentuje 60+373 splitu. **Fix:** Albo dopisz w R3 (preferowane — to dane), albo footnote pod Tab 4.1: "433 = 60 UOKiK + 373 RF FAQ (treated jako qa_gold w `normalize_encyclopedic`)".

### Standardization claims
- **WARN R4-6:** §4.4.1 (line 199): "Audyt v0.6 potwierdza, że wszystkie 11 000 chunków przechodzi walidator bez błędu". Zweryfikowane: NFC validator jest w `schemas.py:158-165` jako `field_validator("tresc")` — wszystkie 11 000 chunków w `chunks.jsonl` musiały przejść (inaczej Pydantic by je odrzucił). ✓ Można zostawić.

### Methodological signal
- **OK R4-7:** §4.5.4 (line 261): ratio 1:2.5 vs SMOTE granicy 1:10 — `1560:3842` realnie. ✓ Argument balanced klasyfikator bez resamplingu jest defendable. Dobra decyzja inżynierska.
- **WARN R4-8:** §4.5.3 TF-IDF jako baseline — argument "if linear probe nie bije TF-IDF o 10pp AUROC to rozważyć alternative architecture". Engineering pragmatic: dobry kill-switch criterion. ALE: TF-IDF baseline jeszcze NIE istnieje w kodzie. To Iter 1+. **Fix:** "TF-IDF baseline implementacja zaplanowana w Iteracji 1 (RQ1 ablacja A1)".

---

## R5 F1+F2 — issues

### Phantom infrastructure (most critical)
- **BLOCKER R5-1:** Sekcja 5.2.3 (line 144-178) deklaruje 9 komponentów FastAPI (`query_handler`, `retriever`, `prompt_builder`, `generator_client`, `probe_extractor`, `claim_extractor`, `nli_verifier`, `citation_aligner`, `response_builder`) + 9 komponentów Prefect (`data_loader`, `preprocessor`, `halu_generator`, ..., `mlflow_logger`). **Stan kodu:** `ls D:/diplomma/main_project/src/`:
  ```
  citation/  ← __init__.py (puste)
  probe/     ← __init__.py (puste)
  verifier/  ← __init__.py (puste)
  halu/      ← 10 modułów, ~3,7k LOC (TYLKO data pipeline)
  ingest/    ← scrape
  scrape/    ← scrape
  ```
  FastAPI nie istnieje w ogóle. SGLang nie istnieje. TEI nie istnieje. Qdrant exists tylko jako wrapper w `src/halu/qdrant_indexer.py` (NIE deployed). **9 z 9 komponentów Container 1 są phantom** (chyba że "to-be-implemented w Iteracji X"). Komponent `probe_extractor` w R5 §5.2.3 jest deklarowany jako runtime + training cross-container — w kodzie: jeden plik `src/probe/__init__.py` 0 LOC. **Fix:** każdy fig 5.3 komponent musi mieć status:
    - `[OK] retriever, embedder, qdrant_indexer` → istnieją w `src/halu/`
    - `[TODO Iter X] FastAPI gateway, probe_extractor, nli_verifier, claim_extractor, citation_aligner` → planowane
  Inaczej R5 czyta się jako "system już działa", a obrona padnie na "pokażcie kod".

### Container count drift
- **BLOCKER R5-2:** Line 76 tekstu: `System składa się z jedenastu kontenerów w czterech logicznych grupach: serving modeli ML (3 kontenery), storage (2), orchestration + experiment tracking (2), observability (3), oraz application + UI (1).`
  - 3+2+2+3+1 = **11** ✓ (liczba OK)
  - Ale 4 grupy?? **5 grup** w wyliczeniu (Serving / Storage / Orchestration / Observability / Application).
  - **Fix:** zmień "czterech" → "pięciu".
- **BLOCKER R5-3:** Fig 5.2 diagram (line 96-142) lista zawiera **MinIO** w grupie Storage:
  ```
  Grupa "Storage":
    [Qdrant : vector index HNSW]
    [PostgreSQL : metadata + traces]
    [MinIO (S3-compat) : artifact storage]   ← TYLKO W DIAGRAMIE
  ```
  Tabela 5.1 nie wymienia MinIO (11 wierszy, no MinIO). Tekst mówi "11 kontenerów", a diagram pokazuje 12 (3 storage + reszta). **Fix:** wybierz:
    - opcja A: dodaj wiersz MinIO do Tab 5.1, zmień "jedenastu" → "dwunastu", grup 5 (Storage = 3), zmień "(2)" → "(3)" w wyliczeniu;
    - opcja B: usuń MinIO z Fig 5.2, dopisz "MinIO traktowane jako backing store MLflow, NIE jako osobny kontener".

### Math
- **WARN R5-4:** §5.9.3 (line 285): `MLOps stanowi 37,5 % rozdziału (sekcje 5.4 + 5.5 + 5.6)`. 9 sekcji łącznie (5.1-5.9), 3 MLOps = 33,3%. 37,5% = 3/8 (i.e., gdyby zliczać 8 sekcji). Twoja §5.1 mówi "Z dziewięciu sekcji rozdziału trzy". **Fix:** podmień `37,5%` → `33,3%` (lub w §5.1 deklaruj 8 sekcji + uzasadnij).

### Phantom "MLOps depth"
- **WARN R5-5:** §5.4, 5.5, 5.6 (line 243-257) to JEDNO-AKAPITOWE blockquotes (~5-7 zdań każda). Mówisz "MLOps stanowi 33-37% rozdziału", ale 3 sekcje × 1 akapit każda = ~21 linii LOC z 297 LOC R5 = **7% rozdziału**, NIE 33%. To text-level claim niezgodny z fizyczną długością. **Fix:** albo dopisz sekcje 5.4-5.6 do realnej proporcji, albo zmień klaim w §5.1 na "sekcje 5.4-5.6 dokumentują core MLOps pipeline, którego pełen rozwój opisany jest w Iteracji 3-4 (build + observability deployment)".
- **OK R5-6:** §5.1 "wybór C4 motywowany jest trzema czynnikami" + §5.2.3 "trzy zoom-iny pokrywają wszystkie kontenery których wewnętrzna struktura jest contribution-specific" — strukturalnie OK, defendable.

### Diagram quality vs sweat-equity
- **WARN R5-7:** "Wariant szkielet wykresu (text-only listing)" jest **content-free placeholder**. Komisja zobaczy: brak rzeczywistego SVG/Mermaid + "polishing post-sprint w Iteracji 7". Ryzyko: pre-defense reviewer kwalifikuje to jako "praca niedokończona". **Fix:** wygeneruj 7 Mermaid `.mmd` plików w `thesis_research/diagrams/r05_*.mmd` z prawdziwymi diagramami przed oddaniem. Mermaid via MCP `validate_and_render_mermaid_diagram` jest dostępne. Każdy diagram ~15-30 min pracy.

### 3-tier verifier scope creep
- **WARN R5-8:** §5.2.3 zoom-in 3 (line 220-224):
  ```
  Tier 1: TEI mDeBERTa (production default, T1 PASS 80.6%)
  Tier 2: TEI HerBERT-large + CDSC-E fine-tune (reserved fallback)
  Tier 3: SGLang LLM judge (Bielik/PLLuM/Gemma 3/Claude Haiku ablation w R7)
  ```
  Tier 1 PASS empirycznie (`iter0b_poc/results/t1_mdeberta_20260516_115505.json`: accuracy 80.6%, n=93). ✓
  Tier 2 i Tier 3 są planowane i nigdy nie zaimplementowane. Confidence-based routing też. Dla 6-tygodniowej obrony to overengineered. Recommended: Tier 1 prymary, Tier 2 + Tier 3 = "ablacja R7 jeśli czas". **Fix:** dopisz w fig 5.3: "Tier 2 + Tier 3 = ablation paths zaplanowane w R7 jeśli budżet pozwala. Production default: Tier 1." Też wsadź to do scope: nie wymyślaj fallback chain logiki w kodzie do oddania.

### Polish / language hygiene
- **OK R5-9:** Codemix EN-PL w sekcjach 5.4-5.6 (blockquotes) — `MLOps view`, `Runtime view`, `parallel branch`, `eval split`, `failure detection`, `canary deployment` — to OK w **draft** (CLAUDE.md notes "codemix English-Polish w drafcie pracy NIE — czysty akademicki polski"). **Fix:** Iteracja 7 polishing przepisać na polski; flagi dla self: `ewaluacja`, `obserwowalność`, `dryf`, `gałąź równoległa`, `wdrożenie kanarkowe`.

---

## Cross-chapter consistency

| Numer | R3 | R4 | DATASET_CARD | `chunks.jsonl` | Match? |
|---|---|---|---|---|---|
| Total chunks | 11 000 | 11 000 | 11 000 | 11 000 | ✓ |
| Halu pairs | 5 402 | 5 402 | 5 402 | 5 402 | ✓ |
| Retrieval corpus | **8 022** | n/a | n/a | **7 622** | ✗ Off-by-400 |
| qa_gold | 433 | 433 | 433 | 60+373=433 | ✓ |
| Drop count (Wariant B) | 6 862 | 6 862 | 6 862 | n/a | ✓ |
| Drop ratio | 38,4 % | 38,4 % | 38,4 % | n/a | ✓ |
| Source types | 9 | 9 | 9 | 9 enum | ✓ |
| Halu types | 5 | 5 | n/a | 5 enum | ✓ |
| Categories | 14 | 14 | 14 | 14 enum | ✓ |
| Normalizers | "9 rodzin" | n/a | n/a | **10 funkcji** | ✗ Off-by-1 |
| Eval set | 200 par | 200 par | n/a | **0 plików** | ✗ Aspirational |
| Containers | n/a | n/a | n/a | – | – |
| Containers (R5 tekst) | – | – | – | – | **11 vs 12 (MinIO)** |
| MLOps % rozdziału | – | – | – | – | **33,3 % vs 37,5 %** |

**Fixes one-liner:**
1. R3 Tab 3.1 line 21: `8 022` → `7 622`
2. R3 §3.4.1 line 131: `dziewięciu rodzin źródeł` → `9 typów źródłowych (10 normalizerów)` (lub doklej footnote)
3. R3 §3.3.2 line 106: `splits/  # train/val/test (stratified)` → `# splits/ planowane w Iteracji 1`
4. R3 §3.5.3 line 182: `200 par` → `~110 par (60 UOKiK + 50 manual)` (defendable scope)
5. R5 §5.2.2 line 76: `czterech logicznych grupach` → `pięciu logicznych grupach`
6. R5 §5.2.2 + Fig 5.2: rozstrzygnij MinIO (12 z, 11 bez)
7. R5 §5.9.3 line 285: `37,5 %` → `33,3 %`
8. R5 §5.2.3: każdy komponent oznacz statusem `[OK]` lub `[TODO Iter X]`
9. DATASET_CARD §Files: usuń `splits/` lub oznacz jako planned

---

## Build reproducibility

**Pytanie:** Czy reader z dev backgroundem może uruchomić pipeline po przeczytaniu R3+R4+R5?

**Sytuacja obecna:**
- R3 §3.4.1 podaje CLI: `uv run python -m src.halu.dataset_builder --raw-dir data/raw --output-dir data/processed --version v0.6 --filter-policy strict --halu-injection-per-pair 10 --halu-legal-chunks-sample 1500 --seed 42`. **Zweryfikowane:** wszystkie flagi istnieją w `dataset_builder.py:454-484` z dokładnie tymi nazwami i defaultami. ✓
- Reproducibility wymaga `data/raw/` z 32 subkatalogami. R3 §3.7 mówi `~1,4 GB commitowanych do git`. Nie zweryfikowałem rozmiaru, ale są tam meta + jsonl. ✓
- RNG seed = 42 ✓ (linia 473 `dataset_builder.py`).

**TOP 3 brakujące informacje (engineering POV):**

1. **`SETUP.md` brak**. R5 nie odsyła do żadnego setup-doc. Reader musi sam się domyślić: `uv sync`, Python 3.13, `cd main_project`, gdzie raw data jest itp. **Fix:** dodaj minimalny `main_project/SETUP.md` z 5 kroków: clone → uv sync → set PYTHONPATH=src → cd main_project → uv run python -m src.halu.dataset_builder.
2. **Brak `requirements snapshot` lub `uv.lock` link w R3**. `pyproject.toml` zmienia się ze sprintami; bez lock'a reader nie odtworzy. **Fix:** w R3 §3.7 dopisz: "commit hash + uv.lock SHA pinned in DATASET_CARD."
3. **`data/raw/` size + audit**. R3 §3.3.2 mówi raw archived w `_archive/` z `_manifest.json`, ale nie podaje sumy size + sumy `chunk_id → archive_file` przypisań. Reader nie wie co dostanie po clone. **Fix:** w `_archive_sweep_summary.json` (już istnieje!) zlinkuj z R3, dopisz "audit raw data: 32 sources × N files, ~1,4 GB."

**Czy `uv run python -m src.halu.dataset_builder --filter-policy strict --version v0.6 --seed 42` odtwarza v0.6 bit-identical?**

- Seed control ✓ (`random.Random(seed)` w `halu_injector.py:291, 363`)
- Wszystkie 10 normalizerów deterministyczne (NFC + regex, no LLM) ✓
- Dedup deterministyczny (hash 500 znaków) — implementation TBD verified
- Filter `strict` deterministyczny ✓ (`chunk_filter.py`)
- BERTopic / UMAP NIE są w `dataset_builder` — to notebook side, NIE re-run pipeline
- **Wniosek:** chunks.jsonl + halu_pairs.jsonl re-run powinno być bit-identical. NIE testowane empirycznie, ale na podstawie kodu probability 95%+. **Rec:** zrób jeden re-run + `diff` test dla potwierdzenia przed oddaniem.

---

## Over-engineering / scope creep signals

### 3-tier NLI verifier — over-engineered dla scope thesis
- Tier 1 mDeBERTa: ✓ PASS empirycznie (80.6%, n=93)
- Tier 2 HerBERT-large + CDSC-E fine-tune: zaplanowane, niezrealizowane, ~1-2 tyg pracy
- Tier 3 LLM judge: zaplanowane, niezrealizowane, jako ablation w R7
- Confidence-based routing z threshold 0.5: NIE zaimplementowane
- **Engineering verdict:** Tier 1 sam wystarczy do defendable claim. Tier 2 = future work. Tier 3 = R7 ablacja z 1 modelem (Claude Haiku najprostszy bo API), NIE 4 (Bielik/PLLuM/Gemma/Claude). **Rec:** zaweź scope do Tier 1 jako production + ewentualny LLM judge (1 model) jako baseline w R7.

### 7 figur Mermaid + 1 Gradio mockup
- 7 figur dla R5 typowo OK dla architecture chapter (komercyjne ADR mają 5-10). ✓
- 1 Gradio mockup OK (single-figure low-effort).
- **Rec:** zostaw 7 figur, **ale wygeneruj Mermaid SVG, NIE ASCII szkielet**. Mockup Gradio może być screenshot z lokalnego dev runu lub Figma sketch.

### 5 typów halucynacji
- 5 typów jest defendable (`schemas.py:HaluType`, `halu_injector.py` implementacja). Realna dystrybucja w `halu_pairs.jsonl`: factual_fabrication 1620, entity_confusion 985, negation_flip 467, paragraph_mis_citation 427, temporal_drift 343. Negacja czasowa najsłabsza (343 = 8.6%). **Rec:** zostaw 5 typów (defendable taksonomia). Nie redukuj do 4 — paragraph_mis_citation jest WYSOKO POŻĄDANY dla citation-grounding RQ (utracilibyśmy unique contribution). Nie rozszerzaj do 6-7 — entity_confusion już pokrywa najczęstsze błędy semantyczne.

### Eval set 200 par
- 200 par = engineering optimum, ALE wymaga 5-7h manualnej anotacji
- 110-160 par = realistic dla weekend hyperfocus burst
- **Rec:** 120 par (60 UOKiK + 60 manual). Sweet spot defendable scope vs deliverable time.

---

## Top 5 fixes priority

1. **R5 phantom infrastructure** — w §5.2.3 oznacz każdy komponent statusem `[OK]` / `[TODO Iter X]`. Inaczej obrona padnie na "pokażcie kod FastAPI/probe_extractor/nli_verifier". (1h pracy)
2. **R5 container count drift** (BLOCKER R5-2 + R5-3) — rozstrzygnij MinIO (11 vs 12) + fix "czterech" → "pięciu" grup + Tab 5.1 + Fig 5.2 zgodne. (30 min)
3. **R3 Tab 3.1 8 022 → 7 622** (BLOCKER R3-1) — single-cell fix. (1 min)
4. **R4 placeholders Tab 4.3 + Tab 4.5 + Tab 4.8** (BLOCKER R4-1) — Tab 4.3 możesz zrobić w 5 min (recipe niżej). Tab 4.6/4.8 wymagają realnych runów BERTopic/Bielik (1-2h). (2-3h)
5. **R5 MLOps 37,5 % → 33,3 %** + dopisz proza dla §5.4-5.6 (obecnie 1-akapit blockquote) — żeby twierdzenie o 33% nie było goły. (2-3h pracy R5 fragmenty 3+4)

---

## Engineering verdict per rozdział

- **R3:** **NEEDS WORK** — fundamenty solidne, 4-6 mikro-fixów liczb + decyzja na eval set scope. ~3h pracy do gotowości.
- **R4:** **NEEDS WORK** — całkiem dobre EDA-style writing, ale placeholders bloat. Bez Tab 4.3/4.6/4.8 z realnymi liczbami rozdział nie nadaje się do oddania. ~3-5h pracy (notebook run + cell-filling).
- **R5 F1+F2:** **NEEDS WORK + dokończenie F3-F5** — sekcje 5.1/5.2 strukturalnie OK z fixami consistency. ALE sekcje 5.3-5.9 to placeholdery (jednoakapitowe blockquoty). Realna fixed wersja = (5.1+5.2 cleanup 2h) + (5.3+5.4+5.5+5.6+5.7+5.8+5.9 napisanie 8-12h). Razem ~10-14h do oddania.

**Aggregate:** żaden z trzech rozdziałów nie jest ready-to-submit, ALE fundament empiryczny jest realny i defendable. Większość issues to consistency cleanup (5min do 1h każdy), nie merytoryczne pomyłki. Code review-wise to "PR needs 4-5 follow-up commits", nie "PR rejected".

---

## Bonus — Tab 4.3 recipe (5-min fix)

```python
# Run from D:/diplomma/main_project/
python -c "
import json
from collections import Counter
src_total = Counter()
src_with_cit = Counter()
with open('data/processed/citationbench_v0.6_2026-05-16/chunks.jsonl', encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        src_total[r['source_type']] += 1
        if r['cited_articles']:
            src_with_cit[r['source_type']] += 1
for st in sorted(src_total, key=lambda x: -src_with_cit[x]):
    t, w = src_total[st], src_with_cit[st]
    print(f'{st:30s} | {w:5d} ({100*w/t:.1f}%) z {t}')
"
```

Wynik wstaw do Tab 4.3 i sekcja 4.2.3 jest gotowa.

---

## Mismatch sign-off

| Reviewer claim | Verified? |
|---|---|
| arXiv 2604.10799 jest valid past date (Apr 2026 < May 2026 today) | ✓ |
| 9 source_types | ✓ (`SourceType` enum) |
| 5 halu types | ✓ (`HaluType` enum) |
| 14 categories | ✓ (`Category` enum) |
| 11 000 chunks | ✓ (`wc -l chunks.jsonl`) |
| 5 402 halu pairs | ✓ (`wc -l halu_pairs.jsonl`) |
| 38,4 % drop ratio | ✓ (DATASET_CARD) |
| qa_gold = 60 UOKiK + 373 RF FAQ | ✓ (jsonl groupby) |
| T1 mDeBERTa 80,6 % | ✓ (`iter0b_poc/results/t1_mdeberta_20260516_115505.json`, n=93) |
| 11 containers (text), 12 (diagram) | ✗ (inconsistency, fix needed) |
| 9 normalizers (R3 text) | ✗ (faktycznie 10) |
| Retrieval corpus 8 022 | ✗ (faktycznie 7 622) |
| `splits/` directory | ✗ (nie istnieje) |
| `src/probe/`, `src/verifier/`, `src/citation/` z kodem | ✗ (puste `__init__.py`) |
| `SETUP.md` | ✗ (nie istnieje) |

---
