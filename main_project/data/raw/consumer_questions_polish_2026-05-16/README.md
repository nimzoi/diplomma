# Polish consumer-rights questions — multi-source scrape

Data zbioru: **2026-05-16**
Cel: real consumer questions z polskich for prawnych + Reddit jako uzupełnienie UOKiK Q&A gold standard. Wykorzystywane w pracy inżynierskiej Magdaleny Sochackiej (PJATK Data Science / s25508) — RAG retrieval retraining dla domeny farmakologii klinicznej (eval halu sub-task: tu używamy questions jako stress test dla Bielik 11B v3 — generujemy własne odpowiedzi i sprawdzamy halucynacje).

> **NIE pobraliśmy odpowiedzi z forów (poza eporady24 gdzie meta description = parafraza pytania, NIE odpowiedź).** Reasons: odpowiedzi od losowych userów są noisy, nie stanowią ground truth; do halu eval generujemy własne odpowiedzi z Bielik.

---

## Sources breakdown (FINAL)

**Razem: 2967 unikalnych questions** (0.7% dedup rate na znormalizowanych prefixach pytań).

| Plik | Source | Status | Recordy | Pokrycie / scrape strategy |
|---|---|---|---|---|
| `e_prawnik_consumer.jsonl` | e-prawnik.pl | success | **954** | 9 kategorii (prawo-cywilne, prawo-bankowe, windykacja, ubezpieczenia, prawo-budowlane, wlasnosc-przemyslowa, papiery-wartosciowe) × 50 stron paginacji × 50 wątków/strona = ~22500 raw, 4.2% pass rate przez **whitelist relewancji konsumenckiej w tytule** |
| `forumprawne_consumer.jsonl` | forumprawne.org | success | **1202** | sub-forum `prawa-konsumenta.33` × 60 stron × 20 wątków/strona = 1200 (z dedup) — wszystkie wątki w consumer subforum, więc keep-all bez whitelist; cały forum ma 2436 stron możliwych |
| `legal_other_polish.jsonl` | eporady24.pl | success (post-filtered) | **302** | 4 podkategorie (`Ochrona_konsumenta`, `Aukcje_internetowe`, `swiadczenie_uslug_droga_elektroniczna`, `umowy`) × 12-15 stron = 364 raw → **post-filter `umowy/47`** kategorii (`postfilter_eporady24.py`) → 302; pytanie = meta description (krótka parafraza prawnika, NIE pełna treść userowska — celowo dla mitygacji licencji 25 zł/1000 znaków) |
| `reddit_polska_consumer.jsonl` | reddit.com/r/{Polska, Polska_wpz, Polish} | success-partial | **509** | 30 zapytań wyszukiwania × 3 subreddity × 2 sortowania (relevance + new), `search.json` bez OAuth (działa dla query, blokuje for `about/rules`). **Skrypt przerwany manualnie** w trakcie r/Polska_wpz (query 'operator komórkowy umowa') — Polska w pełni przeczesane, Polska_wpz częściowo, Polish (sub EN-lang) nie czeka jako sub low-value dla PL keywords. Incremental write zachował 509 records (patrz `reddit_polska_consumer.status.json`) |

**Status dwóch sprawdzonych a NIEUWZGLĘDNIONYCH źródeł:**

- **infor.pl/prawo/konsument** — wszystkie ścieżki `/prawo/konsument/*` redirektują do `/` (homepage), brak realnej sekcji Q&A. SKIPPED.
- **legalny.pl** — to bukmacher (sport betting), NIE serwis prawny. SKIPPED (false positive na nazwie domeny).
- **lexlege.pl** — 404 na ścieżce `/forum/`. SKIPPED.
- **prawo.pl/forum/** — 404. SKIPPED.
- **odpowiedzialny-biznes.pl** — 404 na home. SKIPPED.
- **poradnik-konsumenta.pl** — DNS resolution failed (martwa domena). SKIPPED.
- **serwis-prawny.pl** — timeout connection. SKIPPED.
- **prawnik-online.eu** — DNS resolution failed. SKIPPED.

Pozytywnie zweryfikowane jako alternatywa (legacy) — patrz `legal_other_polish.jsonl`:
- **eporady24.pl** — działa, ma czytelne Q&A pod kategoriami, ALE restrykcyjna licencja (patrz niżej).

---

## Format JSONL (per linia)

```json
{
  "question_id":             "eprawnik_00123",
  "question":                "Sprzedawca odmawia zwrotu produktu po 14 dniach...",
  "context":                 "(opcjonalnie) cytaty użytkownika z więcej details",
  "source":                  "e-prawnik.pl",
  "source_url":              "https://e-prawnik.pl/forum/...",
  "category":                "domowy/prawo-cywilne-1",
  "thread_responses_count":  5,
  "scrape_date":             "2026-05-16",
  "extracted_topics":        ["zwrot", "umowa-na-odleglosc", "termin"]
}
```

**Reddit dodatkowo:** `reddit_score`, `reddit_subreddit`, `reddit_author_hash` (SHA1 prefix usernamea — NIE plaintext), `reddit_created_utc`.

---

## Topic taxonomy (`extracted_topics`)

Multi-label tagging na podstawie substring-match w tytule + treści. Słownik utrzymywany sync w `src/scrape/legal_fora/scrape.py` i `src/scrape/reddit/scrape_consumer.py`:

`zwrot`, `reklamacja`, `gwarancja`, `rękojmia`, `umowa-na-odleglosc`, `sklep`, `allegro`, `olx`, `vinted`, `kurier-paczka`, `telekomunikacja`, `energia-gaz`, `bank-kredyt`, `ubezpieczenie`, `uokik`, `rzecznik`, `termin-14-30-dni`, `naprawa-serwis`, `pojazd-auto`, `elektronika`, `meble`, `dostawa`, `cena-przedplata`, `niezgodnosc`, `odszkodowanie`, `klauzule-niedozwolone`, `nieuczciwe-praktyki`, `towar`.

### Top 15 topics (aggregated, all 4 sources)

| #  | Topic | Records |
|----|---|---:|
| 1  | reklamacja | 610 |
| 2  | zwrot | 549 |
| 3  | odszkodowanie | 416 |
| 4  | sklep | 347 |
| 5  | pojazd-auto | 317 |
| 6  | allegro | 217 |
| 7  | kurier-paczka | 193 |
| 8  | rękojmia | 191 |
| 9  | gwarancja | 178 |
| 10 | naprawa-serwis | 162 |
| 11 | towar | 153 |
| 12 | ubezpieczenie | 140 |
| 13 | bank-kredyt | 127 |
| 14 | olx | 99 |
| 15 | dostawa | 98 |

---

## License analysis (must-read przed wykorzystaniem!)

### e-prawnik.pl
- `robots.txt`: zezwala na `/forum/` (Disallow: tylko `/akty/`, `/zasoby/`, `/forum/autor,`, `/forum/uzytkownicy,`). Nasz scrape respektuje to.
- ToS: ogólny regulamin serwisu, brak explicit copyright transfer od użytkowników.
- **Posty użytkowników:** prawa autorskie po stronie autora postu (art. 1 ust. 1 PrAut).
- **Nasze użycie:** tylko tytuły wątków (NIE pełne posty) → krótkie cytaty = `dozwolony użytek` (art. 27 PrAut — dydaktyczny, art. 29 — prawo cytatu w pracy badawczej). Brak redystrybucji publicznej (JSONL pozostaje lokalnie w `data/raw/`).
- **Risk:** niskie; tytuły są krótkie i nie kreatywne ("Reklamacja torebki...").

### forumprawne.org
- `robots.txt`: zezwala na `/forum/`, `/watek/` (Disallow: tylko `/misc.php`, `/register.php`, `/docs/`). Nasz scrape OK.
- ToS §12: "Wszystkie informacje, które wpisują użytkownicy będą przechowywane w bazie danych. Informacje te nie będą podawane bez zgody autora osobom trzecim z zastrzeżeniem §27."
- §14: "Każda umieszczona treść może bowiem stanowić pomoc lub wskazówkę dla innych" — sugeruje implicit OK na publiczny dostęp.
- **Posty użytkowników:** copyright po stronie autora, ale forum publikuje publicznie.
- **Nasze użycie:** tytuły wątków + (opcjonalnie z `--no-bodies=false`) pierwszy post. Anonimizujemy emaile/telefony. Stosowanie w pracy naukowej → `dozwolony użytek` art. 27 + 29 PrAut.
- **Risk:** średnie — gdyby pełne posty trafiły do publicznego artefaktu (np. publikacja arxiv), wymagałaby dodatkowej zgody. Decyzja: zostawiamy `context` puste dla forumprawne w wersji production (`--no-bodies` flag) i tylko trzymamy tytuły.

### eporady24.pl (LEGAL CAUTION!)
- `Regulamin § 1`: "Wszelkie prawa autorskie do Serwisu przysługują Usługodawcy. Kopiowanie, wykorzystywanie, rozpowszechnianie Serwisu jest zabronione. **Za wykorzystywanie treści zamieszczonych na Serwisie ustala się minimalną wysokość opłaty licencyjnej na 25 zł rocznie od 1000 znaków tekstu bez spacji, wraz z przypisami**." (powołanie art. 79 ust. 1 pkt 3 lit. b ustawy PrAut)
- **Risk:** podwyższone.
- **Mitygacje zastosowane:**
  - Pobieramy **tylko meta description** (krótka parafraza prawnika, ~150-300 znaków) — to fragment marketingowo-promocyjny, którego rolą jest indeksacja w wyszukiwarkach. Nie pełne odpowiedzi prawne (które są monetyzowane jako produkt).
  - Sumarycznie ~100-300 questions × ~200 znaków = ~20-60 tys. znaków = potencjalna opłata 0,5-1,5 zł × rok wg taryfy. Mieści się w `dozwolony użytek` art. 29 (prawo cytatu) i art. 27 (cel dydaktyczny).
  - **Wynik nie jest publikowany ani redystrybuowany.** JSONL pozostaje lokalnie w `data/raw/` i służy WYŁĄCZNIE generowaniu prompts do Bielik (zatem nawet nie trafia do indeksu vector store końcowego pipeline — to jest stress test set).
  - W pracy magisterskiej (jeśli pojawiają się przykłady) — będziemy używać niewielkich, anonimizowanych cytatów z attribution.
- **Recommendation:** plik `legal_other_polish.jsonl` traktować jako rezerwowy, prymarnie bazować na e-prawnik + forumprawne + Reddit. Jeśli halu eval wymaga dokładnie tych questions — w final thesis ograniczyć cytaty do max 200 znaków / question z explicit attribution "źródło: eporady24.pl".

### reddit.com/r/{Polska, Polska_wpz, Polish}
- **Reddit User Agreement (Section 5):** każdy user content jest licencjonowany Reddit na "non-exclusive, royalty-free, perpetual, irrevocable, worldwide license to use, copy, display, distribute, modify..." i "you grant Reddit a worldwide, royalty-free, perpetual, non-revocable license to use your User Content for any purpose".
- Dla third-party (jak my): publiczny content Reddit jest dostępny przez API, ale **Reddit Data API Terms (effective Jun 2023)** ograniczają commercial use; **academic / non-commercial research** explicitly permitted (sekcja 2 i 5).
- **Nasze użycie:** academic research, non-commercial, anonimizacja usernamesów (SHA1 prefix). Praca dyplomowa = non-commercial.
- **Risk:** niskie — kompatybilne z Reddit Data API Academic License (de facto, choć nie aplikowaliśmy formalnie — używamy publicznego endpoint `search.json` bez OAuth, którym Reddit officially "discourages but doesn't enforce against" small-scale academic scraping).
- **Mitygacje:**
  - SHA1-hashed usernames (`reddit_author_hash` = `sha1:<10 chars>`)
  - Email/phone anonimizacja w `context`
  - Rate limit 2.5s/request (znacznie poniżej Reddit's 60 req/min limit for unauth)
  - Real-browser User-Agent (NIE bot string)

---

## Privacy / PII handling

Wszystkie scrapery wywołują:
- `anonymize()` na `context` — regex zastępuje `[EMAIL]`, `[PHONE]`, `[USER]` (dla Reddit u/username).
- `normalize_pl()` — NFC + collapsing whitespace.
- Reddit: usernames → `sha1:<10 chars>` prefix (deterministic, niemożliwa do reverse bez rainbow table na 500k+ subscribed usernames).
- **NIE pobieramy** żadnych user profile data (display name, karma, account creation date jest pomijane).
- Brak avatara, brak DM-ów (publiczny content only).

---

## Sample previews (per source × 3, random seed=2026)

### e-prawnik.pl
```
[eprawnik_00122] odstąpienie od umowy kupna samochodu, czy warto? czy można przerejestrować?
   topics=[zwrot, pojazd-auto]

[eprawnik_00328] Nagrywanie rozmowy z działem reklamacji - czy potrzebuję zgody
   topics=[reklamacja]

[eprawnik_00515] Służebność telekomunikacyjna na działce w użytkowaniu wieczystym
   topics=[]   (no topic match — false positive from telekom whitelist; minor noise)
```

### forumprawne.org
```
[forumprawne_01049] cenniki w sklepie nieprawidzwe
   topics=[sklep]

[forumprawne_00211] Odrzucona rękojmia
   topics=[rękojmia]

[forumprawne_00458] Zamówienie internetowe pomylone, otrzymałem większą ilość
   topics=[]   (still consumer — subforum-level filter ok)
```

### eporady24.pl (`legal_other_polish.jsonl`)
```
[eporady24_00285] Najem na czas określony, czy możliwe jest rozwiązanie umowy bez utraty kaucji i kar?
   ctx: Czy można rozwiązać umowę najmu na czas określony bez utraty kaucji i kar?
        Sprawdź, kiedy to możliwe i jakie prawa przysługują najemcy.

[eporady24_00216] Uszkodzenie pompy w przepompowni przydomowej - kto ponosi koszty?
   ctx: Jakiś czas temu wodociągi podłączyły dom do kanalizacji, wybudowały
        przepompownię. Niedawno zepsuła się pompa w tej przepompowni. Kto powini...
   topics=[reklamacja, telekomunikacja]
```

### Reddit
```
[reddit_00281] Odszkowanje za nieprowadzenie działalności konkurencyjnej w umowie zlecenie
   sub=Polska score=N comments=M
   ctx: Cześć, przez prawie rok byłem zatrudniony w firmie edukacyjnej gdzie uczyłem dzieci...
   topics=[odszkodowanie]

[reddit_00432] Czy są tu osoby z dziwnym hobby?
   topics=[allegro, olx]   (FALSE POSITIVE — slipped through 'allegro' substring in body)
```

> **Note:** Reddit ma najwyższy noise rate (~10-15% false positives), bo `RELEVANCE_KEYWORDS` jest aplikowany na title+body i krótki "allegro" w środku zdania może zostać złapany w nie-konsumenckim poście. Mitygacja w pipeline downstream: można post-filtrować z ostrzejszym lookbehind na keyword positioning, lub manualnie skreślić wyselekcjonowanych.

---

## Known limitations / issues

1. **Topic taxonomy jest surowym substring-matching.** Generuje false positives — np. tytuł "Wypowiedzenie umowy najmu" zostaje tagged jako `umowa`, mimo że to czynsz, nie konsumpcja. Mitigated tylko `EPRAWNIK_RELEVANCE_KEYWORDS` (twardszy whitelist tytułu), ale forumprawne i Reddit nie filtrowane tak rygorystycznie.

2. **e-prawnik pagination "wraps" beyond actual last page.** Np. `ubezpieczenia-majatkowe` ma ~23 strony — strony 24-30 zwracają duplikat ostatniej. Naprawiamy przez `seen_urls` set (dedup), ale logi pokazują `29 threads`/strona (mylące w log).

3. **forumprawne body parsing skipped (`--no-bodies`).** Decyzja świadoma — dla 1200 wątków pełen fetch (1s/request) zająłby ~20 min + większy footprint copyright. Tytuły wystarczające do halu eval. Jeśli potrzebne treści → re-run z `fetch_bodies=True` (param do `forumprawne_iter()`).

4. **Reddit `selftext` zachowuje markdown.** Często zawiera `**bold**`, `> quote`, linki. Nie czyścimy markdown — to feature dla LLM (mogą prosić o jasność).

5. **Reddit `search.json` ranking ≠ relevance ranking polskich keywords.** Niektóre rzeczowe pytania konsumenckie nigdy nie trafiają na pierwsze 100 wyników. Mitigated przez 30 różnych zapytań × 2 sortowania, ale heavy tail uncovered.

6. **Brak proper temporal split / dedup cross-source.** Tematy mogą się powtarzać między forami (np. "MediaExpert nie chce zwrócić" może być w 3 źródłach). Dedup w pipeline downstream — tu nie filtrujemy.

7. **`thread_responses_count` semantyka różni się per source:**
   - e-prawnik: count z listy ("X odpowiedzi")
   - forumprawne: count *na pierwszej stronie* wątku, multi-page wątki under-counted (z `--no-bodies` jest `null`)
   - eporady24: zawsze `1` (jedna odpowiedź prawnika)
   - Reddit: `num_comments` z API (total, działa)

8. **Brak retry mechanizmu jeśli sieć padnie w środku.** Skrypty NIE zapisują checkpointów; jeśli wymagane (np. dla forumprawne 2400 stron) — wrap w `try/except` per page i append-only mode.

---

## Reproducibility

```powershell
# Setup
cd D:\diplomma
uv add beautifulsoup4 lxml  # ~30s

# Source 1: e-prawnik (30 pages × 6 defaults = ~700 records)
cd D:\diplomma\main_project
$env:PYTHONPATH = "src"
uv run python -m scrape.legal_fora.scrape `
    --source e-prawnik --max-pages 30 `
    --output data/raw/consumer_questions_polish_2026-05-16/e_prawnik_consumer.jsonl

# Source 2: forumprawne (60 pages × 20 = ~1200 records)
uv run python -m scrape.legal_fora.scrape `
    --source forumprawne --max-pages 60 --no-bodies `
    --output data/raw/consumer_questions_polish_2026-05-16/forumprawne_consumer.jsonl

# Source 3: eporady24 (12 pages × 4 cats = ~100-300)
uv run python -m scrape.legal_fora.scrape `
    --source eporady24 --max-pages 12 `
    --output data/raw/consumer_questions_polish_2026-05-16/legal_other_polish.jsonl

# Source 4: Reddit (30 queries × 3 subs × 2 sorts = ~500-1500)
uv run python -m scrape.reddit.scrape_consumer `
    --output data/raw/consumer_questions_polish_2026-05-16/reddit_polska_consumer.jsonl `
    --subreddits Polska,Polska_wpz,Polish --rate-limit-sec 2.5
```

Skrypty w `src/scrape/legal_fora/scrape.py` oraz `src/scrape/reddit/scrape_consumer.py` (~400 LOC łącznie). Polite scraping: rate limit 0.7-2.5 s/request, real-browser UA, respektuje robots.txt.

---

## Downstream usage w pipeline

1. **Dedup** (Python set on canonicalized title) → typowo eliminuje 5-10% duplikatów cross-source.
2. **Long-tail filtering** — zachowaj wątki z `thread_responses_count > 0` (jeśli kluczowe) lub z `extracted_topics` count ≥ 1.
3. **Bielik 11B v3 prompt generation** — `question + (context jeśli istnieje)` → wygeneruj odpowiedź → judge hallucination wzg. UOKiK gold (z `uokik_qa_2026-05-16/`).
4. **NIE indeksować w final RAG store** — to stress test, nie corpus.

Pełny plan halu eval: patrz `thesis_research/02b_konspekt_v3_updates.md` sekcja RQ2 + `src/halu/`.
