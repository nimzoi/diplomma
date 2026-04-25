"""Fetch Polish Wikipedia articles relevant for JDG context.

Wikipedia API returns wikitext or rendered HTML. We grab the rendered HTML,
strip down to article body, save as `.html` (not PDF). Adds a defininitional
layer to the dataset that complements the legal acts and government guides.
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

from common import (
    DATA_DIR,
    fetch,
    log_fetch,
    magic_ok,
    now_iso,
    save_artifact,
    session_factory,
    load_manifest,
)
from topics import assign_topics

ARTICLES = [
    # (title, topic_hint)
    ("Jednoosobowa działalność gospodarcza", "jdg ceidg dzialalnosc nierejestrowana"),
    ("Centralna Ewidencja i Informacja o Działalności Gospodarczej",
     "ceidg rejestracja zawieszenie wznowienie zamkniecie"),
    ("Polska Klasyfikacja Działalności", "pkd 2007 ceidg pkd"),
    ("Podatek od towarów i usług w Polsce", "vat stawki rejestracja jpk"),
    ("Krajowy System e-Faktur", "ksef faktury ustrukturyzowane"),
    ("Podatek dochodowy od osób fizycznych w Polsce", "pit skala liniowy"),
    ("Ryczałt od przychodów ewidencjonowanych", "ryczalt stawki pkd pit-28"),
    ("Karta podatkowa", "karta podatkowa pit-16a"),
    ("Skala podatkowa", "skala podatkowa progresja"),
    ("IP Box", "ip box programisci 5%"),
    ("Podatkowa księga przychodów i rozchodów", "kpir ksiega ewidencja"),
    ("Zakład Ubezpieczeń Społecznych", "zus skladki preferencyjny"),
    ("Mały ZUS Plus", "maly zus plus art 18c"),
    ("Ulga na start", "ulga na start art 18 prawo przedsiebiorcow 6 miesiecy"),
    ("Składka zdrowotna", "skladka zdrowotna jdg ryczalt"),
    ("Rozporządzenie o ochronie danych osobowych", "rodo art 13 art 30 iod"),
    ("Inspektor ochrony danych", "iod rodo art 37 art 38"),
    ("Kodeks pracy (Polska)", "kodeks pracy umowa o prace urlop wypowiedzenie"),
    ("Umowa o pracę", "umowa o prace kodeks pracy art 25"),
    ("Umowa zlecenia", "umowa zlecenie art 734 kodeks cywilny"),
    ("Umowa o dzieło", "umowa o dzielo art 627 kodeks cywilny"),
    ("Działalność nierejestrowana", "dzialalnosc nierejestrowana art 5 prawo przedsiebiorcow"),
    ("Krajowa Administracja Skarbowa", "kas urzad skarbowy"),
    ("Biała lista podatników VAT", "biala lista vat wykaz podatnikow"),
    ("Jednolity Plik Kontrolny", "jpk vat jpk_v7"),
]

API = "https://pl.wikipedia.org/w/api.php"


def fetch_article(title: str, sess) -> bytes | None:
    """Get rendered HTML via the parse API."""
    params = {
        "action": "parse",
        "page": title,
        "format": "json",
        "prop": "text",
        "redirects": "1",
        "formatversion": "2",
    }
    from urllib.parse import urlencode
    url = f"{API}?{urlencode(params)}"
    res = fetch(url, sess)
    log_fetch({"ts": now_iso(), "url": url, "ok": res.ok, "status": res.status, "bytes": len(res.content)})
    if not res.ok:
        return None
    import json
    try:
        data = json.loads(res.content.decode("utf-8"))
    except Exception:
        return None
    if "error" in data:
        print(f"  api error: {data['error'].get('info','?')}")
        return None
    body = data.get("parse", {}).get("text", "")
    if isinstance(body, dict):
        body = body.get("*", "")
    if not body:
        return None
    # Wrap in minimal HTML doc
    final = f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<title>{title} — Wikipedia (PL)</title>
<base href="https://pl.wikipedia.org/wiki/">
</head>
<body>
<h1>{title}</h1>
<article>{body}</article>
<footer><p>Source: pl.wikipedia.org/wiki/{title.replace(' ', '_')}</p></footer>
</body>
</html>
"""
    return final.encode("utf-8")


def main() -> None:
    sess = session_factory()
    manifest = load_manifest()
    have_url = {r.get("url", "") for r in manifest}
    have_sha = {r.get("sha256", "") for r in manifest}
    saved = 0
    for title, hint in ARTICLES:
        url = f"https://pl.wikipedia.org/wiki/{title.replace(' ', '_')}"
        if url in have_url:
            continue
        time.sleep(0.5)
        content = fetch_article(title, sess)
        if not content or len(content) < 2000:
            print(f"FAIL  {title}")
            continue
        sha = hashlib.sha256(content).hexdigest()
        if sha in have_sha:
            continue
        have_sha.add(sha)
        topics = assign_topics(title, hint)
        if not topics:
            topics = ["ceidg_rejestracja"]
        slug = re.sub(r"[^A-Za-z0-9._\-]", "_", title)[:80]
        rel = Path("raw/wikipedia") / f"wiki_{slug}.html"
        save_artifact(
            content=content,
            rel_path=rel,
            url=url,
            source="wikipedia",
            topic_ids=topics,
            layer="L3",
            fmt="html",
            http_status=200,
            content_type="text/html; charset=utf-8",
            title=f"Wikipedia (PL): {title}",
            is_official=False,
            discovery_source="seed",
            extra_notes="Polish Wikipedia article (definitional context, L3)",
        )
        saved += 1
        print(f"OK    {title} -> {rel}")
    print(f"\n[wikipedia] saved={saved}")


if __name__ == "__main__":
    main()
