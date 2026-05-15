# thesis_research/

Source-of-truth dokumenty projektu.

## ⚠ Status (2026-05-15)

**Domena projektu zrotowana:** psychiatria → farmakologia szeroka (psych jako eval subset). Konsekwencje dla dokumentów:

- `02_konspekt_v3_FINAL.docx` — niektóre sekcje **superseded**:
  - II.1 (streszczenie wykonawcze) → patrz `02b_konspekt_v3_updates.md`
  - II.2.1 (domena specjalistyczna jako testbed)
  - II.3.3 (pytania badawcze — dodano RQ5)
  - II.3.4 (scope IN/OUT — drobne modyfikacje)
  - II.4 (cała strategia danych — Plan A całkiem nowy, Plan B deactivated)
  - II.7 (LLM-as-judge — dodano 4. protokół cross-register)
  - II.13 (out of scope — dodano cross-language register transfer)
  - II.15 (strategia rozmowy z promotorem — nowe argumenty)
  - II.16 (next steps — nowy Tydzień 0 dla URPL feasibility)
- **Sekcje aktywne v3 FINAL bez zmian:** II.2.2, II.3.1, II.3.2, II.5, II.6, II.8, II.9, II.10, II.11, II.12, II.14

**Single source of truth:** `02b_konspekt_v3_updates.md` (delta) nadrzędne nad odpowiednimi sekcjami .docx.

Pełen audit trail decyzji w `decisions/DEC-001_wybor-domeny.md` i `DEC-002_chpl-ulotka-pairing.md`.

## Co czytać i w jakiej kolejności

| File | Kiedy | Priorytet |
|------|---|---|
| `01_agent_brief.docx` | ZAWSZE first w nowej sesji | 🔴 P0 |
| **`02b_konspekt_v3_updates.md`** | ZAWSZE second w nowej sesji — delta nadrzędna nad .docx | 🔴 P0 |
| `02_konspekt_v3_FINAL.docx` | Dla NIE-zmienionych sekcji (II.5/II.6/II.8/II.9/II.10/II.11/II.12/II.14) | 🟠 P1 |
| `sources_catalog.md` | Praca nad R3 (dane), R4 (EDA), scrape pipeline | 🟠 P1 |
| `decisions/DEC-001_*.md` | Gdy pytanie "dlaczego farmakologia a nie psychiatria" | 🟡 P2 |
| `decisions/DEC-002_*.md` | Gdy pytanie "skąd cross-register angle" | 🟡 P2 |
| `05_stack_techniczny.docx` | Decyzje technologiczne, uzasadnienia, alternatywy | 🟡 P2 |
| `03_diagrams_architektury.docx` | Praca nad R5 (architektura IT) | 🟡 P2 |
| `04_dev_environment.docx` | Setup kodu, CI/CD, reproducibility | 🟡 P2 |
| `06_raport_feasibility_psychiatria.docx` | Historical context; psych pozostaje jako eval subset | 🟢 P3 |

## Jak czytać .docx

```
docling.convert_document_into_docling_document(source="<absolutna ścieżka>")
  → returns {"document_key": "..."}
docling.export_docling_document_to_markdown(document_key="...")
  → returns markdown
```

**Cold start ~60s** przy pierwszym wywołaniu po starcie sesji. Spodziewaj się timeoutu MCP (30s) przy pierwszej próbie. **Retry once.** Druga próba przejdzie.

Alternatywa dla prostego tekstu (bez struktury): `pypdf` lub `PDF_Tools.read_pdf_content`. Ale dla pracy z thesis dokumentami preferuj docling.

## Drafts

`thesis_research/drafts/` — workspace dla pre-rozdziałowych szkiców, brainstormów, draft sekcji.

## Decisions log

`thesis_research/decisions/` — ADR (Architecture Decision Records) generowane przez `/decision`.

**Active decisions:**
- **DEC-001** (2026-05-15): domena psychiatria → farmakologia szeroka
- **DEC-002** (2026-05-15): ChPL+Ulotka pairing jako 5. RQ

## Sources catalog

`sources_catalog.md` — **single source of truth dla R3 (Dane)**. Pełna tabela źródeł korpusu farmakologicznego z URL-ami, licencjami, scrape methods, mapping na training data dla rerankera. Synchronizuj z `02b_konspekt_v3_updates.md` sekcja II.4.

## Anti-patterns

- **Nie edytuj** istniejących .docx-ów (01-06) bez explicit zgody autorki — to są zatwierdzone source-of-truth artefakty.
- **Nie re-eksportuj** do .docx via Claude bez prośby (formatowanie się rozjedzie).
- **Nie traktuj** żadnego pojedynczego docx jako kanonicznego — zawsze cross-check z `02b_konspekt_v3_updates.md` + DEC log.
- **Nie scrapuj URPL RPL XML równolegle z dane.gov.pl dataset 397** — ten sam content, dedup overhead.
- **Nie zatwierdzaj rotacji domeny ponownie** — DEC-001 to ostateczna decyzja. Jeśli ktoś (Ty, Claude, promotor) sugeruje 4. pivot, najpierw przeczytaj DEC-001 kill criteria.
