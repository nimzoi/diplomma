#!/usr/bin/env python3
"""Collect L1 legislation PDFs for JDG knowledge base.

The script reads a CSV with seed acts and downloads PDFs with retry/backoff,
then writes one metadata JSON sidecar per file and appends a manifest row.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime

DEFAULT_UA = "Mozilla/5.0 (compatible; AcademicResearch/1.0; +mailto:research@example.com)"
DEFAULT_ACCEPT = "application/pdf"
REJECTED_MARKER = b"Request Rejected"
PDF_MAGIC = b"%PDF"


class DownloadError(RuntimeError):
    """Raised when a URL cannot be downloaded in a valid form."""


def read_seeds(seeds_path: pathlib.Path) -> list[dict[str, str]]:
    with seeds_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"eli_id", "title", "url", "layer", "topic_group"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {sorted(missing)}")
        return [row for row in reader if row.get("url")]


def fetch_pdf(url: str, user_agent: str, timeout: int) -> tuple[bytes, int, dict[str, str]]:
    headers = {"User-Agent": user_agent, "Accept": DEFAULT_ACCEPT}
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as response:  # nosec B310
        payload = response.read()
        status = getattr(response, "status", 200)
        response_headers = {k.lower(): v for k, v in response.headers.items()}
    return payload, status, response_headers


def validate_payload(payload: bytes) -> None:
    if not payload.startswith(PDF_MAGIC):
        preview = payload[:2048]
        if REJECTED_MARKER in preview:
            raise DownloadError("WAF rejection detected (Request Rejected)")
        raise DownloadError("Downloaded file is not a PDF (%PDF header missing)")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def ensure_manifest_header(path: pathlib.Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "doc_id",
                "eli_id",
                "title",
                "layer",
                "topic_group",
                "source_url",
                "downloaded_at_utc",
                "http_status",
                "content_type",
                "size_bytes",
                "sha256",
                "local_path",
                "sidecar_path",
            ]
        )


def append_manifest_row(path: pathlib.Path, row: list[str]) -> None:
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(row)


def download_with_retries(url: str, user_agent: str, timeout: int, retries: int) -> tuple[bytes, int, dict[str, str], int]:
    backoff_seconds = [1, 4, 16]
    attempts = max(1, retries)

    last_exc: Exception | None = None
    for idx in range(attempts):
        attempt_no = idx + 1
        try:
            payload, status, headers = fetch_pdf(url, user_agent=user_agent, timeout=timeout)
            validate_payload(payload)
            return payload, status, headers, attempt_no
        except (DownloadError, urllib.error.URLError, TimeoutError) as exc:
            last_exc = exc
            if attempt_no < attempts:
                sleep_for = backoff_seconds[min(idx, len(backoff_seconds) - 1)]
                time.sleep(sleep_for)
    raise DownloadError(f"Failed after {attempts} attempts: {url} ({last_exc})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download L1 legislation PDFs and metadata")
    parser.add_argument("--seeds", type=pathlib.Path, default=pathlib.Path("data/seeds/l1_legislation.csv"))
    parser.add_argument("--raw-dir", type=pathlib.Path, default=pathlib.Path("data/raw/legislation"))
    parser.add_argument("--manifest", type=pathlib.Path, default=pathlib.Path("data/manifests/manifest_l1.csv"))
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--user-agent", default=DEFAULT_UA)
    parser.add_argument("--fail-log", type=pathlib.Path, default=pathlib.Path("data/logs/l1_failures.csv"))
    args = parser.parse_args()

    seeds = read_seeds(args.seeds)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    ensure_manifest_header(args.manifest)

    ok = 0
    failed = 0

    args.fail_log.parent.mkdir(parents=True, exist_ok=True)
    if not args.fail_log.exists():
        with args.fail_log.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["doc_id", "source_url", "error", "timestamp_utc"])

    for row in seeds:
        eli_id = row["eli_id"].strip()
        title = row["title"].strip()
        layer = row["layer"].strip() or "L1"
        topic_group = row["topic_group"].strip() or "general"
        url = row["url"].strip()
        doc_id = eli_id

        pdf_path = args.raw_dir / f"{doc_id}.pdf"
        sidecar_path = args.raw_dir / f"{doc_id}.json"

        try:
            payload, status, headers, attempts = download_with_retries(
                url=url,
                user_agent=args.user_agent,
                timeout=args.timeout,
                retries=args.retries,
            )
            downloaded_at = datetime.now(UTC).isoformat()
            file_hash = sha256_bytes(payload)
            pdf_path.write_bytes(payload)

            sidecar = {
                "doc_id": doc_id,
                "eli_id": eli_id,
                "title": title,
                "layer": layer,
                "topic_group": topic_group,
                "source_url": url,
                "downloaded_at_utc": downloaded_at,
                "http_status": status,
                "content_type": headers.get("content-type", ""),
                "content_length": len(payload),
                "sha256": file_hash,
                "attempts": attempts,
                "local_path": str(pdf_path.as_posix()),
            }
            sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")

            append_manifest_row(
                args.manifest,
                [
                    doc_id,
                    eli_id,
                    title,
                    layer,
                    topic_group,
                    url,
                    downloaded_at,
                    str(status),
                    headers.get("content-type", ""),
                    str(len(payload)),
                    file_hash,
                    pdf_path.as_posix(),
                    sidecar_path.as_posix(),
                ],
            )

            ok += 1
            print(f"[OK] {doc_id} -> {pdf_path}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            err_text = str(exc)
            print(f"[ERR] {doc_id}: {err_text}", file=sys.stderr)
            with args.fail_log.open("a", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow([doc_id, url, err_text, datetime.now(UTC).isoformat()])

    print(f"Done. Success={ok}, Failed={failed}, Total={len(seeds)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
