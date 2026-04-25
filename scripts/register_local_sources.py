#!/usr/bin/env python3
"""Register already downloaded source files into manifest/sidecar structure.

Workaround for restricted network environments: user can provide files manually
and this script builds auditable metadata expected by the project pipeline.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import shutil
from datetime import UTC, datetime

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".html", ".htm"}


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        csv.writer(handle).writerow(row)


def load_seed_map(seeds_csv: pathlib.Path) -> dict[str, dict[str, str]]:
    if not seeds_csv.exists():
        return {}
    with seeds_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {r.get("eli_id", "").strip(): r for r in rows if r.get("eli_id")}


def detect_content_type(ext: str) -> str:
    return {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".html": "text/html",
        ".htm": "text/html",
    }.get(ext, "application/octet-stream")


def main() -> int:
    parser = argparse.ArgumentParser(description="Register local sources into sidecars + manifest")
    parser.add_argument("--input-dir", type=pathlib.Path, required=True, help="Folder with local files to register")
    parser.add_argument("--raw-dir", type=pathlib.Path, default=pathlib.Path("data/raw/legislation"))
    parser.add_argument("--manifest", type=pathlib.Path, default=pathlib.Path("data/manifests/manifest_l1.csv"))
    parser.add_argument("--seeds", type=pathlib.Path, default=pathlib.Path("data/seeds/l1_legislation.csv"))
    parser.add_argument("--layer", default="L1")
    parser.add_argument("--topic-group", default="manual_import")
    args = parser.parse_args()

    if not args.input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {args.input_dir}")

    seed_map = load_seed_map(args.seeds)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    ensure_manifest_header(args.manifest)

    files = sorted([p for p in args.input_dir.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS])
    if not files:
        print("No supported files found (.pdf/.docx/.html/.htm).")
        return 0

    for src in files:
        ext = src.suffix.lower()
        doc_id = src.stem
        seed = seed_map.get(doc_id, {})
        eli_id = seed.get("eli_id", doc_id)
        title = seed.get("title", doc_id)
        layer = seed.get("layer", args.layer)
        topic_group = seed.get("topic_group", args.topic_group)
        source_url = seed.get("url", "local://manual-import")

        target_file = args.raw_dir / src.name
        shutil.copy2(src, target_file)

        file_hash = sha256_file(target_file)
        file_size = target_file.stat().st_size
        downloaded_at = datetime.now(UTC).isoformat()
        content_type = detect_content_type(ext)

        sidecar_path = args.raw_dir / f"{doc_id}.json"
        sidecar = {
            "doc_id": doc_id,
            "eli_id": eli_id,
            "title": title,
            "layer": layer,
            "topic_group": topic_group,
            "source_url": source_url,
            "downloaded_at_utc": downloaded_at,
            "http_status": 200,
            "content_type": content_type,
            "content_length": file_size,
            "sha256": file_hash,
            "attempts": 1,
            "local_path": target_file.as_posix(),
            "import_mode": "manual_local_register",
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
                source_url,
                downloaded_at,
                "200",
                content_type,
                str(file_size),
                file_hash,
                target_file.as_posix(),
                sidecar_path.as_posix(),
            ],
        )
        print(f"[OK] Registered {src.name} -> {target_file}")

    print(f"Registered {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
