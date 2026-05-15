# main_project/

Implementacja pracy inżynierskiej: pipeline MLOps retrainingu rerankera dla
polskojęzycznego RAG (psychiatria).

## Stack pinning

- **Python 3.13** (zgodnie z `pyproject.toml`: `requires-python = ">=3.13"`)
- **uv** (Astral) — package manager. **NIE używać** `pip`, `poetry`, `conda`.
  - Dodawanie zależności: `uv add <pkg>`
  - Sync: `uv sync`
  - Run: `uv run python ...`
- **ruff** — linter + formatter. Źródło prawdy dla stylu. `black` jest w deps
  ale **nie jest używany** (legacy, do usunięcia z pyproject przy okazji).
- **pyrefly** — type checker, `strict` dla `src/`, luźno dla `notebooks/`
- **pytest** + `pytest-asyncio` — testy
- **pre-commit hooks** — ruff + pyrefly check przed commitem

## Planowany layout

```
main_project/
├── pyproject.toml          # już istnieje (w root, nie tu — do przemyślenia)
├── src/
│   ├── ingest/             # corpus scraping (PTP, AOTMiT, URPL, IPiN)
│   ├── chunking/           # 3 strategie: recursive markdown / legal-aware / Q&A
│   ├── embed/              # BGE-M3 wrapper (frozen)
│   ├── reranker/           # polish-reranker-roberta-v3 fine-tuning + serving
│   ├── judge/              # PLLuM-12B-instruct (pairwise/pointwise/faithfulness)
│   ├── pipeline/           # Prefect DAGs (ingest, gen, judge, train, eval, deploy)
│   ├── eval/               # nDCG/MRR/kappa + RAGAS integration
│   ├── drift/              # Evidently + Alibi Detect, simulated OOD experiment
│   └── api/                # FastAPI inference endpoint (Gradio UI overlay)
├── configs/                # Hydra YAML (per-experiment, per-stage)
├── tests/                  # pytest, fixtures, mocks dla LLM calls
├── notebooks/              # EDA, error analysis, ad-hoc explorations
├── scripts/                # one-off helpers (feasibility scrapers, etc.)
└── docker/                 # Dockerfile + compose dla services
```

## Konwencje

- **Konfiguracja:** Pydantic Settings dla secrets (.env via `pydantic-settings`),
  Hydra YAML dla experiment configs.
- **Model loading:** factory functions, NIE hardcoded paths.
  ```python
  def load_reranker(version: str | None = None) -> CrossEncoder: ...
  ```
- **Logging:** standard library `logging`, configured via Hydra.
- **MLflow tracking:** każdy training run = osobny `mlflow.start_run()`.
  Każdy Optuna trial = sub-run.
- **Async:** Prefect 3 async natywny — używaj `async def` dla flow/task.
- **Errors:** raise wcześnie, łap późno. Custom exception hierarchy dla domain.
- **Commits:** conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`,
  `test:`, `chore:`). Trunk-based, krótkie branche, mergowanie do `main`.

## Reguły dla Claude przy pisaniu kodu

- **Decision before output:** zaproponuj API/interfejs **zanim** zaczniesz implementację.
- **Brak fallback bullshitów:** jeśli funkcja przyjmuje `Path`, niech wymaga `Path`.
  Walidacja na granicy (boundary), nie wszędzie.
- **No backwards-compat shims** — kod świeży, nie podpieraj martwego API.
- **No comments explaining WHAT.** Tylko WHY jeśli non-obvious.
- **Type hints all the way.** `from __future__ import annotations` w każdym pliku.
- **Tests first** dla logiki biznesowej (chunking, eval metrics, drift detection).
  Skip dla glue code (Prefect flow definitions, API endpoints).

## Anti-patterns

- ❌ `pip install` / `poetry add` / `conda install` — tylko `uv add`.
- ❌ Hardkodowanie hyperparams — wszystko w Hydra config.
- ❌ Commit `.env`, `data/raw/`, `data/processed/`, `models/`, `mlruns/`, `*.ipynb_checkpoints/`.
- ❌ `from x import *` — explicit imports.
- ❌ Czytanie `.env` bezpośrednio (jest w deny w settings.json) — przez `pydantic-settings`.
- ❌ `print()` debug — `logger.debug()`.
- ❌ Mocking LLM API w produkcyjnym kodzie — używaj `responses=fake_responses` parametru.

## Stack dependencies (do `pyproject.toml` przy implementacji)

Główne (przykład, do uzupełnienia przy faktycznym setupie):
```toml
[project]
dependencies = [
    "torch>=2.1",
    "transformers>=4.40",
    "sentence-transformers>=3.0",
    "qdrant-client>=1.10",
    "psycopg[binary]>=3.2",
    "prefect>=3.0",
    "mlflow>=2.15",
    "optuna>=4.0",
    "evidently>=0.5",
    "alibi-detect>=0.12",
    "llama-index>=0.11",
    "ragas>=0.2",
    "langfuse>=2.0",
    "pydantic-settings>=2.4",
    "hydra-core>=1.3",
    "fastapi>=0.115",
    "gradio>=5.0",
    "vllm>=0.6",
]
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.6",
    "pyrefly>=0.45",
    "pre-commit>=3.8",
]
```
