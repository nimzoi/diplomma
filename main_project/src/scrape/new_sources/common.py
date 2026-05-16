"""Wspólne helpery dla NEW_SOURCES scrape (15 portali/urzędów, Magda override 2026-05-16).

* ``ArticleRecord`` — unified schema (per task spec, kompatybilny z resztą datasetu)
* ``Fetcher`` — politely-rate-limited HTTP z retries + sniff dla WAF (`requests`-based)
* ``normalize_pl`` — NFC + whitespace collapse
* ``parse_html_article`` — generic article extraction (title + body + meta) z BeautifulSoup
* ``persist_article`` — zapis _archive/<id>.html + meta.json + idempotency check
* ``write_jsonl_articles`` / ``write_manifest`` / ``write_summary`` — I/O
* ``extract_citations`` — heuristic „art. X ust. Y" extraction

Wszystkie sources zapisują do:

    data/raw/<source>_2026-05-16/
        articles.jsonl
        _archive/{article_id}.html + .meta.json
        _manifest.json
        _summary.json
        _failed.log     # URLs które fail-owały po retries
        README.md
"""

from __future__ import annotations

import hashlib
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
import urllib3
from bs4 import BeautifulSoup

# Disable noisy InsecureRequestWarning — gov sites mają nieaktualne certs lokalnie.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

SCRAPE_DATE = "2026-05-16"
TODAY = datetime.now().strftime("%Y-%m-%d")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 "
    "(PJATK thesis - consumer-rights-academic-research@pjwstk.edu.pl)"
)
REQUEST_TIMEOUT_SEC = 30.0
RATE_LIMIT_SEC = 1.0

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    # NIE prosi o brotli — requests-stdlib nie ma dekodera. gzip+deflate wystarczą.
    "Accept-Encoding": "gzip, deflate",
    "Upgrade-Insecure-Requests": "1",
}

LICENSE_FAIR_USE = "fair-use Art. 29 PrAut (academic research, attribution preserved)"
LICENSE_URZEDOWE = "urzędowe (Art. 4 ust. 2 PrAut, public domain)"

# Default min content size for valid article.
MIN_ARTICLE_CHARS = 250


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ArticleRecord:
    """Unified schema dla wszystkich new_sources (per task spec).

    Mapowanie do reszty datasetu odbywa się w ingest step — tu trzymamy wide
    schema z metadata dict dla per-source quirks.
    """

    article_id: str
    source: str  # np. "bankier.pl"
    source_url: str
    title: str
    tresc: str  # NFC-normalized full body
    license: str
    scrape_date: str
    subtitle: str | None = None
    author: str | None = None
    publication_date: str | None = None  # YYYY-MM-DD if extracted
    category: str | None = None
    tags: list[str] = field(default_factory=list)
    extracted_citations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScrapeSummary:
    """Per-source aggregate stats."""

    source: str
    scrape_date: str = SCRAPE_DATE
    license: str = ""
    discovered_urls: int = 0
    successful_articles: int = 0
    failed_urls: int = 0
    skipped_too_short: int = 0
    skipped_duplicate: int = 0
    waf_blocks: int = 0
    total_chars: int = 0
    avg_chars_per_article: float = 0.0
    archive_mb: float = 0.0
    notes: str = ""
    categories: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def normalize_pl(text: str) -> str:
    """NFC normalize + whitespace collapse + HTML entity decode.

    Preserve newlines via join. Decodes HTML entities (np. &nbsp;) tylko
    jeśli text zawiera & — żeby nie szkodzić tekstom które mają explicit
    sekwencje (ampersandy w tekście prawniczym).
    """
    if not text:
        return ""
    if "&" in text and ";" in text:
        # html.unescape decodes &nbsp;, &amp;, &lt;, etc. to chars.
        import html as _html

        text = _html.unescape(text)
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\xa0", " ").replace("​", "").replace("‌", "")
    # Collapse multiple spaces/tabs but preserve newlines.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def anonymize(text: str) -> str:
    """Remove obvious email/phone from user-generated text."""
    text = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "[EMAIL]", text)
    text = re.sub(r"\+?\d[\d \-]{7,}\d", "[PHONE]", text)
    return text


_ART_REF_RE = re.compile(
    r"art\.\s*\d+[a-zA-Z]*(?:\s*[¹²³⁰⁴-⁹])?"
    r"(?:\s*[§\xa7]\s*\d+[a-zA-Z]*)?"
    r"(?:\s+(?:ust\.|pkt|lit\.|in\.|zd\.)\s*[\w\s\d.,;-]+?(?="
    r"\s+(?:i\s+art\.|oraz\s+art\.|art\.|Kodeksu|ustawy|w\s+zwiazku|w\s+zw\.|$|\.|,)))?",
    re.IGNORECASE,
)


def extract_citations(text: str) -> list[str]:
    """Heuristic — 'art. X ust. Y Kodeksu/ustawy ...' fragmenty z tekstu."""
    out: list[str] = []
    seen: set[str] = set()
    for m in _ART_REF_RE.finditer(text):
        cite = normalize_pl(m.group(0))
        key = cite.lower()
        if cite and key not in seen:
            seen.add(key)
            out.append(cite)
    return out


def slug_from_title(title: str, max_len: int = 60) -> str:
    """Lowercased ASCII-ish slug; fallback 'untitled'."""
    s = unicodedata.normalize("NFKD", title)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\W+", "_", s.lower()).strip("_")
    return s[:max_len] or "untitled"


def detect_pubdate(soup: BeautifulSoup, html: str) -> str | None:
    """Try to extract YYYY-MM-DD publication date.

    Looks at common meta tags + JSON-LD + visible date tokens.
    """
    # JSON-LD datePublished
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(tag.string or "")
        except Exception:
            continue
        if isinstance(data, dict):
            candidates = [data]
        elif isinstance(data, list):
            candidates = data
        else:
            candidates = []
        for c in candidates:
            if not isinstance(c, dict):
                continue
            dp = c.get("datePublished") or c.get("dateCreated")
            if isinstance(dp, str) and len(dp) >= 10:
                return dp[:10]
            # nested @graph
            for sub in c.get("@graph", []) if isinstance(c.get("@graph"), list) else []:
                if isinstance(sub, dict):
                    dp = sub.get("datePublished") or sub.get("dateCreated")
                    if isinstance(dp, str) and len(dp) >= 10:
                        return dp[:10]

    # Meta tags
    for sel in [
        ('meta[property="article:published_time"]', "content"),
        ('meta[name="DC.date.issued"]', "content"),
        ('meta[name="pubdate"]', "content"),
        ('meta[name="date"]', "content"),
        ('meta[itemprop="datePublished"]', "content"),
        ("time[datetime]", "datetime"),
    ]:
        el = soup.select_one(sel[0])
        if el:
            v = el.get(sel[1], "")
            if v and len(v) >= 10:
                return v[:10]

    # Polish date pattern w widocznym tekście np. „2024-05-12" lub „12.05.2024"
    m = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", html[:5000])
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"\b(\d{2})\.(\d{2})\.(20\d{2})\b", html[:5000])
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return None


# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------


WAF_MARKERS = (
    b"_Incapsula_Resource",
    b"cf-browser-verification",
    b"Just a moment",
    b"<title>Access denied</title>",
    b"<title>Request Rejected</title>",
)


class Fetcher:
    """Politely-rate-limited HTTP z retries + WAF detection."""

    def __init__(
        self,
        rate_limit_sec: float = RATE_LIMIT_SEC,
        per_request_session: bool = False,
        verify_ssl: bool = True,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.per_request_session = per_request_session
        self.verify_ssl = verify_ssl
        self._headers = dict(DEFAULT_HEADERS)
        if extra_headers:
            self._headers.update(extra_headers)
        if not per_request_session:
            self.session = requests.Session()
            self.session.headers.update(self._headers)
        self.rate_limit_sec = rate_limit_sec
        self._last_fetch = 0.0

    def _session(self) -> requests.Session:
        if self.per_request_session:
            s = requests.Session()
            s.headers.update(self._headers)
            return s
        return self.session

    def get(
        self,
        url: str,
        *,
        retries: int = 2,
        timeout: float = REQUEST_TIMEOUT_SEC,
        check_waf: bool = True,
    ) -> requests.Response | None:
        wait = self.rate_limit_sec - (time.monotonic() - self._last_fetch)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(retries + 1):
            try:
                resp = self._session().get(
                    url,
                    timeout=timeout,
                    allow_redirects=True,
                    verify=self.verify_ssl,
                )
                self._last_fetch = time.monotonic()
                if resp.status_code == 200:
                    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
                        resp.encoding = "utf-8"
                    if check_waf and len(resp.content) < 8192:
                        if any(m in resp.content for m in WAF_MARKERS):
                            logger.warning(
                                "GET %s -> WAF challenge (attempt %d/%d)",
                                url,
                                attempt + 1,
                                retries + 1,
                            )
                            time.sleep(2.0 * (attempt + 1))
                            continue
                    return resp
                # 404 is final — no point retrying.
                if resp.status_code == 404:
                    logger.info("GET %s -> 404 (no retry)", url)
                    return resp  # caller decides
                logger.warning(
                    "GET %s -> %d (attempt %d/%d)",
                    url,
                    resp.status_code,
                    attempt + 1,
                    retries + 1,
                )
            except requests.RequestException as exc:
                logger.warning(
                    "GET %s ERR %s (attempt %d/%d)", url, exc, attempt + 1, retries + 1
                )
            time.sleep(2.0 * (attempt + 1))
        return None


# ---------------------------------------------------------------------------
# Article parsing (generic)
# ---------------------------------------------------------------------------


_TAGS_TO_STRIP = (
    "script",
    "style",
    "noscript",
    "iframe",
    "nav",
    "aside",
    "footer",
    "header",
    "form",
    "button",
    "svg",
    "picture",
    "figure",
)


def clean_soup(soup: BeautifulSoup) -> None:
    """Remove obvious non-content elements in-place."""
    for tag_name in _TAGS_TO_STRIP:
        for el in soup.find_all(tag_name):
            el.decompose()
    # Common ad/UI selectors
    for sel in [
        ".advertisement",
        ".ad-",
        ".social",
        ".share-",
        ".comments",
        ".cookie",
        ".newsletter",
        ".breadcrumb",
        ".breadcrumbs",
        ".sidebar",
        ".menu",
        ".navigation",
        ".related",
        ".tags",
        ".pagination",
    ]:
        for el in soup.select(f"[class*='{sel.strip('.')}']"):
            el.decompose()


def extract_main_text(soup: BeautifulSoup) -> str:
    """Find the article body via common selectors + paragraph fallback."""
    # Priority selectors — try article / main / typical CMS classes
    selectors = [
        "article",
        "main",
        '[role="main"]',
        ".article__content",
        ".article-content",
        ".article-body",
        ".entry-content",
        ".post-content",
        ".content-main",
        "#main-content",
        "#content",
        ".tresc",
        ".tekst",
        ".artykul",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            paragraphs = []
            for p in el.find_all(["p", "h2", "h3", "li"]):
                t = p.get_text(" ", strip=True)
                if t and len(t) > 15:
                    paragraphs.append(t)
            if paragraphs:
                body = "\n".join(paragraphs)
                if len(body) > MIN_ARTICLE_CHARS:
                    return normalize_pl(body)

    # Fallback — all paragraphs in document
    paragraphs = []
    for p in soup.find_all(["p", "h2", "h3"]):
        t = p.get_text(" ", strip=True)
        if t and len(t) > 25:
            paragraphs.append(t)
    return normalize_pl("\n".join(paragraphs))


def extract_title(soup: BeautifulSoup, fallback: str = "(no title)") -> str:
    """Title via og:title / h1 / <title>."""
    el = soup.select_one('meta[property="og:title"]')
    if el and el.get("content"):
        return normalize_pl(el["content"])
    el = soup.select_one("h1")
    if el:
        return normalize_pl(el.get_text(" ", strip=True))
    el = soup.find("title")
    if el:
        return normalize_pl(el.get_text(" ", strip=True))
    return fallback


def extract_subtitle(soup: BeautifulSoup) -> str | None:
    """Try og:description / meta description / .lead."""
    for sel in [
        'meta[property="og:description"]',
        'meta[name="description"]',
    ]:
        el = soup.select_one(sel)
        if el and el.get("content"):
            return normalize_pl(el["content"])
    for sel in [".lead", ".entry-summary", ".article-lead", ".article__lead"]:
        el = soup.select_one(sel)
        if el:
            txt = normalize_pl(el.get_text(" ", strip=True))
            if 30 < len(txt) < 500:
                return txt
    return None


def extract_author(soup: BeautifulSoup) -> str | None:
    """Try meta author / .author / byline."""
    for sel, attr in [
        ('meta[name="author"]', "content"),
        ('meta[property="article:author"]', "content"),
    ]:
        el = soup.select_one(sel)
        if el and el.get(attr):
            return normalize_pl(el[attr])
    for sel in [".author", ".byline", ".article-author", "[rel='author']"]:
        el = soup.select_one(sel)
        if el:
            txt = normalize_pl(el.get_text(" ", strip=True))
            if 0 < len(txt) < 200:
                return txt
    return None


# ---------------------------------------------------------------------------
# I/O & idempotency
# ---------------------------------------------------------------------------


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def persist_raw_html(
    archive_dir: Path, article_id: str, html_bytes: bytes, url: str, status: int
) -> dict[str, Any]:
    """Write raw HTML + meta.json to _archive/. Return meta dict."""
    archive_dir.mkdir(parents=True, exist_ok=True)
    html_path = archive_dir / f"{article_id}.html"
    meta_path = archive_dir / f"{article_id}.meta.json"
    html_path.write_bytes(html_bytes)
    meta = {
        "article_id": article_id,
        "url": url,
        "status_code": status,
        "size_bytes": len(html_bytes),
        "sha256": sha256_hex(html_bytes),
        "download_date": TODAY,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def already_archived(archive_dir: Path, article_id: str) -> bool:
    return (archive_dir / f"{article_id}.html").exists()


def write_jsonl_articles(records: list[ArticleRecord], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec.as_dict(), ensure_ascii=False) + "\n")
            n += 1
    return n


def write_manifest(manifest: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {"scrape_date": SCRAPE_DATE, "count": len(manifest), "entries": manifest},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def write_summary(summary: ScrapeSummary, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(summary.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_readme(
    output_dir: Path,
    source_name: str,
    source_url: str,
    license_str: str,
    method: str,
) -> None:
    md = (
        f"# {source_name} — consumer rights scrape (2026-05-16)\n\n"
        f"**Source:** <{source_url}>\n\n"
        f"**License:** {license_str}\n\n"
        f"**Method:** {method}\n\n"
        f"**Scrape date:** {SCRAPE_DATE}\n\n"
        f"## Schema\n\n"
        f"Każdy rekord w `articles.jsonl` ma pola: "
        f"`article_id`, `source`, `source_url`, `title`, `subtitle`, `author`, "
        f"`publication_date`, `tresc`, `category`, `tags`, `extracted_citations`, "
        f"`license`, `scrape_date`, `metadata`.\n\n"
        f"## Files\n\n"
        f"- `articles.jsonl` — extracted, normalized text\n"
        f"- `_archive/{{article_id}}.html` + `.meta.json` — raw HTML + sha256\n"
        f"- `_manifest.json` — full mapping article_id → url, status, size\n"
        f"- `_summary.json` — aggregate stats\n"
        f"- `_failed.log` — URLs które nie udało się pobrać (jeśli istnieje)\n\n"
        f"## License rationale\n\n"
        f"{license_str}. Pobór mieści się w Polish TDM exception 2024 "
        f"(implementacja Art. 4 DSM Directive 2019/790) — text and data mining "
        f"dla research scientific purposes is permitted without authorization. "
        f"Attribution preserved via `source_url` w każdym rekordzie.\n"
    )
    (output_dir / "README.md").write_text(md, encoding="utf-8")


def write_failed_log(failed: list[tuple[str, str]], path: Path) -> None:
    """Save list of (url, reason) tuples that failed."""
    if not failed:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for url, reason in failed:
            f.write(f"{url}\t{reason}\n")


def archive_size_mb(archive_dir: Path) -> float:
    if not archive_dir.exists():
        return 0.0
    total = 0
    for p in archive_dir.glob("*.html"):
        total += p.stat().st_size
    return round(total / (1024 * 1024), 2)


# ---------------------------------------------------------------------------
# Sitemap helper
# ---------------------------------------------------------------------------


def parse_sitemap(xml_bytes: bytes) -> list[str]:
    """Extract all <loc> URLs (works for sitemapindex or urlset)."""
    text = xml_bytes.decode("utf-8", "replace")
    return re.findall(r"<loc>([^<]+)</loc>", text)


def fetch_sitemap_urls(
    fetcher: Fetcher, sitemap_url: str, max_levels: int = 2
) -> list[str]:
    """Recursively walk sitemap index, return final article URLs.

    Stops at ``max_levels`` to avoid pathological loops.
    """
    seen: set[str] = set()
    queue: list[tuple[str, int]] = [(sitemap_url, 0)]
    out: list[str] = []
    while queue:
        url, depth = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            continue
        urls = parse_sitemap(resp.content)
        for u in urls:
            if u.endswith(".xml") and depth < max_levels:
                queue.append((u, depth + 1))
            else:
                out.append(u)
    return out
