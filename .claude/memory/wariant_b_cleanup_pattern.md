---
name: Wariant B cleanup pattern
description: Gdy scope creep — devil's advocate review → archive stale → cleanup w pipeline → POC tests + DEC sign-off
type: workflow
originSessionId: 5630a386-3d25-4119-adc8-3884cf68b58c
---

**Trigger:** scope creep detected (np. dataset rośnie 5,150 → 17,862 records w 1 dzień, 80% korpusu off-topic, drafty pisane przed POC verification, ratio chunks:halu_pairs 1:0.013).

## Wariant A vs B vs C (decision framework)

Po krytyce devil's advocate agenta (`/validate` + critical scope review):

- **A — Continue jak jest:** scope creep accepted, ryzyko ogólne defense (większość Kojałowicz questions NIE OBRONIMY)
- **B — POSPRZĄTAĆ scope** (recommended w 2026-05-16 case): drop ~50% chunks per audit, run POC tests, rewrite components → defensible przed obroną
- **C — Cleanup tylko najjawniejsze:** średnia ścieżka, ryzyko half-fix bez prawdziwego cleanup

## Implementation pattern (sprawdzone 2026-05-16)

1. **Spawn devil's advocate agent** (general-purpose subagent) z explicit „NIE validation, brutalne RED FLAGS, cytuj sprzeczności z CLAUDE.md/ADRs". Output: `notes/KRYTYCZNA_ocena_scope_<date>.md` z TLDR + 5-10 RED FLAGS + 10 killer questions promotora + recommendation A/B/C.
2. **User picks variant.** NIE auto-execute — wymaga sign-off.
3. **Cleanup agent (parallel)** — implementuje per-source DROP/KEEP/PARTIAL audit + module + tests:
   - `chunk_filter.py` z policy enum (strict/loose/none)
   - `--filter-policy strict` CLI arg
   - Per-source `notes/scope_cleanup_decisions_<date>.md`
   - `test_chunk_filter.py` (parametryzowane)
4. **Solo: POC test scaffolds** w `iter0b_poc/` (4 testy z explicit kill criteria + JSON output + PASS/FAIL verdict)
5. **Solo: halu generator rewrite** (jeśli ratio chunks:halu_pairs broken) — expand templates, add multi-source generation, type-aware NLI label mapping
6. **DEC ADR template** dla POC results sign-off (Wariant A 4/4 PASS / B 1-3 FAIL / C 4/4 FAIL)
7. **Archive stale drafts** do `_archive/v3.X-pre-clean/drafts/` z README explanation + restore instrukcje

## Konkretne archeived items (2026-05-16 audit)

- v0.1-v0.4 datasets → kept w `data/processed/` (audit trail), v0.5 strict + v0.6 type-aware = aktualne
- pre-cleanup drafty R3/R4/R5 (1,315 LOC) → `_archive/v3.2-pre-clean/drafts/`
- v3.1 farma materials → `_archive/v3-pharma-reranker/`

## POC kill criteria approach (DEC-004 pattern, reusable)

Każdy test w `iter0b_poc/`:
- Dedykowany Python script z `--mode lab-side` lub SSH variant
- Explicit kill criterion w docstring (np. "accuracy < 50% = random baseline")
- JSON output z timestamp w `iter0b_poc/results/`
- PASS/FAIL verdict + per-class breakdown + per-type analysis
- Decision tree A/B/C w DEC ADR template:
  - A 4/4 PASS → AUTHORIZE next iteration
  - B 1-3 FAIL → CONDITIONAL z per-test fallback (np. T1 FAIL → upgrade Tier 2 wcześniej; T3 FAIL → fallback Bielik 1.5B/3B)
  - C 4/4 FAIL → STOP + escalate (per CLAUDE.md anti-pattern „Nie zatwierdzaj 4. rotacji domeny")

## Lesson z T1 mDeBERTa (2026-05-16)

T1 dwukrotnie uruchomione:
- **Run 1:** 6.1% FAIL — diagnoza: bug w halu_injector (WSZYSTKIE positive labelled CONTRADICTED, ale `factual_fabrication` to NIE contradiction → unsupported claim → NEUTRAL)
- **Run 2 po fix:** 80.6% PASS — type-aware `_HALU_TYPE_NLI_LABEL` map (factual_fabrication=NEUTRAL, reszta=CONTRADICTED)

**Wniosek:** debug-first przed claim FAIL. Suspicious low results (6%) zazwyczaj = bug w eval setup, NIE problem modelu.

## Why

Speed-run mode + 3 pivots history = scope creep ryzyko KAŻDEJ iteracji. Wariant B pattern catches przed kontynuacją w bad state. Devil's advocate agent jest tańszy niż obronowa porażka. Build-first-finalize-last (CLAUDE.md Wzorzec 8) wymaga że POC tests są PIERWSZE, pisanie OSTATNIE.

## How to apply

- **Sprawdź sygnały scope creep** co iteracja: dataset growth >2× planu, drafts przed POC, ratio chunks:halu_pairs <0.1, 80%+ off-topic per własna kategoryzacja.
- **Spawn devil's advocate agent** z explicit „brutal, no validation, cite CLAUDE.md sprzeczności" — nie pisz krytyki sam (bias).
- **Wait sign-off** na A/B/C przed execute — NIE auto-cleanup.
- **Archive zamiast delete** — audit trail dla obrony („dlaczego Pani dropowała X — ze względu na Y, archived w Z").
- **POC kill criteria PIERWSZE** — przed full build pipeline. T1-T4 pattern dla każdej major iteracji.
- **Po fix wracać do build, NIE spawn kolejnego agenta krytyki** (cross-ref: outsourced decisiveness w feedback_collaboration.md). Devil's advocate jest single-shot na trigger, nie infinite loop. Jeśli Magda waha post-cleanup → nazwij trade-off + binary choice, nie kolejne reviewer round.
