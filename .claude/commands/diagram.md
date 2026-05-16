---
description: Work on architecture diagrams for R5 (centralny rozdział v3.2) — using Mermaid via MCP. 7 diagrams total per 02_konspekt_v3.2_skeleton.
---

Argument: $ARGUMENTS — który diagram (`context`, `container`, `rag-flow`,
`probe-extraction`, `verifier`, `training-loop`, `observability`), albo "list"
żeby pokazać wszystkie 7, albo puste = zapytaj.

## 7 diagramów dla R5 v3.2 (z 02_konspekt_v3.2_skeleton + DEC-003)

| # | Nazwa | Typ | Co pokazuje |
|---|-------|-----|---|
| 1 | C4 Context | C4 | System w otoczeniu — Magda, lab GPU, judge LLM ablation, źródła ISAP/UOKiK/EUR-Lex |
| 2 | C4 Container | C4 | SGLang (Bielik) / TEI (BGE-M3 + mDeBERTa) / FastAPI / Qdrant / Prefect / Langfuse / LGTM |
| 3 | RAG flow | Flow | Query → BGE-M3 retrieve top-k → Bielik 11B v3 gen (Outlines) → per-claim citation alignment |
| 4 | Probe extraction | Flow | Bielik forward pass → PyTorch hooks layer 47 → mean-pool last 5 tokens → sklearn LR probe → halu score |
| 5 | 3-tier NLI verifier | Flow | claim+evidence → mDeBERTa Tier 1 → (jeśli confidence < threshold) HerBERT Tier 2 → (R7 ablation) LLM-judge Tier 3 |
| 6 | Continuous improvement loop | Sequence | Halu probe + verifier outputs → Langfuse → preference dataset → retrain probe → A/B gating (3 cykle per RQ3) |
| 7 | Observability + drift | Flow | Langfuse traces → Evidently data drift + Alibi Detect embedding KS/MMD → Alertmanager halu rate spike |

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
   ├── diag-3-rag-flow.mmd
   ├── diag-4-probe-extraction.mmd
   ├── diag-5-3tier-verifier.mmd
   ├── diag-6-continuous-improvement-loop.mmd
   └── diag-7-observability-drift.mmd
   ```

## Konwencje stylu Mermaid

- Polskie etykiety dla nodów (np. "Reranker (training)", nie "Reranker training")
- Konkretne nazwy modeli/komponentów (Bielik 11B v3, BGE-M3, MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7, HerBERT-large, gliclass-multilang-ultra)
- Konsystentna kolorystyka per kategoria (np. wszystkie LLM = jasnoniebieski, DB = jasnozielony)
- Direction: `LR` dla flowów (bardziej naturalnie czyta się), `TB` dla C4
- Subgraphy dla logicznego grupowania (np. "Storage layer", "Compute layer")

## Export do .docx pracy

Z konspektu v3.2 (Iter. 7-8 writing phase): formatowanie końcowe wymaga wektorowych
diagramów. Mermaid widget pozwala pobrać SVG/PNG — autorka exportuje ręcznie
i wkleja do `R05_architektura.docx`. Powiedz to autorce gdy diagram jest finalny.

## Anti-patterns

- ❌ Generowanie Mermaid bez sign-off — często autorka chce inny poziom szczegółu
- ❌ Próba renderowania w tekście (ASCII diagrams) zamiast MCP — nie nadaje się do pracy
- ❌ Mieszanie poziomów abstrakcji (C4 Container z konkretami z C4 Component)
- ❌ Polskie + angielskie etykiety na jednym diagramie
