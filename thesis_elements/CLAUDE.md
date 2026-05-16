# thesis_elements/

Draft rozdziałów `.docx` (Iter. 7 writing phase). Drafty markdown w `thesis_research/drafts/` PUSTE per build-first-finalize-last.

## Konwencja nazw

`R{NN}_{slug}.docx` — np. `R01_wprowadzenie.docx`, `R05_architektura.docx`.

| NN | Slug | Treść |
|---|---|---|
| 01 | wprowadzenie | tło RAG + halucynacje + citation grounding + RQ1-RQ4 (3+1) + luka PL (Mu-SHROOM 2025 pominął polski) |
| 02 | literatura | ~30 ref: halu detection 2024-2026 (Farquhar→SEP→AggTruth), citation-grounded RAG (Wallat 2025 2-metric), polish NLP, „Mirage of Halu Detection" EMNLP 2025 |
| 03 | dane | Polish CitationBench v0.6 (11k chunks + 5,402 halu pairs), 9 source_types, Wariant B cleanup audit, halu injection 5 typów, NLI 3-tier labeling |
| 04 | eda | rozkłady halu types + source_type distribution + citation lengths + scope filter audit |
| 05 | **architektura** (CENTRALNY) | 7 figur Mermaid (per `.claude/commands/diagram.md`): C4 Context/Container + RAG flow + probe extraction + 3-tier verifier + continuous improvement loop + observability+drift |
| 06 | modele | probe details (LR linear primary + MLP ablation, Bielik 11B v3 layer 47) + 3-tier verifier (mDeBERTa ✓ T1 PASS + HerBERT + LLM judge) + ablations A0-A4 |
| 07 | wyniki | probe AUROC + bootstrap CI vs baselines (Lynx, HHEM, gliclass) + citation accuracy (Wallat 2-metric) + cykle retraining + error analysis 6-poziomowa |
| 08 | podsumowanie | synteza RQ1-RQ4 + 5-wymiarowa kontrybucja + future work (multi-turn, cybersec, cross-domain) |

## Format PJATK

- **Font:** TNR 12pt, line 1.5, margins 2.5cm A4
- **Headings:** H1 bold 14pt, H2 bold 12pt (sprawdź wersję template Task 09)
- **Footnotes:** IEEE z bookmark anchors, 10pt
- **Bibliografia:** ≥30 pozycji, alphabetical, footnotes-style
- **Length:** ≥45,000 znaków (≈25 stron)
- **Abstract:** PL + EN max 1000 znaków każdy + 3-5 keywords
- **Listy tabel/rysunków** mandatory if used
- **Binding:** hardbound (granatowy/czarny/bordowy/zielony)

## Workflow rozdziału

1. **Outline** — H1/H2/H3 w chacie. Sign-off Magdy ZANIM piszesz.
2. **Read context** — `02_konspekt_v3.2_skeleton.md` (mapowanie do rozdz.) + `decisions/DEC-003` + `decisions/DEC-004` + (R3/R4) `notes/scope_cleanup_decisions_2026-05-16.md` + (R2/R6) `research/halu_detection_sota_2024_2026.md` + `research/nli_models_2026_update.md`
3. **Draft** — pełen tekst. Reguły: time-proofed, cytacje verifiable, defensibility nad novelty, spójna terminologia z konspekt v3.2, **czysty polski akademicki** (NIE codemix EN-PL).
4. **Self-review** (checklist niżej)
5. **Citation pass** — `/citations PATH` (citation-checker subagent)

## Workflow .docx

Bezpośrednia edycja .docx przez `python-docx` jest fragile. Preferowany:
1. Claude tworzy markdown w `thesis_research/drafts/R{NN}_draft.md`
2. Magda kopiuje do Worda + formatuje ręcznie
3. Finalna wersja → `thesis_elements/R{NN}_{slug}.docx`

Jeśli explicit prosi o `python-docx` — OK, ale potwierdź.

## Writing rules (z promotor feedback v1)

### R1 — classic intro structure (NIE RQ-first)

Kolejność: Background (25-30%) → Motivation+Problem (20-25%) → Aim+Objectives (15%) → Scope (10%) → Thesis Structure (10%) → **RQ+H na KOŃCU (15%)**

Minimum **10-15 cytacji** w R1 (RAG, halu detection, citation grounding, hidden-states probes, polish NLP, MLOps).

### R2 — explicit selection methodology

Sekcja 2.1 "Metodologia przeglądu":
- Inclusion + exclusion criteria + search strategy (bazy + keywords) + selection pipeline + final count

Tabele consistent:
- Identyczne kolumny per typ (*Author, Year, Method, Contribution, Limitation*)
- Identyczna szerokość, sortowanie po jednym kryterium (rok wzrastająco)
- Numeracja: Tabela N.M w R N

Evidence-to-conclusion explicit:
- Po każdej tabeli: sekcja "Synteza" cytująca **konkretne wiersze** per IEEE
- *„Tabela 2.X pokazuje, że X autorów [3, 5, 7] proponuje Y..."* — NIE *„Z tabeli wynika że Y jest popularne"*

### Academic style (wszędzie R1-R8)

- Trzecia osoba / strona bierna (*„W pracy zaprojektowano…"*, NIE *„Zaprojektowałam…"*)
- Bez potocyzmów, krótkie zdania (1 zdanie = 1 myśl)
- Bez time-proofing: „obecnie", „rosnące", „brak", „jedyny", „żaden"
- Bez emoji
- Konsystentne kursywy dla terminów technicznych przy 1st wystąpieniu
- Czysty polski (NIE codemix EN-PL)

## Self-review checklist

- [ ] R1: classic intro (background → ... → RQ na końcu)
- [ ] R1: min. 10-15 cytacji
- [ ] R2: explicit selection methodology
- [ ] R2: consistent table formatting + numeracja
- [ ] R2: evidence-to-conclusion linking
- [ ] Academic style throughout
- [ ] Brak time-proofing zakazanych słów
- [ ] Brak phantom citations (`sdadas/polish-nli` NIE istnieje)
- [ ] PJATK format zachowany
- [ ] Brak farma/ChPL/Ulotka/reranker (DEC-003 OUT)

## Defense scaffolding (zaszyj w odpowiednich rozdziałach)

### 1. Ablation studies w cyklu 1 (R6 + R7)

| Ablacja | Wariant | Cel diagnostyczny |
|---|---|---|
| **A0 baseline** | Probe layer 47 + mDeBERTa Tier 1 + Bielik 11B + post-hoc citation | Pełen pipeline reference |
| **A1: probe → semantic entropy** | Farquhar 2024 classic uncertainty | Czy hidden-states bije classic uncertainty? |
| **A2: probe target → 1.5B/3B vs 11B** | Probe na mniejszy Bielik | Trade-off compute vs detection quality |
| **A3: verifier → LLM-judge** | Bielik / PLLuM / Gemma 3 / Claude Haiku zamiast mDeBERTa | Programatic NLI vs LLM-judge dla polish (RQ4 supporting) |
| **A4: citation → generation-time** | Outlines structured output zamiast post-hoc | Generation-time vs post-hoc dla polish (pending T2 lab PASS) |

**R7 dodatkowo:** gliclass-multilang-ultra jako Tier 0 alternative (per `research/nli_models_2026_update.md`).

### 2. Error analysis 6-poziomowa (R7)

Po każdym cyklu retreningu probe, kategoryzacja błędów na próbce ≥100 niepoprawnych predykcji:

| Kategoria | Definicja | Mitygacja |
|---|---|---|
| Factual fabrication | Claim NIEobjęty retrieved context | Probe re-train z więcej factual_fabrication |
| Entity confusion | Pomyłka podmiotów | NLI verifier secondary signal |
| Temporal drift | Błędna data/okres | Probe re-train (Wariant B drop CHF noise) |
| Negation flip | Subtle odwrócenie sensu | Hardest case, known limitation flag R8 |
| Paragraph mis-citation | Cite art. X ale treść z Y | Citation alignment catches independently |
| Ambiguous claim | Multi-interpretable | Acceptable — flag, NIE liczyć jako error |

Nawet jeśli AUROC nie poprawia się, **rozkład błędów to wartościowy wynik metodologiczny**.

### 3. Negative-result publishability (R8)

Zaszyj paragraf w R8.1/R8.2:

> *„Wkład pracy ma pięć niezależnych wymiarów. Empiryczna magnitude poprawy probe AUROC (RQ1) jest tylko jednym z nich: (1) Metodologiczny — pierwszy publicznie udokumentowany polish halu detection methodology; (2) Inżynierski — reprodukowalny pipeline RAG+probe+verifier open-source; (3) Artefaktowy — 3 HuggingFace artifacts (CitationBench v0.6, probe model, mDeBERTa verifier); (4) Eksperymentalny — porównanie polish probe vs Lynx + HHEM + gliclass + Wallat 2-metric; (5) Korpusowy — pierwszy polish CitationBench z deterministic citation grounding (ISAP-based). Każdy wymiar broni się niezależnie. W przypadku odrzucenia H1 (AUROC <0.70 lub CI lower <0.60), wkład (2)-(5) stoi niezależnie, z dataset jako standalone publishable artifact."*

Defensive shield dla obrony — promotor widzi *"co jeśli probe leży?"* zanim padnie pytanie.

## Anti-patterns

- Nie pisz rozdziału bez outline + sign-off
- Nie cytuj z głowy (`sdadas/polish-nli` PHANTOM, `finecat-nli-l` license UNSPECIFIED)
- Nie używaj time-proofing zakazanych słów
- Nie commituj wersji bez peer-glance Magdy (chyba że poprosi)
- Nie usuwaj defense scaffolding — świadoma obrona, nie dekoracja
- Nie wracaj do farma/ChPL/Ulotka/reranker — DEC-003 OUT

## Koniec sesji nad rozdziałem

Zawsze kończ:
```
Co dalej w tym rozdziale:
1. [konkretny krok, max 2h]
2. [opcjonalny drugi]
3. [opcjonalny trzeci]
```
