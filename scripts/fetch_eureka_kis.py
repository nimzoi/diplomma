"""Fetch KIS interpretacje indywidualne from eureka.mf.gov.pl POST API.

Discovered endpoint:
  POST /api/public/v1/wyszukiwarka/informacje/?size=N&page=K&sort=parametryPozycjonowania,asc
  body: {"filter":{...}, "columns":[...]}

We run the 10 queries from spec section 7.1, filter to IN_FORCE individual
interpretations from 2023+, fetch detail for each, save as HTML (interpretation
text + metadata).

The detail page URL pattern (observed): https://eureka.mf.gov.pl/informacje/podglad/{ID}
Backend: GET /api/public/v1/informacje/{ID} returns JSON with full text.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

from common import (
    fetch,
    log_fetch,
    now_iso,
    save_artifact,
    session_factory,
    load_manifest,
)
from topics import assign_topics

UA_CHROME = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

API_LIST = "https://eureka.mf.gov.pl/api/public/v1/wyszukiwarka/informacje/"
API_DETAIL = "https://eureka.mf.gov.pl/api/public/v1/informacje/"

# (query_phrase, topic_hint, max_results)
QUERIES = [
    ("ryczalt programista", "pit_ryczalt pit_ip_box pit_stawki_ryczalt_pkd", 10),
    ("IP Box programista", "pit_ip_box", 10),
    ("KUP samochod", "pit_kup pit_amortyzacja", 6),
    ("amortyzacja laptop", "pit_amortyzacja pit_kup", 6),
    ("ZUS preferencyjny", "zus_preferencyjny zus_ulga_na_start", 6),
    ("KPiR wydatki", "pit_kpir pit_kup", 6),
    ("VAT zwolnienie podmiotowe 200 tys", "vat_zwolnienie_200k vat_rejestracja", 6),
    ("dzialalnosc nierejestrowana", "ceidg_dzialalnosc_nierejestrowana", 6),
    ("zawieszenie dzialalnosci", "ceidg_zawieszenie", 5),
    ("test samozatrudnienia b2b", "kp_umowa_o_prace pit_skala", 6),
    ("skladka zdrowotna ryczalt", "zus_skladka_zdrowotna_jdg", 6),
    ("KSeF zwolnienie mikro", "vat_ksef", 5),
    ("wakacje skladkowe", "zus_wakacje_skladkowe", 5),
    ("Maly ZUS Plus", "zus_maly_zus_plus", 5),
    ("ulga na start", "zus_ulga_na_start", 5),
]

COLUMNS = [
    "KATEGORIA_INFORMACJI", "SYG", "DT_WYD", "AUTOR", "ID_INFORMACJI",
    "TEZA", "SLOWA_KLUCZOWE", "PRZEPISY", "ZAGADNIENIA",
    "STATUS_INFORMACJI", "DATA_REJESTRACJI",
]


def search(sess, phrase: str, size: int = 10) -> list[dict]:
    # Format observed from real SPA: searchQuery at top level, filter={}.
    body = {
        "filter": {},
        "columns": COLUMNS,
        "searchInFullPhrase": False,
        "searchInContent": True,
        "searchInSynonyms": False,
        "searchQuery": phrase,
        "warunkiDodatkowe": [],
    }
    url = f"{API_LIST}?size={size}&page=0&sort=parametryPozycjonowania,asc"
    r = sess.post(url, json=body, headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": UA_CHROME,
    }, timeout=30)
    if r.status_code != 200:
        return []
    try:
        data = r.json()
        return data.get("results", []) or []
    except Exception:
        return []


def fetch_detail(sess, info_id: str) -> dict | None:
    url = f"{API_DETAIL}{info_id}"
    r = sess.get(url, headers={"Accept": "application/json", "User-Agent": UA_CHROME}, timeout=30)
    if r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


def detail_to_html(detail: dict, info_id: str) -> bytes:
    """Render the API JSON detail (dokument.fields[] structure) as HTML."""
    fields = {}
    doc = detail.get("dokument") or {}
    for f in doc.get("fields", []) or []:
        k = f.get("key", "")
        v = f.get("value", "")
        if isinstance(v, list):
            v = "; ".join(str(x) for x in v)
        if k:
            fields[k] = str(v) if v is not None else ""

    syg = fields.get("SYG", "") or str(detail.get("id", info_id))
    teza = fields.get("TEZA", "")
    autor = fields.get("AUTOR", "")
    dtwyd = fields.get("DT_WYD", "")
    przepisy = fields.get("PRZEPISY", "")
    zagadnienia = fields.get("ZAGADNIENIA", "")
    tresc = (fields.get("TRESC_INTERESARIUSZ", "")
             or fields.get("TRESC_INFORMACJI", "")
             or fields.get("TRESC", "")
             or "")
    if not tresc:
        return b""

    title = f"Interpretacja KIS {syg}".strip()
    head = f"""<!doctype html>
<html lang="pl"><head>
<meta charset="utf-8"><title>{title}</title></head><body>
<h1>{title}</h1>
<p><b>Sygnatura:</b> {syg}</p>
<p><b>Data wydania:</b> {dtwyd}</p>
<p><b>Autor (kod):</b> {autor}</p>
<p><b>Przepisy (kody):</b> {przepisy}</p>
<p><b>Zagadnienia (kody):</b> {zagadnienia}</p>
<h2>Teza</h2><div>{teza}</div>
<h2>Treść interpretacji</h2><article>{tresc}</article>
<footer><p>Source: eureka.mf.gov.pl/informacje/podglad/{info_id}</p></footer>
</body></html>"""
    return head.encode("utf-8")


def main() -> None:
    sess = session_factory({"User-Agent": UA_CHROME})
    manifest = load_manifest()
    have_url = {r.get("url", "") for r in manifest}
    have_sha = {r.get("sha256", "") for r in manifest}
    saved = 0

    for phrase, hint, size in QUERIES:
        time.sleep(0.7)
        results = search(sess, phrase, size=size)
        print(f"\n>>> {phrase!r}: {len(results)} hits")
        for item in results:
            info_id = str(item.get("ID_INFORMACJI", "")).strip()
            if not info_id:
                continue
            url = f"https://eureka.mf.gov.pl/informacje/podglad/{info_id}"
            if url in have_url:
                continue
            time.sleep(0.4)
            detail = fetch_detail(sess, info_id)
            if not detail:
                continue
            content = detail_to_html(detail, info_id)
            if len(content) < 1500:
                continue
            sha = hashlib.sha256(content).hexdigest()
            if sha in have_sha:
                continue
            have_sha.add(sha)
            topics = assign_topics(item.get("TEZA", "") or "", hint, phrase)
            if not topics:
                topics = hint.split()[0:1] if hint else ["pit_skala"]
            syg = item.get("SYG", info_id).replace("/", "_").replace(".", "_")
            slug = re.sub(r"[^A-Za-z0-9._\-]", "_", syg)[:80]
            rel = Path("raw/kis") / f"kis_{slug}.html"
            save_artifact(
                content=content,
                rel_path=rel,
                url=url,
                source="kis",
                topic_ids=topics,
                layer="L3",
                fmt="html",
                http_status=200,
                content_type="text/html",
                title=f"KIS {item.get('SYG','')} — {(item.get('TEZA','') or '')[:120]}",
                last_modified=item.get("DT_WYD", ""),
                is_official=True,
                discovery_source="eureka_api",
                extra_notes=f"phrase={phrase!r}, autor={item.get('AUTOR','')}",
            )
            saved += 1
            if saved % 5 == 0:
                print(f"  saved {saved}")
    print(f"\n[kis] saved={saved}")


if __name__ == "__main__":
    main()
