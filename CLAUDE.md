# Praca inżynierska — Citation-grounded polish RAG z hallucination detection

## Status (zaktualizowano 2026-05-16, post-DEC-003)
- Autor: Magdalena Sochacka (s25508), PJATK, Wydział Informatyki, Data Science
- Promotor: mgr inż. Piotr Kojałowicz (MLOps mindset, structured technical defensiveness)
- **Tytuł aktualny (v3.2):** *„Citation-grounded polish RAG z hidden-states hallucination probe — pipeline produkcyjny dla domen krytycznych (studium przypadku: prawa konsumenta)"*
- **Domena: polish consumer rights** (legal informational, NIE doradcze)
  - Korpus: ISAP (ustawy konsumenckie + Kodeks cywilny art. 535-581), UOKiK (decyzje + raporty edukacyjne), Reddit r/Polska + fora prawne (real consumer questions)
  - Eval set 100 par manual gold standard by autorka
- **Trzeci pivot:** v1 administracja → v2 prompt injection → v3 psychiatria → **v3.1 farmakologia + reranker** (DEC-001) → **v3.2 halu detection + consumer rights** (DEC-003, 2026-05-16). Pełen audit trail w `thesis_research/decisions/`.
- **⚠ Cały materiał v3.1 (farma + reranker) zarchiwizowany** w `thesis_research/_archive/v3-pharma-reranker/` jako historical record + evidence dla DEC-003 pivot.

## Źródła prawdy (w `thesis_research/`)
- `_archive/v3-pharma-reranker/01_agent_brief.docx` — historical brief, NIE aktywny (psychiatry framing pre-DEC-001)
- **`02_konspekt_v3.2_skeleton.md`** — AKTUALNY konspekt v3.2 (post-DEC-003)
- **`research/halu_detection_sota_2024_2026.md`** — SOTA research halu detection (Mu-SHROOM polish gap, hidden-states probes, FaithJudge, polish landscape)
- **`research/domain_A_feasibility.md`** — feasibility report ISAP + UOKiK + Reddit + polish NLI models
- `_archive/v3-pharma-reranker/decisions/DEC-001_wybor-domeny.md` — historical (zarchiwizowane): rotacja psych → farma
- `_archive/v3-pharma-reranker/decisions/DEC-002_chpl-ulotka-pairing.md` — historical (zarchiwizowane): cross-register pairing (ChPL+Ulotka) — explicit NIE używane w v3.2
- **`decisions/DEC-003_pivot-na-halu-detection.md`** — AKTUALNY: pivot na halu detection + consumer rights
- `_archive/v3-pharma-reranker/04_dev_environment.docx` — Python toolchain, struktura repo, CI/CD (historical, większość reusable)
- `_archive/v3-pharma-reranker/05_stack_techniczny.docx` — uzasadnienia stacku (historical, większość reusable, halu-specific dodatki w nowym konspekcie v3.2)
- `_archive/v3-pharma-reranker/` — historical farma+reranker materials (drafts, sources_catalog, training_dataset_spec, iter0 evidence)

**Jak czytać .docx:** `docling.convert_document_into_docling_document(source=PATH)` → `docling.export_docling_document_to_markdown(document_key)`. Cold start ~60s; timeout MCP 30s; retry once.

## Pytania badawcze (3 main + 2 supporting, NIE 5)

**Main hypotheses:**
- **RQ1/H1 (probe quality):** hidden-states halu probe trenowany na Bielik osiąga AUROC ≥0.80 detection halucynacji w polish consumer rights answers (vs random baseline 0.50, vs multilingual baseline Lynx ≥X pp poprawy).
- **RQ2/H2 (citation grounding):** post-hoc citation alignment pipeline osiąga ≥85% precision dla per-claim grounding na 100 par gold standard (czy każdy claim jest poprawnie wsparty cytacją do exact paragrafu ISAP).
- **RQ3/H3 (continuous improvement):** continuous retraining loop probe (3 cykle) **konwerguje** — każdy cykl zwiększa AUROC lub plateau, brak regresji w >50% cykli.

**Supporting hypotheses:**
- **RQ4/H4 (verifier quality):** programatic NLI verifier (MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7) osiąga ≥75% agreement z manual labels na ~100-300 par eval set (UOKiK Q&A + autorka).

## Scope
**IN:**
- Hidden-states hallucination probe na Bielik (training + inference + eval)
- Post-hoc citation grounding pipeline (NLI-based)
- Polish consumer rights RAG demo (Bielik + Qdrant + LlamaIndex)
- Continuous improvement loop probe (cykle retreningu z drift triggers)
- Observability stack (Langfuse + Evidently + LGTM)
- 3 publishable artefakty: (a) Polish CitationBench dataset na HuggingFace, (b) probe model + verifier model na HuggingFace, (c) Gradio app (3 zakładki)

**OUT:**
- Doradztwo prawne (informational, NIE legal advice — explicit disclaimer)
- Reranker fine-tuning (z poprzedniej iteracji — passé per Iter. 0a feasibility)
- Farma domain jako central (przesunięta do bonus eksperymentu / future work)
- LLM full fine-tuning (probe NIE LoRA — modern technique 2025-2026)
- Real-time production deployment z user traffic
- Cross-language transfer
- Reranker dla consumer rights (jeśli probe + verifier + RAG działa, reranker by był overkill)

## Korpus (target ~10-15k pairs)

| Komponent | Source | ~size | Method |
|---|---|---|---|
| Ustawy konsumenckie | ISAP (Ustawa o prawach konsumenta + Kodeks cywilny art. 535-581 + ust. o reklamacji) | ~500-1000 chunks | Agent scrape XML/HTML |
| UOKiK | decyzje + raporty edukacyjne | ~200-500 chunks | Agent scrape HTML |
| Real consumer questions | r/Polska + r/PrawoPL + Forum Infor.pl + Prawo.pl | ~2-3k pytań | Reddit API + scrape |
| Synthetic halu pairs | Bielik 11B generated answers + injected halu (5 typów) | ~5-10k pairs | Programatic agent |
| Manual gold standard | hand-annotated by autorka | 100 par | Magda weekend hyperfocus |
| **Total** | | **~10-15k pairs** | |

Pełen feasibility w `research/domain_A_feasibility.md`.

## Stack (pinned, większość z v3.1 zostaje)
- **Python:** 3.13 (pyproject), uv (NIE pip), ruff (format + lint), pyrefly (types), pytest
- **Modele:**
  - Bielik 11B v3 (generator RAG, Apache 2.0)
  - **Bielik 11B v3 jako probe target (primary, lab GPU SP7 H200; fallback 1.5B/3B dla local CPU dev)** — confirmed PyTorch hooks compatible (50 layers × 4096 hidden, ~22 GB VRAM bf16)
  - BGE-M3 (embedder dla retrieval)
  - **MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7** (300M, MIT, 105k polish pairs trained) — primary verifier; HerBERT-large custom NLI fine-tune na CDSC-E — opcjonalny upgrade (`sdadas/polish-nli` nie istnieje — phantom citation z poprzedniego research)
  - **Hidden-states probe (NEW — trained from scratch, small classifier nad activations Bielika)**
  - Lynx 8B / 70B + HHEM 2.x (multilingual baselines dla comparison)
- **Storage:** PostgreSQL (metadata) + Qdrant (vectors) + Redis Stack (cache) + DVC + MinIO
- **Orchestration:** Prefect 3 (async natywny)
- **Tracking:** MLflow + Optuna integrated
- **Observability:** Langfuse + OpenTelemetry + LGTM stack + Alertmanager
- **Drift:** Evidently (data + halu rate distributions) + Alibi Detect (statistical)
- **RAG framework:** LlamaIndex (z Citation Query Engine post-hoc lub structured output Outlines/Instructor)
- **Eval:** RAGAS (faithfulness, answer_relevancy) + custom probe AUROC + citation accuracy
- **Hidden-states extraction:** PyTorch hooks lub `transformer-lens` / `nnsight` library
- **Serving:** SGLang (Bielik 11B) + TEI (BGE-M3 + verifier) + FastAPI + Docker + GitHub Actions
- **UI:** Gradio (3 zakładki: Chat / Inspect / Compare)

## Wzorce pracy (przestrzegaj zawsze)

1. **Decision before output.** Sign-off na scope/strategy zanim cokolwiek wygeneruję. Nie pisz kodu ani treści dopóki autorka nie potwierdzi kierunku.
2. **Citation hygiene.** Każda cytacja verifiable. Phantom citations, błędne inicjały, złe lata, duplikaty footnote'ów = red flags. Flag niepewność, NIE wymyślaj.
3. **Time-proofing.** Bez „obecnie", „rosnące", „brak", „jedyny", „żaden", ani specyficznych implementation references które się starzeją. **Defensibility ponad novelty.**
4. **Honest critical feedback, NIE validation.** Reasonable disagreement OK. Kontestowanie scope creep **wymagane**.
5. **Versioned iteration.** Eksplicytne before/after; alternatywne drafty + evaluation/fusion.
6. **Anti-paraliż.** Przy nieodwracalnych decyzjach nazwij trade-offy wprost i powiedz czy „wystarczająco dobre". Nie zostawiaj autorki bez konkluzji.
7. **Honest motivation framing (NEW post-pivot DEC-003).** Catch own overstatement BEFORE promotor does. NIE „LLM nie umie polish prawa" (overstated). TAK „polish-specific halu detection nie zostało publicznie udokumentowane (Mu-SHROOM 2025 pominął polski) + production RAG dla legal domain wymaga citation grounding + halu control".
8. **Build-first, finalize-last (Magda's flow).** Pisanie ostatnie 20%, NIE pierwsze. Najpierw BUILD (scrape, train, eval, demo), potem polish prose w Iter. 7-8.
9. **Agent-rozkładalne zadania.** Rozdzielać prace: agenty robią scaffolding + scrape + format + boilerplate + draft, Magda robi training + decisions + 100 par manual annotation + final review.

## Faza aktualna: SETUP po PIVOT DEC-003 (2026-05-16)
- Domena zrotowana z farma na consumer rights
- Stack core zostaje, dodatki halu detection (probe + verifier + citation alignment)
- 3+2 RQ zamiast 5

**Następny krok: Iteracja 0b** — feasibility verification (research agent in flight) + dataset scaffolding setup. Szczegóły w nowym konspekcie v3.2.

## Mapowanie zadań PRO-D → rozdziały PJATK
| PRO-D | Rozdz. PJATK | Treść (v3.2 post-pivot) |
|---|---|---|
| Task 01 | R1 Wprowadzenie | tło RAG + halucynacje + citation grounding + RQ1-RQ5 (3 main + 2 supporting) |
| Task 02 | R2 Literatura | ~30 ref: hallucination detection 2024-2026 (semantic entropy → hidden-states probes), citation-grounded RAG, polish NLP, „Mirage of Halu Detection" critique |
| Task 03 | R3 Dane | ISAP scrape methodology, UOKiK, Reddit/fora questions, halu injection 5 typów, NLI labeling, 100 par gold standard |
| Task 04 | R4 EDA | rozkłady halu types, citation lengths, paragraph distribution z ustaw, polish question characteristics |
| Task 05 | **R5 Architektura (CENTRALNY)** | 7 figur: RAG flow + probe extraction + verifier + citation alignment + training loop + observability + drift |
| Task 06 | R6 Modele | hidden-states probe details + verifier (NLI LoRA) + Bielik generator + ablations |
| Task 07 | R7 Wyniki | probe AUROC vs baselines + citation accuracy + cykle retreningu + error analysis 6-poziomowa + ablations |
| Task 08 | R8 Podsumowanie | synteza RQ1-RQ4 + 5-wymiarowa kontrybucja (probe + dataset + verifier + Gradio + methodology) + future work (multi-turn, cybersec, cross-domain transfer to other polish legal domains) |
| Task 09 | (formal) | TNR 12pt, footnotes IEEE, ~30+ ref |
| Task 10 | (self-check, 0pkt) | self-assessment |
| Task 11 | (final) | comprehensive summary |

## Anti-patterns
- **Nie pisz rozdziałów bez outline + sign-off.** Zawsze najpierw szkielet w chacie.
- **Nie generuj cytowań z głowy.** Nieznany rok/autor → flag, nie zmyślaj.
- **Nie wzbudzaj scope creep.** Cybersec angle = future work pkt R8, NIE central. Cross-domain stress test = OPCJONALNY R7.
- **Nie wracaj do reranker fine-tuning.** Pivot DEC-003 deactivated reranker jako central — citation alignment + probe to nowy core.
- **Nie wracaj do farma ani ChPL+Ulotka.** Z poprzedniej iteracji explicit NIE używamy — Magda decision 2026-05-16 „już tej ulotki nie mieszajmy" (DEC-003 § Konsekwencje + supersession DEC-002).
- **Nie używaj sformułowań starzejących się** („obecnie najnowszy", „rosnące zainteresowanie", „brak prac w temacie").
- **Nie commituj automatycznie.** Nigdy `git push`. Nie ruszaj `.venv/`, `.git/`, `.idea/`.
- **Nie używaj pip/poetry/conda.** Tylko `uv`.
- **Nie używaj black** mimo że jest w deps. `ruff format` jest źródłem prawdy.
- **Nie pisz codemix English-Polish w drafcie pracy** (CLAUDE.md + spec docs OK, R1-R8 NIE — czysty akademicki polski).

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
- **DEC-001** (2026-05-15): Rotacja domeny psychiatria → farmakologia szeroka. Status: SUPERSEDED przez DEC-003.
- **DEC-002** (2026-05-15): ChPL+Ulotka cross-register pairing jako RQ5. Status: SUPERSEDED przez DEC-003 — explicit NIE używane („już tej ulotki nie mieszajmy", Magda 2026-05-16).
- **DEC-003** (2026-05-16): Pivot na hallucination detection + citation grounding + consumer rights domain. Status: ACTIVE.

## Defense scaffolding (post-pivot)
3 mikro-podszepty:
1. **Ablation studies w cyklu 1** — probe na full vs partial activations, NLI verifier vs LLM-judge, citation post-hoc vs generation-time, baseline Lynx multilingual vs Twoja polish probe
2. **Kategoryczna error analysis** — 6-poziomowa taksonomia halu types: factual fabrication / entity confusion / temporal drift / negation flip / paragraph mis-citation / ambiguous claim
3. **5-wymiarowa kontrybucja w R8 (negative-result publishability framing):**
   - Metodologiczny: pierwszy publicznie udokumentowany polish hallucination detection methodology
   - Inżynierski: reprodukowalny pipeline citation-grounded RAG + halu probe + verifier
   - Artefaktowy: 3 publishable na HuggingFace (dataset + probe model + verifier model)
   - Eksperymentalny: porównanie hidden-states probe vs multilingual baselines (Lynx, HHEM)
   - Korpusowy: pierwszy polish CitationBench dataset z deterministic citation grounding (ISAP-based)

   Każdy wymiar broni się niezależnie. W przypadku odrzucenia H1 (probe AUROC <0.80), kontrybucje (2)-(5) stoją niezależnie — z szczególnym wyróżnieniem dataset jako standalone publishable artifact.
