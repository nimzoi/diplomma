# Plan zadania 01 — Wprowadzenie (R1 Introduction)

**Institutional source:** `assignments/01.md` (Task 01, 10 pkt)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/01-Defining-the-Research-Problem-and-Research-Questions.md` (Assignment 1, 2-4 stron)
**Mapuje na rozdział:** R1 Wprowadzenie
**Iteracja realizacji:** 7 (writing) — pre-condition: Iteracje 0-6 ukończone z partial results
**⚠ KRYTYCZNY constraint:** Writing rules R1 z `thesis_elements/CLAUDE.md` (promotor uwagi: 7/10 w v1)

## 1. Czego instytucjonalnie wymaga Task 01

Klasyczny układ intro (~5-8 stron, 1000-1500 słów):
1. Background and Context (~25-30%)
2. Motivation and Problem Statement (~20-25%)
3. Aim and Objectives (~15%)
4. Scope of the Study (~10%)
5. Thesis Structure overview (~10%)
6. **RQ + hipotezy na końcu (~15%)** — NIE na początku!

Plus: academic style (3rd person / passive voice), minimum 10-15 cytacji w R1 dla kontekstu naukowego.

## 2. Czego wymaga PRO-D-THESIS Assignment 1

Formalne sformułowanie:
- **A. Problem Context and Motivation** — domena, gap, dlaczego non-trivial
- **B. Formal Research Problem Statement** — input space X, output Y, constraints Z, optimization M
- **C. Research Question(s)** — empirically answerable
- **D. Hypothesis** — testable, falsifiable
- **E. Success Criteria** — metrics + thresholds
- **F. Feasibility and Scope Justification** — data, compute, risks

## 3. Jak to wygląda w naszym v3.1

### Background and Context
- Ewolucja RAG → CAG → Agentic RAG (Singh i in. 2025)
- Reranker jako determinant retrieval quality
- Polish-reranker-roberta-v3 base — trenowany na MSMARCO-translation, brak domain adaptation dla specjalistycznych domen
- MLOps continuous training jako paradygmat (Sculley, Kreuzberger)
- Brak publicznych benchmarków LLM-as-judge dla polskiego specialty domain
- Drift detection w RAG production systems

### Motivation
- Off-the-shelf polish-reranker miss-rankuje specialty terminology (długie nazewnictwo łacińsko-polskie, kody ATC, DCI)
- Brak walidowanego framework LLM-as-judge dla polskiej domeny — judge'a używają, ale nie walidują kappa vs ekspert
- Polish ChPL↔Ulotka aligned corpus + cross-register retrieval methodology — luka w literaturze (Grabowski 2017 EN-PL, brak intra-PL)

### Problem statement (operational)
Input X: pytania w polskim dotyczące farmakologii (lay i professional register).
Output Y: rerankowane fragmenty ChPL/Ulotek z trafnym semantycznym dopasowaniem.
Constraints Z: open-source stack, on-premise, polski język.
Optimization M: nDCG@10, MRR@10, kappa LLM-judge, drift precision/recall, cross-register accuracy.

### 5 RQ + 5 H — przeniesione z `02b_konspekt_v3_updates.md` sekcja II.3.3

(NA KOŃCU R1, zgodnie z Writing rules!)

### Success criteria (descriptive narrative — NIE statystyczne progi w R1)

Promotor v1 wytknął **„szafowanie kryteriami"** — formalne progi statystyczne w intro odbierane jako over-formalizm. W R1 stosujemy **descriptive narrative parę zdań**; konkretne wartości progów (nDCG@10, kappa, precision/recall, accuracy@10) referencujemy w R6 (Modele) i R7 (Wyniki), gdzie eval methodology jest właściwym miejscem.

Sformułowanie w R1 (przykład draft):
> *„Praca zostanie uznana za zakończoną z sukcesem, gdy zostanie zbudowany reprodukowalny pipeline MLOps retreningu polskiego rerankera farmaceutycznego jako open-source artefakt; gdy framework LLM-as-judge dla polskiej domeny zostanie zwalidowany przeciwko manualnym labelom autorki; gdy iteracyjny retrening zostanie wykonany w trzech cyklach z analizą plateau; gdy framework drift detection zostanie zweryfikowany na symulowanym OOD; oraz gdy aligned ChPL↔Ulotka corpus z metodologią cross-register retrieval zostanie udokumentowany. Pięć wymiarów wkładu pracy (inżynierski, metodologiczny, artefaktowy, eksperymentalny, korpusowy) broni się niezależnie — magnitude empirycznych wyników retrievalu jest jednym z wymiarów, ale nie jedynym warunkiem sukcesu."*

Falsyfikowalne hipotezy H1-H5 z konkretnymi progami **referencjonowane w R6/R7**, NIE wkładane do R1.

### Feasibility
- Sources: `sources_catalog.md` (4100 docs, ~145k preference pairs)
- Compute: SGLang serving, GPU H200 (transfer z poprzedniej infrastruktury)
- Risks: DEC-001 + DEC-002 kill criteria

## 4. Co musimy znaleźć / przygotować

### Cytacje 15-25 w R1 — rozłożone tematycznie (LLMOps × MLOps × PL LLM × RAG/CAG × Domain × Cross-register)

**Cluster 1: LLMOps × MLOps continuous training (3-4 cytacji):**
- Pahune & Akhtar 2025 *Transitioning from MLOps to LLMOps* (Information 16(2)) — z v1
- Sculley et al. 2015 *Hidden Technical Debt in ML Systems* (NeurIPS) — classic foundational
- Kreuzberger et al. 2023 *MLOps: Overview, Definition, Architecture* (IEEE Access)

**Cluster 2: RAG / CAG / Agentic RAG architectures (4-5 cytacji):**
- Lewis et al. 2020 *RAG for Knowledge-Intensive NLP* (NeurIPS) — foundational
- Singh et al. 2025 *Agentic RAG: A Survey* (arXiv:2501.09136) — z v1
- Chan et al. 2025 *Don't Do RAG: CAG* (WWW '25) — z v1
- Gao et al. 2024 *RAG for LLMs: A Survey*
- Jin et al. 2024 *RAGCache* (arXiv:2404.12457) — z v1

**Cluster 3: Polish LLM ecosystem (3-4 cytacji):**
- Ociepa et al. 2025 *Bielik 11B v3* (Computer Science 26(4))
- PLLuM technical report (NCBR/HIVE) — 🟡 verify
- Sławomir Dadas — polish-reranker-roberta-v3 model card — 🟡 verify
- Chen et al. 2024 *BGE-M3* (multilingual embedder)
- Wróbel et al. 2026 *Bielik Guard* (arXiv) — z v1

**Cluster 4: LLM-as-judge methodology (2-3 cytacji):**
- Zheng et al. 2023 *Judging LLM-as-a-Judge* (NeurIPS) — foundational
- Chiang & Lee 2023 *LLMs as Alternative to Human Evaluations* (ACL)

**Cluster 5: Drift detection (1-2 cytacji):**
- Gama et al. 2014 *Concept Drift Adaptation Survey* (ACM CS) — foundational
- Rabanser et al. 2019 *Failing Loudly: Dataset Shift Detection* (NeurIPS)

**Cluster 6: Cross-register medical NLP (do RQ5) (2-3 cytacji):**
- Grabowski 2017 *EN-PL PIL comparable corpus* — DEC-002 🟡 verify
- Cao et al. 2020 *Expertise Style Transfer* (ACL)
- Devaraj et al. 2021 *Paragraph-level Simplification of Medical Texts* — DEC-002 🟡 verify

**Cluster 7: Domain context + DPR (1-2 cytacji):**
- URPL Art. 4 ustawy o prawie autorskim (legal anchor)
- EMA QRD template (Ulotka structure)
- Karpukhin et al. 2020 *DPR* — z hard negatives w II.4.6

**Total target: 15-25 cytacji w R1**, distributed across 7 thematic clusters reflecting LLMOps × MLOps × Polish LLM × RAG/CAG × Domain × Cross-register framing.

Wszystkie cytacje verified przez `/citations` (citation-checker subagent) przed final R1 submission.

### Artefakty w rozdziale
- (brak figur w R1 zazwyczaj; opcjonalnie diagram konceptualny architektury jako Fig. 1.1)

### Pre-conditions z innych iteracji
- Iteracje 0-6 wyniki (mogą wpłynąć na sformułowanie limitations w intro)
- Final lista RQ z 02b_konspekt_v3_updates.md

## 5. Writing rules application (CRITICAL z thesis_elements/CLAUDE.md)

- ⚠ **Classic intro structure FIRST.** RQ NA KOŃCU, nie na początku (promotor uwaga z v1: *„struktura R1 częściowo przesunięta w stronę pytań/hipotez/metryk"*).
- ⚠ **Min 10-15 cytacji** w R1 — kontekst naukowy substantial, NIE odkładać do R2.
- ⚠ **Academic style:** 3rd person passive, krótkie zdania, bez "obecnie", "rosnące", "brak", "jedyny", "żaden".
- ⚠ **Bez emoji.** (Spec docs mają, R1 nie ma.)

## 6. Defense scaffolding application

R1 zazwyczaj **nie zawiera** elementów scaffolding (ablations / error analysis / negative-result framing). Te są w R6/R7/R8.

ALE: warto w sekcji **Aim and Objectives** wymienić *wyraźnie* 5 wymiarów kontrybucji (z Defense pkt 3) jako cele inżynierskie pracy:
> *„Celami inżynierskimi pracy są: (1) walidowany framework LLM-as-judge dla polskiej domeny specjalistycznej; (2) reprodukowalny pipeline MLOps retreningu komponentów RAG; (3) dotrenowany cross-encoder reranker jako artefakt HuggingFace; (4) framework drift detection z simulated drift evaluation; (5) pierwszy publicznie udokumentowany Polish ChPL↔Ulotka aligned corpus z cross-register retrieval methodology."*

To wprowadza 5-wymiarową obronę dla późniejszego R8.

## 7. Acceptance checklist

- [ ] Klasyczny układ (background → ... → RQ na końcu) zachowany
- [ ] Min 10-15 cytacji
- [ ] Academic style w całości
- [ ] 5 RQ explicit
- [ ] 5 H falsifiable z konkretnymi progami
- [ ] Scope IN/OUT explicit (z 02b II.3.4)
- [ ] Feasibility — odniesienie do DEC-001/002 kill criteria
- [ ] 5 wymiarów kontrybucji wymienione w Aim and Objectives
- [ ] Section linkujący do każdego z R2-R8 (Thesis Structure)
- [ ] Length 1000-1500 słów (~5-8 stron)

## 8. Risks / common pitfalls

- ❌ Promotor v1 wytknął "RQ za wcześnie w R1" — **NIE powtarzać**. RQ tylko w ostatniej sekcji R1.
- ❌ "Aim and Objectives" się rozjeżdża z RQ — sprawdź spójność (każde Objective musi być powiązane z którymś RQ).
- ❌ Cytacje z głowy — citation-checker pass przed submission.
- ❌ Length under 1000 słów — promotor v1 uwaga: "kontekst naukowy skromny". Dłuższy intro lepszy.

## 9. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Outline R1 | Proponuje classic intro structure z proporcjami długości per sekcja (background ~25-30% / motivation ~20-25% / aim ~15% / scope ~10% / outline ~10% / RQ na końcu ~15%) | Sign-off na strukturę |
| 2 | Background section (1.1) | Drafts 250-400 słów: rozkład pola RAG/CAG/Agentic + LLMOps × MLOps continuous training + PL LLM ecosystem + drift detection w prod; 5-8 cytacji | Reviews język + fact-check cytacji |
| 3 | Motivation + Problem (1.2-1.3) | Drafts 200-300 słów: 3 luki badawcze (brak PL specialized RAG pipeline + brak walidowanego PL LLM-as-judge + brak Polish ChPL↔Ulotka aligned corpus) grounded w literaturze | Reviews argumentację |
| 4 | Aim & Objectives (1.4) | Lists **5 wymiarów kontrybucji** explicit jako cele inżynierskie (Defense scaffolding pkt 3); **NIE wkłada progów statystycznych** | Reviews completeness |
| 5 | Scope IN/OUT (1.5) | Drafts z konspekt II.3.4 + 2 kluczowe wyłączenia (medical correctness + embedder fine-tuning) | Reviews jasność |
| 6 | Thesis Structure (1.6) | Maps R1-R8 1-2 zdaniami per rozdział | Reviews accuracy |
| 7 | RQ + H section (1.7, NA KOŃCU) | Formalnie RQ1-RQ5 + H1-H5 + **descriptive success criteria narrative** parę zdań (NIE tabela progów) | Reviews defensibility |
| 8 | Citation pass | `/citations thesis_elements/R01_wprowadzenie.docx` | Reviews findings + fixes |
| 9 | Writing rules check | Audit: 3rd person, no time-proofing ("obecnie/rosnące/brak/jedyny/żaden"), no emoji, formal academic, length 1000-1500 słów | Final read-through |

**Workflow note:** każda iteracja Claude generuje propozycję → Ty robisz sign-off lub iterację dalej (Decision before output wzorzec z agent_brief sekcja 8). Iteracje 1, 7 i 8 są obowiązkowe (outline + RQ formalne + citations); pozostałe można pominąć jeśli draft jest gotowy do read-through.
