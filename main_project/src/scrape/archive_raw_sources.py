"""Comprehensive raw source archive sweep.

Pobiera oryginalne PDF / HTML dla wszystkich źródeł korpusu które miały tylko
extracted text + metadata (post-scrape) — żeby na dysku znalazło się też raw
source jako evidence + reproducibility hook.

Workflow per source:
1. Czytaj per-source manifest (``documents.jsonl`` lub ``*.jsonl``)
2. Resolve target URL + naming convention
3. Download (idempotent — skip jeśli `_archive/<file>` istnieje)
4. Zapisz SHA256, content_type, size_bytes do ``_archive/_manifest.json``
5. Per source: rate limit, WAF bypass (per_request_session=True dla rf.gov.pl)

Output topology (per source dir w ``main_project/data/raw/``):

    <source_dir>/_archive/
        <doc_id>.{pdf,html}
        _manifest.json

Skip ELI — already complete w ``data/raw/eli_pdf_2026-05-16/`` (20 PDFów).

Komenda::

    uv run python -m main_project.src.scrape.archive_raw_sources --all
    uv run python -m main_project.src.scrape.archive_raw_sources --source priority1
    uv run python -m main_project.src.scrape.archive_raw_sources --source uokik_pdfs

License attribution stays in ``_manifest.json["license"]`` per record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

# === Constants ===

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_RAW = REPO_ROOT / "main_project" / "data" / "raw"
TODAY = datetime.now().strftime("%Y-%m-%d")

USER_AGENT_BASE = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36 "
    "(PJATK thesis citation-grounded polish RAG - consumer-rights-academic-research@pjwstk.edu.pl)"
)
REQUEST_TIMEOUT_SEC = 30.0


# === HTTP client (mirror extended/common.Fetcher) ===


class ArchiveFetcher:
    """Politely-rate-limited HTTP client z retries + WAF challenge detection.

    ``per_request_session=True`` używa fresh ``requests.Session`` na każdy
    request — workaround dla Incapsula/WAF deployments które flagują session
    reuse jako bot (rf.gov.pl).
    """

    def __init__(
        self,
        rate_limit_sec: float = 1.0,
        per_request_session: bool = False,
    ) -> None:
        self.rate_limit_sec = rate_limit_sec
        self.per_request_session = per_request_session
        self._last_fetch = 0.0
        self._default_headers = {
            "User-Agent": USER_AGENT_BASE,
            "Accept-Language": "pl,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",  # noqa: E501
            "Accept-Encoding": "gzip, deflate, br",
        }
        if not per_request_session:
            self._session = requests.Session()
            self._session.headers.update(self._default_headers)

    def _make_session(self) -> requests.Session:
        if self.per_request_session:
            s = requests.Session()
            s.headers.update(self._default_headers)
            return s
        return self._session

    def get(self, url: str, *, retries: int = 3) -> requests.Response | None:
        """Politely GET url. Returns ``None`` on persistent failure."""
        wait = self.rate_limit_sec - (time.monotonic() - self._last_fetch)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(retries + 1):
            try:
                resp = self._make_session().get(
                    url,
                    timeout=REQUEST_TIMEOUT_SEC,
                    allow_redirects=True,
                )
                self._last_fetch = time.monotonic()
                if resp.status_code == 200:
                    # WAF Incapsula challenge (tiny body z _Incapsula_Resource)
                    if len(resp.content) < 2048 and b"_Incapsula_Resource" in resp.content:
                        logger.warning(
                            "GET %s -> WAF challenge (Incapsula) attempt %d/%d",
                            url,
                            attempt + 1,
                            retries + 1,
                        )
                        time.sleep(3.0 * (attempt + 1))
                        continue
                    # ms.gov.pl rate-limit response: "Połączenie odrzucone" mini-page
                    if len(resp.content) < 1024 and (
                        b"Po\xc5\x82\xc4\x85czenie odrzucone" in resp.content
                        or b"Po\xc5\x82\xc4\x85czenie do" in resp.content
                        or b"connection refused" in resp.content.lower()
                    ):
                        logger.warning(
                            "GET %s -> rate-limit reject (ms.gov.pl) attempt %d/%d",
                            url,
                            attempt + 1,
                            retries + 1,
                        )
                        time.sleep(8.0 * (attempt + 1))
                        continue
                    return resp
                if resp.status_code in (429, 503):
                    logger.warning(
                        "GET %s -> HTTP %d (backoff) attempt %d",
                        url,
                        resp.status_code,
                        attempt + 1,
                    )
                    time.sleep(4.0 * (attempt + 1))
                    continue
                if resp.status_code == 404:
                    logger.error("GET %s -> HTTP 404 (no retry)", url)
                    return resp  # surface 404 to caller
                logger.warning(
                    "GET %s -> HTTP %d (attempt %d)",
                    url,
                    resp.status_code,
                    attempt + 1,
                )
            except requests.RequestException as exc:
                logger.warning("GET %s ERR %s (attempt %d)", url, exc, attempt + 1)
            time.sleep(2.0 * (attempt + 1))
        return None


# === Manifest ===


@dataclass
class ManifestEntry:
    """Single entry — mapping chunk_id|doc_id → archive file on disk."""

    doc_id: str
    source_url: str
    archive_path: str  # relative to source_dir
    content_type: str  # "application/pdf" | "text/html"
    size_bytes: int
    sha256: str
    download_date: str = TODAY
    chunk_ids: list[str] = field(default_factory=list)
    license: str | None = None
    http_status: int = 200
    error_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        d = {
            "doc_id": self.doc_id,
            "source_url": self.source_url,
            "archive_path": self.archive_path,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "download_date": self.download_date,
            "chunk_ids": self.chunk_ids,
            "license": self.license,
            "http_status": self.http_status,
        }
        if self.error_reason:
            d["error_reason"] = self.error_reason
        return d


@dataclass
class ArchiveManifest:
    """Per source-dir manifest aggregator."""

    source: str
    source_dir: str  # relative repo path
    scrape_date: str = TODAY
    entries: list[ManifestEntry] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)

    def add(self, entry: ManifestEntry) -> None:
        self.entries.append(entry)

    def add_error(self, doc_id: str, source_url: str, reason: str) -> None:
        self.errors.append({"doc_id": doc_id, "source_url": source_url, "reason": reason})

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        d = {
            "source": self.source,
            "source_dir": self.source_dir,
            "scrape_date": self.scrape_date,
            "stats": {
                "total_entries": len(self.entries),
                "total_errors": len(self.errors),
                "total_bytes": sum(e.size_bytes for e in self.entries),
                **self.stats,
            },
            "entries": [e.as_dict() for e in self.entries],
            "errors": self.errors,
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        logger.info(
            "manifest -> %s (%d entries, %d errors)", path, len(self.entries), len(self.errors)
        )


# === Helpers ===


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def slugify_for_filename(text: str, *, max_len: int = 120) -> str:
    """Filename-safe slug — alphanumerics + dashes only."""
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", text)
    s = re.sub(r"_+", "_", s).strip("_-")
    return s[:max_len] if s else "unnamed"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_existing_manifest(path: Path) -> dict[str, ManifestEntry]:
    """Load existing manifest entries keyed by doc_id for idempotent re-runs.

    Tolerant of:
    - missing file → {}
    - corrupted JSON → {}
    - foreign manifest schema (e.g. from another scraper) → {}
    """
    if not path.exists():
        return {}
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    out: dict[str, ManifestEntry] = {}
    entries = d.get("entries")
    if not isinstance(entries, list):
        return {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        if "error_reason" in e:
            continue  # don't trust errors — re-attempt
        # Require minimum schema fields
        if not all(
            k in e for k in ("doc_id", "source_url", "archive_path", "sha256", "size_bytes")
        ):
            return {}  # foreign manifest schema — treat as missing
        out[e["doc_id"]] = ManifestEntry(
            doc_id=e["doc_id"],
            source_url=e["source_url"],
            archive_path=e["archive_path"],
            content_type=e.get("content_type", "text/html"),
            size_bytes=e["size_bytes"],
            sha256=e["sha256"],
            download_date=e.get("download_date", TODAY),
            chunk_ids=e.get("chunk_ids", []),
            license=e.get("license"),
            http_status=e.get("http_status", 200),
        )
    return out


def detect_content_type(resp: requests.Response, fallback: str) -> str:
    """Detect content-type, normalize, fallback if missing."""
    ct = resp.headers.get("Content-Type", "").lower().split(";")[0].strip()
    if "pdf" in ct:
        return "application/pdf"
    if "html" in ct or "xml" in ct:
        return "text/html"
    return fallback


def write_binary(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


# === Source download functions ===


def archive_uokik_pdfs(*, dry_run: bool = False) -> ArchiveManifest:
    """8 UOKiK poradniki PDF — z documents.jsonl + per-doc meta.json."""
    source_dir = DATA_RAW / "consumer_documents_2026-05-16" / "uokik_pdfs"
    archive_dir = source_dir / "_archive"
    manifest_path = archive_dir / "_manifest.json"
    manifest = ArchiveManifest(
        source="uokik.gov.pl/Download", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )

    # Map document_id -> chunk_ids
    chunk_map: dict[str, list[str]] = {}
    records = load_jsonl(source_dir / "documents.jsonl")
    for rec in records:
        chunk_map.setdefault(rec["document_id"], []).append(rec["chunk_id"])

    existing = load_existing_manifest(manifest_path)
    fetcher = ArchiveFetcher(rate_limit_sec=1.5)

    # Find all meta files
    meta_files = sorted(source_dir.glob("uokik_pdf_*.meta.json"))
    logger.info("uokik_pdfs: %d documents to process", len(meta_files))

    for meta_path in meta_files:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        doc_id = meta["document_id"]
        url = meta["source_url"]
        archive_path_rel = f"_archive/{doc_id}.pdf"
        archive_path_abs = source_dir / "_archive" / f"{doc_id}.pdf"

        if doc_id in existing and archive_path_abs.exists():
            logger.info("skip %s (already archived)", doc_id)
            manifest.add(existing[doc_id])
            continue

        if dry_run:
            logger.info("[DRY] would fetch %s -> %s", url, archive_path_rel)
            continue

        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            status = resp.status_code if resp is not None else 0
            logger.error("FAIL %s: HTTP %d", doc_id, status)
            manifest.add_error(doc_id, url, f"HTTP {status}")
            continue

        data = resp.content
        if not data.startswith(b"%PDF"):
            logger.error("FAIL %s: not a PDF (first bytes: %r)", doc_id, data[:16])
            manifest.add_error(doc_id, url, "not_a_pdf")
            continue

        write_binary(archive_path_abs, data)
        entry = ManifestEntry(
            doc_id=doc_id,
            source_url=url,
            archive_path=archive_path_rel,
            content_type=detect_content_type(resp, "application/pdf"),
            size_bytes=len(data),
            sha256=sha256_bytes(data),
            chunk_ids=chunk_map.get(doc_id, []),
            license=meta.get("license"),
        )
        manifest.add(entry)
        logger.info("OK %s (%d bytes)", doc_id, len(data))

    manifest.save(manifest_path)
    return manifest


def archive_rf_pdfs(*, dry_run: bool = False) -> ArchiveManifest:
    """36 Rzecznik Finansowy analizy PDF — WAF (Incapsula) hosted."""
    source_dir = DATA_RAW / "consumer_documents_2026-05-16" / "rf_pdfs"
    archive_dir = source_dir / "_archive"
    manifest_path = archive_dir / "_manifest.json"
    manifest = ArchiveManifest(
        source="rf.gov.pl", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )

    chunk_map: dict[str, list[str]] = {}
    records = load_jsonl(source_dir / "documents.jsonl")
    for rec in records:
        chunk_map.setdefault(rec["document_id"], []).append(rec["chunk_id"])

    existing = load_existing_manifest(manifest_path)
    fetcher = ArchiveFetcher(rate_limit_sec=3.0, per_request_session=True)

    meta_files = sorted(source_dir.glob("rf_pdf_*.meta.json"))
    logger.info("rf_pdfs: %d documents to process (WAF — slow)", len(meta_files))

    for meta_path in meta_files:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        doc_id = meta["document_id"]
        url = meta["source_url"]
        archive_path_rel = f"_archive/{doc_id}.pdf"
        archive_path_abs = source_dir / "_archive" / f"{doc_id}.pdf"

        if doc_id in existing and archive_path_abs.exists():
            manifest.add(existing[doc_id])
            continue

        if dry_run:
            logger.info("[DRY] %s -> %s", url, archive_path_rel)
            continue

        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            status = resp.status_code if resp is not None else 0
            reason = "WAF_blocked" if status == 0 else f"HTTP {status}"
            logger.error("FAIL %s: %s", doc_id, reason)
            manifest.add_error(doc_id, url, reason)
            continue

        data = resp.content
        if not data.startswith(b"%PDF"):
            logger.error("FAIL %s: not a PDF (got HTML/WAF page)", doc_id)
            manifest.add_error(doc_id, url, "not_a_pdf_likely_WAF")
            continue

        write_binary(archive_path_abs, data)
        entry = ManifestEntry(
            doc_id=doc_id,
            source_url=url,
            archive_path=archive_path_rel,
            content_type="application/pdf",
            size_bytes=len(data),
            sha256=sha256_bytes(data),
            chunk_ids=chunk_map.get(doc_id, []),
            license=meta.get("license"),
        )
        manifest.add(entry)
        logger.info("OK %s (%d bytes)", doc_id, len(data))

    manifest.save(manifest_path)
    return manifest


def archive_federacja_documents(*, dry_run: bool = False) -> ArchiveManifest:
    """5 Federacja Konsumentów (3 PDF + 2 HTML) z documents.jsonl."""
    source_dir = DATA_RAW / "consumer_documents_2026-05-16" / "federacja_konsumentow"
    archive_dir = source_dir / "_archive"
    manifest_path = archive_dir / "_manifest.json"
    manifest = ArchiveManifest(
        source="federacja-konsumentow.org.pl", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )

    chunk_map: dict[str, list[str]] = {}
    records = load_jsonl(source_dir / "documents.jsonl")
    for rec in records:
        chunk_map.setdefault(rec["document_id"], []).append(rec["chunk_id"])

    existing = load_existing_manifest(manifest_path)
    fetcher = ArchiveFetcher(rate_limit_sec=1.5)

    meta_files = sorted(source_dir.glob("fk_*.meta.json"))
    logger.info("federacja: %d documents", len(meta_files))

    for meta_path in meta_files:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        doc_id = meta["document_id"]
        url = meta["source_url"]
        is_pdf = doc_id.startswith("fk_pdf_")
        ext = "pdf" if is_pdf else "html"
        archive_path_rel = f"_archive/{doc_id}.{ext}"
        archive_path_abs = source_dir / "_archive" / f"{doc_id}.{ext}"

        if doc_id in existing and archive_path_abs.exists():
            manifest.add(existing[doc_id])
            continue

        if dry_run:
            logger.info("[DRY] %s -> %s", url, archive_path_rel)
            continue

        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            status = resp.status_code if resp is not None else 0
            logger.error("FAIL %s: HTTP %d", doc_id, status)
            manifest.add_error(doc_id, url, f"HTTP {status}")
            continue

        data = resp.content
        if is_pdf and not data.startswith(b"%PDF"):
            logger.error("FAIL %s: PDF expected but got non-PDF body", doc_id)
            manifest.add_error(doc_id, url, "not_a_pdf")
            continue

        write_binary(archive_path_abs, data)
        entry = ManifestEntry(
            doc_id=doc_id,
            source_url=url,
            archive_path=archive_path_rel,
            content_type=detect_content_type(resp, f"application/{ext}" if is_pdf else "text/html"),
            size_bytes=len(data),
            sha256=sha256_bytes(data),
            chunk_ids=chunk_map.get(doc_id, []),
            license=meta.get("license"),
        )
        manifest.add(entry)
        logger.info("OK %s (%d bytes)", doc_id, len(data))

    manifest.save(manifest_path)
    return manifest


def archive_orzeczenia(*, dry_run: bool = False) -> ArchiveManifest:
    """10 wyroków orzeczenia.ms.gov.pl — raw HTML."""
    source_dir = DATA_RAW / "consumer_documents_2026-05-16" / "orzeczenia"
    archive_dir = source_dir / "_archive"
    manifest_path = archive_dir / "_manifest.json"
    manifest = ArchiveManifest(
        source="orzeczenia.ms.gov.pl", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )

    chunk_map: dict[str, list[str]] = {}
    records = load_jsonl(source_dir / "documents.jsonl")
    for rec in records:
        chunk_map.setdefault(rec["document_id"], []).append(rec["chunk_id"])

    existing = load_existing_manifest(manifest_path)
    # ms.gov.pl is touchy — slower rate to avoid rate-limit reject pages
    fetcher = ArchiveFetcher(rate_limit_sec=4.0)

    meta_files = sorted(source_dir.glob("orz_*.meta.json"))
    logger.info("orzeczenia: %d documents", len(meta_files))

    for meta_path in meta_files:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        doc_id = meta["document_id"]
        url = meta["source_url"]
        archive_path_rel = f"_archive/{doc_id}.html"
        archive_path_abs = source_dir / "_archive" / f"{doc_id}.html"

        if doc_id in existing and archive_path_abs.exists():
            manifest.add(existing[doc_id])
            continue

        if dry_run:
            logger.info("[DRY] %s -> %s", url, archive_path_rel)
            continue

        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            status = resp.status_code if resp is not None else 0
            logger.error("FAIL %s: HTTP %d", doc_id, status)
            manifest.add_error(doc_id, url, f"HTTP {status}")
            continue

        # Use response.text (utf-8 decoded) for HTML
        if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
            resp.encoding = "utf-8"
        data = resp.text.encode("utf-8")

        # Detect ms.gov.pl rate-limit reject pages (sub-512B)
        if len(data) < 512 and (
            "Połączenie odrzucone" in resp.text or "Twój identyfikator zgłoszenia" in resp.text
        ):
            logger.error("FAIL %s: rate-limit reject page", doc_id)
            manifest.add_error(doc_id, url, "rate_limit_reject_after_retries")
            continue

        write_binary(archive_path_abs, data)
        entry = ManifestEntry(
            doc_id=doc_id,
            source_url=url,
            archive_path=archive_path_rel,
            content_type="text/html",
            size_bytes=len(data),
            sha256=sha256_bytes(data),
            chunk_ids=chunk_map.get(doc_id, []),
            license=meta.get("license"),
        )
        manifest.add(entry)
        logger.info("OK %s (%d bytes)", doc_id, len(data))

    manifest.save(manifest_path)
    return manifest


def archive_ue_dyrektywy(*, dry_run: bool = False) -> ArchiveManifest:
    """8 dyrektyw UE z EUR-Lex — both PDF + HTML per CELEX."""
    source_dir = DATA_RAW / "ue_dyrektywy_2026-05-16"
    archive_dir = source_dir / "_archive"
    manifest_path = archive_dir / "_manifest.json"
    manifest = ArchiveManifest(
        source="eur-lex.europa.eu", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )

    existing = load_existing_manifest(manifest_path)
    fetcher = ArchiveFetcher(rate_limit_sec=2.0)  # EUR-Lex polite rate

    meta_files = sorted(source_dir.glob("*_meta.json"))
    logger.info(
        "ue_dyrektywy: %d directives x 2 formats = %d files", len(meta_files), 2 * len(meta_files)
    )

    for meta_path in meta_files:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        celex_id = meta["celex_id"]

        chunk_ids: list[str] = []
        jsonl_path = source_dir / f"{celex_id}.jsonl"
        if jsonl_path.exists():
            chunk_ids = [r["chunk_id"] for r in load_jsonl(jsonl_path)]

        for fmt in ("pdf", "html"):
            doc_id = f"{celex_id}_{fmt}"
            url = meta.get("source_url_pdf") if fmt == "pdf" else meta.get("source_url_html")
            if not url:
                url = f"https://eur-lex.europa.eu/legal-content/PL/TXT/{fmt.upper()}/?uri=CELEX:{celex_id}"
            archive_path_rel = f"_archive/{celex_id}.{fmt}"
            archive_path_abs = source_dir / "_archive" / f"{celex_id}.{fmt}"

            if doc_id in existing and archive_path_abs.exists():
                manifest.add(existing[doc_id])
                continue

            if dry_run:
                logger.info("[DRY] %s -> %s", url, archive_path_rel)
                continue

            resp = fetcher.get(url)
            if resp is None or resp.status_code != 200:
                status = resp.status_code if resp is not None else 0
                logger.error("FAIL %s: HTTP %d", doc_id, status)
                manifest.add_error(doc_id, url, f"HTTP {status}")
                continue

            if fmt == "pdf":
                data = resp.content
                if not data.startswith(b"%PDF"):
                    logger.error("FAIL %s: not a PDF", doc_id)
                    manifest.add_error(doc_id, url, "not_a_pdf")
                    continue
                ct = "application/pdf"
            else:
                if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
                    resp.encoding = "utf-8"
                data = resp.text.encode("utf-8")
                ct = "text/html"

            write_binary(archive_path_abs, data)
            entry = ManifestEntry(
                doc_id=doc_id,
                source_url=url,
                archive_path=archive_path_rel,
                content_type=ct,
                size_bytes=len(data),
                sha256=sha256_bytes(data),
                chunk_ids=chunk_ids,
                license=meta.get("license"),
            )
            manifest.add(entry)
            logger.info("OK %s (%d bytes)", doc_id, len(data))

    manifest.save(manifest_path)
    return manifest


def archive_tsue(*, dry_run: bool = False) -> ArchiveManifest:
    """29 TSUE cases z EUR-Lex — both PDF + HTML per case."""
    source_dir = DATA_RAW / "tsue_orzeczenia_2026-05-16"
    archive_dir = source_dir / "_archive"
    manifest_path = archive_dir / "_manifest.json"
    manifest = ArchiveManifest(
        source="eur-lex.europa.eu (TSUE)", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )

    existing = load_existing_manifest(manifest_path)
    fetcher = ArchiveFetcher(rate_limit_sec=2.0)

    # Build chunk_id map from main jsonl
    chunk_map: dict[str, list[str]] = {}
    jsonl_path = source_dir / "tsue_orzeczenia.jsonl"
    for rec in load_jsonl(jsonl_path):
        celex = rec.get("celex_id") or rec.get("metadata", {}).get("celex_id")
        if celex:
            chunk_map.setdefault(celex, []).append(rec.get("chunk_id", rec.get("case_id", "")))

    meta_files = sorted((source_dir / "per_case_meta").glob("*_meta.json"))
    logger.info("tsue: %d cases x 2 formats = %d files", len(meta_files), 2 * len(meta_files))

    for meta_path in meta_files:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        celex_id = meta["celex_id"]

        for fmt in ("pdf", "html"):
            doc_id = f"{celex_id}_{fmt}"
            url = f"https://eur-lex.europa.eu/legal-content/PL/TXT/{fmt.upper()}/?uri=CELEX:{celex_id}"
            archive_path_rel = f"_archive/{celex_id}.{fmt}"
            archive_path_abs = source_dir / "_archive" / f"{celex_id}.{fmt}"

            if doc_id in existing and archive_path_abs.exists():
                manifest.add(existing[doc_id])
                continue

            if dry_run:
                logger.info("[DRY] %s -> %s", url, archive_path_rel)
                continue

            resp = fetcher.get(url)
            if resp is None or resp.status_code != 200:
                status = resp.status_code if resp is not None else 0
                logger.error("FAIL %s: HTTP %d", doc_id, status)
                manifest.add_error(doc_id, url, f"HTTP {status}")
                continue

            if fmt == "pdf":
                data = resp.content
                if not data.startswith(b"%PDF"):
                    logger.error("FAIL %s: not a PDF", doc_id)
                    manifest.add_error(doc_id, url, "not_a_pdf")
                    continue
                ct = "application/pdf"
            else:
                if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
                    resp.encoding = "utf-8"
                data = resp.text.encode("utf-8")
                ct = "text/html"

            write_binary(archive_path_abs, data)
            entry = ManifestEntry(
                doc_id=doc_id,
                source_url=url,
                archive_path=archive_path_rel,
                content_type=ct,
                size_bytes=len(data),
                sha256=sha256_bytes(data),
                chunk_ids=chunk_map.get(celex_id, []),
                license=meta.get("license"),
            )
            manifest.add(entry)
            logger.info("OK %s (%d bytes)", doc_id, len(data))

    manifest.save(manifest_path)
    return manifest


# === E1 extended sources (HTML, 1:1 URL/record except wikipedia, RF FAQ) ===


def _archive_extended_html(
    jsonl_path: Path,
    archive_subdir: str,
    *,
    fetcher: ArchiveFetcher,
    manifest: ArchiveManifest,
    existing: dict[str, ManifestEntry],
    dry_run: bool = False,
    id_field: str = "chunk_id",
    group_by_url: bool = False,
    slug_field: str | None = None,
) -> None:
    """Generic helper — fetch per-URL HTML, dedupe if needed, write."""
    records = load_jsonl(jsonl_path)
    archive_dir = jsonl_path.parent / "_archive" / archive_subdir

    # Dedupe by URL (for wikipedia, rf_faq)
    if group_by_url:
        url_to_record: dict[str, dict[str, Any]] = {}
        url_to_chunks: dict[str, list[str]] = {}
        for rec in records:
            url = rec["source_url"]
            if url not in url_to_record:
                url_to_record[url] = rec
            url_to_chunks.setdefault(url, []).append(rec.get(id_field, ""))
        targets = list(url_to_record.items())  # list of (url, first_rec)
    else:
        targets = [(rec["source_url"], rec) for rec in records]
        url_to_chunks = {rec["source_url"]: [rec.get(id_field, "")] for rec in records}

    logger.info(
        "%s: %d records -> %d unique URLs to fetch", archive_subdir, len(records), len(targets)
    )

    for url, rec in targets:
        if slug_field and rec.get(slug_field):
            slug = slugify_for_filename(rec[slug_field])
        elif group_by_url:
            # Build slug from URL path
            path_part = url.rstrip("/").split("/")[-1] or "index"
            slug = slugify_for_filename(path_part)
        else:
            slug = slugify_for_filename(rec.get(id_field, url))
        # Ensure uniqueness — append short hash if collision
        url_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
        filename = f"{slug}__{url_hash}.html"
        doc_id = filename[:-5]  # drop .html
        archive_path_rel = f"_archive/{archive_subdir}/{filename}"
        archive_path_abs = archive_dir / filename

        if doc_id in existing and archive_path_abs.exists():
            manifest.add(existing[doc_id])
            continue

        if dry_run:
            logger.info("[DRY] %s -> %s", url, archive_path_rel)
            continue

        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            status = resp.status_code if resp is not None else 0
            logger.error("FAIL %s: HTTP %d", doc_id, status)
            manifest.add_error(doc_id, url, f"HTTP {status}")
            continue

        if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
            resp.encoding = "utf-8"
        data = resp.text.encode("utf-8")

        write_binary(archive_path_abs, data)
        entry = ManifestEntry(
            doc_id=doc_id,
            source_url=url,
            archive_path=archive_path_rel,
            content_type="text/html",
            size_bytes=len(data),
            sha256=sha256_bytes(data),
            chunk_ids=url_to_chunks.get(url, []),
            license=rec.get("license"),
        )
        manifest.add(entry)
        logger.info("OK %s (%d bytes)", doc_id, len(data))


def archive_extended_wikipedia(*, dry_run: bool = False) -> ArchiveManifest:
    """Wikipedia: 34 chunks → 15 unique URLs."""
    source_dir = DATA_RAW / "extended_consumer_2026-05-16"
    manifest_path = source_dir / "_archive" / "wikipedia" / "_manifest.json"
    manifest = ArchiveManifest(
        source="pl.wikipedia.org", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )
    fetcher = ArchiveFetcher(rate_limit_sec=1.0)
    existing = load_existing_manifest(manifest_path)
    _archive_extended_html(
        source_dir / "wikipedia_consumer.jsonl",
        "wikipedia",
        fetcher=fetcher,
        manifest=manifest,
        existing=existing,
        dry_run=dry_run,
        group_by_url=True,
    )
    manifest.save(manifest_path)
    return manifest


def archive_extended_federacja(*, dry_run: bool = False) -> ArchiveManifest:
    """Federacja E1: 192 records, 1:1 with URL."""
    source_dir = DATA_RAW / "extended_consumer_2026-05-16"
    manifest_path = source_dir / "_archive" / "federacja" / "_manifest.json"
    manifest = ArchiveManifest(
        source="federacja-konsumentow.org.pl (E1)",
        source_dir=str(source_dir.relative_to(REPO_ROOT)),
    )
    fetcher = ArchiveFetcher(rate_limit_sec=1.5)
    existing = load_existing_manifest(manifest_path)
    _archive_extended_html(
        source_dir / "federacja_konsumentow.jsonl",
        "federacja",
        fetcher=fetcher,
        manifest=manifest,
        existing=existing,
        dry_run=dry_run,
    )
    manifest.save(manifest_path)
    return manifest


def archive_extended_uokik_news(*, dry_run: bool = False) -> ArchiveManifest:
    """UOKiK news E1: 111 records, 1:1."""
    source_dir = DATA_RAW / "extended_consumer_2026-05-16"
    manifest_path = source_dir / "_archive" / "uokik_news" / "_manifest.json"
    manifest = ArchiveManifest(
        source="uokik.gov.pl (news)", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )
    fetcher = ArchiveFetcher(rate_limit_sec=1.5)
    existing = load_existing_manifest(manifest_path)
    _archive_extended_html(
        source_dir / "uokik_news.jsonl",
        "uokik_news",
        fetcher=fetcher,
        manifest=manifest,
        existing=existing,
        dry_run=dry_run,
    )
    manifest.save(manifest_path)
    return manifest


def archive_extended_gov_pl(*, dry_run: bool = False) -> ArchiveManifest:
    """gov.pl E1: 5 records."""
    source_dir = DATA_RAW / "extended_consumer_2026-05-16"
    manifest_path = source_dir / "_archive" / "gov_pl" / "_manifest.json"
    manifest = ArchiveManifest(source="gov.pl", source_dir=str(source_dir.relative_to(REPO_ROOT)))
    fetcher = ArchiveFetcher(rate_limit_sec=1.5)
    existing = load_existing_manifest(manifest_path)
    _archive_extended_html(
        source_dir / "gov_pl_consumer.jsonl",
        "gov_pl",
        fetcher=fetcher,
        manifest=manifest,
        existing=existing,
        dry_run=dry_run,
    )
    manifest.save(manifest_path)
    return manifest


def archive_extended_rf_faq(*, dry_run: bool = False) -> ArchiveManifest:
    """RF FAQ E1: 374 records → 25 unique URLs (per-category). WAF."""
    source_dir = DATA_RAW / "extended_consumer_2026-05-16"
    manifest_path = source_dir / "_archive" / "rf_faq" / "_manifest.json"
    manifest = ArchiveManifest(
        source="rf.gov.pl (FAQ)", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )
    fetcher = ArchiveFetcher(rate_limit_sec=3.0, per_request_session=True)
    existing = load_existing_manifest(manifest_path)
    _archive_extended_html(
        source_dir / "rzecznik_finansowy_faq.jsonl",
        "rf_faq",
        fetcher=fetcher,
        manifest=manifest,
        existing=existing,
        dry_run=dry_run,
        id_field="qa_id",
        group_by_url=True,
        slug_field="category",
    )
    manifest.save(manifest_path)
    return manifest


def archive_uokik_qa(*, dry_run: bool = False) -> ArchiveManifest:
    """UOKiK Q&A gold: 60 pairs → 5 unique URLs (per-category)."""
    source_dir = DATA_RAW / "uokik_qa_2026-05-16"
    manifest_path = source_dir / "_archive" / "_manifest.json"
    manifest = ArchiveManifest(
        source="prawakonsumenta.uokik.gov.pl", source_dir=str(source_dir.relative_to(REPO_ROOT))
    )
    fetcher = ArchiveFetcher(rate_limit_sec=1.5)
    existing = load_existing_manifest(manifest_path)
    _archive_extended_html(
        source_dir / "uokik_qa.jsonl",
        ".",  # store directly in _archive/
        fetcher=fetcher,
        manifest=manifest,
        existing=existing,
        dry_run=dry_run,
        id_field="qa_id",
        group_by_url=True,
        slug_field="category",
    )
    manifest.save(manifest_path)
    return manifest


def archive_consumer_questions_sample(*, dry_run: bool = False) -> ArchiveManifest:
    """Consumer questions PROOF SAMPLE — 20 records from each of 4 forums (80 total).

    Full 2,967 archive skipped per task brief (session/cookie restrictions).
    Sample as evidence that URLs are real + format consistent.

    Note: a separate pre-existing archive tool (z innym schema manifestu) już zbudowało
    częściowy archive w ``_archive/<forum>/eprawnik_NNN.html``. Nie nadpisujemy —
    zapisujemy nasz manifest osobno jako ``_archive_manifest_proof.json`` żeby coexist.
    """
    source_dir = DATA_RAW / "consumer_questions_polish_2026-05-16"
    # Use a separate manifest filename to avoid clash with existing pre-archive tool's manifest
    manifest_path = source_dir / "_archive" / "_manifest_archive_sweep.json"
    manifest = ArchiveManifest(
        source="consumer_questions_sample",
        source_dir=str(source_dir.relative_to(REPO_ROOT)),
    )
    manifest.stats["proof_sample"] = True
    manifest.stats["proof_sample_per_forum"] = 20
    manifest.stats["note"] = (
        "Separate from pre-existing _manifest.json (other tool). "
        "This sweep produces _manifest_archive_sweep.json — proof sample only."
    )
    fetcher = ArchiveFetcher(rate_limit_sec=2.0)
    existing = load_existing_manifest(manifest_path)

    forums = [
        ("e_prawnik", source_dir / "e_prawnik_consumer.jsonl"),
        ("forumprawne", source_dir / "forumprawne_consumer.jsonl"),
        ("legal_other", source_dir / "legal_other_polish.jsonl"),
        ("reddit_polska", source_dir / "reddit_polska_consumer.jsonl"),
    ]

    for forum_name, jsonl_path in forums:
        if not jsonl_path.exists():
            logger.warning("skip %s (no jsonl)", forum_name)
            continue
        records = load_jsonl(jsonl_path)[:20]
        archive_dir = source_dir / "_archive" / forum_name
        logger.info("consumer_questions_sample/%s: %d records", forum_name, len(records))
        for rec in records:
            qid = rec.get("question_id") or rec.get("id") or rec.get("post_id") or "unk"
            url = rec.get("source_url") or rec.get("url")
            if not url:
                continue
            url_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
            filename = f"{slugify_for_filename(qid)}__{url_hash}.html"
            doc_id = f"{forum_name}/{filename[:-5]}"
            archive_path_rel = f"_archive/{forum_name}/{filename}"
            archive_path_abs = archive_dir / filename

            if doc_id in existing and archive_path_abs.exists():
                manifest.add(existing[doc_id])
                continue
            if dry_run:
                logger.info("[DRY] %s -> %s", url, archive_path_rel)
                continue

            resp = fetcher.get(url, retries=1)  # don't waste budget on closed forums
            if resp is None or resp.status_code != 200:
                status = resp.status_code if resp is not None else 0
                manifest.add_error(doc_id, url, f"HTTP {status}")
                continue
            if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
                resp.encoding = "utf-8"
            data = resp.text.encode("utf-8")
            if len(data) < 1024 and (b"cloudflare" in data.lower() or b"captcha" in data.lower()):
                manifest.add_error(doc_id, url, "captcha_or_cloudflare")
                continue
            write_binary(archive_path_abs, data)
            entry = ManifestEntry(
                doc_id=doc_id,
                source_url=url,
                archive_path=archive_path_rel,
                content_type="text/html",
                size_bytes=len(data),
                sha256=sha256_bytes(data),
                chunk_ids=[qid],
                license="fair-use research sample",
            )
            manifest.add(entry)
            logger.info("OK %s (%d bytes)", doc_id, len(data))

    manifest.save(manifest_path)
    return manifest


# === Orchestrator ===


SOURCE_REGISTRY: dict[str, tuple[str, Any]] = {
    "uokik_pdfs": ("Priority 1: UOKiK poradniki PDF", archive_uokik_pdfs),
    "rf_pdfs": ("Priority 1: RF analizy PDF (WAF)", archive_rf_pdfs),
    "federacja_docs": ("Priority 1: Federacja PDF+HTML", archive_federacja_documents),
    "orzeczenia": ("Priority 1: orzeczenia.ms.gov.pl HTML", archive_orzeczenia),
    "ue_dyrektywy": ("Priority 2: UE dyrektywy PDF+HTML", archive_ue_dyrektywy),
    "tsue": ("Priority 2: TSUE PDF+HTML", archive_tsue),
    "wikipedia": ("Priority 3: Wikipedia consumer HTML", archive_extended_wikipedia),
    "federacja_e1": ("Priority 3: Federacja E1 HTML", archive_extended_federacja),
    "uokik_news": ("Priority 3: UOKiK news HTML", archive_extended_uokik_news),
    "gov_pl": ("Priority 3: gov.pl HTML", archive_extended_gov_pl),
    "rf_faq": ("Priority 3: RF FAQ HTML (WAF)", archive_extended_rf_faq),
    "uokik_qa": ("Priority 4: UOKiK Q&A categories HTML", archive_uokik_qa),
    "consumer_questions": (
        "Priority 4: consumer questions proof sample",
        archive_consumer_questions_sample,
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", "-s", action="append", default=None, help="Source key (repeat for multiple)"
    )
    parser.add_argument("--all", action="store_true", help="Run all sources")
    parser.add_argument("--dry-run", action="store_true", help="Don't download — log plan")
    parser.add_argument("--log-level", default="INFO", help="DEBUG|INFO|WARNING")
    parser.add_argument("--list", action="store_true", help="List sources and exit")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.list:
        for key, (descr, _) in SOURCE_REGISTRY.items():
            print(f"  {key:20s}  {descr}")
        return 0

    targets: list[str]
    if args.all:
        targets = list(SOURCE_REGISTRY.keys())
    elif args.source:
        targets = args.source
    else:
        parser.error("Specify --all or --source <key>")

    # Validate
    for t in targets:
        if t not in SOURCE_REGISTRY:
            parser.error(f"Unknown source: {t}. Try --list.")

    summary: dict[str, dict[str, Any]] = {}
    for key in targets:
        descr, fn = SOURCE_REGISTRY[key]
        logger.info("=" * 70)
        logger.info("SOURCE: %s — %s", key, descr)
        logger.info("=" * 70)
        try:
            m = fn(dry_run=args.dry_run)
            summary[key] = {
                "entries": len(m.entries),
                "errors": len(m.errors),
                "total_bytes": sum(e.size_bytes for e in m.entries),
            }
        except Exception as exc:
            logger.exception("source %s FAILED: %s", key, exc)
            summary[key] = {"entries": 0, "errors": -1, "total_bytes": 0, "exception": str(exc)}

    # Aggregate summary
    sweep_summary_path = DATA_RAW / "_archive_sweep_summary.json"
    sweep_summary_path.write_text(
        json.dumps(
            {
                "sweep_date": TODAY,
                "user_agent": USER_AGENT_BASE,
                "sources": summary,
                "total_bytes": sum(s["total_bytes"] for s in summary.values()),
                "total_entries": sum(s["entries"] for s in summary.values()),
                "total_errors": sum(s["errors"] for s in summary.values() if s["errors"] >= 0),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("sweep summary -> %s", sweep_summary_path)

    print("\n=== SWEEP SUMMARY ===")
    for key, s in summary.items():
        print(
            f"  {key:20s}  entries={s['entries']:4d}  errors={s['errors']:3d}  bytes={s['total_bytes']:>12,d}"  # noqa: E501
        )
    print(
        f"\nTOTAL: {sum(s['entries'] for s in summary.values())} entries, "
        f"{sum(s['total_bytes'] for s in summary.values()):,} bytes "
        f"(~{sum(s['total_bytes'] for s in summary.values()) / 1024 / 1024:.1f} MB)"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
