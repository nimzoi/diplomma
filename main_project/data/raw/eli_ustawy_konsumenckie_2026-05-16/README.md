# ELI corpus — polskie ustawy konsumenckie (2026-05-16)

Pobrane przez `scrape_eli.py` z ELI API (`api.sejm.gov.pl/eli`). Korpus chunks
dla citation-grounded polskiego RAG (deterministyczne źródłowanie per
art./§/ust./pkt./lit.).

**Skrypt:** `main_project/src/scrape/isap/scrape_eli.py`
**Data scrape:** 2026-05-16
**Łącznie:** 2 123 chunks, 2 157 918 bajtów (~2.1 MB)

## Status per ustawa

| ID | Tytuł | Status | Chunks | Plik |
|---|---|---|---|---|
| DU/2014/827 | Ustawa o prawach konsumenta | OK | 240 | `DU_2014_827.jsonl` |
| DU/1964/93 | Kodeks cywilny (art. 384-385, 535-581) | OK | 92 | `DU_1964_93.jsonl` |
| DU/2007/1206 | Ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym | OK | 113 | `DU_2007_1206.jsonl` |
| DU/2007/331 | Ustawa o ochronie konkurencji i konsumentów | OK | 500 | `DU_2007_331.jsonl` |
| DU/2011/1175 | Ustawa o usługach płatniczych | OK | 888 | `DU_2011_1175.jsonl` |
| DU/2016/1823 | Ustawa o pozasądowym rozwiązywaniu sporów konsumenckich | OK | 290 | `DU_2016_1823.jsonl` |

Wszystkie ustawy zostały pobrane w aktualnym tekście (current consolidated state
udostępniany przez ELI HTML endpoint). Per ustawa: jeden plik `.jsonl` z chunks
oraz `_meta.json` z metadanymi aktu (tytuł, daty, status, lista nowelizacji,
referencje do tekstów jednolitych, implementowane dyrektywy UE).

## Schemat chunku (`.jsonl`)

```jsonc
{
  "ustawa_id": "DU/2014/827",
  "ustawa_title": "Ustawa z dnia 30 maja 2014 r. o prawach konsumenta",
  "art": "27",
  "para": null,            // § (używane w KC; null gdy brak)
  "ust": null,             // ust. (null gdy brak)
  "pkt": null,             // pkt (null gdy brak)
  "lit": null,             // lit. (null gdy brak)
  "tresc": "Konsument, który zawarł umowę na odległość lub poza lokalem ...",
  "citation_string": "art. 27 Ustawy o prawach konsumenta z dnia 30 maja 2014 r. (Dz.U. 2014 poz. 827)",
  "scrape_date": "2026-05-16",
  "source_url": "https://api.sejm.gov.pl/eli/acts/DU/2014/827/text.html/art=27",
  "metadata": {
    "data_uchwalenia": "2014-05-30",
    "data_promulgacji": "2014-06-24",
    "data_wejscia_w_zycie": "2014-12-25",
    "ostatnia_zmiana": "2026-03-10T16:09:11",
    "obowiazujaca": true,
    "status": "akt posiada tekst jednolity",
    "rozdzial": "Rozdział 4 Prawo odstąpienia od umowy",
    "lead_in": "<opcjonalny tekst nadrzędnej jednostki>"
  }
}
```

`citation_string` jest **deterministyczny** — zbudowany zawsze w tej samej
formie z `art`, `para/ust/pkt/lit`, krótkiego tytułu ustawy, daty uchwalenia
i adresu `Dz.U.`. To kluczowe dla detekcji halucynacji w generatorze RAG.

## Sample 3 chunks per ustawa

### Dz.U. 1964 nr 16 poz. 93 — Kodeks cywilny

**Sample 1** — art. 576 § 3 Kodeksu cywilnego z dnia 23 kwietnia 1964 r. (Dz.U. 1964 poz. 93)
> Zarzut z tytułu rękojmi może być podniesiony także po upływie powyższego
> terminu, jeżeli przed jego upływem kupujący zawiadomił sprzedawcę o wadzie.

**Sample 2** — art. 540 § 1 Kodeksu cywilnego z dnia 23 kwietnia 1964 r. (Dz.U. 1964 poz. 93)
> Jeżeli właściwy organ państwowy ustalił, w jaki sposób sprzedawca ma obliczyć
> cenę za rzeczy danego rodzaju lub gatunku (cena wynikowa), stosuje się,
> zależnie od właściwości takiej ceny, bądź przepisy o cenie sztywnej, bądź
> przepisy o cenie maksymalnej.

**Sample 3** — art. 385 § 2 Kodeksu cywilnego z dnia 23 kwietnia 1964 r. (Dz.U. 1964 poz. 93)
> Regulamin wydany w czasie trwania stosunku prawnego o charakterze ciągłym
> wiąże drugą stronę, jeżeli zostały zachowane przepisy paragrafu poprzedzającego,
> a druga strona nie wypowiedziała umowy z najbliższym terminem wypowiedzenia.

### Dz.U. 2007 nr 171 poz. 1206 — Ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym

**Sample 1** — art. 16 ust. 1 Ustawy o przeciwdziałaniu nieuczciwym praktykom rynkowym z dnia 23 sierpnia 2007 r. (Dz.U. 2007 poz. 1206)
> Kto stosuje nieuczciwą praktykę rynkową polegającą na zarządzaniu mieniem
> gromadzonym w ramach grupy z udziałem konsumentów w celu finansowania zakupu
> produktu w systemie konsorcyjnym, podlega karze pozbawienia wolności od 3
> miesięcy do lat 5.

**Sample 2** — art. 6 ust. 4 pkt 5 Ustawy o przeciwdziałaniu nieuczciwym praktykom rynkowym z dnia 23 sierpnia 2007 r. (Dz.U. 2007 poz. 1206)
> informacje o istnieniu prawa do odstąpienia od umowy lub rozwiązania umowy,
> jeżeli prawo takie wynika z ustawy lub umowy.

**Sample 3** — art. 2 pkt 10 Ustawy o przeciwdziałaniu nieuczciwym praktykom rynkowym z dnia 23 sierpnia 2007 r. (Dz.U. 2007 poz. 1206)
> systemie konsorcyjnym - rozumie się przez to prowadzenie działalności
> gospodarczej polegającej na zarządzaniu mieniem gromadzonym w ramach grupy z
> udziałem konsumentów...

### Dz.U. 2007 nr 50 poz. 331 — Ustawa o ochronie konkurencji i konsumentów

**Sample 1** — art. 22 ust. 3 Ustawy o ochronie konkurencji i konsumentów z dnia 16 lutego 2007 r. (Dz.U. 2007 poz. 331)
> Przed wydaniem postanowienia o przedłużeniu terminu, o którym mowa w ust. 1,
> Prezes Urzędu może przeprowadzić postępowanie wyjaśniające.

**Sample 2** — art. 11 ust. 2 Ustawy o ochronie konkurencji i konsumentów z dnia 16 lutego 2007 r. (Dz.U. 2007 poz. 331)
> W przypadku określonym w ust. 1 Prezes Urzędu wydaje decyzję o uznaniu praktyki
> za ograniczającą konkurencję i stwierdzającą zaniechanie jej stosowania.

**Sample 3** — art. 84 Ustawy o ochronie konkurencji i konsumentów z dnia 16 lutego 2007 r. (Dz.U. 2007 poz. 331)
> W sprawach dotyczących dowodów w postępowaniu przed Prezesem Urzędu w zakresie
> nieuregulowanym w niniejszym rozdziale stosuje się odpowiednio art. 227-315
> ustawy z dnia 17 listopada 1964 r. - Kodeks postępowania cywilnego.

### Dz.U. 2011 nr 199 poz. 1175 — Ustawa o usługach płatniczych

**Sample 1** — art. 8 ust. 2 Ustawy o usługach płatniczych z dnia 19 sierpnia 2011 r. (Dz.U. 2011 poz. 1175)
> Postanowienia umów o usługi płatnicze mniej korzystne dla użytkownika niż
> przepisy ustawy są nieważne; zamiast nich stosuje się odpowiednie przepisy
> ustawy.

**Sample 2** — art. 18 Ustawy o usługach płatniczych z dnia 19 sierpnia 2011 r. (Dz.U. 2011 poz. 1175)
> Ciężar udowodnienia spełnienia przez dostawcę wymogów w zakresie przekazania
> użytkownikowi informacji określonych w przepisach niniejszego działu spoczywa
> na dostawcy.

**Sample 3** — art. 28 ust. 1 Ustawy o usługach płatniczych z dnia 19 sierpnia 2011 r. (Dz.U. 2011 poz. 1175)
> W okresie obowiązywania umowy ramowej użytkownik ma prawo żądać w każdym czasie
> udostępnienia mu postanowień umowy oraz informacji określonych w art. 27, w
> postaci papierowej lub na innym trwałym nośniku...

### Dz.U. 2014 poz. 827 — Ustawa o prawach konsumenta

**Sample 1** — art. 27 Ustawy o prawach konsumenta z dnia 30 maja 2014 r. (Dz.U. 2014 poz. 827)
> Konsument, który zawarł umowę na odległość lub poza lokalem przedsiębiorstwa,
> może w terminie 14 dni odstąpić od niej bez podawania przyczyny i bez
> ponoszenia kosztów, z wyjątkiem kosztów określonych w art. 33, art. 34 ust. 2
> i art. 35.

**Sample 2** — art. 31 ust. 1 Ustawy o prawach konsumenta z dnia 30 maja 2014 r. (Dz.U. 2014 poz. 827)
> W przypadku odstąpienia od umowy zawartej na odległość lub umowy zawartej poza
> lokalem przedsiębiorstwa umowę uważa się za niezawartą.

**Sample 3** — art. 12 ust. 1 pkt 1 Ustawy o prawach konsumenta z dnia 30 maja 2014 r. (Dz.U. 2014 poz. 827)
> głównych cechach świadczenia z uwzględnieniem przedmiotu świadczenia oraz
> sposobu porozumiewania się z konsumentem;

### Dz.U. 2016 poz. 1823 — Ustawa o pozasądowym rozwiązywaniu sporów konsumenckich

**Sample 1** — art. 4 ust. 2 pkt 1 Ustawy o pozasądowym rozwiązywaniu sporów konsumenckich z dnia 23 września 2016 r. (Dz.U. 2016 poz. 1823)
> osobą fizyczną - miejsce wykonywania działalności gospodarczej;

**Sample 2** — art. 4 ust. 2 pkt 2 Ustawy o pozasądowym rozwiązywaniu sporów konsumenckich z dnia 23 września 2016 r. (Dz.U. 2016 poz. 1823)
> osobą prawną lub jednostką organizacyjną nieposiadającą osobowości prawnej,
> której ustawa przyznaje zdolność prawną - siedzibę jej organu zarządzającego
> lub miejsce wykonywania działalności gospodarczej, w szczególności miejsce, w
> którym znajduje się jej oddział lub zakład.

**Sample 3** — art. 10 pkt 15 Ustawy o pozasądowym rozwiązywaniu sporów konsumenckich z dnia 23 września 2016 r. (Dz.U. 2016 poz. 1823)
> wskazanie skutków prawnych danego sposobu zakończenia postępowania w sprawie
> pozasądowego rozwiązywania sporów konsumenckich, w tym konsekwencji
> niezastosowania się do wiążącego rozstrzygnięcia sporu;

## Metodologia

1. **Endpoint discovery.** Per ustawa, fetch JSON metadata (`/eli/acts/{P}/{Y}/{N}`)
   oraz `struct` (`/eli/acts/{P}/{Y}/{N}/struct`) — authoritative hierarchia
   prawna (`arti` → `para`/`pass`/`pint` → `pint`/`lett`).

2. **Pobranie tekstu.** Pełen `text.html` (`/eli/acts/{P}/{Y}/{N}/text.html`)
   reprezentuje aktualny stan po wszystkich nowelizacjach. **Endpoint
   per-artykuł** (`/text.html/art={N}`) zwraca pustkę dla niektórych ustaw
   (KC, Ochrona konkur., Usługi płatn.) — pełen tekst zawsze działa.

3. **Parsowanie HTML.** Stack-based `html.parser` (stdlib) walka po divach
   `unit_arti/para/pass/pint/lett`, treść w `<div data-template="xText">`.
   Sub-artykuły (np. `arti_4a`) nieobecne w `struct` to przepisy zmieniające
   inną ustawę — pomijane.

4. **Walidacja względem ELI struct.** Każdy chunk path (np. `arti=44 → pint=2`)
   musi istnieć w `struct` aktu. Hierarchia czysto kanoniczna: pod `pkt` może
   być tylko `lit`. Inaczej to amending text wstawiony w HTML (np. inserted
   przepis nowelizujący KC) i jest odrzucany.

5. **Chunkowanie.** Atom = najgłębsza walidna jednostka w hierarchii ELI:
   - artykuł bez podziału → cały artykuł = chunk
   - artykuł z ustępami bez pkt → ustęp = chunk
   - artykuł z ustępami i pkt → pkt = chunk (z `lead_in` = treść ustępu)
   - itd. dla `lit`

6. **NFC normalization.** Wszystkie pola tekstowe przepuszczone przez
   `unicodedata.normalize("NFC", ...)`. Polish nbsp (` `) konwertowane
   do regular space. Whitespace zwijany.

7. **Citation string.** Deterministyczne złożenie z meta:
   `art. {N}[ § {P}][ ust. {U}][ pkt {K}][ lit. {L}] {short_title}
   z dnia {DD miesiąca YYYY} r. ({Dz.U. YYYY poz. NNNN})`

## Statystyki

| Plik | Chunks | Bajty | Średnia dł. (chars) | Min | Max |
|---|---:|---:|---:|---:|---:|
| DU_1964_93.jsonl | 92 | 85 929 | 258 | 41 | 702 |
| DU_2007_1206.jsonl | 113 | 120 025 | 198 | 20 | 1 413 |
| DU_2007_331.jsonl | 500 | 491 656 | 184 | 16 | 2 591 |
| DU_2011_1175.jsonl | 888 | 934 017 | 187 | 10 | 2 004 |
| DU_2014_827.jsonl | 240 | 239 084 | 171 | 20 | 654 |
| DU_2016_1823.jsonl | 290 | 287 207 | 137 | 18 | 538 |
| **TOTAL** | **2 123** | **2 157 918** | — | — | — |

## QA results

| Check | Status |
|---|---|
| Liczba unikalnych artykułów per ustawa zgodna z ELI `struct` | OK (0 missing, 0 extra) |
| `tresc` non-empty | OK (0 empty) |
| Pole `citation_string` populated | OK (0 brakujących) |
| NFC normalization | OK (0 not-NFC) |
| Duplikaty po (art, para, ust, pkt, lit) | OK (0 dupes) |
| Brak path-ów niezgodnych z ELI struct (np. § w ustawie używającej tylko ust.) | OK |

## Known issues / gotchas

1. **Krótkie chunks z amending provisions.** Niektóre rozdziały (np. Rozdział 6
   Ustawy o prawach konsumenta art. 44-50) zawierają przepisy zmieniające
   inne ustawy. Treść chunków to wówczas instrukcja typu:
   *„art. 22¹ otrzymuje brzmienie: ..."* + cytowana treść inserted artykułu
   trafia do `lead_in`. Cytat poprawnie wskazuje art. 44 pkt N konsumenta,
   bez fałszywego `§` (which would suggest hierarchy not present in act).

2. **Hierarchia hybrid.** Niektóre artykuły mają `lett` bezpośrednio bez `pkt`
   (np. `art. 48 lit. a` w konsumenta) — zgodne z ELI `struct` i obsłużone
   poprawnie.

3. **KC filter.** Pobrane tylko wybrane sekcje KC zgodnie z scope pracy:
   art. 384-385 (wzorce umowne), 535-555 (umowa sprzedaży), 556-576 (rękojmia
   za wady), 577-581 (gwarancja jakości). Pominięte artykuły uchylone — w
   zakresie 384-581 jest 48 obowiązujących artykułów z 198 słotów.

4. **Brak chunków z `§` w nie-KC ustawach.** Konsumenta/Ochrona konkur./
   Usługi płatn./Pozasądowym używają tylko `ust.`, nie `§`. Walidacja struct
   potwierdza poprawność.

5. **Polish chars coverage <100%** dla niektórych ustaw — to chunki bardzo
   krótkie (jednowyrazowe definicje, list items, krzyżowe referencje typu
   *"sposobie i terminie zapłaty;"*). Nie błąd encoding — po prostu krótkie
   wyrażenia bez polskich diakrytyków.

## Licencja źródła

**Art. 4 ust. 1 ustawy o prawie autorskim i prawach pokrewnych (Dz.U. 1994
poz. 83):**

> Nie stanowią przedmiotu prawa autorskiego:
> 1) akty normatywne lub ich urzędowe projekty;

Wszystkie pobrane ustawy są **public domain de facto**. ELI API udostępnia
content publicznie, bez API key i bez restrykcji licencyjnych. Korpus może być
swobodnie wykorzystywany do trenowania modeli, evaluacji RAG, publikacji
naukowych.

## Reprodukcja

```powershell
# Pełen scrape (wszystkie 6 ustaw):
uv run python -m src.scrape.isap.scrape_eli

# Pojedyncza ustawa:
uv run python -m src.scrape.isap.scrape_eli --ustawa DU/2014/827

# Dry-run (parse bez zapisu):
uv run python -m src.scrape.isap.scrape_eli --dry-run

# Verbose logging:
uv run python -m src.scrape.isap.scrape_eli -v
```

Wymagania: Python 3.13, stdlib only (urllib, html.parser, json, dataclasses).
Bez zewnętrznych zależności (BeautifulSoup, requests etc.) — czysta stdlib.

Czas wykonania: ~6 s (6 ustaw × ~1s na fetch + parse).
