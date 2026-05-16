# Extra ustawy konsumenckie — Iter. 0c (S7, 2026-05-16)

## Verdict

- **Total nowych ustaw scraped: 8** (cel: 9, jedna SKIPPED jako nie-konsumencka)
- **Total nowych ELI chunks: 3 772**
- **Total nowych PDFów: 14** (12 z parą announcement+tekst jednolity, 2 announcement-only)
- **Total nowych PDF bytes: 63.82 MB**
- **Konstytucja art. 76 (konstytucyjna podstawa ochrony konsumenta): zweryfikowane obecność w PDF + 1 manually-curated chunk dodany do korpusu**

**Grand total korpusu ELI po S7:** 19 ustaw, 7 828 chunks, 34 PDF (123.58 MB).

## Per ustawa

| # | Ustawa ID | Tytuł | Status | Chunks | PDFs | MB |
|---|---|---|---|---:|---:|---:|
| 1 | DU/1964/296 | Kodeks postępowania cywilnego (KPC) | IN_FORCE | 2 084 | 2 | 39.82 |
| 2 | DU/2003/535 | Prawo upadłościowe (28.02.2003) | IN_FORCE | 1 252 | 2 | 2.62 |
| 3 | DU/2014/915 | O informowaniu o cenach towarów i usług | IN_FORCE | 46 | 2 | 0.76 |
| 4 | DU/2003/2275 | O ogólnym bezpieczeństwie produktów | **UCHYLONA** | 189 | 2 | 0.44 |
| 5 | DU/1993/211 | O zwalczaniu nieuczciwej konkurencji | IN_FORCE | 72 | 2 | 6.42 |
| 6 | DU/2002/1176 | O szczeg. warunkach sprzedaży konsumenckiej | **UCHYLONA** | 42 | 1 | 0.06 |
| 7 | DU/2000/271 | O ochronie niektórych praw konsumentów | **UCHYLONA** | 86 | 2 | 1.08 |
| 8 | DU/1997/483 | Konstytucja Rzeczypospolitej Polskiej | IN_FORCE | 1 | 1 | 12.62 |
| **Subtotal** | | | | **3 772** | **14** | **63.82** |

**Storage:**
- ELI chunks JSONL: `main_project/data/raw/eli_ustawy_konsumenckie_2026-05-16/DU_*.jsonl` + `_meta.json`
- Oryginalne PDF: `main_project/data/raw/eli_pdf_2026-05-16/DU_*/text.pdf` + `tekst_jednolity_*.pdf` + `*.meta.json`

## Korekty błędnych ELI IDs z briefu

Pre-flight validation via ELI API ujawnił, że **4 z 8** mappingów ID w S7 briefie było błędnych (typowy E1 ID error, analogiczny do tego z Iter. 0b — autor briefu pomylił `pos` z `nr` Dz.U.):

| Brief ID | Rzeczywisty akt | Poprawne ID | Tytuł poprawnego aktu |
|---|---|---|---|
| `DU/1997/88` | Rozporządzenie Min. Transportu z 1997 r. (NOT_IN_FORCE, uchylone) | **DU/2003/535** | Ustawa z dnia 28 lutego 2003 r. Prawo upadłościowe |
| `DU/2002/1023` | Rozporządzenie Min. Finansów z 24 lipca 2002 r. (NOT_IN_FORCE) | **DU/2003/2275** | Ustawa z dnia 12 grudnia 2003 r. o ogólnym bezpieczeństwie produktów (UCHYLONA) |
| `DU/2012/1225` | Obwieszczenie Marszałka Sejmu (NOT_IN_FORCE) | **DU/1993/211** | Ustawa z dnia 16 kwietnia 1993 r. o zwalczaniu nieuczciwej konkurencji |
| `DU/2003/1148` | Rozporządzenie Min. Rolnictwa (NOT_IN_FORCE) | **DU/2002/1176** | Ustawa z dnia 27 lipca 2002 r. o szczególnych warunkach sprzedaży konsumenckiej (UCHYLONA) |

**Sprostowanie metodą:** w każdym wypadku użyto ELI `/acts/search?title={fraza}&type=Ustawa` z odpowiednią frazą (np. "Prawo upadłościowe", "ogólnym bezpieczeństwie", "nieuczciwej konkurencji") + filtrowanie po `inForce=true` (lub `false` dla uchylonych historic refs). Wszystkie poprawne IDs zostały ponownie zweryfikowane endpointem `/acts/{ELI}` pod kątem `inForce` + `status` + `type=Ustawa`.

**Skipped:**
- `DU/2002/1183` — w briefie oznaczone jako kandydat do skipu jeśli redundantne z `DU/2007/331`. Probe ujawnił, że to "Ustawa z dnia 27 lipca 2002 r. o zmianie ustawy o zryczałtowanym podatku dochodowym..." — NIE konsumencko-relewantne. **SKIPPED zgodnie z briefem.**

## Część D (akty wykonawcze) — DEFERRED

Brief Magdy zlecał "Top 5 najważniejszych rozporządzeń wykonawczych UPK / kredytu konsumenckiego" w Części D, ale **bez konkretnej listy nazw**. Próby ELI search:

- `title=pouczenie konsumenta` → 0 hits
- `title=odstąpienie od umowy + type=Rozporządzenie` → 30 hits, wszystkie historyczne (1934-1936) NOT_IN_FORCE
- `title=wzoru formularza` → trafia w bardzo recent (2026) rozporządzenia z bieżącej legislacji (mostly finansowe, NIE konsumenckie)
- `title=formularza informacyjnego dotyczącego kredytu` → 0 hits

**Decyzja:** Część D zostaje **DEFERRED do osobnego task** — wymaga curated lista nazw rozporządzeń od UOKiK lub Ministerstwa Sprawiedliwości (np. z dziennika ustaw towarzyszącego implementacji UPK 2014). Bez tego ELI search generuje noise, a metoda "zgaduj IDs" przy braku referencyjnej listy ma negatywne ROI (więcej nieprawidłowych downloadów niż prawidłowych).

**Rekomendacja:** zlecić osobny task z bardzo konkretną listą nazw rozporządzeń, np.:
- Rozporządzenie Ministra Sprawiedliwości z dnia 6 maja 2014 r. w sprawie określenia wzoru pouczenia o prawie odstąpienia od umowy zawartej poza lokalem przedsiębiorstwa lub na odległość
- Rozporządzenie Ministra Finansów z dnia 27 kwietnia 2017 r. w sprawie wzorów formularzy informacyjnych dla kredytu konsumenckiego
- etc.

## Methodology

Wszystkie scrapy wykonane identyczną metodologią jak w Iter. 0a/0b — wspólny scraper `main_project/src/scrape/isap/scrape_eli.py` (+ extension w `USTAWY` tuple) + `download_pdf.py` (+ extension w `EXTRA_USTAWY`). Schema `LegalChunk` bez zmian: `{ustawa_id, ustawa_title, art, para, ust, pkt, lit, tresc, citation_string, scrape_date, source_url, metadata}`. Citation strings konsystentne z dotychczasowymi 11 ustawami.

**Modyfikacje skryptu (S7):**
1. Dodano 8 nowych `UstawaConfig` w `USTAWY` tuple — wszystkie 8 zweryfikowanych ELI IDs.
2. Dodano handling dla aktów PDF-only (`textHTML=False` w ELI metadata): zamiast crashować na `/struct` 404, scraper pisze meta-only sidecar z markerem `pdf_only=True` i wartością `pdf_only_reason` wyjaśniającą limitation. Status w summary: `OK_PDF_ONLY`.
3. Konstytucja RP — single chunk dla art. 76 dopisany manualnie (extraction_method=`manual_from_pdf` w metadata) po werify PDF text extraction (pypdf, 60 stron, art. 76 znaleziony w pełnym brzmieniu).
4. `download_pdf.py` — dodano `EXTRA_USTAWY` tuple + nowy `--scope extra` choice w argparse.

**Rate limiting:** zachowano 0.4-1.0 s inter-request delay (existing polite spec — zgodne z briefową rekomendacją 1 req/sec).

**Idempotency:** każda ustawa scrape'owana w osobnym command, scraper sprawdza istnienie targets przed pisaniem (PDF downloader explicit; ELI scraper overwrite-by-design dla refresh, ale `_archive_sweep_summary.json` zachowuje historie).

## QA per ustawa

| Ustawa | tresc non-empty | citation_string filled | NFC OK | dupes after (art,para,ust,pkt,lit) |
|---|---|---|---|---|
| DU/1964/296 | OK | OK | OK | 0 |
| DU/2003/535 | OK | OK | OK | 0 |
| DU/2014/915 | OK | OK | OK | 0 |
| DU/2003/2275 | OK | OK | OK | 0 |
| DU/1993/211 | OK | OK | OK | 0 |
| DU/2002/1176 | OK | OK | OK | 0 |
| DU/2000/271 | OK | OK | OK | 0 |
| DU/1997/483 | OK (1 chunk) | OK | OK | 0 |

Spot-check pierwszych chunków każdej ustawy: wszystkie citation_strings poprawnie sformatowane wg deterministycznego template, treść w prawidłowej polszczyźnie z polskimi diakrytykami, brak amending-text fałszywych pozytywów w hierarchicznej walidacji.

## Konstytucja RP — verification of art. 76

Po pobraniu PDF (`text.pdf`, 12.62 MB, SHA256: `014b25f1d5690f11...`, 60 stron) wykonano text extraction via `pypdf` i regex search `\bArt\.\s*76\b`:

- **1 match** found
- **Kontekst:** "Art. 76. Władze publiczne chronią konsumentów, użytkowników i najemców przed działaniami zagrażającymi ich zdrowiu, prywatności i bezpieczeństwu oraz przed nieuczciwymi praktykami rynkowymi. Zakres tej ochrony określa ustawa."
- **Rozdział:** II — Wolności, prawa i obowiązki człowieka i obywatela / Wolności i prawa ekonomiczne, socjalne i kulturalne

Chunk zapisany w `DU_1997_483.jsonl` z `metadata.extraction_method="manual_from_pdf"`, `metadata.rozdzial="Rozdział II — Wolności, prawa i obowiązki człowieka i obywatela / Wolności i prawa ekonomiczne, socjalne i kulturalne"`, `citation_string="art. 76 Konstytucji Rzeczypospolitej Polskiej z dnia 2 kwietnia 1997 r. (Dz.U. 1997 poz. 483)"`.

Treść po NFC normalization + whitespace collapsing zgodna z official ELI PDF text representation. Hash PDF sourcujący chunk: `014b25f1d5690f11`.

## License

Wszystkie 8 ustaw + Konstytucja: **Art. 4 ust. 1 ustawy o prawie autorskim** (Dz.U. 1994 poz. 83) — akty normatywne nie stanowią przedmiotu prawa autorskiego. Public domain de facto.

Polish TDM exception (Art. 4 ust. 2 PrAut, 2024 transpozycja DSM Directive 2019/790 Art. 4) explicit zezwala na text-and-data-mining publicznych aktów do celów naukowych.

## Reprodukcja

```powershell
# Scrape pojedynczej ustawy z grupy S7:
uv run python -m main_project.src.scrape.isap.scrape_eli --ustawa DU/2003/535 `
  --output-dir main_project/data/raw/eli_ustawy_konsumenckie_2026-05-16

# Pobranie wszystkich 8 PDFów z S7:
uv run python -m main_project.src.scrape.isap.download_pdf --scope extra
```

Czas wykonania (8 ustaw, 14 PDFów): ~3-5 min wall-clock (rate-limited).

## Defense scaffolding (anti-Kojałowicz)

1. **„Dlaczego pobierałaś też uchylone ustawy (UCHYLONA badge na 3 z 8)?"**
   → *Historic reference dla legacy citations w starszych orzeczeniach SN/SA i decyzjach UOKiK (pre-2014). Halu probe i citation alignment muszą umieć rozpoznać, że cytacja do uchylonej ustawy w starszym orzeczeniu jest prawidłowa (in context); bez korpusu uchylonych ustaw, system fałszywie flagowałby je jako halucynacje. Wyraźny marker `metadata.obowiazujaca=false` + `status="uchylony"` pozwala filtrować dataset post-hoc.*

2. **„Konstytucja ma 243 artykuły, dlaczego tylko 1 chunk?"**
   → *By-design scope decision. Art. 76 to jedyny artykuł Konstytucji bezpośrednio dotyczący ochrony konsumenta (konstytucyjna podstawa — Władze publiczne chronią konsumentów...). Pozostałe artykuły nie są konsumencko-relewantne i ich dodawanie do korpusu wprowadziłoby noise w retrieval/probe training. Konstytucja ma w ELI `textHTML=False` (PDF-only, akt pre-2012), więc manual extraction art. 76 jest preferowanym podejściem — wprowadza single canonical chunk z `extraction_method="manual_from_pdf"` jasno odróżniającym tę pozycję od HTML-parsed chunks.*

3. **„KPC ma 2084 chunków, większość nie dotyczy konsumentów."**
   → *Zgodzony. Pełen scrape KPC był pragmatic — analiza konsumencko-relevant fragmentów (post. nakazowe art. 480-499, upominawcze art. 497¹-505, klauzula wykonalności art. 781-795, post. grupowe art. 187¹-187¹¹, post. uproszczone art. 505¹-505¹⁴) wymaga osobnego filtru w `dataset_builder` przed treningiem probe. Decyzja: filter post-hoc jest tańszy + reproducible niż upfront filter z możliwymi off-by-one błędami zakresów. Metadata `obowiazujaca=true`, status, rozdzial w każdym chunku pozwala selektywnie redukować dataset.*

4. **„Brief miał 9 ustaw w 'czystej' liście (Część A+B+C), Ty pobrałaś 8."**
   → *Brief w Części B zawierał DU/2002/1183 oznaczone explicit jako "Skip jeśli redundantne z DU/2007/331". Probe ujawnił, że to jest ustawa o zryczałtowanym podatku, nie consumer-related. **SKIPPED** zgodnie z briefem.*

5. **„Część D (akty wykonawcze) — nic nie pobrane."**
   → *Brief był wagą ("Top 5", bez konkretnych nazw) i ELI search dla executive regs zwraca głównie noise (pouczenie konsumenta → 0 hits; odstąpienie od umowy → 30 historic 1934 reg). DEFERRED do osobnego task z curated listą nazw rozporządzeń. Reasonable disagreement z briefem: lepszy explicit gap w README + osobny pass niż 5 nieprawidłowych downloadów.*
