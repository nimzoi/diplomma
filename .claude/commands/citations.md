---
description: Audit citations in a thesis document — phantom citations, wrong years/initials, duplicates. Delegates to citation-checker subagent.
---

Argument: $ARGUMENTS — path to .docx file (np. `thesis_elements/R02_literatura.docx`)
albo "all" żeby przeskanować wszystkie istniejące rozdziały.

## Procedura

1. **Eksportuj .docx do markdown** przez docling (citation-checker subagent nie ma
   tooli docling, więc Ty musisz tu pomóc):
   ```
   docling.convert_document_into_docling_document(source=PATH)
   docling.export_docling_document_to_markdown(document_key=...)
   ```
2. **Zapisz markdown** do `thesis_research/drafts/{filename}_citations_check.md` (tymczasowo).
3. **Deleguj do citation-checker subagent** przez `Agent({subagent_type: "citation-checker", ...})`
   z prompt zawierającym ścieżkę do markdown export.
4. Subagent wróci z raportem w formacie:
   ```
   [N] [🟢/🟡/🔴] CITATION_TEXT
       Issue: ...
       Source check: URL jeśli znaleziona
       Recommendation: ...
   ```
5. **Przedstaw raport autorce.** NIE auto-fix. Tylko reportuj.
6. **Po review autorki** — jeśli zdecyduje co poprawić, dopiero wtedy modyfikuj
   plik (i tylko punkty które wskazała).

## Co flagujemy (z brief sekcja 8)

- Phantom citations (brak dowodu że praca istnieje)
- Wrong author initials
- Wrong years (np. cited as published po faktycznej dacie)
- Duplicate footnote anchors
- Missing pages/volumes dla papers
- Niespójność year-venue (np. "Zheng 2023 NeurIPS 2024")

## Po raporcie — sprzątanie

Usuń tymczasowy plik `thesis_research/drafts/{filename}_citations_check.md` (po
sign-off autorki). Albo zostaw jako artefakt — zapytaj.
