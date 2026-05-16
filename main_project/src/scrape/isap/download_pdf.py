"""Downloader oryginalnych PDF Dziennika Ustaw dla ustaw konsumenckich.

Cel: canonical PDF source side-by-side z XML/HTML scrape (`scrape_eli.py`).
Defense argument: Dziennik Ustaw PDF jest official Government of Poland
publication, XML/HTML jest representation. Cross-check XML vs PDF dla
deterministic citation alignment.

Endpoints (in priority order):
  1. `https://api.sejm.gov.pl/eli/acts/{ELI}/text.pdf` (consolidated/announce.)
  2. `https://api.sejm.gov.pl/eli/acts/{ELI}/text/T/D{YYYY}{NNNNNNN}L.pdf` (tekst jednolity)
  3. Per consolidated_text_references — pojedyncze późniejsze obwieszczenia

Storage layout:
  data/raw/eli_pdf_2026-05-16/
    DU_2014_827/
      text.pdf                                   # primary announcement PDF
      tekst_jednolity_2024_1796.pdf              # opcjonalnie jeśli istnieje
      meta.json                                  # rozmiar, sha256, source_url etc.

Per-PDF meta.json schema:
  {
    "ustawa_id": "DU/2014/827",
    "kind": "announcement" | "tekst_jednolity",
    "consolidated_ref": "DU/2024/1796" | null,
    "source_url": "https://...",
    "size_bytes": 659246,
    "sha256": "...",
    "download_date": "2026-05-16",
    "error": false | true,
    "error_msg": null | "..."
  }

Usage:
    uv run python -m src.scrape.isap.download_pdf            # wszystkie
    uv run python -m src.scrape.isap.download_pdf --ustawa DU/2014/827
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ELI_BASE = "https://api.sejm.gov.pl/eli/acts"
USER_AGENT = "ELI corpus collector - MgSochacka PJATK thesis (citation-grounded RAG)"
REQUEST_TIMEOUT_SEC = 60.0  # PDFs są duże
INTER_REQUEST_DELAY_SEC = 1.0  # polite — 1 req/sec per scope brief
DOWNLOAD_DATE = "2026-05-16"


@dataclass(frozen=True)
class PdfTarget:
    """Ustawa do pobrania PDF."""

    ustawa_id: str  # "DU/2014/827"
    title_short: str  # human-readable label


# Existing 6 ustaw — primary PDF download targets (Część A z briefu)
EXISTING_USTAWY: tuple[PdfTarget, ...] = (
    PdfTarget("DU/2014/827", "Ustawa o prawach konsumenta (UPK)"),
    PdfTarget("DU/1964/93", "Kodeks cywilny (KC)"),
    PdfTarget("DU/2007/1206", "Ust. o przeciwdziałaniu nieuczciwym praktykom rynkowym"),
    PdfTarget("DU/2007/331", "Ust. o ochronie konkurencji i konsumentów"),
    PdfTarget("DU/2011/1175", "Ust. o usługach płatniczych"),
    PdfTarget("DU/2016/1823", "Ust. o pozasądowym rozwiązywaniu sporów konsumenckich"),
)

# 5 nowych ustaw (Część B z briefu) — także PDF
NEW_USTAWY: tuple[PdfTarget, ...] = (
    PdfTarget("DU/1997/939", "Prawo bankowe"),
    PdfTarget("DU/2002/1204", "Ust. o świadczeniu usług drogą elektroniczną"),
    PdfTarget("DU/2024/1221", "Prawo komunikacji elektronicznej"),
    PdfTarget("DU/2011/715", "Ust. o kredycie konsumenckim"),
    PdfTarget("DU/2010/44", "Ust. o dochodzeniu roszczeń w postępowaniu grupowym"),
)

# 8 extra ustaw konsumenckich (Iter. 0b ext. #2, S7 2026-05-16)
# IDs zweryfikowane via ELI search — brief Magdy miał błędne 4 z 8 (Pr. upadlosciowe,
# bezp. produktów, zwalcz. nieucz. konkur., sprzedaż konsumencka).
EXTRA_USTAWY: tuple[PdfTarget, ...] = (
    PdfTarget("DU/1964/296", "Kodeks postępowania cywilnego (KPC)"),
    PdfTarget("DU/2003/535", "Prawo upadłościowe (z upadłością konsumencką)"),
    PdfTarget("DU/2014/915", "Ust. o informowaniu o cenach towarów i usług"),
    PdfTarget("DU/2003/2275", "Ust. o ogólnym bezpieczeństwie produktów (UCHYLONA, historic)"),
    PdfTarget("DU/1993/211", "Ust. o zwalczaniu nieuczciwej konkurencji"),
    PdfTarget("DU/2002/1176", "Ust. o szczeg. warunkach sprzedaży konsumenckiej (UCHYLONA, historic)"),
    PdfTarget("DU/2000/271", "Ust. o ochronie niektórych praw konsumentów (UCHYLONA, historic)"),
    PdfTarget("DU/1997/483", "Konstytucja RP"),
)


def http_get(url: str, *, accept: str = "*/*") -> tuple[int, bytes, str]:
    """HTTP GET. Zwraca (status, body, content_type). Raise on network errors."""
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": accept}
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SEC) as response:
            return (
                response.status,
                response.read(),
                response.headers.get("Content-Type", ""),
            )
    except urllib.error.HTTPError as exc:
        return exc.code, b"", str(exc.reason)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error for {url}: {exc.reason}") from exc


def fetch_metadata(ustawa_id: str) -> dict[str, Any]:
    pub, yr, num = ustawa_id.split("/")
    url = f"{ELI_BASE}/{pub}/{yr}/{num}"
    s, body, _ = http_get(url, accept="application/json")
    if s != 200:
        raise RuntimeError(f"meta fetch failed {s} for {url}")
    return json.loads(body.decode("utf-8"))


def candidate_pdf_urls(
    ustawa_id: str, meta: dict[str, Any]
) -> list[tuple[str, str, str | None]]:
    """Zwróć listę kandydatów PDF: (url, kind, consolidated_ref).

    Kind: 'announcement' (oryginalny) | 'tekst_jednolity' (later konsolidacja).
    """
    pub, yr, num = ustawa_id.split("/")
    out: list[tuple[str, str, str | None]] = []
    # Primary — announcement PDF z głównego endpoint
    out.append((f"{ELI_BASE}/{pub}/{yr}/{num}/text.pdf", "announcement", None))

    # Tekst jednolity refs (opcjonalne — najnowszy konsolidat)
    refs = meta.get("references", {})
    if isinstance(refs, dict):
        tj_refs = refs.get("Inf. o tekście jednolitym", [])
        if tj_refs and isinstance(tj_refs, list):
            # Bierzemy NAJNOWSZY (pierwszy w liście wg ELI ordering)
            tj_id = tj_refs[0].get("id") if isinstance(tj_refs[0], dict) else None
            if tj_id and "/" in tj_id:
                tj_pub, tj_yr, tj_pos = tj_id.split("/")
                tj_url = f"{ELI_BASE}/{tj_pub}/{tj_yr}/{tj_pos}/text.pdf"
                out.append((tj_url, "tekst_jednolity", tj_id))

    return out


def sha256_hex(blob: bytes) -> str:
    h = hashlib.sha256()
    h.update(blob)
    return h.hexdigest()


def download_one(target: PdfTarget, output_root: Path) -> dict[str, Any]:
    """Pobierz wszystkie PDF dla jednej ustawy. Zwróć summary dict."""
    safe_id = target.ustawa_id.replace("/", "_")
    out_dir = output_root / safe_id
    out_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "ustawa_id": target.ustawa_id,
        "title_short": target.title_short,
        "files": [],
        "errors": [],
    }

    try:
        meta = fetch_metadata(target.ustawa_id)
        time.sleep(INTER_REQUEST_DELAY_SEC)
    except RuntimeError as exc:
        logger.error("Meta fetch failed for %s: %s", target.ustawa_id, exc)
        summary["errors"].append({"step": "metadata", "msg": str(exc)})
        return summary

    summary["title_full"] = meta.get("title", "?")
    summary["display_address"] = meta.get("displayAddress", "?")
    summary["in_force"] = meta.get("inForce", "?")

    candidates = candidate_pdf_urls(target.ustawa_id, meta)
    logger.info("Trying %d PDF candidates for %s", len(candidates), target.ustawa_id)

    for url, kind, consolidated_ref in candidates:
        fname = "text.pdf" if kind == "announcement" else f"tekst_jednolity_{(consolidated_ref or '').replace('/','_')}.pdf"
        pdf_path = out_dir / fname
        meta_path = out_dir / f"{fname}.meta.json"

        if pdf_path.exists() and meta_path.exists():
            logger.info("Already exists, skip: %s", pdf_path)
            summary["files"].append({"path": str(pdf_path), "kind": kind, "status": "exists"})
            continue

        logger.info("Downloading %s [%s]", url, kind)
        try:
            status, body, ct = http_get(url, accept="application/pdf")
        except RuntimeError as exc:
            logger.warning("Network error: %s", exc)
            summary["errors"].append({"url": url, "kind": kind, "msg": str(exc)})
            time.sleep(INTER_REQUEST_DELAY_SEC)
            continue

        if status != 200 or "pdf" not in ct.lower():
            logger.warning(
                "Bad response %s ct=%s sz=%d for %s", status, ct, len(body), url
            )
            summary["errors"].append(
                {"url": url, "kind": kind, "status": status, "content_type": ct}
            )
            time.sleep(INTER_REQUEST_DELAY_SEC)
            continue

        # Sanity: PDF header check
        if not body.startswith(b"%PDF"):
            logger.warning("Body not starting with %%PDF for %s", url)
            summary["errors"].append({"url": url, "kind": kind, "msg": "not_pdf_header"})
            time.sleep(INTER_REQUEST_DELAY_SEC)
            continue

        pdf_path.write_bytes(body)
        sha = sha256_hex(body)
        pdf_meta: dict[str, Any] = {
            "ustawa_id": target.ustawa_id,
            "ustawa_title": meta.get("title"),
            "kind": kind,
            "consolidated_ref": consolidated_ref,
            "source_url": url,
            "size_bytes": len(body),
            "sha256": sha,
            "download_date": DOWNLOAD_DATE,
            "user_agent": USER_AGENT,
            "license": "Art. 4 ust. 1 ustawy o prawie autorskim (DU/1994/83) — akty normatywne public domain",
            "in_force_at_download": meta.get("inForce"),
            "error": False,
        }
        meta_path.write_text(
            json.dumps(pdf_meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Wrote %s (%d bytes, sha=%s)", pdf_path, len(body), sha[:16])

        summary["files"].append(
            {
                "path": str(pdf_path),
                "kind": kind,
                "size_bytes": len(body),
                "sha256": sha,
                "status": "downloaded",
            }
        )
        time.sleep(INTER_REQUEST_DELAY_SEC)

    return summary


def configure_logging(verbose: bool = False) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ustawa",
        type=str,
        default=None,
        help='ID jednej ustawy (np. "DU/2014/827"). Domyślnie: wszystkie 11.',
    )
    parser.add_argument(
        "--scope",
        choices=("all", "existing", "new", "extra"),
        default="all",
        help="all=19 ustaw, existing=6 (Iter. 0a), new=5 (Iter. 0b Część B), extra=8 (S7 2026-05-16)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(f"main_project/data/raw/eli_pdf_{DOWNLOAD_DATE}"),
        help="Katalog wyjściowy (domyślnie data/raw/eli_pdf_{date}/).",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    configure_logging(args.verbose)

    targets: list[PdfTarget]
    if args.ustawa:
        all_targets = list(EXISTING_USTAWY) + list(NEW_USTAWY) + list(EXTRA_USTAWY)
        targets = [t for t in all_targets if t.ustawa_id == args.ustawa]
        if not targets:
            logger.error("Nieznana ustawa: %s", args.ustawa)
            return 2
    elif args.scope == "existing":
        targets = list(EXISTING_USTAWY)
    elif args.scope == "new":
        targets = list(NEW_USTAWY)
    elif args.scope == "extra":
        targets = list(EXTRA_USTAWY)
    else:
        targets = list(EXISTING_USTAWY) + list(NEW_USTAWY) + list(EXTRA_USTAWY)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, Any]] = []
    for target in targets:
        logger.info("=" * 60)
        logger.info("PDF DOWNLOAD: %s — %s", target.ustawa_id, target.title_short)
        logger.info("=" * 60)
        summary = download_one(target, args.output_dir)
        summaries.append(summary)

    # Aggregate summary
    out_summary_path = args.output_dir / "_download_summary.json"
    out_summary = {
        "download_date": DOWNLOAD_DATE,
        "user_agent": USER_AGENT,
        "total_ustaw": len(summaries),
        "total_files": sum(len(s.get("files", [])) for s in summaries),
        "total_errors": sum(len(s.get("errors", [])) for s in summaries),
        "total_bytes": sum(
            f.get("size_bytes", 0)
            for s in summaries
            for f in s.get("files", [])
            if f.get("size_bytes")
        ),
        "ustawy": summaries,
    }
    out_summary_path.write_text(
        json.dumps(out_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\n=== PDF DOWNLOAD SUMMARY ===")
    print(f"{'ustawa_id':<14} {'files':>6} {'errors':>7} {'MB':>7}  title")
    print("-" * 100)
    for s in summaries:
        mb = sum(f.get("size_bytes", 0) for f in s.get("files", [])) / 1024 / 1024
        print(
            f"{s['ustawa_id']:<14} {len(s.get('files', [])):>6} "
            f"{len(s.get('errors', [])):>7} {mb:>7.2f}  {s.get('title_short','?')}"
        )
    print("-" * 100)
    print(
        f"TOTAL ustaw={len(summaries)} files={out_summary['total_files']} "
        f"errors={out_summary['total_errors']} bytes={out_summary['total_bytes']:,}"
        f" ({out_summary['total_bytes']/1024/1024:.2f} MB)"
    )
    print(f"\nOutput: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
