"""Wspólne helpery dla Playwright-based scrape adapterów.

* ``BrowserSession`` — context manager nad sync Playwright z stealth + WAF-friendly headers
* ``normalize_pl`` — NFC + whitespace collapse (kompatybilny z scrape/extended/common.py)
* ``save_snapshot`` — zapis HTML snapshot dla debug (gitignored ``_snapshots/`` dir)
* ``write_jsonl`` / ``write_meta`` — JSONL + meta JSON helpers
* ``extract_citations`` — heuristic ekstrakcja "art. X" / "art. X §Y ust. Z" citation strings
* ``count_words`` — liczy słowa po regex
* ``ScrapeStats`` — agregacja per-source

Realistyczny Chrome UA + ``playwright-stealth`` JS patches automatycznie obchodzą
podstawowe headless detection (navigator.webdriver = false, plugins, Chrome
runtime, etc.).
"""

from __future__ import annotations

import json
import logging
import re
import time
import unicodedata
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# stałe
# ---------------------------------------------------------------------------

TODAY = datetime.now().strftime("%Y-%m-%d")
SCRAPE_DATE = "2026-05-16"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)
VIEWPORT_W = 1366
VIEWPORT_H = 1024
NAVIGATION_TIMEOUT_MS = 60_000
RATE_LIMIT_SEC = 2.0
LICENSE_URZEDOWE = "urzędowe (Art. 4 ust. 2 PrAut)"
LICENSE_FAIR_USE = "fair-use Art. 29 PrAut"

DEFAULT_HEADERS = {
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


# ---------------------------------------------------------------------------
# data classes
# ---------------------------------------------------------------------------


@dataclass
class ScrapeStats:
    """Per-source aggregate."""

    source: str
    scrape_date: str = SCRAPE_DATE
    license: str = ""
    attempted: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    waf_blocks: int = 0
    parse_errors: int = 0
    total_words: int = 0
    skip_reasons: dict[str, int] = field(default_factory=dict)
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------


def normalize_pl(text: str) -> str:
    """NFC + whitespace collapse (kompatybilne z scrape/extended/common.py)."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\xa0", " ").replace("​", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


# Citation extraction — kompatybilna z scrape/extended/common.py.
_ART_REF_RE = re.compile(
    r"art\.\s*\d+[a-zA-Z]*(?:\s*[¹²³⁰⁴-⁹])?"
    r"(?:\s*[§\xa7]\s*\d+[a-zA-Z]*)?"
    r"(?:\s+(?:ust\.|pkt|lit\.|in\.|zd\.)\s*[\w\s\d.,;-]+?(?="
    r"\s+(?:i\s+art\.|oraz\s+art\.|art\.|Kodeksu|ustawy|w\s+zwiazku|w\s+zw\.|$|\.|,)))?",
    re.IGNORECASE,
)


def extract_citations(text: str) -> list[str]:
    """Heuristic — 'art. X ust. Y Kodeksu/ustawy ...' fragmenty.

    Conservative: zwraca jedynie fragmenty z explicit 'art.' + ewentualny § / ust.
    Używane do tagowania ``podstawy_prawne`` w decyzjach + tezach orzeczeń.
    """
    out: list[str] = []
    seen: set[str] = set()
    for m in _ART_REF_RE.finditer(text):
        cite = normalize_pl(m.group(0))
        if not cite:
            continue
        key = cite.lower()
        if key not in seen:
            seen.add(key)
            out.append(cite)
    return out


_KARA_RE = re.compile(
    # "karę pieniężną w wysokości 1 234 567,89 zł", "kwota 500000 zł",
    # "grzywna 10 000,00 PLN" — pochwytujemy phrase z liczbą + zł/PLN.
    r"(?:kar[ęaęy]|grzywn[aęy]|kwot[aęy]|w\s+wysokości|wysokoś[cć][ąi])"
    r"[\w\s,;.()-]{0,80}?"
    r"(\d[\d\s .,]*?)\s*(?:zł|PLN|złotych)",
    re.IGNORECASE,
)


def extract_kara_pln(text: str) -> float | None:
    """Heuristic ekstrakcja kary w PLN z tekstu decyzji UOKiK.

    Pattern: "karę pieniężną w wysokości 1 234 567,89 zł". Bierze pierwsze
    matche; jeśli żadne — zwraca None. Konserwatywne — może chybić edge cases
    (np. wieloczęściowe kary, kary w EUR), ale lepsze niż brak.
    """
    for m in _KARA_RE.finditer(text):
        raw = m.group(1).strip()
        # normalize: usuń spacje, zamień , na .
        cleaned = re.sub(r"\s+", "", raw).replace(",", ".")
        # usuń dot tysięcy (jeśli >2 cyfry po ostatniej kropce)
        # np. "1.234.567.89" → potraktuj jako "1234567.89"
        if cleaned.count(".") > 1:
            head, _, tail = cleaned.rpartition(".")
            cleaned = head.replace(".", "") + "." + tail
        try:
            val = float(cleaned)
            if val > 0:
                return val
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def write_jsonl(records: Iterable[Any], path: Path) -> int:
    """Append-safe JSONL writer. Dataclass / dict / Pydantic obj OK."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            if hasattr(rec, "model_dump"):
                d = rec.model_dump(mode="json")
            elif hasattr(rec, "as_dict"):
                d = rec.as_dict()
            elif hasattr(rec, "__dataclass_fields__"):
                d = asdict(rec)
            else:
                d = rec
            f.write(json.dumps(d, ensure_ascii=False, default=str) + "\n")
            n += 1
    return n


def write_meta(path: Path, meta: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(meta, "model_dump"):
        d = meta.model_dump(mode="json")
    elif hasattr(meta, "as_dict"):
        d = meta.as_dict()
    elif hasattr(meta, "__dataclass_fields__"):
        d = asdict(meta)
    else:
        d = meta
    with path.open("w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2, default=str)


def save_snapshot(html: str, snapshots_dir: Path, name: str) -> Path:
    """Zapisz HTML snapshot dla debug (gitignored)."""
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", name)[:80]
    path = snapshots_dir / f"{safe}.html"
    path.write_text(html, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Browser session
# ---------------------------------------------------------------------------


class BrowserSession:
    """Context manager — Playwright sync API z stealth + rate limit.

    Usage::

        with BrowserSession() as sess:
            page = sess.new_page()
            page.goto(url)
            ...
            sess.throttle()   # zachowuje min RATE_LIMIT_SEC między navigacjami

    Stealth JS patches stosowane na każdej page (apply_stealth_sync).
    """

    def __init__(
        self,
        *,
        headless: bool = True,
        rate_limit_sec: float = RATE_LIMIT_SEC,
        user_agent: str = USER_AGENT,
        viewport: tuple[int, int] = (VIEWPORT_W, VIEWPORT_H),
        locale: str = "pl-PL",
        timezone_id: str = "Europe/Warsaw",
    ) -> None:
        self._headless = headless
        self._rate_limit_sec = rate_limit_sec
        self._user_agent = user_agent
        self._viewport = {"width": viewport[0], "height": viewport[1]}
        self._locale = locale
        self._timezone = timezone_id
        self._last_nav: float = 0.0
        self._pw = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._stealth = Stealth()

    def __enter__(self) -> BrowserSession:
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=self._headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        self._context = self._browser.new_context(
            user_agent=self._user_agent,
            viewport=self._viewport,
            locale=self._locale,
            timezone_id=self._timezone,
            extra_http_headers=DEFAULT_HEADERS,
        )
        return self

    def __exit__(self, *exc: Any) -> None:
        try:
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
        finally:
            if self._pw:
                self._pw.stop()

    def new_page(self) -> Page:
        if self._context is None:
            raise RuntimeError("BrowserSession not entered")
        page = self._context.new_page()
        # Apply stealth patches.
        self._stealth.apply_stealth_sync(page)
        return page

    def throttle(self) -> None:
        """Sleep do osiągnięcia min ``rate_limit_sec`` od ostatniego ``goto``."""
        elapsed = time.monotonic() - self._last_nav
        wait = self._rate_limit_sec - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_nav = time.monotonic()

    def safe_goto(
        self,
        page: Page,
        url: str,
        *,
        retries: int = 2,
        timeout_ms: int = NAVIGATION_TIMEOUT_MS,
        wait_until: str = "domcontentloaded",
        post_wait_ms: int = 1500,
    ) -> bool:
        """Goto z retries + rate limit + WAF challenge detection.

        Returns: True jeśli udane (status 200 + brak WAF reject markers).
        """
        self.throttle()
        for attempt in range(retries + 1):
            try:
                resp = page.goto(url, timeout=timeout_ms, wait_until=wait_until)
                page.wait_for_timeout(post_wait_ms)
                status = resp.status if resp else 0
                title = ""
                try:
                    title = page.title() or ""
                except Exception:
                    pass
                # F5 WAF reject signals.
                if (
                    "Request Rejected" in title
                    or "Access Denied" in title
                    or status in (403, 429, 503)
                ):
                    logger.warning(
                        "WAF/error block on %s (status=%s, title=%r) attempt %d",
                        url,
                        status,
                        title,
                        attempt + 1,
                    )
                    if attempt < retries:
                        time.sleep((attempt + 1) * 3.0)
                        continue
                    return False
                return True
            except Exception as exc:
                logger.warning("goto %s failed: %s (attempt %d)", url, exc, attempt + 1)
                if attempt < retries:
                    time.sleep((attempt + 1) * 2.0)
                    continue
                return False
        return False
