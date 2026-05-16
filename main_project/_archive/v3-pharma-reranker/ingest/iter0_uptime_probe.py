"""Iteracja 0a phase 2 — URPL uptime SLA probe (pre-condition #1).

Tick co INTERVAL_MIN minut przez HOURS godzin. Każdy probe:
- HTTP HEAD na URPL_XML_URL (lub GET jeśli serwer nie wspiera HEAD)
- Append do JSONL: {timestamp, status, elapsed_sec, error?}

Sukces (pre-condition #1): ≥99% probes z status 200 w 24h.

Usage (Linux/WSL):
    nohup uv run python -m ingest.iter0_uptime_probe \\
        --url "$URPL_XML_URL" \\
        --hours 24 --interval-min 60 \\
        > /tmp/uptime.log 2>&1 &

Usage (Windows PowerShell):
    Start-Job -ScriptBlock {
        cd D:\\diplomma\\main_project
        uv run python -m ingest.iter0_uptime_probe `
            --url "<URPL_XML_URL>" `
            --hours 24 --interval-min 60
    }

Output:
    {output}.jsonl         — per-probe append log
    {output}.summary.json  — aggregate (po zakończeniu run)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)
USER_AGENT = "Mozilla/5.0 (URPL uptime probe - MgSochacka PJATK thesis)"
REQUEST_TIMEOUT_SEC = 30.0


def probe_once(url: str, method: str = "HEAD") -> dict[str, Any]:
    t0 = time.monotonic()
    timestamp = datetime.now().isoformat()
    try:
        response = requests.request(
            method,
            url,
            timeout=REQUEST_TIMEOUT_SEC,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
        )
        elapsed = time.monotonic() - t0
        return {
            "timestamp": timestamp,
            "method": method,
            "status": response.status_code,
            "elapsed_sec": elapsed,
            "error": None,
        }
    except requests.RequestException as exc:
        return {
            "timestamp": timestamp,
            "method": method,
            "status": None,
            "elapsed_sec": time.monotonic() - t0,
            "error": str(exc),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, type=str)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("../thesis_research/iter0_feasibility/uptime.jsonl"),
    )
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--interval-min", type=int, default=60)
    parser.add_argument(
        "--method",
        type=str,
        default="HEAD",
        choices=["HEAD", "GET"],
        help="HTTP method; HEAD preferred (lower bandwidth), fall back to GET if 405.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now()
    end_at = started_at + timedelta(hours=args.hours)
    n_probes = 0
    n_failures = 0
    method = args.method

    with args.output.open("a", encoding="utf-8") as fh:
        while datetime.now() < end_at:
            entry = probe_once(args.url, method=method)
            n_probes += 1
            ok = entry["status"] == 200
            if not ok:
                n_failures += 1
                logger.warning(
                    "Probe %d: status=%s, error=%s",
                    n_probes,
                    entry["status"],
                    entry["error"],
                )
                # If HEAD returns 405 (Method Not Allowed), fall back to GET dla pozostałych probes
                if entry["status"] == 405 and method == "HEAD":
                    logger.info("HEAD returned 405 — switching to GET for remaining probes")
                    method = "GET"
            else:
                logger.info(
                    "Probe %d: OK (%.2fs) elapsed",
                    n_probes,
                    entry["elapsed_sec"] or 0.0,
                )
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            fh.flush()

            sleep_sec = args.interval_min * 60
            if datetime.now() + timedelta(seconds=sleep_sec) > end_at:
                break
            time.sleep(sleep_sec)

    uptime_pct = (n_probes - n_failures) / n_probes if n_probes else 0.0
    summary = {
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now().isoformat(),
        "url": args.url,
        "total_probes": n_probes,
        "failures": n_failures,
        "uptime_rate": uptime_pct,
        "precondition_1_threshold": 0.99,
        "precondition_1_result": "PASS" if uptime_pct >= 0.99 else "FAIL",
    }
    summary_path = args.output.with_suffix(".summary.json")
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(
        "Summary: %d probes, uptime %.1f%%, pre-condition #1 %s",
        n_probes,
        uptime_pct * 100,
        summary["precondition_1_result"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
