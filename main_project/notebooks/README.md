# Notebooks

Eksploracja danych + sanity checks dla Polish CitationBench.

## `eda_v0.ipynb`

**Iteracja 0 (2026-05-16) — REAL EDA na initial 5,150 scrape'owanych rekordach (PRE-cleanup, historical snapshot).**

**Note:** EDA uruchomione na pre-Wariant B build (5,150 raw items). **Current dataset = Polish CitationBench v0.6** (11,000 unified chunks + 5,402 halu pairs, post-cleanup) w `data/processed/citationbench_v0.6_2026-05-16/`. Notebook EDA zostaje jako historical snapshot dla porównania pre/post-cleanup; refresh post-v0.6 = `eda_v1_processed.ipynb` (planned Iter. 1).

Sekcje:
- **A.** Setup + data loading (workaround do `dataset_builder` — schema drift fix)
- **B.** Dataset overview (counts, size distribution, validation rate)
- **C.** ELI ustawy — per ustawa stats, chunk length distribution, citation format validation, hierarchy depth
- **D.** UOKiK Q&A — per kategoria, citation density, most-cited statutes, Q vs A length
- **E.** Consumer questions — per source, top topics, length per source, topic overlap heatmap
- **F.** Cross-source — UOKiK→ELI citation overlap, topic coverage matrix, BGE-M3 token/cost estimate
- **G.** Konkluzje + rekomendacje dla Iter. 1

**Run:**
```bash
# Wymagane dodatkowe deps (NIE w pyproject.toml — Iter. 0 exploration):
uv pip install matplotlib seaborn pandas nbformat nbclient ipykernel jupyter
uv run jupyter lab main_project/notebooks/
```

**Outputy notebooka:** 8 matplotlib/seaborn figur + tabele DataFrame z faktycznymi statystykami (pre-rendered w komitowanym `.ipynb`).

**Kluczowe findings (G.1 Quality issues):**
1. **Schema drift ELI** — `dataset_builder.load_eli_chunks` rzuca walidację bo raw scraper produkuje `para` zamiast `paragraf`, brak `chunk_id`, `ustawa_data_uchwalenia` w `metadata`. Notebook obchodzi adapterem; **decyzja Iter. 1 wymagana** (fix scraper czy schema).
2. **UOKiK → ELI corpus overlap** — część cytatów referuje ustawy spoza naszych 6 ELI. Eval ceiling implications.
3. **Reddit context bloat** — median ~2k chars; embedder truncate. Decyzja: query = tylko `question`, context jako payload.
4. **UOKiK n=60** — mało dla statistical power; consider scrape expansion w Iter. 2.

## Przyszłe notebooks (Iter. 1+)

- `eda_v1_processed.ipynb` — porównanie v0 vs v0.6 stats (pre-cleanup vs post-Wariant B)
- `probe_layer_search.ipynb` — layer 47 verification (Bielik 11B v3 internal hidden states dla halu detection — D10)
- `error_analysis.ipynb` — kategoryczna error analysis halu types per cykl retreningu (R7 wyniki)
- `umap_embeddings.ipynb` — UMAP per source_type, sprawdzenie coverage diversity dla probe training distribution
