# Plan zadania 07 — Wyniki, Dyskusja i Prezentacja (R7)

**Institutional source:** `assignments/07.md` (Task 07, 10 pkt)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/09-Results-Analysis-and-Interpretation.md` (Assignment 9)
**Mapuje na rozdział:** R7 Wyniki + Dyskusja
**Iteracja realizacji:** 8 (finalization) — pre-condition: Iteracje 2-6 ukończone z wszystkimi metrykami w MLflow

## 1. Czego instytucjonalnie wymaga Task 07

- Organize results **per experiment / RQ**, NIE per tool/dataset
- Tables + figures (numerowane, podpisane, referenced w text)
- Metrics z confidence intervals lub std
- Comparisons (baseline vs target, ablation, sensitivity)
- Visualizations: learning curves, confusion matrices, ROC/PR, error analysis examples
- Discussion: interpretation + relate to literature + limitations + strengths/weaknesses

## 2. Czego wymaga PRO-D-THESIS Assignment 9

- A. Consolidated comparative results (all baselines + target + variability)
- B. Structured error analysis (where model fails, failure types, patterns)
- C. Model interpretability + feature contribution (SHAP / sensitivity / attention)
- D. Robustness + stability assessment (variance across folds, hyperparam sensitivity)
- E. Alignment z research question + hypothesis (explicit answer)

## 3. Jak to wygląda w naszym v3.1

### Organizacja R7 per 5 RQ + error analysis + synthesis

#### Sekcja 7.1: RQ1 — Retraining effectiveness

- **Tabela 7.1.1:** baselines × cykle 1/2/3 × seeds (mean ± std)
- Metryki: nDCG@10, MRR@10, recall@10
- **Figura 7.1.1:** training curves (z MLflow)
- **Figura 7.1.2:** baseline vs cykl 1/2/3 comparison plot
- Discussion **descriptive** — co znaczy konkretna magnitude poprawy w kontekście BEIR domain adaptation (5-15pp expected)
- Statistical significance: t-test seed-pairs (1 statystyka per claim, NIE p-value cult)

#### Sekcja 7.2: RQ2 — LLM-judge quality

- **Tabela 7.2.1:** Cohen's kappa table per judge × protocol (pairwise/pointwise/faithfulness/cross-register)
- **Tabela 7.2.2:** Agreement % vs autorka manual labels (200 par psych subset)
- **Figura 7.2.1:** Confusion matrix judge predictions vs manual (3-class: A/B/tie)
- **Negative findings explicit** — jeśli kappa <0.50 dla protokołu, to też wynik z analizą prompt design failures
- Comparison z literaturą (Karp 2025 PL legal LLM-judge kappa)

#### Sekcja 7.3: RQ3 — Plateau analysis (3 cykle retreningu)

- **Tabela 7.3.1:** Cycle × metric trend (1 → 2 → 3)
- **Figura 7.3.1:** Marginal gain per cycle (line chart)
- Plateau confirmation OR rejection (H3 expected: ≤2pp cykl 3 vs cykl 2)
- Discussion: dlaczego plateau (judge label saturation? model capacity? data redundancy?)

#### Sekcja 7.4: RQ4 — Drift detection

- **Tabela 7.4.1:** Simulated OOD results (precision/recall per threshold)
- **Figura 7.4.1:** ROC curve drift detector
- **Figura 7.4.2:** Detection latency vs threshold trade-off
- False positive analysis (in-distribution flagged as OOD — wzorce)

#### Sekcja 7.5: RQ5 — Cross-register retrieval

- **Tabela 7.5.1:** **MRR + accuracy@10 PER DIRECTION** (lay→pro vs pro→lay separately)
- **Tabela 7.5.2:** Direction asymmetry gap `Δ_dir` per training variant (ChPL-only vs ChPL+Ulotka — A4 ablation)
- **Figura 7.5.1:** Per-direction performance comparison
- **Figura 7.5.2:** Example cross-register query-passage pairs (positive + negative)
- Discussion: czy training na pairs naprawdę pomaga w cross-register (A4 evidence)

#### Sekcja 7.6: **Kategoryczna error analysis** (Defense scaffolding pkt 2)

**6-poziomowa taksonomia z thesis_elements/CLAUDE.md Defense scaffolding:**

| # | Kategoria błędu | Definicja |
|---|---|---|
| 1 | Terminology miss | Query lay synonym, top-1 professional synonym wrong |
| 2 | Ambiguous query | Query pasuje do ≥2 sekcji (acceptable, flag) |
| 3 | Length mismatch | Gold passage znacznie dłuższy/krótszy niż top-1 |
| 4 | OOD chunk | Top-1 dotyczy nie tej klasy ATC co query |
| 5 | Register mismatch (RQ5-specific) | Query lay → top-1 lay (gold = professional) lub odwrotnie |
| 6 | OCR artifact | Top-1 z uszkodzonym tekstem |

- **Tabela 7.6.1:** Distribution kategorii błędów per cykl (1/2/3) na próbce 100 incorrect rankings per cykl
- **Figura 7.6.1:** Histogram error categories per cykl
- **Tabela 7.6.2:** Top 3 dominant error patterns z rekomendacjami dla future work

#### Sekcja 7.7: Cross-RQ synthesis + limitations

- **Tabela 7.7.1:** 5 RQ × Status (supported/rejected/partial) × Evidence (sekcja reference)
- Mapping 5 RQ → 5 wymiarów kontrybucji (Defense scaffolding pkt 3)
- Limitations explicit (per category):
  - Dataset: Iteracja 0 OCR overhead, biases z R3
  - Model: BGE-M3 frozen, polish-reranker ~360M scale
  - Eval: 200 par psych subset (świadomy bias), simulated drift NIE real
  - External: PL-only, single domain

### Discussion format (Task 07 wymóg)

Po każdej tabeli/figurze — paragraf interpretacji w 4 częściach:
1. **Co tabela pokazuje** (literal description)
2. **Co to znaczy** (interpretation)
3. **Jak to się odnosi do literatury** (R2 references z [N] format)
4. **Limitacje** (transparent)

## 4. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Outline R7 | Proponuje 7 podsekcji per RQ + error analysis + synthesis | Sign-off |
| 2 | Sekcja 7.1 RQ1 results | Drafts tabelę + 4-part discussion descriptive | Reviews data accuracy |
| 3 | Sekcja 7.2 RQ2 judge | Drafts kappa tabela + interpretation + literature comparison | Reviews |
| 4 | Sekcja 7.3 RQ3 plateau | Drafts chart + interpretation | Reviews |
| 5 | Sekcja 7.4 RQ4 drift | Drafts ROC + interpretation + false positive analysis | Reviews |
| 6 | Sekcja 7.5 RQ5 cross-register | Drafts MRR per direction + Δ_dir asymmetry + A4 evidence | Reviews |
| 7 | Sekcja 7.6 Kategoryczna error analysis | Drafts 6-poziomową distribution per cykl + patterns | Reviews accuracy |
| 8 | Sekcja 7.7 Cross-RQ synthesis | Drafts 5 RQ status table + limitations | Reviews coherence |
| 9 | Citation pass | `/citations` (R2 references) — comparison z literature claims | Reviews findings |
| 10 | Writing rules check | Style audit + table consistency + evidence-conclusion linking | Final read-through |

**Workflow note:** sekcje 7.1-7.5 mogą być drafted paralelnie po sign-off na outline + dostępność wszystkich metryk w MLflow.

## 5. Co musimy znaleźć / przygotować

### Pre-conditions
- Iteracje 2-6 ukończone z MLflow runs zarchiwizowane
- Error analysis dataset (100 incorrect rankings per cykl) extracted z eval logs
- Drift simulation results dla RQ4
- Cross-register 1800 par eval results dla RQ5
- 4 ablations A1-A4 z osobnymi MLflow runs

### Artefakty
- ~10-15 tabel (wyniki per RQ + ablations + error analysis + cross-RQ synthesis)
- ~8-12 figur (learning curves, ROC, confusion-style for ranking, UMAP, error histograms, example pairs)
- Wszystkie z 3 random seeds → mean ± std + 95% CI

## 6. Writing rules application

- Reguła 5 **consistent table formatting**: ~15 tabel R7 z jedną konwencją (Method | Cycle | Metric | mean ± std | CI)
- Reguła 6 **evidence-conclusion linking**: **kluczowe** — każda interpretacja cytuje konkretną tabelę/figurę z numerem (np. *„Tabela 7.1.1 pokazuje, że cykl 1 daje X pp poprawy nDCG@10 vs base [Sekcja 6.2 baselines], co jest zgodne z BEIR results [Thakur 2021]"*)

## 7. Defense scaffolding application

**Wszystkie 3 mikro-podszepty FULL DEVELOPMENT tu:**

1. **Ablations A1-A4 reported** w sekcji 7.1 (jako sub-tables per cykl) + 7.5 (A4 cross-register specific)
2. **Kategoryczna error analysis** = pełna **sekcja 7.6** z 6-poziomową taksonomią
3. **Negative-result framing** w 7.7 explicit z odniesieniem do R8 (5-wymiarowa kontrybucja)

## 8. Acceptance checklist

- [ ] 5 podsekcji per RQ + error analysis + cross-RQ synthesis = 7 sekcji
- [ ] Każda tabela referenced w tekście (grep audit)
- [ ] Każda figura podpisana + referenced
- [ ] Mean ± std lub 95% CI w wszystkich metrykach
- [ ] Kategoryczna error analysis 6-poziomowa kompletna z distribution per cykl
- [ ] Limitations explicit w 7.7 (4 kategorie)
- [ ] Cross-RQ synthesis mapping 5 RQ → 5 wymiarów kontrybucji
- [ ] Discussion format 4-part po każdej tabeli/figurze
- [ ] Ablations A1-A4 reported

## 9. Risks / common pitfalls

- ❌ Over-formalizm statystyczny (promotor wytknął w v1 "szafowanie") → effect size + std priority, p-value cult NO
- ❌ Selective reporting → wszystkie 5 RQ raportowane explicit, nawet jeśli H odrzucona (H1 negative w 7.1 still reported)
- ❌ Brak 4-part interpretation paragraph po każdej tabeli → Task 07 explicit wymóg
- ❌ Cherry-picked figures → balanced positive/negative
- ❌ Brak error analysis 6-level → Defense scaffolding wymóg
- ❌ Tabele inconsistent format → Writing rule 5 audit
