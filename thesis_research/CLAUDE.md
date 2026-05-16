# thesis_research/

Source-of-truth dokumenty projektu.

## ⚠ Status (2026-05-16, post-DEC-003 pivot)

**Trzeci pivot zakończony:** v3.1 farma + reranker → **v3.2 hallucination detection + citation grounding + consumer rights**.

**Konsekwencje dla dokumentów:**

- **Cały materiał v3.1** (farma + reranker drafts, sources_catalog, training_dataset_spec, iter0 evidence) zarchiwizowany w `_archive/v3-pharma-reranker/` jako historical record + audit trail evidence dla DEC-003.
- **Nowy konspekt v3.2** w `02_konspekt_v3.2_skeleton.md`.
- **DEC-003** w `decisions/DEC-003_pivot-na-halu-detection.md`.
- **Stack docs (`04_dev_environment.docx`, `05_stack_techniczny.docx`) zostają** — większość stacku reusable (Bielik, Qdrant, Prefect, MLflow, Langfuse, Evidently). Halu-specific dodatki dokumentowane w nowym konspekcie.
- DEC-001 + DEC-002 zostają jako historical record (audit trail), NIE są aktywne — superseded przez DEC-003.

## Co czytać i w jakiej kolejności (post-DEC-003)

| File | Kiedy | Priorytet |
|------|---|---|
| `D:\diplomma\CLAUDE.md` | ZAWSZE first w nowej sesji | 🔴 P0 |
| **`02_konspekt_v3.2_skeleton.md`** | ZAWSZE second — aktualny konspekt v3.2 | 🔴 P0 |
| **`decisions/DEC-003_pivot-na-halu-detection.md`** | Gdy potrzebny defense argument dla pivot lub pełny rationale | 🔴 P0 |
| `research/halu_detection_sota_2024_2026.md` | Praca nad R2 (literatura), R6 (modele methodology) | 🟠 P1 |
| `research/domain_A_feasibility.md` | Praca nad R3 (dane), scrape pipeline ISAP+UOKiK+Reddit | 🟠 P1 |
| **`notes/sources_z_v3.1_do_reuse_w_v3.2.md`** | Praca nad R1+R2 — 24/31 v3.1 refs reusable + framing carry-over (~70% R1 adapter) | 🟠 P1 |
| `05_stack_techniczny.docx` | Decyzje technologiczne, uzasadnienia, alternatywy | 🟡 P2 |
| `04_dev_environment.docx` | Setup kodu, CI/CD, reproducibility | 🟡 P2 |
| `01_agent_brief.docx` | Historical context (psych framing pre-pivots) | 🟢 P3 |
| `_archive/v3-pharma-reranker/*` | Tylko jeśli explicit audit trail / pivot rationale | 🟢 P3 historical |
| `decisions/DEC-001_*.md`, `DEC-002_*.md` | Historical pivots — gdy promotor pyta „dlaczego tyle pivotów" | 🟢 P3 historical |

## Jak czytać .docx

```
docling.convert_document_into_docling_document(source="<absolutna ścieżka>")
  → returns {"document_key": "..."}
docling.export_docling_document_to_markdown(document_key="...")
  → returns markdown
```

**Cold start ~60s** przy pierwszym wywołaniu po starcie sesji. Spodziewaj się timeoutu MCP (30s) przy pierwszej próbie. **Retry once.** Druga próba przejdzie.

Alternatywa dla prostego tekstu (bez struktury): `pypdf` lub `PDF_Tools.read_pdf_content`. Ale dla pracy z thesis dokumentami preferuj docling.

## Drafts

`thesis_research/drafts/` — workspace dla pre-rozdziałowych szkiców, brainstormów, draft sekcji.

**Status drafts (2026-05-16, post-Wariant B cleanup):** **PUSTY** per CLAUDE.md.
- Stare drafty v3.1 (R1_wprowadzenie, R2_literatura, R3_dane, R4_eda, R5_outline, R6_modele, R7_wyniki, R8_podsumowanie) → `_archive/v3-pharma-reranker/drafts/`
- Pre-cleanup v3.2 drafty R3/R4/R5 (1,315 LOC, pre-Wariant B, pre-T1 PASS, pre-v0.6 dataset) → `_archive/v3.2-pre-clean/drafts/` z README explanation
- Nowe drafty v3.2 powstają w **Iter. 7 writing phase** (po wszystkich Iter. 1-6 ablations) per build-first-finalize-last (CLAUDE.md Wzorzec 8)

**Nowe drafty v3.2** będą tworzone w Iteracji 7 (writing phase) per build-first-finalize-last principle (patrz `D:\diplomma\CLAUDE.md` Wzorce pracy pkt 8).

## Research

`research/` — agent research outputs, single-source-of-truth dla literature + feasibility.

- **`halu_detection_sota_2024_2026.md`** — SOTA hallucination detection 2024-2026 (Mu-SHROOM polish gap, hidden-states probes lineage Farquhar→SEP→Semantic Energy→real-time, „Mirage of Halu Detection" critique EMNLP 2025, polish landscape audit, ~22 papierów + 10+ tools)
- **`domain_A_feasibility.md`** — feasibility ISAP + UOKiK + Reddit + polish NLI models + hidden-states probe implementation refs + dataset numbers estimate (in progress, agent-spawned)

## Decisions log

`decisions/` — ADR (Architecture Decision Records) generowane przez `/decision`.

**Active:**
- **DEC-003** (2026-05-16): Pivot na hallucination detection + citation grounding + consumer rights

**Historical (audit trail, NIE aktywne):**
- **DEC-001** (2026-05-15): rotacja psych → farma — superseded przez DEC-003
- **DEC-002** (2026-05-15): ChPL+Ulotka cross-register — superseded; explicit NIE używane w v3.2 („już tej ulotki nie mieszajmy", Magda 2026-05-16)

## Anti-patterns

- **Nie edytuj** istniejących .docx-ów (01, 04, 05) bez explicit zgody autorki — to są zatwierdzone source-of-truth artefakty.
- **Nie re-eksportuj** do .docx via Claude bez prośby (formatowanie się rozjedzie).
- **Nie traktuj** żadnego pojedynczego docx jako kanonicznego — zawsze cross-check z `02_konspekt_v3.2_skeleton.md` + DEC log.
- **Nie scrapuj jednocześnie ISAP w wielu różnych formatach** (XML + HTML) — wybierz jedno źródło, dedup.
- **Nie zatwierdzaj 4. rotacji domeny** — DEC-003 to ostateczna decyzja po trzech pivotach. Jeśli ktoś sugeruje kolejny pivot, najpierw przeczytaj DEC-003 kill criteria.
- **Nie wracaj do reranker fine-tuning ani farma jako central** — patrz DEC-003 anti-patterns + supersession logic.
- **Nie usuwaj `_archive/`** — historical record ma value dla audit trail w obronie („kiedy i dlaczego pivot").
- **Nie pisz codemix English-Polish w drafcie pracy** (CLAUDE.md + spec docs OK, R1-R8 NIE — czysty akademicki polski).
