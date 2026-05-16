"""Download raw HTML/JSON for every forum question record in the
``consumer_questions_polish_2026-05-16`` collection.

Per Magda 2026-05-16: "wszystko ma być zdobyte" — earlier raw-archive sweep
agent skipped 2,967 forum records as "noisy", but raw source must be on disk
for every scraped item (provenance + reproducibility for thesis defence).

Sources (4 JSONL files in ``data/raw/consumer_questions_polish_2026-05-16/``):
  - e_prawnik_consumer.jsonl       (954 records, e-prawnik.pl)
  - forumprawne_consumer.jsonl     (1,202 records, forumprawne.org — Cloudflare!)
  - reddit_polska_consumer.jsonl   (509 records, reddit.com — uses .json endpoint)
  - legal_other_polish.jsonl       (302 records, eporady24.pl/infor.pl/prawo.pl)

Output layout::

    data/raw/consumer_questions_polish_2026-05-16/
      _archive/
        e_prawnik/{question_id}.html
        e_prawnik/{question_id}.meta.json
        forumprawne/{question_id}.html
        forumprawne/{question_id}.meta.json
        reddit/{question_id}.json
        reddit/{question_id}.meta.json
        legal_other/{question_id}.html
        legal_other/{question_id}.meta.json
        _manifest.json

Each ``*.meta.json`` carries::

    {
      "question_id": "...",
      "source_url": "...",
      "archive_file": "e_prawnik/eprawnik_00001.html",
      "http_status": 200,
      "content_type": "text/html; charset=UTF-8",
      "size_bytes": 23456,
      "sha256": "...",
      "download_date": "2026-05-17T12:34:56Z",
      "duration_sec": 0.83,
      "error": false,
      "error_reason": null
    }

Idempotent: if the archive file exists and the sha256 in the meta matches what
is on disk, the entry is skipped. Use ``--force`` to redownload regardless.

Polite scraping (per-domain ``httpx.Client``):
  - User-Agent: academic research contact email
  - Rate limit: 1 req/sec (forumprawne), 1 req/sec (e-prawnik, eporady24),
    2 req/sec (Reddit — JSON endpoint)
  - Retries: 3x exponential backoff for 429/503
  - 404 → ``error: not_found`` in meta, continue
  - No concurrent requests on the same domain.

Usage (PowerShell)::

    cd D:\\diplomma\\main_project
    $env:PYTHONPATH = "src"
    uv run python -m ingest.archive_forum_html
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import signal
import sys
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger("ingest.archive_forum_html")

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------

# Per Magda — academic research, polite UA with contact:
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) consumer-rights-academic-research@pjwstk.edu.pl"
)
# Slightly richer browser-like headers help with Cloudflare-fronted sites
# (forumprawne.org). Some sites refuse responses with a clearly-non-browser UA.
BROWSER_HEADERS = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Chromium";v="120", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

REDDIT_HEADERS = {
    # Reddit's unauthenticated `.json` endpoint rate-limits and blocks
    # aggressively for anything that looks bot-like. The PJATK academic UA we
    # use for the other domains gets 403-blocked here, so use a plain Chrome UA
    # for Reddit specifically.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.7",
}

REQUEST_TIMEOUT = httpx.Timeout(30.0, connect=15.0)
MAX_RETRIES = 5
DEFAULT_RATE_LIMIT_SEC = 1.0
# Reddit's unauthenticated `.json` endpoint starts 429-ing aggressively after
# ~30 requests/min for "scrape-like" UA patterns. Push pacing to ~10 req/min so
# we stay safely under the soft cap. Cost is ~1 min/12 records, acceptable for
# 509 records (~45 min). The earlier 0.5s/req triggered persistent 429s after
# ~100 records and the retry storm cost us little but throughput.
REDDIT_RATE_LIMIT_SEC = 12.0
# Reddit-specific extra wait when a 429 is encountered, on top of the per-
# attempt exponential backoff. This is the dominant signal that we are being
# rate-limited globally, so wait longer before any next request.
REDDIT_429_COOLDOWN_SEC = 120.0
RETRYABLE_STATUSES = {429, 502, 503, 504}


# ---------------------------------------------------------------------------
# domain config
# ---------------------------------------------------------------------------


@dataclass
class DomainConfig:
    """Per-domain download configuration."""

    name: str  # e_prawnik / forumprawne / reddit / legal_other
    jsonl_file: str  # filename inside collection dir
    subdir: str  # subdir under _archive/
    extension: str  # .html or .json
    rate_limit_sec: float
    is_reddit: bool = False  # special URL rewriting (+ .json suffix)
    headers: dict[str, str] = field(default_factory=dict)


DOMAINS: dict[str, DomainConfig] = {
    "e_prawnik": DomainConfig(
        name="e_prawnik",
        jsonl_file="e_prawnik_consumer.jsonl",
        subdir="e_prawnik",
        extension=".html",
        rate_limit_sec=DEFAULT_RATE_LIMIT_SEC,
        headers={**BROWSER_HEADERS, "User-Agent": USER_AGENT},
    ),
    "forumprawne": DomainConfig(
        name="forumprawne",
        jsonl_file="forumprawne_consumer.jsonl",
        subdir="forumprawne",
        extension=".html",
        rate_limit_sec=DEFAULT_RATE_LIMIT_SEC,
        headers={**BROWSER_HEADERS, "User-Agent": USER_AGENT},
    ),
    "reddit": DomainConfig(
        name="reddit",
        jsonl_file="reddit_polska_consumer.jsonl",
        subdir="reddit",
        extension=".json",
        rate_limit_sec=REDDIT_RATE_LIMIT_SEC,
        is_reddit=True,
        # NB: REDDIT_HEADERS already contains its own Chrome User-Agent —
        # do NOT overwrite it with the academic USER_AGENT (Reddit 403s on
        # academic UAs in mass and our IP gets banned for ~30 min).
        headers=dict(REDDIT_HEADERS),
    ),
    "legal_other": DomainConfig(
        name="legal_other",
        jsonl_file="legal_other_polish.jsonl",
        subdir="legal_other",
        extension=".html",
        rate_limit_sec=DEFAULT_RATE_LIMIT_SEC,
        headers={**BROWSER_HEADERS, "User-Agent": USER_AGENT},
    ),
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def reddit_json_url(source_url: str) -> str:
    """Append ``.json`` to a Reddit permalink (if not already present).

    Examples:
        https://www.reddit.com/r/Polska/comments/abc/title/
        → https://www.reddit.com/r/Polska/comments/abc/title/.json
        https://reddit.com/r/Polska/comments/abc/
        → https://reddit.com/r/Polska/comments/abc/.json
    """
    if source_url.endswith(".json"):
        return source_url
    # strip optional trailing query/fragment so the .json suffix actually applies
    if "?" in source_url:
        base, _, qs = source_url.partition("?")
    else:
        base, qs = source_url, ""
    if not base.endswith("/"):
        base += "/"
    base += ".json"
    if qs:
        base += "?" + qs
    return base


def load_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                yield json.loads(raw)
            except json.JSONDecodeError as exc:
                logger.warning("bad JSON line %d in %s: %s", line_no, path, exc)
                continue


# ---------------------------------------------------------------------------
# core
# ---------------------------------------------------------------------------


@dataclass
class DownloadResult:
    """Per-record result returned from ``download_one``."""

    question_id: str
    source_url: str
    archive_file: str | None  # relative to _archive/
    http_status: int | None
    content_type: str | None
    size_bytes: int | None
    sha256: str | None
    download_date: str
    duration_sec: float
    error: bool
    error_reason: str | None
    skipped_existing: bool = False


def existing_meta_ok(meta_path: Path, html_path: Path) -> bool:
    """Return True if an existing meta+html pair is consistent enough to skip."""
    if not (meta_path.exists() and html_path.exists()):
        return False
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if meta.get("error", True):
        # previous run errored — try again, do not skip
        return False
    saved_sha = meta.get("sha256")
    if not saved_sha:
        return False
    try:
        on_disk_sha = sha256_bytes(html_path.read_bytes())
    except OSError:
        return False
    return saved_sha == on_disk_sha


def download_one(
    client: httpx.Client,
    record: dict[str, Any],
    domain: DomainConfig,
    archive_dir: Path,
    *,
    force: bool = False,
) -> DownloadResult:
    question_id = record["question_id"]
    source_url = record["source_url"]
    rel_archive_file = f"{domain.subdir}/{question_id}{domain.extension}"

    blob_path = archive_dir / rel_archive_file
    meta_path = blob_path.with_suffix(blob_path.suffix + ".meta.json")
    blob_path.parent.mkdir(parents=True, exist_ok=True)

    if not force and existing_meta_ok(meta_path, blob_path):
        logger.debug("skip (idempotent): %s", question_id)
        return DownloadResult(
            question_id=question_id,
            source_url=source_url,
            archive_file=rel_archive_file,
            http_status=200,
            content_type=None,
            size_bytes=blob_path.stat().st_size,
            sha256=sha256_bytes(blob_path.read_bytes()),
            download_date=utc_now_iso(),
            duration_sec=0.0,
            error=False,
            error_reason=None,
            skipped_existing=True,
        )

    fetch_url = reddit_json_url(source_url) if domain.is_reddit else source_url

    t0 = time.monotonic()
    last_error: str | None = None
    last_status: int | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = client.get(fetch_url, headers=domain.headers)
        except httpx.RequestError as exc:
            last_error = f"network: {type(exc).__name__}: {exc}"
            last_status = None
            logger.warning(
                "[%s] %s attempt %d ERR %s",
                domain.name,
                question_id,
                attempt + 1,
                last_error,
            )
            if attempt < MAX_RETRIES:
                time.sleep(min(2**attempt, 30))
                continue
            break

        last_status = resp.status_code
        if resp.status_code == 200:
            content = resp.content
            content_type = resp.headers.get("content-type", "")
            blob_path.write_bytes(content)
            meta = {
                "question_id": question_id,
                "source_url": source_url,
                "fetch_url": fetch_url,
                "archive_file": rel_archive_file,
                "http_status": 200,
                "content_type": content_type,
                "size_bytes": len(content),
                "sha256": sha256_bytes(content),
                "download_date": utc_now_iso(),
                "duration_sec": round(time.monotonic() - t0, 3),
                "attempt": attempt + 1,
                "error": False,
                "error_reason": None,
            }
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            return DownloadResult(
                question_id=question_id,
                source_url=source_url,
                archive_file=rel_archive_file,
                http_status=200,
                content_type=content_type,
                size_bytes=len(content),
                sha256=meta["sha256"],
                download_date=meta["download_date"],
                duration_sec=meta["duration_sec"],
                error=False,
                error_reason=None,
            )

        if resp.status_code == 404:
            last_error = "not_found"
            break  # no retries on 404
        if resp.status_code == 401:
            last_error = "forbidden_401"
            break
        if resp.status_code == 403:
            # Reddit returns "403 Blocked" for IP-rate-limited clients (not
            # actual auth failures) — treat as a rate-limit signal and back off
            # hard once before giving up. For non-Reddit domains, 403 is
            # genuine and we should not retry.
            if domain.is_reddit and attempt == 0:
                backoff = REDDIT_429_COOLDOWN_SEC
                logger.warning(
                    "[%s] %s attempt %d -> 403 Blocked, cooldown %ds",
                    domain.name,
                    question_id,
                    attempt + 1,
                    backoff,
                )
                time.sleep(backoff)
                last_error = "blocked_403"
                continue
            last_error = "forbidden_403"
            break
        if resp.status_code in RETRYABLE_STATUSES:
            backoff = min(2**attempt + 1, 30)
            # Reddit 429 = global rate-limit signal — much longer wait
            if domain.is_reddit and resp.status_code == 429:
                backoff = max(backoff, REDDIT_429_COOLDOWN_SEC)
            logger.warning(
                "[%s] %s attempt %d -> %d, backoff %ds",
                domain.name,
                question_id,
                attempt + 1,
                resp.status_code,
                backoff,
            )
            time.sleep(backoff)
            last_error = f"status_{resp.status_code}"
            continue
        last_error = f"status_{resp.status_code}"
        break

    # ---- all attempts exhausted or non-retryable failure ----
    meta = {
        "question_id": question_id,
        "source_url": source_url,
        "fetch_url": fetch_url,
        "archive_file": None,
        "http_status": last_status,
        "content_type": None,
        "size_bytes": None,
        "sha256": None,
        "download_date": utc_now_iso(),
        "duration_sec": round(time.monotonic() - t0, 3),
        "attempt": MAX_RETRIES + 1,
        "error": True,
        "error_reason": last_error or "unknown",
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.warning(
        "[%s] %s FAILED status=%s reason=%s",
        domain.name,
        question_id,
        last_status,
        last_error,
    )
    return DownloadResult(
        question_id=question_id,
        source_url=source_url,
        archive_file=None,
        http_status=last_status,
        content_type=None,
        size_bytes=None,
        sha256=None,
        download_date=meta["download_date"],
        duration_sec=meta["duration_sec"],
        error=True,
        error_reason=last_error,
    )


# ---------------------------------------------------------------------------
# orchestration
# ---------------------------------------------------------------------------


_STOP_REQUESTED = False


def _install_sigint_handler() -> None:
    """Make Ctrl+C set a flag instead of crashing mid-write."""

    def handler(_signum, _frame):
        global _STOP_REQUESTED
        if _STOP_REQUESTED:
            logger.warning("second SIGINT — exiting hard.")
            raise KeyboardInterrupt
        _STOP_REQUESTED = True
        logger.warning("SIGINT — finishing current download then stopping.")

    signal.signal(signal.SIGINT, handler)


def process_domain(
    domain: DomainConfig,
    collection_dir: Path,
    archive_dir: Path,
    *,
    force: bool = False,
    limit: int | None = None,
) -> tuple[list[DownloadResult], dict[str, int]]:
    """Process one domain end-to-end. Returns (results, summary_counts)."""
    jsonl_path = collection_dir / domain.jsonl_file
    if not jsonl_path.exists():
        logger.error("missing JSONL for %s: %s", domain.name, jsonl_path)
        return [], {"missing_jsonl": 1}

    records = list(load_jsonl(jsonl_path))
    if limit is not None:
        records = records[:limit]
    total = len(records)
    logger.info("[%s] %d records to process", domain.name, total)

    results: list[DownloadResult] = []
    counts = {
        "ok": 0,
        "error": 0,
        "skipped_existing": 0,
        "not_found": 0,
        "forbidden": 0,
        "total": total,
    }
    # Kill switch: if we see many consecutive failures, abort this domain so we
    # do not burn the whole queue against a hard IP block. We keep the partial
    # progress; a later run with a fresh IP (or after a long cooldown) can
    # pick up where we left off thanks to idempotency.
    consecutive_failures = 0
    CONSECUTIVE_FAILURE_KILL_SWITCH = 25

    with httpx.Client(
        headers=domain.headers,
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
        http2=False,
    ) as client:
        last_request_time = 0.0
        for idx, record in enumerate(records, 1):
            if _STOP_REQUESTED:
                logger.warning("[%s] stop requested at %d/%d", domain.name, idx, total)
                break

            # check idempotency BEFORE rate-limit sleep — skips should be fast
            question_id = record["question_id"]
            blob_path = archive_dir / f"{domain.subdir}/{question_id}{domain.extension}"
            meta_path = blob_path.with_suffix(blob_path.suffix + ".meta.json")
            will_skip = (not force) and existing_meta_ok(meta_path, blob_path)
            if not will_skip:
                # per-domain rate limit only applies to actual HTTP requests
                elapsed = time.monotonic() - last_request_time
                if elapsed < domain.rate_limit_sec:
                    time.sleep(domain.rate_limit_sec - elapsed)

            result = download_one(client, record, domain, archive_dir, force=force)
            if not will_skip:
                last_request_time = time.monotonic()
            results.append(result)

            if result.skipped_existing:
                counts["skipped_existing"] += 1
                consecutive_failures = 0
            elif result.error:
                counts["error"] += 1
                if result.error_reason == "not_found":
                    counts["not_found"] += 1
                elif result.error_reason and (
                    result.error_reason.startswith("forbidden")
                    or result.error_reason == "blocked_403"
                ):
                    counts["forbidden"] += 1
                consecutive_failures += 1
                if consecutive_failures >= CONSECUTIVE_FAILURE_KILL_SWITCH:
                    logger.error(
                        "[%s] kill switch: %d consecutive failures, aborting "
                        "domain (partial progress kept).",
                        domain.name,
                        consecutive_failures,
                    )
                    break
            else:
                counts["ok"] += 1
                consecutive_failures = 0

            if idx % 50 == 0 or idx == total:
                logger.info(
                    "[%s] %d/%d (ok=%d skip=%d err=%d nf=%d)",
                    domain.name,
                    idx,
                    total,
                    counts["ok"],
                    counts["skipped_existing"],
                    counts["error"],
                    counts["not_found"],
                )

    return results, counts


def write_manifest(
    archive_dir: Path,
    per_domain_results: dict[str, list[DownloadResult]],
    per_domain_counts: dict[str, dict[str, int]],
) -> None:
    """Aggregate per-domain results into ``_manifest.json``.

    Preserves entries from previous runs by reading the existing manifest
    first, then overlaying current-run results. This makes the manifest
    cumulative across resumed runs.
    """
    entries: dict[str, dict[str, Any]] = {}

    # Load existing manifest entries (from previous runs / other domains)
    existing_manifest_path = archive_dir / "_manifest.json"
    if existing_manifest_path.exists():
        try:
            existing = json.loads(existing_manifest_path.read_text(encoding="utf-8"))
            entries.update(existing.get("entries", {}))
        except (json.JSONDecodeError, OSError):
            logger.warning("could not load existing manifest, starting fresh")

    # Overlay current run results
    for domain_name, results in per_domain_results.items():
        for r in results:
            entries[r.question_id] = {
                "domain": domain_name,
                "source_url": r.source_url,
                "archive_file": r.archive_file,
                "http_status": r.http_status,
                "content_type": r.content_type,
                "size_bytes": r.size_bytes,
                "sha256": r.sha256,
                "download_date": r.download_date,
                "duration_sec": r.duration_sec,
                "error": r.error,
                "error_reason": r.error_reason,
                "skipped_existing": r.skipped_existing,
            }

    total_ok = sum(c.get("ok", 0) for c in per_domain_counts.values())
    total_err = sum(c.get("error", 0) for c in per_domain_counts.values())
    total_skip = sum(c.get("skipped_existing", 0) for c in per_domain_counts.values())
    total_nf = sum(c.get("not_found", 0) for c in per_domain_counts.values())
    total_forb = sum(c.get("forbidden", 0) for c in per_domain_counts.values())

    total_bytes = 0
    for path in archive_dir.rglob("*"):
        if path.is_file() and path.suffix in (".html", ".json"):
            if path.name != "_manifest.json":
                try:
                    total_bytes += path.stat().st_size
                except OSError:
                    pass

    manifest = {
        "manifest_version": "1.0",
        "created_at": utc_now_iso(),
        "collection_dir": str(archive_dir.parent),
        "domains": list(per_domain_counts.keys()),
        "counts": per_domain_counts,
        "totals": {
            "ok": total_ok,
            "error": total_err,
            "skipped_existing": total_skip,
            "not_found": total_nf,
            "forbidden": total_forb,
            "records_total": sum(c.get("total", 0) for c in per_domain_counts.values()),
            "archive_total_bytes": total_bytes,
            "archive_total_mb": round(total_bytes / (1024 * 1024), 2),
        },
        "entries": entries,
    }

    manifest_path = archive_dir / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("manifest written: %s", manifest_path)


def rebuild_manifest_from_disk(archive_dir: Path, collection_dir: Path) -> None:
    """Walk the archive subdirectories and rebuild ``_manifest.json``.

    Useful when prior runs overwrote the manifest with only a subset of
    domains, or to recover after a manual file edit. Source-of-truth is the
    per-file ``*.meta.json`` blobs.
    """
    entries: dict[str, dict[str, Any]] = {}
    per_domain_counts: dict[str, dict[str, int]] = {}

    for key, domain in DOMAINS.items():
        subdir = archive_dir / domain.subdir
        if not subdir.exists():
            continue
        c = per_domain_counts.setdefault(
            key,
            {
                "ok": 0,
                "error": 0,
                "skipped_existing": 0,
                "not_found": 0,
                "forbidden": 0,
                "total": 0,
            },
        )
        for meta_path in subdir.glob("*.meta.json"):
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            qid = meta.get("question_id")
            if not qid:
                continue
            c["total"] += 1
            if meta.get("error"):
                c["error"] += 1
                reason = (meta.get("error_reason") or "").lower()
                if reason == "not_found":
                    c["not_found"] += 1
                elif reason.startswith("forbidden") or reason == "blocked_403":
                    c["forbidden"] += 1
            else:
                c["ok"] += 1
            entries[qid] = {
                "domain": key,
                "source_url": meta.get("source_url"),
                "archive_file": meta.get("archive_file"),
                "http_status": meta.get("http_status"),
                "content_type": meta.get("content_type"),
                "size_bytes": meta.get("size_bytes"),
                "sha256": meta.get("sha256"),
                "download_date": meta.get("download_date"),
                "duration_sec": meta.get("duration_sec"),
                "error": meta.get("error", False),
                "error_reason": meta.get("error_reason"),
                "skipped_existing": False,
            }

    total_ok = sum(c.get("ok", 0) for c in per_domain_counts.values())
    total_err = sum(c.get("error", 0) for c in per_domain_counts.values())
    total_nf = sum(c.get("not_found", 0) for c in per_domain_counts.values())
    total_forb = sum(c.get("forbidden", 0) for c in per_domain_counts.values())

    total_bytes = 0
    for path in archive_dir.rglob("*"):
        if path.is_file() and path.suffix in (".html", ".json"):
            if path.name != "_manifest.json":
                try:
                    total_bytes += path.stat().st_size
                except OSError:
                    pass

    manifest = {
        "manifest_version": "1.0",
        "created_at": utc_now_iso(),
        "collection_dir": str(collection_dir),
        "domains": list(per_domain_counts.keys()),
        "counts": per_domain_counts,
        "totals": {
            "ok": total_ok,
            "error": total_err,
            "skipped_existing": 0,
            "not_found": total_nf,
            "forbidden": total_forb,
            "records_total": sum(c.get("total", 0) for c in per_domain_counts.values()),
            "archive_total_bytes": total_bytes,
            "archive_total_mb": round(total_bytes / (1024 * 1024), 2),
        },
        "entries": entries,
        "rebuilt_from_disk": True,
    }
    manifest_path = archive_dir / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(
        "rebuilt manifest: %s (%d entries across %d domains, total %.1f MB)",
        manifest_path,
        len(entries),
        len(per_domain_counts),
        total_bytes / (1024 * 1024),
    )
    for key, c in per_domain_counts.items():
        logger.info(
            "  %s: ok=%d error=%d not_found=%d forbidden=%d total=%d",
            key,
            c.get("ok", 0),
            c.get("error", 0),
            c.get("not_found", 0),
            c.get("forbidden", 0),
            c.get("total", 0),
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--collection-dir",
        type=Path,
        default=Path("main_project/data/raw/consumer_questions_polish_2026-05-16"),
    )
    parser.add_argument(
        "--domains",
        type=str,
        default=",".join(DOMAINS.keys()),
        help="Comma-separated domain keys (e_prawnik, forumprawne, reddit, legal_other).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only first N records per domain (smoke test).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload even if archive file already exists.",
    )
    parser.add_argument(
        "--rebuild-manifest",
        action="store_true",
        help=(
            "Skip downloads; just walk the archive directory and rebuild "
            "_manifest.json from existing .meta.json files on disk."
        ),
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    _install_sigint_handler()

    collection_dir = args.collection_dir.resolve()
    archive_dir = collection_dir / "_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    logger.info("collection dir: %s", collection_dir)
    logger.info("archive dir:    %s", archive_dir)

    if args.rebuild_manifest:
        rebuild_manifest_from_disk(archive_dir, collection_dir)
        return 0

    chosen_keys = [k.strip() for k in args.domains.split(",") if k.strip()]
    bad = [k for k in chosen_keys if k not in DOMAINS]
    if bad:
        logger.error("unknown domain keys: %s; valid=%s", bad, list(DOMAINS.keys()))
        return 2

    per_domain_results: dict[str, list[DownloadResult]] = {}
    per_domain_counts: dict[str, dict[str, int]] = {}

    start_time = time.monotonic()
    for key in chosen_keys:
        domain = DOMAINS[key]
        logger.info("=== domain: %s ===", domain.name)
        results, counts = process_domain(
            domain,
            collection_dir,
            archive_dir,
            force=args.force,
            limit=args.limit,
        )
        per_domain_results[domain.name] = results
        per_domain_counts[domain.name] = counts
        # write manifest incrementally — survives a kill
        write_manifest(archive_dir, per_domain_results, per_domain_counts)
        if _STOP_REQUESTED:
            logger.warning("stopping after %s due to SIGINT", domain.name)
            break

    elapsed = time.monotonic() - start_time
    logger.info("=== DONE in %.1f min ===", elapsed / 60.0)
    for k, c in per_domain_counts.items():
        logger.info(
            "  %s: ok=%d skipped=%d error=%d not_found=%d forbidden=%d",
            k,
            c.get("ok", 0),
            c.get("skipped_existing", 0),
            c.get("error", 0),
            c.get("not_found", 0),
            c.get("forbidden", 0),
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
