"""Hot-2025/2026 collector — KIS individual interpretacje (eureka.mf.gov.pl).

Reuses the discovered POST API contract from fetch_eureka_kis.py.
Adds queries targeting the 11 hot topics:
  - estoński CIT
  - DAC7 / platformy cyfrowe
  - JPK_CIT / księgi 2026
  - ulga ekspansja / prototyp / robotyzacja / B+R
  - przekształcenie JDG -> sp. z o.o.
  - faktoring / cesja / split payment
  - kasa fiskalna online
  - de minimis
  - cudzoziemcy
  - CRBR (rzadkie w KIS, ale spróbujemy)
  - art. 22 KP / b2b vs UOP
"""
from __future__ import annotations

import hashlib
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
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

QUERIES: list[tuple[str, str, int]] = [
    ("estonski CIT ryczalt od dochodow spolek", "estonski_cit", 8),
    ("ukryte zyski estonski CIT", "estonski_cit", 6),
    ("CIT-8E warunki", "estonski_cit", 5),
    ("DAC7 platformy cyfrowe", "dac7_platformy", 6),
    ("operator platformy DAC7", "dac7_platformy", 5),
    ("ulga na ekspansje", "ulga_ekspansja_prototyp_robotyzacja", 6),
    ("ulga na prototyp", "ulga_ekspansja_prototyp_robotyzacja", 5),
    ("ulga na robotyzacje art 38eb", "ulga_ekspansja_prototyp_robotyzacja", 5),
    ("ulga badawczo rozwojowa B+R", "ulga_ekspansja_prototyp_robotyzacja", 5),
    ("przeksztalcenie jednoosobowej dzialalnosci spolka", "przeksztalcenie_jdg_spzoo", 6),
    ("art 5841 ksh przeksztalcenie przedsiebiorcy", "przeksztalcenie_jdg_spzoo", 5),
    ("faktoring koszty uzyskania przychodow", "faktoring_cesja_wierzytelnosci", 6),
    ("cesja wierzytelnosci podatek", "faktoring_cesja_wierzytelnosci", 5),
    ("mechanizm podzielonej platnosci split payment", "faktoring_cesja_wierzytelnosci", 5),
    ("JPK_CIT JPK_KR_PD obowiazek", "jpk_cit_jpk_kr", 5),
    ("kasa fiskalna online obowiazek", "kasa_fiskalna_online", 5),
    ("ulga na zakup kasy fiskalnej", "kasa_fiskalna_online", 5),
    ("pomoc de minimis 300 tys", "pomoc_de_minimis", 5),
    ("zezwolenie na prace cudzoziemca", "zatrudnianie_cudzoziemcow", 5),
    ("oswiadczenie o powierzeniu pracy cudzoziemcowi", "zatrudnianie_cudzoziemcow", 5),
    ("CRBR beneficjent rzeczywisty", "crbr_beneficjent_rzeczywisty", 5),
    ("art 22 kodeksu pracy samozatrudnienie", "b2b_zmiana_na_uop", 6),
    ("ukryte zatrudnienie b2b", "b2b_zmiana_na_uop", 5),
]

COLUMNS = [
    "KATEGORIA_INFORMACJI", "SYG", "DT_WYD", "AUTOR", "ID_INFORMACJI",
    "TEZA", "SLOWA_KLUCZOWE", "PRZEPISY", "ZAGADNIENIA",
    "STATUS_INFORMACJI", "DATA_REJESTRACJI",
]


def search(sess, phrase: str, size: int = 8) -> list[dict]:
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
    try:
        r = sess.post(url, json=body, headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": UA_CHROME,
        }, timeout=30)
        if r.status_code != 200:
            return []
        return r.json().get("results", []) or []
    except Exception:
        return []


def fetch_detail(sess, info_id: str) -> dict | None:
    url = f"{API_DETAIL}{info_id}"
    try:
        r = sess.get(url, headers={"Accept": "application/json", "User-Agent": UA_CHROME}, timeout=30)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def detail_to_html(detail: dict, info_id: str) -> bytes:
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
    by_topic: dict[str, int] = {}

    for phrase, hint, size in QUERIES:
        time.sleep(0.7)
        results = search(sess, phrase, size=size)
        print(f">>> {phrase!r}: {len(results)} hits ({hint})")
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
            def _coerce(v):
                if v is None:
                    return ""
                if isinstance(v, list):
                    return " ".join(str(x) for x in v)
                return str(v)
            topics = assign_topics(_coerce(item.get("TEZA")),
                                   _coerce(item.get("ZAGADNIENIA")),
                                   phrase) or []
            if hint not in topics:
                topics.append(hint)
            syg = item.get("SYG", info_id).replace("/", "_").replace(".", "_")
            slug = re.sub(r"[^A-Za-z0-9._\-]", "_", syg)[:80]
            rel = Path("raw/kis") / f"kis_hot_{slug}.html"
            save_artifact(
                content=content, rel_path=rel, url=url, source="kis",
                topic_ids=topics, layer="L3", fmt="html", http_status=200,
                content_type="text/html", title=f"KIS {item.get('SYG','')} — {(item.get('TEZA','') or '')[:120]}",
                last_modified=item.get("DT_WYD", ""), is_official=True,
                discovery_source="eureka_api_hot",
                extra_notes=f"phrase={phrase!r}, hot_hint={hint}",
            )
            saved += 1
            by_topic[hint] = by_topic.get(hint, 0) + 1
    print(f"\n[hot kis] saved={saved}")
    for k, v in sorted(by_topic.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
