# main_project/

Implementacja v3.2: citation-grounded polish RAG + hidden-states halu probe + 3-tier NLI verifier dla consumer rights.

## Stack pinning

- **Python 3.13** (`requires-python = ">=3.13"`)
- **uv** — package manager. NIE używaj `pip` / `poetry` / `conda`. `uv add <pkg>` · `uv sync` · `uv run python ...`
- **ruff** — format + lint (źródło prawdy). `black` w deps ale NIE używać.
- **pyrefly** — type checker (strict dla `src/`, luźny dla notebooks)
- **pytest** — testy

## Layout

```
main_project/
├── src/halu/                  # halu detection core
│   ├── schemas.py             # Chunk + HaluPair Pydantic models
│   ├── dataset_builder.py     # CitationBench v0.X builder
│   ├── chunk_filter.py        # Wariant B scope filter (strict/loose/none)
│   ├── halu_injector.py       # 5 typów halu programatic (factual_fabrication=NEUTRAL)
│   ├── citation_extractor.py  # ISAP citation parser
│   ├── normalizers.py         # tekst normalization
│   ├── embedder.py            # BGE-M3 wrapper (frozen)
│   ├── retriever.py           # Qdrant retrieval
│   └── qdrant_indexer.py      # Qdrant collection mgmt
├── src/probe/                 # hidden-states probe (Iter. 1+)
├── src/verifier/              # 3-tier NLI (mDeBERTa ✓ + HerBERT + LLM judge)
├── src/citation/              # post-hoc citation alignment
├── src/ingest/                # corpus ingest
├── src/scrape/                # source-specific (isap, uokik, reddit, legal_fora, ue, playwright_sources, new_sources)
├── iter0b_poc/
│   ├── t1_mdeberta_nli_sanity.py    # ✓ PASS 80.6%
│   ├── t2/t3/t4_*.py                # pending lab GPU
│   └── results/                     # JSON outputs
├── data/raw/                  # scraped JSONL (commitowane w v0.X build)
├── data/processed/citationbench_v0.6_2026-05-16/  # CURRENT
├── configs/                   # Hydra YAML
└── tests/                     # pytest
```

## Konwencje

- **Config:** `pydantic-settings` dla secrets (.env), Hydra YAML dla experiments.
- **Loaders:** factory functions, NIE hardcoded paths. `def load_verifier(tier: int = 1) -> NLIModel: ...`
- **Logging:** stdlib `logging` (NIE `print`), configured via Hydra.
- **MLflow:** każdy training run = `mlflow.start_run()`. Każdy Optuna trial = sub-run.
- **Async:** Prefect 3 native — `async def` dla flow/task.
- **Errors:** raise wcześnie, łap późno. Custom exception hierarchy.
- **Commits:** conventional (`feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`). Trunk-based.

## Reguły dla Claude

- **Decision before output** — zaproponuj API zanim zaimplementujesz.
- **Brak fallback bullshitów** — funkcja przyjmuje `Path` → wymaga `Path`. Walidacja na boundary.
- **No backwards-compat shims** — kod świeży.
- **No comments explaining WHAT** — tylko WHY jeśli non-obvious.
- **Type hints all the way.** `from __future__ import annotations` w każdym pliku.
- **Tests first** dla logiki biznesowej (chunking, halu injection, scope filter, NLI scoring, probe training, drift detection). Skip dla glue code.

## Anti-patterns

- ❌ `pip install` / `poetry add` / `conda install` — tylko `uv add`
- ❌ Hardkodowanie hyperparams — wszystko w Hydra config
- ❌ Commit `.env`, `data/raw/` (jeśli wrażliwe), `models/`, `mlruns/`, `*.ipynb_checkpoints/`
- ❌ `from x import *` — explicit imports
- ❌ Czytanie `.env` bezpośrednio — `pydantic-settings`
- ❌ `print()` debug — `logger.debug()`
- ❌ Dodawanie ChPL/Ulotka, farma, reranker fine-tuning — DEC-003 OUT
