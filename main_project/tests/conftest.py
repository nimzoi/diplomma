"""Pytest fixtures dla Polish CitationBench testing.

Sample data + paths dla unit/integration testów scrape pipelines + schemas.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from src.halu.schemas import ConsumerSource, HaluType, NLILabel


@pytest.fixture
def repo_root() -> Path:
    """Repo root path (D:/diplomma)."""
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def main_project_root(repo_root: Path) -> Path:
    return repo_root / "main_project"


@pytest.fixture
def raw_data_dir(main_project_root: Path) -> Path:
    return main_project_root / "data" / "raw"


@pytest.fixture
def test_data_dir() -> Path:
    """Sample data dla unit testów (NIE production data)."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_legal_chunk_dict() -> dict:
    """Valid LegalChunk record (Pydantic test fixture)."""
    return {
        "chunk_id": "eli_DU_2014_827_art_27_ust_1",
        "ustawa_id": "DU/2014/827",
        "ustawa_title": "Ustawa o prawach konsumenta",
        "ustawa_data_uchwalenia": date(2014, 5, 30),
        "art": "27",
        "paragraf": None,
        "ust": "1",
        "pkt": None,
        "lit": None,
        "tresc": (
            "Konsument, który zawarł umowę na odległość lub poza lokalem przedsiębiorstwa, "
            "może w terminie 14 dni odstąpić od niej bez podawania przyczyny."
        ),
        "citation_string": (
            "art. 27 ust. 1 Ustawy o prawach konsumenta z dnia 30 maja 2014 r. "
            "(Dz.U. 2014 poz. 827)"
        ),
        "scrape_date": date(2026, 5, 16),
        "source_url": "https://api.sejm.gov.pl/eli/acts/DU/2014/827/text.html",
        "metadata": {},
    }


@pytest.fixture
def sample_uokik_qa_dict() -> dict:
    """Valid QAGoldPair record."""
    return {
        "qa_id": "uokik_zagadnienia-ogolne_001",
        "question": "Kiedy jestem konsumentem?",
        "answer": (
            "Konsument to osoba fizyczna dokonująca z przedsiębiorcą czynności prawnej "
            "niezwiązanej bezpośrednio z jej działalnością gospodarczą lub zawodową."
        ),
        "cited_articles": ["art. 22^1 Kodeksu cywilnego"],
        "category": "Zagadnienia ogólne",
        "source_url": (
            "https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/"
            "zagadnienia-ogolne/kiedy-jestem-konsumentem/"
        ),
        "scrape_date": date(2026, 5, 16),
    }


@pytest.fixture
def sample_consumer_question_dict() -> dict:
    """Valid ConsumerQuestion record."""
    return {
        "question_id": "eprawnik_001",
        "question": (
            "Sprzedawca odmawia zwrotu produktu po 14 dniach od zakupu w sklepie internetowym. "
            "Co mogę zrobić?"
        ),
        "context": None,
        "source": ConsumerSource.E_PRAWNIK,
        "source_url": "https://e-prawnik.pl/forum/example/123",
        "category": "ochrona-konsumenta",
        "thread_responses_count": 5,
        "extracted_topics": ["zwrot", "umowa-na-odleglosc"],
        "scrape_date": date(2026, 5, 16),
    }


@pytest.fixture
def sample_halu_pair_dict(sample_legal_chunk_dict: dict) -> dict:
    """Valid HaluPair record (synthetic factual_fabrication)."""
    return {
        "pair_id": "halu_synth_001",
        "source_qa_id": "uokik_zagadnienia-ogolne_001",
        "query": "Kiedy mam prawo zwrócić produkt z e-sklepu?",
        "claim": "Konsument ma 60 dni na zwrot bez podania przyczyny.",
        "evidence_chunks": [sample_legal_chunk_dict["chunk_id"]],
        "is_hallucinated": True,
        "halu_type": HaluType.FACTUAL_FABRICATION,
        "nli_label": NLILabel.CONTRADICTED,
        "generation_method": "manual_test_fixture",
        "metadata": {"correct_value": "14 dni", "fabricated_value": "60 dni"},
    }
