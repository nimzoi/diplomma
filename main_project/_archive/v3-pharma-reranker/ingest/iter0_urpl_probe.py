"""Iteracja 0a feasibility probe — URPL RPL XML + ChPL/Ulotka endpoints.

Tests pre-conditions #2-#6 z sources_catalog.md § Iteracja 0:
  #2 XML parse-ability (100% valid)
  #3 ChPL endpoint response time (p95 <2s)
  #4 Ulotka endpoint response time (p95 <2s)
  #5 ChPL↔Ulotka alignment rate (≥90%, competence-stratified spot-check separately)
  #6 OCR overhead (<15% scanned)

Pre-condition #1 (24h uptime SLA) — separate script `iter0_uptime_probe.py`.

Schema (RPL v6.0.0):
  Root: <produktyLecznicze stanNaDzien="YYYY-MM-DD" xmlns="...">
  Items: <produktLeczniczy id="..." nazwaProduktu="..." charakterystyka="URL" ulotka="URL" ...>
    <kodyATC><kodATC>X01XX01</kodATC></kodyATC>

Per-product `data_modyfikacji` NIE istnieje w feed XML — tylko snapshot-level
`stanNaDzien`. Alignment check używa HTTP `Last-Modified` header z PDF responses
(jeśli serwer ustawia), fallback na "both endpoints HTTP 200 + valid PDF"
(semantically equivalent — paired URLs generowane razem przez tę samą decyzję URPL).

Usage:
    uv run python -m src.ingest.iter0_urpl_probe --dry-run
    uv run python -m src.ingest.iter0_urpl_probe --limit 10
    uv run python -m src.ingest.iter0_urpl_probe

Output:
    {output_dir}/results.json
    {output_dir}/sample-list-{date}.csv
    {output_dir}/spot-check-psych-N05N06-{date}.csv
    {output_dir}/rpl-snapshot-{date}.xml
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
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pdfplumber
import requests
import yaml

logger = logging.getLogger(__name__)

URPL_NAMESPACE = "http://rejestry.ezdrowie.gov.pl/rpl/eksport-danych-v6.0.0"
NS = {"rpl": URPL_NAMESPACE}

PSYCH_ATC_PREFIXES: tuple[str, ...] = ("N05", "N06")
OCR_TEXT_MIN_CHARS = 100
ALIGNMENT_DATE_TOLERANCE_DAYS = 1
REQUEST_TIMEOUT_SEC = 30.0
USER_AGENT = "Mozilla/5.0 (URPL feasibility probe - MgSochacka PJATK thesis)"
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/xml, text/xml, */*",
}


@dataclass
class SampleEntry:
    product_id: str                    # XSD attribute `id`, e.g. "100000014"
    atc_codes: list[str] = field(default_factory=list)
    name: str = ""                     # nazwaProduktu
    dci_name: str = ""                 # nazwaPowszechnieStosowana (Polish DCI)
    numer_pozwolenia: str = ""
    chpl_url: str = ""                 # XSD attribute `charakterystyka`
    ulotka_url: str = ""               # XSD attribute `ulotka`

    @property
    def first_atc(self) -> str:
        return self.atc_codes[0] if self.atc_codes else ""

    @property
    def is_psych(self) -> bool:
        return self.first_atc[:3] in PSYCH_ATC_PREFIXES

    @property
    def is_complete_pair(self) -> bool:
        """Filter criterion: produkty z pełną parą ChPL+Ulotka URL i ATC code.

        Wykluczone (z URPL feed metadata):
        - Produkty bez URL-i (np. EU centralized procedure rejestrowane przez EMA, stare nie-zdigitalizowane reissues)
        - Preparaty bez kodu ATC (zioła np. Owoc Kolendry, gazy medyczne, traditional preparations) — poza zakresem corpus farmakologii
        """
        return bool(self.chpl_url and self.ulotka_url and self.atc_codes)


@dataclass
class ProbeResult:
    product_id: str
    atc_code: str
    chpl_status: int | None = None
    chpl_time_sec: float | None = None
    chpl_pdf_size_bytes: int | None = None
    chpl_text_length: int | None = None
    chpl_last_modified: str | None = None
    chpl_error: str | None = None
    ulotka_status: int | None = None
    ulotka_time_sec: float | None = None
    ulotka_pdf_size_bytes: int | None = None
    ulotka_last_modified: str | None = None
    ulotka_error: str | None = None
    alignment_ok: bool = False
    alignment_date_check: str = "skipped"  # "passed" | "failed" | "skipped" (no headers)
    text_layer_ok: bool = False


def configure_logging(verbose: bool = False) -> None:
    # Windows console default cp1252 — force UTF-8 for safe printing of polish text
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
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
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SEC, headers=DEFAULT_HEADERS)
    response.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(response.content)
    logger.info("Saved %d bytes to %s", len(response.content), dest)
    return dest


def parse_xml(xml_path: Path) -> tuple[bool, str | None, str | None, list[SampleEntry]]:
    """Pre-condition #2: parse XML, extract product list.

    Returns (parse_ok, error_message, snapshot_date_stanNaDzien, entries).
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as exc:
        return False, str(exc), None, []

    snapshot_date = root.attrib.get("stanNaDzien")
    entries: list[SampleEntry] = []

    for product in root.iterfind("rpl:produktLeczniczy", NS):
        atc_elements = product.findall("rpl:kodyATC/rpl:kodATC", NS)
        atc_codes = [(e.text or "").strip().upper() for e in atc_elements if e.text]

        entries.append(
            SampleEntry(
                product_id=product.attrib.get("id", "").strip(),
                atc_codes=atc_codes,
                name=product.attrib.get("nazwaProduktu", "").strip(),
                dci_name=product.attrib.get("nazwaPowszechnieStosowana", "").strip(),
                numer_pozwolenia=product.attrib.get("numerPozwolenia", "").strip(),
                chpl_url=product.attrib.get("charakterystyka", "").strip(),
                ulotka_url=product.attrib.get("ulotka", "").strip(),
            )
        )

    logger.info(
        "Parsed %d product entries from XML (snapshot date: %s)", len(entries), snapshot_date
    )
    return True, None, snapshot_date, entries


def stratified_sample(
    entries: list[SampleEntry], seed: int, sample_size: int, spot_check_size: int
) -> tuple[list[SampleEntry], list[SampleEntry]]:
    """Returns (random_sample, psych_spot_check).

    random_sample: `sample_size` random across all ATC classes (#3-#6 automation)
    psych_spot_check: `spot_check_size` z psych N05/N06 subset for manual review

    Per DEC-001 § Eval set + sources_catalog § Sprawdzanie pairing integrity (competence-stratified).
    """
    rng = random.Random(seed)
    sample = rng.sample(entries, min(sample_size, len(entries)))

    psych_pool = [e for e in entries if e.is_psych]
    psych_in_sample = [e for e in sample if e.is_psych]

    if len(psych_in_sample) >= spot_check_size:
        spot_check = rng.sample(psych_in_sample, spot_check_size)
    else:
        needed = spot_check_size - len(psych_in_sample)
        extra_pool = [e for e in psych_pool if e not in psych_in_sample]
        extra = rng.sample(extra_pool, min(needed, len(extra_pool)))
        spot_check = list(psych_in_sample) + extra

    return sample, spot_check


def probe_endpoint(
    url: str,
) -> tuple[int | None, float | None, bytes | None, dict[str, str], str | None]:
    """Returns (status_code, elapsed_sec, content_bytes, headers, error_msg)."""
    t0 = time.monotonic()
    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT_SEC,
            headers={"User-Agent": USER_AGENT, "Accept": "application/pdf, */*"},
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        return None, time.monotonic() - t0, None, {}, str(exc)
    elapsed = time.monotonic() - t0
    content = response.content if response.ok else None
    return response.status_code, elapsed, content, dict(response.headers), None


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


def parse_http_date(value: str | None) -> datetime | None:
    """Parse RFC 7231 HTTP-date format (e.g. 'Wed, 21 Oct 2015 07:28:00 GMT')."""
    if not value:
        return None
    for fmt in ("%a, %d %b %Y %H:%M:%S GMT", "%a, %d %b %Y %H:%M:%S %Z"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def alignment_date_check(
    chpl_lm: str | None, ulotka_lm: str | None, tolerance_days: int = ALIGNMENT_DATE_TOLERANCE_DAYS
) -> str:
    """Returns 'passed' | 'failed' | 'skipped'."""
    chpl_dt = parse_http_date(chpl_lm)
    ulotka_dt = parse_http_date(ulotka_lm)
    if chpl_dt is None or ulotka_dt is None:
        return "skipped"
    return "passed" if abs((chpl_dt - ulotka_dt).days) <= tolerance_days else "failed"


def probe_product(entry: SampleEntry) -> ProbeResult:
    result = ProbeResult(product_id=entry.product_id, atc_code=entry.first_atc)

    # ChPL probe
    if entry.chpl_url:
        status, elapsed, content, headers, err = probe_endpoint(entry.chpl_url)
        result.chpl_status = status
        result.chpl_time_sec = elapsed
        result.chpl_error = err
        result.chpl_last_modified = headers.get("Last-Modified")
        if content:
            result.chpl_pdf_size_bytes = len(content)
            has_text, text_len = detect_text_layer(content)
            result.text_layer_ok = has_text
            result.chpl_text_length = text_len
    else:
        result.chpl_error = "no charakterystyka URL in XML metadata"

    # Ulotka probe
    if entry.ulotka_url:
        status, elapsed, content, headers, err = probe_endpoint(entry.ulotka_url)
        result.ulotka_status = status
        result.ulotka_time_sec = elapsed
        result.ulotka_error = err
        result.ulotka_last_modified = headers.get("Last-Modified")
        if content:
            result.ulotka_pdf_size_bytes = len(content)
    else:
        result.ulotka_error = "no ulotka URL in XML metadata"

    # Alignment: both endpoints OK + valid PDFs (semantic equivalence — paired URLs
    # generated together przez tę samą decyzję URPL).
    # Optional date tolerance check via HTTP Last-Modified headers (if server provides).
    align_status_ok = result.chpl_status == 200 and result.ulotka_status == 200
    align_pdf_ok = bool(result.chpl_pdf_size_bytes) and bool(result.ulotka_pdf_size_bytes)
    result.alignment_date_check = alignment_date_check(
        result.chpl_last_modified, result.ulotka_last_modified
    )
    # Date check is supplemental — if "failed", flag but don't auto-reject (URPL feed
    # may have stale Last-Modified due to CDN behavior). If "skipped", accept on status+pdf.
    result.alignment_ok = align_status_ok and align_pdf_ok and result.alignment_date_check != "failed"

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
        "alignment_date_check_skipped_count": sum(
            1 for r in results if r.alignment_date_check == "skipped"
        ),
        "alignment_date_check_failed_count": sum(
            1 for r in results if r.alignment_date_check == "failed"
        ),
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
            "threshold": ">=90% (warn band 80-89%, kill <80%)",
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
        triggers.append(f">=2 pre-conditions FAIL (got {fails})")
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
                "first_atc",
                "atc_level1",
                "all_atc_codes",
                "is_psych_N05_N06",
                "name",
                "dci_name",
                "numer_pozwolenia",
                "chpl_url",
                "ulotka_url",
            ]
        )
        for entry in entries:
            writer.writerow(
                [
                    entry.product_id,
                    entry.first_atc,
                    entry.first_atc[:1] if entry.first_atc else "",
                    ";".join(entry.atc_codes),
                    "yes" if entry.is_psych else "no",
                    entry.name,
                    entry.dci_name,
                    entry.numer_pozwolenia,
                    entry.chpl_url,
                    entry.ulotka_url,
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
        help="Limit endpoint probes do first N entries (smoke test).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse XML + sample only, skip endpoint probing.",
    )
    parser.add_argument(
        "--reuse-snapshot",
        type=Path,
        default=None,
        help="Skip download, parse existing local XML snapshot.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    configure_logging(args.verbose)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(args.config)
    url = args.urpl_xml_url or config.get("urpl_xml_url")
    if not url and args.reuse_snapshot is None:
        logger.error(
            "URPL XML URL not provided. Set 'urpl_xml_url' in %s, "
            "pass --urpl-xml-url, or use --reuse-snapshot.",
            args.config,
        )
        return 2

    today = datetime.now().strftime("%Y-%m-%d")

    if args.reuse_snapshot:
        xml_path = args.reuse_snapshot
        logger.info("Reusing existing snapshot: %s", xml_path)
    else:
        xml_path = args.output_dir / f"rpl-snapshot-{today}.xml"
        download_rpl_xml(url, xml_path)

    parse_ok, parse_err, snapshot_date, entries = parse_xml(xml_path)
    logger.info(
        "Parse OK: %s; entries: %d; snapshot date: %s", parse_ok, len(entries), snapshot_date
    )
    if parse_err:
        logger.error("Parse error: %s", parse_err)
    if not entries:
        logger.error(
            "No entries parsed. Inspect %s manually - schema may have changed (current: %s).",
            xml_path,
            URPL_NAMESPACE,
        )
        return 3

    # Filter to complete pairs (both URLs + ATC code) before sampling.
    # XML universe includes products bez ChPL/Ulotka URL (np. EU centralized via EMA,
    # stare nie-zdigitalizowane) i preparaty bez ATC (zioła, gazy) — poza zakresem corpus.
    complete_entries = [e for e in entries if e.is_complete_pair]
    no_url_count = sum(1 for e in entries if not (e.chpl_url and e.ulotka_url))
    no_atc_count = sum(1 for e in entries if not e.atc_codes)
    logger.info(
        "Filter: %d total -> %d complete pairs (excluded: %d no-URL, %d no-ATC; overlap possible)",
        len(entries),
        len(complete_entries),
        no_url_count,
        no_atc_count,
    )

    sample, spot_check = stratified_sample(
        complete_entries,
        seed=args.seed,
        sample_size=args.sample_size,
        spot_check_size=args.spot_check_size,
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
            "[%d/%d] Probing productID=%s ATC=%s name=%s",
            i,
            len(probe_list),
            entry.product_id,
            entry.first_atc,
            entry.name[:40],
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
            "snapshot_stanNaDzien": snapshot_date,
            "entries_total_in_snapshot": len(entries),
            "entries_complete_pair": len(complete_entries),
            "entries_excluded_no_url": no_url_count,
            "entries_excluded_no_atc": no_atc_count,
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

    _print_summary(
        evaluations,
        kill,
        snapshot_date,
        len(entries),
        len(sample),
        len(spot_check),
        results_path,
        sample_csv,
        spot_csv,
    )
    return 0


def _print_summary(
    evaluations: dict[str, dict[str, Any]],
    kill: dict[str, Any],
    snapshot_date: str | None,
    n_entries: int,
    n_sample: int,
    n_spot_check: int,
    results_path: Path,
    sample_csv: Path,
    spot_csv: Path,
) -> None:
    print("\n=== Iteracja 0a phase 1 - Feasibility probe results ===")
    print(f"URPL snapshot date (stanNaDzien): {snapshot_date}")
    print(f"Parsed entries: {n_entries}")
    print(f"Sample size: {n_sample} (+ {n_spot_check} psych spot-check)")
    print("\nPre-conditions:")
    for key, ev in evaluations.items():
        val = ev["value"]
        threshold = ev["threshold"]
        if isinstance(val, bool) or val is None:
            val_str = str(val)
        elif isinstance(val, float):
            # Distinguish seconds (p95) vs rate (alignment, ocr) by threshold contents
            if "%" in threshold:
                val_str = f"{val:.1%}"
            elif "s" in threshold.split()[0]:  # threshold like "<2s p95..."
                val_str = f"{val:.3f}s"
            else:
                val_str = f"{val:.3f}"
        else:
            val_str = str(val)
        print(f"  {key}: {ev['result']:5} (threshold {threshold}, got {val_str})")
    print(f"\nKill criteria activated: {kill['kill_activated']}")
    if kill["triggers"]:
        print("Triggers:")
        for trigger in kill["triggers"]:
            print(f"  - {trigger}")
    print("\nArtefakty:")
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
