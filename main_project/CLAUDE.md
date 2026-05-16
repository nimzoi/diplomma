# main_project/

Implementacja pracy inżynierskiej (v3.2 post-DEC-003): citation-grounded polish RAG z hidden-states hallucination probe + 3-tier NLI verifier dla domeny consumer rights (ISAP/UOKiK/Reddit/EUR-Lex).

**Status 2026-05-16 evening:** post-Wariant B + T1 mDeBERTa NLI PASS 80.6% + Polish CitationBench v0.6 build (11,000 chunks + 5,402 halu pairs).

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

## Aktualny layout (v3.2 post-pivot)

```
main_project/
├── pyproject.toml          # w root D:\diplomma\
├── src/
│   ├── halu/                  # halu detection core (NEW v3.2)
│   │   ├── schemas.py         # Chunk + HaluPair Pydantic models
│   │   ├── dataset_builder.py # build CitationBench v0.X z raw scrape
│   │   ├── chunk_filter.py    # Wariant B scope filter (strict policy)
│   │   ├── halu_injector.py   # 5 typów halu injection programatic
│   │   ├── citation_extractor.py  # ISAP citation parsing
│   │   ├── normalizers.py     # tekst normalization
│   │   ├── embedder.py        # BGE-M3 wrapper (frozen)
│   │   ├── retriever.py       # Qdrant retrieval
│   │   └── qdrant_indexer.py  # Qdrant collection management
│   ├── probe/                 # hidden-states probe (Iter. 1+)
│   │   └── (PyTorch hooks Bielik 11B layer 47, sklearn LR linear primary)
│   ├── verifier/              # 3-tier NLI verifier (Iter. 1+)
│   │   └── (mDeBERTa Tier 1 ✓ T1 PASS + HerBERT Tier 2 + LLM judge Tier 3)
│   ├── citation/              # post-hoc citation alignment (Iter. 1+)
│   ├── ingest/                # corpus ingest pipeline
│   ├── scrape/                # source-specific scrapers
│   │   ├── isap/              # ELI ustawy konsumenckie
│   │   ├── uokik/             # Q&A + decyzje + raporty
│   │   ├── reddit/            # Pushshift dumps + r/Polska filter
│   │   └── legal_fora/        # e-prawnik + forumprawne
│   └── ...                    # eval/, drift/, api/ — Iter. 2-6
├── iter0b_poc/                # POC scripts dla DEC-004 kill criteria
│   ├── t1_mdeberta_nli_sanity.py    # ✓ DONE PASS 80.6%
│   ├── t2_outlines_bielik_diakrytyki.py  # pending lab GPU
│   ├── t3_pytorch_hooks_bielik.py        # pending lab GPU
│   ├── t4_lab_gpu_verify.py              # pending lab GPU
│   └── results/               # JSON outputs per test
├── data/
│   ├── raw/                   # scraped JSONL (gitignored przesyłany manualnie)
│   └── processed/
│       └── citationbench_v0.6_2026-05-16/  # CURRENT (11,000 chunks + 5,402 halu pairs)
├── configs/                   # Hydra YAML (per-experiment, per-stage)
├── tests/                     # pytest, fixtures, mocks dla LLM calls
├── notebooks/                 # EDA, error analysis, ad-hoc explorations
└── _archive/                  # archived v3.1 farma+reranker code (historical)
```

## Konwencje

- **Konfiguracja:** Pydantic Settings dla secrets (.env via `pydantic-settings`),
  Hydra YAML dla experiment configs.
- **Model loading:** factory functions, NIE hardcoded paths.
  ```python
  def load_verifier(tier: int = 1) -> NLIModel: ...
  def load_probe(version: str | None = None) -> ProbeClassifier: ...
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
- **Tests first** dla logiki biznesowej (chunking, halu injection, scope filter,
  NLI scoring, probe training, drift detection). Skip dla glue code (Prefect flow
  definitions, API endpoints).

## Anti-patterns

- ❌ `pip install` / `poetry add` / `conda install` — tylko `uv add`.
- ❌ Hardkodowanie hyperparams — wszystko w Hydra config.
- ❌ Commit `.env`, `data/raw/`, `data/processed/`, `models/`, `mlruns/`, `*.ipynb_checkpoints/`.
- ❌ `from x import *` — explicit imports.
- ❌ Czytanie `.env` bezpośrednio (jest w deny w settings.json) — przez `pydantic-settings`.
- ❌ `print()` debug — `logger.debug()`.
- ❌ Mocking LLM API w produkcyjnym kodzie — używaj `responses=fake_responses` parametru.
- ❌ Dodawanie ChPL/Ulotka, farma, reranker fine-tuning — explicit OUT of scope per DEC-003.

## Stack dependencies (główne, w `pyproject.toml`)

```toml
[project]
dependencies = [
    "torch>=2.1",
    "transformers>=4.40",
    "sentence-transformers>=3.0",  # BGE-M3 + mDeBERTa
    "qdrant-client>=1.10",
    "psycopg[binary]>=3.2",
    "prefect>=3.0",
    "mlflow>=2.15",
    "optuna>=4.0",
    "evidently>=0.5",
    "alibi-detect>=0.12",
    "llama-index>=0.11",          # RAG framework + Citation Query Engine
    "ragas>=0.2",                 # eval (faithfulness, answer_relevancy)
    "langfuse>=2.0",              # LLM observability
    "outlines>=0.1",              # structured output Bielik (T2 pending lab GPU)
    "pydantic-settings>=2.4",
    "hydra-core>=1.3",
    "fastapi>=0.115",
    "gradio>=5.0",                # UI (3 zakładki: Chat / Inspect / Compare)
    "vllm>=0.6",                  # alternative serving; SGLang preferred dla Bielik
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
