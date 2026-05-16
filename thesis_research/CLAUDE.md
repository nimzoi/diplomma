# thesis_research/

Source-of-truth dokumenty projektu (v3.2 post-DEC-003).

## Read order

| File | Kiedy | Priorytet |
|---|---|---|
| `D:\diplomma\CLAUDE.md` | ZAWSZE first w nowej sesji | 🔴 P0 |
| `02_konspekt_v3.2_skeleton.md` | ZAWSZE second — aktualny konspekt | 🔴 P0 |
| `decisions/DEC-003_pivot-na-halu-detection.md` | Defense argument dla scope/RQ choice | 🔴 P0 |
| `decisions/DEC-004_iter0b_poc_results.md` | POC progress + sign-off framework | 🔴 P0 |
| `research/halu_detection_sota_2024_2026.md` | Praca nad R2 + R6 methodology | 🟠 P1 |
| `research/nli_models_2026_update.md` | 3-tier NLI verifier decisions (gliclass + dleemiller + mDeBERTa) | 🟠 P1 |
| `notes/sources_z_v3.1_do_reuse_w_v3.2.md` | R1+R2 writing — 24/31 v3.1 refs reusable + ~80 modern 2024-2026 | 🟠 P1 |
| `notes/KRYTYCZNA_ocena_scope_2026-05-16.md` + `notes/scope_cleanup_decisions_2026-05-16.md` | Wariant B audit (per-source DROP/KEEP) | 🟠 P1 |
| `_archive/v3-pharma-reranker/` | Historical only (v3.1 farma+reranker audit trail) | 🟢 P3 |
| `_archive/v3.2-pre-clean/drafts/` | Historical only (pre-Wariant B R3/R4/R5) | 🟢 P3 |

## Jak czytać .docx

```
docling.convert_document_into_docling_document(source="<abs path>")
  → {"document_key": "..."}
docling.export_docling_document_to_markdown(document_key="...")
```

Cold start ~60s; spodziewaj się timeoutu 30s pierwszego wywołania, **retry once**.

## Drafts

`thesis_research/drafts/` — **PUSTY** (post-Wariant B per CLAUDE.md). Drafty v3.2 powstają w Iter. 7 (build-first-finalize-last). Historical drafty: `_archive/v3-pharma-reranker/drafts/` (v3.1) + `_archive/v3.2-pre-clean/drafts/` (pre-cleanup v3.2).

## Decisions log

**Active:** DEC-003 (pivot halu detection + consumer rights) + DEC-004 (Iter. 0b POC PARTIAL).
**Historical:** DEC-001 + DEC-002 SUPERSEDED w `_archive/v3-pharma-reranker/decisions/`.

## Anti-patterns

- **Nie zatwierdzaj 4. rotacji domeny** — DEC-003 ostateczne. Przed sugerowaniem pivot → przeczytaj DEC-003 kill criteria.
- **Nie wracaj do reranker / farma / ChPL/Ulotka** — DEC-003 OUT.
- **Nie edytuj** zatwierdzonych .docx (`01_agent_brief`, `04_dev_environment`, `05_stack_techniczny`) bez zgody.
- **Nie usuwaj `_archive/`** — audit trail dla obrony („kiedy i dlaczego pivot").
- **Nie scrapuj jednocześnie ISAP w wielu formatach** — XML XOR HTML, dedup.
- **Nie pisz codemix EN-PL w drafcie pracy** (CLAUDE.md/spec docs OK, R1-R8 czysty polski).
