---
description: Work on a specific thesis chapter (R01-R08). Outline + sign-off → draft → review.
---

Argument: $ARGUMENTS (np. "R01", "1", "wprowadzenie", "5 architektura")

## Mapowanie

| NN | Slug | Treść |
|----|------|---|
| 01 | wprowadzenie | tło, problem, RQ |
| 02 | literatura | review ~30 źródeł |
| 03 | dane | 5-6 źródeł psychiatrii, codebooks |
| 04 | eda | EDA + standaryzacja + normalizacja |
| 05 | architektura | **CENTRALNY** — 5 z 7 figur |
| 06 | modele | reranker + LLM-as-judge |
| 07 | wyniki | baselines × cykle, error analysis, drift |
| 08 | podsumowanie | synteza + future work |

## Workflow (zawsze ta kolejność)

1. **Locate or create** `thesis_elements/R{NN}_{slug}.docx`. Jeśli tworzysz nowy
   plik — **zapytaj autorkę o potwierdzenie** zanim utworzysz.
2. **Read relevant context** (W TEJ KOLEJNOŚCI):
   - `thesis_research/02b_konspekt_v3_updates.md` — **delta nadrzędna** (domena farmakologia, RQ5 cross-register)
   - `thesis_research/02_konspekt_v3_FINAL.docx` — sekcja mapująca do rozdziału (dla NIE-zmienionych sekcji)
   - `thesis_research/sources_catalog.md` — gdy R3 (Dane) lub R4 (EDA)
   - `thesis_research/decisions/DEC-001*.md` + `DEC-002*.md` — gdy uzasadnienia domenowe / cross-register
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
