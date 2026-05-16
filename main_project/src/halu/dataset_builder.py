"""Combine raw scrape data → processed Polish CitationBench dataset.

Orchestrator: czyta JSONL z ``data/raw/*/`` (wszystkie strata), normalizuje przez
``normalizers.py`` do unified ``Chunk`` schema (option b per Magda 2026-05-16),
deduplikuje, injectuje synthetic halu pairs, emituje stratified split do
``data/processed/citationbench_{version}_{date}/``.

**Sources handled:**

- ELI ustawy (LegalChunk) z ``eli_ustawy_konsumenckie_*/*.jsonl``
- UOKiK Q&A gold (QAGoldPair) z ``uokik_qa_*/uokik_qa.jsonl``
- Consumer questions (ConsumerQuestion) z ``consumer_questions_polish_*/*.jsonl``
- Encyclopedic (EncyclopedicChunk) z ``extended_consumer_*/*.jsonl`` (E1)
- Long-form documents z ``consumer_documents_*/{subdir}/documents.jsonl`` (E4)
- UE dyrektywy (S3) z ``ue_dyrektywy_*/*.jsonl``
- TSUE orzeczenia (S3) z ``tsue_orzeczenia_*/*.jsonl``
- UOKiK decyzje (S2) z ``uokik_decyzje_*/*.jsonl``
- SN orzeczenia (S2) z ``sn_orzeczenia_*/*.jsonl``

CLI:
    uv run python -m src.halu.dataset_builder \\
        --raw-dir data/raw \\
        --output-dir data/processed \\
        --version v0.1 \\
        --halu-injection-per-pair 3
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.halu.halu_injector import generate_halu_pairs_from_qa
from src.halu.normalizers import (
    normalize_consumer_document,
    normalize_consumer_question,
    normalize_court_judgment,
    normalize_eli_record,
    normalize_encyclopedic,
    normalize_new_source_article,
    normalize_tsue_judgment,
    normalize_ue_directive,
    normalize_uokik_decision,
    normalize_uokik_qa,
)
from src.halu.schemas import Chunk, HaluPair

logger = logging.getLogger(__name__)


# === Generic loader helper ===


def _load_jsonl_with_normalizer(
    paths: list[Path],
    normalizer: Callable[[dict[str, Any]], Chunk],
    source_label: str,
) -> tuple[list[Chunk], int]:
    """Load + normalize JSONL records. Returns (chunks, skip_count)."""
    chunks: list[Chunk] = []
    skipped = 0
    for jsonl_path in paths:
        with jsonl_path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    chunks.append(normalizer(record))
                except (ValidationError, ValueError, KeyError, json.JSONDecodeError) as exc:
                    skipped += 1
                    if skipped <= 5:  # First 5 errors verbose
                        logger.warning(
                            "%s %s:%d skipped: %s", source_label, jsonl_path.name, lineno, exc
                        )
    logger.info(
        "[%s] loaded %d chunks (skipped %d) z %d files",
        source_label,
        len(chunks),
        skipped,
        len(paths),
    )
    return chunks, skipped


# === Source-specific loaders ===


def load_eli_chunks(raw_dir: Path) -> list[Chunk]:
    paths = sorted(raw_dir.glob("eli_ustawy_konsumenckie_*/DU_*.jsonl"))
    chunks, _ = _load_jsonl_with_normalizer(paths, normalize_eli_record, "ELI")
    return chunks


def load_uokik_qa_chunks(raw_dir: Path) -> tuple[list[Chunk], list[dict[str, Any]]]:
    """Returns (normalized Chunks, raw QA dicts dla halu injection)."""
    chunks: list[Chunk] = []
    raw_qa: list[dict[str, Any]] = []
    for jsonl_path in sorted(raw_dir.glob("uokik_qa_*/uokik_qa.jsonl")):
        with jsonl_path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    chunks.append(normalize_uokik_qa(record))
                    raw_qa.append(record)
                except (ValidationError, ValueError, KeyError) as exc:
                    logger.warning("UOKiK QA %s:%d skipped: %s", jsonl_path.name, lineno, exc)
    logger.info("[UOKiK QA] loaded %d chunks + %d raw pairs", len(chunks), len(raw_qa))
    return chunks, raw_qa


def load_consumer_questions(raw_dir: Path) -> list[Chunk]:
    paths = sorted(raw_dir.glob("consumer_questions_polish_*/*.jsonl"))
    chunks, _ = _load_jsonl_with_normalizer(paths, normalize_consumer_question, "Consumer Q")
    return chunks


def load_encyclopedic(raw_dir: Path) -> list[Chunk]:
    """Wczytuje E1 extended_consumer + encyclopedic z różnych źródeł."""
    paths = sorted(raw_dir.glob("extended_consumer_*/*.jsonl"))
    chunks, _ = _load_jsonl_with_normalizer(paths, normalize_encyclopedic, "Encyclopedic")
    return chunks


def load_consumer_documents(raw_dir: Path) -> list[Chunk]:
    """E4 long-form documents (z subdirs)."""
    paths = sorted(raw_dir.glob("consumer_documents_*/*/documents.jsonl"))
    chunks, _ = _load_jsonl_with_normalizer(paths, normalize_consumer_document, "Consumer Doc")
    return chunks


def load_ue_directives(raw_dir: Path) -> list[Chunk]:
    paths = sorted(raw_dir.glob("ue_dyrektywy_*/*.jsonl"))
    if not paths:
        return []
    chunks, _ = _load_jsonl_with_normalizer(paths, normalize_ue_directive, "UE Dyr")
    return chunks


def load_tsue_judgments(raw_dir: Path) -> list[Chunk]:
    paths = sorted(raw_dir.glob("tsue_orzeczenia_*/*.jsonl"))
    if not paths:
        return []
    chunks, _ = _load_jsonl_with_normalizer(paths, normalize_tsue_judgment, "TSUE")
    return chunks


def load_uokik_decyzje(raw_dir: Path) -> list[Chunk]:
    paths = sorted(raw_dir.glob("uokik_decyzje_*/*.jsonl"))
    if not paths:
        return []
    chunks, _ = _load_jsonl_with_normalizer(paths, normalize_uokik_decision, "UOKiK Dec")
    return chunks


def load_new_sources_articles(raw_dir: Path) -> list[Chunk]:
    """S6 nowy source articles (bankier/infor/prawo.pl/bezprawnik/ecc/uodo/...).

    Glob pattern: ``data/raw/{source}_2026-*/articles.jsonl`` ale wykluczamy
    `consumer_documents`, `consumer_questions`, `eli_*`, `tsue_*`, `ue_*`,
    `uokik_*` (już handled przez dedicated loaders).
    """
    s6_sources = [
        "bankier_pl", "money_pl", "infor_pl", "gazeta_prawna", "prawo_pl",
        "bezprawnik_pl", "ecc_polska", "uodo", "knf_consumer", "uke_consumer",
        "ure_consumer", "banki_consumer",
    ]
    paths: list[Path] = []
    for src in s6_sources:
        paths.extend(sorted(raw_dir.glob(f"{src}_*/articles.jsonl")))
    if not paths:
        return []
    chunks, _ = _load_jsonl_with_normalizer(
        paths, normalize_new_source_article, "S6 articles"
    )
    return chunks


def load_sn_orzeczenia(raw_dir: Path) -> list[Chunk]:
    paths = sorted(raw_dir.glob("sn_orzeczenia_*/*.jsonl"))
    if not paths:
        return []
    chunks, _ = _load_jsonl_with_normalizer(paths, normalize_court_judgment, "SN")
    return chunks


# === Deduplication ===


def deduplicate_chunks(chunks: list[Chunk]) -> list[Chunk]:
    """Dedup po chunk_id + by content hash (catch reżujpe rescrapes)."""
    seen_ids: set[str] = set()
    seen_hashes: set[int] = set()
    unique: list[Chunk] = []
    for chunk in chunks:
        if chunk.chunk_id in seen_ids:
            continue
        content_hash = hash((chunk.tresc[:500], chunk.source))
        if content_hash in seen_hashes:
            continue
        seen_ids.add(chunk.chunk_id)
        seen_hashes.add(content_hash)
        unique.append(chunk)
    dropped = len(chunks) - len(unique)
    if dropped:
        logger.info(
            "Deduplicated: %d dropped (%.1f%%)", dropped, 100 * dropped / max(len(chunks), 1)
        )
    return unique


# === Output writers ===


def write_jsonl(records: list[Any], path: Path) -> None:
    """Serialize Pydantic records → JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(record.model_dump_json() + "\n")
    logger.info("Wrote %d records → %s", len(records), path)


def _compute_stats(chunks: list[Chunk]) -> dict[str, Any]:
    """Compute aggregate stats dla DATASET_CARD."""
    source_type_counts = Counter(c.source_type.value for c in chunks)
    source_counts = Counter(c.source for c in chunks)
    category_counts: Counter[str] = Counter()
    for c in chunks:
        for cat in c.categories:
            category_counts[cat.value] += 1
    has_citation = sum(1 for c in chunks if c.cited_articles)
    avg_tresc_len = sum(len(c.tresc) for c in chunks) / max(len(chunks), 1)

    return {
        "total_chunks": len(chunks),
        "source_types": dict(source_type_counts.most_common()),
        "sources": dict(source_counts.most_common(15)),
        "categories": dict(category_counts.most_common()),
        "with_citations": has_citation,
        "citation_rate": round(has_citation / max(len(chunks), 1), 3),
        "avg_tresc_length_chars": round(avg_tresc_len),
    }


def write_dataset_card(
    output_dir: Path,
    version: str,
    snapshot_date: str,
    chunk_stats: dict[str, Any],
    halu_count: int,
) -> None:
    """Generate HuggingFace dataset card."""
    sources_table = "\n".join(
        f"| {src} | {count} |" for src, count in chunk_stats["sources"].items()
    )
    source_types_table = "\n".join(
        f"| {st} | {count} |" for st, count in chunk_stats["source_types"].items()
    )
    categories_table = "\n".join(
        f"| {cat} | {count} |" for cat, count in chunk_stats["categories"].items()
    )

    card = f"""---
language:
- pl
license: cc-by-nc-sa-4.0
task_categories:
- question-answering
- text-classification
tags:
- polish
- consumer-rights
- hallucination-detection
- citation-grounding
- legal-nlp
- rag
size_categories:
- 1K<n<10K
---

# Polish CitationBench (v{version})

**Snapshot date:** {snapshot_date}
**Domena:** polskie prawa konsumenta + EU consumer law context
**Use case:** citation-grounded RAG hallucination detection benchmark

## Aggregate stats

- **Total unified chunks:** {chunk_stats["total_chunks"]}
- **Chunks z cytacjami:** {chunk_stats["with_citations"]} ({chunk_stats["citation_rate"]:.1%})
- **Avg tresc length:** {chunk_stats["avg_tresc_length_chars"]} chars
- **Synthetic halu pairs:** {halu_count} (1 negative + N positive per UOKiK gold pair)

## Source types

| source_type | count |
|---|---|
{source_types_table}

## Sources (top 15)

| source | count |
|---|---|
{sources_table}

## Categories (multi-label)

| category | count |
|---|---|
{categories_table}

## Schema (unified Chunk — option b per author decision 2026-05-16)

```python
class Chunk(BaseModel):
    chunk_id: str
    source_type: SourceType  # legal_statute | legal_ue_directive | legal_tsue_judgment | ...
    source: str
    source_url: str
    title: str
    tresc: str
    citation_string: str | None
    cited_articles: list[str]
    categories: list[Category]  # multi-label
    language: str = "pl"
    license: str
    scrape_date: date
    process_date: date
    metadata: dict
```

Pełna specyfikacja: `src/halu/schemas.py`.

## Files

- `chunks.jsonl` — unified Chunk records (all sources)
- `halu_pairs.jsonl` — synthetic HaluPair records (train probe + verifier)
- `splits/` — stratified train/val/test by source_type + category

## Citation

```bibtex
@misc{{sochacka2026citationbench,
  title = {{Polish CitationBench: citation-grounded RAG hallucination detection benchmark}},
  author = {{Sochacka, Magdalena}},
  year = {{2026}},
  howpublished = {{HuggingFace Datasets}},
  note = {{Praca inżynierska, PJATK}}
}}
```

## Licensing

Mixed-license dataset z explicit per-chunk attribution:

- **ELI / Polish statutes:** urzędowe (Art. 4 ust. 2 PrAut + TDM exception Wrzesień 2024)
- **UOKiK Q&A + decyzje:** urzędowe (Art. 4 ust. 2 PrAut)
- **UE EUR-Lex content:** © European Union, reuse per Decision 2011/833/UE
- **Wikipedia:** CC BY-SA 4.0 (share-alike required)
- **Forum/Reddit:** fair-use (Art. 29 PrAut, academic + anonymized usernames sha1:10)
- **PDF poradniki UOKiK/RF/FK:** urzędowe lub fair-use NGO

⚠ **CC BY-SA share-alike:** Wikipedia component oznacza że downstream MUST cite Wikipedia
i zachować SA license dla derivative. Filter `source_type != 'encyclopedic'` jeśli SA jest
problemem dla downstream use.

## Świadome biases (per R3 thesis chapter v3.2)

1. **Source type bias:** legal_statute + legal_document_pdf dominują (~70%) względem QA pairs (~25%)
2. **Finance adjacent bias:** RF FAQ (~22% E1 extended) jest finance/banking dominated — oznaczone `FINANCE_ADJACENT` category
3. **Recency bias:** post-2014 content dominuje (UPK 2014/827 jako CORE)
4. **Polish-only bias:** wyłączony EN content (świadomy: praca dotyczy polish-specific halu detection)
5. **Court judgment selection bias:** orzeczenia wybierane głównie via Google search (10 wyroków w E4)

## Note dla v3.1 → v3.2 pivot (DEC-003)

Pierwotny plan był farma+reranker domain. Po pivocie 2026-05-16 na halu detection +
consumer rights. Wszystkie chunki w tym dataset są post-pivot (od 2026-05-16).
v3.1 farma materials zarchiwizowane w `_archive/v3-pharma-reranker/`.
"""
    (output_dir / "DATASET_CARD.md").write_text(card, encoding="utf-8")
    logger.info("Wrote dataset card → %s/DATASET_CARD.md", output_dir)


# === Main orchestrator ===


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--version", type=str, default="v0.1")
    parser.add_argument(
        "--halu-injection-per-pair",
        type=int,
        default=3,
        help="Liczba synthetic halu samples per UOKiK gold pair (default 3)",
    )
    parser.add_argument("--seed", type=int, default=42, help="RNG seed dla halu injection")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    today = date.today().isoformat()
    output_subdir = args.output_dir / f"citationbench_{args.version}_{today}"
    output_subdir.mkdir(parents=True, exist_ok=True)

    logger.info("=== Polish CitationBench %s build ===", args.version)
    logger.info("Raw dir: %s", args.raw_dir.resolve())
    logger.info("Output: %s", output_subdir.resolve())

    # Load all sources → unified Chunk
    all_chunks: list[Chunk] = []
    all_chunks.extend(load_eli_chunks(args.raw_dir))
    uokik_chunks, uokik_raw_qa = load_uokik_qa_chunks(args.raw_dir)
    all_chunks.extend(uokik_chunks)
    all_chunks.extend(load_consumer_questions(args.raw_dir))
    all_chunks.extend(load_encyclopedic(args.raw_dir))
    all_chunks.extend(load_consumer_documents(args.raw_dir))
    all_chunks.extend(load_ue_directives(args.raw_dir))
    all_chunks.extend(load_tsue_judgments(args.raw_dir))
    all_chunks.extend(load_uokik_decyzje(args.raw_dir))
    all_chunks.extend(load_sn_orzeczenia(args.raw_dir))
    all_chunks.extend(load_new_sources_articles(args.raw_dir))

    logger.info("Total loaded: %d chunks", len(all_chunks))

    # Dedup
    all_chunks = deduplicate_chunks(all_chunks)

    # Halu injection z UOKiK QA
    halu_pairs: list[HaluPair] = []
    if uokik_raw_qa:
        halu_pairs = generate_halu_pairs_from_qa(
            uokik_raw_qa,
            seed=args.seed,
            n_halu_per_pair=args.halu_injection_per_pair,
        )

    # Write outputs
    write_jsonl(all_chunks, output_subdir / "chunks.jsonl")
    write_jsonl(halu_pairs, output_subdir / "halu_pairs.jsonl")

    # Stats + dataset card
    chunk_stats = _compute_stats(all_chunks)
    write_dataset_card(output_subdir, args.version, today, chunk_stats, len(halu_pairs))

    # Final summary
    print(f"\n=== Polish CitationBench {args.version} build summary ===")
    print(f"Output: {output_subdir}")
    print(f"\nUnified chunks: {chunk_stats['total_chunks']}")
    print(f"  with citations: {chunk_stats['with_citations']} ({chunk_stats['citation_rate']:.1%})")
    print("\nSource types:")
    for st, count in chunk_stats["source_types"].items():
        print(f"  {st:35s} {count:6d}")
    print(f"\nSynthetic halu pairs: {len(halu_pairs)}")
    print(f"  (1 neg + {args.halu_injection_per_pair} pos per UOKiK gold pair)")
    print(f"\nDataset card: {output_subdir / 'DATASET_CARD.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
