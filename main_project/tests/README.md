# Tests

Pytest test suite dla Polish CitationBench pipeline.

## Run

```bash
cd D:/diplomma
uv run pytest                          # all tests
uv run pytest main_project/tests -v    # verbose
uv run pytest -k schemas               # tylko schema unit tests
uv run pytest -k integration -m       # only integration (slow, requires raw data)
```

## Structure

```
tests/
├── conftest.py             # Pytest fixtures (sample data, paths)
├── test_schemas.py         # Unit tests Pydantic schemas (fast, no I/O)
├── test_dataset_builder.py # Integration tests vs real raw data (skip if absent)
├── data/                   # Sample minimal JSONL fixtures (small, committed)
└── README.md               # This file
```

## Conventions

- **Unit tests:** schemas validation, parser logic — fast, no external dependencies
- **Integration tests:** require real scraped data w `data/raw/`, skip gracefully jeśli brak
- **Fixtures:** session-scoped dla expensive setups, function-scoped dla mutable
- **Naming:** `test_<module>.py` z `Test<ClassName>` classes

## Coverage target

`pytest --cov=src --cov-report=term-missing` — target ≥80% dla schemas, ≥60% dla scrape parsers (HTML logic ciężko testować).

## CI integration (future)

GitHub Actions workflow `.github/workflows/test.yml` w Iter. 7. Runs:
1. `ruff format --check`
2. `ruff check`
3. `pyrefly check`
4. `pytest --cov=src`

## Adding new tests

Per nowy moduł `src/{halu,probe,verifier,citation,scrape}/X.py`:
1. Dodaj `tests/test_X.py`
2. Imports: `from src.{module} import ...`
3. Fixtures: re-use lub dodaj do `conftest.py` jeśli reusable cross-test
4. Run lokalnie przed commit: `uv run pytest tests/test_X.py -v`
