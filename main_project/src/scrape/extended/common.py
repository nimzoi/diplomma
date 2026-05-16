"""Wspólne helpery dla extended scrape adapterów.

- ``Fetcher`` — politely-rate-limited HTTP client z retries
- ``normalize_pl`` — NFC + whitespace collapse
- ``anonymize`` — strip email / phone z user-generated text
- ``EncyclopedicChunk`` — schema dla artykułów / porad / encyklopedycznego content
- ``ScrapeStats`` — agregacja metryk per source
"""

from __future__ import annotations

import json
import logging
import re
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

TODAY = datetime.now().strftime("%Y-%m-%d")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 "
    "(PJATK thesis - extended consumer rights - magmarsochacka@gmail.com)"
)
REQUEST_TIMEOUT_SEC = 30.0
RATE_LIMIT_SEC = 1.0


def normalize_pl(text: str) -> str:
    """NFC normalize + whitespace collapse. Preserve newlines? No — join."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def anonymize(text: str) -> str:
    """Remove obvious email/phone leaks from user-generated text."""
    text = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "[EMAIL]", text)
    text = re.sub(r"\+?\d[\d \-]{7,}\d", "[PHONE]", text)
    return text


@dataclass
class EncyclopedicChunk:
    """Schema dla encyclopedycznego / poradnikowego chunk.

    Używany dla Wikipedia, Federacja Konsumentów porady, gov.pl strony.
    Bardziej elastyczny niż ``LegalChunk`` (nie wymaga citation hierarchy).
    """

    chunk_id: str
    source: str  # np. "wikipedia.pl", "federacja-konsumentow.org.pl"
    source_url: str
    title: str
    section: str | None  # H2/H3 section if applicable
    tresc: str  # NFC-normalized body text (chunk-level)
    license: str  # explicit license string
    scrape_date: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QARecord:
    """Q&A record — kompatybilny z ``QAGoldPair`` ale tolerant (no strict validation here).

    cited_articles może być pusta lista jeśli źródło nie podaje explicit citations.
    """

    qa_id: str
    question: str
    answer: str
    cited_articles: list[str]
    category: str
    source: str
    source_url: str
    license: str
    scrape_date: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScrapeStats:
    """Agregat per adapter."""

    source: str
    scrape_date: str
    license: str
    total_records: int = 0
    records_with_citations: int = 0
    avg_text_length: float = 0.0
    categories: dict[str, int] = field(default_factory=dict)
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "pl,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}


class Fetcher:
    """Politely-rate-limited HTTP client z retries.

    ``per_request_session=True`` używa fresh ``requests.Session`` na każdy
    request — workaround dla Incapsula/WAF deployments które flagują session
    reuse jako bot (np. rf.gov.pl).
    """

    def __init__(
        self,
        rate_limit_sec: float = RATE_LIMIT_SEC,
        per_request_session: bool = False,
    ) -> None:
        self.per_request_session = per_request_session
        if not per_request_session:
            self.session = requests.Session()
            self.session.headers.update(DEFAULT_HEADERS)
        self.rate_limit_sec = rate_limit_sec
        self._last_fetch = 0.0

    def _session(self) -> requests.Session:
        if self.per_request_session:
            s = requests.Session()
            s.headers.update(DEFAULT_HEADERS)
            return s
        return self.session

    def get(self, url: str, *, retries: int = 2) -> requests.Response | None:
        wait = self.rate_limit_sec - (time.monotonic() - self._last_fetch)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(retries + 1):
            try:
                resp = self._session().get(
                    url, timeout=REQUEST_TIMEOUT_SEC, allow_redirects=True
                )
                self._last_fetch = time.monotonic()
                if resp.status_code == 200:
                    # Force UTF-8 (most Polish sites)
                    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
                        resp.encoding = "utf-8"
                    # WAF challenge check — tiny body z _Incapsula_Resource
                    if (
                        len(resp.content) < 1024
                        and b"_Incapsula_Resource" in resp.content
                    ):
                        logger.warning(
                            "GET %s -> WAF challenge (Incapsula) attempt %d",
                            url, attempt + 1,
                        )
                        time.sleep(3.0 * (attempt + 1))
                        continue
                    return resp
                logger.warning(
                    "GET %s -> %d (attempt %d)", url, resp.status_code, attempt + 1
                )
            except requests.RequestException as exc:
                logger.warning("GET %s ERR %s (attempt %d)", url, exc, attempt + 1)
            time.sleep(2.0 * (attempt + 1))
        return None


def write_jsonl(records: list[Any], path: Path) -> None:
    """Write list of dataclass-or-dict records as JSONL (utf-8, no ascii escape)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            d = rec.as_dict() if hasattr(rec, "as_dict") else rec
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    logger.info("wrote %d records -> %s", len(records), path)


def write_stats(stats: ScrapeStats, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(stats.as_dict(), f, ensure_ascii=False, indent=2)
    logger.info("wrote stats -> %s", path)


# Citation extraction — reused from uokik scraper, simplified.
ART_REF_RE = re.compile(
    r"art\.\s*\d+[a-zA-Z]*(?:\s*[¹²³⁰⁴-⁹])?"
    r"(?:\s*\xa7\s*\d+[a-zA-Z]*)?"
    r"(?:\s+(?:ust\.|pkt|lit\.|in\.|zd\.)\s*[\w\s\d.,;-]+?(?="
    r"\s+(?:i\s+art\.|oraz\s+art\.|art\.|Kodeksu|ustawy|w\s+zwiazku|w\s+zw\.|$|\.|,)))?",
    re.IGNORECASE,
)


def extract_citations(text: str) -> list[str]:
    """Heuristic — wyłuskaj 'art. X ustawy/Kodeksu Y' z tekstu.

    Conservative: zwraca tylko fragmenty z explicit 'art.' + statute marker.
    Używane do tagowania QARecord.cited_articles gdy źródło nie ma osobnego
    "Podstawa prawna" pola.
    """
    out: list[str] = []
    seen: set[str] = set()
    for m in ART_REF_RE.finditer(text):
        cite = normalize_pl(m.group(0))
        if cite.lower() not in seen:
            seen.add(cite.lower())
            out.append(cite)
    return out
