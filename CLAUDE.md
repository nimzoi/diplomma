# Praca inżynierska — Citation-grounded polish RAG z hallucination detection

## Status (zaktualizowano 2026-05-16, evening — post-Wariant B + T1 PASS + v0.6)
- Autor: Magdalena Sochacka (s25508), PJATK, Wydział Informatyki, Data Science
- Promotor: mgr inż. Piotr Kojałowicz (MLOps mindset, structured technical defensiveness)
- **Tytuł aktualny (v3.2):** *„Citation-grounded polish RAG z hidden-states hallucination probe — pipeline produkcyjny dla domen krytycznych (studium przypadku: prawa konsumenta)"*
- **Domena: polish consumer rights** (legal informational, NIE doradcze)
  - Korpus: ISAP (ustawy konsumenckie + Kodeks cywilny art. 535-581), UOKiK (decyzje + Q&A + raporty edukacyjne), Reddit r/Polska + e-prawnik + forumprawne (real consumer questions)
  - Polish CitationBench v0.6 (post-Wariant B cleanup): **11,000 unified chunks + 5,402 halu pairs** (balanced 5/5 typów; factual_fabrication=NEUTRAL, reszta CONTRADICTED)
  - Eval set: UOKiK Q&A 60 par ready-made (✓ DONE 2026-05-16) + ~50-100 par manual gold standard by autorka (planned)
- **Trzeci pivot:** v1 administracja → v2 prompt injection → v3 psychiatria → **v3.1 farmakologia + reranker** (DEC-001) → **v3.2 halu detection + consumer rights** (DEC-003, 2026-05-16). Pełen audit trail w `thesis_research/decisions/`.
- **⚠ Cały materiał v3.1 (farma + reranker) zarchiwizowany** w `thesis_research/_archive/v3-pharma-reranker/` jako historical record + evidence dla DEC-003 pivot.
- **⚠ Pre-cleanup v3.2 drafty R3/R4/R5** (1,315 LOC, pre-Wariant B) zarchiwizowane w `thesis_research/_archive/v3.2-pre-clean/drafts/`. **`thesis_research/drafts/` jest PUSTY** (powstaną w Iter. 7 writing phase per build-first-finalize-last).
- **Iter. 0b POC status:** T1 mDeBERTa NLI sanity ✓ PASS 80.6% (lokal CPU 2026-05-16 11:55, DEC-004); T2 Outlines+Bielik diakrytyki / T3 PyTorch hooks Bielik layer 47 / T4 lab GPU verify — pending lab GPU (SP7 H200).

## Źródła prawdy (w `thesis_research/`)
- `_archive/v3-pharma-reranker/01_agent_brief.docx` — historical brief, NIE aktywny (psychiatry framing pre-DEC-001)
- **`02_konspekt_v3.2_skeleton.md`** — AKTUALNY konspekt v3.2 (post-DEC-003)
- **`research/halu_detection_sota_2024_2026.md`** — SOTA research halu detection (Mu-SHROOM polish gap, hidden-states probes, FaithJudge, polish landscape)
- **`research/domain_A_feasibility.md`** — feasibility report ISAP + UOKiK + Reddit + polish NLI models
- `_archive/v3-pharma-reranker/decisions/DEC-001_wybor-domeny.md` — historical (zarchiwizowane): rotacja psych → farma
- `_archive/v3-pharma-reranker/decisions/DEC-002_chpl-ulotka-pairing.md` — historical (zarchiwizowane): cross-register pairing (ChPL+Ulotka) — explicit NIE używane w v3.2
- **`decisions/DEC-003_pivot-na-halu-detection.md`** — AKTUALNY: pivot na halu detection + consumer rights
- **`decisions/DEC-004_iter0b_poc_results.md`** — AKTUALNY (PARTIAL): T1 PASS 80.6%; T2/T3/T4 pending lab GPU
- **`notes/KRYTYCZNA_ocena_scope_2026-05-16.md`** + **`notes/scope_cleanup_decisions_2026-05-16.md`** — Wariant B cleanup audit + per-source decyzje (drop ~38.4% chunks)
- **`notes/sources_z_v3.1_do_reuse_w_v3.2.md`** — 24/31 v3.1 refs reusable + framing carry-over (~70% R1 adapter)
- `_archive/v3.2-pre-clean/drafts/` — pre-Wariant B v3.2 drafts R3/R4/R5 (1,315 LOC, archived 2026-05-16 with README explanation)
- `_archive/v3-pharma-reranker/04_dev_environment.docx` — Python toolchain, struktura repo, CI/CD (historical, większość reusable)
- `_archive/v3-pharma-reranker/05_stack_techniczny.docx` — uzasadnienia stacku (historical, większość reusable, halu-specific dodatki w nowym konspekcie v3.2)
- `_archive/v3-pharma-reranker/` — historical farma+reranker materials (drafts, sources_catalog, training_dataset_spec, iter0 evidence)

**Jak czytać .docx:** `docling.convert_document_into_docling_document(source=PATH)` → `docling.export_docling_document_to_markdown(document_key)`. Cold start ~60s; timeout MCP 30s; retry once.

## Pytania badawcze (3 main + 1 supporting, NIE 5)

**Main hypotheses:**
- **RQ1/H1 (probe quality, IN-DOMAIN):** hidden-states halu probe trenowany na Bielik 11B v3 layer 47 (= ⌊0.95 × 50⌋ per Balcells et al. 2025) osiąga **AUROC ≥0.70 z bootstrap CI lower bound ≥0.60** (per D14 + Dubanowska EMNLP 2025 evidence) detection halucynacji w polish consumer rights answers (in-domain). Random baseline 0.50; Lynx multilingual + HHEM jako baselines do comparison.
- **RQ2/H2 (citation grounding — TWO-METRIC per Wallat ICTIR 2025):**
  - **H2a — Faithfulness:** czy citation linkuje do retrieved content? Precision ≥85% target.
  - **H2b — Correctness:** czy linked content faktycznie wspiera claim (NIE post-rationalized)? Precision ≥75% target.
- **RQ3/H3 (3-tier NLI verifier citation precision):** 3-tier NLI verifier (mDeBERTa Tier 1 → HerBERT-large Tier 2 fallback → LLM judge Tier 3 ablation) osiąga ≥85% citation precision dla per-claim grounding na ~110-160 par eval set (UOKiK Q&A + autorka).

**Supporting hypotheses:**
- **RQ4/H4 (LLM-as-judge):** LLM-as-judge (Bielik / PLLuM / Gemma 3 / Claude Haiku) → kappa ≥0.50 z manual labels (substantial agreement per Landis-Koch).

**Note:** RQ5 cross-domain transferability **deprecated** (Magda decision 2026-05-16 + Dubanowska EMNLP 2025 + Vaddi 2026-03 evidence: SOTA halu probes mają OOD AUROC ≈ random). Continuous improvement convergence cykl test = R7 ablation (NIE separate RQ).

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

## Korpus — Polish CitationBench v0.6 (BUILT 2026-05-16, post-Wariant B cleanup)

**Output:** `main_project/data/processed/citationbench_v0.6_2026-05-16/`

| Komponent (source_type) | count | source |
|---|---|---|
| `legal_statute` (ISAP ELI) | 2,541 | isap.sejm.gov.pl |
| `qa_raw` (real consumer questions) | 2,945 | forumprawne / e-prawnik / reddit / eporady24 / federacja / konsument.gov.pl / ... |
| `legal_document_pdf` (UOKiK/RF/FK poradniki) | 1,965 | rf.gov.pl + uokik.gov.pl + federacja-konsumentow + uodo + cik.uke + knf |
| `legal_ue_directive` (EUR-Lex) | 1,360 | eur-lex.europa.eu |
| `encyclopedic` | 1,167 | wikipedia (CC BY-SA — share-alike caveat per DATASET_CARD) |
| `legal_court_judgment` | 534 | orzeczenia.ms.gov.pl |
| `qa_gold` (UOKiK Q&A scraped) | 433 | prawakonsumenta.uokik.gov.pl + ekspansja |
| `legal_tsue_judgment` | 29 | EUR-Lex CURIA |
| `legal_uokik_decision` | 26 | uokik.gov.pl decyzje |
| **Unified chunks total** | **11,000** | (post-cleanup z 17,862 = drop 38.4%) |
| **Synthetic halu pairs** | **5,402** | Bielik+injection 5 typów; balanced; factual_fabrication=NEUTRAL, reszta CONTRADICTED |

**Cleanup notes (Wariant B 2026-05-16):** dropped KPC, Prawo upadłościowe, Prawo bankowe, Usługi płatnicze, finance journalism (bankier/money/infor/gazeta_prawna/prawo.pl/bezprawnik), uchylone ustawy, CHF/franki SN orzeczenia, pure-insurance RF chunks. Per-source decyzje: `notes/scope_cleanup_decisions_2026-05-16.md`.

Pełen feasibility w `research/domain_A_feasibility.md`. Dataset card: `main_project/data/processed/citationbench_v0.6_2026-05-16/DATASET_CARD.md`.

## Stack (pinned, większość z v3.1 zostaje)
- **Python:** 3.13 (pyproject), uv (NIE pip), ruff (format + lint), pyrefly (types), pytest
- **Modele:**
  - **Bielik 11B v3** (generator RAG + probe target, Apache 2.0) — primary, lab GPU SP7 H200 80GB; fallback 1.5B/3B dla local CPU dev. Confirmed PyTorch hooks compatible (50 layers × 4096 hidden, ~22 GB VRAM bf16). T3 lab GPU verify pending.
  - **BGE-M3** (embedder dla retrieval, frozen)
  - **MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7** (300M, MIT, 27 langs incl. polish trained) — **Tier 1 verifier ✓ T1 PASS 80.6% (2026-05-16, lokal CPU sanity, DEC-004)**. Per-class: contradicted P=1.000/R=0.766; entailed P=0.800/R=0.706; neutral P=0.643/R=0.931 (model conservative).
  - **HerBERT-large + custom CDSC-E fine-tune** — Tier 2 fallback (NIE wymagany teraz, T1 PASS). Note: `sdadas/polish-nli` nie istnieje — phantom citation z poprzedniego research.
  - **Bielik / PLLuM / Gemma 3 / Claude Haiku** — LLM judge Tier 3 ablation (RQ4 supporting + R7 ablation A3).
  - **gliclass-multilang-ultra** — Tier 0 ablation w R7 per `research/nli_models_2026_update.md`.
  - **Hidden-states probe** (NEW — trained from scratch, sklearn LogisticRegression linear primary, MLP nonlinear w ablation jeśli linear < threshold per Liang & Wang Dec 2025 + Dubanowska EMNLP 2025).
  - **Lynx 8B / 70B + HHEM 2.x** (multilingual baselines dla R7 comparison vs polish probe).
- **Storage:** PostgreSQL (metadata) + Qdrant (vectors) + Redis Stack (cache) + DVC + MinIO
- **Orchestration:** Prefect 3 (async natywny)
- **Tracking:** MLflow + Optuna integrated
- **Observability:** Langfuse + OpenTelemetry + LGTM stack + Alertmanager
- **Drift:** Evidently (data + halu rate distributions) + Alibi Detect (statistical KS/MMD)
- **RAG framework:** LlamaIndex (z Citation Query Engine post-hoc lub structured output Outlines/Instructor)
- **Eval:** RAGAS (faithfulness, answer_relevancy) + custom probe AUROC z bootstrap CI + Wallat 2-metric (faithfulness vs correctness) + citation accuracy
- **Hidden-states extraction:** **PyTorch hooks + HF `output_hidden_states=True`** (NIE transformer-lens — brak natywnego support dla 50L Mistral; NIE nnsight — overhead dla pilota)
- **Reference probe impl:** `obalcells/hallucination_probes` (Apache-2.0; Mistral Small 24B native = Bielik 11B compat trivially via config edit + layer_idx update)
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

## Faza aktualna: post-Wariant B + T1 PASS + v0.6 (2026-05-16, evening)
- Domena zrotowana z farma na consumer rights (DEC-003)
- Stack core zostaje, dodatki halu detection (probe + verifier + citation alignment)
- **3+1 RQ** (RQ5 deprecated per OOD evidence + Magda decision)
- **Polish CitationBench v0.6** built (11,000 chunks + 5,402 halu pairs)
- **T1 mDeBERTa NLI PASS 80.6%** (lokal CPU sanity, DEC-004) — Tier 1 confirmed working
- **Drafty PUSTE** (post-Wariant B; pre-cleanup R3/R4/R5 → `_archive/v3.2-pre-clean/drafts/`)

**Następny krok: T2/T3/T4 lab GPU verify** (SP7 H200) — Outlines+Bielik diakrytyki + PyTorch hooks layer 47 + smoke inference. Po tym: Iter. 1 probe training pipeline. Szczegóły w `decisions/DEC-004_iter0b_poc_results.md`.

## Mapowanie zadań PRO-D → rozdziały PJATK
| PRO-D | Rozdz. PJATK | Treść (v3.2 post-pivot) |
|---|---|---|
| Task 01 | R1 Wprowadzenie | tło RAG + halucynacje + citation grounding + RQ1-RQ4 (3 main + 1 supporting) |
| Task 02 | R2 Literatura | ~30 ref: hallucination detection 2024-2026 (semantic entropy → hidden-states probes), citation-grounded RAG, polish NLP, „Mirage of Halu Detection" critique, AggTruth, Wallat 2025 2-metric |
| Task 03 | R3 Dane | ISAP scrape methodology, UOKiK Q&A + decyzje + raporty, EUR-Lex UE directives, Reddit/fora questions, halu injection 5 typów, NLI labeling 3-tier, ~110-160 par gold standard, Wariant B cleanup audit |
| Task 04 | R4 EDA | rozkłady halu types, citation lengths, source_type distribution (9 typów), polish question characteristics, scope filter audit |
| Task 05 | **R5 Architektura (CENTRALNY)** | 7 figur: RAG flow + probe extraction (layer 47) + verifier (3-tier) + citation alignment + training loop + observability + drift |
| Task 06 | R6 Modele | hidden-states probe details (linear primary, MLP fallback) + verifier (mDeBERTa Tier 1 PASS + HerBERT Tier 2 + LLM judge Tier 3) + Bielik generator + ablations A0-A4 |
| Task 07 | R7 Wyniki | probe AUROC vs baselines (Lynx, HHEM, gliclass) + citation accuracy (Wallat 2-metric) + cykle retreningu + error analysis 6-poziomowa + ablations |
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
- **DEC-004** (2026-05-16): Iter. 0b POC results — T1 mDeBERTa NLI sanity PASS 80.6% (lokal CPU); T2/T3/T4 pending lab GPU. Status: PARTIAL.

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

   Każdy wymiar broni się niezależnie. W przypadku odrzucenia H1 (probe AUROC <0.70 lub CI lower <0.60), kontrybucje (2)-(5) stoją niezależnie — z szczególnym wyróżnieniem dataset jako standalone publishable artifact.
