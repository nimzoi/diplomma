# Praca inżynierska — MLOps RAG retrieval retraining

## Status (zaktualizowano 2026-05-15)
- Autor: Magdalena Sochacka (s25508), PJATK, Wydział Informatyki, Data Science
- Promotor: mgr inż. Piotr Kojałowicz (MLOps mindset, structured technical defensiveness)
- **Tytuł aktualny (v3.1):** *„Pipeline MLOps do iteracyjnego dotrenowywania komponentów retrievalu w polskojęzycznych systemach RAG na podstawie sygnałów z observability — studium przypadku dla domeny farmakologii klinicznej z eksperymentem cross-register retrieval (paired ChPL↔Ulotka)"*
- **Domena: farmakologia kliniczna szeroka** (rotacja z psychiatria 2026-05-15 — zobacz DEC-001)
  - Korpus pokrywa pełną farmakologię (ChPL + Ulotki + AOTMiT + NFZ + OA journals)
  - Manual gold standard eval set (200 par) próbkowany z **psychiatrycznej podgrupy** (ATC N05-N06) — leverage autorki kompetencje
- **Plan A active.** Plan B (cybersec) deactivated — corpus farmakologiczny stabilny.
- Harmonogram: sem. II = pipeline + 60-70% rozdziałów, sem. III = drift + finalizacja.
- **⚠ Konspekt `02_konspekt_v3_FINAL.docx` ma stare framing.** Obowiązuje delta `02b_konspekt_v3_updates.md` + dwie decyzje DEC-001 i DEC-002.

## Źródła prawdy (w `thesis_research/`)
- `01_agent_brief.docx` — krótki brief (read first w każdej nowej sesji)
- `02_konspekt_v3_FINAL.docx` — pełen konspekt v3 (HISTORICAL — niektóre sekcje superseded, patrz niżej)
- **`02b_konspekt_v3_updates.md`** — DELTA: zaktualizowane sekcje (II.1, II.2.1, II.3.3 + RQ5, II.4, II.7, II.13, II.15, II.16). Czytaj zaraz po briefie.
- **`sources_catalog.md`** — pełna tabela źródeł farmakologii (single source of truth dla R3 Dane)
- `decisions/DEC-001_wybor-domeny.md` — ADR rotacji psych → pharma
- `decisions/DEC-002_chpl-ulotka-pairing.md` — ADR RQ5 cross-register
- `05_stack_techniczny.docx` — uzasadnienia stacku
- `03_diagrams_architektury.docx` — 7 diagramów do Rozdz. 5
- `04_dev_environment.docx` — Python toolchain, struktura repo, CI/CD
- `06_raport_feasibility_psychiatria.docx` — audit trail historical; psych pozostaje jako eval subset

**Jak czytać .docx:** `docling.convert_document_into_docling_document(source=PATH)` → `docling.export_docling_document_to_markdown(document_key)`. Cold start ~60s; timeout MCP 30s; retry once.

## Pytania badawcze (pełne w 02b_konspekt_v3_updates.md sekcja II.3.3)
- **RQ1/H1:** retrening rerankera → ≥10pp poprawy nDCG@10 vs base polish-reranker
- **RQ2/H2:** PLLuM-12B-instruct judge agreement z manual ≥75% (Cohen's kappa ≥0.50)
- **RQ3/H3:** 3 cykle retreningu — plateau po cyklu 2 (cykl 3 ≤2pp, p>0.05)
- **RQ4/H4:** drift detector precision ≥0.80, recall ≥0.70 na simulated OOD
- **RQ5/H5 (NEW, 2026-05-15):** **Cross-register retrieval z paired ChPL↔Ulotka** — czy reranker dotrenowany na corpus z paired pro/lay versions handluje lay queries → professional answers z accuracy@10 ≥70%, gap ≤5pp poniżej same-register? **Novel angle** — w literaturze brak Polish ChPL↔Ulotka aligned corpus (Grabowski 2017 ma EN-PL, nie intra-PL cross-register).

## Scope
**IN:** retrieval quality (nDCG, MRR), judge quality (kappa), pipeline engineering (Prefect, MLflow, A/B gating), drift detection (simulated), **cross-register retrieval ChPL↔Ulotka (RQ5)**.

**OUT:** medical/pharmaceutical correctness validation (autorka nie jest farmaceutką), hard negative mining dla embeddera, embedder fine-tuning (BGE-M3 frozen), end-user clinical, real-time drift na production traffic, cross-domain generalization, cross-lingual register transfer (przyszła praca).

## Korpus (po rotacji 2026-05-15, target ~4100 dokumentów)

| Strata | Source | ~docs | % |
|---|---|---|---|
| Regulatory professional | ChPL stratified (ATC N05/N06 over-rep) | 900 | 22% |
| **Regulatory consumer** | Ulotki dla pacjenta (paired z ChPL) | 900 | 22% |
| HTA + refundation legal | AOTMiT + MZ obwieszczenia + programy B.xx | 700 | 17% |
| **Refundation operational** | Zarządzenia Prezesa NFZ + BIP komunikaty | 400 | 10% |
| OA PL journals | Farmacja Polska + Lek w Polsce + AAMS + CIPMS | 900 | 22% |
| Adjacencies | URPL DHPC + MZ braki list | 300 | 7% |
| **Total** | | **~4100** | 100% |

**Eval set (gold standard 200 par):** próbkowane z **psychiatrycznej podgrupy** (ATC N05-N06), manual ranked by autorka. Świadoma decyzja architektoniczna — leverage autorki kompetencje na poddomenie którą zna, korpus szeroki na całą farmakologię.

Pełna tabela źródeł z URL-ami, licencjami, scrape methods: `thesis_research/sources_catalog.md`.

## Stack (pinned, pełne uzasadnienia w 05_stack_techniczny.docx)
- **Python:** 3.13 (pyproject), uv (NIE pip), ruff (format + lint), pyrefly (types), pytest
- **Modele:** BGE-M3 (frozen embedder) + polish-reranker-roberta-v3 (fine-tunable, ~360M, RDZEŃ) + Bielik 11B v3 (generator, Apache 2.0) + `<judge_model>` (sędzia — kandydaci: Bielik 11B v3 / Gemma 3 27B / Qwen 3 32B / Claude Haiku 4.5, decyzja w Iteracji 0)
- **Storage:** PostgreSQL (metadata) + Qdrant (vectors) + Redis Stack (cache) + DVC + MinIO
- **Orchestration:** Prefect 3 (async natywny)
- **Tracking:** MLflow + Optuna integrated
- **Observability:** Langfuse + OpenTelemetry + LGTM stack + Alertmanager
- **Drift:** Evidently (data) + Alibi Detect (statistical)
- **RAG framework:** LlamaIndex
- **Eval:** RAGAS (context_precision, context_recall, faithfulness, answer_relevancy)
- **Serving:** SGLang (LLM serving — Bielik/judge) + TEI (BGE-M3 + reranker, Rust 2-3× szybsze niż sentence-transformers) + FastAPI + Docker + GitHub Actions

## Wzorce pracy (z brief sekcja 8 — przestrzegaj zawsze)

1. **Decision before output.** Sign-off na scope/strategy zanim cokolwiek wygeneruję. Nie pisz kodu ani treści dopóki autorka nie potwierdzi kierunku.
2. **Citation hygiene.** Każda cytacja verifiable. Phantom citations, błędne inicjały, złe lata, duplikaty footnote'ów = red flags. Flag niepewność, NIE wymyślaj.
3. **Time-proofing.** Bez "obecnie", "rosnące", "brak", "jedyny", "żaden", ani specyficznych implementation references które się starzeją. **Defensibility ponad novelty.**
4. **Honest critical feedback, NIE validation.** Reasonable disagreement OK. Kontestowanie scope creep **wymagane**.
5. **Versioned iteration.** Eksplicytne before/after; alternatywne drafty + evaluation/fusion.
6. **Anti-paraliż.** Przy nieodwracalnych decyzjach nazwij trade-offy wprost i powiedz czy "wystarczająco dobre". Nie zostawiaj autorki bez konkluzji.

## Faza aktualna: SETUP po VALIDATION
Walidacja scope zakończona 2026-05-15. Domena zrotowana, RQ5 dodany.

**Następny krok: Tydzień 0 (16-22.05.2026)** — feasibility test URPL RPL XML scrape + ChPL/Ulotka download + chunkowanie. Szczegóły w `02b_konspekt_v3_updates.md` sekcja II.16.

## Mapowanie zadań PRO-D → rozdziały PJATK
| PRO-D | Rozdz. PJATK | Treść |
|---|---|---|
| Task 01 | R1 Wprowadzenie | tło RAG, problem, RQ1-RQ5 |
| Task 02 | R2 Literatura | ~22 starych + ~10 nowych (LLM-as-judge, MLOps CT, drift, cross-register) |
| Task 03 | R3 Dane | 6 strata farmakologii, codebooks, licencje (zobacz sources_catalog.md) |
| Task 04 | R4 EDA | rozkłady, embedding clusters UMAP, OCR quality, **paired ChPL↔Ulotka analysis** |
| Task 05 | **R5 Architektura (CENTRALNY)** | 5 z 7 figur diagramów + pipeline cross-register |
| Task 06 | R6 Modele | reranker + LLM-as-judge szczegóły + ablations |
| Task 07 | R7 Wyniki | baselines × cykle 1/2/3, kategoryczna error analysis, drift simulation, **RQ5 cross-register results** |
| Task 08 | R8 Podsumowanie | synteza RQ1-RQ5 + future work + negative-result framing |
| Task 09 | (formal) | TNR 12pt, footnotes IEEE, ~30+ ref |
| Task 10 | (self-check, 0pkt) | self-assessment |
| Task 11 | (final) | comprehensive summary |

## Anti-patterns
- **Nie pisz rozdziałów bez outline + sign-off.** Zawsze najpierw szkielet w chacie.
- **Nie generuj cytowań z głowy.** Nieznany rok/autor → flag, nie zmyślaj.
- **Nie wzbudzaj scope creep.** Plan B (cybersec) zdezaktywowany — nie sugeruj go bez konkretnego powodu.
- **Nie usuwaj ChPL+Ulotka pairing bez czytania DEC-002.** Cross-register angle to potencjalnie publishable sub-contribution.
- **Nie traktuj eval set jako "pełna farmakologia"** — gold standard to psych subset (ATC N05-N06), świadomie. Mówi to R5.
- **Nie scrape'uj jednocześnie URPL RPL XML + dane.gov.pl dataset 397** — ten sam content, deduplication overhead.
- **Nie używaj sformułowań starzejących się** ("obecnie najnowszy", "rosnące zainteresowanie", "brak prac w temacie").
- **Nie commituj automatycznie.** Nigdy `git push`. Nie ruszaj `.venv/`, `.git/`, `.idea/`.
- **Nie używaj pip/poetry/conda.** Tylko `uv`.
- **Nie używaj black** mimo że jest w deps. `ruff format` jest źródłem prawdy.

## Komendy slash (zobacz `.claude/commands/`)
- `/validate` — devil's advocate na bieżący scope/decyzję
- `/chapter R0X` — fokus na konkretny rozdział
- `/citations PATH` — audyt cytowań (deleguje do citation-checker)
- `/promotor [obszar]` — wymyśl 10 pytań od Kojałowicza
- `/status` — gdzie jestem względem harmonogramu (brutalnie szczerze)
- `/decision TYTUŁ` — zaloguj decyzję przed wykonaniem
- `/diagram` — praca nad diagramami architektury (Rozdz. 5)

## Subagent
- `citation-checker` — weryfikuje cytowania (Read + WebFetch + WebSearch, model: haiku)

## Decision log (ADR)
- **DEC-001** (2026-05-15): Rotacja domeny psychiatria → farmakologia szeroka (psych jako eval subset). Szczegóły: `thesis_research/decisions/DEC-001_wybor-domeny.md`
- **DEC-002** (2026-05-15): ChPL+Ulotka cross-register pairing jako RQ5. Szczegóły: `thesis_research/decisions/DEC-002_chpl-ulotka-pairing.md`

## Defense scaffolding
Patrz `thesis_elements/CLAUDE.md` sekcja **„Defense scaffolding"** — 3 mikro-podszepty przygotowujące obronę:
1. Ablation studies w cyklu 1 (PLLuM vs random, PLLuM vs Bielik, full vs psych-only subset)
2. Kategoryczna error analysis (terminology miss, ambiguous query, length mismatch, OOD chunk, **register mismatch**)
3. Negative-result publishability framing R8 (jeśli H1 odpada → kontrybucje H2, H4, H5 nadal stoją niezależnie)
