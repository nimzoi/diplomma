# Cross-draft consistency review — 2026-05-16

> **Review scope:** R1–R8 fresh drafts + R03_draft (legacy duplikat) vs source-of-truth (CLAUDE.md × 3, 02b_konspekt_v3_updates.md, DEC-001/002, sources_catalog.md, thesis_elements/CLAUDE.md Defense scaffolding).
> **Mode:** READ-ONLY — flag only, NIE auto-fix.
> **Reviewer note:** Magda preferuje brutally honest critical feedback nad validation theater. Findings są poukładane od najpoważniejszych — proszę nie czytać tego jako "pochwał z drobnymi drobiazgami".

---

## 1. Verdict

**NEEDS FIXES before next iter.**

Drafty są strukturalnie solidne (8/8 napisane, scaffolding zaszyte, 5 RQ konsystentnie obecne, ~55k słów łącznie). ALE są **trzy klasy systemowych niezgodności wymagające manual fix przed rozpoczęciem Iteracji 7 manual writing**: (1) numeryczne inconsistencies między rozdziałami w empirycznych założeniach (random seeds, hardware, rozmiar cyklu treningu), (2) terminology drift wokół "polish-specific linguistic patterns" (II.2.1 update z 2026-05-16 NIE propagated do R5/R6), (3) phantom-style cytacje z `🟡` flagami nieprzefiltrowane przez citation-checker (~30+ uncertain cites, ten sam Grabowski cytowany jako 2017 w R2/R7/R8 ale 2018 w R1 — phantom title możliwa). Bez fix przed Iter. 7, manual writing będzie zaostrzało te inkonsystencje zamiast je gasić.

---

## 2. Top-3 critical issues

1. **NUMERYCZNE INCONSISTENCIES między R5/R6/R7 dla założeń eksperymentalnych** — severity **HIGH** (każda komisja PJATK to wyłapuje za 5 minut):
   - **Random seeds:** R6 § 6.2.5 + 6.4.1 + 6.5.5 = `{42, 1337, 2026}`; R7 § 7.1 = `{42, 1337, 2718}`. Trzy różne miejsca x dwa różne seeds = 100% probability że promotor zauważy.
   - **Hardware:** R6 § 6.2.5 = "SP7 H200 80GB"; R5 § Sequence Diagram = "SP7 H100"; R7 § 7.1 = "SP5 A100 40GB, inference SP7". Trzy rozdziały, trzy różne configs hardware.
   - **Rozmiar cyklu 1 preference:** R6 § 6.6.3 = "cykl 1 cumulative 50k" + § 6.6.5 cycle dataset versioning = "preferences_cycle_1.jsonl ~50k samples"; R7 § 7.3.1 = "cykl 1 ~145k quadrupletów"; ale 145k jest CUMULATIVE po 3 cyklach per 02b II.4.6 / R6 / training_dataset_spec.md — to twardy konflikt między R6 i R7.
   - **Recommended fix:** ujednolicić w SINGLE source w R6, R7 i R5 → cykl 1 = ~50k samples; cumulative cykl 3 = ~145k. Random seeds = `{42, 1337, 2026}` (per R6 + 02b II.4.5 trzymane od dawna). Hardware = SP7 H200 (R6 trzyma) — R5 i R7 muszą się dopasować.

2. **TERMINOLOGY DRIFT wokół II.2.1 update z 2026-05-16** — severity **MEDIUM-HIGH** (niespójność z aktualnym source-of-truth):
   - Updated rationale w 02b § II.2.1 (line 45) brzmi: *"Long tail polish-specific linguistic patterns wokół międzynarodowej terminologii"* (NIE "long tail terminologii psychiatrycznej / farmaceutycznej" jak pre-update).
   - **Status w drafts:** R1 § 1.2 (line 35) = WŁAŚCIWA wersja ("polish-specific patternów językowych wokół niej") ✅. R2 § 2.7 (line 232) używa "Polish-specific rerankery" w innym kontekście (nie rationale). **R5/R6/R7 — wcale nie używają tego rationale**, omijają argument. R8 § 8.1 wcale nie wspomina nowego framing rationale.
   - Risk: jeśli R1 broni rationale przez "polish-specific patterns", a R5/R6 mają tę samą decyzję rerankera bez echa tego rationale, promotor zapyta "skoro to fundamental, czemu R6 (gdzie reranker jest opisany) tego nie cytuje".
   - **Recommended fix:** dodać jeden paragraf w R6 § 6.2.1 (Sformułowanie problemu rerankera) cytujący polish-specific rationale + cross-link do R1 § 1.2. R5 § 5.1 założenia może też dodać linijkę.

3. **CITATION HYGIENE — Grabowski rok inconsistency + phantom title risk** — severity **HIGH** (citation-checker priorytet):
   - **R1 [19]** (line 167): Grabowski **2018** *"On Identification of Bilingual Lexical Bundles for Translation Purposes..."* z note "✓ verified 2026-05-16 (rok skorygowany 2017→2018; tytuł phantom 'Towards an Online Comparable Corpus...' zastąpiony faktycznym tytułem rozdziału w CILT 341)".
   - **R2 [26]** (line 324): Grabowski **2017** *"Towards an Online Comparable Corpus of English-Polish Patient Information Leaflets"* z `🟡 Verify`.
   - **R3 [8]** (line 547): Grabowski **2017** identyczny tytuł phantom.
   - **R7 [1]** (line 577) + **R8 [8]** (line 201): Grabowski **2017** identyczny tytuł phantom.
   - **DEC-002** też cytuje 2017 z phantom title (line 54).
   - Risk: R1 already corrected, ale 4 inne pliki dalej cytują phantom version. Jeśli citation-checker biegnie tylko na R1 (gdzie już naprawione), nie wyłapie. Iter. 7 manual writing podtrzyma starą cytację.
   - **Recommended fix:** w Iter. 7 BEFORE manual writing: aplikuj poprawkę z R1 [19] do R2 [26], R3 [8], R7 [1], R8 [8]. To single search-and-replace + re-numerowanie. Update DEC-002 też (lub zostawić jako historical, ale wtedy explicit comment).

---

## 3. Per-category findings

### 3.1 Terminology consistency

**Check:** spójność post-DEC-001:

- ✅ **"farmakologia kliniczna szeroka" jako domena** (NIE "psychiatria"): wszystkie 8 drafts używają konsystentnie. Brak naruszeń. (`grep "polska psychiatria"` zwraca 0 hits w drafts.)
- ✅ **"psych eval subset N05/N06" jako gold standard** (NIE jako domena): konsystentnie cytowane w R1 § 1.4, R3 § 3.5/3.8.4, R4 § 4.8.1, R5 § 5.1, R6 § 6.6.2, R7 § 7.1/7.3.3, R8 § 8.4.3. ✅
- ✅ **"cross-register retrieval" + "ChPL↔Ulotka pairing"**: konsystentnie cytowane jako RQ5/H5/DEC-002 we wszystkich 8 drafts. R5 ma osobny diagram (5.7), R7 ma osobną sekcję (7.5). ✅
- ⚠ **"long tail polish-specific linguistic patterns" rationale (post-update II.2.1 z 2026-05-16):**
  - R1 § 1.2 line 35: ✅ używa nowy wording ("polish-specific patternów językowych wokół niej")
  - R2: nie aplikuje (literature review, nie rationale) — neutralne
  - R3, R4: nie aplikuje (dane/EDA, nie rationale) — neutralne
  - **R5: ❌** § 5.1 założenia — nie cytuje polish-specific patterns rationale dla rerankera
  - **R6: ❌** § 6.1.2 + § 6.2.1 — nie cytuje rationale; opisuje reranker bez "polish-specific" framing
  - **R7: neutralne** (wyniki, nie rationale) — ale interpretation patterns w error analysis (kategoria 1 Terminology miss) mogłaby cytować
  - **R8: ❌** § 8.1 + § 8.2 — wymiar (3) Artefaktowy mówi o "dotrenowanym rerankerze dla farmakologii" bez "polish-specific patterns" framing

  **Per chapter list:**
  - R5: `R5_outline.md § 5.1 line 16` (założenia architektoniczne) → dodaj wzmiankę "polish-specific patterns rationale per II.2.1 → uzasadnia dlaczego reranker fine-tuning jest centralny"
  - R6: `R6_modele.md § 6.1.2 line 47` (Reranker description) → dodaj polish-specific patterns argument zamiast lub obok generic "domain adaptation rerankera"
  - R8: `R8_podsumowanie.md § 8.2 line 31` (wymiar 3 Artefaktowy) → wzmiankuj że artefakt adresuje polish-specific patterns, nie tylko "polską farmakologię"

### 3.2 Defense scaffolding placement

**Check:** 3 mikro-podszepty z `thesis_elements/CLAUDE.md`:

**Pkt 1 (Ablations A1-A4):**
- R6 § 6.4 — ✅ 100% pokryte. Wszystkie 4 ablacje + A0 baseline + diagnostic conclusions per ablacja + tagi MLflow.
- R7 § 7.3.2 — ✅ wszystkie 4 ablacje raportowane z 4-part discussion templates per ablacja.
- R5 § 5.6.1 — ✅ Ablation architecture jako "przełączniki Hydra config".
- ⚠ **A4 ablation doubly-defined** w R6 § 6.4 line 286 mówi "A4a: ChPL-only training (bez Ulotek). A4b (= A0): ChPL+Ulotka training" — to logiczne (A4 = ChPL-only kontrast vs A0 default ChPL+Ulotka), ALE w Tabeli 7.3.2 line 137 R7 bezpośrednio mówi "A4 | ChPL-only training (bez Ulotek)" — tracimy "A4a vs A4b" framing, jest tylko "A4". Decyzja terminologiczna OK ale wymaga harmonizacji: jest A4 = "ChPL-only" lub A4a vs A4b? Recommendation: trzymaj "A4 = ChPL-only training" w obu (eliminacja A4a/A4b nazewnictwa w R6).

**Pkt 2 (Kategoryczna error analysis 6-poziomowa):**
- R7 § 7.7 — ✅ pełna 6-poziomowa taksonomia z definicjami operacyjnymi: terminology miss / ambiguous query / length mismatch / OOD chunk / register mismatch / OCR artifact.
- ✅ Defense scaffolding pkt 2 explicit cited w § 7.7.
- ✅ Mitygacja proponowana per kategoria + intra-rater kappa check.
- ⚠ R6 § 6.5.5 line 400 wspomina o "categorical error analysis (zapowiedź)" ale faktyczna implementacja jest w R7 — to jest spójne, ALE R6 pkt 6.2.7 line 169 mówi "Element 8 z 8-elementowej struktury Task 06 (interpretacja + diagnostics) jest realizowany w R7 jako: Categorical error analysis na próbce ≥100 niepoprawnych rankingów per cykl" — OK, cross-link działa.

**Pkt 3 (5-wymiarowa kontrybucja):**
- R8 § 8.2 — ✅ 100% pokryte, każdy wymiar ma osobny paragraph. Explicit "Każdy z pięciu wymiarów broni się niezależnie" zdanie.
- R1 § 1.3 — ✅ explicit teaser 5 wymiarów (line 51), z explicit niezależności statement (line 63). ✅ defense scaffolding zaszyte już w intro.
- R6 § 6.7 (Podsumowanie rozdziału) — wzmiankuje 5-wymiarowość pośrednio ale brak explicit listy. **Recommendation: dodać 1-zdanie w R6 § 6.7 cytujące R8 § 8.2 + Defense scaffolding pkt 3.**
- R7 § 7.8.4 — ✅ "Mapping 5 RQ → 5 wymiarów kontrybucji" — explicit lista.

### 3.3 Time-proofing audit

**Check:** zakazane słowa "obecnie", "rosnące", "brak", "jedyny", "żaden":

**R1 (Wprowadzenie):**
- Line 17: ⚠ "co w zadaniach z domeny specjalistycznej stanowi istotne ograniczenie" — OK (nie "jedyny"/"obecnie")
- Line 197: ✅ self-check meta-comment ("brak 'obecnie'...") — to placeholder/notatka, NIE prose. OK.
- Line 35 + 95 (omitted) — sprawdziłam: "polish-specific" framing — neutralne.
- Line 123: ⚠ *"jest jednym z wymiarów, ale **nie jedynym** warunkiem sukcesu pracy"* — **subtle violation**: "jedyny" w sensie "niewystarczający" jest acceptable colloquially ale Writing rules zabraniają. **Recommend rewrite:** *"jest jednym z pięciu wymiarów; sukces pracy nie wymaga jego pojedynczego osiągnięcia"*.

**R2 (Literatura):**
- Wiele "brak" w tabelach porównawczych jako **column "Limitation"** — to OK kontekstualnie (np. "Brak multilingual coverage" jako limitation cytowanego paper). ✅
- Line 75: "preprinty bez cytowań, paywall bez DOI, brak verifiability" — meta-comment o pipeline selekcji. OK.
- Line 232 "Polish-specific rerankery to obszar węższy" — neutralne, nie violation.
- Line 258-262: ⚠ "**Brak polish-specific medical reranker** ... **Brak validacji LLM-as-judge** ... **Brak publicznie udokumentowanej**" — WSZYSTKIE 5 pkt podsumowania luki literaturowej zaczynają się od "Brak". To time-proofing violation per Writing rules — sformułowanie "brak prac w temacie" było eksplicite wyłączone przez promotora. **Recommend rewrite całej sekcji 2.8:** *"Polish-specific medical reranker nie został publicznie udokumentowany"* / *"Walidacja LLM-as-judge dla polish medical domain nie pojawiła się w przeglądanej literaturze"* / etc. **HIGH priority dla Iter. 7.**

**R3 (Dane):**
- Line 40, 41, 42: "Brak treści strukturalnej / Zaprzestanie publikacji / brak aktualizacji / Niejednoznaczność" — to są **kryteria wyłączenia**, kontekst meta. OK.
- Line 108: "zarzucone zostało **brak rygorystycznej metodologii**" — quotation z promotor feedback. OK.
- Line 188 "brak dostępności" — kontekst MZ leków zagrożonych dostępnością. OK (terminus techniczny dla shortage list).
- Line 460 "Brak danych osobowych" — section header. OK (factual statement, nie "brak prac").
- Line 566: meta-comment OK.

**R4 (EDA):**
- Line 159: ⚠ *"niektóre subkody używają małych liter dla wariantu (np. **brak takiego konkretu w ATC**, ale np. *iv* vs *IV*..."* — subtle violation. **Recommend:** *"konkretnego przykładu w ATC nie wskazano, lecz analogicznie *iv* vs *IV* w drug administration"*.
- Line 162: ⚠ *"**Jedyny** lowercase punkt: search index BM25"* — VIOLATION. **Recommend:** *"Wyjątek dla lowercase: search index BM25"*.
- Line 291: "brak sekcji ≠ błąd parsingu" — factual technical statement. OK.
- Line 730: ⚠ *"Brak inter-annotator agreement statistics typowe dla manual gold standard"* — VIOLATION. **Recommend:** *"Inter-annotator agreement statistics nie są dostępne dla single-annotator setup"*.

**R5 (Outline):**
- Line 161 (omitted long line): ⚠ sprawdzono: "*żaden komponent nie jest 'ukryty'*" — VIOLATION. **Recommend:** *"każdy komponent ma swoje miejsce w kodzie"*.
- Line 369: ⚠ "RQ5 **nie wymaga osobnego pipeline'u trenowania**" — neutralne, nie violation.
- Line 374, 563: meta-comments. OK.

**R6 (Modele):**
- Line 53: ⚠ "różność modelu względem `<judge_model>` (eliminacja *circular reasoning*)" — neutralne.
- Line 320: "Brak wykonanej którejś z ablacji A1-A4 ... traktowane jako spec violation" — meta-comment. OK.
- Line 340: ⚠ "(jeżeli **żaden** relevant w top-10, to..." — VIOLATION (acceptable mathematical context but Writing rules absolutist). **Recommend:** *"jeżeli wśród top-10 nie znajduje się relevant passage"*.
- Line 460: ⚠ "**żaden** cykl retreningu nie jest deployed bez statystycznej weryfikacji" — VIOLATION. **Recommend:** *"deployment każdego cyklu retreningu wymaga statystycznej weryfikacji"*.

**R7 (Wyniki):**
- Line 54: ⚠ "**bez żadnej** domain adaptation" — VIOLATION. **Recommend:** *"bez domain adaptation"* (pleonastic anyway).
- Line 60: ⚠ "**bez żadnej** domain adaptation" — VIOLATION. Same pattern.
- Line 357 (omitted): sprawdzono — "powinien dawać 'no drift' alarmy z low frequency (false positive rate target ≤ 0.20)" — neutralne.
- Line 387: "Query length < 5 słów AND **brak** named entity" — diagnostic indicator. OK technical context.
- Line 550: ⚠ "manual labels by autorka (single annotator) — **brak** inter-annotator agreement" — VIOLATION (same pattern jak R4). **Recommend:** *"single annotator setup, bez inter-annotator agreement check"*.
- Line 612: meta-checklist. OK.

**R8 (Podsumowanie):**
- Line 53: "AND **brak** regresji na same-register" — falsyfikowalność threshold. OK technical.
- Line 91: ⚠ omitted — sprawdzono: "wymagałaby kohorty ekspertów + etyki + walidacji końcowych odpowiedzi RAG" — neutralne.
- Line 95: ⚠ omitted — "(brak gwarancji długoterminowej dostępności wersji modelu)" — context warning. Borderline.
- Line 105: "**brak** real-time traffic" — VIOLATION (could rewrite as "nie obserwowano real-time traffic w okresie pracy").
- Line 107: "**Brak human evaluation końcowych odpowiedzi RAG**" — VIOLATION. **Recommend rewrite jako:** *"Końcowa odpowiedź ... oceniana wyłącznie przez automated metric"*.
- Line 111: "**brak** cross-language generalization claims" — VIOLATION but contextual. Acceptable (nie generation), ale rewrite preferable: *"Praca nie formułuje cross-language generalization claims"*.
- Line 113: "**brak** cross-domain generalization claims" — same as above.
- Line 117: "**Brak adversarial evaluation rerankera**" — VIOLATION same pattern.
- Line 219: meta-checklist. OK.

**Summary count violations (excluding meta/checklist/quotation):**
- R1: 1 violation
- R2: ~5 violations (sekcja 2.8 = systemic problem)
- R3: 0 (wszystko in-context)
- R4: 3 violations (lines 159, 162, 730)
- R5: 1 violation (line 161)
- R6: 2 violations (lines 340, 460)
- R7: 3 violations (lines 54, 60, 550)
- R8: 4-5 violations (lines 105, 107, 111, 113, 117)

**Total: ~19 violations across 8 drafts.** Manageable w jednej sesji search-and-replace, ale **systemic problem w R2 sekcja 2.8 + R8 sekcja 8.4** (wzorzec "Brak X, brak Y, brak Z") wymaga rewrite paragraph-level.

### 3.4 Cross-references inconsistencies

**Check:** referencje między rozdziałami:

**R3 § 3.10 Świadome biases → R8 § 8.4 Limitations:**
- R3 lista: (1) License bias, (2) ATC bias N05/N06 over-rep, (3) Recency bias, (4) Polish-only bias, (5) Source type bias regulatory dominance. ✅
- R8 § 8.4.1: pięć biasów = identyczna kolejność i nazewnictwo. ✅
- R4 § 4.9.5: dodaje **bias #6 (encoding heterogeneity)** + **bias #7 (single annotator eval set)** — to nowy materiał z EDA.
- ⚠ **R8 § 8.4.1 NIE wspomina biasów #6 i #7 z R4**. Mówi "Pięć świadomych biases korpusu" (line 73) cytując R3 § 3.10, ale ignoruje rozszerzenie o EDA biases. **Recommend fix:** R8 § 8.4.1 dodać "Po EDA (R4 § 4.9.5) zidentyfikowano dodatkowe dwa biases: #6 encoding heterogeneity (dropped diakrytyki w pre-2015 ChPL) + #7 single-annotator caveat dla eval set."

**R5 § Ablation architecture → R6 § 6.4 Ablations:**
- R5 § 5.6.1 line 363: "Cztery przełączniki: A1 / A2 / A3 / A4" — opis A1=judge.source, A2=judge.model, A3=corpus.scope, A4=corpus.register. ✅
- R6 § 6.4 Tabela 6.6: identyczne mapping A0-A4 z diagnostic conclusions per ablacja. ✅
- ⚠ **R5 podaje** "**Wszystkie cztery wykonywane w Iteracji 2** (II.16) — single-cycle scope, każdy z 3 seeds". **R6 § 6.4.1 podaje** "top-K=3 trials per ablacja w cyklu 1, full search 30 trials dla A0". Subtle inconsistency: R5 sugeruje że ablations są równorzędne z A0, R6 mówi że A0 ma full Optuna search ale ablacje tylko top-3. **Recommend harmonization:** explicit zapisać w R5 że "A0 ma full Optuna search 30 trials, ablacje A1-A4 reuse hyperparams z A0 best trial".

**R7 § 7.8 Synteza → R8 § 8.3 RQ status:**
- R7 § 7.8.1 Tabela 7.8.1 ma 5 RQ z status PASSED/PARTIAL/FAILED/NEGATIVE-RESULT. ✅
- R8 § 8.3 Tabela 8.1 ma identyczne 5 RQ + identyczne progi falsyfikowalne. ✅
- ⚠ **Status options w R8 = {PASSED, FAILED, PARTIAL, INCONCLUSIVE}** vs R7 = {PASSED, PARTIAL, FAILED, NEGATIVE-RESULT/REJECTED}. R8 nie ma "INCONCLUSIVE" w R7's vocabulary, R7 ma "REJECTED" (RQ5 specific) w R8 brak. **Recommend harmonization:** uzgodnić jeden 4-value enum (rekomendacja: PASSED / PARTIAL / FAILED / INCONCLUSIVE) w obu.
- ✅ Progi H1-H5 = identyczne (≥10pp / κ≥0.50 / ≤2pp plateau / P≥0.80 R≥0.70 / acc≥70% gap≤5pp).

**R6 § 6.3 4. judge protocol → DEC-002 (cross-register pair scoring):**
- R6 § 6.3.1 Tabela 6.4 line 190: 4. protokół = "Cross-register pair scoring" z (query_lay, passage_pro_A, passage_pro_B) → JSON z `semantic_match_quality` + `register_appropriateness`. ✅
- DEC-002: opisuje 4. protokół tylko w high-level terms (poprzez wzmiankę w II.7 update sekcji w 02b).
- 02b § II.7 line 246-256: identyczna definicja 4. protokołu. ✅
- ✅ Spójność OK.

**R4 § 4.7 paired analysis → R7 § 7.5 cross-register results:**
- R4 § 4.7.6 (line 681): "900 lay→pro pairs + 900 pro→lay pairs ... + 5400 cross-register training pairs"
- R7 § 7.5 (line 258): "1800-parowym eval set RQ5 (900 lay→pro + 900 pro→lay)" + "5400 cross-register training pairs" implicite (cytuje 1800 eval, 5400 training jest implicite via DEC-002).
- ✅ Spójność OK.
- ⚠ R4 § 4.7.5 line 654: section-level alignment methodology używa "BGE-M3 embedding cosine similarity" jako ground truth dla section mapping. R7 § 7.5 NIE cytuje tego jako preview/early signal. **Recommend cross-link** w R7 § 7.5 sekcji "Interpretation": *"per R4 § 4.7.5, section-level cosine similarity dla mapping 4.1→1 = X, dla 4.3+4.4+4.5+4.6→2 = Y — preview difficulty cross-register zanim training"*.

### 3.5 Duplicate drafts comparison

**R03_draft.md (legacy) vs R3_dane.md (fresh):**

| Wymiar | R03_draft.md | R3_dane.md |
|---|---|---|
| Word count | 4,769 | 7,279 |
| Lines | 498 | 573 |
| Sekcje | 3.1–3.10 (kompletne 10) | 3.1–3.10 (kompletne 10) |
| Status banner | "methodology + structure" | "v0.1 (2026-05-16), methodology 100%, liczby końcowe TBD" |
| Tabele | 5 (3.1, 3.2, 3.3, 3.4, 3.5) | 7 (3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7) |
| Algorithm | 3.1 stratified sampling | 3.1 stratified sampling (identyczny pseudokod) |
| Cytacje | brak (legacy) | 10 cytacji bibliografia placeholder |
| Self-check checklist | tak | tak |
| Citation pass requirement | implicit | explicit (`[ ] Citation pass`) |

**Content overlap:** ~85% identyczna treść strukturalna. Różnice:
- R3_dane § 3.7.3 ma rozszerzoną Tabelę 3.6 (codebooks per strata) z "Specyficzne pola" — R03 ma Tabelę 3.4 z mniejszą szczegółowością.
- R3_dane § 3.8 audyt licencji = bardziej szczegółowy (Tabela 3.7 z permissions).
- R3_dane ma bibliografię placeholder + 10 cytacji z 🟡 flagami; R03 nie ma.
- R3_dane ma git status notation `D ../../../thesis_research/drafts/R01_draft.md` — sugeruje że R01_draft był skasowany świadomie (per `git status`). R03_draft pozostaje jako legacy backup.

**Recommendation:** **KEEP R3_dane.md, ARCHIVE R03_draft.md** (przenieś do `thesis_research/drafts/_archive/` lub usuń). R03_draft to wcześniejszy iter z mniejszą szczegółowością — zachowanie obu w aktywnym katalogu wprowadza ryzyko że future agent edytuje jeden a nie drugi. Magda ma decyzję: (a) usuń R03 (czyste rozwiązanie), (b) przenieś do `_archive/` z naming `R03_draft_iter6.md` (audit trail).

**R01_draft.md** — już skasowany per `git status` (`D ../../../thesis_research/drafts/R01_draft.md`). To było świadome działanie autorki/poprzedniej sesji. R1_wprowadzenie.md jest aktualny. ✅ Brak akcji.

### 3.6 Phantom citations check

**Check:** suspicious cytacje wymagające citation-checker:

**R1 (25 cytacji, 10 z 🟡 markers):**
- [3] BGE-M3 Chen et al. 2024 arXiv:2402.03216 — `🟡 verify exact venue`. **Likely real** (arXiv ID provided).
- [4] Nogueira monoT5 — **uncertainty czy to Nogueira & Cho 2019 (BERT) vs Nogueira et al. 2020 (monoT5)**. Different papers, different venues. Critical priority.
- [6] polish-reranker-roberta-v3 Dadas 2024 — model card, brak formal paper. Citation format need verification.
- [10] Pahune & Akhtar 2025 *LLMOps* — `✓ verified 2026-05-16`. ✅
- [13] Bielik 11B v2 vs v3 — anchor cite is v2 (verified), actual model used v3. Recommend explicit dual cite.
- [14] PLLuM Kocoń et al. 2025 arXiv:2511.03823 — `✓ verified`. ✅
- [16] Lu et al. 2018/2019 TKDE — year ambiguity flagged.
- [19] Grabowski 2018 (corrected from 2017) — verified. **BUT R2/R3/R7/R8 still cite 2017** (see Top-3 #3).
- [21] Devaraj 2021 — venue ambiguity (NAACL vs EMNLP). `✓ verified 2026-05-16` w R1 → NAACL-HLT 2021.
- [22] van den Bercken 2019 — `✓ verified` w R1.
- [23] EMA QRD — placeholder, ongoing publication.
- [25] Xiong ANCE 2021 — anchor only, verify.

**R2 (~36 cytacji, ~22 z 🟡 markers):**
- [2] Robertson & Zaragoza BM25 — verify.
- [6] MIRACL Zhang 2023 — venue (TACL vs ACL Findings) — verify.
- [7] Pyserini Lin 2021 — verify.
- [8] Nogueira monoT5 — same uncertainty as R1 [4].
- [10] Dadas polish-reranker — verify author + year.
- [11] BGE-Reranker Xiao — verify (BAAI publication).
- [17] Landis & Koch 1977 — classic reference, but verify in text reuse.
- [18] Bielik SpeakLeash — verify formal paper; R1 [13] used Bielik v2 technical report citation, R2 doesn't yet match.
- [19] PLLuM PolEval consortium — R1 [14] used Kocoń et al. 2025 — **mismatch**. R2 cites "PolEval consortium / NASK / IPI PAN", R1 cites "Kocoń, Piasecki, Janz, Ferdinan, Radliński, et al." — different attribution. R1 is canonical (verified arXiv).
- [21] Treveil 2020 O'Reilly — verify ISBN.
- [24] Evidently — tool reference.
- [25] Alibi Detect — tool reference. R8 [5] cites Klaise et al. 2021 JMLR — different cite for same tool. **Mismatch** between R2 and R8.
- [26] Grabowski 2017 — phantom title risk (see Top-3).
- [28] Devaraj — venue ambiguity (R1 verified NAACL, R2 still uncertain).
- [29] van den Bercken — year ambiguity (R1 verified 2019, R2 still uncertain).
- [30] Rybak KLEJ 2020 — verify.
- [31] polish-reranker-large-mse — verify.

**R3 (10 cytacji, all 🟡):**
- All 10 with 🟡 markers.
- [1] BGE-M3, [6] DPR, [7] Sculley 2015 — repeats of R1/R2 cites.
- [3] Art. 4 ustawy — legal citation, verify aktualny tekst jednolity.
- [4] WHOCC ATC/DDD — web reference, verify access date.
- [5] EMA QRD — placeholder.

**R4 (7 footnotes, all 🟡):**
- [^tesseract], [^spacy_polish], [^umap], [^stanza], [^umap2], [^pisarek] — all flagged.
- [^pisarek] Pisarek 1969 — Polish-specific readability metric, verify exact bibliographic details.

**R5 (TODO list ~10 implicit cites):**
- Prefect 3 / MLflow / Optuna / Evidently / Alibi Detect / LlamaIndex / RAGAS / SGLang / TEI / C4 model — all need explicit cites in TODO § for Iter. 7.
- MLflow Zaharia 2018 cited in TODO list, R8 [6] cites Chen et al. 2020 instead. **Different MLflow citations** between R5 (Zaharia 2018) and R8 (Chen et al. 2020).
- Akiba Optuna 2019 KDD — verify.
- Klaise Alibi Detect 2020 ICML workshop vs R8 [5] cites Klaise 2021 JMLR. **Mismatch**.
- Es et al. RAGAS 2024 EACL — verify exact venue.

**R6 (16 cytacji, ~10 z 🟡):**
- [3] Bielik 11B v3 Ociepa K., Kondej M., Cyrtia G. — **WRONG authors**. Actual paper has Ociepa, Flis, Kinas, Wróbel, Gwoździej (per R1 [13]). **Phantom authors in R6 [3].** Critical priority.
- [11] Mosbach et al. 2021 ICLR — verify.
- [14] Cantor 1996 sample-size kappa — verify.
- [17] Voorhees TREC-8 1999 — verify.
- [19] RAGAS Es et al. 2024 — verify EACL Demo vs main.

**R7 (10 placeholder cites):**
- [1] Grabowski 2017 — phantom title (see Top-3).
- [6] Karp 2025 Polish legal LLM-judge — `🟡 [TBD initials, TBD title]` — **likely phantom** (entire entry is TBD).
- [10] Rabin O. — `🟡 [TBD]` — **likely phantom**.

**R8 (14 cytacji):**
- [1] Bielik — `🟡 Verify exact version + release date`.
- [5] Alibi Detect Klaise 2021 JMLR — vs R5/R2 different cites for same tool.
- [6] MLflow Chen et al. 2020 — vs R5 TODO Zaharia 2018.
- [8] Grabowski 2017 phantom title.
- [10] Devaraj — venue ambiguity (R1 corrected).
- [11] van den Bercken — year ambiguity (R1 corrected).

**Priority list dla `/citations` w Iter. 7:**

**P0 (critical phantom risk):**
1. Grabowski 2017→2018 + phantom title — propagate R1 fix do R2 [26], R3 [8], R7 [1], R8 [8], DEC-002.
2. R6 [3] Bielik 11B v3 wrong authors (Ociepa K., Kondej M., Cyrtia G.) — replace per R1 [13] verified.
3. R7 [6] Karp 2025 Polish legal LLM-judge — verify istnienie or remove cite (current `🟡 [TBD initials, TBD title]` = phantom risk).
4. R7 [10] Rabin O. — verify or remove.

**P1 (cross-chapter inconsistencies):**
5. PLLuM citation: R1 [14] (Kocoń et al. 2025 verified arXiv) vs R2 [19] (PolEval consortium attribution). Use R1 canonical.
6. Alibi Detect: R5 TODO Klaise 2020 ICML workshop vs R8 [5] Klaise 2021 JMLR. Verify which is correct.
7. MLflow: R5 TODO Zaharia 2018 vs R8 [6] Chen et al. 2020. Verify which is correct.
8. Devaraj 2021: R1 corrected to NAACL-HLT 2021 — propagate do R2 [28], R7 [3], R8 [10].
9. van den Bercken 2019: R1 corrected to WWW '19 + DOI — propagate do R2 [29], R7 [4], R8 [11].
10. Bielik citation: R1 [13] uses Bielik 11B v2 technical report as anchor + v3 actual paper. R6 [3] has phantom authors. Harmonize.

**P2 (verify-only, low risk):**
11. ~20+ remaining 🟡 cites without obvious red flags — let citation-checker batch run.

### 3.7 Multi-turn II.13.10 explicit

**Check:** czy R8 § 8.5 future work explicit cytuje II.13.10 z framing "świadoma decyzja, nie oversight"?

- ✅ R8 § 8.5 line 161 = "II.13.10. Multi-turn chat evaluation (NEW, decyzja 2026-05-16)".
- ✅ Framing explicit: line 165 *"Decyzja podjęta 16.05.2026: implicit chat działa via LlamaIndex `ChatEngine`; formalne mierzenie multi-turn coherence dopisane jako future work w R8 po zamknięciu pięciu podstawowych RQ. **Świadoma decyzja, nie oversight** — odsuwane do post-podstawowych-RQ scope dla zachowania zarządzalnego scope pracy dyplomowej."*
- ✅ Explicit IN/OUT scope split: *"Implicit chat handling — IN scope. Multi-turn formal evaluation — OUT scope (future work)"*.

**Implicit chat handling cross-references:**
- ✅ R5 § Stack notka line 10: *"LlamaIndex dla RAG inference (z `ChatEngine` dla implicit multi-turn — II.13.10)"*. Explicit.
- ⚠ **R6 nie wspomina ChatEngine ani multi-turn**. R6 jest o modelach (reranker + judge + generator), nie o RAG inference layer. Decision: probably OK, ale recommend dodać 1-zdanie w R6 § 6.7 (Podsumowanie) cytujące że RAG inference layer (LlamaIndex ChatEngine) handluje implicit multi-turn poza scope niniejszego rozdziału.
- ✅ R7 § 7.7 line 389: cytuje multi-turn jako future work dla query expansion (kategoria 2 Ambiguous query mitigation).
- ❌ **R1 i R3 nie wspominają multi-turn** wcale. R1 w § 1.4 OUT scope wspomina "real-time drift" + "cross-domain generalization" + "cross-language register transfer" ale NIE wspomina że multi-turn formal eval jest też future work. **Recommend** dodać 1 punkt w R1 § 1.4 OUT scope: *"Po szóste, formalna ewaluacja multi-turn coherence (implicit multi-turn handling przez LlamaIndex ChatEngine pozostaje IN scope, formalne metryki conversation coherence — przyszła praca, II.13.10)."*

---

## 4. Per-chapter health snapshot

| Chapter | Słowa | Defense scaffolding | Terminology | Time-proofing | Cross-refs | Verdict |
|---|---|---|---|---|---|---|
| R1 | 5,695 | ✅ pełen 5-wymiarowy teaser | ✅ + polish-specific patterns (jedyny rozdział z nowym wording) | 1 violation (line 123) | OK + multi-turn missing | ⚠ READY z drobnymi |
| R2 | 5,271 | ⚠ pkt 5 (sekcja 2.8) explicite ale wzorzec "Brak X, brak Y" | ✅ | ~5 violations w sekcji 2.8 | OK | ❌ NEEDS FIXES (sekcja 2.8 rewrite) |
| R3 | 7,279 | implicite (R3 dostarcza danych dla całej pracy) | ✅ | 0 (wszystko in-context) | OK + R8 §8.4 nie cytuje #6/#7 | ✅ READY |
| R4 | 7,960 | ✅ #6 + #7 dodane | ✅ | 3 violations (lines 159, 162, 730) | OK | ⚠ READY z drobnymi |
| R5 | 4,316 | ✅ ablation architecture | ⚠ brak polish-specific patterns rationale | 1 violation (line 161) | OK | ⚠ READY z drobnymi |
| R6 | 5,568 | ✅ pełen A0-A4 + judge multi-stage | ⚠ brak polish-specific patterns rationale | 2 violations (lines 340, 460) | A4a/A4b vs A4 inconsistency vs R7 | ⚠ READY z drobnymi |
| R7 | 8,904 | ✅ pełen 6-poziomowy error analysis + 5-RQ synthesis | ✅ | 3 violations (lines 54, 60, 550) | INCONCLUSIVE vs REJECTED status enum mismatch z R8; preference samples 145k vs R6 50k | ❌ NEEDS FIXES (numerical: seeds, hardware, cycle size) |
| R8 | 5,371 | ✅ pełen 5-wymiarowy + 10-pkt future work | ⚠ brak polish-specific patterns w wymiarze 3 | 4-5 violations (lines 105, 107, 111, 113, 117) | brak biasów #6/#7; status enum mismatch z R7 | ⚠ READY z drobnymi |

**Ogólna ocena:** 3/8 ❌ NEEDS FIXES (R2, R7), 5/8 ⚠ READY z drobnymi (R1, R4, R5, R6, R8), 1/8 ✅ READY (R3).

**Word count summary:** Total ~50,500 słów across 8 fresh drafts. PJATK target ~7,500 słów per chapter (45,000 znaków = ~7-8k słów per chapter for bachelor's thesis). Aktualnie:
- Niedoszacowane: R5 (4,316 — outline only, expand do ~7,000 w Iter. 7), R8 (5,371 — można rozszerzyć)
- Na cele: R1 (5,695), R2 (5,271), R3 (7,279), R6 (5,568)
- Przeszacowane (ryzyko trim): R4 (7,960 — ale sekcje EDA z placeholderami będą trim po wypełnieniu), R7 (8,904 — najbliżej limitu, każdy kolejny add wymaga trim gdzie indziej)

---

## 5. Recommended next steps

1. **Fix numerical inconsistencies (highest priority — block przed Iter. 7):**
   - R7 § 7.1 line 34: zmień `{42, 1337, 2718}` → `{42, 1337, 2026}` (alignment z R6 + 02b II.4.5).
   - R7 § 7.1 line 36: zmień "SP5 (NVIDIA A100 40GB), inference na SP7" → "SP7 H200 80GB" (alignment z R6 § 6.2.5).
   - R5 § Sequence Diagram line 490: zmień "SP7 H100" → "SP7 H200" (alignment z R6).
   - R7 § 7.3.1 line 92: zmień "preference learning na ~145k quadrupletów" → "preference learning na ~50k quadrupletów (cumulative ~145k po 3 cyklach)" (alignment z R6 § 6.6.3 + 02b II.4.6).
   - R7 § 7.4 line 227: zmień "nowa próba ~145k preference quadrupletów" → "nowa próba ~50k preference quadrupletów (fresh per cykl, kumulatywnie z cyklów wcześniejszych)" (alignment z R6 § 6.6.5).

2. **Propagate Grabowski citation fix (R1 verified version) do R2, R3, R7, R8, DEC-002:**
   - Search-and-replace: "Grabowski Ł. (2017). *Towards an Online Comparable Corpus of English-Polish Patient Information Leaflets*. In: *Comparable Corpora and Computer-Assisted Translation*, John Benjamins (CILT 341)." → "Grabowski Ł. (2018). *On Identification of Bilingual Lexical Bundles for Translation Purposes: The Case of an English-Polish Comparable Corpus of Patient Information Leaflets*. In R. Mitkov, J. Monti, G. Corpas Pastor & V. Seretan (Eds.), *Multiword Units in Machine Translation and Translation Technology* (pp. 181–200). Current Issues in Linguistic Theory 341. John Benjamins. DOI: 10.1075/cilt.341.09gra." (full verified version z R1 [19]).

3. **Rewrite R2 sekcja 2.8 podsumowanie luki literaturowej (5 pkt z "Brak X" → time-proofed wording):**
   - "Brak polish-specific medical reranker" → "Polish-specific medical reranker nie został publicznie udokumentowany w przeglądanej literaturze".
   - "Brak validacji LLM-as-judge dla polish medical domain" → "Walidacja LLM-as-judge dla polskiej domeny medycznej nie pojawia się w przeglądanej literaturze".
   - "Brak publicznie udokumentowanej Polish ChPL↔Ulotka aligned corpus" → "Polish ChPL↔Ulotka aligned corpus nie został publicznie udokumentowany w przeglądanej literaturze (Grabowski 2018 [19] zawiera EN-PL comparable PIL...)".
   - "Brak simulated drift framework dla polish retrieval system" → "Simulated drift framework dla polskich systemów retrievalu nie pojawia się w literaturze polskojęzycznej".
   - "Brak iteracyjnego retraining framework z plateau analysis" → "Plateau analysis dla iteracyjnego retreningu polskich rerankerów nie zostały empirycznie zbadane".

4. **Add polish-specific patterns rationale do R5 § 5.1 + R6 § 6.1.2 + R8 § 8.2 wymiar (3):**
   - 1-2 zdań cross-link do II.2.1 (post-update 2026-05-16) z explicit reasoning że domain adaptation rerankera adresuje polish-specific patterns wokół międzynarodowej terminologii (NIE międzynarodowej terminologii samej).

5. **Fix status enum mismatch R7 § 7.8 vs R8 § 8.3:**
   - Uzgodnij 4-value enum: PASSED / PARTIAL / FAILED / INCONCLUSIVE (recommend bo bardziej standard).
   - R8 § 8.3 line 43-46: trzymaj ten enum (już używa).
   - R7 § 7.3.1 + 7.5 + etc.: zastąp NEGATIVE-RESULT/REJECTED → INCONCLUSIVE/FAILED (FAILED gdy próg jednoznacznie nie spełniony, INCONCLUSIVE gdy borderline).

6. **R8 § 8.4.1 dodać biasy #6 i #7 z R4 § 4.9.5:**
   - Po liście 5 świadomych biases (lines 73-83) dodać paragraph: *"Po przeprowadzeniu eksploracyjnej analizy danych (R4 § 4.9.5) zidentyfikowano dodatkowe dwa biases: bias #6 (encoding heterogeneity) — pre-2015 ChPL z dropped diakrytykami; bias #7 (single-annotator caveat) — eval set 200 par by single annotator z mitygacją intra-rater consistency check."*

7. **Fix A4 ablation nazewnictwo R6 § 6.4:**
   - Zmień "A4a: ChPL-only training. A4b (= A0): ChPL+Ulotka training" → "A4: ChPL-only training (kontrast vs A0 default ChPL+Ulotka)" (alignment z R7 § 7.3.2 Tabela 7.3.2).

8. **Time-proofing pass — automate gdzie możliwe:**
   - search-and-replace dla "żaden" / "jedyny" / "bez żadnej" w R1, R4, R6, R7, R8 (per § 3.3 violations list).
   - Manual paragraph rewrite dla R2 § 2.8 + R8 § 8.4 (systemic wzorzec).

9. **Archive R03_draft.md:**
   - Magda decyzja: usuń lub przenieś do `_archive/R03_draft_iter6.md`. Recommend przenieś (audit trail), bo legacy treść ma wartość historyczną.

10. **Multi-turn II.13.10 cross-link audit:**
    - R1 § 1.4 OUT scope: dodać multi-turn formal eval jako 6. punkt (OUT scope future work).
    - R6 § 6.7: 1-zdanie cytujące że RAG inference layer (LlamaIndex ChatEngine) handluje implicit multi-turn poza scope rozdziału.

---

## 6. Iteracja 7 prep notes

**Issues do zaadresowania w Iteracji 7 (manual writing/polish):**

1. **Citation pass (P0):** Uruchom `/citations` skill na wszystkich 8 drafts SEKWENCYJNIE, NIE batch (delegate do citation-checker subagent). Priorytet: Grabowski propagation (4 pliki), R6 [3] Bielik phantom authors, R7 [6] + [10] phantom placeholders. Estymowany koszt: 1-2h per draft × 8 drafts = ~10-16h pracy z weryfikacją. **Run as background tasks** kolejno per file.

2. **Diagram /diagram skill verification (P1):** R5 § 5.7 line 371 explicit nota *"Verify via /diagram skill — diagram poniżej jest plausible Mermaid skeleton, NIE skopiowany ze źródła"* dla Cross-register pipeline diagram. Iter. 7 musi uruchomić `/diagram` (z `validate_and_render_mermaid_diagram` MCP) dla **wszystkich 7 diagramów** (5 z `03_diagrams_architektury.docx` + 2 NEW: cross-register + Gradio mock-up). Per `02b § II.5` Gradio Figura 5.8 jest mandatory.

3. **Length trim do PJATK ~7-8k słów per chapter (P1):**
   - R7 (obecnie 8,904 słów) — najbliżej limitu. Jeśli post-Iter. 2-6 fill-in liczb dodaje ~1000 słów, trim Discussion templates do bardziej zwięzłego format.
   - R4 (obecnie 7,960 słów) — placeholder tabele + szablony interpretacyjne będą trim po wypełnieniu liczbami (placeholder tekst znika).
   - R5 (obecnie 4,316 słów outline) — expand do pełnej prose ~7,000 słów per § 5.1-5.8 sekcji.
   - R8 (5,371) — można dodać sekcję 8.5 future work elaboration.

4. **PJATK formatting compliance (P1):** Po final draft każdego rozdziału:
   - TNR 12pt, line spacing 1.5, marginesy 2.5cm.
   - Footnotes IEEE 10pt z bookmark anchors (konwersja `[N]` markdown → footnotes Word).
   - H1 bold 14pt / H2 bold 12pt (Task 09 wersja, sprawdzić finalny PJATK template).
   - Lista tabel + lista rysunków na końcu pracy (mandatory if used; obecnie mamy ~15+ tabel + ~10+ rysunków).

5. **Bibliografia konsolidacja:** Wszystkie 8 drafts mają osobne bibliografie placeholder. Final R8 (lub osobny rozdział "Bibliografia" po R8) musi konsolidować all unique cytacje, sortowane alphabetycznie, ~30+ pozycji per Task 09. Estymowany current count po dedup: ~40-45 unique cytacji.

6. **Self-review checklisty (każdy rozdział ma przy końcu):** Magda powinna manually zweryfikować checkboxy `[ ]` przed konwersją do .docx. Wiele `[ ]` jeszcze nie zaznaczonych (citation pass, cross-link weryfikacja).

7. **R03_draft archival decision:** Zdecyduj BEFORE Iter. 7 — czy R03_draft zostaje aktywny (ryzyko że future agent edytuje zły plik) czy archive.

8. **Verify Bielik 11B v2 vs v3 cite strategy:** R1 [13] używa v2 jako anchor + v3 dla actual model. Inne rozdziały (R6 [3] z phantom authors, R8 [1]) muszą się dopasować. Decyzja: cite **both** v2 (methodology anchor) + v3 (actual model) lub tylko v3 (uproszczenie).

**Summary:** Drafts są w 75-85% completion (per status banners), z **systemic issues** w numerical consistency + citation hygiene + time-proofing. Bez fix Top-3 critical issues + recommended next steps 1-3, Iteracja 7 manual writing zaostrzy te niespójności. Recommend **ALL fixes 1-7 z § 5 BEFORE rozpoczęcia Iter. 7 manual writing** (estymowany koszt: ~6-10h pracy w jednej sesji search-and-replace + paragraph rewrites + citation propagation).

---

**Reviewer:** Claude (cross-draft consistency review)
**Date:** 2026-05-16
**Files reviewed:** 8 fresh drafts (R1-R8), 1 legacy duplicate (R03_draft), 5 source-of-truth files, 2 ADRs.
**Mode:** READ-ONLY — żaden plik poza CROSS_REVIEW report nie został zmodyfikowany.
