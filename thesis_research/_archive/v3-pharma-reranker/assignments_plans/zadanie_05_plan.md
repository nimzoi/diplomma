# Plan zadania 05 — IT System Architecture (R5 CENTRALNY)

**Institutional source:** `assignments/05.md` (Task 05, 10 pkt)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/03-Project-Architecture-and-Experimental-Plan.md` (Assignment 3) + `04-Reproducibility-and-Code-Organization.md` (Assignment 4)
**Mapuje na rozdział:** **R5 Architektura IT (CENTRALNY — 5 z 7 figur diagramów per konspekt v3 + Fig 5.8 Gradio UI mock-up + Fig 5.9 CAG inference flow detail per 02b II.5 dopisków = łącznie 9 figur w R5)**

**Dodatkowe sekcje R5 (per 02b dopisków):**
- **Sekcja 5.X "User-facing Gradio demo"** + Fig 5.8 — z 02b § II.5 Gradio demo
- **Sekcja 5.X "Cache-Augmented Generation layer"** + Fig 5.9 + Tabela 5.X (cache decisions/thresholds) — z 02b § II.5 CAG inference layer
  - Frame: CAG = **engineering layer**, NIE research question (NIE 6. RQ)
  - GPTCache (semantic cache) + LMCache (KV-prefix cache) — już w stack II.11, tu foregrounded
  - Reference do R7 sekcja 7.X "CAG layer effectiveness" (secondary operational metrics)
**Iteracja realizacji:** 7 (writing) — pre-condition: Iteracje 0-5 (architektura stabilizowana)

## 1. Czego instytucjonalnie wymaga Task 05

7 components:
1. Hardware Architecture
2. Software Architecture
3. Data Architecture
4. Network Architecture
5. Security Architecture
6. Integration Architecture
7. Deployment and Infrastructure Architecture

Plus 10 design considerations (scalability, reliability, performance, security, maintainability, interoperability, cost, UX, observability, future-proofing).

Plus 7 common types (monolithic / N-Tier / microservices / event-driven / serverless / SOA / cloud-native).

## 2. Czego wymaga PRO-D-THESIS Assignment 3 + 4

**Assignment 3 (4-6 stron):**
- A. Operationalization of RQ → variables, hypothesis → metrics, gap → comparison
- B. Dataset description (already R3)
- C. **Experimental Pipeline Architecture** ← główne dla R5
- D. Baseline + comparative models (do R6)
- E. Evaluation Protocol (cross R6/R7)
- F. Risk Assessment and Feasibility (do R8 limitations + DEC-001 kill criteria)

**Assignment 4 (2-3 stron):**
- A. Repository Structure and Modularity
- B. Environment and Dependency Management
- C. Version Control + Experimental Traceability
- D. Configuration and Experiment Management
- E. Documentation Standards

## 3. Jak to wygląda w naszym v3.1

### Sekcja 5.1: Architectural overview

Hybrid architecture — **microservices + event-driven** dla scaling, **on-premise** dla suwerenność. Reference do `main_project/CLAUDE.md` dla code-level conventions.

### Sekcja 5.2: 7 components mapped na nasz stack

#### 5.2.1 Hardware
- GPU H200 (transfer z poprzedniej infrastruktury ZAiAI@LAB SP7) — Bielik + judge serving
- SP5 — BGE-M3 + reranker training
- SP3 — MLflow + Prometheus + Grafana
- Pojedyncza stacja robocza dla developmentu lokalnego

#### 5.2.2 Software (stack pinned, z `02b II.1 streszczenie`)
- Python 3.13, uv, ruff, pyrefly, pytest
- Bielik 11B v3 (generator), `<judge_model>` (sędzia, wybrany w Iteracji 0), BGE-M3 (embedder frozen), polish-reranker-roberta-v3 (fine-tunable)
- LlamaIndex (RAG framework), RAGAS (eval)
- Pydantic Settings (.env), Hydra YAML (experiment configs)

#### 5.2.3 Data Architecture
- **PostgreSQL** — metadata, chunks, eval pairs, run logs, judge outputs, drift metrics
- **Qdrant** — vector collections (BGE-M3 embeddings, 1024-dim hybrid dense+sparse)
- **Redis Stack** — semantic cache (GPTCache) + KV-prefix (LMCache)
- **DVC** — corpus versioning + sample list snapshots (RANDOM_SEED=42 lock)
- **MinIO** — raw PDFs (ChPL, Ulotki, AOTMiT, NFZ etc.)

#### 5.2.4 Network
- LAN ZAiAI@LAB internal
- VPN do SP3/5/7 dla remote development
- Localhost dla developmentu

#### 5.2.5 Security
- Pydantic Settings — secrets w `.env`, NIE w code
- File permissions — `data/raw/` read-only after scrape
- Brak external API exposure (on-premise)

#### 5.2.6 Integration
- **Prefect 3** orchestration (async natywny) — DAGs: corpus_ingest / query_generation / judge_pipeline / training_cycle / evaluation / drift_check / deployment
- **MLflow** model registry — A/B gating
- **SGLang** model serving (Bielik + judge)
- **TEI** (Text Embeddings Inference, Rust) — BGE-M3 + reranker serving, 2-3× szybsze niż sentence-transformers

#### 5.2.7 Deployment
- Docker + LXD containerization
- GitHub Actions CI/CD
- Trunk-based git, conventional commits

### Sekcja 5.3: Reproducibility infrastructure (z Assignment 4 PRO-D)

- **Repository structure** — z `main_project/CLAUDE.md` "Planowany layout"
- **Dependency management** — `uv` + `pyproject.toml` (pinned versions)
- **Random seed handling** — RANDOM_SEED=42 w `configs/sampling.yaml`, MLflow tracks seed per run
- **Version control** — Git + DVC dla data
- **Config management** — Pydantic Settings + Hydra YAML, no hardcoded params
- **Documentation** — README + per-module docstrings (Polish docstrings OK, function names EN per convention)

### Sekcja 5.4: 7 diagramów architektury (CRITICAL — z `02b II.1` + `commands/diagram.md`)

| # | Nazwa | Typ | Co pokazuje |
|---|-------|-----|---|
| 1 | C4 Context | C4 | System w otoczeniu — autorka, judge LLM, external eval, źródła danych URPL/AOTMiT/NFZ/journals |
| 2 | C4 Container | C4 | **SGLang** / TEI / FastAPI / PostgreSQL / Qdrant / Prefect / MLflow / Langfuse — kontenery i ich relacje |
| 3 | C4 Component | C4 | Wewnątrz reranker training pipeline — moduły src/ |
| 4 | Training flow | Flow | Generate queries → judge pairwise → preference dataset (z 4-level hard negatives) → train → eval → registry |
| 5 | Inference flow | Flow | Query → BGE-M3 retrieve top-k → reranker → top-n → **Bielik gen via SGLang** |
| 6 | Drift detection flow | Flow | Rolling embeddings → KS/MMD na BGE-M3 → threshold → trigger retrain |
| 7 | A/B gating sequence | Sequence | MLflow registry → eval gate → A/B test → promote/rollback |

**Workflow tworzenia diagramów:** `/diagram` slash command → mermaid render → save do `thesis_research/diagrams/diag-N-slug.mmd`. Eksport SVG/PNG dla finalnej pracy.

### Sekcja 5.5: Decisions architektoniczne (justification)

Per Defense scaffolding R5 pkt 1 (pipeline as deliverable) — uzasadnij każdy major choice:
- Dlaczego Prefect a nie Airflow? (async natywny, łatwiejszy)
- Dlaczego MLflow a nie W&B? (open-source, registry)
- Dlaczego SGLang a nie vLLM? (newer, faster structured generation)
- Dlaczego TEI a nie sentence-transformers? (Rust, 2-3× speed)
- Dlaczego Redis Stack semantic cache vs LMCache? (orthogonal cache layers)
- Dlaczego Evidently + Alibi Detect (oba)? (Evidently = data drift z reporting, Alibi = statistical KS/MMD na embeddings)

Reference do `thesis_research/05_stack_techniczny.docx` dla full uzasadnień + alternatives rejected.

### Sekcja 5.6: Architectural principles applied

Z 10 design considerations Task 05:
- **Scalability:** Prefect async + Docker containerization
- **Reliability:** MLflow tracking + DVC corpus versioning → reprodukowalność
- **Performance:** TEI Rust + SGLang structured gen + Redis cache
- **Security:** Pydantic Settings, .env, on-premise
- **Maintainability:** modular src/ + Hydra config
- **Interoperability:** PostgreSQL + Qdrant standard APIs
- **Observability:** Langfuse + OpenTelemetry + LGTM stack
- **Future-proofing:** stack open-source (no vendor lock-in)

## 4. Co musimy znaleźć / przygotować

### Cytacje
- LlamaIndex framework reference
- Prefect 3, MLflow, Evidently, Langfuse — official references
- Kreuzberger MLOps survey
- SGLang paper (jeśli istnieje, 🟡 verify)

### Artefakty
- **7 Mermaid diagramów** w `thesis_research/diagrams/` — eksport do .png/.svg
- **Tab. 5.1:** 7 components stack mapping
- **Tab. 5.2:** Architectural decisions (component / choice / alternative / rationale)
- **Tab. 5.3:** Reproducibility setup (random seeds / DVC / config files)

### Pre-conditions z innych iteracji
- Architektura stabilizowana po Iteracji 2 (cykl 1 pipeline running)
- Iteracja 5 (drift) finalizuje drift architecture w R5

## 5. Writing rules application

- **Classic architecture description first** — overview → components → decisions
- Każda decyzja architektoniczna uzasadniona (trade-off explicit)
- Tabele konsystentne
- 5 z 7 figur diagramów = CENTRALNY rozdział

## 6. Defense scaffolding application

- **Defense pkt 1 (Pipeline as deliverable):** R5 jest reprezentacją Defense pkt 1 — reprodukowalny pipeline MLOps jako wkład inżynierski. R5 musi być **bogaty, szczegółowy** — to nasza karta przetargowa.
- 7 diagramów eksponuje skalę architektury → "structured technical defensiveness" promotora Kojałowicza
- Reference do `main_project/` (concrete code paths) — pokazuje że nie jest to tylko design, ale realna implementacja

## 7. Acceptance checklist

- [ ] 7 components opisane (hardware → software → data → network → security → integration → deployment)
- [ ] 5 z 7 diagramów embedded (Mermaid → SVG)
- [ ] 7 diagramów w `thesis_research/diagrams/` source code
- [ ] Decisions justified — każdy major choice ma rationale
- [ ] Reproducibility infrastructure (Section 5.3) — random seeds, DVC, configs
- [ ] Reference do `main_project/` (concrete paths)
- [ ] 10 design considerations co najmniej 8 covered
- [ ] Length: 8-12 stron (najdłuższy rozdział, **centralny**)

## 8. Risks / common pitfalls

- ❌ Zbyt abstrakcyjne (general "system has microservices") — używaj **konkretnych nazw komponentów** (Prefect, MLflow, SGLang)
- ❌ Mieszanie z R6 (modele) — R5 to **system**, R6 to **modele i metody**
- ❌ Diagramy nieczytelne — eksportuj w wysokiej rozdzielczości SVG, NIE PNG niskiej jakości
- ❌ Brak uzasadnień technologicznych — promotor zapyta "*czemu X a nie Y*", musi być w R5.5
- ❌ Hard-coded paths w przykładach — referencuj config files, nie ścieżki

## 9. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Outline R5 | 8 sekcji: overview → 7 diagramów → 7 components mapped → decisions justification → architectural principles → reproducibility → eval protocol → risks | Sign-off na strukturę |
| 2 | Diagram 1 C4 Context | `/diagram context` → mermaid: system w otoczeniu (autorka, judge LLM, external eval, źródła URPL/AOTMiT/NFZ/OA journals) | Reviews wizualizacja |
| 3 | Diagram 2 C4 Container | `/diagram container` → mermaid: **SGLang** / TEI / FastAPI / PostgreSQL / Qdrant / Prefect / MLflow / Langfuse — kontenery i relacje | Reviews |
| 4 | Diagram 3 C4 Component | `/diagram component` → mermaid: wewnątrz reranker training pipeline — moduły `src/` (ingest, chunking, embed, reranker, judge, pipeline, eval, drift, api) | Reviews |
| 5 | Diagram 4 Training flow | `/diagram training` → mermaid: generate queries (Bielik) → judge pairwise (`<judge_model>`) → preference dataset (z 4-level hard negatives II.4.6) → train reranker → eval → MLflow registry → A/B gate | Reviews |
| 6 | Diagram 5 Inference flow | `/diagram inference` → mermaid: query → BGE-M3 retrieve top-k → reranker → top-n → **Bielik gen via SGLang** | Reviews |
| 7 | Diagram 6 Drift detection flow | `/diagram drift` → mermaid: rolling embeddings → KS/MMD detection (Evidently+Alibi) → threshold breach → Alertmanager → trigger retrain | Reviews |
| 8 | Diagram 7 A/B gating sequence | `/diagram sequence` → mermaid: MLflow registry → eval gate → A/B test → promote/rollback decision | Reviews |
| 9 | Sekcja 5.2 7 components mapped na stack | Drafts hardware (SP3/5/7 H200) → software (Python 3.13 stack) → data (PostgreSQL + Qdrant + DVC + MinIO) → network → security (.env, on-prem) → integration → deployment (Docker + Prefect) | Reviews completeness |
| 10 | Sekcja 5.5 Architectural decisions justification | Drafts per major choice: Prefect vs Airflow (async), MLflow vs W&B (open), SGLang vs vLLM (structured gen), TEI vs sentence-transformers (Rust 2-3×), Redis Stack vs LMCache (orthogonal layers), Evidently + Alibi (oba) | Reviews logic |
| 11 | Sekcja 5.6 Architectural principles applied | Drafts 10 design considerations addressed per layer (scalability/reliability/performance/security/maintainability/interoperability/cost/UX/observability/future-proofing) | Reviews completeness |
| 12 | Sekcja 5.7 Reproducibility infrastructure (A4) | Repo structure + environment (uv + pyproject.toml) + version control (Git + DVC) + configs (Hydra YAML) + README standards | Reviews |
| 13 | Sekcja 5.8 Eval protocol + experimental setup | 200 par psych gold standard, 4 baselines, 4 ablations A1-A4, RQ5 cross-register per direction | Reviews z konspekt II.9 mapping |
| 14 | Sekcja 5.9 Risk register | Z konspekt v3 FINAL II.12 (niezmienione) + nowe RQ5 alignment risks (paired integrity, length mismatch, cross-register noise) | Reviews |
| 15 | Citation pass | `/citations` audit (LlamaIndex, Prefect, MLflow, Evidently, Langfuse, SGLang 🟡 verify) | Reviews findings |
| 16 | Writing rules check | 7 diagramów referenced + consistent table formatting + concrete component names (NIE general "microservices") | Final read-through |

**Workflow note:** 7 diagramów (iteracje 2-8) mogą iść **równolegle** po sign-off na outline (każdy = osobny `/diagram` invocation z mermaid render → SVG export). Sekcje 5.2-5.9 (iteracje 9-14) mogą iść również równolegle po diagramach. **Critical:** każdy diagram eksportowany w SVG (nie PNG), wektor wymagany dla wektorowej jakości w finalnej pracy.

**SPECIAL R5 emphasis:** to jest **CENTRALNY rozdział** (5 z 7 figur). Promotor MLOps mindset oczekuje **konkretów technicznych** — używaj nazw komponentów (Prefect, MLflow, SGLang, TEI), NIE abstract terms ("microservices framework"). Reference do `main_project/` paths gdzie możliwe (pokazuje że nie tylko design ale i implementacja istnieje).
