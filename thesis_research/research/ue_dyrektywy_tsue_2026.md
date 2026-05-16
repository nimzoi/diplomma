# UE dyrektywy konsumenckie + TSUE orzecznictwo (PL) — S3 scrape report

**Scrape date:** 2026-05-16
**Iteration:** S3 (UE-level acts implementujące polskie prawo konsumenta)
**Defense argument:** pełen consumer law stack = polskie ustawy + UE dyrektywy
(źródło polskich implementacji) + TSUE orzecznictwo (autorytatywna wykładnia).

---

## Summary stats

| Komponent | Records | Source |
|---|---:|---|
| UE dyrektywy chunks | **1480** | EUR-Lex PL HTML, 8 dyrektyw |
| TSUE orzeczenia (full text) | **29** | EUR-Lex PL HTML, hand-curated priority |
| Polska implementacja mapping | 8 | manual cross-reference ISAP↔EUR-Lex |

**Distribution UE chunks per dyrektywa:**

| CELEX | Dyrektywa | Motyw chunks | Art chunks | Total |
|---|---|---:|---:|---:|
| 32011L0083 | CRD (Consumer Rights) | 67 | 137 | 204 |
| 32019L0770 | DCD (Digital Content) | 87 | 100 | 187 |
| 32019L0771 | SGD (Sale of Goods) | 72 | 85 | 157 |
| 32019L2161 | Omnibus | 60 | 55 | 115 |
| 31993L0013 | UCT (Unfair Contract Terms) | 0* | 22 | 22 |
| 32005L0029 | UCPD (Unfair Commercial Practices) | 25 | 64 | 89 |
| 32008L0048 | CCD I (Consumer Credit) | 51 | 184 | 235 |
| 32023L2225 | CCD II (nowa Consumer Credit) | 98 | 373 | 471 |
| **TOTAL** | | **460** | **1020** | **1480** |

\* Stary format HTML 93/13/EWG (1993) — TXT_TE flat `<p>` bez semantic classes; parser
legacy obsługuje, ale motyw struktura preambuły mniej regularna, więc preambuła
nie była chunkowana (pełen tekst preambuły dostępny w `pelna_tresc`).

---

## Część A: 8 dyrektyw UE konsumenckich

Każda dyrektywa pobrana w polskiej wersji językowej (EUR-Lex `URI=CELEX:{id}&lang=PL`),
parsed do atomic chunks (artykuł/ustęp/litera) per metodologia ELI. Citation strings
deterministycznie generowane:

```
art. 6 ust. 1 lit. a Dyrektywy 2011/83/UE     # nowoczesne dyrektywy
art. 3 Dyrektywy 93/13/EWG                     # stara dyrektywa (1993)
motyw 13 Dyrektywy 2011/83/UE                  # preambuła
```

**Schemas:** `halu.schemas.UEDyrektywa` (Pydantic strict). Wszystkie chunks NFC normalizowane.

**Storage:** `main_project/data/raw/ue_dyrektywy_2026-05-16/`
- `{CELEX_ID}.jsonl` — chunks
- `{CELEX_ID}_meta.json` — metadata + scrape stats
- `_summary.json` — aggregate
- `README.md` — license + reproducibility info (auto-generowane)

---

## Część B: 29 priority orzeczeń TSUE

Hand-curated lista 30 spraw priority, 29 udostępnione w PL (1 pre-akcesyjna 1995
— Benincasa C-269/95 — nie ma PL wersji, dokumentowane w `_summary.json.skipped_no_pl`).

**Distribution by year:** 2005:2, 2009:1, 2010:1, 2012:2, 2013:1, 2014:3, 2016:3,
2017:1, 2018:3, 2019:5, 2020:3, 2021:2, 2022:1, 2023:1.

**Distribution by dyrektywa:**

| Dyrektywa | Spraw |
|---|---:|
| 93/13/EWG (UCT — klauzule abuzywne, CHF) | 18 |
| 2008/48/WE (CCD — kredyt) | 5 |
| 2011/83/UE (CRD — odstąpienie) | 4 |
| 2005/29/WE (UCPD — nieuczciwe praktyki) | 3 |
| 97/7/WE + bez dyrektywy | 2 |

### Key prior art verified
- **C-260/18 Dziubak** ✓ scraped, 40k chars, sentencja: art. 6 ust. 1 dyrektywy 93/13/EWG
  → fundament polskiego CHF orzecznictwa (kredyt indeksowany; możliwość usunięcia
  klauzul vs. unieważnienie całej umowy)
- **C-26/13 Kásler** ✓ scraped — standard transparentności klauzul walutowych
- **C-377/14 Radlinger** ✓ — klauzule abuzywne + kredyt konsumencki + ex officio
- **C-19/20 Bank BPH** ✓ — kontynuacja CHF, skutek abuzywności
- **C-520/21 Bank M.** ✓ — wynagrodzenie banku za korzystanie z kapitału (polskie
  pytanie prejudycjalne 2023, fundamentalne dla post-Dziubak scenariuszy)
- **C-628/17 Orange Polska** ✓ — agresywne praktyki, polskie tło UOKiK
- **C-243/08 Pannon GSM** ✓ — ex officio kontrola klauzul

### Per-case fields zachowane (TSUEOrzeczenie schema)
- `case_id`, `celex_id`, `case_name`
- `data_orzeczenia` (29/29 successfully extracted via regex z header)
- `sklad` (izba + sędzia sprawozdawca)
- `streszczenie` (descriptors z header pre-orzeczenie — kluczowe pojęcia rozdzielone
  myślnikami: „Odesłanie prejudycjalne – Dyrektywa 93/13/EWG – ...")
- `tezy_kluczowe` (operative part / sentencja po marker „Trybunał orzeka, co następuje:")
- `pelna_tresc` (40k-60k znaków per case)
- `metadata.related_directives`, `metadata.legal_topic`, `metadata.notes`

### Skipped cases (no PL version)
- **C-269/95 Benincasa** — orzeczenie z 1997 r., przed akcesją PL do UE (2004-05-01).
  EUR-Lex zwraca tylko EN/DE/FR/IT/ES wersje. Documented w `_summary.json`. Należy
  cytować z streszczeń wtórnych (np. komentarz Sądu Najwyższego, podręczniki KC).

### Anti-pattern correction
- Pierwotnie task brief zawierał **C-126/18** dla Gómez del Moral Guasch. Sprawdzono
  EUR-Lex: faktyczny case_id to **C-125/18** (CELEX 62018CJ0125). Korekta zachowana
  w `PRIORITY_CASES` z notes field.

---

## Część C: UE → PL implementacja mapping

`mapping.json` — strukturalny mapping CELEX → polska ustawa implementacyjna:

| Dyrektywa | Polska ustawa | Data PL wejścia w życie |
|---|---|---|
| 2011/83/UE | DU/2014/827 (Ustawa o prawach konsumenta) | 2014-12-25 |
| 2019/770/UE (DCD) | DU/2022/2337 (nowelizacja UPK) | 2023-01-01 |
| 2019/771/UE (SGD) | DU/2022/2337 (ta sama nowelizacja) | 2023-01-01 |
| 2019/2161/UE (Omnibus) | DU/2022/2581 | 2023-01-01 |
| 93/13/EWG (UCT) | DU/1964/93 (KC art. 385¹ i nast., wprowadzone przez DU/2000/443) | 2000-07-01 |
| 2005/29/WE (UCPD) | DU/2007/1206 | 2007-12-21 |
| 2008/48/WE (CCD I) | DU/2011/126 | 2011-12-18 |
| 2023/2225/UE (CCD II) | **(transpozycja w toku, deadline 2025-11-20)** | — |

**Defense usage:** w fazie probe inference + verifier reasoning, można skonstruować
citation chains typu:

```
[Polish claim] "Konsument ma 14 dni na odstąpienie od umowy zawartej na odległość."
[Polish citation] "art. 27 Ustawy o prawach konsumenta (DU/2014/827)"
[UE level citation] "art. 9 ust. 1 Dyrektywy 2011/83/UE"
[TSUE wykładnia] "C-249/21 Fuhrmann-2 (interpretacja wymogów informacyjnych)"
```

Cross-language consistency check: jeśli claim w polish jest grounded w polish ustawie
implementującej dyrektywę X, a TSUE wyłożyłeś dyrektywę X inaczej, to potencjalna
halucynacja / niezgodność. Future work pkt dla halu detection.

---

## License attribution

EUR-Lex content jest objęty **Decyzją 2011/833/UE** o reuse public-sector information:
- ✓ Wolne użycie dla celów badawczych/edukacyjnych
- ✓ Wymaga attribution: link do source EUR-Lex URL (zachowane w `source_url` field)
- ✓ Source field w schemach: `"(c) European Union, https://eur-lex.europa.eu/ — free
  reuse per Decyzja 2011/833/UE (attribution required: link to EUR-Lex source)"`

**Checklist (per chunk + per record):**
- ✓ Każdy record ma `license` field z full attribution string
- ✓ Każdy record ma `source_url` z deep-link do CELEX page
- ✓ `_summary.json` per output dir zawiera license w nagłówku
- ✓ Mapping README zawiera license section dla UE + dla polskich ustaw

**Polskie ustawy (mapping):** art. 4 ust. 1 ustawy o prawie autorskim (DU/1994/83) —
akty normatywne nie są przedmiotem prawa autorskiego (public domain de facto).

---

## Key teorie prawne ekstrahowane (TSUE)

Z `tezy_kluczowe` priority orzeczeń, dominujące teorie/rozstrzygnięcia:

### Dyrektywa 93/13/EWG (klauzule abuzywne — najbardziej cytowana w polskim orzecznictwie):
1. **Ex officio kontrola** (C-243/08 Pannon, C-415/11 Aziz) — sąd musi z urzędu badać
   abuzywność klauzul nawet bez zarzutu konsumenta.
2. **Skutek abuzywności** (C-260/18 Dziubak) — sąd nie ma kompetencji do modyfikacji
   nieuczciwej klauzuli; może albo ją usunąć, albo unieważnić całą umowę (jeśli
   bez klauzuli nie może się utrzymać).
3. **Transparentność klauzul walutowych** (C-26/13 Kásler, C-186/16 Andriciuc) —
   wymóg jasnego i zrozumiałego sposobu poinformowania konsumenta o ryzyku.
4. **Kontrola abstrakcyjna** (C-472/10 Invitel) — klauzule standardowe mogą być
   badane in abstracto przez sąd, nie tylko w sprawach indywidualnych.
5. **Bezzwrotnoty bankowi za kapitał** (C-520/21 Bank M.) — bank nie ma prawa
   żądać od konsumenta wynagrodzenia za korzystanie z kapitału po unieważnieniu
   umowy CHF z powodu klauzul abuzywnych (polski pytanie prejudycjalne).

### Dyrektywa 2008/48/WE (kredyt konsumencki):
1. **Ocena zdolności kredytowej** (C-449/13 CA Consumer Finance) — ciężar dowodu
   należytego sprawdzenia zdolności po stronie banku.
2. **Forma pisemna** (C-42/15 Home Credit Slovakia) — wymogi formalne umowy kredytu
   muszą być sankcjonowane (proporcjonalnie).
3. **Odstąpienie** (C-66/19 Kreissparkasse) — wymóg jasności klauzul o prawie
   odstąpienia: brak jasności = brak rozpoczęcia biegu 14-dniowego terminu.

### Dyrektywa 2011/83/UE (prawa konsumenta):
1. **Przycisk „zamów z obowiązkiem zapłaty"** (C-249/21 Fuhrmann-2) — sformułowanie
   przycisku finalizującego zakup musi jednoznacznie informować o zobowiązaniu.
2. **Towary „specjalne"** (C-380/17 Verbraucherzentrale) — wyłączenia z prawa
   odstąpienia interpretowane wąsko.

### Dyrektywa 2005/29/WE (nieuczciwe praktyki):
1. **Agresywne praktyki** (C-628/17 Orange Polska) — wprowadzające w błąd
   konstruowanie ofert telekomunikacyjnych = agresywna praktyka.

---

## Reproducibility
```bash
# Wszystkie dyrektywy (~30 sek):
uv run python -m src.scrape.ue.dyrektywy

# Wszystkie TSUE (~90 sek dla 30 spraw przy 2-sec rate limit):
uv run python -m src.scrape.ue.tsue

# Mapping (sekunda):
uv run python -m src.scrape.ue.mapping

# Selektywnie:
uv run python -m src.scrape.ue.dyrektywy --celex 32011L0083
uv run python -m src.scrape.ue.tsue --case C-260/18
```

## Notes na dalsze iteracje
- **Future S3+:** dodać orzeczenia post-2023 (sprawy z polskimi pytaniami
  prejudycjalnymi w toku — np. CHF-related W.A. v Powszechna Kasa Oszczędności Bank).
- **Verifier feature engineering:** TSUE `streszczenie` field (descriptors) + Polish
  ustawa cited articles → potencjał na automated citation chain validation.
- **Halu probe training augmentation:** synthetic halu injection MOŻE używać
  `tezy_kluczowe` TSUE jako template do generation contradicted claims (e.g.
  flip „nie stoi na przeszkodzie" → „stoi na przeszkodzie") — temporal_drift +
  negation_flip typy halu.
