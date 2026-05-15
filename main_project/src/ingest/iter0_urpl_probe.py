"""Iteracja 0a feasibility probe — URPL RPL XML + ChPL/Ulotka endpoints.

Tests pre-conditions #2-#6 z sources_catalog.md § Iteracja 0:
  #2 XML parse-ability (100% valid)
  #3 ChPL endpoint response time (p95 <2s)
  #4 Ulotka endpoint response time (p95 <2s)
  #5 ChPL↔Ulotka alignment rate (≥90%, competence-stratified spot-check separately)
  #6 OCR overhead (<15% scanned)

Pre-condition #1 (24h uptime SLA) — separate script `iter0_uptime_probe.py`.

Usage:
    uv run python -m ingest.iter0_urpl_probe \\
        --config configs/sampling.yaml \\
        --output-dir ../thesis_research/iter0_feasibility \\
        --urpl-xml-url <URL>  # from manual recon

Output:
    {output_dir}/results.json                   — structured metrics + per-product
    {output_dir}/sample-list-{date}.csv         — sample of productIDs (DVC trackable)
    {output_dir}/spot-check-psych-N05N06-{date}.csv — 10 psych pairs (manual review)
    {output_dir}/rpl-snapshot-{date}.xml        — XML snapshot (DVC trackable)
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import random
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pdfplumber
import requests
import yaml

logger = logging.getLogger(__name__)

CHPL_ENDPOINT_TEMPLATE = (
    "https://rejestrymedyczne.ezdrowie.gov.pl/api/rpl/medicinal-products/"
    "{product_id}/characteristic"
)
ULOTKA_ENDPOINT_TEMPLATE = (
    "https://rejestrymedyczne.ezdrowie.gov.pl/api/rpl/medicinal-products/"
    "{product_id}/leaflet"
)

PSYCH_ATC_PREFIXES: tuple[str, ...] = ("N05", "N06")
OCR_TEXT_MIN_CHARS = 100
ALIGNMENT_DATE_TOLERANCE_DAYS = 1
REQUEST_TIMEOUT_SEC = 30.0
USER_AGENT = "Mozilla/5.0 (URPL feasibility probe — MgSochacka PJATK thesis)"


@dataclass
class SampleEntry:
    product_id: str
    atc_code: str
    data_modyfikacji_chpl: str | None = None
    name: str = ""


@dataclass
class ProbeResult:
    product_id: str
    atc_code: str
    chpl_status: int | None = None
    chpl_time_sec: float | None = None
    chpl_pdf_size_bytes: int | None = None
    chpl_text_length: int | None = None
    chpl_data_modyfikacji: str | None = None
    chpl_error: str | None = None
    ulotka_status: int | None = None
    ulotka_time_sec: float | None = None
    ulotka_pdf_size_bytes: int | None = None
    ulotka_data_modyfikacji: str | None = None
    ulotka_error: str | None = None
    alignment_ok: bool = False
    text_layer_ok: bool = False


def configure_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}
    with config_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def download_rpl_xml(url: str, dest: Path) -> Path:
    logger.info("Downloading URPL RPL XML feed: %s", url)
    response = requests.get(
        url, timeout=REQUEST_TIMEOUT_SEC, headers={"User-Agent": USER_AGENT}
    )
    response.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(response.content)
    logger.info("Saved %d bytes to %s", len(response.content), dest)
    return dest


def parse_xml(xml_path: Path) -> tuple[bool, str | None, list[SampleEntry]]:
    """Pre-condition #2: parse XML, extract product list.

    Heurystyka schema discovery — actual URPL element names TBD na podstawie XML inspection.
    Po pierwszym dry-run otwórz snapshot, sprawdź element names, adjust if needed.

    Returns (parse_ok, error_message, entries).
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as exc:
        return False, str(exc), []

    entries: list[SampleEntry] = []
    for elem in root.iter():
        product_id = (
            elem.findtext("productId")
            or elem.findtext("id")
            or elem.attrib.get("productId")
            or elem.attrib.get("id")
        )
        atc_code = (
            elem.findtext("atcCode")
            or elem.findtext("atc")
            or elem.attrib.get("atcCode")
            or ""
        )
        if product_id and atc_code:
            entries.append(
                SampleEntry(
                    product_id=str(product_id).strip(),
                    atc_code=str(atc_code).strip().upper(),
                    data_modyfikacji_chpl=(
                        elem.findtext("dataModyfikacji")
                        or elem.findtext("modificationDate")
                    ),
                    name=elem.findtext("name") or elem.findtext("productName") or "",
                )
            )
    logger.info("Parsed %d product entries from XML", len(entries))
    return True, None, entries


def stratified_sample(
    entries: list[SampleEntry], seed: int, sample_size: int, spot_check_size: int
) -> tuple[list[SampleEntry], list[SampleEntry]]:
    """Returns (random_sample, psych_spot_check).

    random_sample: `sample_size` random across all ATC classes (#3-#6 automation)
    psych_spot_check: `spot_check_size` from psych N05/N06 subset for manual review

    Per DEC-001 § Eval set + sources_catalog § Sprawdzanie pairing integrity (competence-stratified).
    """
    rng = random.Random(seed)
    sample = rng.sample(entries, min(sample_size, len(entries)))

    psych_pool = [e for e in entries if e.atc_code[:3] in PSYCH_ATC_PREFIXES]
    psych_in_sample = [e for e in sample if e.atc_code[:3] in PSYCH_ATC_PREFIXES]

    if len(psych_in_sample) >= spot_check_size:
        spot_check = rng.sample(psych_in_sample, spot_check_size)
    else:
        needed = spot_check_size - len(psych_in_sample)
        extra_pool = [e for e in psych_pool if e not in psych_in_sample]
        extra = rng.sample(extra_pool, min(needed, len(extra_pool)))
        spot_check = list(psych_in_sample) + extra

    return sample, spot_check


def probe_endpoint(url: str) -> tuple[int | None, float | None, bytes | None, str | None]:
    """Returns (status_code, elapsed_sec, content_bytes, error_msg)."""
    t0 = time.monotonic()
    try:
        response = requests.get(
            url, timeout=REQUEST_TIMEOUT_SEC, headers={"User-Agent": USER_AGENT}
        )
    except requests.RequestException as exc:
        return None, time.monotonic() - t0, None, str(exc)
    elapsed = time.monotonic() - t0
    content = response.content if response.ok else None
    return response.status_code, elapsed, content, None


def detect_text_layer(pdf_bytes: bytes | None) -> tuple[bool, int]:
    """Pre-condition #6: returns (has_text_layer, text_length).

    Heurystyka: first 3 pages, threshold OCR_TEXT_MIN_CHARS znaków na stripped text.
    """
    if not pdf_bytes:
        return False, 0
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = "".join((page.extract_text() or "") for page in pdf.pages[:3])
    except Exception as exc:
        logger.warning("pdfplumber failed: %s", exc)
        return False, 0
    text_length = len(text.strip())
    return text_length >= OCR_TEXT_MIN_CHARS, text_length


def days_between(d1: str | None, d2: str | None) -> int | None:
    if not d1 or not d2:
        return None
    try:
        dt1 = datetime.fromisoformat(d1[:10])
        dt2 = datetime.fromisoformat(d2[:10])
    except ValueError:
        return None
    return abs((dt1 - dt2).days)


def probe_product(entry: SampleEntry) -> ProbeResult:
    result = ProbeResult(product_id=entry.product_id, atc_code=entry.atc_code)

    chpl_url = CHPL_ENDPOINT_TEMPLATE.format(product_id=entry.product_id)
    status, elapsed, content, err = probe_endpoint(chpl_url)
    result.chpl_status = status
    result.chpl_time_sec = elapsed
    result.chpl_error = err
    if content:
        result.chpl_pdf_size_bytes = len(content)
        has_text, text_len = detect_text_layer(content)
        result.text_layer_ok = has_text
        result.chpl_text_length = text_len
    result.chpl_data_modyfikacji = entry.data_modyfikacji_chpl

    ulotka_url = ULOTKA_ENDPOINT_TEMPLATE.format(product_id=entry.product_id)
    status, elapsed, content, err = probe_endpoint(ulotka_url)
    result.ulotka_status = status
    result.ulotka_time_sec = elapsed
    result.ulotka_error = err
    if content:
        result.ulotka_pdf_size_bytes = len(content)
    # data_modyfikacji Ulotki: TODO — moze byc w response headers (Last-Modified) lub
    # w osobnym XML metadata. Po recon dostosuj.

    align_status_ok = result.chpl_status == 200 and result.ulotka_status == 200
    align_pdf_ok = bool(result.chpl_pdf_size_bytes) and bool(result.ulotka_pdf_size_bytes)
    date_delta = days_between(result.chpl_data_modyfikacji, result.ulotka_data_modyfikacji)
    align_date_ok = date_delta is None or date_delta <= ALIGNMENT_DATE_TOLERANCE_DAYS
    result.alignment_ok = align_status_ok and align_pdf_ok and align_date_ok

    return result


def aggregate(results: list[ProbeResult]) -> dict[str, Any]:
    chpl_times = [r.chpl_time_sec for r in results if r.chpl_time_sec is not None]
    ulotka_times = [r.ulotka_time_sec for r in results if r.ulotka_time_sec is not None]
    alignments = [r.alignment_ok for r in results]
    text_layers = [r.text_layer_ok for r in results]

    text_rate = sum(text_layers) / len(text_layers) if text_layers else 0.0
    return {
        "n_sample": len(results),
        "chpl_p50_sec": float(np.percentile(chpl_times, 50)) if chpl_times else None,
        "chpl_p95_sec": float(np.percentile(chpl_times, 95)) if chpl_times else None,
        "ulotka_p50_sec": float(np.percentile(ulotka_times, 50)) if ulotka_times else None,
        "ulotka_p95_sec": float(np.percentile(ulotka_times, 95)) if ulotka_times else None,
        "alignment_rate": sum(alignments) / len(alignments) if alignments else 0.0,
        "text_layer_rate": text_rate,
        "ocr_overhead_rate": 1.0 - text_rate if text_layers else 0.0,
    }


def evaluate_preconditions(
    aggregated: dict[str, Any], parse_ok: bool
) -> dict[str, dict[str, Any]]:
    def verdict_p95(value: float | None, success: float, warning: float) -> str:
        if value is None:
            return "FAIL"
        if value < success:
            return "PASS"
        if value < warning:
            return "WARN"
        return "FAIL"

    align = aggregated["alignment_rate"]
    ocr = aggregated["ocr_overhead_rate"]

    return {
        "pre_2_xml_parse": {
            "threshold": "100% valid",
            "value": parse_ok,
            "result": "PASS" if parse_ok else "FAIL",
        },
        "pre_3_chpl_p95": {
            "threshold": "<2s p95 (warn band 2-5s)",
            "value": aggregated["chpl_p95_sec"],
            "result": verdict_p95(aggregated["chpl_p95_sec"], 2.0, 5.0),
        },
        "pre_4_ulotka_p95": {
            "threshold": "<2s p95 (warn band 2-5s)",
            "value": aggregated["ulotka_p95_sec"],
            "result": verdict_p95(aggregated["ulotka_p95_sec"], 2.0, 5.0),
        },
        "pre_5_alignment": {
            "threshold": "≥90% (warn band 80-89%, kill <80%)",
            "value": align,
            "result": "PASS" if align >= 0.90 else ("WARN" if align >= 0.80 else "FAIL"),
        },
        "pre_6_ocr_overhead": {
            "threshold": "<15% (warn band 15-24%, kill >25%)",
            "value": ocr,
            "result": "PASS" if ocr < 0.15 else ("WARN" if ocr < 0.25 else "FAIL"),
        },
    }


def kill_criteria_check(
    evaluations: dict[str, dict[str, Any]], aggregated: dict[str, Any]
) -> dict[str, Any]:
    """Kill criteria per sources_catalog.md § Iteracja 0:
    ≥2 FAIL, LUB OCR>25%, LUB alignment<80%.
    """
    fails = sum(1 for e in evaluations.values() if e["result"] == "FAIL")
    triggers: list[str] = []
    if fails >= 2:
        triggers.append(f"≥2 pre-conditions FAIL (got {fails})")
    ocr = aggregated["ocr_overhead_rate"]
    if ocr is not None and ocr > 0.25:
        triggers.append(f"OCR overhead >25% (got {ocr:.1%})")
    align = aggregated["alignment_rate"]
    if align is not None and align < 0.80:
        triggers.append(f"Alignment <80% (got {align:.1%})")
    return {"kill_activated": bool(triggers), "triggers": triggers, "fail_count": fails}


def write_sample_csv(entries: list[SampleEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "product_id",
                "atc_code",
                "atc_level1",
                "is_psych_N05_N06",
                "name",
                "data_modyfikacji_chpl",
            ]
        )
        for entry in entries:
            writer.writerow(
                [
                    entry.product_id,
                    entry.atc_code,
                    entry.atc_code[:1] if entry.atc_code else "",
                    "yes" if entry.atc_code[:3] in PSYCH_ATC_PREFIXES else "no",
                    entry.name,
                    entry.data_modyfikacji_chpl or "",
                ]
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/sampling.yaml"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../thesis_research/iter0_feasibility"),
    )
    parser.add_argument(
        "--urpl-xml-url",
        type=str,
        default=None,
        help="URPL RPL XML feed URL. Override config. Required if not in config.",
    )
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--spot-check-size", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit endpoint probes to first N entries (smoke test).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse XML + sample only, skip endpoint probing.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    configure_logging(args.verbose)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(args.config)
    url = args.urpl_xml_url or config.get("urpl_xml_url")
    if not url:
        logger.error(
            "URPL XML URL not provided. Set 'urpl_xml_url' in %s or pass --urpl-xml-url",
            args.config,
        )
        return 2

    today = datetime.now().strftime("%Y-%m-%d")
    xml_path = args.output_dir / f"rpl-snapshot-{today}.xml"

    download_rpl_xml(url, xml_path)
    parse_ok, parse_err, entries = parse_xml(xml_path)
    logger.info("Parse OK: %s; entries: %d", parse_ok, len(entries))
    if parse_err:
        logger.error("Parse error: %s", parse_err)
    if not entries:
        logger.error(
            "No entries parsed — schema discovery needed. Inspect XML at %s manually, "
            "adjust parse_xml() heuristics (element names, namespaces).",
            xml_path,
        )
        return 3

    sample, spot_check = stratified_sample(
        entries, seed=args.seed, sample_size=args.sample_size, spot_check_size=args.spot_check_size
    )
    sample_csv = args.output_dir / f"sample-list-{today}.csv"
    spot_csv = args.output_dir / f"spot-check-psych-N05N06-{today}.csv"
    write_sample_csv(sample, sample_csv)
    write_sample_csv(spot_check, spot_csv)
    logger.info(
        "Wrote %s (%d entries) + %s (%d psych spot-check entries)",
        sample_csv,
        len(sample),
        spot_csv,
        len(spot_check),
    )

    if args.dry_run:
        logger.info("--dry-run: skipping endpoint probes")
        return 0

    probe_list = sample[: args.limit] if args.limit else sample
    results: list[ProbeResult] = []
    for i, entry in enumerate(probe_list, 1):
        logger.info(
            "[%d/%d] Probing productID=%s ATC=%s",
            i,
            len(probe_list),
            entry.product_id,
            entry.atc_code,
        )
        results.append(probe_product(entry))

    aggregated = aggregate(results)
    evaluations = evaluate_preconditions(aggregated, parse_ok)
    kill = kill_criteria_check(evaluations, aggregated)

    output = {
        "metadata": {
            "run_at": datetime.now().isoformat(),
            "seed": args.seed,
            "sample_size_requested": args.sample_size,
            "sample_size_probed": len(results),
            "urpl_xml_url": url,
            "snapshot_xml": str(xml_path),
        },
        "preconditions": evaluations,
        "kill_criteria": kill,
        "aggregated_metrics": aggregated,
        "per_product_results": [asdict(r) for r in results],
    }

    results_path = args.output_dir / "results.json"
    results_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info("Wrote %s", results_path)

    _print_summary(evaluations, kill, len(entries), len(sample), len(spot_check), results_path, sample_csv, spot_csv)
    return 0


def _print_summary(
    evaluations: dict[str, dict[str, Any]],
    kill: dict[str, Any],
    n_entries: int,
    n_sample: int,
    n_spot_check: int,
    results_path: Path,
    sample_csv: Path,
    spot_csv: Path,
) -> None:
    print("\n=== Iteracja 0a phase 1 — Feasibility probe results ===")
    print(f"Parsed entries: {n_entries}")
    print(f"Sample size: {n_sample} (+ {n_spot_check} psych spot-check)")
    print("\nPre-conditions:")
    for key, ev in evaluations.items():
        val = ev["value"]
        if isinstance(val, float) and abs(val) <= 10:
            val_str = f"{val:.1%}" if abs(val) <= 1 else f"{val:.2f}"
        else:
            val_str = str(val)
        print(f"  {key}: {ev['result']:5} (threshold {ev['threshold']}, got {val_str})")
    print(f"\nKill criteria activated: {kill['kill_activated']}")
    if kill["triggers"]:
        print("Triggers:")
        for trigger in kill["triggers"]:
            print(f"  - {trigger}")
    print(f"\nArtefakty:")
    print(f"  results.json:   {results_path}")
    print(f"  sample list:    {sample_csv}")
    print(f"  spot-check:     {spot_csv}  (manual review)")
    print("\nNastępne kroki:")
    print("  1. Przejrzyj results.json + sample-list CSV (atc distribution sanity)")
    print("  2. Manualnie spot-check 10 par z psych subset (ChPL sekcja 4.1 vs Ulotka sekcja 1)")
    print("  3. Uruchom `iter0_uptime_probe.py` w background dla 24h SLA (pre-condition #1)")
    print("  4. Wypełnij iteration-0-feasibility-report.md template")


if __name__ == "__main__":
    sys.exit(main())
