# Setup instrukcje — nowy laptop / migration

**Data:** 2026-05-16
**Cel:** Po `git clone` mieć fully working repo do continue Iter. 0b POC.

---

## 1. Repo clone

```bash
git clone https://github.com/nimzoi/diplomma.git
cd diplomma
```

## 2. Python toolchain (uv + Python 3.13)

**Install uv** (Astral): https://github.com/astral-sh/uv

```bash
# Linux/macOS:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Install Python 3.13** (jeśli nie ma):

```bash
uv python install 3.13
```

**Sync dependencies:**

```bash
uv sync                    # install wszystkie deps z pyproject.toml + uv.lock
uv run python --version    # verify Python 3.13.X
```

## 3. Models download (HuggingFace)

```bash
# Login (z HF token):
huggingface-cli login

# Bielik 11B v3 (generator + probe target — ~22 GB bf16, ~11 GB FP8)
huggingface-cli download speakleash/Bielik-11B-v3.0-Instruct
# Alternative dla H100 GPU:
huggingface-cli download speakleash/Bielik-11B-v3.0-Instruct-FP8-Dynamic

# BGE-M3 (embedder dla retrieval, ~568M params, ~2 GB)
huggingface-cli download BAAI/bge-m3

# mDeBERTa NLI Tier 1 verifier (~300M params, ~1 GB)
huggingface-cli download MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7

# HerBERT-large (Tier 2 fallback, jeśli mDeBERTa < 70% — opcjonalne, ~1.3 GB)
huggingface-cli download allegro/herbert-large-cased

# Reference probe impl (clone, NOT download)
git clone https://github.com/obalcells/hallucination_probes.git ../hallucination_probes-reference
```

## 4. Qdrant (vector DB) — Iter. 1+

```bash
# Local Docker (cleanest):
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

# Verify:
curl http://localhost:6333/healthz
```

Alternative: Qdrant Cloud free tier (1 GB) lub install local binary.

## 5. Environment variables

```bash
cp .env.example .env
# Edytuj .env i dodaj:
# - HUGGINGFACE_TOKEN=hf_xxx (z https://huggingface.co/settings/tokens)
# - OPENROUTER_API_KEY=sk-or-xxx (z https://openrouter.ai/keys — dla cross-model ablations)
# - WANDB_API_KEY=xxx (opcjonalne, dla MLflow/W&B integration Iter. 2+)
```

## 6. Verify dataset (already w repo)

```bash
ls main_project/data/raw/
# Powinien być:
# - eli_ustawy_konsumenckie_2026-05-16/   (2,123 chunks z 6 ustaw)
# - uokik_qa_2026-05-16/                  (60 par gold standard)
# - consumer_questions_polish_2026-05-16/ (2,967 questions)
# - extended_consumer_2026-05-16/         (jeśli E1 done — Q&A z dodatkowych źródeł)
# - consumer_documents_2026-05-16/        (jeśli E4 done — long-form documents)

wc -l main_project/data/raw/uokik_qa_2026-05-16/uokik_qa.jsonl
# Should be 60
```

**Note:** `thesis_research/iter0_feasibility/rpl-snapshot-2026-05-16.xml` (~70 MB) jest **gitignored** (locked legacy artifact z v3.1 farma probe). Nie potrzebujesz go — historical reference only.

## 7. Run tests

```bash
uv run pytest                                 # all tests (schemas unit + integration)
uv run pytest -v -k schemas                   # tylko schema unit tests
uv run pytest -v -k "not integration"         # skip slow integration
```

Expected: schemas unit tests PASS. Integration tests skip jeśli raw data path różny.

## 8. Build processed dataset (Polish CitationBench v0.1)

```bash
cd main_project
uv run python -m src.halu.dataset_builder \
    --raw-dir data/raw \
    --output-dir data/processed \
    --version v0.1
```

Output: `data/processed/citationbench_v0.1_<date>/` z `legal_chunks.jsonl`, `uokik_gold.jsonl`, `consumer_questions.jsonl`, `DATASET_CARD.md`.

## 9. Iter. 0b POC start (po setup)

Per `thesis_research/PLAN_cele_i_kroki.md` § Iter. 0b — 4 testy:

1. **Outlines + Bielik z polish diakrytyki** (D13 priority 1)
2. **PyTorch hooks na Bielik layer 47** (D10+D11)
3. **mDeBERTa NLI sanity** na 50 par UOKiK Q&A (D2)
4. **Lab GPU verify** (D9)

Code templates → `thesis_research/research/bielik_tools_outlines_research.md` § 6 + `probes_polish_llm_research.md` § 9.

## 10. Where to start (read order, post-clone)

1. **`D:\diplomma\CLAUDE.md`** — project state v3.2 (post-DEC-003 pivot)
2. **`thesis_research/CLAUDE.md`** — read order priorities post-pivot
3. **`thesis_research/EXPLAINER_temat_dla_siebie.md`** — narrative + glossary (50+ pojęć)
4. **`thesis_research/PLAN_cele_i_kroki.md`** — daily operational reference (D1-D15 decisions)
5. **`thesis_research/02_konspekt_v3.2_skeleton.md`** — akademicki konspekt (12 sekcji)
6. **`thesis_research/decisions/DEC-003_pivot-na-halu-detection.md`** — pivot rationale dla promotora
7. Research outputs (8 plików w `thesis_research/research/`) — gdy potrzebny depth na konkretny topic

## 11. Common workflows

### Run scrape (refresh)
```bash
cd main_project
uv run python -m src.scrape.uokik.scrape_qa --output ../data/raw/uokik_qa_<date>
uv run python -m src.scrape.isap.scrape_eli                # full ELI rescrape
uv run python -m src.scrape.legal_fora.scrape              # consumer questions refresh
```

### Run notebook EDA
```bash
cd main_project
uv run jupyter lab notebooks/
# Open: eda_v0.ipynb
```

### Format + lint przed commit
```bash
uv run ruff format
uv run ruff check
uv run pyrefly check       # type check src/
uv run pytest              # run tests
```

## 12. Git workflow

```bash
git status
git add -A
git commit -m "feat(scope): description ..."
git push                   # do origin/main
```

**Anti-patterns** (per `D:\diplomma\CLAUDE.md`):
- NIE auto-commit (zawsze sign-off Magdy)
- NIE force push do main
- NIE commituj `.env`, `models/`, `mlruns/`, `qdrant_storage/`, `.venv/`
- Conventional commits: `feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`

## 13. Lab GPU access (specific dla Magdy ZAiAI@LAB)

Per Magdy konspekt v3.1 historical — dostęp do SP7 H200 80GB. Verify że:
- SSH access działa do lab serwera
- Bielik weights pre-downloaded na lab (oszczędza ~22 GB transfer)
- Qdrant może działać lokalnie lub na lab (decyzja per Iter. 0b)

## 14. Heads-up dla migration laptop

**Co się przeniesie z git clone (gotowe):**
- ✅ Cały code (`main_project/src/`, `tests/`)
- ✅ Wszystkie scraped data (~5,150 items + extended po E1/E4 land — JSONL)
- ✅ Wszystkie research outputs + chapter skeletons + spec docs
- ✅ Pyproject + lock file (deterministyczna re-install via `uv sync`)
- ✅ .gitignore + SETUP.md + README

**Co trzeba osobno (post-clone):**
- 🔄 Models z HuggingFace (~25 GB total — Bielik + BGE-M3 + mDeBERTa)
- 🔄 `.env` z API tokens (HuggingFace, OpenRouter)
- 🔄 Qdrant Docker / install
- 🔄 Lab GPU access verification (SSH config)

**Co zostaje na poprzednim laptopie (NIE migrate):**
- `.venv/` (regenerate via `uv sync`)
- `qdrant_storage/` (rebuild z scraped data via Iter. 1 indexing)
- `mlruns/` (jeśli starty MLflow runs — sometimes useful migrate, sometimes nie)
- IDE config (`.idea/` — gitignored)
- `iter0_feasibility/rpl-snapshot-2026-05-16.xml` (70 MB legacy, gitignored)
