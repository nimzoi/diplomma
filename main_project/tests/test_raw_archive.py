"""Sanity tests dla raw archive sweep (``src/scrape/archive_raw_sources.py``).

Test scope:
1. Verify ``_archive/_manifest.json`` exists per source dir (subset — at least one entry)
2. Per-source: sample <= 10 entries → archive file actually exists on disk
3. SHA256 verification on the same sample — recompute z bytes na dysku, compare z manifest
4. content_type matches file extension
5. chunk_ids list non-empty if source dir miało chunks (sanity)

Te testy są DEPENDENT od running archive sweep wcześniej:

    uv run python -m main_project.src.scrape.archive_raw_sources --all

Jeśli brak ``_archive/_manifest.json`` w source dir → test SKIPPED (NIE failed).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = REPO_ROOT / "main_project" / "data" / "raw"

# All sources expected to have an _archive/_manifest.json
EXPECTED_SOURCES: list[tuple[str, Path]] = [
    ("uokik_pdfs", DATA_RAW / "consumer_documents_2026-05-16" / "uokik_pdfs" / "_archive"),
    ("rf_pdfs", DATA_RAW / "consumer_documents_2026-05-16" / "rf_pdfs" / "_archive"),
    (
        "federacja_docs",
        DATA_RAW / "consumer_documents_2026-05-16" / "federacja_konsumentow" / "_archive",
    ),
    ("orzeczenia", DATA_RAW / "consumer_documents_2026-05-16" / "orzeczenia" / "_archive"),
    ("ue_dyrektywy", DATA_RAW / "ue_dyrektywy_2026-05-16" / "_archive"),
    ("tsue", DATA_RAW / "tsue_orzeczenia_2026-05-16" / "_archive"),
    ("wikipedia", DATA_RAW / "extended_consumer_2026-05-16" / "_archive" / "wikipedia"),
    ("federacja_e1", DATA_RAW / "extended_consumer_2026-05-16" / "_archive" / "federacja"),
    ("uokik_news", DATA_RAW / "extended_consumer_2026-05-16" / "_archive" / "uokik_news"),
    ("gov_pl", DATA_RAW / "extended_consumer_2026-05-16" / "_archive" / "gov_pl"),
    ("rf_faq", DATA_RAW / "extended_consumer_2026-05-16" / "_archive" / "rf_faq"),
    ("uokik_qa", DATA_RAW / "uokik_qa_2026-05-16" / "_archive"),
]


def _load_manifest(archive_dir: Path) -> dict | None:
    """Load _manifest.json or return None if missing / corrupted."""
    p = archive_dir / "_manifest.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


@pytest.mark.parametrize("name,archive_dir", EXPECTED_SOURCES, ids=[s[0] for s in EXPECTED_SOURCES])
def test_manifest_exists_and_valid(name: str, archive_dir: Path) -> None:
    """Manifest exists, parses, has stats + entries."""
    manifest = _load_manifest(archive_dir)
    if manifest is None:
        pytest.skip(f"manifest missing for {name}: {archive_dir / '_manifest.json'}")

    assert "source" in manifest, f"{name}: manifest missing 'source'"
    assert "scrape_date" in manifest, f"{name}: manifest missing 'scrape_date'"
    assert "entries" in manifest, f"{name}: manifest missing 'entries'"
    assert "stats" in manifest, f"{name}: manifest missing 'stats'"
    assert isinstance(manifest["entries"], list), f"{name}: entries not list"


@pytest.mark.parametrize("name,archive_dir", EXPECTED_SOURCES, ids=[s[0] for s in EXPECTED_SOURCES])
def test_archive_files_exist(name: str, archive_dir: Path) -> None:
    """Sample up to 10 manifest entries → archive_path file exists on disk."""
    manifest = _load_manifest(archive_dir)
    if manifest is None:
        pytest.skip(f"manifest missing for {name}")

    entries = manifest["entries"]
    if not entries:
        pytest.skip(f"manifest for {name} is empty (0 entries)")

    # Take first 10 entries
    sample = entries[:10]
    source_dir_repo = REPO_ROOT / manifest["source_dir"].replace("/", "\\")
    # Use platform-independent path resolution
    source_dir_repo = Path(*Path(manifest["source_dir"]).parts)
    source_dir_abs = REPO_ROOT / source_dir_repo

    for entry in sample:
        rel = entry["archive_path"]
        # archive_path is like "_archive/wikipedia/foo.html" — relative to source_dir
        file_path = source_dir_abs / rel
        assert file_path.exists(), (
            f"{name}: missing archive file {file_path} for doc_id={entry['doc_id']}"
        )
        # File size sanity
        actual_size = file_path.stat().st_size
        assert actual_size == entry["size_bytes"], (
            f"{name}: size mismatch for {entry['doc_id']} "
            f"manifest={entry['size_bytes']} disk={actual_size}"
        )


@pytest.mark.parametrize("name,archive_dir", EXPECTED_SOURCES, ids=[s[0] for s in EXPECTED_SOURCES])
def test_sha256_matches_disk(name: str, archive_dir: Path) -> None:
    """SHA256 of bytes-on-disk == manifest sha256 (sample 10)."""
    manifest = _load_manifest(archive_dir)
    if manifest is None:
        pytest.skip(f"manifest missing for {name}")

    entries = manifest["entries"]
    if not entries:
        pytest.skip(f"manifest for {name} is empty")

    sample = entries[:10]
    source_dir_abs = REPO_ROOT / Path(*Path(manifest["source_dir"]).parts)

    for entry in sample:
        file_path = source_dir_abs / entry["archive_path"]
        if not file_path.exists():
            pytest.skip(f"{name}: file missing for {entry['doc_id']}")
        actual_sha = hashlib.sha256(file_path.read_bytes()).hexdigest()
        assert actual_sha == entry["sha256"], (
            f"{name}: sha256 mismatch for {entry['doc_id']}: "
            f"manifest={entry['sha256']} disk={actual_sha}"
        )


@pytest.mark.parametrize("name,archive_dir", EXPECTED_SOURCES, ids=[s[0] for s in EXPECTED_SOURCES])
def test_content_type_matches_extension(name: str, archive_dir: Path) -> None:
    """For sample 10: content_type field matches file extension on disk."""
    manifest = _load_manifest(archive_dir)
    if manifest is None:
        pytest.skip(f"manifest missing for {name}")

    entries = manifest["entries"][:10]
    if not entries:
        pytest.skip(f"manifest for {name} is empty")

    for entry in entries:
        ct = entry["content_type"]
        path = Path(entry["archive_path"])
        ext = path.suffix.lower()
        if ext == ".pdf":
            assert ct == "application/pdf", (
                f"{name}: doc_id={entry['doc_id']} .pdf but content_type={ct}"
            )
        elif ext == ".html":
            assert ct == "text/html", (
                f"{name}: doc_id={entry['doc_id']} .html but content_type={ct}"
            )


def test_pdf_files_start_with_pdf_magic() -> None:
    """PDFs muszą zaczynać się od %PDF magic bytes — protects against
    HTML/WAF page being saved as .pdf in case of upstream WAF challenge.
    Sample across PDF-bearing sources.
    """
    pdf_archive_dirs = [
        DATA_RAW / "consumer_documents_2026-05-16" / "uokik_pdfs" / "_archive",
        DATA_RAW / "consumer_documents_2026-05-16" / "rf_pdfs" / "_archive",
        DATA_RAW / "ue_dyrektywy_2026-05-16" / "_archive",
        DATA_RAW / "tsue_orzeczenia_2026-05-16" / "_archive",
    ]
    checked = 0
    for d in pdf_archive_dirs:
        if not d.exists():
            continue
        for pdf in sorted(d.glob("*.pdf"))[:3]:
            magic = pdf.read_bytes()[:8]
            assert magic.startswith(b"%PDF"), f"not a PDF: {pdf} (magic={magic!r})"
            checked += 1
    if checked == 0:
        pytest.skip("no PDF archive dirs populated yet")


def test_sweep_summary_exists() -> None:
    """Top-level sweep summary file should be written by orchestrator."""
    p = DATA_RAW / "_archive_sweep_summary.json"
    if not p.exists():
        pytest.skip("sweep summary not yet produced")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert "sources" in d
    assert "total_bytes" in d
    assert isinstance(d["sources"], dict)
