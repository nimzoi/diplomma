# UOKiK Q&A (consumer rights FAQ) — 2026-05-16

Scrape pytań i odpowiedzi konsumenckich z portalu **UOKiK (Urząd Ochrony
Konkurencji i Konsumentów)** — `https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/`.

Powód użycia: ready-made gold standard pairs **(pytanie → odpowiecz +
explicit cytowania artykułów ustaw)** dla benchmarku citation-grounded
polish RAG hallucination detection (Iteracja 0, praca dyplomowa
M. Sochacka, PJATK 2026).

## Zawartość

| Plik | Opis |
| --- | --- |
| `uokik_qa.jsonl` | 60 par Q&A, jedno JSON na linię |
| `uokik_meta.json` | Statystyki agregatu (counts, avg cit/pair) |
| `README.md` | Ten plik |

## Format `uokik_qa.jsonl`

```json
{
  "qa_id": "uokik_zagadnienia-ogolne_001",
  "question": "Kiedy jestem konsumentem?",
  "answer": "Konsument to osoba fizyczna...",
  "cited_articles": ["art. 22^1 Kodeksu cywilnego"],
  "category": "Ogolne",
  "source_url": "https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/zagadnienia-ogolne/",
  "scrape_date": "2026-05-16",
  "anchor": "faq001"
}
```

Pola:

- **`qa_id`** — `uokik_<slug-kategorii>_<numer>` (stabilny across re-scrapes,
  o ile UOKiK nie zmieni kolejności / liczby pytań).
- **`question`** — pytanie konsumenta. Prefix `N. ` jest usunięty.
- **`answer`** — odpowiedź ekspercka, normalizacja NFC, whitespace
  zcollapsowany. `Podstawa prawna: ...` jest usuwane (przeniesione do
  `cited_articles`).
- **`cited_articles`** — lista referencji do artykułów ustaw / kodeksów.
  Każdy artykuł osobno; statute name dołączony nawet jeśli oryginalnie
  współdzielony przez kilka artykułów (np. `art. 20 ust. 2 i art. 21
  ust. 1 ustawy o prawach konsumenta` → 2 osobne elementy listy).
  Indeks górny (`art. 22¹`) normalizowany do `art. 22^1`. Mianownik
  `ustawa` normalizowany do dopełniacza `ustawy`.
- **`category`** — etykieta kategorii (5 zdefiniowanych przez UOKiK).
- **`source_url`** — URL kategorii (UOKiK nie ma osobnych URL per pytanie;
  używaj `anchor` do nawigacji).
- **`scrape_date`** — ISO date scrapowania (= 2026-05-16).
- **`anchor`** — slug accordionu (`data-anchor` z HTML), np. `faq001`,
  `faq203`. Nie jest used w `#hash` na żywej stronie, ale stabilny ID.

## Statystyki agregatu

- **Total pairs:** 60
- **Pairs with at least 1 citation:** 55 / 60 (92%)
- **Average citations per pair:** 1.07 (range: 0–3)
- **Unique citations:** 52
- **Average answer length:** ~472 znaków

### Breakdown per kategoria

| Kategoria | Pairs |
| --- | ---: |
| Prawo do informacji (`obowiazki-informacyjne`) | 20 |
| Odstapienie od umowy (`odstapienie-od-umowy`) | 19 |
| Ogolne (`zagadnienia-ogolne`) | 12 |
| Reklamacja (`reklamacje`) | 6 |
| Telemarketing (`telemarketing`) | 3 |

### Pary bez cytowań

5/60 par nie ma `cited_articles`. To **nie jest bug parsera** — są to
pytania genuinely without `Podstawa prawna:` block w HTML UOKiK (zazwyczaj
pytania definicyjne / orientacyjne, np. „Gdzie można uzyskać informacje
dot. bezpłatnej pomocy konsumenckiej?"):

- `uokik_zagadnienia-ogolne_012`
- `uokik_obowiazki-informacyjne_015`
- `uokik_odstapienie-od-umowy_013`
- `uokik_reklamacje_002`
- `uokik_reklamacje_003`

## Metodologia scrape

Skrypt: `main_project/src/scrape/uokik/scrape_qa.py`.

1. **Discover:** root `/pytania-i-odpowiedzi/` listuje 5 podstron-kategorii.
   Wszystkie pytania renderowane inline w accordionie `su-spoiler`
   (Shortcodes Ultimate wp plugin) na stronie kategorii — **nie ma
   osobnych URL per pytanie**.
2. **Iterate categories:** dla każdej z 5 kategorii pobierz HTML.
3. **Parse per spoiler:**
   - `div.su-spoiler-title` → question (clean `N. ` prefix + icon span).
   - `div.su-spoiler-content` → answer body + blockquote z `Podstawa prawna:`.
   - `<sup>N</sup>` zamieniany na `^N` (zachowuje superscript info
     w plain text).
   - `blockquote` z `Podstawa prawna: <statute_refs>` ekstraktowane do
     `cited_articles`, usuwane z `answer`.
4. **Citation parsing** (`parse_citations`):
   - Pattern grupowy `(art. ... art. ...) <statute>` → lista artykułów,
     każdy z dołączonym statute name.
   - Splittery na `,` `;` ` i ` ` oraz ` tylko jeśli następuje `art.`
     (żeby nie chopnąć `art. 10 ust. 1 i 2`).
   - Obsługa kodeksów (cywilny, postępowania cywilnego, karny, wykroczeń),
     ustaw (`ustawy/ustawa o ...`), Praw (Prawa telekomunikacyjnego), oraz
     częściowo Rozporządzeń EU.
5. **Rate limit:** 1 req/s.

### Patterns cytowań rozpoznawane

```text
art. 22¹ Kodeksu cywilnego              → art. 22^1 Kodeksu cywilnego
art. 10 ust. 1 i 2 ustawy o ...         → 1 element listy (ust. 1 i 2 razem)
art. 20 ust. 2 i art. 21 ust. 1 ust...  → 2 osobne elementy
art. 577² Kodeksu cywilnego             → art. 577^2 Kodeksu cywilnego
art. 172 i 174 ust. 1 Prawa teleko...   → 1 element (range w pojedynczej ref)
art. 35 ustawa o prawach konsumenta     → normalized to ustawy
```

Znany limit: rzadkie rozporządzenia UE z opisowym tytułem zawierającym
przecinki (1/60 par) skutkują utratą referencji do rozporządzenia — KC
część jest parsowana.

## Sanity check — sample 5 pairs (manual annotation)

| qa_id | citation parseable correctly? | comment |
| --- | --- | --- |
| `uokik_zagadnienia-ogolne_001` | TAK | `art. 22¹ KC` → `art. 22^1 Kodeksu cywilnego`, superscript preserved |
| `uokik_obowiazki-informacyjne_002` | TAK | Single canonical citation |
| `uokik_odstapienie-od-umowy_001` | TAK | 2 artykuły, statute shared, `ustawa` → `ustawy` normalized |
| `uokik_reklamacje_001` | TAK | KC, single citation |
| `uokik_telemarketing_001` | TAK | `Prawa telekomunikacyjnego` recognized (non-Kodeks/non-ustawa pattern) |

## Sample 5 par (preview)

### `uokik_zagadnienia-ogolne_001` (Ogolne, anchor `faq001`)

**Q:** Kiedy jestem konsumentem?

**A:** Konsument to osoba fizyczna dokonująca z przedsiębiorcą czynności
prawnej niezwiązanej bezpośrednio z jej działalnością gospodarczą lub
zawodową. Przykład Jan jest konsumentem, jeżeli kupi dziecku laptop;
nie będzie nim jednak, gdy kupi laptop dla firmy i pozwoli dziecku
sporadycznie z niego korzystać. Uznanie za konsumenta ma istotne
znaczenie prawne – od tego często zależy jakie przepisy zostaną
zastosowane do oceny całej transakcji. W wielu przypadkach sytuacja
prawna konsumenta jest z góry wzmacniana przez przepisy.

**cited_articles:** `["art. 22^1 Kodeksu cywilnego"]`

---

### `uokik_obowiazki-informacyjne_002` (Prawo do informacji, anchor `faq102`)

**Q:** Czy sklep internetowy musi posiadać numer telefonu do kontaktu
z konsumentami?

**A:** Tak, sklep internetowy powinien posiadać kontaktowy numer telefonu
i poinformować o nim konsumenta przed zawarciem umowy (podobnie jak
o adresie przedsiębiorstwa oraz adresie poczty elektronicznej).

**cited_articles:** `["art. 12 ust. 1 pkt 3 ustawy o prawach konsumenta"]`

---

### `uokik_odstapienie-od-umowy_001` (Odstapienie od umowy, anchor `faq301`)

**Q:** Konsument zawarł przez telefon umowę z firmą telekomunikacyjną
i zażądał rozpoczęcia jej wykonywania przed terminem na odstąpienie. Czy
ma prawo odstąpić od tej umowy?

**A:** Tak, gdyż umowa o świadczenie usług telekomunikacyjnych zawarta
na odległość (np. przez telefon) lub poza lokalem przedsiębiorstwa
podlega ustawie o prawach konsumenta. Konsument może od niej odstąpić
w terminie 14 dni od dnia jej zawarcia bez podawania przyczyn. (...
proporcjonalne rozliczenie świadczenia spełnionego do chwili
odstąpienia ...)

**cited_articles:** `["art. 15 ust. 3 ustawy o prawach konsumenta",
"art. 35 ustawy o prawach konsumenta"]`

---

### `uokik_reklamacje_001` (Reklamacja, anchor `faq203`)

**Q:** Jakie zasady reklamacji obowiązują w przypadku zakupu
nieruchomości?

**A:** Do umów sprzedaży nieruchomości zawieranych przez konsumenta
z przedsiębiorcą (w szczególności z deweloperem) stosuje się przepisy
o rękojmi.

**cited_articles:** `["art. 556 Kodeksu cywilnego"]`

---

### `uokik_telemarketing_001` (Telemarketing, anchor `faq401`)

**Q:** Do konsumenta dzwoni konsultant z propozycją uczestnictwa
w pokazie i kupna towaru (sprzedaż poza lokalem przedsiębiorstwa), bądź
też z propozycją zawarcia umowy przez telefon. Twierdzi, że numer
telefonu został wybrany losowo. Czy to jest dopuszczalne, jeżeli
konsument nie wyraził uprzedniej zgody na taki kontakt telefoniczny?

**A:** Nie, gdyż zakazane jest używanie telefonów do celów marketingu
bezpośredniego, chyba że konsument przedtem wyraził na to zgodę. Zgoda
nie powinna być domniemana lub dorozumiana z oświadczenia o innej
treści. Może być wyrażona drogą elektroniczną (pod warunkiem jej
utrwalenia i potwierdzenia przez konsumenta), jak również w każdym
czasie wycofana – w sposób prosty i wolny od opłat.

**cited_articles:** `["art. 172 i 174 ust. 1 Prawa telekomunikacyjnego"]`

## Licencja

Treść UOKiK to **materiały urzędowe** w rozumieniu **art. 4 pkt 2 ustawy
z dnia 4 lutego 1994 r. o prawie autorskim i prawach pokrewnych** —
nie stanowią przedmiotu prawa autorskiego (public domain de facto).

Cytat za UOKiK regulaminem portalu (https://uokik.gov.pl): treści można
swobodnie wykorzystywać z podaniem źródła. Polityka prywatności i terms
of service nie zabraniają scrape do celów badawczych.

**Atrybucja:** w pracach pochodnych podawać "Źródło: UOKiK,
https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/, scrape
2026-05-16".

## Re-run

```bash
cd D:/diplomma/main_project
uv run python -m src.scrape.uokik.scrape_qa \
    --output ../data/raw/uokik_qa_2026-05-16
```

Polityka rescrape: UOKiK Q&A jest aktualizowane sporadycznie po zmianach
ustawowych. Przy każdym rescrape sprawdź `total_pairs` vs `60` — jeśli
liczba pytań się zmieniła, IDs są nadal stabilne w obrębie tej samej
kategorii (zachowują kolejność z HTML).

## Limity i caveats (dla benchmarku)

- **N=60 par to mało** dla pełnego eval setu — UOKiK Q&A można użyć
  jako *gold standard subset*, dopełnić innymi źródłami (np. ISAP,
  Rejestr Klauzul Niedozwolonych UOKiK, infor.pl Q&A).
- **Domena to consumer rights — nie pharmacology.** Ta data jest
  out-of-scope dla głównego use case pracy (farmakologia kliniczna),
  ale citation-grounded RAG patterns przenoszą się — `Podstawa prawna:
  <statute>` jest analogiczne do `Zgodnie z art. X Prawa
  Farmaceutycznego` w ChPL/Ulotka pairing (RQ5).
- **Statute strings są raw z UOKiK** — nie są zmapowane na konkretne
  publication IDs (np. nie ma linka do ISAP entry). Dla downstream
  use w benchmarku grounded retrieval rekomendowane: dorobić mapping
  table (`ustawy o prawach konsumenta` → `Dz.U. 2014 poz. 827` etc.).
- **Brak hard negative pairs.** Q i A są bezpośrednio sąsiadujące —
  dla negative samples (false-citation detection) trzeba samplować z
  innych Q&A lub generować synthetic.
