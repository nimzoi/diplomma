# Archive — drafts pre-clean (Wariant B 2026-05-16)

**Data archiwizacji:** 2026-05-16
**Powód:** Krytyczna ocena scope (`thesis_research/notes/KRYTYCZNA_ocena_scope_2026-05-16.md`)
RED FLAG #3: drafty R3/R4/R5 sprzeczne z `thesis_research/CLAUDE.md` § Drafts
„PUSTY po pivot DEC-003" + Wzorzec 1 (sign-off before output) + Wzorzec 8
(build-first-finalize-last).

## Files

- `R3_dane.md` (41 kB) — pre-cleanup data chapter draft (v0.4 dataset, pre-Wariant B)
- `R4_eda.md` (36 kB) — pre-cleanup EDA chapter draft
- `R5_architektura.md` (37 kB) — pre-cleanup architecture chapter draft

## Status

**STALE** — write-off do future reference only:
- Dataset reference: v0.4 (17,862 chunks) — obecny: **v0.6 (11,000 chunks)** post-strict cleanup
- Architecture: pre T1 PASS — obecny: confirmed mDeBERTa Tier 1 (T1 80.6%) + 3-tier strategy
- Halu pairs: pre-fix labels (ALL CONTRADICTED) — obecny: type-aware (factual_fabrication=NEUTRAL)
- NIE używaj jako podstawa Iter. 7 writing — pisać świeżo z aktualnym contentem

## Reuse w Iter. 7 writing

Można wziąć **structural patterns** (sekcje, tabele template, podrozdziały) ale NIE
content — content będzie świeży po Iter. 1-6 ablation results.

Przykład reuse:
- R3 v3.2 sekcje 3.1-3.10 (per-source methodology) — mogą replikować layout z R3_dane.md ALE numbers + tables musi być z v0.6 + S2/S6 + raw_archive sweep stats
- R4 v3.2 — same: layout EDA + 3 chunking strategies + 7 świadomych biases + plots — content z v0.6 + 5,402 halu pairs distribution
- R5 v3.2 — 7 figur architectury Mermaid mogą być re-templated, content z confirmed POC results (T1 mDeBERTa, T3 layer 47, T2 Outlines)

## Restore (jeśli kiedyś potrzebne)

```bash
git mv thesis_research/_archive/v3.2-pre-clean/drafts/R3_dane.md thesis_research/drafts/
# itd.
```
