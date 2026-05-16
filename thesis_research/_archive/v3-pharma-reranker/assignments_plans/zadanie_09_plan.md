# Plan zadania 09 — Formal & Editorial Requirements

**Institutional source:** `assignments/09.md` (Task 09, 10 pkt)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/10-Writing-the-Methodology-and-Technical-Chapters.md` (Assignment 10) — partial mapping
**Mapuje na:** Apply across all R1-R8 + bibliografia + listy + abstract + binding
**Iteracja realizacji:** 8 (finalization) — apply jako transversal compliance

## 1. Czego instytucjonalnie wymaga Task 09

### Mandatory structure (12 elementów w kolejności)

1. Title page (institutional template)
2. Abstract (max 1000 znaków + PL dla non-PL theses)
3. Keywords (3-5)
4. Table of contents (auto-generated z proper headings)
5. List of abbreviations (jeśli aplikuje)
6. Introduction (R1)
7. Main chapters + subchapters (R2-R7, numbered, no period after titles)
8. Conclusion/Summary (R8)
9. List of tables (jeśli tabele są)
10. List of figures (jeśli figury są)
11. Bibliography (alphabetical)
12. Additional materials / appendices (jeśli aplikuje)

### Formatting strict

- **Font:** Times New Roman 12pt main text, **10pt footnotes**
- **Line spacing:** 1.5
- **Margins:** 2.5cm all sides
- **Alignment:** justified
- **Page numbers:** mandatory
- **Headings:** Chapter Bold 14pt; Subchapter Bold 12pt
- **No periods** po chapter/subchapter titles

### Citations (Task 09 preferred: footnotes)

- All citations w footnotes (NIE in-text), 10pt
- Punctuation after footnote number
- Repeated refs: *Ibidem*, *op. cit.*
- Paraphrazowane: *cf.* / *see*
- Internet sources: URL + access date

### Bibliography

- Alphabetical by surname
- Tylko cited sources (1:1 with footnotes)
- Multiple works per author: alphabetical by title

### Tables/figures

- Title **above** tables (no period)
- Source **below** (with period)
- All tables → List of tables
- All figures → List of figures

### Length (Bachelor's)

- Min **45,000 characters** (~25 stron equivalents)

### Binding

- **Hardbound** w ciemnym kolorze (navy / black / burgundy / dark green)
- Cover z thesis type explicit ("Praca inżynierska")

## 2. Czego wymaga PRO-D-THESIS Assignment 10 (partially)

A10 dotyczy writing the methodology and technical chapters (głównie R3-R6 + R10 finalization). Apply z Writing rules `thesis_elements/CLAUDE.md` (6 reguł z promotor feedback v1).

## 3. Jak to wygląda w naszym v3.1

Apply Task 09 jako **transversal compliance** across R1-R8 docs + bibliografia + abstract + listy.

### Format checklist global

- [ ] TNR 12pt main text, 10pt footnotes
- [ ] Line spacing 1.5
- [ ] Margins 2.5cm
- [ ] Justified text
- [ ] Page numbers mandatory
- [ ] Heading hierarchy consistent (Chapter Bold 14pt, Subchapter Bold 12pt)
- [ ] No periods po heading titles
- [ ] Single-sided lub double-sided (author's discretion)
- [ ] Footnotes 10pt z punctuation after number

### Bibliography compliance

- [ ] Min 30+ pozycji (target z R2 Literature Review)
- [ ] Alphabetical by surname
- [ ] IEEE format consistent
- [ ] Wszystkie citations w tekście → wszystkie w bibliografii (1:1 mapping audit)
- [ ] Internet sources z URL + access date
- [ ] Multiple works same author: alphabetical by title

### Tables/figures lists

- [ ] List of tables: ~20-30 pozycji (R3-R7 mają większość)
- [ ] List of figures: ~15-20 pozycji
- [ ] Każda numerowana per rozdział (Table 5.1, 5.2, Figure 7.3, etc.)
- [ ] Każda referenced w tekście (grep audit)
- [ ] Title above tables (no period), source below (with period)

### Abstract requirements

- [ ] **PL abstract** max 1000 znaków (włącznie ze spacjami)
- [ ] **EN abstract** max 1000 znaków
- [ ] **3-5 keywords PL** + **3-5 keywords EN**
- [ ] Streszczenie merytoryczne: cel + metoda + 5 wymiarów kontrybucji + key wyniki

### Length verification

- [ ] Total characters ≥45,000 (~25 stron Bachelor's)
- [ ] Per rozdział distribution sensible (R5 centralny ~25-30%, R7 wyniki ~20%, others smaller)

## 4. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Format audit script | Audit TNR 12pt + spacing + margins + headings consistency across R1-R8 .docx | Reviews findings |
| 2 | Bibliography compilation | Aggregate all citations z R1-R8, alphabetize, IEEE format consistency check | Reviews completeness |
| 3 | Citation cross-check (`/citations`) | Audit: each in-text citation has bibliography entry (no orphan); each bibliography entry has in-text use (no unused) | Reviews + fixes orphans |
| 4 | Lists generation | Auto-generate List of tables + List of figures z all .docx | Reviews accuracy |
| 5 | Abstract PL draft | Draft 1000-char abstract: cel + metoda + 5 wymiarów kontrybucji + key results | Reviews + edits |
| 6 | Abstract EN draft | Translate z PL OR draft separately (recommended separate) | Reviews translation quality |
| 7 | Keywords selection | 3-5 PL + 3-5 EN keywords (e.g., "MLOps", "Polish RAG", "cross-register retrieval", "pharmacology", "reranker fine-tuning") | Sign-off |
| 8 | Length verification | Character count per rozdział + total ≥45k | Reviews distribution |
| 9 | Heading hierarchy audit | Verify Bold 14pt chapter / Bold 12pt subchapter consistent | Reviews format |
| 10 | Footnotes format audit | Verify 10pt + IEEE style + Ibidem/op.cit. usage | Reviews precision |
| 11 | Tables/figures format audit | Verify title above table (no period) + source below (with period) | Reviews compliance |
| 12 | Final binding-ready check | Pre-print review: cover/title page/structure complete | Final approval before print |

## 5. Co musimy znaleźć / przygotować

### Pre-conditions
- R1-R8 drafted (Iteracja 7)
- Wszystkie citations w tekście (R1-R8)
- Wszystkie figures z proper captions
- Wszystkie tables z proper titles + sources
- PJATK template available (institutional)

### Tools
- Word native styles (PJATK template if available — preferred over manual format)
- `/citations` subagent dla orphan audit
- `python-docx` dla automated character count + format check (optional)
- Pdftk lub similar dla page count verification

### Output
- Final formatted `thesis_final.docx` → PDF export → hardbound print
- Abstract.md (separate file dla EDU upload jeśli wymaga)

## 6. Writing rules application

- Reguła 3 **academic style** global — last-pass check (no time-proofing words, 3rd person)
- Reguła 5 **consistent table formatting** — final audit across ~20-30 tables
- Reguła 6 **evidence-conclusion linking** — last-pass verify każda konkluzja cytuje

## 7. Defense scaffolding application

Brak nowych elementów; Task 09 jest **last verification step**:

- [ ] Ablations A1-A4 są w R6 + R7
- [ ] Error analysis taxonomy 6-poziomowa w R7
- [ ] 5-wymiarowa kontrybucja explicit w R8 abstract + R8 conclusions

## 8. Acceptance checklist

Patrz Task 09 sekcja "Self-Check Checklist for Students" — pełen checklist. Kluczowe:

### Formal Requirements
- [ ] Hardbound w ciemnym kolorze (navy/black/burgundy/dark green)
- [ ] Cover z thesis type stated ("Praca inżynierska")

### Structure
- [ ] Official title page (PJATK template)
- [ ] Abstract ≤1000 znaków + 3-5 keywords (PL + EN if non-PL)
- [ ] Auto-generated table of contents
- [ ] Introduction + conclusion w prawidłowym miejscu
- [ ] All mandatory lists (tables, figures, abbreviations jeśli aplikuje)
- [ ] Bibliography at end

### Length
- [ ] Min 45,000 znaków (Bachelor's)

### Formatting
- [ ] TNR 12pt, line spacing 1.5
- [ ] Margins 2.5cm all sides
- [ ] Page numbers
- [ ] Headings correctly formatted + numbered

### Citations
- [ ] All sources w footnotes IEEE 10pt
- [ ] Correct *Ibidem* / *op. cit.* usage
- [ ] Internet sources z access dates
- [ ] Bibliography alphabetical

### Tables/figures
- [ ] Titles above tables (no period), sources below (with period)
- [ ] Lists of tables/figures included

## 9. Risks / common pitfalls

- ❌ **Inconsistent heading levels** → use Word styles strictly, NIE manual formatting
- ❌ **Citations w tekście NIE w bibliografii** (orphan) → `/citations` audit mandatory
- ❌ **Tables/figures NIE referenced** w tekście → grep audit per rozdział
- ❌ **Length under 45k znaków** → likely problem; expansion w R7+ jeśli potrzeba (NIE w R1)
- ❌ **Abstract over 1000 chars** → strict count limit (włącznie ze spacjami!)
- ❌ **Footnotes IEEE format inconsistency** → manual format check (jeden styl, nie mix)
- ❌ **Heading bez period vs z period** mixing — Word style consistency
- ❌ **PJATK template missing** → kontakt z promotorem / sekretariat WEII
