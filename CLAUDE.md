# Praca inżynierska — Citation-grounded polish RAG z hallucination detection

**Autor:** Magdalena Sochacka (s25508), PJATK Data Science. **Promotor:** mgr inż. Piotr Kojałowicz (MLOps mindset, structured technical defensiveness).

**Tytuł v3.2:** *„Citation-grounded polski RAG z hidden-states hallucination probe — pipeline produkcyjny dla domen krytycznych (studium przypadku: prawa konsumenta)"*

**Domena:** polish consumer rights (informational, NIE doradcze prawnie — explicit disclaimer w UI).

> 📖 **PEŁEN OPIS PRACY:** [`thesis_research/02_konspekt_v3.2_skeleton.md`](thesis_research/02_konspekt_v3.2_skeleton.md) (14 sekcji: tytuł / abstract / domena / RQ / dane / architektura / modele / citation grounding / MLOps / defense / OUT scope / iter plan / promotor). Plus operational: [`PLAN_cele_i_kroki.md`](thesis_research/PLAN_cele_i_kroki.md) (D1-D15 decisions per iter) + [`EXPLAINER_temat_dla_siebie.md`](thesis_research/EXPLAINER_temat_dla_siebie.md) (narrative + glossary 50+ pojęć).

## Status (current — 2026-05-16 evening)

- **Polish CitationBench v0.6:** 11,000 unified chunks + 5,402 halu pairs (balanced 5/5 typów). `main_project/data/processed/citationbench_v0.6_2026-05-16/`
- **Iter. 0b POC:** T1 mDeBERTa NLI sanity ✅ **PASS 80.6%** (lokal CPU). T2/T3/T4 pending lab GPU SP7 H200.
- **`thesis_research/drafts/` PUSTY** — drafty powstają w Iter. 7 (build-first-finalize-last).
- **Origin/main aktualne**, working tree clean.

## Pytania badawcze (3 main + 1 supporting)

- **RQ1/H1 (probe quality):** hidden-states halu probe Bielik 11B v3 layer 47 → **AUROC ≥0.70 z bootstrap CI lower ≥0.60** (in-domain; per Dubanowska EMNLP 2025).
- **RQ2/H2 (citation grounding, Wallat 2025 2-metric):** H2a faithfulness ≥85% precision; H2b correctness ≥75% precision.
- **RQ3/H3 (3-tier NLI verifier):** mDeBERTa Tier 1 → HerBERT Tier 2 fallback → LLM judge Tier 3 ablation → ≥85% citation precision.
- **RQ4/H4 supporting (LLM-as-judge):** kappa ≥0.50 z manual labels (Landis-Koch substantial).

## Scope

**IN:** halu probe + citation grounding pipeline + RAG demo (Bielik + Qdrant + LlamaIndex) + continuous improvement loop + observability stack + Gradio 3-tab + 3 HuggingFace artifacts (dataset + probe + verifier).

**OUT:** doradztwo prawne, reranker fine-tuning, farma domain, LLM full fine-tuning, real-time production traffic, cross-language transfer.

## Stack

- **Python 3.13** + uv (NIE pip) + ruff (format + lint) + pyrefly + pytest
- **Bielik 11B v3** (generator + probe target, Apache 2.0, 50 layers × 4096 hidden, layer 47 = ⌊0.95×50⌋)
- **BGE-M3** (embedder, frozen, multilingual)
- **`MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`** — Tier 1 verifier **✓ T1 PASS 80.6%** (MIT, 27 langs)
- **HerBERT-large + CDSC-E custom** — Tier 2 fallback (nie wymagany teraz)
- **Bielik / PLLuM / Gemma 3 / Claude Haiku** — LLM judge Tier 3 (R7 ablation A3)
- **`knowledgator/gliclass-multilang-ultra`** — Tier 0 ablation w R7 (multi-class native maps na 6 halu types)
- **Halu probe:** sklearn LogisticRegression linear primary; MLP nonlinear ablation jeśli linear < threshold
- **Hidden-states extraction:** PyTorch hooks + HF `output_hidden_states=True` (NIE transformer-lens — brak 50L Mistral support)
- **Reference probe impl:** `obalcells/hallucination_probes` (Apache-2.0, Mistral arch compat)
- **Storage:** PostgreSQL + Qdrant + Redis + DVC + MinIO
- **MLOps:** Prefect 3 + MLflow + Optuna + Langfuse + Evidently + Alibi Detect + LGTM + Alertmanager
- **RAG framework:** LlamaIndex + Outlines (structured output) + RAGAS (eval)
- **Serving:** SGLang (Bielik) + TEI (BGE-M3 + verifier) + FastAPI + Docker + GH Actions
- **UI:** Gradio (3 zakładki: Chat / Inspect / Compare)

## Phantom-citation watchlist

- `sdadas/polish-nli` — **NIE istnieje** na HF (confirmed 2026-05-16)
- `finecat-nli-l` — license UNSPECIFIED, NIE używać dla HF publication

## Wzorce pracy

1. **Decision before output.** Sign-off na scope przed kodem/treścią.
2. **Citation hygiene.** Każda cytacja verifiable. Phantom = red flag.
3. **Time-proofing.** Bez „obecnie", „rosnące", „brak", „jedyny", „żaden".
4. **Brutal feedback, NIE validation.** Kontestowanie scope creep wymagane.
5. **Honest motivation framing.** Catch own overstatement. NIE „LLM nie umie polish prawa" — TAK „polish halu detection nie udokumentowane publicznie (Mu-SHROOM 2025 pominął PL)".
6. **Build-first, finalize-last.** Pisanie ostatnie 20%, NIE pierwsze.
7. **Agent-rozkładalne zadania.** Agenty: scaffolding / scrape / format / draft. Magda: training / decisions / manual annotation / final review.

## Anti-patterns

- Nie pisz rozdziałów bez outline + sign-off.
- Nie generuj cytowań z głowy.
- **Nie wzbudzaj scope creep.** Cybersec / cross-domain stress = future work, NIE central.
- **Nie wracaj do reranker fine-tuning, farma, ChPL/Ulotka, RQ5** — DEC-003 explicit OUT.
- Nie używaj sformułowań starzejących się.
- Nie commituj automatycznie. Nigdy `git push` bez prośby. Nie ruszaj `.venv/`, `.git/`, `.idea/`.
- Nie używaj pip/poetry/conda — tylko `uv`. Nie używaj black — `ruff format` źródło prawdy.
- Nie pisz codemix EN-PL w drafcie pracy (CLAUDE.md/spec OK, R1-R8 czysty polski akademicki).

## Read order (post-pivot)

P0 (zawsze first w sesji): root `CLAUDE.md` → `thesis_research/02_konspekt_v3.2_skeleton.md` → `decisions/DEC-003` + `decisions/DEC-004`

P1 (do work): `research/halu_detection_sota_2024_2026.md` + `research/nli_models_2026_update.md` + `notes/sources_z_v3.1_do_reuse_w_v3.2.md` + `notes/KRYTYCZNA_ocena_scope_2026-05-16.md`

P3 (historical only): `_archive/v3-pharma-reranker/` (v3.1 farma+reranker) + `_archive/v3.2-pre-clean/drafts/` (pre-Wariant B R3/R4/R5)

## Slash commands (w `.claude/commands/`)

`/validate` (devil's advocate) · `/chapter R0X` (focus rozdz.) · `/citations PATH` (citation-checker subagent) · `/promotor [obszar]` (10 Kojałowicz pytań) · `/status` (vs iteration plan) · `/decision TYTUŁ` (log ADR) · `/diagram` (R5 architecture)

## Decision log (active only)

- **DEC-003** (2026-05-16): Pivot na halu detection + citation grounding + consumer rights. **ACTIVE.**
- **DEC-004** (2026-05-16): Iter. 0b POC results — T1 PASS 80.6%; T2/T3/T4 pending lab GPU. **PARTIAL.**
- DEC-001 + DEC-002 SUPERSEDED przez DEC-003 (zachowane w `_archive/v3-pharma-reranker/decisions/`).

## Defense scaffolding (5-wymiarowa kontrybucja R8)

Każdy wymiar broni się niezależnie. Jeśli H1 odpada (probe AUROC <0.70 lub CI lower <0.60), kontrybucje 2-5 stoją niezależnie:

1. **Metodologiczny** — pierwszy publicznie udokumentowany polish hallucination detection methodology
2. **Inżynierski** — reprodukowalny pipeline citation-grounded RAG + halu probe + verifier
3. **Artefaktowy** — 3 publishable na HuggingFace (dataset + probe + verifier)
4. **Eksperymentalny** — porównanie polish probe vs Lynx multilingual + HHEM + gliclass
5. **Korpusowy** — pierwszy polish CitationBench z deterministic citation grounding (ISAP-based)

Standalone publishable: dataset jako HF release nawet jeśli reszta H odrzucone.
