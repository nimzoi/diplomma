"""Wspolne helpery dla EUR-Lex scrape.

- ``Fetcher`` — politely-rate-limited HTTP client (1 req per 2 sec dla EUR-Lex)
- ``normalize_pl`` — NFC + whitespace collapse (preserves paragraphs via doubled \\n)
- ``EurLexFormats`` — dataclass z URL templates (HTML, PDF, ALL summary)
- citation builders (build_citation_directive, build_citation_tsue)
- license stamping (LICENSE_EURLEX)

EUR-Lex content jest objete free-reuse per Decyzja 2011/833/UE — wymaga attribution
(link do source EUR-Lex URL).
"""

from __future__ import annotations

import json
import logging
import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

TODAY = datetime.now().strftime("%Y-%m-%d")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 "
    "(PJATK thesis citation-grounded polish RAG - magmarsochacka@gmail.com)"
)
REQUEST_TIMEOUT_SEC = 30.0
# EUR-Lex polite rate limit — 1 request per 2 seconds (task brief recommendation)
RATE_LIMIT_SEC = 2.0

LICENSE_EURLEX = (
    "(c) European Union, https://eur-lex.europa.eu/ — free reuse per Decyzja "
    "2011/833/UE (attribution required: link to EUR-Lex source)"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "pl,en;q=0.5",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}


# === Polish months for citation strings ===

POLISH_MONTHS_GEN = {
    1: "stycznia",
    2: "lutego",
    3: "marca",
    4: "kwietnia",
    5: "maja",
    6: "czerwca",
    7: "lipca",
    8: "sierpnia",
    9: "wrzesnia",
    10: "pazdziernika",
    11: "listopada",
    12: "grudnia",
}


def format_polish_date(d: datetime | None) -> str:
    """Format date as 'd miesiac yyyy r.' (Polish citation convention)."""
    if d is None:
        return ""
    return f"{d.day} {POLISH_MONTHS_GEN[d.month]} {d.year} r."


# === EUR-Lex URL templates ===


@dataclass(frozen=True)
class EurLexFormats:
    """URL templates for EUR-Lex document fetch."""

    celex_id: str

    @property
    def url_html(self) -> str:
        """Rendered HTML (clean) — preferred for parsing."""
        return f"https://eur-lex.europa.eu/legal-content/PL/TXT/HTML/?uri=CELEX:{self.celex_id}"

    @property
    def url_landing(self) -> str:
        """Landing page (PL, with metadata sidebar)."""
        return f"https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:{self.celex_id}"

    @property
    def url_all(self) -> str:
        """ALL languages summary page (used to detect if PL exists)."""
        return f"https://eur-lex.europa.eu/legal-content/PL/ALL/?uri=CELEX:{self.celex_id}"

    @property
    def url_pdf(self) -> str:
        """PDF fallback (preserves formatting)."""
        return f"https://eur-lex.europa.eu/legal-content/PL/TXT/PDF/?uri=CELEX:{self.celex_id}"


# === Text normalization ===


def normalize_pl(text: str) -> str:
    """NFC normalize + whitespace collapse. Preserves paragraph breaks via \\n\\n."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\xa0", " ")
    # Preserve paragraph breaks (double newlines) but collapse inline whitespace
    lines = []
    for paragraph in re.split(r"\n\s*\n", text):
        line = re.sub(r"\s+", " ", paragraph).strip()
        if line:
            lines.append(line)
    return "\n\n".join(lines)


def normalize_inline(text: str) -> str:
    """NFC + collapse ALL whitespace incl. newlines (for chunk-level text)."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# === Citation builders ===


def build_citation_directive(
    direktywa_id: str,
    art: str | None = None,
    ust: str | None = None,
    pkt: str | None = None,
    lit: str | None = None,
    motyw: str | None = None,
) -> str:
    """Build deterministic citation string dla dyrektywy UE.

    Examples:
        art. 6 ust. 1 lit. a Dyrektywy 2011/83/UE
        art. 3 Dyrektywy 93/13/EWG
        motyw 13 Dyrektywy 2011/83/UE
    """
    parts: list[str] = []
    if motyw is not None and art is None:
        parts.append(f"motyw {motyw}")
    if art is not None:
        parts.append(f"art. {art}")
    if ust is not None:
        parts.append(f"ust. {ust}")
    if pkt is not None:
        parts.append(f"pkt {pkt}")
    if lit is not None:
        parts.append(f"lit. {lit}")
    head = " ".join(parts) if parts else ""
    if head:
        return f"{head} Dyrektywy {direktywa_id}"
    return f"Dyrektywa {direktywa_id}"


def build_citation_tsue(
    case_id: str,
    case_name_short: str | None = None,
    data_orzeczenia: datetime | None = None,
) -> str:
    """Build citation string dla orzeczenia TSUE.

    Example:
        Wyrok TSUE z dnia 3 pazdziernika 2019 r. w sprawie C-260/18 Dziubak
    """
    date_part = format_polish_date(data_orzeczenia)
    if date_part:
        head = f"Wyrok TSUE z dnia {date_part} w sprawie {case_id}"
    else:
        head = f"Wyrok TSUE w sprawie {case_id}"
    if case_name_short:
        return f"{head} {case_name_short}"
    return head


# === HTTP client ===


class Fetcher:
    """Politely-rate-limited HTTP client z retries.

    Default rate: 1 req per 2 sec (EUR-Lex recommended).
    """

    def __init__(self, rate_limit_sec: float = RATE_LIMIT_SEC) -> None:
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.rate_limit_sec = rate_limit_sec
        self._last_fetch = 0.0

    def get(self, url: str, *, retries: int = 2) -> requests.Response | None:
        wait = self.rate_limit_sec - (time.monotonic() - self._last_fetch)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(retries + 1):
            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT_SEC, allow_redirects=True)
                self._last_fetch = time.monotonic()
                if resp.status_code == 200:
                    if not resp.encoding or resp.encoding.lower() in (
                        "iso-8859-1",
                        "ascii",
                    ):
                        resp.encoding = "utf-8"
                    return resp
                logger.warning("GET %s -> HTTP %d (attempt %d)", url, resp.status_code, attempt + 1)
            except requests.RequestException as exc:
                logger.warning("GET %s ERR %s (attempt %d)", url, exc, attempt + 1)
            time.sleep(2.0 * (attempt + 1))
        return None


# === Output helpers ===


def write_jsonl(records: list[Any], path: Path) -> None:
    """Write list of dicts (or objects with .model_dump()) as JSONL (utf-8)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            if hasattr(rec, "model_dump"):
                d = rec.model_dump(mode="json")
            elif hasattr(rec, "as_dict"):
                d = rec.as_dict()
            else:
                d = rec
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    logger.info("wrote %d records -> %s", len(records), path)


def write_json(obj: Any, path: Path) -> None:
    """Write single dict/object as JSON (utf-8, indent=2)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(obj, "as_dict"):
        d = obj.as_dict()
    else:
        d = obj
    with path.open("w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    logger.info("wrote -> %s", path)


# === Stats dataclass ===


@dataclass
class ScrapeStats:
    """Aggregate stats per dyrektywa / TSUE collection."""

    source: str
    scrape_date: str
    license: str
    total_records: int = 0
    skipped_no_pl: list[str] = field(default_factory=list)
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "scrape_date": self.scrape_date,
            "license": self.license,
            "total_records": self.total_records,
            "skipped_no_pl": self.skipped_no_pl,
            "notes": self.notes,
        }
