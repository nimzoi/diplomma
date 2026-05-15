# DEC-002: ChPL+Ulotka pairing jako 5. RQ (cross-register retrieval)

**Data:** 2026-05-15
**Status:** ACCEPTED
**Autorka:** Magdalena Sochacka
**Related:** DEC-001 (rotacja domeny — enabling decision dla niniejszej)

## Kontekst

Po przyjęciu DEC-001 (rotacja na farmakologię szeroką z URPL RPL XML feed jako primary source), sources research R2 ujawnił, że każdy lek zarejestrowany w URPL ma **dwa równoległe dokumenty regulacyjne**:

1. **ChPL (Charakterystyka Produktu Leczniczego)** — dokument profesjonalny dla lekarzy/farmaceutów. Standaryzowana struktura 10 sekcji, terminologia medyczno-łacińska, rejestr formalny.
2. **Ulotka dla pacjenta** — laypersonowski odpowiednik dla użytkowników. QRD-aligned 6 sekcji, polszczyzna codzienna, imperatyw, rejestr instruktażowy.

Oba dokumenty są:
- Wytwarzane przez tego samego MAH (Marketing Authorization Holder)
- Zatwierdzane przez URPL w ramach tej samej decyzji administracyjnej
- Dostępne z tego samego RPL XML feed (endpointy `/medicinal-products/{ID}/leaflet` i parallel ChPL endpoint)
- Pod identycznym statusem licencyjnym (urzędowe materiały, Art. 4 ustawy o prawie autorskim)
- **Semantycznie aligned** — opisują ten sam lek, te same wskazania, te same przeciwwskazania, ten sam mechanizm farmakologiczny

Ale **lingwistycznie się dywergują** — różny register, różne struktury syntaktyczne, różne wybory leksykalne, różne odbiorcy.

Sources research R2 zwerifikował, że **w literaturze brak publicznie udokumentowanej polskiej pary ChPL↔Ulotka jako training corpus**. Najbliższa istniejąca praca: Grabowski 2017 — *English-Polish comparable PIL corpus* — ale to **cross-language, nie intra-Polish cross-register**.

## Opcje rozważane

| Opcja | Co to znaczy | Pros | Cons |
|-------|-------------|------|------|
| **A: Ignorować Ulotki** | Korpus z samego ChPL (i innych źródeł), Ulotki nie pobierane | Mniej danych do przetwarzania; węższy scope | Marnuje strukturalny benefit URPL feed; traci unique training signal; brak cross-register sub-contribution |
| **B: Ulotki w korpusie, bez explicit RQ** | Trening na ChPL ∪ Ulotki, ale RQ1-RQ4 pozostają jak w v3 | Reranker uczy się obu rejestrów; lepsza diversity | **Niewykorzystany methodological potential** — sygnał alignment się marnuje; brak publishable sub-contribution |
| **C: Ulotki w korpusie + ChPL↔Ulotka pairing jako 5. RQ** | Eksplicytna evaluacja cross-register retrieval (lay query → professional answer i odwrotnie); nowy RQ5/H5 | Novel sub-contribution; publishable jako standalone artifact (Polish ChPL↔Ulotka aligned corpus); explicit defense argument dla wartości pracy | Dodatkowy RQ do uzasadnienia, evaluation set design, ablation needed |
| **D: Pairing jako future work** | Dodać Ulotki, pairing tylko zaznaczony jako "future work" w R8 | Bezpieczne; niski risk scope creep | Słabsza obrona; konkurencja może zająć ten teren w okresie sem. III |

## Decyzja

**Wybrana: Opcja C — eksplicytny 5. RQ na cross-register retrieval.**

## Uzasadnienie

1. **Strukturalna parowalność za darmo.** Alignment ChPL↔Ulotka jest **deterministyczny** przez `productID` z URPL RPL feed. Każdy produkt zwraca obie wersje, dla każdej można wyciągnąć paired pro/lay versions. **Zero kosztu manualnej anotacji** dla 14k+ par leków. Sample 900 par to projektowo idealny dataset dla preference learning cross-register.

2. **Literature gap potwierdzony.** Sources research R2 nie znalazł publicznie udokumentowanego Polish ChPL↔Ulotka aligned corpus. Najbliższa istniejąca praca: Grabowski (2017) [1] — *English-Polish comparable PIL corpus* — cross-language (EN→PL), **nie** intra-PL cross-register.

Globalna literatura cross-register / simplification medical istnieje dla anglojęzycznych setupów:
- Cao i in. (2020) [2] *Expertise Style Transfer* — expert↔layman style transfer w domenie medical, ACL 2020
- Devaraj i in. (2021) [3] *Paragraph-level Simplification of Medical Texts* — biomedical abstract simplification
- van den Bercken i in. (2019) [4] *Evaluating Neural Text Simplification in the Medical Domain* — WWW 2019

Wszystkie te prace są **anglojęzyczne** i **nie wykorzystują regulatorowych pair** typu SPC/PIL (analogon ChPL/Ulotka). To znaczy że niniejsza praca jest **pierwszą publicznie udokumentowaną aligned ChPL↔Ulotka methodology dla polskiego BioNLP**, w paradygmacie cross-register **retrieval** (vs cross-register simplification z literatury EN).

**Cytacje (do verify w citation pass + ostatecznie R2):**

> [1] Grabowski Ł. (2017). *Towards an Online Comparable Corpus of English-Polish Patient Information Leaflets*. In: *Comparable Corpora and Computer-Assisted Translation*, John Benjamins (CILT 341). 🟡 Verify exact title via `citation-checker`.
>
> [2] Cao Y., Shui R., Pan L., Kan M.Y., Liu Z., Chua T.S. (2020). *Expertise Style Transfer: A New Task Towards Better Communication Between Experts and Laymen*. ACL 2020.
>
> [3] Devaraj A., Marshall I.J., Wallace B.C., Li J.J. (2021). *Paragraph-level Simplification of Medical Texts*. 🟡 Verify exact venue (NAACL 2021 vs EMNLP 2021) via `citation-checker`.
>
> [4] van den Bercken L., Sips R.J., Lofi C. (2019). *Evaluating Neural Text Simplification in the Medical Domain*. WWW 2019. 🟡 Verify year (2019 vs 2020) via `citation-checker`.

**Note:** te 4 cytacje stanowią literature anchor dla DEC-002 + przyszłej R2 Literature Review (sekcja *„Cross-register medical NLP"* / *„Text simplification in healthcare"*). Przed final R2 — full citation hygiene check via komenda `/citations` (deleguje do `citation-checker` subagent).

3. **Defense scaffolding strengthens.** Dodatkowy niezależny RQ + niezależny artefakt = piąty wymiar wkładu pracy. Jeśli H1 (retrening rerankera) odpada, H5 (cross-register) może pozostać aktywne i niezależnie defensible. To bezpośrednio adresuje obawę "*co jeśli reranker nie wyjdzie*" zgłoszoną przez autorkę 2026-05-15.

4. **Naturalna kontynuacja pipeline'u.** Cross-register retrieval **nie wymaga osobnego pipeline'u** — używa tego samego rerankera (już trenowanego) i tych samych narzędzi ewaluacji. Dodatkowy koszt eksperymentalny to:
   - Konstrukcja query setu (lay→pro, pro→lay) — automatyczna z ChPL/Ulotka headers
   - Dodatkowe metryki w R7
   - 1 dodatkowy ablation (A4: ChPL-only vs ChPL+Ulotka)
   - Razem: ~1 tydzień pracy w cyklu 1, ~3 dni pisania R7 sekcji

5. **Publishable independence.** Korpus paired ChPL↔Ulotka + cross-register retrieval evaluation = **standalone publishable artifact**. Możliwa publikacja na BioNLP / Polish NLP workshop niezależnie od pełnej pracy. To z perspektywy CV autorki = dodatkowa wartość poza dyplomem.

6. **Methodological consistency z RQ2 (LLM-as-judge).** RQ5 może wykorzystać ten sam LLM-judge (PLLuM-12B-instruct) z dodatkowym 4. protokołem (cross-register pair scoring). To **rozszerza** istniejący framework, nie dodaje nowy. Spójność architektoniczna pracy zachowana.

## Konsekwencje

### Pozytywne

- **Novel sub-contribution** publishable poza dyplomem
- Dodatkowy artefakt: paired Polish ChPL↔Ulotka corpus (8100+ par leków → 16k+ section-level pairs)
- 5. niezależny wymiar obrony w R8 (defense scaffolding pkt 3)
- Wzrost training corpus diversity bez wzrostu cost manualnej anotacji
- Spójność architektoniczna (LLM-judge reusable)
- Ramowanie zewnętrzne pracy: *"polska farmakologia + cross-register retrieval"* brzmi bardziej dystynktywne niż samo *"reranker fine-tuning"*

### Negatywne / koszty

- **Nowy RQ5/H5** do uzasadnienia w R1 + ewaluacji w R7 — koszt: ~5 dni pisania
- Dodatkowe metryki: accuracy@10 cross-register, gap same-vs-cross — koszt: 1 dzień implementacji
- Dodatkowa ablation A4 (ChPL-only vs ChPL+Ulotka) — koszt: 1 dzień ML
- Dodatkowy 4. protokół LLM-judge (cross-register pair scoring) — koszt: 2 dni implementacji + walidacji
- **Ryzyko scope creep** w R5 (architektura) — należy explicit ograniczyć cross-register pipeline do prostego switch w training data, NIE separate model

### Neutralne

- Stack bez zmian (PLLuM-judge already w pipeline, same datasets URPL)
- Harmonogram bez zmian (RQ5 mieści się w cyklu 1 + R7)
- Eval set strategy — 200 par gold standard nadal psych (N05/N06), dla cross-register evaluation używamy programatycznie generated query-passage pairs z URPL alignment (gold standard implicite przez alignment)

## Definicja eksperymentu RQ5

**RQ5:** Czy reranker dotrenowany na corpus z paired pro/lay versions (ChPL ↔ Ulotka tych samych leków) handluje cross-register queries (lay → professional answer i odwrotnie) z accuracy@10 ≥70%, z gap ≤5pp poniżej same-register accuracy?

**H5:** Reranker dotrenowany na corpus zawierającym ChPL+Ulotka pairs osiąga ≥70% accuracy@10 na cross-register pairs, gap ≤5pp poniżej same-register.

**Falsyfikowalność:**
- Hipoteza odrzucona jeśli (a) accuracy@10 < 60%, lub
- (b) gap same-vs-cross > 15pp, lub
- (c) trening na pairs **degraduje** base-line retrieval na same-register (regresja > 2pp)

**Setup ewaluacyjny:**
- **Test query set:** programatycznie wygenerowane z 900 paired par leków
  - Lay query: pierwsze zdanie sekcji Ulotki (np. *"Co zrobić jak zapomniałem o dawce?"*)
  - Gold professional passage: odpowiadająca sekcja ChPL (np. 4.2 Dawkowanie)
  - Hard negatives: ten sam ChPL sekcja innego leku tej samej klasy ATC
- **Test set size:** 1800 cross-register pairs (900 lay→pro + 900 pro→lay)
- **Metryki:** accuracy@10, MRR@10, gap vs same-register baseline
- **Ablation A4:** porównanie ChPL-only training vs ChPL+Ulotka training na samym cross-register test set

## Kill criteria

Decyzja zostanie podważona jeśli:
- **Alignment quality poor** — sampling 100 paired pairs ujawnia że >30% par to różne wersje (np. ChPL z 2020 vs Ulotka z 2024 leku który zmienił indications) — wtedy alignment nie jest pełen
- **Length mismatch katastrofalny** — Ulotki średnio < 30% długości ChPL, co czyni naturalny pair odbiorczo nierówny
- **Promotor explicit blokuje** dodawanie 5. RQ jako "scope creep" — wtedy fallback: pozostawić corpus + pairing jako enabling data, RQ5 do future work R8
- **Cross-register evaluation niefeasible** — np. lay queries okazują się zbyt ambiguous (multiple ChPL passages legitimate) — wtedy adjust threshold na accuracy@10 lub przejść na MRR@10

## Powiązane

- **DEC-001**: Rotacja na farmakologię (enabling decision)
- Konspekt v3 FINAL II.7 (LLM-as-judge) — superseded w `02b_konspekt_v3_updates.md` z dodatkowym 4. protokołem
- Konspekt v3 FINAL II.3.3 (pytania badawcze) — superseded z dodatkowym RQ5
- `sources_catalog.md` — Ulotki jako Strata 2 (22% korpusu, 900 docs paired z ChPL)
- `thesis_elements/CLAUDE.md` Defense scaffolding pkt 3 — H5 jako jedna z 5 niezależnych kontrybucji
