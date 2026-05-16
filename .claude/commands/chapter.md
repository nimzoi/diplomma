---
description: Work on a specific thesis chapter (R01-R08). Outline + sign-off → draft → review.
---

Argument: $ARGUMENTS (np. "R01", "1", "wprowadzenie", "5 architektura")

## Mapowanie (v3.2 post-DEC-003)

| NN | Slug | Treść |
|----|------|---|
| 01 | wprowadzenie | tło RAG + halucynacje + citation grounding + 3 main + 1 supporting RQ + luka PL |
| 02 | literatura | review ~30 źródeł (hallucination detection 2024-2026, hidden-states probes, Wallat 2025 2-metric, „Mirage" critique) |
| 03 | dane | Polish CitationBench v0.6: ISAP + UOKiK + EUR-Lex + Reddit + 5 halu types injection + 3-tier NLI labeling + Wariant B cleanup audit |
| 04 | eda | rozkłady halu types + source_type distribution (9 typów) + scope filter audit |
| 05 | architektura | **CENTRALNY** — 7 figur Mermaid (probe + verifier + citation + drift) |
| 06 | modele | hidden-states probe Bielik 11B layer 47 + 3-tier verifier (mDeBERTa T1 ✓ + HerBERT T2 + LLM T3) |
| 07 | wyniki | probe AUROC + bootstrap CI + ablations A0-A4 + Wallat 2-metric + error analysis 6-poziomowa |
| 08 | podsumowanie | synteza RQ1-RQ4 + 5-wymiarowa kontrybucja + future work |

## Workflow (zawsze ta kolejność)

1. **Locate or create** `thesis_elements/R{NN}_{slug}.docx`. Jeśli tworzysz nowy
   plik — **zapytaj autorkę o potwierdzenie** zanim utworzysz.
2. **Read relevant context** (W TEJ KOLEJNOŚCI):
   - `thesis_research/02_konspekt_v3.2_skeleton.md` — **aktualny konspekt v3.2** (sekcja mapująca do rozdziału)
   - `thesis_research/decisions/DEC-003_pivot-na-halu-detection.md` — pivot rationale dla promotora
   - `thesis_research/decisions/DEC-004_iter0b_poc_results.md` — POC results (T1 PASS; T2/T3/T4 pending lab GPU)
   - `thesis_research/notes/sources_z_v3.1_do_reuse_w_v3.2.md` — gdy R1+R2 (24/31 v3.1 refs reusable)
   - `thesis_research/notes/scope_cleanup_decisions_2026-05-16.md` — gdy R3 (Dane) lub R4 (EDA)
   - `thesis_research/research/halu_detection_sota_2024_2026.md` + `probes_polish_llm_research.md` + `nli_alternatives_2026.md` — gdy R2 lub R6
   - `main_project/data/processed/citationbench_v0.6_2026-05-16/DATASET_CARD.md` — gdy R3 lub R4
   - `assignments/{NN}.md` — PRO-D task description dla tego rozdziału
   - `assignments/PRO-D-THESIS-practical-work-main/{NN}-*.md` — practical assignment (rygorystyczne wymagania)
3. **Outline before content** — zaproponuj outline H1/H2/H3 w chacie. **Sign-off
   autorki ZANIM ruszysz z pisaniem treści.** To wzorzec "Decision before output".
4. **Draft** — pełen tekst rozdziału. Reguły:
   - Time-proofed: bez "obecnie", "rosnące", "brak", "jedyny", "żaden"
   - Cytacje verifiable, flag niepewności
   - Defensibility nad novelty
   - Spójność terminologii z konspektem
5. **Self-review** (checklist):
   - [ ] Wszystkie zdania bronią się przed promotorem Kojałowiczem
   - [ ] Brak phantom citations
   - [ ] Footnotes spójnie numerowane
   - [ ] Linki do tabel/rysunków konsekwentne
   - [ ] PJATK format: TNR 12pt, line 1.5, margins 2.5cm (template-driven)
   - [ ] Heading 1 bold 16pt, Heading 2 non-bold 14pt
6. **Citation pass** — zaproponuj uruchomienie `citation-checker` subagent na pliku.

## Konwencja edycji

Bezpośrednia edycja .docx przez `python-docx` jest fragile (formatowanie się rozjeżdża).
**Preferowany flow:**
1. Claude tworzy/edytuje draft jako markdown w `thesis_research/drafts/R{NN}_draft.md`
2. Autorka kopiuje sekcję do Worda i formatuje ręcznie
3. Po zatwierdzeniu — autorka zapisuje finalną wersję do `thesis_elements/R{NN}_{slug}.docx`

Jeśli autorka explicit prosi o python-docx — OK, ale **najpierw potwierdź** że to
chce zrobić tym sposobem.

## Koniec sesji nad rozdziałem

Zawsze kończ wiadomością w formacie:
```
Co dalej w tym rozdziale:
1. [konkretny krok, max 2h]
2. [opcjonalny drugi]
3. [opcjonalny trzeci]
```
