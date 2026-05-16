# thesis_elements/

Draft rozdziałów pracy w `.docx`. Tu trafia treść która docelowo ląduje w finalnej pracy (po Iter. 7 writing phase).

**Status 2026-05-16 evening:** v3.2 post-pivot DEC-003 + post-Wariant B + T1 PASS + v0.6. Drafty markdown w `thesis_research/drafts/` PUSTE (post-Wariant B; pre-cleanup R3/R4/R5 → `_archive/v3.2-pre-clean/drafts/`); .docx w `thesis_elements/` NIE rozpoczęte (Iter. 7 manual writing).

## Konwencja nazw

```
R{NN}_{slug}.docx
```

Przykład: `R01_wprowadzenie.docx`, `R05_architektura.docx`, `R07_wyniki.docx`.

Numery rozdziałów (struktura PJATK 8-rozdziałowa, v3.2 post-DEC-003):

| NN | Slug | Treść |
|----|------|---|
| 01 | wprowadzenie | tło RAG + halucynacje + citation grounding + RQ1-RQ4 (3 main + 1 supporting) + luka PL (Mu-SHROOM 2025 pominął polski) |
| 02 | literatura | review ~30 źródeł: hallucination detection 2024-2026 (semantic entropy → hidden-states probes Farquhar→SEP→AggTruth), citation-grounded RAG (Wallat 2025 2-metric), polish NLP, „Mirage of Halu Detection" critique EMNLP 2025 |
| 03 | dane | Polish CitationBench v0.6 (11,000 chunks + 5,402 halu pairs): ISAP 2,541 + UOKiK Q&A+decyzje+raporty + EUR-Lex 1,360 + qa_raw 2,945 (Reddit+e-prawnik+forumprawne) + court judgments 597 + encyclopedic Wikipedia. Wariant B cleanup audit (drop 38.4%). Halu injection 5 typów. NLI 3-tier labeling. ~110-160 par gold standard |
| 04 | eda | rozkłady halu types, source_type distribution (9 typów), citation lengths, scope filter audit (per-source decyzje Wariant B), polish question characteristics |
| 05 | architektura | **CENTRALNY** — 7 figur Mermaid: C4 Context + C4 Container + C4 Component (probe training loop) + ingestion flow + inference + citation alignment + continuous improvement loop + drift detection sequence + Gradio UI mockup |
| 06 | modele | hidden-states probe details (linear LR primary, MLP nonlinear ablation, Bielik 11B v3 layer 47) + 3-tier verifier (mDeBERTa Tier 1 ✓ T1 PASS 80.6% + HerBERT Tier 2 fallback + LLM judge Tier 3) + Bielik generator + ablations A0-A4 |
| 07 | wyniki | probe AUROC z bootstrap CI vs baselines (Lynx, HHEM, gliclass) + citation accuracy (Wallat 2-metric: faithfulness + correctness) + cykle retreningu konvergencja + error analysis 6-poziomowa + ablations A0-A4 |
| 08 | podsumowanie | synteza RQ1-RQ4 + 5-wymiarowa kontrybucja (probe + dataset + verifier + Gradio + methodology) + future work (multi-turn, cybersec adversarial halu, cross-domain transfer to other polish legal domains) |

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
2. **Read context** — `02_konspekt_v3.2_skeleton.md` (sekcja mapująca do rozdziału) + `decisions/DEC-003*.md` + `decisions/DEC-004*.md` + (jeśli rozdział R3/R4) `notes/scope_cleanup_decisions_2026-05-16.md` + (jeśli rozdział R2/R6) `research/halu_detection_sota_2024_2026.md` + `research/probes_polish_llm_research.md` + `research/nli_alternatives_2026.md`
3. **Draft** — pełen tekst rozdziału. Reguły:
   - Time-proofed: bez "obecnie", "rosnące", "brak", "jedyny", "żaden"
   - Cytacje verifiable, flag niepewności
   - Defensibility nad novelty
   - Spójność terminologii z konspekt v3.2
   - **Polish consumer rights** jako domena; ISAP/UOKiK/Reddit jako sources
   - **Bielik 11B v3** jako probe target + generator; **mDeBERTa Tier 1** jako primary verifier
4. **Self-review** — checklist:
   - [ ] Wszystkie zdania bronią się przed promotorem Kojałowiczem
   - [ ] Brak phantom citations (np. `sdadas/polish-nli` NIE istnieje)
   - [ ] Footnotes spójnie numerowane (IEEE)
   - [ ] Linki do tabel/rysunków konsekwentne
   - [ ] PJATK format zachowany
   - [ ] NIE wymieniaj farma/ChPL/Ulotka/reranker fine-tuning (DEC-003 OUT)
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

Te zasady wynikają z konkretnych ocen z poprzedniego tematu pracy (v1 administracja). Promotor: mgr inż. Piotr Kojałowicz. **Constraint na writing rozdziałów R1-R8 (.docx), NIE na pliki spec wewnętrzne** (`02_konspekt_v3.2_skeleton`, `notes/`, ADR-y).

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

**2. Naukowy kontekst MUST be substantial.** Minimum **10-15 cytacji** w R1 dla rozkładu pola (RAG, hallucination detection, citation grounding, hidden-states probes, polish NLP, MLOps continuous training). Nie odkładaj całej literatury do R2.

**3. Academic style throughout (apply globally):**
- Trzecia osoba lub strona bierna: ✅ *„W pracy zaprojektowano…"* / ❌ *„Zaprojektowałam…"*
- Bez potocznych zwrotów (nawet jeśli są w naszych roboczych docs)
- Krótkie zdania, jedno zdanie = jedna myśl
- Bez "obecnie", "rosnące", "brak", "jedyny", "żaden" (time-proofing)
- Bez emoji w finalnych rozdziałach (w spec docs OK, w R1-R8 absolutnie nie)
- Konsystentne kursywy dla terminów technicznych przy pierwszym wystąpieniu
- **Czysty akademicki polski — NIE codemix English-Polish** w drafcie pracy (CLAUDE.md + spec docs OK, R1-R8 NIE).

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
| `02_konspekt_v3.2_skeleton.md` | OK jako spec wewnętrzny — RQ-first OK tu |
| `notes/sources_z_v3.1_do_reuse_w_v3.2.md` | OK + zawiera ~24/31 ref reusable + framing carry-over (~70% R1 adapter) |
| `research/halu_detection_sota_2024_2026.md` | OK — source-of-truth dla R2 hallucination detection lineage + selection methodology |
| ADR-y (DEC-003, DEC-004) | OK — ADR strukturalnie wymagają explicit options/reasoning, nie podpadają pod regułę 1 |
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
- [ ] NIE referencujesz farma/ChPL/Ulotka/reranker (DEC-003 OUT) ✓?

---

# Defense scaffolding (v3.2 post-pivot DEC-003)

Trzy mikro-podszepty zatwierdzone 2026-05-16. **Zaszywaj je w odpowiednich rozdziałach systematycznie**, żeby praca broniła się przy każdym empirycznym wyjściu eksperymentów.

## 1. Ablation studies w cyklu 1 (R6 + R7)

Cykl 1 retreningu probe ma uwzględniać **cztery ablacje** (każda osobny MLflow run, każda osobny wynik do dyskusji w R7):

| Ablacja | Wariant | Cel diagnostyczny |
|---|---|---|
| **A0 (baseline)** | Probe na Bielik 11B layer 47 + mDeBERTa Tier 1 NLI verifier + Bielik 11B generator + post-hoc citation alignment | Pełen pipeline reference |
| **A1: probe → semantic entropy** | Klasyczny semantic entropy (Farquhar 2024) zamiast hidden-states probe | Czy hidden-states bije classic uncertainty? |
| **A2: probe target → mniejszy / większy Bielik** | Probe na Bielik 1.5B vs 3B vs 11B activations | Trade-off compute vs detection quality |
| **A3: verifier → LLM-as-judge** | Bielik / PLLuM / Gemma 3 / Claude Haiku z few-shot prompting zamiast mDeBERTa NLI | Czy programatic NLI bije LLM-judge dla polish? Plus RQ4 supporting (kappa ≥0.50) |
| **A4: citation → generation-time** | Bielik instruct + Outlines structured output zamiast post-hoc alignment | Czy generation-time bije post-hoc dla polish? Pending T2 lab GPU PASS dla diakrytyki |

**Dodatkowa ablacja R7 (Tier 0):** gliclass-multilang-ultra jako alternative NLI baseline per `research/nli_models_2026_update.md`.

**Decyzja w R6.4 (Ablation studies):**
> *"W cyklu 1 wykonano cztery ablacje (A1-A4) służące diagnostyce źródła poprawy halu detection. Wyniki ablacji raportowane w sekcji 7.X."*

## 2. Kategoryczna error analysis (R7)

Po każdym cyklu retreningu probe, **kategoryzacja błędów** na próbce ≥100 niepoprawnych predykcji (probe predicted halu=False ale faktycznie halu, lub odwrotnie):

| Kategoria błędu | Definicja operacyjna | Mitygacja |
|---|---|---|
| **Factual fabrication** | LLM dodaje claim którego NIE ma w retrieved context, probe NIE alarm | Probe re-train z więcej factual_fabrication examples |
| **Entity confusion** | LLM myli podmioty/instytucje, probe nie alarm | NLI verifier secondary signal compensates |
| **Temporal drift** | LLM podaje błędną datę / okres, probe nie alarm | Probe re-train z dataset Wariant B (drop CHF/franki orzeczenia minimalizuje temporal noise) |
| **Negation flip** | LLM odwraca sens (subtle), probe nie alarm | Hardest case — known limitation, flag w R8 |
| **Paragraph mis-citation** | LLM cytuje art. X ale treść z art. Y | Citation alignment post-hoc catches this independently |
| **Ambiguous claim** | claim multi-interpretable, multiple evidence equally plausible | Acceptable — flag w taxonomy, NIE liczyć jako error |

**Decyzja w R7.4 (Error analysis):**
> *"Błędy probe kategoryzowane zgodnie z 6-poziomową taksonomią (Tabela 7.X). Rozkład kategorii informuje o priorytetach przyszłych iteracji."*

Nawet jeśli AUROC nie poprawia się dramatically, **rozkład błędów to wartościowy wynik metodologiczny**.

## 3. Negative-result publishability framing (R8)

W rozdziale R8 (Podsumowanie) jawnie zapisz **rozdzielność kontrybucji**:

> *"Wkład pracy ma pięć niezależnych wymiarów. Empiryczna magnitude poprawy probe AUROC (RQ1) jest tylko jednym z nich:*
>
> *1. **Metodologiczny:** pierwszy publicznie udokumentowany polish hallucination detection methodology (Mu-SHROOM 2025 pominął polski; AggTruth ICCS 2025 = English-only).*
> *2. **Inżynierski:** reprodukowalny pipeline citation-grounded RAG + halu probe + 3-tier NLI verifier (open-source artefakt).*
> *3. **Artefaktowy:** trzy modele/datasety na HuggingFace — Polish CitationBench v0.6 (11,000 chunks + 5,402 halu pairs) + hidden-states halu probe model + mDeBERTa polish-tuned verifier (jeśli Tier 2 fine-tune w R6 ablation).*
> *4. **Eksperymentalny:** porównanie hidden-states probe vs multilingual baselines (Lynx, HHEM, gliclass) na polish corpus + Wallat 2-metric (faithfulness vs correctness).*
> *5. **Korpusowy:** pierwszy polish CitationBench dataset z deterministic citation grounding (ISAP-based), Wariant B cleanup audit, 9 source_types diverse coverage.*
>
> *Każdy z pięciu wymiarów broni się niezależnie. W przypadku odrzucenia H1 (probe AUROC <0.70 lub CI lower <0.60), praca zachowuje wkład w wymiarach (2)-(5), z dataset jako wyróżnioną kontrybucją (standalone publishable artifact dla polish NLP community)."*

Zaszyj ten paragraf w R8.1 lub R8.2. To jest **defensive shield dla obrony** — promotor i komisja widzą *"co jeśli probe leży?"* od razu i widzą że masz odpowiedź wcześniej niż padnie pytanie.

## Anti-patterns
- **Nie pisz rozdziału bez outline + sign-off.** Tracisz godzinę a autorka i tak każe przepisać.
- **Nie cytuj z głowy.** Każda cytacja musi mieć źródło które można sprawdzić. `sdadas/polish-nli` NIE istnieje (phantom citation z poprzedniego research).
- **Nie używaj** "obecnie", "rosnące zainteresowanie", "brak prac", "jedyny", "żaden" — wszystko się starzeje w 6 miesięcy.
- **Nie commituj** wersji rozdziału bez peer-glance autorki, chyba że ona poprosi.
- **Nie usuwaj defense scaffolding sekcji** — to świadoma obrona, nie dekoracja.
- **Nie wracaj do farma/ChPL/Ulotka/reranker fine-tuning** — explicit OUT per DEC-003 + supersession DEC-002.
