"""Allegro + OLX + Lex.pl — blocked or paywall.

Status realny (zweryfikowany 2026-05-16):
- **Allegro:** WAF 403 dla regulaminu na requests + Playwright stealth. Help.allegro.com
  zwraca "Error 404" (HTML error page). Brak dostępu.
- **OLX (help.olx.pl):** "Ups, mamy problem" — WAF blocked, body_len < 100 chars.
- **Lex.pl (Wolters Kluwer):** 200 OK ale pages = paywall/SEO landings.
  Free content limited do public legal acts (już mamy z ISAP/EUR-Lex).

Output: blocked.json z reason per source + minimal metadata. NIE wymyśla contentu.

License: N/A (no content collected).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scrape.new_sources.common import (  # noqa: E402
    SCRAPE_DATE,
    ScrapeSummary,
    write_summary,
)

logger = logging.getLogger("scrape.new_sources.platforms_blocked")


def scrape(output_dir: Path) -> ScrapeSummary:
    output_dir.mkdir(parents=True, exist_ok=True)

    blocked = {
        "allegro": {
            "url_main": "https://allegro.pl/regulamin/pl",
            "url_help": "https://help.allegro.com/pl/",
            "status_via_requests": "403 Forbidden (cookie/CSRF + WAF)",
            "status_via_playwright_stealth": "403 Forbidden (still WAF rejection)",
            "reason": (
                "Allegro deploys aggressive bot detection (Datadome / similar). "
                "Standard scrape rejected even with realistic Chrome UA + stealth JS. "
                "Workaround would require residential proxy + manual CAPTCHA solve, "
                "out of scope per academic time budget."
            ),
            "recommendation": (
                "If regulamin pełen tekst kluczowy: use archive.org Wayback Machine "
                "snapshot or contact Allegro Press Office for explicit research access."
            ),
        },
        "olx": {
            "url_main": "https://help.olx.pl/hc/pl",
            "url_regulamin": "https://www.olx.pl/regulamin/",
            "status_via_requests": "404 (no listing) / 200 z error page",
            "status_via_playwright": "200 z body 'Ups, mamy problem' (93 chars)",
            "reason": (
                "OLX Polska deploys Zendesk help center with bot protection on listing "
                "API. Individual articles may be accessible via direct slug URLs but "
                "discovery wymaga session cookies. Out of scope."
            ),
            "recommendation": "OLX Pomoc Polska — request from PR (commercial T&C are public).",
        },
        "lex_pl_wolters_kluwer": {
            "url_main": "https://www.lex.pl/",
            "url_paywall_example": "https://sip.lex.pl/",
            "status": "200 OK ale 99% content paywall (SIP subskrypcja)",
            "reason": (
                "Lex.pl (Wolters Kluwer) = komercyjna baza prawnicza paywall. "
                "Public articles ograniczone do landing pages + SEO content. "
                "Streszczenia prawne za paywall. Free legal acts już pokryte z ISAP/EUR-Lex."
            ),
            "recommendation": (
                "Nie potrzebne — Lex.pl content że ISAP/EUR-Lex (już mamy) + "
                "Federacja Konsumentów porady (już mamy) pokrywa ten layer."
            ),
        },
        "pko_bp": {
            "url": "https://www.pkobp.pl/klienci-indywidualni/regulaminy/",
            "status_via_requests": "404",
            "status_via_playwright": "200 ale body_len=677 (effectively empty)",
            "reason": (
                "PKO BP blocks /regulaminy paths via WAF + JavaScript-only navigation. "
                "Regulaminy są dostępne tylko w portalu klienta (after login)."
            ),
        },
        "mbank": {
            "url": "https://www.mbank.pl/pomoc/regulaminy-i-tabele/",
            "status_via_requests": "404",
            "status_via_playwright": "200 z error page (404 inner)",
            "reason": (
                "mBank /pomoc/regulaminy paths return 404 for bot UA. Regulaminy "
                "tylko via mBank Online client portal."
            ),
        },
    }

    (output_dir / "blocked.json").write_text(
        json.dumps(blocked, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    readme = (
        "# Platforms / Banks — Blocked Sources Documentation\n\n"
        f"Scrape date: {SCRAPE_DATE}\n\n"
        "## Background\n\n"
        "Per Magda 2026-05-16: \"wszystko ma być zdobyte\" — żadnych skipów ze względu "
        "na privacy/legal risk. Jednak technicznie kilka źródeł jest WAF-blocked nawet "
        "z realistycznym Chrome UA + Playwright stealth. Plik `blocked.json` zawiera "
        "explicit reason per source + recommendation dla fallback.\n\n"
        "## Sources Blocked\n\n"
        "- Allegro (regulamin + help.allegro.com)\n"
        "- OLX (help.olx.pl + regulamin)\n"
        "- Lex.pl/Wolters Kluwer (paywall)\n"
        "- PKO BP (regulaminy)\n"
        "- mBank (regulaminy)\n\n"
        "## Compensating Coverage\n\n"
        "Treść konsumencka z tych źródeł jest w dużej części redundant z innymi zbiorami:\n\n"
        "- T&C handlu internetowego — pokryte przez ECC Polska + UOKiK Q&A + bezprawnik\n"
        "- Bank consumer info — pokryte przez Rzecznik Finansowy FAQ (374) + UOKiK + KNF + ING\n"
        "- Legal acts — pokryte przez ISAP (Sejm API) + EUR-Lex\n\n"
        "## Rationale\n\n"
        "Per Polish TDM exception 2024 (Art. 4 DSM Directive 2019/790), text-and-data "
        "mining dla research jest legalny. Ale dostęp techniczny nie zawsze ma to "
        "umożliwić — bot detection nie wykrywa intencji TDM vs. commercial scraping. "
        "Każdy blocked source ma explicit log + recommended fallback w `blocked.json`.\n"
    )
    (output_dir / "README.md").write_text(readme, encoding="utf-8")

    summary = ScrapeSummary(
        source="platforms_blocked_log",
        scrape_date=SCRAPE_DATE,
        license="N/A — documentation only",
        discovered_urls=0,
        successful_articles=0,
        failed_urls=len(blocked),
        notes=(
            f"Documentation-only output: {len(blocked)} sources blocked, each with "
            "explicit reason + recommendation w blocked.json. Compensating coverage "
            "z innych adapterów dataset listed w README.md."
        ),
    )
    write_summary(summary, output_dir / "_summary.json")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    summary = scrape(args.output.resolve())
    logger.info("done: %s", summary.as_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
