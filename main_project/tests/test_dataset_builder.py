"""Integration tests dla dataset_builder z real raw data (jeśli dostępne)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.halu.dataset_builder import (
    load_consumer_questions,
    load_eli_chunks,
    load_uokik_gold,
)


@pytest.fixture
def has_raw_data(raw_data_dir: Path) -> bool:
    """Skip integration testów jeśli brak raw data (np. fresh checkout bez scrape)."""
    return any(raw_data_dir.glob("uokik_qa_*/uokik_qa.jsonl"))


class TestUokikLoading:
    def test_loads_real_uokik_pairs(
        self, raw_data_dir: Path, has_raw_data: bool
    ) -> None:
        if not has_raw_data:
            pytest.skip("Raw UOKiK data not present (run scrape first)")
        pairs = load_uokik_gold(raw_data_dir)
        assert len(pairs) >= 50, f"Expected ≥50 UOKiK pairs, got {len(pairs)}"
        # 92% should have citations per scrape report
        with_citations = sum(1 for p in pairs if p.cited_articles)
        ratio = with_citations / len(pairs)
        assert ratio >= 0.85, f"Citation rate {ratio:.1%} < 85% threshold"


class TestEliLoading:
    def test_loads_real_eli_chunks(
        self, raw_data_dir: Path, has_raw_data: bool
    ) -> None:
        if not has_raw_data:
            pytest.skip("Raw ELI data not present")
        if not any(raw_data_dir.glob("eli_ustawy_konsumenckie_*")):
            pytest.skip("ELI scrape not present")
        chunks = load_eli_chunks(raw_data_dir)
        assert len(chunks) >= 1000, f"Expected ≥1000 ELI chunks, got {len(chunks)}"
        # Sample chunk validation
        first = chunks[0]
        assert first.tresc, "Empty tresc"
        assert "art." in first.citation_string.lower()


class TestConsumerQuestionsLoading:
    def test_loads_real_consumer_questions(
        self, raw_data_dir: Path, has_raw_data: bool
    ) -> None:
        if not has_raw_data:
            pytest.skip("Raw consumer questions not present")
        if not any(raw_data_dir.glob("consumer_questions_polish_*")):
            pytest.skip("Consumer questions scrape not present")
        questions = load_consumer_questions(raw_data_dir)
        assert len(questions) >= 1000, f"Expected ≥1000 consumer questions, got {len(questions)}"


class TestSampleJsonlIntegrity:
    """Sanity checks na sample JSONL records — every record must be valid JSON."""

    def test_uokik_jsonl_is_valid_json(
        self, raw_data_dir: Path, has_raw_data: bool
    ) -> None:
        if not has_raw_data:
            pytest.skip("Raw data not present")
        for path in raw_data_dir.glob("uokik_qa_*/uokik_qa.jsonl"):
            with path.open(encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as exc:
                        pytest.fail(f"{path.name}:{lineno} invalid JSON: {exc}")
