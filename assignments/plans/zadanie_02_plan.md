# Plan zadania 02 — Literature Review (R2)

**Institutional source:** `assignments/02.md` (Task 02, 10 pkt)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/02-Systematic-Literature-Review.md` (Assignment 2, 4-8 stron)
**Mapuje na rozdział:** R2 Literatura
**Iteracja realizacji:** 7 (writing) — pre-condition: corpus literatura zebrany w trakcie Iteracji 1-3
**⚠ KRYTYCZNY constraint:** Writing rules R2 z `thesis_elements/CLAUDE.md` (promotor uwagi: 6/10 w v1 — selection methodology + table formatting + evidence-to-conclusion)

## 1. Czego instytucjonalnie wymaga Task 02

- Strukturalna, **krytyczna analiza** (nie summary po kolei)
- Citations IEEE lub APA (zgodnie z Task 09 — IEEE footnotes preferowane)
- Paraphrazowanie ponad cytaty dosłowne
- Footnotes + Bibliografia
- Critical evaluation źródeł (credibility, relevance, recency, objectivity)
- Identyfikacja gap badawczego

## 2. Czego wymaga PRO-D-THESIS Assignment 2

- **A. Search Strategy and Source Selection** — bazy, keywords, inclusion/exclusion, time range
  - Min 5 peer-reviewed + 3-5 industry reports + dodatkowe
- **B. Thematic Organization** (NIE chronologiczna)
- **C. Comparative Analytical Table** — Authors/Year/Problem/Dataset/Methods/Metrics/Results/Limitations
- **D. Critical Analysis + Research Gap Identification** — explicit
- **E. Positioning of Thesis Contribution**

## 3. Jak to wygląda w naszym v3.1

### Search strategy (skopiować do R2.1 z `sources_catalog.md` Source Selection Methodology)

- **Bazy:** arXiv (cs.CL, cs.IR), IEEE Xplore, ACL Anthology, ACM DL, DOAJ (PL journals), Google Scholar
- **Keywords:** "retrieval-augmented generation", "cross-encoder reranking", "LLM-as-judge", "drift detection", "polish NLP", "patient information leaflet", "cross-register medical", "MLOps continuous training"
- **Time range:** 2019-2026 (z naciskiem na 2022-2026 dla nowych methodologii)
- **Inclusion:** peer-reviewed lub arXiv preprinty z >50 cytacjami, relevance do RAG/rerankers/MLOps/PL NLP
- **Exclusion:** blogs, tutorials, marketing materials, niezindeksowane non-peer-review preprinty bez cytacji

### Tematyczna struktura (NIE chronologiczna)

**2.2. Architektury RAG i agentowe**
- Klasyczny RAG (Lewis i in. 2020)
- Advanced RAG (z query rewriting, multi-hop)
- Agentic RAG (Singh i in. 2025)
- CAG hybrid (Chan 2025)
- Pozycjonowanie: nasza praca = retrieval-only RAG, focus na reranker komponent

**2.3. Cross-encoder rerankery i domain adaptation**
- BEIR benchmark (Thakur i in. 2021) — cross-encoder reranking gives 5-15pp na specialized
- polish-reranker-roberta-v3 (Polish IR)
- Domain adaptation methods
- Gap: brak Polish specialized domain reranker fine-tuning publicznie udokumentowanego

**2.4. LLM-as-judge methodology**
- Zheng i in. 2023 (Judging LLM-as-a-Judge with MT-Bench)
- Chiang & Lee 2023
- RAGAS framework (Es i in. 2024)
- G-Eval, LLM-as-judge robustness
- Gap: brak walidowanego PL LLM-judge przeciw manual labels

**2.5. MLOps continuous training**
- Sculley i in. (ML Technical Debt)
- Kreuzberger MLOps survey
- Iterative retraining patterns
- Trigger logic, model registry, A/B gating

**2.6. Drift detection w embedding spaces**
- Evidently AI, Alibi Detect
- KS test, MMD na embeddings
- Simulated vs real drift evaluation
- Gap: brak PL RAG drift detection benchmark

**2.7. Cross-register medical NLP** (NEW po DEC-002)
- Grabowski 2017 (EN-PL PIL comparable) — 🟡 verify
- Cao 2020 Expertise Style Transfer
- Devaraj 2021 Paragraph-level Simplification (🟡 verify venue)
- van den Bercken 2019 Neural Text Simplification Medical (🟡 verify year)
- Gap: brak intra-PL cross-register, brak retrieval-focused (vs simplification) cross-register methodology

### Comparative Analytical Tables

Minimum 3 tabele (z konsekwentnym formatowaniem — Writing rule):

- **Tabela 2.1: RAG architectures comparison** (Authors / Year / Type / Components / Limitations)
- **Tabela 2.2: LLM-as-judge methodologies** (Authors / Year / Judge model / Validation method / Metric / Limitations)
- **Tabela 2.3: Cross-register medical NLP** (Authors / Year / Domain / Task / Language / Limitations)

Po każdej tabeli — **explicit synteza linkująca wiersze do konkluzji** (Writing rule).

### Research gap (sekcja 2.8 lub equivalent)

4 luki (powtórz z v1, dostosuj do v3.1):
1. **Brak integracji ChPL↔Ulotka paired corpus w PL RAG** — DEC-002 literature
2. **Brak walidowanego LLM-as-judge dla PL specialty** — Karp 2025 częściowo, ale tylko classification
3. **Brak otwartoźródłowej methodology continuous training PL RAG**
4. **Brak cross-register retrieval methodology dla PL medical**

## 4. Co musimy znaleźć / przygotować

### Cytacje minimum 30 pozycji

Plan rozłożenia:
- 5-6 RAG architectures (Lewis, Chan, Jin, Jiang, Singh, Agrawal)
- 4-5 Rerankery + DPR (Thakur, Karpukhin, polish-reranker refs)
- 6-7 LLM-as-judge (Zheng, Chiang & Lee, Es RAGAS, Min FActScore, Wei SAFE, Bang HalluLens, Sun TrustLLM)
- 3-4 MLOps CT (Sculley, Kreuzberger, Pahune)
- 3-4 Drift detection (Evidently/Alibi Detect papers, MMD survey)
- 3-4 Polish NLP / Bielik / PLLuM (Ociepa Bielik, Wróbel Bielik Guard, PLLuM ref)
- 4 Cross-register medical (Grabowski, Cao, Devaraj, van den Bercken)
- 2-3 Polish medical NLP (Karp 2025 KIO, dodatkowe)

= **min 30+ pozycji**

### Artefakty
- 3 tabele comparative (Writing rule: consistent formatting)
- Footnotes IEEE (Task 09 format)
- Bibliografia alfabetyczna

### Pre-conditions
- 22 źródeł z v1+v2 (zachowane per konspekt v3 FINAL II.14)
- ~10 nowych źródeł zebranych w Iteracji 7 (writing)

## 5. Writing rules application (CRITICAL — promotor v1 6/10)

- ⚠ **Section 2.1 Methodology przeglądu** — explicit inclusion/exclusion (skopiować z `sources_catalog.md`)
- ⚠ **Consistent table formatting** — identyczne kolumny, sortowanie po roku, czytelne kapsy
- ⚠ **Evidence-to-conclusion explicit linking** — po każdej tabeli sekcja "Synteza" z cytacjami konkretnych wierszy: *"Tabela 2.X pokazuje, że X autorów [3, 5, 7] proponuje Y..."*
- ⚠ **NIE** chronologiczna struktura — tematyczna

## 6. Defense scaffolding application

R2 zaszywa **5-wymiarową kontrybucję pracy** (Defense pkt 3) implicytnie przez:
- Każdy z 4 gap badawczych = 1 wymiar kontrybucji
- Sekcja "Positioning of Thesis Contribution" (2.8) — explicit jak każdy z 5 wymiarów wkładu odpowiada na każdy z 4 gap

## 7. Acceptance checklist

- [ ] Sekcja 2.1 Methodology przeglądu = explicit inclusion/exclusion criteria
- [ ] Min 30+ cytacji peer-review
- [ ] Tematyczna (NIE chronologiczna) struktura
- [ ] Min 3 comparative tables z konsekwentnym formatowaniem
- [ ] Po każdej tabeli synteza z evidence-to-conclusion linking
- [ ] 4 luki badawcze explicit
- [ ] Positioning thesis contribution sekcja
- [ ] Bibliografia alfabetyczna, IEEE format
- [ ] Footnotes IEEE 10pt
- [ ] Length 4-8 stron (~3000-4000 słów)

## 8. Risks / common pitfalls

- ❌ Promotor v1 wytknął "nierówny przegląd" — **rozłóż słownictwo równo per sekcja** (każda sekcja ~equal depth)
- ❌ "Mało precyzyjna formalnie" — używaj formalnej terminologii, sprawdź IEEE format consistency
- ❌ "Problemy redakcyjne w tabelach" — projekt tabel raz, replikuj formatting
- ❌ "Wnioski nie wynikają z dowodów" — po każdej tabeli synteza z cytatami wierszy
- ❌ Citation hygiene — phantom citations w v1 prawdopodobnie były problem; **uruchom `/citations` przed submission**
- ❌ Cao/Devaraj/van den Bercken — 🟡 verify venues/years przez citation-checker

## 9. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Sekcja 2.1 Search Methodology | Drafts explicit inclusion/exclusion criteria z `sources_catalog.md` template + bazy (arXiv/IEEE/ACL/ACM/DOAJ) + keywords + time range + selection pipeline | Sign-off na criteria |
| 2 | Sekcja 2.2 RAG/CAG/Agentic | Drafts comparative table 2.1 (Author/Year/Type/Components/Limitations) + 250-400 słów synthesis | Reviews accuracy + citations |
| 3 | Sekcja 2.3 Rerankery + domain adaptation | Drafts narrative + BEIR/DPR references + polish-reranker baseline context + gap explicit | Reviews |
| 4 | Sekcja 2.4 LLM-as-judge | Drafts comparative table 2.2 (Judge model / Validation / Metric / Limitations) + Karp 2025 PL legal context flag | Reviews |
| 5 | Sekcja 2.5 MLOps continuous training | Drafts synthesis (Sculley/Kreuzberger/Pahune) + iterative retraining patterns + trigger logic | Reviews |
| 6 | Sekcja 2.6 Drift detection | Drafts synthesis Evidently/Alibi/MMD + PL RAG drift gap flag | Reviews |
| 7 | Sekcja 2.7 Cross-register medical | Drafts comparative table 2.3 (Grabowski/Cao/Devaraj/van den Bercken) + **intra-PL gap explicit flag** | Reviews |
| 8 | Sekcja 2.8 Research gap synthesis | Explicit answer 4 luki (PL specialized RAG + PL LLM-judge validation + Polish ChPL↔Ulotka + cross-register retrieval) | Reviews logic |
| 9 | Sekcja 2.9 Positioning of contribution | Explicit jak 5 wymiarów wkładu (Defense pkt 3) odpowiada na 4 luki | Reviews coherence |
| 10 | Citation pass via `/citations` | Audit all 30+ cytacji (target: 0 phantom citations, 0 wrong years, 0 duplicate footnotes) | Reviews findings + fixes |
| 11 | Table formatting consistency | Audit: 3 tabele comparative R2 z identyczną strukturą kolumn (Author/Year/...) | Reviews format |
| 12 | Evidence-conclusion linking | Audit: każde podsumowanie sekcji cytuje konkretne wiersze [N,M,P] per IEEE | Reviews precision |
| 13 | Writing rules final check | 3rd person, no time-proofing, formal styl, no chronological structure | Final read-through |

**Workflow note:** iteracje 1 (methodology), 10 (citations), 11 (table consistency) są **obowiązkowe** — to są właśnie sprawy które promotor wytknął w v1 6/10. Iteracje 2-9 mogą iść w paralelnym workflow per sekcja (Claude może draftować 2 sekcje równolegle jeśli mam outline approved).
