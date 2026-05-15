---
description: Work on architecture diagrams for Rozdz. 5 — using Mermaid via MCP. 7 diagrams total per konspekt.
---

Argument: $ARGUMENTS — który diagram (`context`, `container`, `component`,
`training`, `inference`, `drift`, `sequence`), albo "list" żeby pokazać wszystkie 7,
albo puste = zapytaj.

## 7 diagramów dla Rozdz. 5 (z konspekt + brief)

| # | Nazwa | Typ | Co pokazuje |
|---|-------|-----|---|
| 1 | C4 Context | C4 | System w otoczeniu — autorka, judge LLM, external eval, źródła danych |
| 2 | C4 Container | C4 | SGLang / TEI / FastAPI / PostgreSQL / Qdrant / Prefect — kontenery i ich relacje |
| 3 | C4 Component | C4 | Wewnątrz reranker training pipeline — moduły src/ |
| 4 | Training flow | Flow | Generate queries → judge pairwise → preference dataset → train → eval → registry |
| 5 | Inference flow | Flow | Query → BGE-M3 retrieve top-k → reranker → top-n → Bielik gen via SGLang |
| 6 | Drift detection flow | Flow | Rolling embeddings → KS/MMD → threshold → trigger retrain |
| 7 | A/B gating sequence | Sequence | MLflow registry → eval gate → A/B test → promote/rollback |

## Workflow

1. **Sign-off na scope diagramu** — co dokładnie ma pokazywać, w jakim poziomie szczegółu.
   NIE startuj od kodu Mermaid. Najpierw bullet point listing nodes + edges.
2. **Po akceptacji** — generuj Mermaid source.
3. **Render via MCP**:
   ```
   mermaid.validate_and_render_mermaid_diagram(
       diagramCode="...",
       title="..."
   )
   ```
4. **Iteruj** na podstawie feedbacku autorki — wizualne poprawki, dodatkowe nody, lepszy layout.
5. **Save final source** do `thesis_research/diagrams/diag-{N}-{slug}.mmd`:
   ```
   thesis_research/diagrams/
   ├── diag-1-context.mmd
   ├── diag-2-container.mmd
   ├── diag-3-component.mmd
   ├── diag-4-training-flow.mmd
   ├── diag-5-inference-flow.mmd
   ├── diag-6-drift-flow.mmd
   └── diag-7-ab-sequence.mmd
   ```

## Konwencje stylu Mermaid

- Polskie etykiety dla nodów (np. "Reranker (training)", nie "Reranker training")
- Konkretne nazwy modeli/komponentów (BGE-M3, polish-reranker-roberta-v3, PLLuM-12B-instruct)
- Konsystentna kolorystyka per kategoria (np. wszystkie LLM = jasnoniebieski, DB = jasnozielony)
- Direction: `LR` dla flowów (bardziej naturalnie czyta się), `TB` dla C4
- Subgraphy dla logicznego grupowania (np. "Storage layer", "Compute layer")

## Export do .docx pracy

Z konspekt (sekcja II.10.6 sem. III): formatowanie końcowe wymaga wektorowych
diagramów. Mermaid widget pozwala pobrać SVG/PNG — autorka exportuje ręcznie
i wkleja do `R05_architektura.docx`. Powiedz to autorce gdy diagram jest finalny.

## Anti-patterns

- ❌ Generowanie Mermaid bez sign-off — często autorka chce inny poziom szczegółu
- ❌ Próba renderowania w tekście (ASCII diagrams) zamiast MCP — nie nadaje się do pracy
- ❌ Mieszanie poziomów abstrakcji (C4 Container z konkretami z C4 Component)
- ❌ Polskie + angielskie etykiety na jednym diagramie
