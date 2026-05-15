# thesis_elements/

Draft rozdziałów pracy w `.docx`. Tu trafia treść która docelowo ląduje w finalnej pracy.

## Konwencja nazw

```
R{NN}_{slug}.docx
```

Przykład: `R01_wprowadzenie.docx`, `R05_architektura.docx`, `R07_wyniki.docx`.

Numery rozdziałów (struktura PJATK 8-rozdziałowa, Option A):

| NN | Slug | Treść |
|----|------|---|
| 01 | wprowadzenie | tło RAG + rerankery + drift + luka PL + cross-register |
| 02 | literatura | review ~30 źródeł (incl. LLM-as-judge, MLOps CT, drift, cross-register / paraphrase) |
| 03 | dane | 6 strata farmakologii (zobacz `thesis_research/sources_catalog.md`), codebooks, licencje |
| 04 | eda | rozkłady, embedding clusters UMAP, OCR quality, paired ChPL↔Ulotka alignment analysis |
| 05 | architektura | **CENTRALNY** — 5 z 7 figur diagramów, pipeline cross-register |
| 06 | modele | reranker + LLM-as-judge szczegóły + ablations |
| 07 | wyniki | baselines × cykle 1/2/3, kategoryczna error analysis, drift, RQ5 cross-register |
| 08 | podsumowanie | synteza RQ1-RQ5 + future work + negative-result framing |

## Format PJATK (z konspekt II.11 + Task 09)

- **Font:** Times New Roman 12pt
- **Line spacing:** 1.5
- **Margins:** 2.5cm (A4)
- **Headings:** H1 bold 16pt, H2 non-bold 14pt (per Task 09: H1 bold 14pt, H2 bold 12pt — sprawdź wersję template)
- **Footnotes:** IEEE z bookmark anchors, 10pt
- **Bibliografia:** ~30+ pozycji minimum, alphabetical, footnotes-style cites
- **Length:** Bachelor's ≥ 45,000 znaków (≈ 25 stron)
- **Abstract:** PL + EN, max 1000 znaków każdy
- **Keywords:** 3-5 słów kluczowych
- **Listy:** tabel + rysunków (mandatory if used)
- **Binding:** hardbound w ciemnym kolorze (granatowy/czarny/bordowy/zielony)

## Workflow rozdziału (zawsze ta kolejność)

1. **Outline** — szkielet H1/H2/H3 w chacie. Sign-off autorki **ZANIM** zacznie się pisanie.
2. **Read context** — `02b_konspekt_v3_updates.md` (sekcja mapująca do rozdziału) + `assignments/{NN}.md` + `assignments/PRO-D-THESIS-practical-work-main/*.md`
3. **Draft** — pełen tekst rozdziału. Reguły:
   - Time-proofed: bez "obecnie", "rosnące", "brak", "jedyny", "żaden"
   - Cytacje verifiable, flag niepewności
   - Defensibility nad novelty
   - Spójność terminologii z konspekt v3 updates
   - **Farmakologia** jako domena, **psychiatryczny eval subset** jako gold standard
4. **Self-review** — checklist:
   - [ ] Wszystkie zdania bronią się przed promotorem Kojałowiczem
   - [ ] Brak phantom citations
   - [ ] Footnotes spójnie numerowane (IEEE)
   - [ ] Linki do tabel/rysunków konsekwentne
   - [ ] PJATK format zachowany
5. **Citation pass** — uruchom `citation-checker` subagent na pliku.

## Konwencja edycji .docx

Bezpośrednia edycja .docx przez `python-docx` jest fragile (formatowanie). **Preferowany flow:**
1. Claude tworzy/edytuje draft jako markdown w `thesis_research/drafts/R{NN}_draft.md`
2. Autorka kopiuje sekcję do Worda i formatuje ręcznie
3. Po zatwierdzeniu — autorka zapisuje finalną wersję do `thesis_elements/R{NN}_{slug}.docx`

Jeśli autorka explicit prosi o `python-docx` — OK, ale **najpierw potwierdź**.

## Koniec sesji nad rozdziałem

Zawsze kończ wiadomością w formacie:
```
Co dalej w tym rozdziale:
1. [konkretny krok, max 2h]
2. [opcjonalny drugi]
3. [opcjonalny trzeci]
```

---

# Writing rules — constraint z promotor feedback v1

Te zasady wynikają z konkretnych ocen z poprzedniego tematu pracy (v1 administracja). Promotor: mgr inż. Piotr Kojałowicz. **Constraint na writing rozdziałów R1-R8 (.docx), NIE na pliki spec wewnętrzne** (`02b_konspekt_updates`, `sources_catalog`, ADR-y).

## Z Task 1 (Wprowadzenie) — ocena 7/10

Promotor wytknął:
- *„Struktura rozdziału 1 jest częściowo przesunięta w stronę pytań/hipotez i metryk, a słabiej domyka klasyczny układ 'intro' z wytycznych."*
- *„Kontekst naukowy jest skromny i opiera się na małej liczbie źródeł."*
- *„Styl miejscami jest mniej akademicki (zbyt potoczne lub rozwlekłe zdania)."*

### Reguły dla pisania R1

**1. Classic intro structure first.** Kolejność sekcji w R1:
1. Background and Context (~25-30% długości)
2. Motivation and Problem Statement (~20-25%)
3. Aim and Objectives (~15%)
4. Scope of the Study (~10%)
5. Thesis Structure overview (~10%)
6. **Pytania badawcze i hipotezy (~15%, NA KOŃCU rozdziału)**

NIE zaczynaj R1 od formalnego sformułowania RQ/H/metryk. Te elementy **zamykają** R1, nie otwierają go.

**2. Naukowy kontekst MUST be substantial.** Minimum **10-15 cytacji** w R1 dla rozkładu pola (RAG, rerankery, MLOps CT, drift, LLM-as-judge, polish NLP). Nie odkładaj całej literatury do R2.

**3. Academic style throughout (apply globally):**
- Trzecia osoba lub strona bierna: ✅ *„W pracy zaprojektowano…"* / ❌ *„Zaprojektowałam…"*
- Bez potocznych zwrotów (nawet jeśli są w naszych roboczych docs)
- Krótkie zdania, jedno zdanie = jedna myśl
- Bez "obecnie", "rosnące", "brak", "jedyny", "żaden" (time-proofing)
- Bez emoji w finalnych rozdziałach (w spec docs OK, w R1-R8 absolutnie nie)
- Konsystentne kursywy dla terminów technicznych przy pierwszym wystąpieniu

## Z Task 2 (Literature Review) — ocena 6/10

Promotor wytknął:
- *„Część przeglądu jest zbyt nierówna i miejscami mało precyzyjna formalnie."*
- *„Widoczne są problemy redakcyjne (formatowanie, spójność zapisu, jakość prezentacji tabeli)."*
- *„Potrzebna bardziej rygorystyczna metodologia selekcji źródeł."*
- *„Wnioski są sensowne, ale powinny mocniej wynikać z jednoznacznie zestawionych dowodów."*

### Reguły dla pisania R2

**4. Explicit source selection methodology** w sekcji 2.1 "Metodologia przeglądu":
- **Inclusion criteria** (recency, peer-review status, relevance, language)
- **Exclusion criteria** (np. książki popularnonaukowe, niezindeksowane preprinty starsze niż X lat)
- **Search strategy** (bazy: arXiv, IEEE, ACL Anthology, Google Scholar, DOAJ; keywords)
- **Selection pipeline** (znalezione → po tytule/abstracts → po pełnym tekście → final)
- **Final count** (ile zostało, ile odpadło, dlaczego)

**5. Consistent table formatting** w R2. Wszystkie tabele:
- Identyczne kolumny per typ (np. *Author, Year, Method, Contribution, Limitation* dla papers-comparison)
- Identyczna szerokość kolumn (CSS-style, nie ad-hoc)
- Sortowanie po jednym konsystentnym kryterium (rok publikacji wzrastająco)
- Czytelne kapsy (*"Title"* nie *"title"*; *"Author (Year)"* nie *"author year"*)
- Numeracja: Tabela N.M w R N

**6. Evidence-to-conclusion explicit linking.** Po każdej tabeli porównawczej:
- Sekcja "Synteza" co wynika z tabeli
- Wnioski explicit cytują **konkretne wiersze** tabeli per IEEE: *„Tabela 2.X pokazuje, że X autorów [3, 5, 7] proponuje Y, podczas gdy Z autorów [8, 12] preferuje W. Ta dywergencja wynika z..."*
- NIE pisz: *„Z tabeli wynika że Y jest popularne"* (bez referencji do wierszy)

## Mapowanie reguł na pliki w `D:\diplomma\`

| Plik | Status vs feedback |
|---|---|
| `02b_konspekt_v3_updates.md` | OK jako spec wewnętrzny — RQ-first OK tu |
| `sources_catalog.md` | OK + zawiera sekcję "Source selection methodology" do skopiowania do R2 sekcja 2.1 |
| ADR-y (DEC-001, DEC-002) | OK — ADR strukturalnie wymagają explicit options/reasoning, nie podpadają pod regułę 1 |
| Defense scaffolding niżej | OK — to constraint na obronę, nie pisanie |

Pliki **spec** powyżej są wewnętrzne narzędzia robocze. Pliki **deliverable** (rozdziały R1-R8 .docx) muszą trzymać się reguł 1-6.

## Tłumaczenie reguł na workflow rozdziału

W `## Workflow rozdziału` (wyżej) dodaj do kroku 2 ("Read context"):
- Czytanie tej sekcji **Writing rules** PRZED rozpoczęciem outline
- Krzyżowanie outline z regułą 1 (klasyczny układ vs RQ-first)
- Krzyżowanie outline z regułą 4 (czy uwzględnia methodology selection)

W kroku 5 ("Self-review") dodaj checklist:
- [ ] R1: klasyczny układ (background → ... → outline → RQ na końcu) ✓?
- [ ] R1: minimum 10-15 cytacji ✓?
- [ ] R2: explicit selection methodology ✓?
- [ ] R2: consistent table formatting ✓?
- [ ] R2: evidence-to-conclusion linking ✓?
- [ ] Academic style throughout (3rd person, no colloquial) ✓?
- [ ] Bez time-proofing zakazanych słów ✓?

---

# Defense scaffolding

Trzy mikro-podszepty zatwierdzone 2026-05-15. **Zaszywaj je w odpowiednich rozdziałach systematycznie**, żeby praca broniła się przy każdym empirycznym wyjściu eksperymentów.

## 1. Ablation studies w cyklu 1 (R6 + R7)

Cykl 1 retreningu rerankera ma uwzględniać **trzy ablacje** (każda osobny MLflow run, każda osobny wynik do dyskusji w R7):

| Ablacja | Wariant | Cel diagnostyczny |
|---|---|---|
| **A0 (baseline)** | polish-reranker-roberta-v3 + LLM-judge PLLuM-12B (default) | Pełen pipeline reference |
| **A1: judge → random** | Random preference labels (zamiast PLLuM) | Czy improvement wynika z signal quality czy z domain exposure? Jeśli random pairs daje podobny gain — judge nic nie wnosi. |
| **A2: judge → Bielik** | Bielik 11B v3 jako judge zamiast PLLuM | Cross-model robustness. Czy konkluzje H2 trzymają się dla innego polskiego LLM-a? |
| **A3: corpus → psych-only** | Trening tylko na ATC N05-N06 (psych subset, ~30% korpusu) | Domain breadth effect. Czy szeroki pharma corpus pomaga, czy psych-only już wystarcza? |
| **A4 (opcjonalna): ChPL-only** | Bez Ulotek (only professional register) | Effect of register diversity (powiązane z RQ5) |

**Decyzja w R6.4 (Ablation studies):**
> *"W cyklu 1 wykonano cztery ablacje (A1-A4) służące diagnostyce źródła poprawy retrieval quality. Wyniki ablacji raportowane w sekcji 7.X."*

## 2. Kategoryczna error analysis (R7)

Po każdym cyklu retreningu, **kategoryzacja błędów** na próbce ≥100 niepoprawnych rankingów (pozycja gold passage > 5 w top-10):

| Kategoria błędu | Definicja operacyjna | Mitygacja |
|---|---|---|
| **Terminology miss** | Query używa lay synonym, reranker miss-rank professional passage z synonimem łacińskim | Cross-register training (RQ5) bezpośrednio adresuje |
| **Ambiguous query** | Query odpowiada na ≥2 sekcje (np. "objawy" pasuje do 4.4 i 4.8) | Acceptable — flag w taxonomy, nie liczyć jako error |
| **Length mismatch** | Gold passage znacznie dłuższy/krótszy niż top-1 | Chunking strategy revision |
| **OOD chunk** | Top-1 dotyczy nie tej klasy ATC co query | Reranker domain confusion — sygnał do podziału training set |
| **Register mismatch** (NEW, dla RQ5) | Query lay, top-1 lay (ale gold = professional) lub odwrotnie | Acceptable jeśli RQ5 explicit cel cross-register; problem jeśli powinno być cross-register |
| **OCR artifact** | Top-1 ma uszkodzony tekst (kwerendy/podstacja itp.) | Pipeline OCR quality threshold |

**Decyzja w R7.4 (Error analysis):**
> *"Błędy rerankera kategoryzowane zgodnie z 6-poziomową taksonomią (Tabela 7.X). Rozkład kategorii informuje o priorytetach przyszłych iteracji."*

Nawet jeśli nDCG@10 nie poprawia się dramatically, **rozkład błędów to wartościowy wynik metodologiczny**.

## 3. Negative-result publishability framing (R8)

W rozdziale R8 (Podsumowanie) jawnie zapisz **rozdzielność kontrybucji**:

> *"Wkład pracy ma pięć niezależnych wymiarów. Empiryczna magnitude poprawy retrievalu (RQ1) jest tylko jednym z nich:*
> 
> *1. **Metodologiczny:** walidowany framework LLM-as-judge dla polskiej domeny specjalistycznej (RQ2) — pierwszy taki audit publicznie dla farmakologii PL.*
> *2. **Inżynierski:** reprodukowalny pipeline MLOps retreningu komponentów RAG (open-source artefakt).*
> *3. **Artefaktowy:** dotrenowany polish-reranker dla farmakologii — artefakt HuggingFace.*
> *4. **Eksperymentalny:** drift detection z simulated drift framework (RQ4).*
> *5. **Korpusowy / metodologiczny novel:** pierwsza publicznie udokumentowana Polish ChPL↔Ulotka aligned corpus + cross-register retrieval evaluation (RQ5) — luka w literaturze potwierdzona (Grabowski 2017 = EN-PL, nie intra-PL cross-register).*
>
> *Każdy z pięciu wymiarów broni się niezależnie. W przypadku odrzucenia H1 (retreningowy reranker nie osiąga założonej poprawy), praca zachowuje wkład w wymiarach (2)-(5), z RQ5 jako wyróżnioną kontrybucją do polskiego BioNLP."*

Zaszyj ten paragraf w R8.1 lub R8.2. To jest **defensive shield dla obrony** — promotor i komisja widzą *"co jeśli reranker leży?"* od razu i widzą że masz odpowiedź wcześniej niż padnie pytanie.

## Anti-patterns
- **Nie pisz rozdziału bez outline + sign-off.** Tracisz godzinę a autorka i tak każe przepisać.
- **Nie cytuj z głowy.** Każda cytacja musi mieć źródło które można sprawdzić.
- **Nie używaj** "obecnie", "rosnące zainteresowanie", "brak prac", "jedyny", "żaden" — wszystko się starzeje w 6 miesięcy.
- **Nie commituj** wersji rozdziału bez peer-glance autorki, chyba że ona poprosi.
- **Nie usuwaj defense scaffolding sekcji** — to świadoma obrona, nie dekoracja.
