# KRYTYCZNA ocena scope 2026-05-16 — devil's advocate przed promotorem

**Tryb:** Validation theater wyłączony. Brutalna prawda > pochwały. Cytuję pliki, liczby, sprzeczności z CLAUDE.md.

**Persona oceniająca:** sceptyczny promotor (mgr inż. Kojałowicz) + cross-checker DEC-003 kill criteria + audyt anti-patterns z CLAUDE.md.

**Zakres audytu:** stan repo po commicie `dac2073` (S6 normalizer + v0.4 dataset 17,862 chunks) — czyli WSZYSTKO co Magda + agenty zbudowali między 2026-05-16 rano (pivot DEC-003) a wieczorem (v0.4 dataset land). To **jeden dzień**.

---

## 1. TL;DR (3 zdania — brutalnie)

**Scope jest niemożliwy do obrony przed Kojałowiczem w obecnej formie.** W ciągu jednego dnia po pivocie DEC-003 zbudowałyśmy dataset 17,862 chunks z 26 unikalnych źródeł i 1.5 GB raw na dysku — gdzie tylko **27%** to faktycznie *consumer rights core* (4,846 z 17,862 per własna kategoryzacja `consumer_core`), **80%** wpadło w bucket `finance_adjacent`, a tylko **240 synthetic halu pairs** (1.3% chunks) jest gotowych do *jedynego rzeczywiście naukowego artefaktu* — probe training. Pivot z farmy na consumer rights w tym momencie wygląda jak **rebrand v3.1 scope creep w nową domenę** — robisz to samo co krytykowała DEC-003 § Kontekst pkt 3 („straciła sense pracy") tylko z polskim prawem zamiast leków, a antywzorzec CLAUDE.md „Nie pisz rozdziałów bez outline + sign-off" już został pogwałcony (R3+R4+R5 drafty 1315 linii istnieją *przed* zakończeniem Iter. 0b POC). **Verdict: POSPRZĄTAĆ scope przed start Iter. 0b — drop ~50% chunks, wytłumacz każde z 26 źródeł, dokończ 4 POC testy z DEC-003 zanim cokolwiek innego.**

---

## 2. Pięć największych RED FLAGS (severity rated)

### 🔴 RED FLAG #1 — Data hoarding zamiast dataset construction (SEVERITY: CRITICAL)

**Co:** Dataset urósł od 5,150 records (Iter. 1a planowane) → 11,591 (v0.1) → 15,784 (v0.2) → 15,790 (v0.3) → **17,862 (v0.4)** w jedne 24h. To wzrost +247%. **Synthetic halu pairs liczba pozostała 240 między v0.1 a v0.4** — czyli przy probe training (jedynym sensownym output v3.2 per RQ1/H1) ratio jest **1.3% pairs / 98.7% irrelevantne chunks**.

**Per CLAUDE.md anti-pattern:** „Nie wzbudzaj scope creep. Cybersec angle = future work pkt R8, NIE central." — analogicznie: Konstytucja RP, KPC 2,084 chunks, frankowicze SN — to **cybersec-poziomu scope creep** dla halu probe.

**Per DEC-003 § Konsekwencje pkt „Negatywne":** „Ustawa o prawach konsumenta jest niewielka (~80 artykułów) — corpus chunks ograniczone, **wymaga uzupełnienia** (Kodeks cywilny, UOKiK, fora) dla wystarczającego material." — DEC-003 przewidział suplement, NIE 24-katalogowy dump.

**Per Magda CLAUDE.md Wzorzec 8 (build-first, finalize-last):** „Najpierw BUILD (scrape, train, eval, demo), potem polish prose." — ALE „BUILD" oznacza buduj to co potrzebne do RQ1-RQ4, nie buduj wszystko co się da scrapnąć.

**Konkret:** Sam korpus consumer-core (UPK 240, KC 92, UOKiK Q&A 60, UOKiK news 111, ECC Polska 400, konsument.gov.pl 393, Federacja 192+262, e-prawnik 948 + bezprawnik 200) = ~2,900 chunks. To wystarczy do RQ1 — probe wymaga halu pairs, nie correlated background chunks. Pozostałe 14,962 chunks (84%) to **noise budget bez probe value**.

---

### 🔴 RED FLAG #2 — KPC 2,084 chunks + Prawo upadłościowe 1,252 chunks = 21% korpusu, NIE consumer rights (SEVERITY: CRITICAL)

**Co:** Kodeks Postępowania Cywilnego (DU/1964/296) i Prawo upadłościowe (DU/2003/535) razem to **3,336 chunks = 18.7% v0.4 dataset**. Brief Magdy z Iter. 0c (S7) sam przyznaje (`thesis_research/research/extra_ustawy_konsumenckie_2026.md` § Defense scaffolding #3):

> *„KPC ma 2084 chunków, większość nie dotyczy konsumentów. Zgodzony. Pełen scrape KPC był pragmatic — analiza konsumencko-relevant fragmentów (post. nakazowe art. 480-499, upominawcze art. 497¹-505, klauzula wykonalności art. 781-795, post. grupowe art. 187¹-187¹¹) wymaga osobnego filtru w `dataset_builder` przed treningiem probe."*

**Zauważ:** to jest "rozwiązanie" w retoryce post-hoc — agent sam wie że scope creep ale defends decyzję argumentem „filter post-hoc jest tańszy + reproducible niż upfront filter". **To CLAUDE.md Wzorzec 7 violated:** „NIE overstated motivation". Tutaj jest: built first, justify later.

**Killer kontekst per DEC-003 Scope IN/OUT:** Konspekt v3.2 § II.4.1 mówi „Ustawy konsumenckie z ISAP" — KPC i Prawo upadłościowe NIE są ustawami konsumenckimi. To **kodeksy proceduralne** które dotykają consumer cases tylko fragmentarycznie. Kojałowicz spojrzy na to i powie: „Pani, gdzie tu jest *prawa konsumenta* w ustawie *o postępowaniu cywilnym*?"

**Defense magiczne („historic reference dla orzeczeń SN/SA i decyzji UOKiK pre-2014") obraca się przeciwko Magdzie** — jeśli celem jest pozwolić probe rozpoznać citation do uchylonej ustawy w starszym orzeczeniu, to wymaga się ZNALEZIENIA i WSTAWIENIA tych orzeczeń do training set, a nie tylko ustaw. To recursive scope expansion.

---

### 🔴 RED FLAG #3 — 121 SN orzeczeń o frankowicach + 597 orzeczeń `orzeczenia.ms.gov.pl` = 4% korpusu, off-topic (SEVERITY: HIGH)

**Co:** Per `playwright_scrape_2026.md` § 1 i § 3, Magda + agent S2 pobrali:
- 121 orzeczeń Sądu Najwyższego (Izba Cywilna) — głównie **klauzule frankowe / abuzywność postanowień** (search phrases: „frankowicze", „klauzula niedozwolona", „abuzywność postanowień")
- 597 orzeczeń `orzeczenia.ms.gov.pl` — keywords: „konsument", „rękojmia", „umowa konsumencka", „klauzule niedozwolone", „kredyt konsumencki"

**Killer pytanie Kojałowicza:**
> *„Czy klauzule frankowe (kredyty hipoteczne CHF) wpadają w pani definicję 'prawa konsumenta' w hidden-states halu probe? Dlaczego 4% pani training data to specialistyczne orzecznictwo finansowe a nie pytania konsumenta o reklamację butów?"*

**Reasonable rebuttal:** „Klauzule abuzywne (art. 3851 KC) są centralne dla consumer protection." OK, częściowo. ALE 121 SN orzeczeń o specific kontrowersjach CHF to jest **expert legal corpus, nie consumer-facing**. Twoje use case to konsument kupuje laptop i nie wie czy ma 14 dni na zwrot. NIE: konsument wziął kredyt hipoteczny CHF w 2008 i procesuje się z bankiem o klauzule denominacji.

**Per `02_konspekt_v3.2_skeleton.md` § II.2.1 pkt 4 (Real-world relevance):**
> *„Każdy konsument w Polsce kontaktuje się z prawami konsumenta (zwroty, reklamacje, gwarancja)."*

Frankowicze ≠ codzienny konsument. To **niche specjalistyczny problem**.

**Per `consumer_documents_2026.md` (jeśli czytałaś, nie sprawdziłam) — czy probe NA orzecznictwie SN naprawdę pomoże na pytaniach z UOKiK Q&A „Kiedy mogę zwrócić buty?".** Dystrybucja domain shift jest realna i agencja agent sama by sygnalizowała.

---

### 🔴 RED FLAG #4 — DRAFTY R3/R4/R5 napisane PRZED Iter. 0b POC (SEVERITY: HIGH — violation CLAUDE.md Wzorzec 1 + 8)

**Co:** W `thesis_research/drafts/` istnieją drafty:
- `R3_dane.md` — 599 linii (~41 KB) napisane 2026-05-16 04:46
- `R4_eda.md` — 366 linii (~36 KB) napisane 2026-05-16 04:45
- `R5_architektura.md` — 350 linii (~37 KB) napisane 2026-05-16 04:48

ALE `thesis_research/CLAUDE.md` § Drafts mówi explicit:
> *„Status drafts (2026-05-16): **PUSTY** po pivot DEC-003. Stare drafty v3.1 zarchiwizowane w `_archive/v3-pharma-reranker/drafts/`. **Nowe drafty v3.2 będą tworzone w Iteracji 7** (writing phase) per build-first-finalize-last principle."*

**Sprzeczność interna w project state.** Albo drafty istnieją zaplanowane (CLAUDE.md trzeba zaktualizować) albo violation. R3 draft sam się odwołuje do „stanu po Iteracji 1a" — ALE PLAN_cele_i_kroki.md § 3 mówi że jesteśmy w Iter. 0b (Iter. 1 jeszcze nie zaczęta). **State mismatch między dokumentami**.

**Per CLAUDE.md Wzorzec 1 (Decision before output):** „Sign-off na scope/strategy zanim cokolwiek wygeneruję. Nie pisz kodu ani treści dopóki autorka nie potwierdzi kierunku."

**Per CLAUDE.md Wzorzec 8 (build-first):** „Pisanie ostatnie 20%, NIE pierwsze."

**3 drafty * 35 KB to 105 KB prozy która została wyprodukowana w nocy bez sign-offu na finalny dataset.** Pytanie: na podstawie czego liczby R3 są realne? Per draft R3 sekcja 3.1.3: "Akty prawne (chunks ELI) 2 123" — ale dataset v0.4 ma już 7,687 chunków `isap.sejm.gov.pl` (3.6× więcej). **Drafty już są stale.** Trzeba je rewrite albo zarchiwizować zanim Kojałowicz je zobaczy.

---

### 🔴 RED FLAG #5 — DEC-003 kill criteria NIE są monitorowane; v0.4 dataset land PRZED POC sanity checks (SEVERITY: HIGH)

**Co:** Per `DEC-003 § Kill criteria`, decyzja zostanie podważona jeśli np.:
- „**Polish NLI models nieadekwatne** — jeśli HerBERT-large NLI / sdadas-polish-nli daje <60% agreement na polish legal text"
- „**Hidden-states probe nie konwerguje** w Iter. 2"
- „Czas insufficient — jeśli scope okazuje się 12+ tygodni"

ALE per `PLAN_cele_i_kroki.md § 3 Iter. 0b`:
> *„Iter. 0b checkpoint go/no-go: jeśli mDeBERTa <50% accuracy → fallback HerBERT-large custom NLI fine-tune"*
> *„Iter. 0b POC critical test: polish diakrytyki w FSM/regex Outlines (ą/ę/ł/ó/ś/ż/ź) — If fail → drop generation-time citation"*

**Te 4 testy POC NIE zostały zrobione.** ZAMIAST tego, agent + Magda zbudowali korpus 17,862 chunks. Sentence: **Buduje się dataset na probę pivotu, ale pivot nie został zweryfikowany feasibility-wise.**

**Killer pytanie Kojałowicza:**
> *„Pani autorka, czy pani sprawdziła czy hidden-states extraction Bielik 11B w ogóle działa na pani lab GPU przed scraping 1.5 GB danych? Pani DEC-003 ma 6 kill criteria. Które z nich pani zweryfikowała?"*

**Honest answer:** zero. Wszystkie 4 POC testy (Outlines+diakrytyki, hooks layer 47, mDeBERTa NLI, lab GPU) są w PLAN_cele_i_kroki.md § 3 jako pending — agent_in_flight, NIE done.

**Konsekwencja:** jeśli probe AUROC <0.65 (kill criterion #3), te 1.5 GB danych są wyrzucone — Magda traci dni scrape pracy + agent kompute, a thesis musi pivotować PO RAZ CZWARTY. Konspekt v3.2 § II.4 i DEC-003 § Pierwszy pivot fail mode → spadnij na semantic entropy lub LLM-judge. Wszystko od nowa.

---

## 3. Dziesięć killer questions Kojałowicza + suggested rebuttals

### Q1: „Dlaczego potrzebowała Pani Konstytucji RP w korpusie do hallucination detection?"

**Suggested rebuttal:** Per `extra_ustawy_konsumenckie_2026.md` § Defense scaffolding #2: art. 76 to konstytucyjna podstawa ochrony konsumenta — *„Władze publiczne chronią konsumentów..."*. Single chunk, manual extraction, nie wprowadza noise.

**Honest assessment:** Defendable, ale **wątłe** — Konstytucja w korpusie NLP halu detection brzmi jak overscope. Lepiej: drop, cite w R3 jako „filozoficzny background, nie część dataset".

---

### Q2: „Co dokładnie 121 SN orzeczeń o CHF kredytach robi w benchmark dla consumer rights halu probe?"

**Suggested rebuttal:** Klauzule abuzywne (art. 3851 KC) są centralne dla consumer protection. SN orzecznictwo daje deterministic citation patterns dla retrieval evaluation.

**Honest assessment:** **NIE OBRONIMY w pełni**. CHF frankowicze to specjalistyczny financial dispute, nie general consumer rights. Sugerowane: drop wszystkich orzeczeń specifically mentioning „frank szwajcarski / CHF / denominacja" — zostaw tylko orzeczenia o reklamacjach, gwarancji, e-commerce. Trim z 121 do może 20-30.

---

### Q3: „Pani autorka, czy Pani potrafi obronić wybór bezprawnik.pl jako źródła wiedzy konsumenckiej?"

**Suggested rebuttal:** Bezprawnik.pl jest popular legal portal czytany przez konsumentów, fair-use Art. 29 PrAut. 200 articles w consumer-relevant tagach.

**Honest assessment:** **Mid-defendable**. Bezprawnik.pl jest opinion site, nie official source — fakty cytowane tam mogą być błędnie interpretowane przez non-lawyer redaktorów. **Risk:** training probe na halucynacjach z bezprawnik artykułów które same zawierają błędy interpretacji prawnej = garbage in, garbage out. Lepiej: użyj jako EVAL questions („consumer phrasing"), NIE jako KNOWLEDGE source.

---

### Q4: „Dlaczego 60% korpusu Rzecznika Finansowego to ubezpieczenia, NIE consumer rights?"

**Suggested rebuttal:** RF FAQ jest oznaczone w category `FINANCE_ADJACENT` per DATASET_CARD § Biases pkt 2. Świadomy bias, dokumentowany.

**Honest assessment:** **Defensive ale słabe**. „Mam świadomy bias" jest słabsze niż „nie mam tego biasu bo dropped". 2,472 chunks z rf.gov.pl to 13.8% korpusu. Plus 22% E1 extended jest RF FAQ. Pytanie: czy probe trained na ubezpieczeniowych Q&A generalizuje na pytania o zwrot butów? **Domain shift risk realny.** Defense: trim RF do tylko consumer credit/banking part, drop pure insurance.

---

### Q5: „Pani 240 synthetic halu pairs przy 17,862 chunks. To 1.3%. Jak Pani planuje train probe na takim ratio?"

**Suggested rebuttal:** Synthetic pairs są dla TRAINING probe, chunks są EVIDENCE corpus dla retrieval w pipeline. Two different roles.

**Honest assessment:** **Częściowo defendable, ale powierzchowne.** Konspekt v3.2 § II.4.1 mówi target *~5-10k synthetic halu pairs*. Mamy 240. To **2.4% celu** zrealizowane. Plus halu_type distribution: 115 factual_fabrication, 55 entity_confusion, 10 temporal_drift, **0 negation_flip, 0 paragraph_mis_citation**. Z 5 typów halu z konspektu, mamy tylko 3 z bardzo nierówną dystrybucją. **To podważa RQ1/H1.** Generator script `programatic_template_injection_v1` musi być rozbudowany ZANIM probe training startuje.

---

### Q6: „Dlaczego Pani zaczyna z 5,150 records (Iter. 1a target) ale Pani v0.4 ma 17,862? Czy Pani follows pani plan?"

**Suggested rebuttal:** Magda override 2026-05-16 — „wszystko ma być zdobyte" (per `new_sources_scrape_2026.md` § Status). Defense for max coverage przed analysis.

**Honest assessment:** **TO JEST WORST RED FLAG dla Kojałowicza** — pokazuje że plan nie jest follow'owany. „Wszystko ma być zdobyte" to NIE methodology, to FOMO. Per CLAUDE.md Wzorzec 4: „Honest critical feedback, NIE validation. Kontestowanie scope creep **wymagane**." — agent (ja) **nie zakontestował**, tylko wykonał. Reasonable disagreement powinno tu zadziałać. Defense: „Nadmiarowy scrape jest standardowy w data engineering, filter post-hoc cheaper than re-scrape." Ale to dobre dla *production engineering*, NIE dla *thesis research methodology*.

---

### Q7: „Co Pani odpowie na Wallat ICTIR 2025 critique że 57% citations w real RAG systems są post-rationalized, czyli inflated faithfulness scores?"

**Suggested rebuttal:** Konspekt § II.3 RQ2 explicit przyjmuje TWO-METRIC framework Wallat 2025: faithfulness ≠ correctness, osobne progi 85% i 75%.

**Honest assessment:** **STRONG defendable** — to jedna z mocniejszych części scope v3.2. Per `02_konspekt_v3.2_skeleton.md` § II.3 RQ2/H2, faithfulness vs correctness są mierzone osobno. Ale: czy 100 par gold standard wystarczy do oszacowania correctness z bootstrap CI? Sample size pewnie jest minimum.

---

### Q8: „Pani Mu-SHROOM 2025 pominął polski. OK. Ale AggTruth (ICCS 2025) Wrocław Tech wypuścili polish-adjacent halu probe pracując nad CLARIN-PL grantem. Dlaczego Pani nie konkuruje z nimi a oni mogą Pani zaorać w 6 miesięcy?"

**Suggested rebuttal:** Per `decisions/DEC-003 § Konsekwencje` — defensive lock-in actions: HF dataset release w Iter. 6 (early), arXiv preprint 2 tyg. przed obroną, R2 sekcja explicit polish landscape audit.

**Honest assessment:** **OK defensible** ale wymagac „early publish" execution. **AggTruth jest dokumentowane w DEC-003 jako MEDIUM risk.** Sytuacja realistyczna: jeśli Magda nie publikuje przed Wrocław, traci first-mover. Mitigation per DEC-003 dotyczy 4 narrowing axes (polish + citation-grounded + consumer rights + hidden-states probe). To zwęża niche.

---

### Q9: „Pani 24 source directories. Brief miał ELI + UOKiK + Reddit + fora + manual gold (5 sources). Skąd 19 dodatkowych?"

**Suggested rebuttal:** Per `new_sources_scrape_2026.md`, 15 sources scrape (12 successful, 3 blocked WAF). Per `extra_ustawy_konsumenckie_2026.md`, 8 extra ustaw. Per `playwright_scrape_2026.md`, 3 sources via Playwright bypass.

**Honest assessment:** **HARD do obrony**. „Maximum coverage" nie jest methodology. Każde nowe źródło wymaga: license check, license attribution, biased sample acknowledgment, post-hoc relevance filter. Im więcej źródeł, tym więcej **defense surface** w R3. **Per Magda's CLAUDE.md anti-pattern „Nie wzbudzaj scope creep" — to MASYWNY violation.** Każde dodatkowe źródło jest dodatkowe killer question dla Kojałowicza.

---

### Q10: „Pani wymyśliła Polish CitationBench jako publishable benchmark na HuggingFace. ALE Pani DATASET_CARD ma `legal_court_judgment` (597), `legal_uokik_decision` (26), `legal_tsue_judgment` (29), `qa_raw` (2945), `encyclopedic` (2414) i 4 INNE category. Jaką dokładną task tutaj ewaluujemy?"

**Suggested rebuttal:** Multi-task benchmark — citation grounding (per chunk), halu detection (per pair), retrieval (per query).

**Honest assessment:** **CIĘŻKO do obrony jako single coherent benchmark.** HuggingFace datasets typu HaluBench / RAGTruth / Mu-SHROOM mają jasny single-task focus. Mixed dataset z 9 source_types może być traktowane przez community jako „messy data dump bez clean evaluation protocol". Defense: split dataset na sub-datasets per task (CitationBench-Statutes, CitationBench-CourtJudgments, CitationBench-QAOnly) — ALE wymaga refactor v0.5+ i pomyślne uzasadnienie 9 source types. **Strong recommendation: REDUCE source_types do 3-4 max przed publish.**

---

## 4. Scope creep audit — co dropować + uzasadnienie

| Komponent | Akcja | Uzasadnienie |
|---|---|---|
| **KPC chunks 2,084** | DROP wszystkie poza ~50 chunkami consumer-specific (post. uproszczone art. 505¹-505¹⁴ + post. grupowe art. 187¹) | 96% KPC NIE dotyczy consumer rights. Filter już zaplanowany per agent — wykonaj NOW, nie post-hoc. |
| **Prawo upadłościowe 1,252** | DROP **całość** | Upadłość konsumencka jest separate domain — możliwa jako future work pkt R8, NIE central. |
| **3 UCHYLONE ustawy 317 chunks** (DU/2003/2275, DU/2002/1176, DU/2000/271) | DROP | Defense „historic reference dla starszych orzeczeń" jest słaba. Probe nie powinien być trenowany na nieobowiązujących ustawach — wprowadza ambiguity. Cite-only w R3 jako legacy context. |
| **Konstytucja art. 76 (1 chunk)** | KEEP single chunk | OK koszt-marginalny, dobry citation w R1 § motywacja. |
| **SN orzeczenia frankowe (~80 z 121)** | DROP CHF-specific, keep ~40 ogólne consumer | Domain shift risk; CHF jest specjalistyczny financial dispute. |
| **orzeczenia.ms.gov.pl 597** | TRIM do ~200 explicit consumer-tagged | „kredyt konsumencki" keyword jest OK, ale „rękojmia" zwraca dużo B2B cases. Stratified filter. |
| **bankier.pl 299, money.pl 31, gazeta_prawna 59, infor.pl 398, prawo.pl 248** | TRIM do max 100 articles per source albo DROP całość | Generic finance/legal journalism, off-topic dla consumer rights. Wybrane evidence: za 5% korpusu (1,035 chunks razem) wprowadzasz duży noise budget bez probe value. |
| **bezprawnik.pl 200** | DROP albo TRIM do 50 | Opinion site, niewysoka quality. Lepiej dla EVAL questions niż KNOWLEDGE source. |
| **rf.gov.pl 2,472** | TRIM do ~500 consumer credit/banking only | 60% to ubezpieczenia. Drop insurance-specific. |
| **eporady24.pl 302, e-prawnik 948, forumprawne 1,186** | KEEP (real consumer questions) | Te są good — autentyczne pytania konsumentów. Per Magda's plan. |
| **Reddit r/Polska 509** | KEEP | Real consumer voices, plan-aligned. |
| **konsument.gov.pl 393, ECC Polska (cik.uke.gov.pl 128)** | KEEP | Official consumer protection, plan-aligned. |
| **UOKiK Q&A 60, UOKiK news 111, decyzje UOKiK 26, prawakonsumenta.uokik.gov.pl 60** | KEEP wszystko | Gold standard, plan-aligned. |
| **UODO 198, KNF 91, URE 15, UKE 128** | TRIM do consumer-tagged ~50 razem | UODO RODO ≠ general consumer rights — domain ambiguity. KNF/URE/UKE są regulatory bodies, less consumer-facing. |
| **TSUE 29 + UE Dyrektywy 8** | KEEP | Foundation dla harmonization Polish/EU. |
| **Wikipedia 34** | KEEP | OK encyclopedic background. |
| **ING regulaminy 22** | DROP | Single-bank sample bez generalizability. |
| **synthetic halu_pairs 240** | **PRIORITY: EXPAND do target 5,000-10,000** | Najważniejsze ze wszystkiego. Plus dodaj brakujące typy: negation_flip + paragraph_mis_citation = 0 obecnie. |

**Post-cleanup target:** ~8,000-10,000 chunks (vs obecne 17,862) z czego ~5,000 to clean consumer-core, ~3,000 to consumer questions, ~2,000 to legal background. Plus 5-10k synthetic halu_pairs (CORE artefakt).

**Time cost:** 1-2h agent work + Magda decision per source. Saves ~30+ defensive scoping pytań Kojałowicza.

---

## 5. Time budget — czy POC start realistyczny

**Iter. 0b w PLAN_cele_i_kroki.md ma 4 POC tests pending:**

| POC test | Magda lub agent | Status | Estimated time |
|---|---|---|---|
| Outlines + Bielik 1.5B z 10 queries (polish diakrytyki) | Agent → Magda review | ⏳ pending | ~2h agent + 1h Magda |
| mDeBERTa NLI sanity check 50 par | Agent → Magda review | ⏳ pending | ~1h agent + 1h Magda |
| PyTorch hooks Bielik 11B layer 47 (extraction works?) | Magda manual | ⏳ pending | ~3-5h Magda |
| Lab GPU verification (H100 FP8 11GB lub A100 22GB) | Magda | ⏳ pending | ~2h Magda (zależne od dostępu) |

**Plus Magda owes:**
- D1, D3 decisions (probe target size, halu typy)
- 5 halu typy definicje operacyjne (`EXPLAINER § 4` jest, ale agent może rozbudować)
- Manual weryfikacja sample 10 chunks ELI

**Total Iter. 0b realistic:** **8-12 hours Magda + ~5h agent** zanim go/no-go.

**Problem:** Magda spędziła te ostatnie 12-15h NA SCRAPE rather than POC tests. **POC tests są więcej krytyczne** — bez nich nie wiemy czy probe w ogóle będzie działać. 1.5 GB dataset jest worthless jeśli POC #3 (hooks layer 47) zwraca crash.

**Per CLAUDE.md Wzorzec 8 (build-first):** *„Najpierw BUILD"* — ale BUILD znaczy też BUILD POC, nie tylko BUILD dataset. Magda traci czas na łatwe zadania (scrape) zamiast na trudne (probe extraction). To **classic procrastination through productivity**.

**Recommendation:** PAUZA scrape NOW. Dokończ 4 POC tests. Sign-off Iter. 0b checkpoint. Potem decyzja czy/co dalej z dataset.

---

## 6. Recommendation: **POSPRZĄTAĆ scope przed POC**

### Krytyczna decyzja w 3 wariantach

#### Wariant A: TRZYMAĆ kurs (NOT RECOMMENDED)
Kontynuować scrape (3 dodatkowe sources jeszcze możliwe per `platforms_blocked.json`), zaczynać POC tests w trakcie. **Risk:** 30+ defense surface pytań Kojałowicza, 4 POC tests opóźniają start probe training do >2 tyg, dataset 17,862 niemożliwy do obrony jako single coherent benchmark.

#### Wariant B: POSPRZĄTAĆ scope (RECOMMENDED) ⭐
Action sequence (in this order):
1. **STOP scrape** (już done w principle — wszystkie planowane sources zaadresowane)
2. **Run 4 POC tests** (Magda 8-12h burst) — kluczowe go/no-go signal
3. **PARALLEL: agent runs `filter_consumer_core` script** — drop ~50% chunks per recommendation w sekcji 4. Output: dataset v0.5 z ~8-10k clean chunks.
4. **Rewrite synthetic halu generator** — dodaj negation_flip + paragraph_mis_citation. Cel: 5-10k synthetic pairs (vs obecne 240).
5. **Sign-off check** — Magda przeglądnij v0.5, Iter. 0b POC results, zatwierdzanie scope dla Iter. 1.
6. **DROP R3/R4/R5 drafty** (1315 linii) — albo zarchiwizować, albo flag jako stale until Iter. 1+ data ready. Per CLAUDE.md Wzorzec 8: pisać w Iter. 7.

**Time cost:** ~3-5 days (mostly agent + Magda POC). **Saves:** 2 tygodnie defensive engineering pre-defense + radical dataset cleanup pre-publish.

#### Wariant C: DRASTIC CUT
Drop wszystko poza UPK + KC art. 535-581 + UOKiK Q&A 60 + manual gold 100. Total: ~500 chunks + ~5-10k synthetic halu. **Minimum viable benchmark.** Lepsze dla focus, ale traci „comprehensive" framing.

**My recommendation: Wariant B.** Daje strong defense („zrobiłam świadomy scope cleanup based on per-source relevance audit" jest stronger than „dropped wszystko bo zbyt szerokie") plus zachowuje wartość już wykonanej scrape pracy.

---

## 7. Co JĄ ratuje (3-5 pozytywów, żeby Magda nie wpadła w panikę)

Mimo brutalnego krytyku, są **realne mocne strony obecnej pracy:**

1. **DEC-003 audit trail jest mocne.** 198-linijkowy ADR z explicit kontekstem, options, uzasadnieniem, kill criteria, consequences. To **najlepszy defense move** dla pivotu — Magda może to pokazać Kojałowiczowi i odpowiedzieć każdą wątpliwość per dokument. Pivot per se obronisz.

2. **UOKiK Q&A 60 par to legitimate goldmine.** 92% z citations, 52 unique legal refs, 5 kategorii. Per `02_konspekt_v3.2_skeleton.md` § II.4 — to **ZERO manual annotation cost** dla połowy gold standard. Massive time-saver.

3. **Stack technologiczny jest stable + reusable.** 70% z v3.1 zostaje (Bielik, BGE-M3, Qdrant, Prefect, MLflow, Langfuse, Evidently — wszystko production-grade open-source per CLAUDE.md). DEC-003 § Uzasadnienie pkt 3 evidence-backed.

4. **Methodology research jest naprawdę głęboka.** 17 plików w `thesis_research/research/` (~50,000 LOC), `halu_detection_sota_2024_2026.md` ma 379 linii z 22+ papierami chronologicznie + critique sections. **Literature review już praktycznie gotowy** dla R2 — należy tylko zrebuildować footnotes IEEE format w Iter. 7. To 3-tygodniowe oszczędności.

5. **Polish-first first-mover framing jest UCZCIWY.** Per `halu_detection_sota_2024_2026.md` § 5.2 Konkretne luki — Mu-SHROOM 2025 polski pominięty (verified fact), PolEval 2025 nie ma halu task (verified fact). DEC-003 § Uzasadnienie pkt 2 cytuje konkretne źródła. **Nie jest overstated** zgodnie z CLAUDE.md Wzorzec 7. AggTruth Wrocław Tech jest acknowledged jako MEDIUM risk z explicit mitigation (defensive lock-in 3 actions). To **strong defense posture**.

**Wniosek:** scope creep w 1 dzień jest fixable. Audit trail + UOKiK gold + stack stability + research depth + honest framing = **fundament jest solid**. Trzeba tylko zaprzestać scraping i wrócić do POC + scope cleanup. **Magdo, NIE panikuj — to nie jest beznadziejne, to po prostu wymaga 3-5 dni dyscypliny.**

---

## Appendix: Anti-pattern audit per CLAUDE.md (quick check)

| Anti-pattern | Violation? | Evidence |
|---|---|---|
| Nie pisz rozdziałów bez outline + sign-off | ✗ **VIOLATED** | R3 (599L) + R4 (366L) + R5 (350L) drafty napisane przed Iter. 0b checkpoint |
| Nie generuj cytowań z głowy | ✓ OK | Research files mają linki, niepewność oznaczona 🟡 |
| Nie wzbudzaj scope creep | ✗ **VIOLATED MASYWNIE** | 17,862 chunks vs 5,150 plan, 24 source dirs vs 5 plan |
| Nie wracaj do reranker fine-tuning | ✓ OK | Reranker passé per DEC-003 |
| Nie wracaj do farma ani ChPL+Ulotka | ✓ OK | Archived, nie używane |
| Nie używaj sformułowań starzejących się | ⚠ MINOR | „rosnącej selektywności" w R3 (1 instance — OK kontekst) |
| Nie commituj automatycznie | ✓ OK | Per git log Magda kontroluje commity (manual) |
| Nie używaj pip/poetry/conda | ✓ OK | uv używane wszędzie |
| Nie pisz codemix English-Polish w drafcie pracy | ⚠ FLAG | R3 draft używa angielskich terminów (np. „chunks", „source selection methodology", „cross-modal retrieval") — to OK dla CLAUDE.md ale potrzeba review w Iter. 7 polish. **Drafty są w pre-Iter.7 stanie, więc OK na razie.** |

**Verdict:** 2 major violations (scope creep + drafty bez sign-off), 2 minor flags. **Drafty są największym one-time fixable problem** — albo archive, albo flag jako WIP-do-rewrite-post-Iter.1.

---

**Koniec audytu. Polskie podsumowanie:** pivot DEC-003 jest defensible, scope wokół niego — NIE. Pospolitań przed POC tests + Iter. 1. Im później to zrobimy, tym więcej defense surface dla Kojałowicza.

*Plik wygenerowany 2026-05-16 jako devil's advocate brutally honest review per /validate skill protocol.*
