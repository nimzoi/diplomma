# diplomma

Inżynierka — projekt i ewaluacja chatbota wiedzy dla JDG (PJATK).

## Status

- **Specyfikacja zadań:** [`descriptions/`](descriptions/) (zadania 01–11 +
  plan zbierania danych w `12_data_collection_execution_plan.md` i pełna
  spec w `data_collection_spec.md`).
- **Zebrany dataset:** [`data/`](data/) — 260 dokumentów, 51/51 tematów
  pokryte. Zobacz [`data/README.md`](data/README.md) i
  [`data/coverage_report.md`](data/coverage_report.md).
- **Skrypty kolekcjonujące:** [`scripts/`](scripts/) — bez headless
  browsera, tylko `requests` + stdlib.

## Następne kroki (poza obecnym etapem)

Parsowanie, chunking, embeddings, retrieval i runtime chatbota — patrz
sekcja 17 specyfikacji (Out of scope dla fazy zbierania).
