"""Shared helpers for the JDG chatbot data collection pipeline.

Responsibility split (per descriptions/data_collection_spec.md):
- discover (per-portal scripts)
- fetch (this module)
- save raw + sidecar metadata + append manifest row (this module)

No parsing, chunking, embeddings, dedup-semantic.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MANIFESTS_DIR = DATA_DIR / "manifests"
LOGS_DIR = DATA_DIR / "logs"
QUARANTINE_DIR = DATA_DIR / "quarantine"

MANIFEST_CSV = DATA_DIR / "manifest.csv"
FETCH_LOG = LOGS_DIR / "fetch_log.ndjson"
REJECTED_LOG = LOGS_DIR / "rejected_files.ndjson"

USER_AGENT = (
    "Mozilla/5.0 (compatible; AcademicResearch/1.0; "
    "+mailto:diplomma-research@example.org)"
)

MANIFEST_FIELDS = [
    "id",
    "url",
    "source",
    "topic_ids",
    "layer",
    "format",
    "fetched_at",
    "http_status",
    "content_type",
    "bytes",
    "relative_path",
    "title",
    "last_modified",
    "is_official",
    "eli_id",
    "parent_url",
    "discovery_source",
    "sha256",
    "quality_flag",
    "notes",
]

WAF_NEEDLES = (
    b"Request Rejected",
    b"Access Denied",
    b"<title>403",
    b"<title>503",
    b"<title>Just a moment",
    b"cf-error",
)


@dataclass
class FetchResult:
    url: str
    ok: bool
    status: int = 0
    content: bytes = b""
    headers: dict = field(default_factory=dict)
    error: str = ""
    retries: int = 0


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def short_id(data: bytes) -> str:
    return sha256_hex(data)[:16]


def detect_waf_block(content: bytes) -> Optional[str]:
    sniff = content[:4096]
    for needle in WAF_NEEDLES:
        if needle in sniff:
            return needle.decode("utf-8", errors="replace")
    return None


def magic_ok(content: bytes, fmt: str) -> bool:
    if fmt == "pdf":
        return content[:4] == b"%PDF"
    if fmt == "docx":
        return content[:2] == b"PK"
    if fmt in ("html", "htm", "xml"):
        sniff = content[:512].lower()
        return b"<html" in sniff or b"<!doctype html" in sniff or b"<?xml" in sniff
    if fmt == "xlsx":
        return content[:2] == b"PK"
    return True


def session_factory(extra_headers: Optional[dict] = None) -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.5",
        }
    )
    if extra_headers:
        s.headers.update(extra_headers)
    return s


def fetch(
    url: str,
    session: Optional[requests.Session] = None,
    accept: Optional[str] = None,
    timeout: int = 30,
    max_retries: int = 3,
    backoff: tuple[float, ...] = (1.0, 4.0, 16.0),
) -> FetchResult:
    """GET with retry/backoff and WAF-error detection."""
    sess = session or session_factory()
    headers = {}
    if accept:
        headers["Accept"] = accept
    last_error = ""
    for attempt in range(max_retries):
        try:
            r = sess.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            content = r.content or b""
            waf = detect_waf_block(content) if content else None
            if r.status_code == 200 and not waf:
                return FetchResult(
                    url=url,
                    ok=True,
                    status=r.status_code,
                    content=content,
                    headers=dict(r.headers),
                    retries=attempt,
                )
            last_error = f"status={r.status_code} waf={waf}"
            # 5xx and WAF-flagged 200s get retried.
            if r.status_code < 500 and not waf and r.status_code not in (429,):
                return FetchResult(
                    url=url,
                    ok=False,
                    status=r.status_code,
                    content=content,
                    headers=dict(r.headers),
                    error=last_error,
                    retries=attempt,
                )
        except requests.RequestException as exc:
            last_error = f"exc={type(exc).__name__}: {exc}"
        if attempt + 1 < max_retries:
            time.sleep(backoff[min(attempt, len(backoff) - 1)])
    return FetchResult(url=url, ok=False, error=last_error, retries=max_retries)


def append_log(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_fetch(record: dict) -> None:
    append_log(FETCH_LOG, record)


def log_rejected(record: dict) -> None:
    append_log(REJECTED_LOG, record)


def ensure_manifest_header() -> None:
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    if not MANIFEST_CSV.exists():
        with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()


def append_manifest(row: dict) -> None:
    ensure_manifest_header()
    out = {k: row.get(k, "") for k in MANIFEST_FIELDS}
    if isinstance(out.get("topic_ids"), (list, tuple, set)):
        out["topic_ids"] = ";".join(sorted(set(out["topic_ids"])))
    with MANIFEST_CSV.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(out)


def load_manifest() -> list[dict]:
    if not MANIFEST_CSV.exists():
        return []
    with MANIFEST_CSV.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def already_have(url: str = "", sha: str = "") -> bool:
    rows = load_manifest()
    for r in rows:
        if url and r.get("url") == url:
            return True
        if sha and r.get("sha256") == sha:
            return True
    return False


def save_artifact(
    *,
    content: bytes,
    rel_path: Path,
    url: str,
    source: str,
    topic_ids: Iterable[str],
    layer: str,
    fmt: str,
    http_status: int,
    content_type: str,
    title: str = "",
    last_modified: str = "",
    is_official: bool = True,
    eli_id: str = "",
    parent_url: str = "",
    discovery_source: str = "",
    headers: Optional[dict] = None,
    extra_notes: str = "",
    quality_flag: str = "accepted",
) -> dict:
    """Persist binary content + sidecar JSON, append manifest row, return manifest row."""
    full_path = DATA_DIR / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(content)

    sha = sha256_hex(content)
    sid = sha[:16]
    fetched_at = now_iso()

    sidecar = {
        "id": sid,
        "url": url,
        "source": source,
        "topic_ids": list(topic_ids),
        "layer": layer,
        "format": fmt,
        "fetched_at": fetched_at,
        "http_status": http_status,
        "content_type": content_type,
        "bytes": len(content),
        "relative_path": str(rel_path).replace("\\", "/"),
        "title": title,
        "last_modified": last_modified,
        "is_official": is_official,
        "eli_id": eli_id,
        "parent_url": parent_url,
        "discovery_source": discovery_source,
        "sha256": sha,
        "quality_flag": quality_flag,
        "notes": extra_notes,
        "headers": headers or {},
    }

    sidecar_path = full_path.with_suffix(full_path.suffix + ".meta.json")
    sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")

    row = {k: sidecar.get(k, "") for k in MANIFEST_FIELDS}
    row["topic_ids"] = ";".join(sorted(set(topic_ids)))
    append_manifest(row)
    return row


def quarantine(content: bytes, name: str, reason_dir: str, note: str) -> Path:
    target_dir = QUARANTINE_DIR / reason_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / name
    target.write_bytes(content)
    log_rejected({"name": name, "reason_dir": reason_dir, "note": note, "ts": now_iso()})
    return target
