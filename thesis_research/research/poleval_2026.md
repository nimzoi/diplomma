# PolEval 2026 + polish halu landscape research — 2026-05-16

Research na potrzeby pracy inżynierskiej Magdaleny Sochackiej (PJATK Data Science). Cel: zweryfikować czy PolEval 2026 planuje task halucynacji/faithfulness/citation grounding w polskim, oraz ocenić ryzyko że ktoś nas wyprzedzi z first-mover claim "Polish RAG halu detection w farmakologii klinicznej".

---

## 0. Verdict

- **PolEval 2026 status:** **NOT YET ANNOUNCED** (stan na 2026-05-16). PolEval 2025 (8. edycja) zakończony 21.11.2025, proceedings opublikowane w ACL Anthology 20.02.2026. Brak komunikatów o edycji 2026 na poleval.pl, brak Call for Tasks. **Pattern historyczny:** Call for Tasks PolEval 2025 ukazał się 10.03.2025, task names 14.04.2025 — więc jeśli PolEval 2026 ma być, anons spodziewany w czerwcu/lipcu 2026.
- **Halu task w PolEval 2026:** **TBD** — nie ma jak zweryfikować, ale **historyczna ekstrapolacja: niskie prawdopodobieństwo halu task** (zero halu tasks w 8 edycjach 2017-2025; PolEval 2025 wybrał generation detection, gender bias, layout, speech emotion — nie halu).
- **First-mover risk dla naszej tezy:** **MEDIUM** (nie LOW, ale też nie HIGH).
  - Brak istniejącego polskiego halu benchmarku ani polskiego RAGTruth — to faktyczna luka.
  - **ALE** Wrocław Tech (Kazienko, Kocoń, Ferdinan) ma active CLARIN-PL grant 2024-2026 na halu detection (AggTruth, ICCS 2025) — ich AggTruth metoda jest **English-only datasety** (NQ, HotPotQA, CNN/DM, XSum), więc nie blokują naszego polish-specific corpus angle, ale są naturalnym kandydatem do polish halu work w 2026-2027.
- **Recommendation:** **Defensywne first-mover lock-in** — opublikować Polish farmakologia halu eval set (200 par psych + cross-register pairs) jako HuggingFace dataset z metadata wcześniej niż obrona (sierpień-wrzesień 2026), spec preprint na arXiv (cs.CL + cs.IR tags) min. 2 tygodnie przed obroną; jednoczesnie **NIE marketingować jako "first Polish halu benchmark"** (ryzyko że ktoś zaserwuje counter-example) tylko jako "first Polish ChPL↔Ulotka cross-register retrieval benchmark with paired halu eval". Cross-register angle (RQ5/DEC-002) jest twoja realna ucieczka od konkurencji.

---

## 1. PolEval 2026 official status

**Źródło prawdy:** http://poleval.pl/ (sprawdzone 2026-05-16) — strona pokazuje wyłącznie PolEval 2025.

| Element | Stan |
|---|---|
| Edycja 2026 announced? | **NIE** — brak na poleval.pl |
| Call for Tasks 2026 | **NIE** |
| Tasks 2026 | brak |
| Workshop dates 2026 | brak |
| Deadlines 2026 | brak |
| Ostatnia activity | PolEval 2025 proceedings published ACL Anthology 20.02.2026 |

**Historyczny pattern PolEval 2025 (referencyjny):**
- Call for Tasks: 10.03.2025
- Task names announced: 14.04.2025
- Test data release: lipiec 2025
- Submission deadline: wrzesień 2025
- Workshop + results: 21.11.2025
- Proceedings: 20.02.2026

**Wnioski:** Jeśli PolEval 2026 będzie, oczekuj Call for Tasks **marzec-kwiecień 2026** (brak — sprawdzone) lub odsunięcie cyklu. **Możliwe że organizatorzy skupiają się na rozkręcaniu PolEval po reorg** (PolEval do 2025 = 8 edycji — utrzymali roczny cykl). **Ryzyko luki w 2026** istnieje — brak indeksowanej aktywności w 2026.

**Adjacent shared task:** POLAR @ SemEval-2026 (https://polar-semeval.github.io/) — DESPITE the name, **nie jest "polish"** tylko polarization detection (22 języków w tym polski jako jeden z wielu). Workshop summer 2026. **Nie konfliktuje z naszą tezą.**

## 2. PolEval historical halu coverage

| Year | Edycja | Tasks | Halu/faithfulness/RAG coverage | Notes |
|---|---|---|---|---|
| 2017 | 1 | LM + POS tagging | NIE | klasyczne NLP |
| 2018 | 2 | NER + LM + sentiment | NIE | |
| 2019 | 3 | Translation + cybersec NER | NIE | |
| 2020 | 4 | Punctuation + abstracts + entail | NIE | |
| 2021 | 5 | Punctuation restoration, QE, OCR, QA | NIE | Task QA = klasyczne QA, nie halu |
| 2022/23 | 6 | Abbrev disambig, passage retrieval | **CZĘŚCIOWO** | Task 3 passage retrieval (NDCG@10) — pure IR, NIE halu/faithfulness/RAG-end-to-end |
| 2024 | 7 | Reading comp + emotion/sentiment + ASR | NIE | |
| 2025 | 8 | ŚMIGIEL (MGT detection) + Gender-inclusive + Layout + Speech emotion | NIE | brak halu/RAG |

**Verdict:** **Zero halu tasks w 8 edycjach** (2017-2025). Najbliżej był 2022/23 Task 3 passage retrieval (autorzy: zespół passage-retrieval-secret na github.com/poleval) — był to **pure IR task (NDCG@10 na trivia/legal/e-commerce)**, NIE end-to-end RAG ani faithfulness. **PolEval nigdy nie miał halu/faithfulness/citation grounding tasku.**

## 3. Polish benchmarks landscape 2024-2026

| Benchmark | Year | Owner | Scope | Halu coverage | Threat dla RQ5? |
|---|---|---|---|---|---|
| **KLEJ** | 2020 | Allegro/Rybak | 9 tasks (NER, QA, NLI, sentiment) | NIE | NIE |
| **LEPISZCZE** | NeurIPS 2022 | CLARIN-PL | 13 task-dataset pairs, leaderboard | NIE | NIE — czysty NLU |
| **PIRB** | LREC 2024 | OPI (Dadas et al.) | 41 IR tasks Polish (medicine, law, business) | NIE | **CZĘŚCIOWO** — same medical/legal corpus overlap; ale nie ma halu/faithfulness layer ani ChPL↔Ulotka pairing |
| **PolQA** | LREC 2024 | IPI PAN (Rybak, Przybyła, Ogrodniczuk) | 7k OpenQA, 7M passages | NIE | NIE — pure QA |
| **PoQuAD** | 2023 | Tuora et al. | 70k Polish SQuAD-style | NIE | NIE |
| **PLLuMIC** | 2025 | PELCRA | Polish instructions, fine-tuning | częściowo (preference data) | NIE — nie halu eval |
| **PLLuM-Align** | EMNLP 2025 | PLLuM consortium | Preference dataset, alignment | częściowo (safety/bias) | NIE — nie RAG faithfulness |
| Polish ling/cult competency | 2025 | (multiple) | 600 manual Q, 6 kategorii (history, geo, grammar) | częściowo (factuality?) | NIE — pure factual QA |
| **Hot-2026 farmakologia (nasz)** | planned 2026 | Sochacka (PJATK) | ChPL+Ulotka+AOTMiT+NFZ+OA, ~4100 docs | **TAK — RQ5 cross-register + halu via reranker quality** | n/a |

**Wnioski:** **Brak polskiego halu/faithfulness benchmarku.** PIRB jest closest neighbour ale czyste IR. PLLuM-Align dotyka faithfulness przez preference data ale to fine-tuning data, nie eval benchmark.

## 4. International halu benchmarks z polish

| Benchmark | Year | Languages | Polish? | Notes |
|---|---|---|---|---|
| **HaluEval** | 2023 | English-only | NIE | task-specific QA/dialogue/summ |
| **FELM** | NeurIPS 2023 | English-only | NIE | factuality, 5 domain, 847 Q |
| **RAGTruth** | ACL 2024 | English-only | NIE | 18k responses, RAG halu corpus |
| **Mu-SHROOM** | SemEval-2025 Task 3 | 14 lang | **NIE** | AR, BS, CA, ZH, CS, EN, FA, FI, FR, DE, HI, IT, ES, SV — **brak PL** (confirmed Helsinki-NLP/mu-shroom) |
| **HalluLens** | ACL 2025 (Meta) | English-only | NIE | dynamic Wikipedia queries |
| **HHEM / Vectara leaderboard** | 2024-2026 | English-only | NIE | summarization halu rate |
| **MultiHal** | arXiv 2505.14101 (2026) | DE, IT, FR, PT, ES + EN | **NIE** | Knowledge graph grounded, 5 EU lang — brak PL |
| **Multilingual TruthfulQA (HiTZ)** | 2502.09387 (2025) | EU, CA, GL, ES, EN | **NIE** | Iberian languages focus |
| **MultiWikiQHalluA** | RESOURCEFUL 2026 | EN, DA, DE, IS evaluation; 30 EU lang classifiers | **częściowo** — synthetic dataset dla 306 jęz., trained on 30 EU lang (likely PL inclusion, ale primary eval EN/DA/DE/IS) | sprawdź dokładnie listę 30 EU lang |
| **HalluHard** | arXiv 2602.01031 (2026) | English-only | NIE | multi-turn medical/legal/research/code |
| **TruthfulQA-PL** | brak | n/a | **NIE ISTNIEJE** | brak professional translation |

**Wnioski:** **Polski jest systematycznie pomijany** w międzynarodowych halu benchmarkach — confirmed gap. MultiWikiQHalluA może mieć synthetic Polish data (warto zweryfikować — to closest competitor), ale to MT-based synthetic, nie native human-annotated, więc nie blokuje native Polish gold standard.

## 5. Active polish NLP research groups + halu activity

| Group | Recent halu work? | Public artifacts | Threat level dla first-mover |
|---|---|---|---|
| **Wrocław Tech AI Dept** (Kazienko, Kocoń, Ferdinan, Matys, Eliasz, Kiełczyński, Langner) | **TAK — VERY ACTIVE** | AggTruth (ICCS 2025, arXiv 2506.18628), Self-Learning LLM (EMNLP Findings 2024 "Into the Unknown"), Self-training LLM through Knowledge Detection (EMNLP Findings 2024), "Breaking the Illusion of Reasoning in Polish LLMs" (EACL 2026) | **HIGH** — CLARIN-PL grant 2024-2026 explicit halu detection focus. Mają infrastrukturę, ludzi, finansowanie. AggTruth English-only ale logical next step = Polish. **Główny potencjalny konkurent.** |
| **CLARIN-PL** (institutional) | **TAK** — finansuje Wroclaw Tech grant + LEPISZCZE | LEPISZCZE benchmark, NLP infrastructure | **MEDIUM-HIGH** — instytucja-parasol, ale konkretne halu publications via Wroclaw Tech |
| **IPI PAN** (Ogrodniczuk, Rybak, Przybyła) | NIE bezpośrednio halu | PolQA, PoQuAD, PLLuM (co-author), edycja PolEval 2025 proceedings | LOW dla halu, MEDIUM dla retrieval (PolQA conflicts dla RQ1 baseline) |
| **NASK** | częściowo (Responsible AI w PLLuM, hybrid output correction) | PLLuM consortium member, LLaVA-PLLuM | LOW — focus instytucjonalny, nie publishing halu benchmarków |
| **OPI** (Dadas, Perełkiewicz, Poświata) | NIE halu, ale silny w retrieval | PIRB, polish-reranker-roberta-v3 (NAS RDZEŃ!), MMLW embeddings | **MEDIUM** dla RQ1 (nasz reranker base), LOW dla halu |
| **PJATK** | brak publicznych halu publikacji | — | LOW |
| **AGH** | Cyfronet hosting Bielik, nie halu publishing | — | LOW |
| **MIM UW** | współpraca z PLLuM consortium | — | LOW |
| **AMU Poznań** | NLP general | — | LOW |
| **University of Łódź** | PLLuM consortium member | — | LOW |
| **IS PAN** (Slavic Studies) | PLLuM consortium, jezykoznawstwo | — | LOW |
| **Allegro NLP** | retrieval/embedding focus, nie halu | HerBERT, KLEJ | LOW dla halu |
| **SpeakLeash** (Bielik twórcy) | częściowo — "Tricky Questions" w Bielik MT-Bench (reasoning + halu avoidance) | Bielik 11B v3 (Apache 2.0) — NASZ generator | LOW dla halu benchmarków, MEDIUM dla modeli (mamy ich generator) |
| **PELCRA** | corpus linguistics | PLLuMIC instructions | LOW |

**Najgroźniejszy konkurent:** **Wrocław Tech (zespół Kazienko/Kocoń)** — mają explicit CLARIN-PL grant 2024-2026 na halu detection. Jeśli ktoś opublikuje "Polish halu benchmark" w 2026 to oni. Już mają infrastrukturę, autorów polish-speaking, dostęp do PLLuM (Wrocław Tech jest koordynatorem PLLuM consortium).

## 6. First-mover risk assessment

### Prawdopodobieństwo że ktoś już pracuje nad polish halu detection — **~35-45%**

**Argumenty FOR aktywnej konkurencji (push to HIGH):**
- Wrocław Tech grant CLARIN-PL 2024-2026 (FENG.02.04-IP.0040004/24) explicit halu detection focus
- PLLuM consortium ma "Responsible AI framework with hybrid output correction" — anti-halu na poziomie produktu
- AggTruth poszedł NIPS/ICCS ścieżką, naturalny next: rozszerzenie na polish + RAG context
- Globalny trend halu benchmarków 2025-2026 (HalluLens, MultiHal, MultiWikiQHalluA) — polish gap będzie kogoś świerzbiał
- ICLR 2026, NAACL 2026, EACL 2026 mają explicit calls dla multilingual hallucination

**Argumenty AGAINST (push to LOW):**
- Mimo 24-36 miesięcy CLARIN-PL grantu, Wroclaw Tech nadal NIE opublikował polish halu benchmarku (AggTruth English-only NQ/HotPotQA/CNN/XSum)
- Jeden grant ≠ jeden output; mogą się skupiać na method papers (AggTruth, Self-Learning) zamiast benchmark papers
- Brak announce'd polish halu benchmarku na HuggingFace, GitHub trending, conferences
- Polski jako "low-resource for halu" pomijany w MultiHal, Mu-SHROOM — niska priorytetyzacja globalna
- Nikt nie zrobił **Polish ChPL↔Ulotka cross-register** — to niche w nicheu

### Konkretni candidates (ranked by threat)

1. **Wroclaw Tech AI Dept (Kazienko/Kocoń/Ferdinan zespół)** — HIGH threat na ogólny "Polish halu benchmark", LOW threat na specific "Polish farmakologia ChPL↔Ulotka cross-register"
2. **OPI (Dadas et al.)** — MEDIUM threat na retrieval-side rerankers (mogą wypuścić "PIRB v2" z halu layer); LOW na farmacja-specific
3. **CLARIN-PL infrastructure team** — MEDIUM (mogą sponsorować halu benchmark z innym zespołem)
4. **Independent researchers / studenci PhD** — UNKNOWN; nieindeksowani, ale niska wykrywalność
5. **Bielik/SpeakLeash team** — LOW threat na benchmark, MEDIUM jeśli zrobią dedicated halu eval dla Bielik v4

### Mitigation strategies dla pracy

**Defensive (chronią first-mover):**
1. **Publish dataset early na HuggingFace** — release 200-par psych gold standard + ChPL↔Ulotka paired subset jako HuggingFace dataset z DOI (Zenodo) **2-3 miesiące przed obroną** (~lipiec-sierpień 2026). Dataset card explicit "released in support of MSc thesis Sochacka 2026".
2. **arXiv preprint spec** — min. 2 tygodnie przed obroną, cs.CL + cs.IR tags, krótki ~6-8 str. paper "Cross-register retrieval evaluation for Polish pharmaceutical RAG: a paired ChPL↔Ulotka benchmark". To timestamp twojej kontrybucji.
3. **GitHub repo public min. 1 miesiąc przed obroną** — kod ewaluacji, eval scripts, baselines (BM25, BGE-M3, polish-reranker-roberta-v3 baseline).
4. **Tag/cytuj AggTruth explicit** w R2 Literatura — pokażesz że znasz polish landscape, ale carve out niche (cross-register, paired, farmakologia). To prevention przed reviewer questioning "why didn't you compare with AggTruth?".

**Offensive (carve out niche):**
1. **Framing: NIE "first Polish halu benchmark"** (ryzyko że Wroclaw zaserwuje counter w 6 miesięcy) **TAK "first Polish ChPL↔Ulotka cross-register retrieval benchmark"** — niche tak wąska że nie do podważenia.
2. **RQ5 jako defensive moat** — DEC-002 ChPL↔Ulotka pairing to twój unique angle (Grabowski 2017 EN-PL nie intra-PL cross-register). Nawet jeśli Wroclaw zrobi Polish halu benchmark generic, twój cross-register zostanie unique sub-contribution.
3. **Farmakologia kliniczna z psych eval subset** — wąska domena chroni przed "ogólnym" konkurentem.
4. **Negative-result framing** (per CLAUDE.md "Defense scaffolding") — nawet jeśli H1 odpada, RQ5 + H4 drift + H2 kappa stoją niezależnie.

### Verdict ostateczny

**First-mover risk MEDIUM, nie HIGH.** Wrocław Tech jest faktyczne zagrożenie ALE nie na twój specific angle (cross-register farmakologia). Wykonalne mitigation: timely HF dataset + arXiv preprint + GitHub repo.

## 7. Recommendations dla pracy

**Action items (ranked by priority, all in next 4-12 months):**

1. **[HIGH PRIO, do iteracji 0 lub 1]** Dodaj do R2 Literatura sekcję **2.X "Polish halu and faithfulness landscape"** cytującą: AggTruth (Matys et al. 2025, ICCS), PLLuM Responsible AI framework, PIRB, oraz explicit przyznanie braku polish halu benchmarku. **Prevents reviewer ambush.**
2. **[HIGH PRIO, do iteracji 0]** Wzbogać RQ5 sekcję w R1 Wprowadzenie o **dwa zdania "Why this is novel"**: (a) brak polish ChPL↔Ulotka aligned corpus, (b) MultiHal/Mu-SHROOM/HalluLens systematicznie pomijają polski. Cytuj URLs verified w tym raporcie.
3. **[MEDIUM PRIO, w iteracji 2-3]** Plan HuggingFace dataset release: eval set 200 par psych + ChPL↔Ulotka subset jako `magdalena-sochacka/polish-pharma-cross-register-eval-2026` z DOI Zenodo. Target release **lipiec-sierpień 2026**.
4. **[MEDIUM PRIO, do iteracji 3-4]** Plan arXiv preprint spec: ~6-8 stron, cs.CL + cs.IR, target submission **2 tygodnie przed obroną**. Tytuł roboczy: "Cross-register retrieval for Polish pharmaceutical RAG: a paired ChPL↔Ulotka evaluation benchmark and reranker fine-tuning case study". Może być sub-paper z thesis.
5. **[LOW PRIO, monitoring]** Setup Google Alert: "PolEval 2026", "AggTruth Polish", "Polish hallucination benchmark", "Polish RAG faithfulness". **Quarterly check** (sierpień 2026, listopad 2026, luty 2027) — sprawdź czy ktoś nie wypuszcza competing benchmark.
6. **[LOW PRIO, opportunistic]** Jeśli PolEval 2026 zostanie ogłoszony z halu taskiem — **zgłoś się jako participant z polish-pharma-eval data**. Twoja praca staje się reference submission. Jeśli halu tasku NIE będzie — zaproponuj na PolEval 2027 jako organizer.
7. **[VERIFY, jednorazowe]** Sprawdź MultiWikiQHalluA dokładną listę 30 EU lang classifiers (arXiv 2605.02504, RESOURCEFUL 2026) — jeśli polish jest w 30, to closest competitor jako "automated polish halu data exists". Wpływ na framing R2.
8. **[VERIFY, jednorazowe]** Sprawdź czy AggTruth ma planowaną v2 z polish datasets — kontakt z autorami via ResearchGate / DBLP (Piotr Matys, Jan Eliasz). Jeśli planowane Q3-Q4 2026 → przyspiesz twoje publication timeline.

---

**Source URLs (verified 2026-05-16):**

- [PolEval 2025 Home](http://poleval.pl/)
- [PolEval 2024 Home](https://2024.poleval.pl/)
- [PolEval GitHub org](https://github.com/poleval) (lista task repos)
- [PolEval 2025 ACL Anthology](https://aclanthology.org/2025.poleval-main.0/)
- [POLAR @ SemEval-2026](https://polar-semeval.github.io/) (NIE polish-specific, polarization)
- [AggTruth arXiv 2506.18628](https://arxiv.org/abs/2506.18628) (Wroclaw Tech, English-only datasets, CLARIN-PL grant)
- [PLLuM arXiv 2511.03823](https://arxiv.org/abs/2511.03823)
- [PIRB arXiv 2402.13350](https://arxiv.org/abs/2402.13350) (Dadas et al., OPI)
- [PolQA arXiv 2212.08897](https://arxiv.org/abs/2212.08897) (Rybak et al., IPI PAN)
- [Mu-SHROOM SemEval-2025 arXiv 2504.11975](https://arxiv.org/abs/2504.11975) (14 lang, brak PL)
- [MultiHal arXiv 2505.14101](https://arxiv.org/abs/2505.14101) (5 EU lang, brak PL)
- [Multilingual TruthfulQA HiTZ arXiv 2502.09387](https://arxiv.org/abs/2502.09387) (Iberian + EN, brak PL)
- [MultiWikiQHalluA arXiv 2605.02504](https://arxiv.org/abs/2605.02504) (synthetic 306 lang, eval 4 lang)
- [HalluHard arXiv 2602.01031](https://arxiv.org/abs/2602.01031) (English-only, 2026)
- [RAGTruth ACL 2024](https://aclanthology.org/2024.acl-long.585/) (English-only)
- [LEPISZCZE GitHub](https://github.com/CLARIN-PL/LEPISZCZE) (NLU, brak halu)
- [KLEJ benchmark](https://klejbenchmark.com/) (NLU 2020, brak halu)
- [polish-reranker-roberta-v3 HF](https://huggingface.co/sdadas/polish-reranker-roberta-v3) (nasz reranker base)
- [Kazienko publications](https://kazienko.eu/en/publications)
- [Jan Kocoń DBLP](https://dblp.org/pid/117/2896.html)
- [Teddy Ferdinan DBLP](https://dblp.org/pid/330/5914.html)
