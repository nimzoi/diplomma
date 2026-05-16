"""Scrape Polish consumer-rights questions from public Reddit JSON API.

Reddit blocks unauthenticated rules.json/about endpoints, but the public
`/r/<sub>/search.json` and `/r/<sub>/<sort>.json` listings still work as long
as we send a real-browser User-Agent and rate-limit ourselves.

Subreddits scanned (Polish-only):
  - r/Polska         — main Polish subreddit, ~870k subs
  - r/Polska_wpz     — "wszystko po za polityką", ~99k subs (more porady)
  - r/Polish         — smaller PL diaspora sub (some consumer threads, EN/PL)

Queries: consumer-rights keywords (sklep, zwrot, reklamacja, allegro, ...).

Output JSONL — one record per submission, in the shared
`QuestionRecord`-compatible schema.

Filtering:
  - Submission must be a self-post (`is_self == true`); link posts skipped.
  - Title or selftext must contain a consumer keyword (defense vs noise).
  - Comments are NOT scraped — for hallucination eval we want only the
    question, not random users' answers.
  - User IDs anonymized: stored as a stable SHA-1 prefix of the username,
    not the username itself.

Usage (PowerShell):
  uv run python -m scrape.reddit.scrape_consumer `
      --output ../data/raw/consumer_questions_polish_2026-05-16/reddit_polska_consumer.jsonl `
      --queries-file ../data/raw/consumer_questions_polish_2026-05-16/_reddit_queries.txt

If the live API returns 403/429, the script logs a clear message and writes
partial output (whatever it managed to collect before being blocked) plus an
empty-on-purpose JSONL with a `_status.json` next to it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger("scrape.reddit.consumer")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 "
    "(PJATK thesis - polish consumer questions - magmarsochacka@gmail.com)"
)
REQUEST_TIMEOUT_SEC = 25.0
RATE_LIMIT_SEC = 2.0  # Reddit is stricter — keep at 2s.
TODAY = datetime.now().strftime("%Y-%m-%d")

DEFAULT_SUBREDDITS: tuple[str, ...] = ("Polska", "Polska_wpz", "Polish")
DEFAULT_QUERIES: tuple[str, ...] = (
    "sklep zwrot",
    "reklamacja sklep",
    "reklamacja allegro",
    "allegro problem",
    "nieuczciwy sklep",
    "prawa konsumenta",
    "zwrot pieniędzy",
    "gwarancja sprzedawca",
    "umowa na odległość",
    "kurier paczka zaginiona",
    "inpost paczkomat",
    "operator komórkowy umowa",
    "play orange t-mobile",
    "bank kredyt problem",
    "ubezpieczenie odmowa",
    "ratalna sprzedaż",
    "rękojmia wada",
    "uokik skarga",
    "rzecznik konsumentów",
    "klauzula niedozwolona",
    "abonament telefoniczny",
    "energia prąd umowa",
    "vinted oszustwo",
    "olx oszustwo",
    "olx allegro spór",
    "wadliwy produkt",
    "nie chcą zwrócić",
    "odstąpienie od umowy",
    "ecommerce reklamacja",
    "ratalna płatność problem",
)

# Topic keywords for tagging (kept in sync with scrape.legal_fora.scrape).
TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "zwrot": ("zwrot", "zwracam", "zwróć", "odstąpienie od umowy"),
    "reklamacja": ("reklamac", "wadliw", "wady towaru", "uszkodz"),
    "gwarancja": ("gwarancj",),
    "rękojmia": ("rękojm", "rekojmi"),
    "umowa-na-odleglosc": (
        "na odległość",
        "umowa zawart",
        "sklep internet",
        "zakup online",
        "zakup przez internet",
    ),
    "sklep": ("sklep", "sprzedawca", "sprzedawc"),
    "allegro": ("allegro",),
    "olx": ("olx",),
    "vinted": ("vinted",),
    "kurier-paczka": ("kurier", "paczk", "przesyłk", "przesylk", "dpd", "inpost"),
    "telekomunikacja": (
        "operator",
        "abonament",
        "orange",
        "t-mobile",
        "play s.a",
        "plus s.a",
    ),
    "energia-gaz": ("prąd", "energia elektr", "tauron", "pgnig"),
    "bank-kredyt": ("kredyt", "pożyczk", "pozyczk", "lokat"),
    "ubezpieczenie": ("ubezpiecz",),
    "uokik": ("uokik",),
    "rzecznik": ("rzecznik konsument",),
    "termin-14-30-dni": ("14 dni", "30 dni"),
    "naprawa-serwis": ("naprawa", "serwis", "warsztat"),
    "pojazd-auto": ("samoch", "auto"),
    "elektronika": ("telewizor", "laptop", "smartfon", "pralka", "lodówk"),
    "meble": ("mebl", "kanapa", "szafa", "łóżk"),
    "dostawa": ("dostawa", "dostarczen", "dostarczy", "wysyłk", "wysylk"),
    "cena-przedplata": ("zaliczk", "przedpłat", "przedplat"),
    "niezgodnosc": ("niezgodn",),
    "odszkodowanie": ("odszkodow",),
    "nieuczciwe-praktyki": ("nieuczciw",),
    "klauzule-niedozwolone": ("klauzul niedozw",),
}

# Consumer-relevance gate: must hit at least one of these substrings somewhere
# in the title or selftext (case-insensitive). Stricter than topic keywords —
# this is "is this even about consumer rights?" Otherwise r/Polska search for
# "sklep" returns shop owners' rants etc.
RELEVANCE_KEYWORDS: tuple[str, ...] = (
    "konsument",
    "konsumen",
    "reklamac",
    "zwrot",
    "rękojm",
    "gwaranc",
    "allegro",
    "olx",
    "vinted",
    "uokik",
    "rzecznik",
    "odstąp",
    "odstapi",
    "kurier",
    "paczk",
    "operator",
    "abonament",
    "umowa",
    "klauzul",
    "nieuczciw",
    "wadliw",
    "odszkodow",
    "sprzedawca",
    "sprzedawc",
)


def normalize_pl(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def anonymize(text: str) -> str:
    text = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "[EMAIL]", text)
    text = re.sub(r"\bu/[A-Za-z0-9_-]+\b", "[USER]", text)
    text = re.sub(r"\+?\d[\d \-]{7,}\d", "[PHONE]", text)
    return text


def anonymize_username(username: str | None) -> str:
    if not username or username == "[deleted]":
        return "deleted"
    h = hashlib.sha1(username.lower().encode("utf-8")).hexdigest()[:10]
    return f"sha1:{h}"


def extract_topics(*texts: str) -> list[str]:
    blob = " ".join(t.lower() for t in texts if t)
    hits: list[str] = []
    for tag, kws in TOPIC_KEYWORDS.items():
        if any(kw in blob for kw in kws):
            hits.append(tag)
    return hits


def is_consumer_relevant(*texts: str) -> bool:
    blob = " ".join(t.lower() for t in texts if t)
    return any(kw in blob for kw in RELEVANCE_KEYWORDS)


@dataclass
class QuestionRecord:
    question_id: str
    question: str
    context: str
    source: str
    source_url: str
    category: str
    thread_responses_count: int | None
    scrape_date: str = TODAY
    extracted_topics: list[str] = field(default_factory=list)
    # Reddit-specific extras (do not break schema; ingested as JSON anyway)
    reddit_score: int | None = None
    reddit_subreddit: str | None = None
    reddit_author_hash: str | None = None
    reddit_created_utc: float | None = None


class RedditFetcher:
    def __init__(self, rate_limit_sec: float = RATE_LIMIT_SEC) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.rate_limit_sec = rate_limit_sec
        self._last_fetch = 0.0
        self.blocked = False

    def get_json(self, url: str, *, retries: int = 2) -> dict[str, Any] | None:
        if self.blocked:
            return None
        wait = self.rate_limit_sec - (time.monotonic() - self._last_fetch)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(retries + 1):
            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT_SEC)
                self._last_fetch = time.monotonic()
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code in (401, 403):
                    logger.error(
                        "Reddit blocked us at %s (status=%d). Stopping.",
                        url,
                        resp.status_code,
                    )
                    self.blocked = True
                    return None
                if resp.status_code == 429:
                    backoff = 30 * (attempt + 1)
                    logger.warning("Reddit 429 — sleeping %ds", backoff)
                    time.sleep(backoff)
                    continue
                logger.warning("GET %s -> %d", url, resp.status_code)
            except (requests.RequestException, ValueError) as exc:
                logger.warning("GET %s ERR %s", url, exc)
            time.sleep(3.0 * (attempt + 1))
        return None


def reddit_search(
    fetcher: RedditFetcher,
    subreddit: str,
    query: str,
    *,
    limit: int = 100,
    sort: str = "relevance",
) -> list[dict[str, Any]]:
    """Return list of submission `data` dicts matching query in subreddit."""
    url = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        f"?q={requests.utils.quote(query)}"
        f"&restrict_sr=on&sort={sort}&limit={min(limit, 100)}"
    )
    resp = fetcher.get_json(url)
    if not resp:
        return []
    children = resp.get("data", {}).get("children", [])
    out = [c.get("data", {}) for c in children if c.get("kind") == "t3"]
    logger.info(
        "r/%s search(%r, sort=%s) -> %d posts", subreddit, query, sort, len(out)
    )
    return out


def reddit_iter(
    fetcher: RedditFetcher,
    subreddits: list[str],
    queries: list[str],
    *,
    incremental_output: Path | None = None,
) -> list[QuestionRecord]:
    """Iterate through (sub × query × sort) tuples.

    If ``incremental_output`` is provided, append each new record to the JSONL
    file as we go (so a 429-induced kill still leaves usable output).
    """
    seen_ids: set[str] = set()
    out: list[QuestionRecord] = []
    counter = 0
    out_fh = None
    if incremental_output is not None:
        incremental_output.parent.mkdir(parents=True, exist_ok=True)
        out_fh = incremental_output.open("w", encoding="utf-8")
    try:
        for sub in subreddits:
            for q in queries:
                if fetcher.blocked:
                    logger.error("Aborting further queries — fetcher blocked.")
                    return out
                for sort in ("relevance", "new"):
                    posts = reddit_search(fetcher, sub, q, sort=sort)
                    for p in posts:
                        pid = p.get("id")
                        if not pid or pid in seen_ids:
                            continue
                        seen_ids.add(pid)
                        title = normalize_pl(p.get("title", ""))
                        body = normalize_pl(p.get("selftext", "") or "")
                        if not p.get("is_self", False):
                            continue
                        if not (title or body):
                            continue
                        if not is_consumer_relevant(title, body):
                            continue
                        counter += 1
                        rec = QuestionRecord(
                            question_id=f"reddit_{counter:05d}",
                            question=title,
                            context=anonymize(body)[:2000],
                            source=f"reddit.com/r/{sub}",
                            source_url=f"https://www.reddit.com{p.get('permalink', '')}",
                            category=f"r/{sub}",
                            thread_responses_count=p.get("num_comments"),
                            extracted_topics=extract_topics(title, body),
                            reddit_score=p.get("score"),
                            reddit_subreddit=sub,
                            reddit_author_hash=anonymize_username(p.get("author")),
                            reddit_created_utc=p.get("created_utc"),
                        )
                        out.append(rec)
                        if out_fh is not None:
                            out_fh.write(
                                json.dumps(asdict(rec), ensure_ascii=False) + "\n"
                            )
                            out_fh.flush()
    finally:
        if out_fh is not None:
            out_fh.close()
    return out


def write_jsonl(records: list[QuestionRecord], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
    return len(records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--subreddits",
        type=str,
        default=",".join(DEFAULT_SUBREDDITS),
        help="Comma-separated subreddits to scan.",
    )
    parser.add_argument(
        "--queries-file",
        type=Path,
        default=None,
        help="Optional path to a text file with one query per line.",
    )
    parser.add_argument("--rate-limit-sec", type=float, default=RATE_LIMIT_SEC)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    subreddits = [s.strip() for s in args.subreddits.split(",") if s.strip()]
    if args.queries_file and args.queries_file.exists():
        queries = [
            line.strip()
            for line in args.queries_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
    else:
        queries = list(DEFAULT_QUERIES)

    fetcher = RedditFetcher(rate_limit_sec=args.rate_limit_sec)
    # Incremental writing — survives a mid-run 429 kill.
    records = reddit_iter(fetcher, subreddits, queries, incremental_output=args.output)
    n = len(records)
    status_path = args.output.with_suffix(".status.json")
    status_path.write_text(
        json.dumps(
            {
                "scrape_date": TODAY,
                "subreddits": subreddits,
                "queries_used": len(queries),
                "records_collected": n,
                "blocked_mid_scrape": fetcher.blocked,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info(
        "Wrote %d Reddit records -> %s (status: %s)", n, args.output, status_path
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
