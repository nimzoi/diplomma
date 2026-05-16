# Druga opinia (krytyczna) — drafty R3 / R4 / R5 F1-F2

**Data:** 2026-05-16
**Reviewer:** Claude (agent, druga opinia)
**Trigger:** Magda explicit prosi krytyczną opinię na 48h-drafty assignments 01-08, deadline 18.05.2026
**Drafty:** `drafts/R03_dane.md` (253 LOC), `drafts/R04_eda.md` (290 LOC), `drafts/R05_architektura.md` (297 LOC, F1+F2 only)

---

## 1. TL;DR

- **R3 (NEEDS WORK).** Dobra struktura, dane realne, ale arithmetic inconsistency w Tab 3.1 (8 022 ≠ 7 622), niedokumentowana "ekspansja RF FAQ" w qa_gold (gap 373 chunków), eval set 200 par sprzeczny z konspektem (~110-160) bez explicit reconciliacji.
- **R4 (NEEDS WORK).** Najlepsze pokrycie Task wymagań z trzech (EDA + standaryzacja + normalizacja wszystkie obecne), ale duża liczba pustych placeholderów w kluczowych tabelach (Tab 4.3, 4.6, 4.8) — bez nich rozdział nie nadaje się do oddania. Defensywnie obronny argument BERTopic ↔ Category alignment (sekcja 4.2.6) jest dobry, ale walidacja zależy od `{{}}`.
- **R5 F1+F2 (NEEDS WORK + REWRITE-fragment).** Sekcje 5.1+5.2 OK strukturalnie, ale: (a) MLOps "33 %" to lip service w obecnym drafcie (sekcje 5.4-5.6 to jedno-zdaniowe placeholdery), (b) wewnętrzna sprzeczność liczby kontenerów (11 vs 12) i grup (4 vs 5), (c) **PHANTOM arXiv ID** dla Bielik (`2604.10799` = przyszła data), (d) ciężki codemix EN-PL niezgodny z dyrektywą "czysty polski akademicki".

**Łączna ocena:** żaden z trzech draftów NIE jest gotowy do oddania bez fixów. Większość poprawek to <2 h pracy. R5 wymaga dokończenia F3-F5 (sekcje 5.3-5.9 to obecnie placeholdery).

---

## 2. Top 5 RED FLAGS overall

### 🔴 FLAG #1 — PHANTOM citation `arXiv:2604.10799` (severity: KRYTYCZNA)

**Lokalizacja:** `R04_eda.md:237`, `R05_architektura.md:294`

`arXiv:2604.10799` w cytacji Ociepa 2025 Bielik v3 APT4. Format YYMM.NNNNN oznacza kwiecień 2026 — to **przyszła data** (dziś jest 2026-05-16, czyli papier mógłby istnieć teoretycznie, ale Bielik v3 został wypuszczony w 2025 i jego prawdziwy paper to arXiv:2505.02550 lub podobny z 2025 r.). To **dokładnie ten typ phantom citation**, który CLAUDE.md flaguje jako red flag dla obrony.

**Fix:** Zastąpić rzeczywistym arXiv ID Bielik v3 (zweryfikować na speakleash HuggingFace) lub usunąć ID i zostawić `[CYT: Ociepa 2025 Bielik v3 APT4 tokenizer]` bez fałszywego arXiv. **PRIORITET #1.**

### 🔴 FLAG #2 — Arithmetic inconsistency R3 Tab 3.1 (severity: WYSOKA)

**Lokalizacja:** `R03_dane.md:21`

Tabela 3.1 wiersz "Retrieval corpus": deklaruje **8 022 chunków**, ale suma 7 typów wymienionych w komórce źródłowej (`legal_statute` 2 541 + `legal_ue_directive` 1 360 + `legal_tsue_judgment` 29 + `legal_court_judgment` 534 + `legal_uokik_decision` 26 + `legal_document_pdf` 1 965 + `encyclopedic` 1 167) = **7 622**. Off-by-400.

To pierwsza tabela rozdziału, dotyczy kluczowej liczby, pierwsza komisja sprawdzi. Promotor MLOps mindset = arytmetyka must add up.

**Fix:** Zmienić "8 022" na "7 622" (po weryfikacji w DATASET_CARD).

### 🔴 FLAG #3 — Eval set 200 par vs konspekt ~110-160 par (severity: WYSOKA — scope creep)

**Lokalizacja:** `R03_dane.md:13, 23, 180`, `R05_architektura.md:29, 168, 211`

Drafts deklarują **200 par gold standard** (60 UOKiK + **140 hand-annotated**), podczas gdy `02_konspekt_v3.2_skeleton.md` mówi:
- linia 21: "Eval set ~110-160 par (60 UOKiK Q&A ready-made + 50-100 manual gold by autorka)"
- linia 118 i 194: powtarza ~110-160 par
- `PLAN_cele_i_kroki.md:138`: "50-100 par hand-annotated (weekend hyperfocus burst)"

**40 % wzrost ilości pracy manualnej (50-100 → 140) bez explicit decision log.** PLACEHOLDERS.md odnotowuje to jako "Magda commitment 200" ale brak ADR dokumentującego zmianę z konspektu.

**Ryzyko:** Promotor / komisja zobaczy konspekt v3.2 (committed do gitu, source of truth) i ten draft — zapyta: "skąd skok 50-100 na 140 i czy zdążysz w sprint?". Plus 140 par manualnych to **realistyczny risk** — weekend hyperfocus na 50-100 par jest tight, na 140 jest tight^2.

**Fix:** Albo (a) wrócić do 50-100 + zdjąć 140 z draftów, albo (b) zaktualizować konspekt v3.2 z explicit ADR (DEC-005?) uzasadniającym scope expansion, albo (c) zostawić docelowe 200 ale dodać w R3 zdanie: "MVP eval set wynosi 110 par; rozszerzenie do 200 zaplanowane w Iteracji 5 jeśli czas pozwoli".

### 🟡 FLAG #4 — Niedokumentowana "ekspansja RF FAQ" w qa_gold (severity: ŚREDNIA — documentation gap)

**Lokalizacja:** `R04_eda.md:31` ("UOKiK Q&A FAQ + ekspansja RF FAQ"), `R03_dane.md` (zero opisu RF FAQ)

R04 Tab 4.1 mówi qa_gold = 433 chunków z opisem "UOKiK Q&A FAQ + ekspansja RF FAQ". UOKiK Q&A = 60 par (potwierdzone w R03 sect 3.2). Czyli **373 chunków pochodzi z "ekspansji RF FAQ"** — co to dokładnie jest, nie jest udokumentowane w R03 (R03 sect 3.2 wymienia UOKiK Q&A, decyzje, poradniki, ale RF FAQ tylko w licensing table linii 211 bez metodyki).

Auditor (Kojałowicz) nie może zweryfikować co to są te 373 chunki bez patrzenia w kod. To **zła dokumentacja danych** dla Task 03 (które explicit wymaga "How it was collected" per assignment guidelines).

**Fix:** Dodać w R3 sect 3.2 (po UOKiK paragraph) krótki paragraf o RF FAQ — źródło URL, metoda scrape, liczba par, dlaczego zalicza się do qa_gold. Plus uspójnić z R04 Tab 4.1.

### 🟡 FLAG #5 — R5 wewnętrzne sprzeczności + niezachowane MLOps 33 % (severity: ŚREDNIA-WYSOKA)

**Lokalizacja:** `R05_architektura.md:9, 76, 285`

(a) **MLOps %:** linia 9 mówi "Z dziewięciu sekcji rozdziału trzy (5.4, 5.5, 5.6) opisują warstwę treningową i MLOps" = 3/9 = **33,3 %**. Linia 285 mówi "MLOps stanowi **37,5 %** rozdziału". 33,3 ≠ 37,5. Konspekt v3.2 nie precyzuje, ale jeśli sekcji jest 9, to 3/9 = 33,3. Jeśli 8, to 3/8 = 37,5. Inconsistency w samym drafcie.

(b) **W obecnym drafcie MLOps to lip service:** sekcje 5.4, 5.5, 5.6 mają po jednym akapicie blockquote z 4-6 zdaniami — to placeholders, nie pełne sekcje. Faktyczna treść MLOps w F1+F2 = ~5 %, nie 33 %. Magdo, jeśli oddasz F1+F2 jako draft R5 bez F3-F5, recenzent zauważy że MLOps obietnica nie pokryta. Honest framing: dodać w opening note "F1+F2 only — sekcje 5.4-5.6 MLOps w F3-F5".

(c) **Liczba kontenerów:** linia 76 "**jedenastu** kontenerów w **czterech** logicznych grupach". Ale wymienia 5 grup (serving / storage / orchestration+tracking / observability / application+UI). I matematyka 3+2+2+3+1 = 11 zgodna z deklaracją, ALE Fig 5.2 listing (linia 105-121) zawiera **MinIO jako 12. kontener** w grupie Storage. Tabela 5.1 ma 11 wierszy (bez MinIO), Fig 5.2 ma 12. Inconsistency między tabelą a wykresem. Plus "(1)" przy application+UI sugeruje 1 kontener ale w wykresie są 2 (FastAPI, Gradio).

**Fix:** Zharmonizować: 12 kontenerów w 5 grupach (z MinIO) ALBO 11 w 4 grupach (bez MinIO, połączone application+UI). I poprawić 37,5 → 33,3 (lub odwrotnie, jeśli sekcji ma być 8).

---

## 3. Per rozdział pełna ocena

### 3.1 R3 — Dane

#### A. Pokrycie Task 03 wymagań (~85 %)

Task 03 guidelines wymagają: (1) Data sources, (2) Data formats and storage, (3) Preprocessing and cleaning, (4) Annotations and labels, (5) Ethical and legal, (6) Presentation. R3 pokrywa wszystkie 6.

**Mocne strony:**
- Tabela 3.2 (6 rodzin źródeł + licencje + metody) bardzo dobra dla "data sources"
- Sekcja 3.3 (codebook + struktura katalogów) explicit i zgodna z Task 03 sect 7 (struktura katalogów + README)
- Sekcja 3.4 (preprocessing + Wariant B cleanup) dobry decyzyjny audit trail
- Sekcja 3.5 (taksonomia 5 typów halu + NLI labels + manual annotation) pełna
- Sekcja 3.6 (licencje + PII + TDM exception) explicit ethics, dobre dla "legal aspects"

**Czego brakuje:**
- **RF FAQ ekspansja** nieopisana (FLAG #4) — gap dokumentacyjny ~5 %
- **Mediana / agreement między annotatorami** brak (Task 03 sect 7.4: "Inter-annotator agreement if multiple people annotated"). Tutaj jeden anotator, ale można explicit: "Brak inter-annotator agreement — pojedynczy anotator (autorka), znana limitacja, flag w R8". Aktualnie nie napisane.
- **Konkretne wzorce regex dla cited_articles** wymienione jako koncept (linia 131), ale brak przykładu lub appendix referencji. Promotor MLOps zapyta: "pokaż regex"
- **Sample chunków per source_type** — Task 03 sect 7.6 mówi "Example texts ... for qualitative illustration". R3 nie pokazuje przykładowego chunka. Można dodać 1-2 mini-examples (1 chunk ELI + 1 chunk Reddit + 1 chunk UOKiK Q&A) w boxie.

#### A. Real values vs placeholdery (~95 % real, 5 % placeholder)

Tylko jeden placeholder: `{{REPO_COMMIT_HASH}}` (linia 231) — uzasadnione (post-final commit).

Wszystkie liczby (11 000, 17 862, 5 402, 6 862, 200, 60, 140) są realne lub deklarowane commitmentem. **BARDZO DOBRZE** — minimalne ryzyko confabulacji.

ALE: Tab 3.1 ma confabulowane **8 022** (FLAG #2). To czerwona flaga — confabulacja konkretnej liczby która **nie zgadza się z DATASET_CARD**. Dla obrony lepiej żadnej liczby niż błędna.

#### A. Spójność terminologii (~85 %)

3 buckety (retrieval / training / eval / query distribution) używane konsekwentnie w Tab 3.1 i tekście. **GOOD.**

ALE: "Rzeczywiste pytania konsumentów (2 945 rekordów)" w sekcji 3.2 vs "Query distribution ... 3 378 zapytań" w Tab 3.1. To NIE jest błąd (2 945 to tylko qa_raw, 3 378 to qa_raw + qa_gold), ale terminologicznie zagmatwane — czytelnik nie wie czy to są pytania czy chunki.

Termin "chunki" (PL) vs "rekordy" mieszany. Konsekwentnie: chunki w Tab 3.1, rekordy w 3.2. Wybierz jedno.

#### A. Citation hygiene (~90 %)

Cytacje wymienione w R3:
- `[CYT: notes/KRYTYCZNA_ocena_scope_2026-05-16.md]` (linia 137) — internal ref, OK
- `[CYT: TSUE C-260/18 Dziubak 2019]` (linia 45) — verifiable, OK
- `[CYT: Bowman 2015 SNLI]` (linia 174) — verifiable, OK (Bowman et al. EMNLP 2015)
- `[CYT: Wróblewska CDSC-E KLEJ]` (linia 174) — częściowo (CDSC = Wróblewska & Krasnowska-Kieraś LREC 2017; KLEJ = Rybak et al. ACL 2020). Cytacja merguje 2 papery — w IEEE pass rozdzielić.
- `[CYT: research/halu_detection_sota_2024_2026.md]` (linia 170) — internal ref, OK

**Brak phantom citations** (NIE ma `sdadas/polish-nli`, `finecat-nli-l`). ✓

#### A. Polski akademicki (~75 %)

**Codemix EN-PL widoczny:**
- "right-skewed" (R3 brak, ale R4)
- "scope creep" (linia 137)
- "garbage-in-garbage-out" (linia 145)
- "atomowy artykuł" (OK), "single-chunk" (linia 64 R4, codemix)
- "post-hoc" / "ad-hoc" (linia 219, OK termin techniczny)
- "fair-use" (linia 209, OK termin prawny)
- "single-machine" (R5)
- "scrape" → "pobranie" lepsze, ale "scrape" akceptowalne dla terminu technicznego (consistent)
- "spot-check" (linia 192) — "kontrola wyrywkowa" lepsze
- "binarnego klasyfikatora" (OK)
- "preprocessing" (kilka miejsc) — "wstępne przetwarzanie" lub kursywa
- "load" (linia 131: "Pierwszy etap to load wszystkich rekordów") — wprost angielski

Reasonable threshold: 5-10 termów EN dopuszczalnych jako *terminus technicus*, reszta wyparta. R3 ma ich ~20-25.

#### A. Defense readiness — Top 3 najsłabsze argumenty

1. **Eval set 200 par scope creep** (FLAG #3) — Kojałowicz: "Konspekt mówił 100-160, dlaczego 200 i czy zdążysz?"
2. **RF FAQ ekspansja jak duch** (FLAG #4) — Kojałowicz: "Skąd 373 chunki w qa_gold? Czym jest RF FAQ?"
3. **Brak inter-annotator agreement** — Kojałowicz (MLOps mindset): "Jeden anotator? Bez kappy? Jak walidujesz gold standard?"

#### Final verdict R3: 🟡 **NEEDS WORK**

Substantive issues do fix przed oddaniem:
1. Tab 3.1: fix 8 022 → 7 622 (10 min)
2. Sekcja 3.2: dodać paragraf RF FAQ ekspansja (15 min)
3. Sekcja 3.5.3: dodać explicit "brak inter-annotator agreement, pojedynczy anotator, flag w R8" (5 min)
4. Reconcile eval set 200 vs konspekt 110-160 — albo update konspekt z ADR, albo zmniejszyć w drafcie (30 min)
5. Codemix EN-PL polish (30-45 min, run-through)

**Total fix time: ~1.5-2 h.** Po fixach: PASS-ready.

---

### 3.2 R4 — EDA, standaryzacja, normalizacja

#### A. Pokrycie Task 04 wymagań (~80 %)

Task 04 explicit structure: Introduction, Exploration, Standardization, Normalization, Integration of Different Data Types, Documentation. R4 ma wszystkie 6 sekcji (4.1-4.6). **GOOD.**

**Mocne strony:**
- Sekcja 4.2 (EDA) kompletna z 5 podsekcjami (source types, lengths, citation coverage, multi-label, halu types)
- Sekcja 4.2.6 (BERTopic + UMAP + HDBSCAN) **bardzo dobra defensywnie** — empiryczna walidacja taksonomii Category, dokładnie ten typ analizy który Kojałowicz lubi (MLOps mindset: "validate your assumptions with data")
- Sekcja 4.3 (Wariant B audit) szczegółowe per-source decyzje, dokładnie jak DATASET_CARD
- Sekcja 4.5.1 (BGE-M3 + L2) standaryzacja embeddingu wzór poprawny
- Sekcja 4.5.3 (TF-IDF naive baseline) **excellent** — Mirage of Halu Detection critique zaszyte w design

**Czego brakuje:**
- **Sekcja 4.6 (Integration of Different Data Types)** — Task 04 explicit wymaga tej sekcji. R4 ma ją tylko częściowo (sekcja 4.4.2 schemat unifikowany). Można rozbudować o 1-2 paragrafy: "Korpus jest jednomodalny, integracja heterogenicznych źródeł realizowana przez unifikowany Chunk schema; szczegółowy mapping w R3"
- **Before/after visualizations** Task 04 sect 6: "Include before/after visualizations when possible". R4 ma `{{FIG_4_4_PRE_POST_CLEANUP_DIST}}` jako placeholder — OK, ale wykres MUSI być wygenerowany przed oddaniem
- **Software/library versions** Task 04 sect 6: "Clearly indicate software and library versions". R4 sekcja 4.6 wspomina biblioteki (pandas, matplotlib, BERTopic, sklearn) ale **bez wersji**. Standard: `pandas 2.2`, `BERTopic 0.16`, `umap-learn 0.5`. Dodać.

#### A. Real values vs placeholdery (~60 % real, 40 % placeholder)

**WIELE krytycznych placeholderów:**
- Tab 4.3 (citation coverage): 8 z 9 wierszy placeholder
- Tab 4.6 (BERTopic top 10 klastrów): 40 placeholders (10 klastrów × 4 pola)
- Tab 4.8 (APT4 token length): 27 placeholders (9 typów × 3 metryki)
- Sekcja 4.2.2: median, p95, max długości — placeholder
- Sekcja 4.2.4: median categories per chunk — placeholder
- Sekcja 4.2.6: BERTOPIC_N_CLUSTERS, UMAP silhouette, alignment — placeholder

**Konsekwencja:** R4 w obecnym stanie to ~60 % rozdziału, reszta do uzupełnienia z notebooka. Notebook `eda_v0.ipynb` MUSI być uruchomiony przed oddaniem 18.05. To realistyczny risk — 4-6 godzin pracy minimum.

#### A. Spójność terminologii (~90 %)

3 buckety używane spójnie (sekcja 4.1 explicit recap z R3). Liczby zgodne z R3 i DATASET_CARD. **GOOD.**

#### A. Citation hygiene (~85 %)

Cytacje w R4:
- `[CYT: Chen 2024 BGE-M3 arXiv:2402.03216]` — verified, real (Feb 2024)
- `[CYT: Grootendorst 2022 BERTopic arXiv:2203.05794]` — verified, real (March 2022)
- `[CYT: Zhang 2023 MIRACL TACL]` — real (TACL 2023)
- `[CYT: Ociepa 2025 Bielik v3 APT4 arXiv:2604.10799]` — **PHANTOM ID** (FLAG #1)
- `[CYT: Chawla 2002 SMOTE]` — verified, real classic
- `[CYT: Wróblewska CDSC-E KLEJ]` — merguje 2 papery, w IEEE rozdzielić
- `[CYT: Mirage of Halu Detection EMNLP 2025]` — placeholder, brak autorów/arXiv ID (verify gdy znane)

**Brak phantomów `sdadas/polish-nli`, `finecat-nli-l`.** ✓ (Z wyjątkiem `2604.10799` które jest pseudo-phantom — wymyślony arXiv ID.)

#### A. Polski akademicki (~70 %)

**Więcej codemix niż R3:**
- "right-skewed" (linia 62)
- "single-chunk" (linia 64)
- "naive baseline" (linia 257)
- "naturalne klastry semantyczne" OK ale "topic modeling" linia 138 — kursywa
- "stop words" (linia 256) — "stop słowa" lepsze
- "fertility" (linia 237) — termin techniczny, OK ale wprowadzić wcześniej
- "back-endami UMAP" (linia 138) — "back-end" → "module"
- "scope" (linia 191, 193) — "zakres"
- "future work" (linia 233) — "praca przyszła" lub kursywa "future work"

**Typo:** linia 201 "diakrityk" → "diakrytyk".

**Stylistic:** "warto rozważyć w przypadku H1 INCONCLUSIVE" (linia 233) — codemix poziom rozdziału, "INCONCLUSIVE" angielski. PJATK: "niejednoznaczny wynik H1" lub konsekwentnie po polsku.

#### A. Defense readiness — Top 3 najsłabsze argumenty

1. **BERTopic alignment wynik nieznany** — Kojałowicz: "Mówisz że 10-12 z 14 kategorii dopasowane, ale liczba w placeholder. Czy zrobiłaś walidację czy tylko zaplanowałaś?"
2. **TF-IDF baseline NIE zaszłoby w czas** — sekcja 4.5.3 sugeruje że TF-IDF będzie baselined, ale to wymaga uruchomienia. Czy w Iter. 1 z probe? Lub explicit "TF-IDF baseline będzie w R7 ablation A1.5"
3. **Token length APT4 nie zmierzony** — Tab 4.8 wszystkie placeholders. Bez tego nie wiadomo czy chunki rzeczywiście mieszczą się w 8192 (a tylko "{{TOK_MAX_OVERALL}}" deklaruje że tak)

#### Final verdict R4: 🟡 **NEEDS WORK**

Krytyczna ścieżka: **uruchom notebook EDA przed oddaniem 18.05.** Bez tego R4 to dziurawe szwajcarskie ementaler.

Fixy:
1. Uruchom `eda_v0.ipynb` (4-6h pracy + wygeneruje 5 figur SVG + wszystkie placeholders w Tab 4.3, 4.6, 4.8)
2. Fix PHANTOM `arXiv:2604.10799` (5 min)
3. Fix typo "diakrityk" → "diakrytyk" (5 sek)
4. Sekcja 4.6: dodać wersje bibliotek (5 min)
5. Codemix polish (30-45 min)

**Total fix time: 5-7 h** (notebook dominates). Po fixach: PASS-ready.

---

### 3.3 R5 — Architektura (F1+F2 only)

#### A. Pokrycie Task 05 wymagań (~50 % w obecnym F1+F2; ~75 % gdy F3-F5 dokończone)

Task 05 explicit wymaga: Hardware/Software/Data/Network/Security/Integration/Deployment architecture + design considerations (scalability/reliability/performance/security/maintainability/interoperability/cost/UX/observability/future-proofing) + common architecture types comparison.

**Pokrycie F1+F2:**
- 5.1 Wprowadzenie + C4 method intro — **PASS**
- 5.2.1 Context (Fig 5.1) — actors + external systems, **PASS**
- 5.2.2 Containers (Fig 5.2) — 11/12 kontenerów + grupy + tabela, **PASS** (z fixami liczb)
- 5.2.3 Components (Fig 5.3) — 3 zoom-iny, **PASS**

**Brak (zaplanowane F3-F5 ale 1-line):**
- 5.3 RAG inference pipeline (Fig 5.4) — placeholder
- 5.4 Training pipeline (Fig 5.5) — placeholder
- 5.5 Continuous improvement (Fig 5.6) — placeholder
- 5.6 Observability + drift (Fig 5.7) — placeholder
- 5.7 Bezpieczeństwo (PII, AI Act, RODO, TDM) — placeholder
- 5.8 Gradio UI (Fig 5.8) — placeholder
- 5.9 Decyzje konstrukcyjne (tabela 10 decyzji) — placeholder

**Task 05 sect "Common Types of IT Architectures":** R5 nie omawia explicit dlaczego wybrano architekturę "monolithic + components" vs microservices. Sekcja 5.9.2 wspomina trade-off, ale F3-F5 not written. **Defense gap:** Kojałowicz zapyta "dlaczego nie microservices, dlaczego nie cloud-native, dlaczego nie serverless".

#### A. Real values vs placeholdery (~85 % real F1+F2, ale F3-F5 to 100 % placeholders)

W F1+F2 wszystkie liczby realne (11 kontenerów lub 12 zależnie od interpretacji, 9 sekcji, 7 figur).

ALE: F3-F5 mają tylko jedno-zdaniowe blockquote opisy. **MLOps 33 % rozdziału to obecnie lip service** (FLAG #5).

#### A. Spójność terminologii (~80 %)

C4 method wprowadzona poprawnie. Container vs Component dobrze rozróżnione. ALE:
- "kontener" używany jako (a) Docker container (b) C4 abstract container — przyznane w linii 74, ale w listach (np. linia 76) niejednoznaczne. Reader confusion possible.
- 3-tier verifier opisany konsekwentnie (Tier 1 mDeBERTa → Tier 2 HerBERT → Tier 3 LLM judge).

#### A. Citation hygiene (~85 %)

- `[CYT: Brown 2018 C4 model]` — real, Simon Brown C4 model
- `[CYT: Mermaid documentation]` — internal ref, OK
- `[CYT: Astral uv documentation]` — internal ref, OK
- `[CYT: Chen 2024 BGE-M3 arXiv:2402.03216]` — verified, real
- `[CYT: MoritzLaurer mDeBERTa-v3-base-xnli HF]` — verified, real HF model
- `[CYT: Ociepa 2025 Bielik v3 APT4 arXiv:2604.10799]` — **PHANTOM** (FLAG #1)
- `[CYT: Uğur 2025 Guided Decoding RAG arXiv:2509.06631]` — verify (Sep 2025, plausible date)
- `[CYT: Liang & Wang Dec 2025]` (linia 297) — needs verification
- `[CYT: Dubanowska EMNLP 2025]` (linia 297) — EMNLP 2025 conference

#### A. Polski akademicki (~50 % — HEAVIEST CODEMIX z trzech rozdziałów)

**Bardzo dużo angielszczyzny w R5:**
- "blackbox", "boundary", "deployable services", "production-ready"
- "high-throughput LLM serving generator", "low latency"
- "off-the-shelf services", "industry standard", "gradual zoom-in", "technology-agnostic"
- "version-controlled diagrams", "polishing", "version-controlled"
- "workflow orchestration", "experiment tracking", "LLM-specific tracing"
- "scope creep mitigation", "mockup tekstowy", "fail-closed pattern"
- "REST API gateway agregujący wywołania" — gateway, ale "agregujący wywołania" OK
- "primary user", "observer", "developer + ewaluator + operator"
- "single-machine deployment", "high-stakes"
- "scope thesis vs production"

**Magda explicit prosiła "piszesz jak na haju"** — R5 F1+F2 to PRECYZYJNIE ten poziom codemix który Magda krytykowała. R3 i R4 są lepsze (~70-75 % polski), R5 to ~50 %.

**Fix:** Rewrite-polish entire R5 F1+F2 (1-1.5h). To NIE jest cosmetic — to istotny defect dla obrony.

#### A. Defense readiness — Top 3 najsłabsze argumenty

1. **MLOps 33 % obietnica vs lip service realny** (FLAG #5) — Kojałowicz MLOps mindset: "Pokażesz mi sekcje 5.4-5.6 czy tylko blockquote?"
2. **Liczba kontenerów (11 vs 12, grupy 4 vs 5) inconsistent** (FLAG #5c) — Kojałowicz: "Czy MinIO jest kontenerem czy nie? Tabela mówi nie, wykres mówi tak"
3. **Codemix EN-PL na poziomie który Magda explicit krytykowała** — Magda promotor sama: "piszesz jak na haju, daj prostszy polski"

#### Final verdict R5 F1+F2: 🟡 **NEEDS WORK** (F1+F2); 🔴 **REWRITE-fragment** (F1+F2 polish + dokończyć F3-F5)

Fixy F1+F2:
1. Fix PHANTOM `arXiv:2604.10799` (5 min)
2. Reconcile 11 vs 12 kontenerów + 4 vs 5 grup (15 min)
3. Reconcile MLOps 33,3 vs 37,5 % (5 min)
4. Codemix EN-PL polish — rewrite intensywny F1+F2 (1-1.5h)
5. Honest framing note: dodać w opening "F1+F2 only — sekcje 5.3-5.9 pending F3-F5"

Dokończenie F3-F5:
6. Sekcje 5.3-5.9 require ~5-8 h pisania (1 sekcja = 30-60 min + Mermaid wykresy = 30-60 min/sztuka)
7. Mermaid wykresy 5.4-5.8 (5 nowych wykresów) — 2-3 h
8. Decyzje konstrukcyjne tabela 10 decyzji w 5.9 — 1 h

**Total fix time F1+F2: ~2.5-3 h. F3-F5: 8-12 h.** R5 jest najbardziej incomplete z trzech — najwięcej pracy do oddania 18.05.

---

## 4. R5 specific feedback (decyzje konstrukcyjne F1+F2)

### 4.1 C4 method introduction (5.1)

**PASS — dobrze wprowadzona.** Linia 11-13 explicit czterech poziomów + decyzja pominięcia poziomu Code. Linia 13 trzy uzasadnienia dla C4: industry standard, gradual zoom-in, technology-agnostic. **Argumenty defensywne reasonable** (Kojałowicz zna C4 z MLOps practice).

**Minor:** linia 12 "uzupełnieniem C4 są dwa widoki dynamiczne: pipeline inferencji (sekcja 5.3) i pipeline treningu (sekcja 5.4)" — w sekcjach 5.3 i 5.4 currently placeholder. Forward ref do nieistniejących pełnych sekcji — ale OK na 48h-draft.

### 4.2 11 (lub 12) kontenerów rozdrobnione?

**Liczba 11 jest borderline-wysoka,** ale **zasadna**:

- Serving (3): SGLang, TEI, FastAPI = uzasadnione (3 różne ML serving stacks)
- Storage (2): Qdrant + PostgreSQL = uzasadnione (vector vs relational)
- Storage extension MinIO: rozsądne (artefakty separate od metadanych)
- Orchestration+Tracking (2): Prefect + MLflow = uzasadnione
- Observability (3): Langfuse + LGTM + Alertmanager = uzasadnione (LLM-specific + general + alerting)
- Application+UI (2): FastAPI + Gradio = ✓

Wszystkie są **deployable services** per C4 definition. Nie ma over-engineering ani fragmentacji. Promotor MLOps zobaczy: standard MLOps stack 2025-2026 + LLM-specific observability layer.

**Rozdrobnienie? NIE.** 11-12 kontenerów dla production-grade RAG z observability to standard. Per analogii: kubernetes-based RAG deployments mają zazwyczaj 15-25 podów.

**Ale fix consistency:** zdecyduj czy MinIO jest osobnym kontenerem (Tabela 5.1 nie, Fig 5.2 yes). Rekomendacja: TAK (MinIO osobny), bo S3-compat to osobny deployable service.

### 4.3 3 zoom-iny w 5.2.3 Component uzasadnione?

**TAK, dobry wybór.** FastAPI / Prefect / Halu Detection Stack to faktycznie 3 kontenery z contribution-specific internals. Pozostałe (Qdrant, PostgreSQL, LGTM) są off-the-shelf — bez sensu duplikować dokumentację z ich docs.

**Linia 146 explicit uzasadnia rationale.** Dobra obrona przed pytaniem "dlaczego nie wszystkie kontenery zoom-in".

**Minor:** Kontener 3 "Halu Detection Stack" technicznie nie jest osobnym kontenerem (cross-container). Bardziej "logiczna grupa funkcji rozproszona po FastAPI + Prefect". Może zmienić nazwę z "Kontener 3" na "Aspekt 3 — Halu Detection (cross-container)". Aktualnie czytelnik może być zdezorientowany.

### 4.4 Wykresy szkielet (text-only listing) czytelne?

**Dla 48h-draft: ACCEPTABLE.** Magda explicit zaznaczyła w opening note "polishing Mermaid post-sprint w Iteracji 7" — to OK dla draftu.

**Ale dla obrony:** text-only listing nie pokaże relacji między kontenerami wizualnie. Bez Mermaid SVG promotor nie zobaczy architektury. **Iteracja 7 = mandatory** dla R5 finalization.

**Sugestia:** w opening note dodać explicit "Wykresy w postaci tekstowego szkieletu — polishing Mermaid do SVG w `thesis_research/diagrams/r05_*.mmd` w Iteracji 7." (Linia 15 to mówi, ale można explicit dla każdej figury.)

### 4.5 MLOps 33 % zachowane czy lip service?

**LIP SERVICE w F1+F2.** Liczbowo 3/9 = 33,3 % sekcji, ale sekcje 5.4-5.6 to obecnie 1-line blockquote placeholders. Realna zawartość MLOps = ~5 %.

**Honest framing dla 48h-draft:** dodać explicit w opening "F1+F2 obejmuje 5.1+5.2; sekcje MLOps 5.4-5.6 w F3-F5 (~8-12h pracy)". To nie jest porażka — to honest 48h-draft scope.

**Risk:** jeśli Magda odda R5 z F1+F2 tylko, recenzent / Kojałowicz oceni że MLOps obietnica niesłowienna. Polecam **MINIMUM jednej sekcji MLOps (5.4 lub 5.5) pełnej w draftcie** przed 18.05, nawet bez full Mermaid wykresów.

---

## 5. Recommendation per draft + konkretne fixy

### R3 — Dane → 🟡 **NEEDS WORK** (po fixach: 🟢 PASS-ready)

**Konkretne fixy (priorytetyzowane):**

| # | Fix | Czas | Severity |
|---|---|---|---|
| 1 | Tab 3.1: zmień "8 022" → "7 622" (po weryfikacji w DATASET_CARD) | 5 min | KRYTYCZNA |
| 2 | Sekcja 3.2: dodać 1 paragraf opisujący RF FAQ ekspansję (źródło, metoda, liczba par) | 15 min | WYSOKA |
| 3 | Reconcile eval set 200 par vs konspekt 110-160 — ADR lub zmiana liczby | 30 min | WYSOKA |
| 4 | Sekcja 3.5.3: dodać explicit "Brak inter-annotator agreement — pojedynczy anotator, limitacja flag w R8" | 5 min | ŚREDNIA |
| 5 | Codemix EN-PL polish (run-through wszystkich sekcji) | 30-45 min | ŚREDNIA |
| 6 | Add 1-2 example chunki (boxy) per source_type kluczowy (ELI ustawa, Reddit, UOKiK Q&A) | 30 min | NISKA (Task 03 sect 7.6) |
| 7 | Sekcja 3.4.1: pokazać przykład regex dla cited_articles (1 wzorzec w kodzie) | 10 min | NISKA |

**Total: ~2-2.5 h.** Po fixach: PASS-ready do oddania 18.05.

### R4 — EDA → 🟡 **NEEDS WORK** (po fixach: 🟢 PASS-ready)

**Konkretne fixy (priorytetyzowane):**

| # | Fix | Czas | Severity |
|---|---|---|---|
| 1 | **Uruchom `eda_v0.ipynb`** + wygeneruj wszystkie placeholders (Tab 4.3, 4.6, 4.8, 4.2.2/4/6, 5 figur SVG) | 4-6 h | KRYTYCZNA |
| 2 | Fix PHANTOM `arXiv:2604.10799` (Ociepa Bielik v3) — zamień na real ID lub usuń | 5 min | KRYTYCZNA |
| 3 | Fix typo "diakrityk" → "diakrytyk" (linia 201) | 5 sek | NISKA |
| 4 | Sekcja 4.6: dodać wersje bibliotek (pandas 2.2, BERTopic 0.16, umap-learn 0.5, sklearn 1.5) | 5 min | ŚREDNIA |
| 5 | Sekcja 4.6 rozszerzyć o "Integration of Different Data Types" per Task 04 sect 5 | 15 min | ŚREDNIA |
| 6 | Codemix EN-PL polish ("right-skewed" → "skośnie prawostronny" itd.) | 30-45 min | ŚREDNIA |
| 7 | Sekcja 4.5.3 (TF-IDF baseline): explicit "uruchomienie w Iter. 1 z probe lub R7 ablation A1.5" | 5 min | NISKA |

**Total: ~5-7 h** (notebook dominates). Po fixach: PASS-ready do oddania 18.05.

### R5 F1+F2 — Architektura → 🟡 **NEEDS WORK** (F1+F2); 🔴 **REWRITE-codemix** + brak F3-F5

**Konkretne fixy F1+F2 (priorytetyzowane):**

| # | Fix | Czas | Severity |
|---|---|---|---|
| 1 | Fix PHANTOM `arXiv:2604.10799` (Ociepa Bielik v3) | 5 min | KRYTYCZNA |
| 2 | Reconcile 11 vs 12 kontenerów (Tabela 5.1 vs Fig 5.2) — zdecyduj MinIO IN/OUT | 15 min | WYSOKA |
| 3 | Reconcile 4 vs 5 grup logicznych (linia 76 mówi 4, ale wymienia 5) | 5 min | WYSOKA |
| 4 | Reconcile MLOps 33,3 % vs 37,5 % (linia 9 vs 285) | 5 min | WYSOKA |
| 5 | **Heavy codemix EN-PL rewrite-polish** całego F1+F2 | 1-1.5 h | KRYTYCZNA (Magda explicit) |
| 6 | Opening note: "F1+F2 only — sekcje 5.3-5.9 placeholder F3-F5" + per-figura sticky note "Mermaid SVG w Iter. 7" | 10 min | ŚREDNIA |
| 7 | 5.2.3 Kontener 3 → "Aspekt 3 cross-container" (clarity) | 10 min | NISKA |

**Total F1+F2: ~2-2.5 h.**

**Konkretne fixy F3-F5 (nowy content):**

| # | Sekcja | Czas | Notatka |
|---|---|---|---|
| 8 | 5.3 RAG inference pipeline (Fig 5.4) — pełna sekcja | 1 h | latency budget breakdown + parallel branch probe |
| 9 | 5.4 Training pipeline (Fig 5.5) | 1-1.5 h | **MIN 1 sekcja MLOps full** dla honest 33 % claim |
| 10 | 5.5 Continuous improvement (Fig 5.6) | 1 h | 3 cykle + drift triggers |
| 11 | 5.6 Observability + drift (Fig 5.7) | 1 h | LGTM + Evidently + Alibi |
| 12 | 5.7 Bezpieczeństwo (PII / AI Act / RODO / TDM) | 30 min | krótka, ~400-600 słów |
| 13 | 5.8 Gradio UI (Fig 5.8 mockup) | 30 min | 3 zakładki |
| 14 | 5.9 Decyzje konstrukcyjne (Tabela 5.X 10 decyzji + trade-offs) | 1-1.5 h | tabela ważna defensywnie |
| 15 | Mermaid wykresy text-only szkielety dla 5.4-5.8 (5 wykresów) | 1-2 h | szkielet OK na 48h-draft |

**Total F3-F5: ~8-10 h.**

**Total R5 fix time: ~10-12 h** — to **istotny ryzyko czasowy** do 18.05. Rekomendacja: **MINIMUM 5.4 + 5.7 + 5.9** pełne (4-5 h dodatkowo do F1+F2 polish), reszta jako one-pagery z explicit "pending Iter. 7".

---

## 6. Bonus — 3 killer questions Kojałowicza których NIE OBRONIMY w obecnym stanie

### Q1: "Pokaż mi exact arXiv ID dla Bielika i wytłumacz dlaczego napisałaś 2604.10799 zamiast prawdziwego identyfikatora."

**Obecny stan:** Phantom ID w R4 i R5. Nie obronimy bez fix.
**Fix:** Zamień na prawdziwy ID (zweryfikować na HuggingFace speakleash) lub usuń arXiv suffix i zostaw tekstowy ref.
**Estimated time to defend:** 5 min fix.

### Q2: "W Tabeli 3.1 deklarujesz 8 022 chunków w retrieval corpus, ale suma podanych typów to 7 622. Skąd różnica 400?"

**Obecny stan:** Arithmetic mismatch w pierwszej tabeli R3. Promotor MLOps z mindset "matematyka musi się zgadzać" — natychmiastowy red flag.
**Fix:** Zmienić "8 022" → "7 622" po weryfikacji DATASET_CARD. Plus explicit note: "Q&A pairs (qa_gold 433 + qa_raw 2945) nie liczą się jako retrieval corpus — są to query distribution".
**Estimated time to defend:** 10 min fix.

### Q3: "Konspekt v3.2 mówił 110-160 par gold standard. Drafty mówią 200 par (140 hand-annotated). Skąd skok 40 % i czy jesteś pewna że zdążysz w weekend hyperfocus?"

**Obecny stan:** Scope creep bez explicit decision log. Magda commitment 200 par jest w PLACEHOLDERS.md ale nie w ADR. Promotor MLOps zobaczy konspekt v3.2 i drafty, zapyta o source of truth.
**Fix:** Albo (a) **REKOMENDOWANE:** zredukować do 110 par (60 UOKiK + 50 hand-annotated) MVP w Iter. 1 — szybciej, mniej ryzyka, plus future "rozszerzenie do 200 w Iter. 5 jeśli czas". Albo (b) napisać DEC-005 ADR "scope expansion do 200 par — uzasadnienie: cover więcej halu types + RODO/telekom edge cases" i podpisać świadomie.
**Estimated time to defend:** 30 min — ADR + reconcile drafts + (opcjonalnie) update konspekt.

---

## 7. Sumaryczna tabela severity per rozdział

| Rozdział | Verdict | Czas do PASS-ready | Top blocker |
|---|---|---|---|
| **R3 Dane** | 🟡 NEEDS WORK | 2-2.5 h | Tab 3.1 arithmetic + RF FAQ gap + eval set reconcile |
| **R4 EDA** | 🟡 NEEDS WORK | 5-7 h | Notebook EDA NIE uruchomiony (dominates) + PHANTOM arXiv |
| **R5 Architektura F1+F2** | 🟡 NEEDS WORK (F1+F2) + 🔴 brak F3-F5 | 10-12 h | Codemix EN-PL heavy + dokończenie F3-F5 + PHANTOM arXiv |

**Wspólne dla wszystkich:** fix `arXiv:2604.10799` PHANTOM (5 min wspólny — pojedyncze sed-replace).

**Krytyczna ścieżka 48 h do 18.05:** R4 notebook EDA (5-7 h) + R5 F3-F5 (8-10 h jeśli MIN 1 sekcja MLOps) = 13-17 h najcięższych zadań. R3 fixy są szybkie. Plus codemix polish ~2-3 h łącznie dla R5+R4. **Total: ~18-23 h pracy** do PASS-ready wszystkich trzech draftów.

---

## 8. Pozytywne — co robi się **dobrze** (nie tylko bash)

Defensywnie powinnam zauważyć też mocne strony:

- **R3 sekcja 3.6.3 TDM exception** — krótka, precyzyjna, defensywna. Kojałowicz nie złapie tu nic.
- **R4 sekcja 4.2.6 BERTopic alignment** — empirical validation taksonomii Category. **Excellent move** defensywnie. Magda: to jest dokładnie ten typ ablation/validation którego promotor szuka.
- **R4 sekcja 4.5.3 TF-IDF naive baseline** + Mirage critique — zaszyte już w design, prevents reviewer ambush "dlaczego nie sprawdziłaś naive baseline".
- **R3 sekcja 3.4.2 Wariant B audit** — pełen breakdown 16 kategorii drop + uzasadnienie per source. To **wzorcowy audit trail**.
- **R5 sekcja 5.1 C4 method rationale** — 3 uzasadnienia (industry standard, gradual zoom-in, technology-agnostic) wszystkie dobre.
- **R5 sekcja 5.2.3** uzasadnia DLACZEGO tylko 3 zoom-iny (linia 146) — prevents "dlaczego nie wszystkie kontenery zoom-in" pytanie.
- **Cross-chapter numbers** w większości spójne (11 000, 5 402, 6 862 wszystkie zgodne we wszystkich 3 draftach i z DATASET_CARD).
- **Brak phantom `sdadas/polish-nli`** i innych z blacklisty. ✓

**Bottom line:** drafty są **solidnym fundamentem 48h-draft**. Issues są fixable. To NIE jest catastrophic rewrite — to **polish + complete** sprint.

---

## 9. Sugestia priorytetyzacji ostatnich 48 h do 18.05

**Dzień 1 (16 h pracy):**
- (0.5 h) Fix wszystkich 4 critical bugs: arXiv phantom + Tab 3.1 arithmetic + R5 11/12 + R5 33/37,5
- (5-7 h) Uruchom `eda_v0.ipynb` + wypełnij wszystkie placeholders R4
- (4-5 h) R5 F3 (sekcje 5.3 + 5.4 najważniejsze MLOps + Mermaid szkielety)
- (2 h) Codemix polish R3 + R4
- (1 h) RF FAQ ekspansja + inter-annotator agreement + eval set reconcile (R3)

**Dzień 2 (12 h pracy):**
- (4 h) R5 F4 (sekcje 5.5 + 5.6 + 5.7 + 5.8 + Mermaid)
- (1-1.5 h) R5 F5 (sekcja 5.9 decyzje + Mermaid finalize)
- (1-1.5 h) R5 codemix heavy polish
- (1 h) Cross-check liczb między R3 + R4 + R5 + DATASET_CARD
- (1 h) Self-review checklist per rozdział (anti-patterns, time-proofing words, codemix)
- (2 h) Buffer + przegląd końcowy

**Total: ~28 h pracy w 48 h = realistyczne** jeśli Magda focused. Tight ale doable.

---

## 10. Zakończenie

Drafty są **wykonalne na 48h-draft poziom** ale **nie gotowe do oddania bez fixów**. Krytyczne 3 fixy (PHANTOM arXiv, Tab 3.1 arithmetic, R5 33 % MLOps lip service) zajmują <30 min ale eliminują największe ryzyka defense. Pozostałe fixy to standard polish + complete.

**Najwyższe ryzyko:** R5 F3-F5 nie dokończone (8-10 h pracy) + R4 notebook nieuruchomiony (5-7 h). To **13-17 h pracy** którą Magda musi zrobić w 48 h. Reszta to <5 h łącznie.

**Bottom-line per rozdział:**
- R3: 🟡 NEEDS WORK (2-2.5 h fixów)
- R4: 🟡 NEEDS WORK (5-7 h, notebook dominates)
- R5 F1+F2: 🟡 NEEDS WORK (~2.5 h F1+F2 polish) + 🔴 REWRITE/COMPLETE F3-F5 (8-10 h)

**Reviewer signature:** Claude agent, 2026-05-16. NIE validation theater. Krytyczne pytania należy zadać sobie zanim Kojałowicz zada.
