# Plan zadania 10 — Self-Assessment (0 pkt, same deadline jako Task 11)

**Institutional source:** `assignments/10.md` (Task 10, **0 pkt** — self-check only)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/11-Full-Practical-Part-Review.md` (Assignment 11)
**Mapuje na:** Self-review across R1-R8 + repository state (NIE osobny rozdział)
**Iteracja realizacji:** 8 (finalization) — **same deadline jako Task 11**, MUST być done first

## 1. Czego instytucjonalnie wymaga Task 10

**Self-check** (NIE graded — 0 pkt). 4 parts:

### Part 1: Yes/No questions (9 pytań)

1. Clear background/motivation/aims/scope w R1?
2. Critical lit analysis w R2 (NIE summary)?
3. Data types properly described + metadata w R3?
4. Complete EDA + statistics + visualizations w R4?
5. Standardization + normalization explained + justified w R4?
6. ML models consistent 8-element structure w R6?
7. IT system architecture (layers/integration/security/deployment) w R5?
8. Results & discussion (outcomes/tables/figures/interpretation/limitations) w R7?
9. Summary + conclusions + future work w R8?

### Part 2: Short answers (6 questions)

10. One major strength of the thesis (structure/methodology adherence)
11. One area to improve (methodological completeness)
12. ML descriptions sufficient for replication?
13. IT architecture meets scalability/security/integration criteria?
14. Best vs weakest preprocessing stage?
15. Objectives alignment z ML results — achieved?

### Part 3: Practical task (1 question)

16. Propose one additional plot/table/metric to improve ML model assessment.

### Part 4: Final overall evaluation (1 sentence)

17. One-sentence overall assessment of thesis technical + academic quality.

## 2. Czego wymaga PRO-D-THESIS Assignment 11

**Full Practical Part Review** — structural verification:

- A. **Logical continuity verification** — czy RQ z A1 jest answered w results? Czy gap z A2 engaged? Czy A3 architecture implemented?
- B. **Completeness of experimental evidence** — baselines, target eval, error analysis, reproducibility
- C. **Internal consistency of writing** — terminology, tables-text alignment, methodological descriptions
- D. **Technical integrity + reproducibility check** — repo state = reported results, configs correspond, seeds consistent, no temporary code
- E. **Identification of necessary corrections** — prioritized list (scientific > logical > clarity > formatting)

## 3. Jak to wygląda w naszym v3.1

### Self-assessment timing

- Wykonane **przed final submission Task 11** (oba mają ten sam deadline)
- 0 pkt — czyli **nie ocena**, ale narzędzie quality control dla autorki
- Output to `thesis_research/self-assessment-task10.md` + `thesis_research/pre-submission-corrections.md`

### Wykorzystanie Defense scaffolding

Self-check = okazja do verify że Defense scaffolding faktycznie się zaszył:

- [ ] **Ablations A1-A4** są w R6 (definition) + R7 (results) — Defense scaffolding pkt 1
- [ ] **Kategoryczna error analysis 6-poziomowa** w R7 sekcja 7.6 — Defense scaffolding pkt 2
- [ ] **5-wymiarowa kontrybucja** explicit paragraph w R8 sekcja 8.2 — Defense scaffolding pkt 3
- [ ] **5 świadomych biases** reflected w odpowiednich rozdziałach (R3 explicit, R5 risk, R7 limitations, R8 limitations)
- [ ] **Cross-register MRR per direction** reported w R7.5 (NIE only aggregate)

## 4. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Self-check Part 1 (9 Yes/No) | Audit każde z 9 pytań przeciwko R1-R8 drafts; flag każde NO z konkretną sekcją braku | Reviews flags, decyduj fixes |
| 2 | Self-check Part 2 (6 short answers) | Drafts proposed answers (~50-100 słów each), Ty edytujesz | Edits + finalizes |
| 3 | Self-check Part 3 (improvement proposal) | Proposes 2-3 candidate plots/tables/metrics z uzasadnieniem (np. SHAP per query type, calibration plot) | Picks one |
| 4 | Self-check Part 4 (1-sentence overall) | Drafts 3 candidate sentences (positive / balanced / critical tones) | Picks one |
| 5 | A11 logical continuity audit | Verify A1 RQ → R7 results mapping table | Reviews findings |
| 6 | A11 experimental completeness | Verify baselines (4) + ablations (A1-A4) + error analysis (6-level) + cross-register (RQ5) all present | Reviews |
| 7 | A11 internal consistency | Audit terminology consistency across R1-R8 + tables-text alignment | Reviews |
| 8 | A11 technical integrity | Verify `main_project/` final state: configs correspond to reported results, seeds consistent, no `# TODO` comments left | Reviews repo |
| 9 | Corrections priority list | Drafts list: critical (must fix przed Task 11) / optional (nice-to-have) / formatting (low priority) | Approves + executes critical |

**Workflow note:** iteracje 1-4 (self-check parts) mogą iść szybko (jedna sesja). Iteracje 5-8 (A11 audits) wymagają deeper analysis per rozdział.

## 5. Co musimy znaleźć / przygotować

### Pre-conditions
- R1-R8 drafted (Iteracja 7 ukończona)
- All experiments completed w MLflow
- Repository final state (no temporary code, no `pdb.set_trace()`, no `# TODO unhinged`)

### Output
- `thesis_research/self-assessment-task10.md` — wypełniona 4-part checklist
- `thesis_research/pre-submission-corrections.md` — prioritized list corrections przed Task 11
- (Opcjonalnie) `thesis_research/a11-review.md` — structural audit findings

## 6. Writing rules application

- Brak bezpośrednich Writing rules (Task 10 jest narzędziem, NIE pisaniem akademickim)
- Format Task 10 deliverable: structured Yes/No + krótkie answers + checklist

## 7. Defense scaffolding application

Self-check **weryfikuje** że Defense scaffolding wszedł — to jest jedyne miejsce w pracy gdzie ktoś (autorka) celowo audytuje że:

- [ ] **A1-A4 ablations** dotarły do R6 + R7 ✓
- [ ] **Error analysis 6-poziomowa** dotarła do R7.6 ✓
- [ ] **5-wymiarowa kontrybucja** dotarła do R8.2 explicit ✓

Jeśli któryś element jest missing → critical correction przed Task 11.

## 8. Acceptance checklist

### Part 1 (Yes/No, 9 pytań) — wszystkie odpowiedzi
- [ ] Wszystkie 9 pytań answered
- [ ] Każde NO ma flag z konkretną sekcją braku
- [ ] Wszystkie critical NOs scheduled do fix przed Task 11

### Part 2 (short answers, 6 pytań)
- [ ] Wszystkie 6 thoughtful (NIE one-word)
- [ ] Each ~50-100 słów

### Part 3 (improvement)
- [ ] 1 actionable improvement proposed z uzasadnieniem

### Part 4 (overall)
- [ ] 1 sentence overall evaluation

### A11 reviews (z PRO-D-THESIS)
- [ ] Logical continuity verified (RQ → results mapping table)
- [ ] Experimental completeness verified (4 baselines + 4 ablations + 6-level error + RQ5)
- [ ] Internal consistency verified (terminology + tables-text)
- [ ] Technical integrity verified (repo clean, configs match, seeds consistent)

### Output
- [ ] `self-assessment-task10.md` written
- [ ] `pre-submission-corrections.md` written (z prioritization)

## 9. Risks / common pitfalls

- ❌ **Self-check jako formality** → faktycznie używaj jako quality control narzędzie przed Task 11; lepiej znaleźć gap teraz niż w obronie
- ❌ **Self-check po Task 11** → MUST być **przed** (same deadline, ale Task 10 first)
- ❌ **Brakuje gap w Yes/No** (np. brak EDA visualizations) → critical correction przed Task 11 submission
- ❌ **A11 review pominięty** → strukturalne problemy zostają niezauważone (kosztowne w defense)
- ❌ **Self-assessment over-optimistic** → balanced honest evaluation (autorka jako recenzent siebie samej); promotor wykryje rozbieżność
- ❌ **`# TODO` komentarze w repo** → znaczy że nie wszystko done; usuń lub flag jako known limitation w R8
