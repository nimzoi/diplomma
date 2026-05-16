"""Combine raw scrape data → processed Polish CitationBench dataset.

Czyta JSONL z ``data/raw/{eli, uokik, consumer_questions}/`` i emituje
``data/processed/citationbench_v0.X_{date}.jsonl`` z combined records po
Pydantic validation.

CLI:
    uv run python -m src.halu.dataset_builder \\
        --raw-dir data/raw \\
        --output-dir data/processed \\
        --version v0.1
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.halu.schemas import ConsumerQuestion, ConsumerSource, LegalChunk, QAGoldPair

logger = logging.getLogger(__name__)


def _parse_date(value: Any) -> date:
    """Parse date z ISO string lub date object."""
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value[:10]).date()
    raise ValueError(f"Cannot parse date from {value!r}")


def load_eli_chunks(raw_dir: Path) -> list[LegalChunk]:
    """Wczytaj wszystkie ELI ustaw chunks z ``data/raw/eli_ustawy_konsumenckie_*/``."""
    chunks: list[LegalChunk] = []
    for jsonl_path in sorted(raw_dir.glob("eli_ustawy_konsumenckie_*/*.jsonl")):
        with jsonl_path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    record["scrape_date"] = _parse_date(record.get("scrape_date"))
                    if "ustawa_data_uchwalenia" in record.get("metadata", {}):
                        record["ustawa_data_uchwalenia"] = _parse_date(
                            record["metadata"]["ustawa_data_uchwalenia"]
                        )
                    chunks.append(LegalChunk.model_validate(record))
                except (ValidationError, ValueError, json.JSONDecodeError) as exc:
                    logger.warning("ELI %s:%d skipped: %s", jsonl_path.name, lineno, exc)
    logger.info("Loaded %d ELI chunks z %s", len(chunks), raw_dir)
    return chunks


def load_uokik_gold(raw_dir: Path) -> list[QAGoldPair]:
    """Wczytaj UOKiK Q&A gold pairs z ``data/raw/uokik_qa_*/uokik_qa.jsonl``."""
    pairs: list[QAGoldPair] = []
    for jsonl_path in sorted(raw_dir.glob("uokik_qa_*/uokik_qa.jsonl")):
        with jsonl_path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    record["scrape_date"] = _parse_date(record.get("scrape_date"))
                    pairs.append(QAGoldPair.model_validate(record))
                except (ValidationError, ValueError, json.JSONDecodeError) as exc:
                    logger.warning("UOKiK %s:%d skipped: %s", jsonl_path.name, lineno, exc)
    logger.info("Loaded %d UOKiK gold pairs", len(pairs))
    return pairs


def load_consumer_questions(raw_dir: Path) -> list[ConsumerQuestion]:
    """Wczytaj real consumer questions z 4 sources."""
    questions: list[ConsumerQuestion] = []
    source_files = {
        "e_prawnik_consumer.jsonl": ConsumerSource.E_PRAWNIK,
        "forumprawne_consumer.jsonl": ConsumerSource.FORUMPRAWNE,
        "legal_other_polish.jsonl": ConsumerSource.EPORADY24,
        "reddit_polska_consumer.jsonl": None,  # Source z record (multiple subreddits)
    }
    for jsonl_path in sorted(raw_dir.glob("consumer_questions_polish_*/*.jsonl")):
        default_source = source_files.get(jsonl_path.name)
        with jsonl_path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    record["scrape_date"] = _parse_date(record.get("scrape_date"))
                    if default_source is not None and "source" not in record:
                        record["source"] = default_source.value
                    questions.append(ConsumerQuestion.model_validate(record))
                except (ValidationError, ValueError, json.JSONDecodeError) as exc:
                    logger.warning("Consumer %s:%d skipped: %s", jsonl_path.name, lineno, exc)
    logger.info("Loaded %d consumer questions", len(questions))
    return questions


def write_jsonl(records: list[Any], path: Path) -> None:
    """Serialize Pydantic records → JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(record.model_dump_json() + "\n")
    logger.info("Wrote %d records → %s", len(records), path)


def write_dataset_card(
    output_dir: Path, version: str, snapshot_date: str, stats: dict[str, int]
) -> None:
    """Generate HuggingFace dataset card stub."""
    card = f"""---
language:
- pl
license: cc-by-nc-sa-4.0  # TBD final license review
task_categories:
- question-answering
- text-classification
tags:
- polish
- consumer-rights
- hallucination-detection
- citation-grounding
- legal-nlp
size_categories:
- 1K<n<10K
---

# Polish CitationBench (v{version})

**Snapshot date:** {snapshot_date}
**Domena:** polskie prawa konsumenta
**Use case:** citation-grounded RAG hallucination detection

## Stats

| Component | Records |
|---|---|
| ELI ustawy chunks | {stats["legal_chunks"]} |
| UOKiK gold Q&A pairs | {stats["uokik_gold"]} |
| Real consumer questions | {stats["consumer_questions"]} |
| Synthetic halu pairs | TBD post-Iter. 1 |
| Manual gold (autorka) | TBD post-Iter. 1 |

## Citation

```bibtex
@misc{{sochacka2026citationbench,
  title = {{Polish CitationBench: citation-grounded RAG halu detection benchmark}},
  author = {{Sochacka, Magdalena}},
  year = {{2026}},
  howpublished = {{HuggingFace Datasets}},
  note = {{Praca inżynierska, PJATK}}
}}
```

## Sources + License

- **ISAP/ELI:** Polish public domain (Art. 4 PrAut + TDM exception 2024)
- **UOKiK Q&A:** urzędowe materiały (Art. 4 PrAut)
- **e-prawnik / forumprawne:** krótki cytat (Art. 29 PrAut)
- **Reddit:** academic use, sha1:10 hashed usernames
- **eporady24:** ⚠ paid license — meta description only, local-only redistribution

## Schema

Patrz `src/halu/schemas.py` (Pydantic v2):
- `LegalChunk` (ELI)
- `QAGoldPair` (UOKiK)
- `ConsumerQuestion` (fora/Reddit)
- `HaluPair` (synthetic)
- `EvalSample` (combined eval)
"""
    (output_dir / "DATASET_CARD.md").write_text(card, encoding="utf-8")
    logger.info("Wrote dataset card → %s/DATASET_CARD.md", output_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--version", type=str, default="v0.1")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    today = date.today().isoformat()
    output_subdir = args.output_dir / f"citationbench_{args.version}_{today}"
    output_subdir.mkdir(parents=True, exist_ok=True)

    legal_chunks = load_eli_chunks(args.raw_dir)
    uokik_gold = load_uokik_gold(args.raw_dir)
    consumer_questions = load_consumer_questions(args.raw_dir)

    write_jsonl(legal_chunks, output_subdir / "legal_chunks.jsonl")
    write_jsonl(uokik_gold, output_subdir / "uokik_gold.jsonl")
    write_jsonl(consumer_questions, output_subdir / "consumer_questions.jsonl")

    stats = {
        "legal_chunks": len(legal_chunks),
        "uokik_gold": len(uokik_gold),
        "consumer_questions": len(consumer_questions),
    }
    write_dataset_card(output_subdir, args.version, today, stats)

    print(f"\n=== Polish CitationBench {args.version} build summary ===")
    print(f"Output: {output_subdir}")
    for component, count in stats.items():
        print(f"  {component}: {count}")
    print(f"\nTotal: {sum(stats.values())} records")
    print(f"Dataset card: {output_subdir / 'DATASET_CARD.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
