# Setup instrukcje — nowy laptop / migration

**Data:** 2026-05-16 (evening — post-Wariant B + T1 PASS + v0.6)
**Cel:** Po `git clone` mieć fully working repo do continue Iter. 0b POC (T2/T3/T4 lab GPU pending) lub Iter. 1 probe training (po T3 PASS).

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
# Powinien być (raw scrape, pre-cleanup):
# - eli_ustawy_konsumenckie_2026-05-16/   (2,541 chunks legal_statute z 6+ ustaw)
# - uokik_qa_2026-05-16/                  (60 par gold standard ready-made)
# - consumer_questions_polish_2026-05-16/ (qa_raw forumprawne+e-prawnik+reddit+...)
# - extended_consumer_2026-05-16/         (Q&A z dodatkowych źródeł)
# - consumer_documents_2026-05-16/        (legal_document_pdf UOKiK/RF/FK poradniki)

ls main_project/data/processed/
# Powinien być (processed, post-Wariant B cleanup):
# - citationbench_v0.1_2026-05-16/  (initial build, historical)
# - citationbench_v0.2_2026-05-16/  (intermediate, historical)
# - citationbench_v0.3_2026-05-16/  (intermediate, historical)
# - citationbench_v0.4_2026-05-16/  (pre-Wariant B, historical)
# - citationbench_v0.5_2026-05-16/  (post-Wariant B initial, historical)
# - citationbench_v0.6_2026-05-16/  (CURRENT — 11,000 chunks + 5,402 halu pairs balanced)

wc -l main_project/data/processed/citationbench_v0.6_2026-05-16/chunks.jsonl
# Should be 11000

wc -l main_project/data/processed/citationbench_v0.6_2026-05-16/halu_pairs.jsonl
# Should be 5402
```

**Note:** `thesis_research/iter0_feasibility/rpl-snapshot-2026-05-16.xml` (~70 MB) jest **gitignored** (locked legacy artifact z v3.1 farma probe). Nie potrzebujesz go — historical reference only.

## 7. Run tests

```bash
uv run pytest                                 # all tests (schemas unit + integration)
uv run pytest -v -k schemas                   # tylko schema unit tests
uv run pytest -v -k "not integration"         # skip slow integration
```

Expected: schemas unit tests PASS. Integration tests skip jeśli raw data path różny.

## 8. Build processed dataset (Polish CitationBench v0.6 — current)

```bash
cd main_project
uv run python -m src.halu.dataset_builder \
    --raw-dir data/raw \
    --output-dir data/processed \
    --version v0.6 \
    --filter-policy strict
```

Output: `data/processed/citationbench_v0.6_<date>/` z `chunks.jsonl` (11,000 unified Chunks), `halu_pairs.jsonl` (5,402 balanced HaluPairs), `DATASET_CARD.md`.

**Note:** v0.6 jest current production version. Wariant B cleanup applied (drop ~38.4% off-scope chunks). Versions v0.1-v0.5 = historical (intermediate builds 2026-05-16).

## 9. Iter. 0b POC status (PARTIAL DONE 2026-05-16)

Per `thesis_research/PLAN_cele_i_kroki.md` § Iter. 0b + `decisions/DEC-004_iter0b_poc_results.md` — 4 testy:

1. **T1 mDeBERTa NLI sanity** na 93 par v0.6 (D2) — ✓ **PASS 80.6%** (lokal CPU 2026-05-16 11:55)
2. **T2 Outlines + Bielik z polish diakrytyki** (D8+D13 priority 1) — pending lab GPU
3. **T3 PyTorch hooks na Bielik 11B layer 47** (D10+D11) — pending lab GPU
4. **T4 Lab GPU verify** (D9 — SP7 H200 80GB SSH + smoke inference) — pending Magdy SSH access

T1 results: `iter0b_poc/results/t1_mdeberta_20260516_115505.json`. Run T2/T3/T4 na lab:
```bash
cd main_project
uv run python -m iter0b_poc.t2_outlines_bielik_diakrytyki --device cuda
uv run python -m iter0b_poc.t3_pytorch_hooks_bielik --device cuda --layer 47
uv run python -m iter0b_poc.t4_lab_gpu_verify --mode lab-side
```

Code templates → `thesis_research/research/bielik_tools_outlines_research.md` § 6 + `probes_polish_llm_research.md` § 9.

## 10. Where to start (read order, post-clone)

1. **`D:\diplomma\CLAUDE.md`** — project state v3.2 (post-DEC-003 pivot, post-Wariant B + T1 PASS + v0.6)
2. **`thesis_research/CLAUDE.md`** — read order priorities post-pivot
3. **`thesis_research/EXPLAINER_temat_dla_siebie.md`** — narrative + glossary (50+ pojęć)
4. **`thesis_research/PLAN_cele_i_kroki.md`** — daily operational reference (D1-D15 decisions)
5. **`thesis_research/02_konspekt_v3.2_skeleton.md`** — akademicki konspekt (12 sekcji)
6. **`thesis_research/decisions/DEC-003_pivot-na-halu-detection.md`** — pivot rationale dla promotora
7. **`thesis_research/decisions/DEC-004_iter0b_poc_results.md`** — POC results PARTIAL (T1 PASS; T2/T3/T4 pending lab GPU)
8. **`thesis_research/notes/scope_cleanup_decisions_2026-05-16.md`** + **`KRYTYCZNA_ocena_scope_2026-05-16.md`** — Wariant B audit
9. **`main_project/data/processed/citationbench_v0.6_2026-05-16/DATASET_CARD.md`** — current dataset stats
10. Research outputs (~19 plików w `thesis_research/research/`) — gdy potrzebny depth na konkretny topic

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
- ✅ Wszystkie raw scraped data (`data/raw/` — JSONL ELI/UOKiK/consumer questions/PDF poradniki)
- ✅ Wszystkie processed datasets (`data/processed/citationbench_v0.1` ... `v0.6_2026-05-16/` — current = v0.6 11,000 chunks + 5,402 halu pairs)
- ✅ Wszystkie research outputs + spec docs (drafts/ PUSTY post-Wariant B; pre-cleanup R3/R4/R5 → `_archive/v3.2-pre-clean/drafts/`)
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
