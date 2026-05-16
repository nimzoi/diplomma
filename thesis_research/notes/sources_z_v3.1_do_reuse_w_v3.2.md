# Sources do reuse z v3.1 (R1+R2) → v3.2 (RAG halu detection)

**Update 2026-05-16: dodano sekcję modern refs po feedback Magdy że pominęłam SOTA z research outputs.** Nowa sekcja "⭐ Modern 2024-2026 refs z research/*.md (mining round 2)" znajduje się ZA istniejącą zawartością — patrz sekcje N-T poniżej. Round 1 obejmował tylko v3.1 drafts (R1 25 refs + R2 31 refs); round 2 wyciągnął ~50 modern refs z 9 plików `D:\diplomma\thesis_research\research\` (~4200 LOC łącznie). Tych refs **NIE BYŁO** w v3.1 (bo v3.1 to era pharma+reranker, nie halu detection).

**Data:** 2026-05-16
**Cel:** Speedrun mining v3.1 R1+R2 drafts dla refs i framingów które przeniosą się 1:1 do v3.2.
**Source files:**
- `thesis_research/_archive/v3-pharma-reranker/drafts/R1_wprowadzenie.md` (212 LOC, 25 refs, ~5500 słów)
- `thesis_research/_archive/v3-pharma-reranker/drafts/R2_literatura.md` (347 LOC, 31 refs, ~5500 słów + tabele)

**Status:** v3.1 drafty były 70-80% complete; cytacje w 60% verified, reszta 🟡 do citation-checker.

---

## TL;DR — co reusable, co dropujemy

| Bucket | Liczba refs | Akcja w v3.2 |
|---|---|---|
| **A. RAG / dense retrieval foundations** | 6 | Reuse 1:1 (R1+R2 v3.2) |
| **B. LLM-as-judge methodology** | 4 | Reuse 1:1 (kappa framework dla halu eval) |
| **C. MLOps / LLMOps** | 3 | Reuse 1:1 (R5 architektura + R2) |
| **D. Polish NLP resources** | 4 | Reuse 1:1 (Bielik core w v3.2) |
| **E. Statistical drift methods** | 2 | Reuse, re-frame (probe AUROC zamiast embedding drift) |
| **F. Reranker prior art** | 3 | Cite jako "co istnieje" — NOT central w v3.2 |
| **G. Drift tooling (Evidently/Alibi)** | 2 | Reuse w v3.2 dla production halu monitoring |
| **H. Cross-register pharma** | 4 | DROP — pharma-specific, nie consumer rights |
| **I. R2 metodologia (PRISMA-light)** | n/a | Reuse szkielet 2.1 z nowymi keywords v3.2 |

**Reusable count:** ~24 z 31 refs w R2 (≈77% reuse rate). Pharma-specific (6) drop, 25 refs immediately portable.

---

## A. RAG / dense retrieval foundations (REUSE 1:1)

| Ref v3.1 | Cytacja | Status verify | v3.2 chapter |
|---|---|---|---|
| [1] | Lewis et al. 2020 *RAG for Knowledge-Intensive NLP* (NeurIPS) arXiv:2005.11401 | ✓ standard | R1 §1.1 + R2 §2.2 |
| [3] | Karpukhin et al. 2020 *DPR* (EMNLP) arXiv:2004.04906 | ✓ standard | R2 §2.2 |
| [4] | Khattab + Zaharia 2020 *ColBERT* (SIGIR) arXiv:2004.12832 | ✓ standard | R2 §2.2 (alternative) |
| [5] | Chen et al. 2024 *BGE M3-Embedding* arXiv:2402.03216 | ✓ standard | R1 + R2 + R5 (CORE — embedder w v3.2) |
| [7] | Lin et al. 2021 *Pyserini* (SIGIR) | 🟡 verify | R2 §2.2 (hybrid retrieval) |
| [9] | Reimers + Gurevych 2019 *Sentence-BERT* (EMNLP) arXiv:1908.10084 | ✓ standard | R2 §2.2 + R6 |

**v3.2 dodatki (NOT w v3.1):** Wallat 2025 *RAG citation faithfulness vs correctness* (CORE dla v3.2 metryki), Asai et al. 2024 *Self-RAG*.

---

## B. LLM-as-judge methodology (REUSE 1:1)

| Ref v3.1 | Cytacja | Status verify | v3.2 chapter |
|---|---|---|---|
| [12] | Zheng et al. 2023 *MT-Bench / LLM-as-Judge* (NeurIPS) arXiv:2306.05685 | ✓ standard | R2 §2.4 + R6 (judge dla halu eval) |
| [13] | Liu et al. 2023 *G-Eval CoT judging* (EMNLP) arXiv:2303.16634 | ✓ standard | R2 §2.4 + R6 |
| [16] | Cohen 1960 *A Coefficient of Agreement for Nominal Scales* (Educ. Psych. Meas.) | ✓ standard | R2 §2.4 + R6 |
| [17] | Landis + Koch 1977 *Measurement of Observer Agreement for Categorical Data* (Biometrics) | 🟡 verify (klasyczne) | R2 §2.4 + R6 (kappa interpretation) |

**Reuse w v3.2:** Te 4 refs dają complete kappa framework dla LLM-as-judge agreement na halu detection labels. **Identyczne z v3.1 — żadna zmiana.** PLLuM-12B + Bielik 11B v3 + Gemma 3 27B + Claude Haiku jako judge candidates pozostają (DEC w Iter. 0).

**v3.2 dodatki:** Es et al. 2024 *RAGAS* (CORE — context_precision/faithfulness metryki dla halu eval), Lin et al. 2025 *judge bias survey* (positional + length bias dla cross-register).

---

## C. MLOps / LLMOps (REUSE 1:1)

| Ref v3.1 | Cytacja | Status verify | v3.2 chapter |
|---|---|---|---|
| [20] | Sculley et al. 2015 *Hidden Technical Debt in ML Systems* (NeurIPS) | ✓ standard | R1 §1.1 + R2 §2.5 + R5 |
| [21] | Treveil et al. 2020 *Introducing MLOps* (O'Reilly) | 🟡 verify ISBN | R2 §2.5 + R5 |
| [10] R1-version (Pahune+Akhtar 2025) | *Transitioning from MLOps to LLMOps* Information 16(2) art. 87 DOI:10.3390/info16020087 | ✓ verified 2026-05-16 | R1 §1.1 + R5 (LLMOps for halu pipeline) |

**Note:** Kreuzberger et al. 2023 IEEE Access (R1 v3.1 ref [8]) też reusable jako "MLOps architecture canonical reference."

---

## D. Polish NLP resources (REUSE 1:1)

| Ref v3.1 | Cytacja | Status verify | v3.2 chapter |
|---|---|---|---|
| [18] | Bielik 11B v2 tech report (Ociepa et al. 2025) arXiv:2505.02410 + Bielik v3 arXiv:2604.10799 | ✓ verified 2026-05-16 | R1 + R2 + R6 (CORE — generator + probe target w v3.2) |
| [19] | PLLuM (Kocoń et al. 2025) arXiv:2511.03823 | ✓ verified 2026-05-16 | R2 §2.4 + R6 (judge candidate) |
| [30] | Rybak et al. 2020 *KLEJ* (ACL) arXiv:2005.00630 | 🟡 verify | R2 §2.7 (Polish NLU benchmark context) |
| [6] | Zhang et al. 2023 *MIRACL* (TACL) arXiv:2210.09984 | 🟡 verify TACL vs ACL Findings | R2 §2.7 (Polish retrieval comparison) |

**Reuse w v3.2:** Bielik 11B v3 jest CENTRAL w v3.2 — generator + halu probe target jednocześnie. PLLuM-12B kandydat na judge model. KLEJ + MIRACL-pl jako Polish NLP context.

**v3.2 dodatki:** PoLitBench (jeśli istnieje per E2 research), AggTruth Wrocław Tech (English-only — cite jako "first-mover risk" w v3.2 R8).

---

## E. Statistical methods (REUSE, RE-FRAME)

| Ref v3.1 | Cytacja | Status verify | Re-frame dla v3.2 |
|---|---|---|---|
| [22] | Lopez-Paz + Oquab 2017 *Revisiting Classifier Two-Sample Tests* (ICLR) arXiv:1610.06545 | ✓ standard | R7 — **AUROC dla halu probe binary classification** zamiast embedding drift detection |
| [23] | Gretton et al. 2012 *A Kernel Two-Sample Test* (JMLR) | ✓ standard | R5/R7 — **MMD jako baseline alternative dla probe** |

**Re-frame:** w v3.1 te refs uzasadniały drift detection na BGE-M3 embeddings. W v3.2 → uzasadniają **probe metryki** (AUROC binary classifier na hidden states). Identyczna statystyka, inna aplikacja.

---

## F. Reranker prior art (CITE jako CONTEXT, NOT central)

| Ref v3.1 | Cytacja | Status verify | v3.2 chapter |
|---|---|---|---|
| [8] | Nogueira et al. 2020 *monoT5* (Findings of EMNLP) | 🟡 verify | R2 §2.3 (cite jako standard retrieval+reranking) |
| [10] | Dadas ~2024 *polish-reranker-roberta-v3* HF | 🟡 verify | R2 §2.3 (cite jako Polish baseline) |
| [11] | Xiao et al. 2023 *BGE-reranker / C-Pack* BAAI | 🟡 verify | R2 §2.3 (multilingual alternative) |

**Decision dla v3.2:** Reranker NIE jest fine-tunable w v3.2 (citation-grounded RAG, NIE iteracyjny retraining). Cytujemy te refs jako "what exists" w R2 background, ale **NIE central contribution.** Może być optional component w R5 architektura (rerank top-50 → top-10 przed citation grounding step).

---

## G. Drift detection tooling (REUSE — production halu monitoring)

| Ref v3.1 | Cytacja | Status verify | Re-use w v3.2 |
|---|---|---|---|
| [24] | Evidently AI Team ~2023 *Evidently OSS* (GitHub) | 🟡 tool ref, no peer-review | R5 architecture — **production halu rate drift monitoring** |
| [25] | Seldon ~2023 *Alibi Detect OSS* (GitHub) | 🟡 tool ref, no peer-review | R5 architecture — **probe confidence drift** |

**v3.2 use case:** Detection że hallucination rate wzrasta w czasie (data drift / model drift). Identyczna tool-stack, inna metryka (P(halu) zamiast retrieval quality drift).

---

## H. Cross-register medical NLP (DROP — pharma-specific)

| Ref v3.1 | Cytacja | v3.2 status |
|---|---|---|
| [26] | Grabowski 2018 *EN-PL PIL corpus* CILT 341 ✓ verified | DROP — consumer rights nie ma cross-register |
| [27] | Cao et al. 2020 *Expertise Style Transfer* (ACL) | DROP — medical-specific |
| [28] | Devaraj et al. 2021 *Paragraph-level Simplification of Medical Texts* (NAACL) ✓ verified | DROP — medical-specific |
| [29] | van den Bercken et al. 2019 *Neural Text Simplification Medical* (WWW) ✓ verified | DROP — medical-specific |

**Note:** Cao 2020 [27] jest re-usable w **future work** sekcji R8 v3.2 jako "expertise style transfer może być dodany jako secondary component dla legal jargon → consumer language" — opcjonalnie.

---

## I. R2 metodologia — PRISMA-light protokół (REUSE szkielet, change keywords)

**Reusable z v3.1 R2 §2.1:**
- Inclusion criteria (recency 2015-2025, peer-review status, relevance, language PL+EN, verifiability) — IDENTYCZNE
- Exclusion criteria (popularnonaukowe, niski citation count, generation-only) — IDENTYCZNE
- Search bases (arXiv, ACL Anthology, IEEE Xplore, Google Scholar, DOAJ) — IDENTYCZNE
- Pipeline selekcyjny (Round 1 → Round 2 → Round 3 funnel) — IDENTYCZNE
- 5 świadomych biases (anglojęzyczny, recency, open-access, survey limited) — IDENTYCZNE plus dodać (6) **first-mover bias** dla v3.2 (mało Polish halu detection literature)

**Zmiana w v3.2 — keywords (PL + EN):**

V3.1 keywords (DROP):
- ~~*Polish reranker, polish-reranker, fine-tuning, LLM-as-judge for medical*~~
- ~~*Cross-register, expertise style transfer, patient information leaflet, ChPL, ulotka*~~
- ~~*Pharmaceutical NLP, ATC, DCI*~~

V3.2 keywords (NEW):
- *Hallucination detection*, *hallucination probe*, *hidden states classifier*, *internal state probing*
- *Citation grounding*, *attribution evaluation*, *faithfulness vs correctness*
- *NLI for citations*, *natural language inference*, *entailment classification*, *mDeBERTa*, *HerBERT*
- *Polish legal NLP*, *consumer rights NLP*, *UOKiK Q&A*, *prawo konsumenckie*
- *Linear probe*, *AUROC binary classifier*, *Wallat 2025*, *AggTruth*, *Dubanowska 2025*
- *RAGAS*, *self-RAG*, *retrieval-augmented faithfulness*

**7 obszarów tematycznych v3.2 (aktualizacja z 6 obszarów v3.1):**
1. RAG paradigm + dense retrieval (KEEP — sekcja 2.2 v3.1)
2. ~~Cross-encoder rerankery~~ → **Citation grounding methodology** (NEW)
3. LLM-as-judge methodology (KEEP — sekcja 2.4 v3.1)
4. **Hidden states halu probes** (NEW — najmocniejszy v3.2 obszar)
5. **NLI classifiers dla citation verification** (NEW — mDeBERTa + HerBERT + CDSC-E)
6. MLOps / LLMOps continuous training (KEEP — sekcja 2.5 v3.1, re-frame dla halu)
7. Polish NLP resources + benchmarks (KEEP — sekcja 2.7 v3.1)

---

## J. R1 framing reusable (overview)

**Reusable z R1 v3.1:**

§1.1 Tło i kontekst — pierwsze 4 paragrafy IDENTYCZNE (RAG paradigm, BGE-M3 embedding, dense retrieval, LLM-as-judge introduction). 5-y paragraf (continuous training MLOps) IDENTYCZNY. 6-y (Polish NLP ecosystem) IDENTYCZNY. **Drop:** ostatnie 3 paragrafy (drift, cross-register medical, pharma domain) → zamienić na **halu detection prior art** (Wrocław Tech AggTruth English-only, mGarbowski/llm-projekt, Polish RAG benchmarks lack of halu metrics).

§1.2 Motywacja — DROP całkowicie (pharma reranker specific). **Replace z trzema lukami:**
1. Polish RAG bez citation grounding metrics (faithfulness vs correctness na polish)
2. Polish hidden states halu probes (English-only Wrocław Tech AggTruth, brak Polish)
3. Polish CitationBench dataset (brak publicznego benchmark dla Polish RAG halu eval)

§1.3 Cel i zadania — pięciowymiarowy model wkładu CONCEPT REUSABLE. Replace v3.1 wymiary z v3.2:
1. ~~Walidacja LLM-as-judge dla pharma~~ → **Walidacja LLM-as-judge dla Polish halu detection**
2. ~~MLOps continuous training pipeline reranker~~ → **MLOps continuous improvement loop dla RAG halu**
3. ~~Dotrenowany cross-encoder reranker~~ → **Hidden states halu probe Bielik 11B v3 layer 47**
4. ~~Drift detection framework~~ → **Probe AUROC framework + production halu drift**
5. ~~Polish ChPL↔Ulotka aligned corpus~~ → **Polish CitationBench (~10-15k pairs publishable HF)**

§1.4 Zakres — szkielet IDENTYCZNY. IN/OUT scope ramy reusable. Świadome biases concept reusable (5 biases v3.1 → 5 biases v3.2 z innymi nazwami).

§1.5 Struktura pracy — szkielet 8 rozdziałów IDENTYCZNY. Treść każdego rozdziału aktualizować pod v3.2.

§1.6 Pytania badawcze — STRUCTURE IDENTYCZNA (5 RQ + 5 H + falsyfikowalne progi). REPLACE content z v3.2 RQ:
- RQ1: Czy linear probe Bielik 11B v3 layer 47 osiąga AUROC ≥0.70 (CI ≥0.60) na halu binary classification?
- RQ2: Czy LLM-as-judge (Bielik / PLLuM / Gemma 3) osiąga kappa ≥0.50 z manual halu labels?
- RQ3: Czy 3-tier NLI (mDeBERTa → HerBERT → judge LLM) osiąga ≥85% citation precision?
- RQ4: Czy citation 2-metric framework (faithfulness vs correctness per Wallat 2025) jest defensible na Polish?
- RQ5 (supporting): Czy Polish CitationBench (~10-15k pairs) jest publishable jako standalone HF artifact?

---

## K. Akcjonowalna lista TODO dla R1+R2 v3.2 (gdy będę pisać)

**R1 v3.2 (5000-7000 słów):**
1. Skopiować §1.1 paragrafy 1-6 z v3.1 (RAG + DPR + BGE-M3 + LLM-as-judge + MLOps + Polish NLP) → **adapter pre-existing 70%**
2. Napisać 3 nowe paragrafy: halu detection background (Wrocław Tech, Wallat 2025), Polish legal NLP context (UOKiK, ELI ustawy), citation grounding distinction (faithfulness vs correctness)
3. §1.2 motywacja — write fresh (3 luki v3.2 per powyżej)
4. §1.3-1.6 — adapter szkielet z v3.1 z v3.2 content

**R2 v3.2 (~6000-9000 słów):**
1. Skopiować §2.1 metodologia z v3.1 (zmień keywords + 7 obszarów tematycznych)
2. §2.2 RAG/dense retrieval — 90% reusable (drop 2 zdania pharma)
3. ~~§2.3 cross-encoder rerankery~~ → **§2.3 citation grounding methodology** — write fresh
4. §2.4 LLM-as-judge — 95% reusable (drop sentence "for pharma")
5. ~~§2.5 MLOps drift~~ → **§2.5 hidden states probes + halu detection** — write fresh (use AggTruth, Dubanowska, Wallat refs)
6. **§2.6 NLI classifiers dla citation verification** (NEW) — write fresh (mDeBERTa, HerBERT, CDSC-E refs)
7. §2.7 MLOps/LLMOps — re-frame z §2.5 v3.1 (Sculley, Treveil, Pahune+Akhtar, Kreuzberger)
8. §2.8 Polish NLP resources — 90% reusable (drop pharma sentence)
9. §2.9 Podsumowanie luk — re-write per v3.2 5 luk

**Time estimate:** R1 v3.2 ~4-6h (60-70% adapter z v3.1), R2 v3.2 ~6-8h (50% adapter, 50% fresh).

---

## L. Citation hygiene — co JESZCZE do verify (carry forward)

Pozycje 🟡 z v3.1 carry-over do v3.2 citation pass:
- [2 R2] Robertson + Zaragoza 2009 BM25
- [7 R2] Pyserini Lin 2021 — verify SIGIR 2021 vs 2022
- [8 R2] Nogueira monoT5 — confirm exact paper
- [10 R2] Dadas polish-reranker — verify author/year
- [11 R2] Xiao BGE-reranker — verify
- [17 R2] Landis Koch 1977 — verify (klasyczne, 99% ok)
- [21 R2] Treveil O'Reilly — verify ISBN
- [24 R2] Evidently AI — tool ref, brak peer-review (cite as docs)
- [25 R2] Alibi Detect — tool ref, brak peer-review (cite as docs)
- [28 R2] Devaraj 2021 — verify NAACL vs EMNLP (R1 verified NAACL ✓)
- [29 R2] van den Bercken 2019 — verify year (R1 verified 2019 ✓)
- [30 R2] Rybak KLEJ — verify

**Action:** uruchomić citation-checker subagent na *.md drafts po napisaniu R1 + R2 v3.2.

---

# ⭐ Modern 2024-2026 refs z research/*.md (mining round 2)

**Data mining:** 2026-05-16
**Trigger:** Magda zauważyła że v3.1 mining (round 1) nie zawiera SOTA z research outputs Iter. 0.
**Source files** (9 plików, ~4200 LOC):
- `halu_detection_sota_2024_2026.md` (378 LOC) — SOTA halu detection scan
- `domain_A_feasibility.md` (458 LOC) — ISAP+UOKiK+Reddit + polish NLI
- `nli_alternatives_2026.md` (431 LOC) — mDeBERTa, HerBERT, polish NLI landscape
- `literature_deep_2026.md` (796 LOC) — DEEPEST mine, ~73 refs
- `poleval_2026.md` (194 LOC) — PolEval 2024-2026 + polish landscape
- `bielik_tools_outlines_research.md` (548 LOC) — Bielik + Outlines + structured output
- `probes_polish_llm_research.md` (474 LOC) — probes implementation refs
- `large_llm_2026_polish.md` (452 LOC) — Polish LLM landscape 2026
- `query_patterns_polish_consumer_2026.md` (497 LOC) — consumer query patterns

**Status legend:** ✓ verified peer-reviewed/standard | 🟡 needs verify (preprint, "Authors TBD", year/venue uncertain)

**Mining methodology:** klastrowanie tematyczne wg 7 obszarów v3.2; każdy ref z (a) pełnym cite, (b) source file + sekcja, (c) chapter destination, (d) status, (e) 1-zdaniowy contribution. Filter: tylko publishable / ważne refs (~50 total target, NIE 200).

---

## Bucket A: Halu detection SOTA 2024-2026

| Ref | Citation full | Source file | v3.2 chapter | Verify status | Contribution |
|---|---|---|---|---|---|
| Farquhar 2024 | Farquhar S., Kossen J., Kuhn L., Gal Y. (2024) *Detecting hallucinations in large language models using semantic entropy.* Nature 630, 625-630. DOI:10.1038/s41586-024-07421-0 | halu_detection_sota §2.1, literature_deep §1.1 ref 7 | R1 §1.1 + R2 §2.5 (foundational) + R6 | ✓ Nature (gold standard) | Foundational — semantic entropy mierzy uncertainty about meanings nie tokens; baseline dla wszystkiego po niej |
| Kossen 2024 SEP | Kossen J., Han J., Razzak M., Schut L., Malik S., Gal Y. (2024) *Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs.* NeurIPS 2024 / ICLR 2025. arXiv:2406.15927 | halu_detection_sota §2 + literature_deep §1.1 ref 8 | R2 §2.5 + R6 (probe lineage) | ✓ NeurIPS/ICLR | Single hidden state → predict semantic entropy; redukuje overhead resampling do near-zero |
| Chen INSIDE 2024 | Chen C., Liu K., Chen Z., Gu Y., Wu Y., Tao M. (2024) *INSIDE: LLMs' Internal States Retain the Power of Hallucination Detection.* arXiv:2402.03744 | literature_deep §1.1 ref 9 + halu_detection_sota §2 | R2 §2.5 + R6 (probes baseline) | 🟡 arXiv preprint | EigenScore z embedding covariance eigenvalues — sentence-level halu detection |
| Obeso 2025 Real-Time | Obeso O., Arditi A., Ferrando J., Freeman J., Holmes C., Nanda N. (2025) *Real-Time Detection of Hallucinated Entities in Long-Form Generation.* arXiv:2509.03531 (rev 2026-02) | literature_deep §1.1 ref 10 + halu_detection_sota §2 + probes_polish §1 | R2 §2.5 + R5 + R6 (CORE — primary impl reference) | 🟡 arXiv | Linear probes on hidden states for real-time streaming halu detection; AUC 0.89-0.90 (Llama-3.3-70B) bije semantic entropy 0.71; **obalcells/hallucination_probes repo** |
| Dubanowska 2025 OOD-fail | Dubanowska Z., Żelaszczyk M., Brzozowski M., Mandica P., Karpowicz M. (2025) *Representation-based Broad Hallucination Detectors Fail to Generalize Out of Distribution.* EMNLP 2025 Findings, arXiv:2509.19372 | literature_deep §1.1 ref 11 + probes_polish §10 | R2 §2.5 + R7 (CRITICAL defensive ref) | 🟡 EMNLP Findings | SOTA probes na RAGTruth driven by spurious correlations; OOD = near-random (~0.5) — MUSI być cited dla defense methodology w R7 |
| AggTruth Wrocław 2025 | Matys P., Eliasz J., Kiełczyński K., Langner M., Ferdinan T., Kazienko P., Kocoń J. (2025) *AggTruth: Aggregated Truth Detection for LLMs.* ICCS 2025, arXiv:2506.18628 | poleval_2026 §5 + halu_detection_sota | R1 §1.2 + R2 §2.5 + R8 future work | 🟡 ICCS 2025 | **Wrocław Tech CLARIN-PL grant** halu detection — ENGLISH-only datasets (NQ, HotPotQA); polish gap explicit, autorka first-mover |
| Mu-SHROOM 2025 | Vázquez R. et al. (2025) *Mu-SHROOM: Multilingual Shared-task on Hallucinations and Related Observable Overgeneration Mistakes.* SemEval 2025 Task 3. arXiv:2504.11975, aclanthology 2025.semeval-1.322 | halu_detection_sota §2 + poleval_2026 §4 + literature_deep §0 | R1 §1.2 + R2 §2.5 + R8 (CRITICAL — polish gap evidence) | ✓ SemEval 2025 | 14 języków, **POLSKI POMINIĘTY** — first-mover argument dla DEC-003 |
| FaithJudge Vectara 2025 | Tamber M., Bao F., Xu R. et al. (2025) *Benchmarking LLM Faithfulness in RAG with Evolving Leaderboards (FaithJudge).* EMNLP 2025 Industry Track. arXiv:2505.04847. github.com/vectara/FaithJudge | halu_detection_sota §2 + literature_deep §5.3 ref 37 | R2 §2.4 + R6 + R7 (judge framework reference) | 🟡 EMNLP Industry | LLM-as-judge framework z human-annotated examples, 84% balanced accuracy z o3-mini-high |
| Mirage of Halu Detection 2025 | Kulkarni A. et al. (Apple) (2025) *Evaluating Evaluation Metrics — The Mirage of Hallucination Detection.* EMNLP 2025 Findings. arXiv:2504.18114 | halu_detection_sota §2 (Trend 1) + probes_polish §10 | R2 §2.5 + R7 (CRITICAL — overestimation warning) | 🟡 EMNLP Findings | ROUGE-based eval przeszacowuje detection o do 45.9% AUROC; meta-analiza |
| Illusion of Progress 2025 | (Authors TBD) (2025) *The Illusion of Progress: Re-evaluating Hallucination Detection.* EMNLP 2025 | halu_detection_sota §2 | R2 §2.5 + R7 | 🟡 EMNLP | Krytyka SOTA na ROUGE eval przeszacowanie — sister paper do "Mirage" |
| HalluLens Meta 2025 | Bang Y., Ji Z., Schelten A., Hartshorn A., Fowler M., Zhang C., Cancedda N., Fung P. (Meta) (2025) *HalluLens: LLM Hallucination Benchmark.* ACL 2025. arXiv:2504.17550 | halu_detection_sota §2 | R2 §2.5 (extrinsic vs intrinsic taxonomy) | 🟡 ACL 2025 | Taxonomy extrinsic vs intrinsic + dynamic test set generation przeciwko data saturation |
| Sardana RAG eval 2025 | Sardana A. (2025) *Real-Time Evaluation Models for RAG: Who Detects Hallucinations Best?* arXiv:2503.21157 | halu_detection_sota §2 + literature_deep §5.3 ref 39 | R7 (Lynx/HHEM/TLM benchmark ref) | 🟡 arXiv | Head-to-head benchmark Lynx, HHEM, TLM, Prometheus, LLM-judge na 6 RAG apps |
| RAGTruth 2024 | Niu C. et al. (2024) *RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models.* ACL 2024 | halu_detection_sota §6.1 + literature_deep §5.1 ref 5 | R2 §2.5 + R3 (corpus reference dla halu labeling) | ✓ ACL 2024 | Word-level hallucination annotations dla RAG workflows; bazowy training set Lynx + Dubanowska's critique target |
| Lynx Patronus 2024 | Ravi S., Patra S., Sun R., Gajraj A., Kannappan A., Pruneski J. A. et al. (2024) *Lynx: An Open Source Hallucination Evaluation Model.* arXiv preprint, Patronus AI | halu_detection_sota §2 + literature_deep §5.1 ref 6 | R2 §2.5 + R6 + R7 (multilingual baseline dla porównania) | 🟡 Patronus AI preprint | HaluBench 15k samples + Lynx 8B/70B — open-source SOTA halu model EN-only, baseline dla polish probe comparison |
| MultiHal 2025 | Vatsal et al. (2025) *MultiHal: KG-grounded Multilingual Hallucination Detection.* arXiv:2505.14101 | halu_detection_sota §2 + poleval_2026 §4 | R2 §2.5 + R8 | 🟡 arXiv | KG-paths z Wikidata, multilingual + multihop; **5 EU lang (DE, IT, FR, PT, ES + EN), POLSKI BRAK** |
| HalluLens / TruthfulQA (multiling) | Lin S., Hilton J., Evans O. (2022) *TruthfulQA: Measuring How Models Mimic Human Falsehoods.* ACL 2022 | literature_deep §5.1 ref 3 | R2 §2.5 (foundational truthfulness benchmark) | ✓ ACL 2022 | Adversarial truthfulness benchmark — foundational; brak PL translation |
| FELM 2023 | (Authors) (2023) *FELM: Benchmarking Factuality Evaluation of Large Language Models.* NeurIPS 2023 | halu_detection_sota §6.1 | R2 §2.5 | 🟡 NeurIPS | Factuality eval, 5 domain, 847 Q — EN-only |
| FActScore 2023 | Min S., Krishna K., Lyu X., Lewis M., Yih W., Koh P. W. et al. (2023) *FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation.* EMNLP 2023 | literature_deep §5.1 ref 2 | R2 §2.4 + R6 (atomic facts methodology) | ✓ EMNLP 2023 | Decomposition into atomic facts → retrieval against Wikipedia → percentage supported — methodology dla per-claim faithfulness |
| SelfCheckGPT 2023 | Manakul P., Liusie A., Gales M. J. F. (2023) *SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models.* EMNLP 2023 | literature_deep §5.1 ref 1 + halu_detection_sota §2 | R2 §2.5 (self-consistency baseline) | ✓ EMNLP 2023 | Sampled responses z LLM-self-divergence → hallucination signal; foundational black-box approach |
| CoVe Meta 2024 | Dhuliawala S., Komeili M., Xu et al. (Meta) (2024) *Chain-of-Verification.* ACL Findings 2024 | halu_detection_sota §2 | R2 §2.5 (self-verification methods) | 🟡 ACL Findings | Model drafts → plans verification questions → answers independently → final |
| HHEM Vectara | Vectara (2024-2026) *HHEM 2.x — Hughes Hallucination Evaluation Model.* HuggingFace + leaderboard | halu_detection_sota §4 + poleval_2026 §4 | R7 (multilingual baseline) | 🟡 commercial/OSS hybrid | NLI fine-tuned classifier; HHEM 2.1 EN/DE/FR; HHEM 2.3 ma 11 langs — sprawdzić listę PL |

---

## Bucket B: Hidden-states probes implementation

| Ref | Citation full | Source file | v3.2 chapter | Verify status | Contribution |
|---|---|---|---|---|---|
| obalcells repo | obalcells (2025-2026) *Hallucination Probes — Production demo + checkpoints.* github.com/obalcells/hallucination_probes + huggingface.co/collections/obalcells/hallucination-probes | probes_polish §2 + literature_deep §1.5 + bielik_tools | R5 + R6 (CORE — primary fork target) | ✓ active OSS | Production-ready repo dla Real-Time Detection paper (Obeso 2025); LoRA + linear value head; Mistral support → Bielik compatibility |
| Vaddi H-Neurons 2026 | Vaddi S., Vaddi P. (2026) *Do Hallucination Neurons Generalize? Evidence from Cross-Domain Transfer in LLMs.* arXiv:2604.19765 | literature_deep §1.1 ref 13 | R2 §2.5 + R7 (cross-domain calibration argument) | 🟡 arXiv 2026 | H-neurons in-domain AUROC 0.783 → cross-domain 0.563 (delta 0.220, p<0.001); per-domain calibration MUSI |
| Liang & Wang Neural Probe 2025 | Liang S., Wang H. (2025) *Neural Probe-Based Hallucination Detection for Large Language Models.* arXiv:2512.20949 | literature_deep §1.1 ref 12 + probes_polish §5 | R2 §2.5 + R6 (MLP fallback architecture) | 🟡 arXiv 2025-12 | MLP probes z multi-objective loss (focal + soft span + sparsity + KL) +270% precision na TriviaQA; Bayesian layer search |
| Radharapu Brier probe 2025 | Radharapu B., Saxena E., Li K., Whitehouse C., Williams A., Cancedda N. (2025) *Calibrating LLM Judges: Linear Probes for Fast and Reliable Uncertainty Estimation.* arXiv:2512.22245 | literature_deep §1.1 ref 19 + §1.6 | R6 (probe calibration approach) | 🟡 arXiv 2025-12 | Brier-score loss linear probe na judge hidden states; ECE -10× compute vs verbalized confidence |
| CCPS 2025 | (Authors) (2025) *CCPS: Calibrating LLM Confidence by Probing Perturbed Representation Stability.* arXiv:2505.21772, EMNLP 2025 | literature_deep §1.6 + §5.2 ref 20 | R6 (calibration ablation Iter. 3) | 🟡 EMNLP 2025 | Adversarial perturbations na final hidden states → ECE -55%, Brier -21% |
| ICR Probe 2025 | (Authors) (2025) *ICR Probe: Tracking Hidden State Dynamics for Reliable Hallucination Detection in LLMs.* ACL 2025, arXiv:2507.16488 | literature_deep §1.1 ref 14 | R2 §2.5 (residual stream dynamics) | 🟡 ACL 2025 | Inter-layer Contribution Ratio, residual updates tracking |
| CLAP 2025 | (Authors) (2025) *Cross-Layer Attention Probing (CLAP) for Fine-Grained Hallucination Detection.* arXiv:2509.09700 | literature_deep §1.1 ref 15 | R6 (multi-layer joint encoding) | 🟡 arXiv | Full residual stream as joint sequence z attention mechanism — OOD outperformance vs single-layer |
| Spectral Attention Maps 2025 | (Authors) (2025) *Hallucination Detection in LLMs Using Spectral Features of Attention Maps.* EMNLP 2025, arXiv:2502.17598 | literature_deep §1.1 ref 16 + halu_detection_sota §3.2 | R2 §2.5 (white-box alternative) | 🟡 EMNLP 2025 | Eigenvalues attention matrices jako structural feature dla halu detection |
| Semantic Energy 2025 | (Authors) (2025) *Semantic Energy: Detecting LLM Hallucination Beyond Entropy.* arXiv:2508.14496 | literature_deep §1.1 ref 17 + halu_detection_sota §3.1 | R2 §2.5 | 🟡 arXiv 2025-08 | Boltzmann energy on penultimate logits — operate na logitach, no training |
| Bayesian SE 2025 | (Authors) (2025) *Hallucination Detection on a Budget: Efficient Bayesian Estimation of Semantic Entropy.* arXiv:2504.03579 | literature_deep §1.1 ref 18 | R2 §2.5 (efficiency improvement on Farquhar) | 🟡 arXiv | Adaptive sampling Bayesian update — 53% mniej samples vs Farquhar 2024 same quality |
| EigenTrack 2025 | (Authors) (2025) *EigenTrack: Temporal Spectral Analysis of Hidden Activations for Hallucination and OOD Detection.* arXiv:2509.15735 | literature_deep §1.1 ref 21 | R8 future work | 🟡 arXiv | Eigenvalue tracking multi-layer covariance, joint halu + OOD detection |
| H-Neurons Existence 2025 | (Authors) (2025) *H-Neurons: On the Existence, Impact, and Origin of Hallucination-Associated Neurons in LLMs.* arXiv:2512.01797 | literature_deep §1.8 ref 23 | R2 §2.5 (theoretical grounding) | 🟡 arXiv 2025-12 | Theoretical grounding hallucination neurons |
| Where Fake Citations 2026 | (Authors) (2026) *Where Fake Citations Are Made: Tracing Field-Level Hallucination to Specific Neurons in LLMs.* arXiv:2604.18880 | literature_deep §1.8 ref 24 | R2 §2.5 + R6 (CORE — citation-specific halu) | 🟡 arXiv 2026-04 | Tracing halucynacji do specific neurons via field-level (Wikipedia, scientific) — wprost relevantne dla citation grounding |
| HALT 2026 | (Authors) (2026) *HALT: Hallucination Assessment via Latent Testing.* arXiv:2601.14210 | literature_deep §1.8 ref 25 | R6 (lightweight probe alternative) | 🟡 arXiv 2026-01 | Lightweight residual probes z hidden states; cheap parallel z inference |
| TransformerLens | TransformerLensOrg / Bloom et al. (active 2025) *TransformerLens — Mechanistic Interpretability of GPT-style LMs.* github.com/TransformerLensOrg/TransformerLens | literature_deep §1.5 ref 67 + probes_polish §3 | R5 (extraction tool) | ✓ active OSS | Mechanistic interpretability framework, exposes wszystkie internal activations HF model — Mistral supported, **Bielik 50L wymaga custom HookedTransformerConfig** |
| nnsight | NDIF/EleutherAI (active 2025) *nnsight — alternative interpretability framework.* github.com/ndif-team/nnsight | probes_polish §3 + literature_deep §1.5 | R5 (alternative) | ✓ active OSS | Alternative do TransformerLens, deferred execution z syntactic API; bardziej direct HF integration |
| Lookback Lens 2024 | Chuang Y.-S. et al. (2024) *Lookback Lens: Detecting and Mitigating Contextual Hallucinations Using Only Attention Maps.* EMNLP 2024. github.com/voidism/Lookback-Lens | probes_polish §2 ref 5 | R2 §2.5 (attention-based alternative) | ✓ EMNLP 2024 | LLaMA-2-7B native; transfers across models 7B→13B; uses attention maps NIE hidden states (alternative paradigm) |
| SAPLMA 2023 | Azaria A., Mitchell T. (2023) *The Internal State of an LLM Knows When It's Lying.* EMNLP 2023, arXiv:2304.13734 | probes_polish §2 ref 6 + literature_deep §1.9 | R2 §2.5 (foundational hidden-states halu detector) | ✓ EMNLP 2023 | Generic; 3 hidden layers MLP (256→128→64); foundational — first hidden-states halu detector |
| Burns CCS 2022 | Burns C. et al. (2022) *Discovering Latent Knowledge in Language Models Without Supervision.* arXiv:2212.03827. github.com/collin-burns/discovering_latent_knowledge | probes_polish §2 ref 2 | R2 §2.5 (unsupervised probe baseline) | ✓ ICLR 2023 | Generic transformer; brak Mistral-specific; unsupervised contrast pairs paradigm |
| LLM-Check NeurIPS 2024 | Sriramanan G. et al. (2024) *LLM-Check: Investigating Detection of Hallucinations.* NeurIPS 2024. github.com/GaurangSriramanan/LLM_Check_Hallucination_Detection | probes_polish §10 ref 11 | R2 §2.5 | ✓ NeurIPS 2024 | Focus na metrykach detekcji halu, mniej infrastruktury |
| Sisinflab Hidden States 2025 | Sisinflab (2025) *Are the Hidden States Hiding Something? Testing Factuality-Encoding Capabilities.* ACL 2025. arXiv:2505.16520 | probes_polish §10 ref 12 | R2 §2.5 | 🟡 ACL 2025 | Extends SAPLMA; factuality-encoding analiza |
| RepE Zou 2023 | Zou A. et al. (2023) *Representation Engineering: A Top-Down Approach to AI Transparency.* arXiv:2310.01405. github.com/andyzoujm/representation-engineering | probes_polish §2 ref 4 | R5 (broader interpretability framework) | 🟡 arXiv 2023 | Generic transformer; RepReading + RepControl pipelines |
| EleutherAI ELK | EleutherAI *elk: Eliciting Latent Knowledge.* github.com/EleutherAI/elk | probes_polish §2 | R5 alternative | ✓ active OSS | Generic, supports HF models; ELK design dla yes-no QA |

---

## Bucket C: NLI dla citation verification

| Ref | Citation full | Source file | v3.2 chapter | Verify status | Contribution |
|---|---|---|---|---|---|
| MoritzLaurer mDeBERTa 2mil7 | MoritzLaurer (2023) *mDeBERTa-v3-base-xnli-multilingual-nli-2mil7.* HuggingFace huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7. License: MIT, 300M params, 27 langs incl. PL (~105k pairs trained) | nli_alternatives §1 + domain_A_feasibility §4 | R5 + R6 (CORE — primary verifier model card cite) | ✓ HF model card verified 2026-05-16 | **De facto standard multilingual NLI**; 275k downloads/mo; XNLI ~0.80 avg, polish proxy ~0.78-0.81; **CORE w v3.2 stack** |
| MoritzLaurer mDeBERTa MNLI-XNLI | MoritzLaurer *mDeBERTa-v3-base-mnli-xnli.* HF, MIT | nli_alternatives §2 | R6 (alternative baseline ablation) | ✓ HF model card | Slightly older training data; XNLI 0.808 avg ale brak pl w training |
| HerBERT-large allegro | Allegro Tech (Mroczkowski R. et al. 2021) *HerBERT-large.* HF allegro/herbert-large-cased. CC BY 4.0, 8.6B PL tokens | nli_alternatives §3 + domain_A_feasibility §4 | R5 + R6 (NLI fine-tune candidate, ablation Iter. 2) | ✓ HF | Native Polish 8.6B tokens; fine-tunable na CDSC-E (~1-2h A100, KLEJ leaderboard 96.4% accuracy) |
| CDSC-E Allegro | Wróblewska A. (2017) *Compositional Distributional Semantics Corpus for Polish (CDSC-E).* HF allegro/klej-cdsc-e. CC BY-NC-SA-4.0, 10k pairs (8k train) | nli_alternatives §3 + domain_A_feasibility §4 | R6 (NLI fine-tune dataset reference) | ✓ HF dataset | Polish entailment 10k pairs; image captions domain (NIE legal — domain shift caveat) |
| sileod tasksource NLI | sileod *mdeberta-v3-base-tasksource-nli.* HF, Apache 2.0 | nli_alternatives §2 | R6 ablation alternative | ✓ HF | Multi-task trained na 30 datasets; multilingual including PL |
| izaitova HerBERT-NLI ⚠ | izaitova *herbert-large-cased_nli.* HF, CC-BY-4.0, val acc 0.77 | nli_alternatives §3 | NIE używać (anti-rec) | ⚠ reproducibility risk | Tylko 6 downloads/mo; training data UNKNOWN; **Magda decision: NIE używać** |
| KLEJ Rybak 2020 | Rybak P., Mroczkowski R., Tracz J., Gawlik I. (2020) *KLEJ: Comprehensive Benchmark for Polish Language Understanding.* ACL 2020, arXiv:2005.00630 | literature_deep §5.5 ref 64 + halu_detection_sota §5.1 | R2 §2.7 + R6 (KLEJ leaderboard reference) | ✓ ACL 2020 | 9 PL NLU tasks foundational benchmark; CDSC-E task w środku |
| sdadas polish-nli (NIE istnieje) | (NEGATIVE FINDING) sdadas/polish-nli — sprawdzono HF, nie istnieje. Phantom citation z poprzedniego research (round 1 omyłkowo). | nli_alternatives §3 + domain_A_feasibility §4 | citation_hygiene — usuń z R2 jeśli była | ❌ phantom | **NIE istnieje na HF** — usuń z R2 jeśli przemknęła; alternative: mDeBERTa multilingual |
| Sieczkowska factivity 2023 | Sieczkowska A. et al. (2023) *Polish Natural Language Inference and Factivity — an Expert-based Dataset and Benchmarks.* Cambridge JNLE, arXiv:2201.03521 | literature_deep §5.5 ref 63 | R2 §2.6 (PL NLI niche) | ✓ Cambridge JNLE | 2,432 verb-complement pairs; BERT factivity F1 ~0.89-0.91; lingwistyka, NIE legal |

---

## Bucket D: Citation grounding / faithfulness

| Ref | Citation full | Source file | v3.2 chapter | Verify status | Contribution |
|---|---|---|---|---|---|
| Wallat 2025 faithfulness | Wallat J., Heuss F., Yates A., Anand A. (2025) *Correctness is not Faithfulness in Retrieval Augmented Generation Attributions.* ICTIR 2025, arXiv:2412.18004. doi:10.1145/3731120.3744592 | literature_deep §0.4 + §2.7 ref 31 | R1 §1.2 + R2 §2.3 + R7 (CRITICAL — 2-metric framework) | ✓ ICTIR 2025 | Distinction correctness vs faithfulness; **57% citations post-rationalized** w real systems → autorka MUSI mierzyć obie metryki |
| ContextCite MIT 2024 | Cohen-Wang B., Shah H., Madry A. (2024) *ContextCite: Attributing Model Generation to Context.* MIT CSAIL, arXiv:2409.00729. gradientscience.org/contextcite | literature_deep §0 + §2.7 ref 27 | R2 §2.3 + R6 (post-hoc multi-granular attribution) | ✓ NeurIPS 2024 | Post-hoc attribution analysis, multi-granular; potencjalna faithfulness measurement methodology |
| RAGAS Es 2024 | Es S., James J., Anke L., Schockaert S. (2024) *RAGAS: Automated Evaluation of Retrieval Augmented Generation.* EACL 2024 | (referenced multiple files) | R7 (CORE — primary eval framework, already in stack) | ✓ EACL 2024 | Faithfulness, context_precision/recall, answer_relevancy metrics — CORE w autorka eval stack |
| Self-RAG Asai 2024 | Asai A., Wu Z., Wang Y., Sil A., Hajishirzi H. (2024) *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.* ICLR 2024, arXiv:2310.11511 | (mentioned v3.2 dodatki) | R2 §2.3 (self-reflection methodology) | ✓ ICLR 2024 | Self-reflection retrieval-augmented generation; alternative methodology dla generation-time citation |
| Generation-Time vs Post-hoc 2025 | (Authors) (2025) *Generation-Time vs. Post-hoc Citation: A Holistic Evaluation of LLM Attribution.* arXiv:2509.21557 | literature_deep §0 + §2.7 ref 30 | R5 + R6 (hybrid G-Cite/P-Cite design rationale) | 🟡 arXiv 2025-09 | G-Cite vs P-Cite porównanie na 4 datasetach; key trade-off generation-time vs post-hoc |
| LongCite 2024 | (Authors) (2024) *LongCite: Enabling LLMs to Generate Fine-grained Citations in Long-Context QA.* arXiv:2409.02897 | literature_deep §2.1 + §5.3 ref 29 | R2 §2.3 (sentence-level citation method) | 🟡 arXiv | Trained model dla fine-grained sentence-level citations; EN-only, methodology adaptable |
| CiteGuard 2025 | (Authors) (2025) *CiteGuard: Faithful Citation Attribution for LLMs via Retrieval-Augmented Validation.* arXiv:2510.17853 | literature_deep §2.1 + §5.3 ref 33 | R2 §2.3 (post-hoc verification method) | 🟡 arXiv | Retrieval-augmented validation post-hoc; polish-friendly methodology |
| Concise Sub-Sentence 2025 | (Authors) (2025) *Concise and Sufficient Sub-Sentence Citations for Retrieval-Augmented Generation.* arXiv:2509.20859 | literature_deep §2.3 + §5.3 ref 34 | R2 §2.3 + R6 (sub-sentence citation granularity) | 🟡 arXiv | Span-level citation methodology — claim decomposition + per-claim attribution |
| Cite-While-You-Generate 2026 | (Authors) (2026) *Cite-While-You-Generate: Training-Free Evidence Attribution for Multimodal Clinical Summarization.* arXiv:2601.16397 | literature_deep §2.3 + §5.3 ref 36 | R2 §2.3 (token-level attribution alternative) | 🟡 arXiv 2026-01 | Decoder-attention-based, training-free; token-level |
| FaithBench 2024 | Bao F., Li X. et al. (2024) *FaithBench: A Diverse Hallucination Benchmark for Summarization by Modern LLMs.* arXiv:2410.13210, NAACL 2025 short. github.com/vectara/FaithBench | literature_deep §5.3 ref 38 | R7 (summarization halu benchmark reference) | ✓ NAACL 2025 short | Summarization hallucination benchmark; complement do FaithJudge |
| CAQA 2025 | (Authors) (2025) *Can LLMs Evaluate Complex Attribution in QA? Automatic Evaluation via CAQA Benchmark.* ACL 2025, aclanthology 2025.acl-long.837 | literature_deep §5.3 ref 32 | R7 | 🟡 ACL 2025 | Automatic evaluation complex attribution w QA |
| Cite Pretrain 2025 | (Authors) (2025) *Cite Pretrain: Retrieval-Free Knowledge Attribution for Large Language Models.* arXiv:2506.17585 | literature_deep §2.6 + §5.3 ref 35 | R8 future work (out of scope) | 🟡 arXiv | Training-time citation methodology — pretraining custom corpus; OOSCOPE dla autorki |

---

## Bucket E: Polish LLM ecosystem 2024-2026

| Ref | Citation full | Source file | v3.2 chapter | Verify status | Contribution |
|---|---|---|---|---|---|
| Bielik 11B v3 | The Bielik LLM Team (2025/2026) *Bielik 11B v3: Multilingual Large Language Model for European Languages.* arXiv:2601.11579 | literature_deep §5.5 ref 52 + bielik_tools §1 | R1 §1.1 + R2 §2.7 + R6 (CORE — primary generator + probe target) | ✓ verified 2026-05-16 | **CORE generator + probe target w v3.2;** 50L × 4096 hidden; APT4 tokenizer; Apache 2.0 |
| Bielik v3 APT4 tokenizer | Ociepa K., Flis Ł., Kinas R., Wróbel K., Gwoździej A. (2026) *Advancing Polish Language Modeling through Tokenizer Optimization in the Bielik v3 7B and 11B Series.* arXiv:2604.10799 | literature_deep §5.5 ref 53 + bielik_tools §1 | R6 (tokenizer details — APT4 fertility 1.62 vs 3.22) | ✓ verified 2026-05-16 | APT4 tokenizer optimization; -15% input tokens dla polish vs Mistral default |
| Bielik 11B v2 tech | The Bielik LLM Team (Ociepa K., Flis Ł., Kinas R., Wróbel K., Gwoździej A. et al.) (2025) *Bielik 11B v2 Technical Report.* arXiv:2505.02410 | literature_deep §5.5 ref 50 | R6 (lineage) | ✓ verified | v2 baseline historical reference |
| Bielik v3 Small | The Bielik LLM Team (2025) *Bielik v3 Small: Technical Report.* arXiv:2505.02550 | literature_deep §5.5 ref 51 | R6 (fallback model option) | ✓ | Bielik 1.5B + 4.5B variants; rapid iteration option dla local CPU dev |
| Bielik 7B v0.1 | (Bielik team) (2024) *Bielik 7B v0.1.* arXiv:2410.18565 | large_llm §1 | R6 (lineage) | 🟡 | Foundational Bielik (superseded by v2/v3) |
| Bielik Guard 2026 | The Bielik LLM Team (2026) *Bielik Guard: Efficient Polish Language Safety Classifiers for LLM Content Moderation.* arXiv:2602.07954 | literature_deep §5.5 ref 62 + halu_detection_sota §5.1 | R2 §2.7 (safety NIE faithfulness — distinction) | 🟡 arXiv 2026-02 | 0.1B + 0.5B safety classifiers, F1 0.785-0.791 — **safety, NIE faithfulness** (distinction!) |
| PLLuM family Kocoń 2025 | Kocoń J. et al. (PLLuM consortium) (2025) *PLLuM: A Family of Polish Large Language Models.* arXiv:2511.03823 | literature_deep §5.5 ref 48 | R2 §2.7 + R6 (judge candidate) | ✓ verified 2026-05-16 | 8B-70B family Llama/Mistral CPT; **PLLuM-12B kandydat na judge** |
| PLLuM Instruction Corpus | Pzik A. et al. (2025) *The PLLuM Instruction Corpus.* arXiv:2511.17161 | literature_deep §5.5 ref 49 | R6 (instruction dataset reference) | 🟡 arXiv 2025-11 | Functional typology of organic + converted + synthetic instructions |
| Llama-PLLuM 70B | CYFRAGOVPL (2025) *Llama-PLLuM-70B-instruct.* HF CYFRAGOVPL/Llama-PLLuM-70B-instruct | large_llm §4 + literature_deep §4.1 | R6 alt comparison (out of compute scope, mention) | ✓ HF | 74 PLCC, 8.05 MT-Bench; **140 GB bf16 — out of lab compute** |
| Qwen 3.5 Medium | Alibaba Cloud (2026-02) *Qwen 3.5 Medium.* HF Qwen/Qwen3.5-27B | large_llm §2 | R6 ablation (multi-model probe comparison) | ✓ HF | 36 layers × 6144 hidden; Apache 2.0; **secondary probe target opcjonalnie** |
| Gemma 3 27B | Google AI (2025-03) *Gemma 3.* ai.google.dev/gemma | large_llm §3 | R6 alt (Gemma judge candidate) | ✓ Google AI | 46 layers × 4096; alternating local/global attention; **Gemma Terms of Use restrictive** |
| Gemma 4 31B | Google AI (2026-04) *Gemma 4 31B dense + 26B-A4B MoE.* ai.google.dev/gemma | large_llm §3 | R6 alt | 🟡 2026-04 | Apache 2.0 (NEW — switched from Gemma Terms!); multimodal text+image+video |
| BGE-M3 | Chen J. et al. (2024) *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings.* arXiv:2402.03216 | (multiple files) | R5 + R6 (CORE — embedder dla retrieval) | ✓ verified | Multilingual including Polish; CORE w autorka stack |
| sdadas mmlw retrieval | Dadas S. *mmlw-retrieval-roberta-large.* HF sdadas/mmlw-retrieval-roberta-large | literature_deep §4.2 | R6 (alternative polish embedder) | ✓ HF | Best na PIRB w 2024; Polish RoBERTa Large + distillation |
| sdadas stella-pl-retrieval | Dadas S. *stella-pl-retrieval.* HF | literature_deep §4.2 | R6 alt | ✓ HF | Tuned for IR, 1.4M queries trained; 1024-dim |
| sdadas polish-reranker-roberta-v3 | Dadas S. *polish-reranker-roberta-v3.* HF | literature_deep §4.2 + bielik_tools §5 | R5 (optional component, 8192 ctx) | ✓ HF | 8192 token context; PIRB 65.17; bije Qwen3-Reranker-8B w 18/41 tasks z 5% params |
| LLMzSzŁ 2025 | Jassem K. et al. (2025) *LLMzSzŁ: A Comprehensive LLM Benchmark for Polish.* arXiv:2501.02266 | literature_deep §5.5 ref 59 + halu_detection_sota §5.1 | R2 §2.7 (PL benchmark reference) | 🟡 arXiv 2025-01 | First comprehensive PL LLM benchmark at scale; Polish national exams; 154 domains 19k closed Qs |
| PIRB Dadas 2024 | Dadas S., Perełkiewicz M., Poświata R. (2024) *PIRB: A Comprehensive Benchmark of Polish Dense and Hybrid Text Retrieval Methods.* LREC-COLING 2024, arXiv:2402.13350 | literature_deep §5.5 ref 54 + poleval_2026 §3 | R2 §2.7 (CORE retrieval baseline) | ✓ LREC-COLING 2024 | 41 IR tasks Polish (medicine, law, business); CORE retrieval baseline |
| PL-MTEB 2024 | Poświata R., Dadas S., Perełkiewicz M. (2024) *PL-MTEB: Polish Massive Text Embedding Benchmark.* arXiv:2405.10138 | literature_deep §5.5 ref 55 | R2 §2.7 | 🟡 arXiv 2024-05 | 30 NLU+IR tasks; comprehensive PL embedding eval |
| PolQA Rybak 2024 | Rybak P., Przybyła P. (2024) *PolQA: Polish Question Answering Dataset.* LREC-COLING 2024, arXiv:2212.08897 | literature_deep §5.5 ref 56 + halu_detection_sota §5.1 | R2 §2.7 + R3 (corpus reference) | ✓ LREC-COLING 2024 | Largest open-domain PL QA — 7k Q + 87.5K passages + 7M corpus; **perfect retrieval baseline** |
| MAUPQA Rybak 2023 | Rybak P. (2023) *MAUPQA: Massive Automatically-created Polish Question Answering Dataset.* arXiv:2305.05486 | literature_deep §5.5 ref 57 + halu_detection_sota §5.1 | R3 | 🟡 arXiv 2023-05 | ~400K Q-passage pairs multi-source |
| PoQuAD Tuora 2023 | Tuora R. et al. (2023) *PoQuAD — The Polish Question Answering Dataset.* KCAP 2023, doi:10.1145/3587259.3627548 | literature_deep §5.5 ref 58 | R3 | ✓ KCAP 2023 | 70K Q-A pairs PL Wikipedia; impossible questions feature — repurposable dla abstain test |
| PLCC Dadas 2025 | Dadas S. (2025) *Evaluating Polish Linguistic and Cultural Competency in Large Language Models (PLCC).* arXiv:2503.00995 | literature_deep §5.5 ref 60 | R2 §2.7 + R7 (PL cultural eval reference) | 🟡 arXiv 2025-03 | 600 manual Qs; 6 categories deterministic rule-based eval (NIE LLM judge) |
| PL-Guard 2025 | Krasnodębska A., Seweryn K., Łukasik A., Kusa M. (2025) *PL-Guard: Benchmarking Language Model Safety for Polish.* arXiv:2506.16322 | literature_deep §5.5 ref 61 | R2 §2.7 (safety distinction) | 🟡 arXiv 2025-06 | Safety NIE faithfulness; HerBERT > Llama-Guard-3-8B + PLLuM under adversarial |
| Outlines library | dottxt-ai team (active 2025) *Outlines — Constrained Generation Library.* github.com/dottxt-ai/outlines, v1.3.0 (2026-05-13) | bielik_tools §3-4 + literature_deep §2.4 | R5 (CORE — structured citation output) | ✓ active OSS | Constrained decoding (FSM/regex); 97% RAG success rate (Uğur 2025); **CORE w v3.2 stack** |
| Instructor library | instructor-ai team (active 2025) *Instructor — Pydantic-based LLM Validation.* github.com/instructor-ai/instructor, v1.15.1 | bielik_tools §3 | R5 (alternative wrapper) | ✓ active OSS | Pydantic-first validation + auto-retry; brak natywnego vLLM provider — workaround needed |
| xgrammar | mlc-ai team (active 2026) *xgrammar.* github.com/mlc-ai/xgrammar, v0.2.0 | bielik_tools §4 | R5 alternative | ✓ active OSS | vLLM/SGLang default; 3.5-14× szybsze niż Outlines ALE 60-78% RAG success rate (vs Outlines 97%) |
| Uğur 2025 RAG benchmark | Uğur et al. (2025) *Guided Decoding and Its Critical Role in Retrieval-Augmented Generation.* arXiv:2509.06631 | bielik_tools §4 + sources | R6 (CORE — Outlines vs xgrammar empirical benchmark) | 🟡 arXiv 2025-09 | **Jedyne real benchmark Outlines vs xgrammar vs LMFE dla RAG**; MUST CITE w R6/R7 |
| LlamaIndex CitationQueryEngine | LlamaIndex (active 2025) *CitationQueryEngine Documentation.* docs.llamaindex.ai/en/stable/examples/query_engine/citation_query_engine | literature_deep §2.5 + §5.6 ref 70 | R5 (CORE — RAG framework citation engine) | ✓ active OSS | Native in-line citations based na source nodes; 40% szybsze retrieval vs LangChain |
| BAML BoundaryML | BoundaryML team (active 2025) *BAML — Schema-Aligned Parsing.* glukhov.org/post/2025/12/baml-vs-instruct-for-structured-output | bielik_tools §2.4 + literature_deep §5.6 ref 71 | R5 alternative DSL | ✓ active OSS | DSL + Schema-Aligned Parsing — tolerates messy output (markdown w JSON, trailing commas) |
| mGarbowski llm-projekt | mGarbowski (2024-2025) *llm-projekt — Polish RAG z Bielik 1.5B + bracket citations.* github.com/mGarbowski/llm-projekt | bielik_tools §5 | R2 §2.3 + R8 defense (DIRECT PRIOR ART — wyróżnij kontrybucję) | ✓ GitHub | **DIRECT PRIOR ART** dla autorka — Polish RAG z bracket citations + Bielik 1.5B v3 + polish-reranker-roberta-v3; **MUST cite w R2 + wyróżnij kontrybucję w R8** |
| Bielik tools repo | SpeakLeash (active 2026) *bielik-tools.* github.com/speakleash/bielik-tools (32★, last commit 2026-04-20) | bielik_tools §1 | R5 (vLLM tool parsers, structured output examples) | ✓ active OSS | Enhanced chat template + vLLM tool parsers per wersja (0.12/0.13/0.15+); structured_output examples |
| SpeakLeash bielik-papers | SpeakLeash (2026) *bielik-papers repo z v3, v3_pl, v3_small folderami.* github.com/speakleash/bielik-papers | bielik_tools §1 | R6 (technical reports source) | ✓ active OSS | Folders zawierają technical reports cite-able dla R6 |

---

## Bucket F: Polish legal/consumer NLP

| Ref | Citation full | Source file | v3.2 chapter | Verify status | Contribution |
|---|---|---|---|---|---|
| ELI API Sejm | Sejm Chancellery (2014+) *ELI — European Legislation Identifier API.* api.sejm.gov.pl/eli | domain_A_feasibility §1 | R3 (CORE — corpus scrape methodology) | ✓ verified scrape 2026-05-16 | **GOLDMINE** — deterministic URL-based citation; ustawy konsumenckie + KC art. 535-581 |
| Ustawa o prawach konsumenta | Sejm RP (2014) *Ustawa z 30.05.2014 o prawach konsumenta.* Dz.U. 2014/827, jednolity tekst Dz.U. 2020/287 [PL source] | domain_A_feasibility §1 | R3 (CORE — primary corpus source) | ✓ verified | Primary corpus dla v3.2 RAG; ~58 artykułów |
| Kodeks Cywilny | Sejm RP (1964) *Ustawa z 23.04.1964 Kodeks cywilny.* Dz.U. 1964/93, art. 535-581 (sprzedaż, rękojmia, gwarancja) [PL source] | domain_A_feasibility §1 | R3 (CORE — secondary corpus source) | ✓ verified | 1088 artykułów total; art. 535-581 specific dla consumer rights |
| Omnibus Dyrektywa PL | Sejm RP (2022) *Nowelizacja "Omnibus".* Dz.U. 2022/2581 (wdrożona 1.12.2022) [PL source] | query_patterns §7.1 | R2 §2.7 + R3 (terminology evolution 2023+) | ✓ verified | Transparency cen, fake reviews, dark patterns; krytyczna terminology change post-2023 |
| EU Consumer Rights Directive | EU Parliament (2011) *Consumer Rights Directive 2011/83/EU* + amendments → polish UPC | literature_deep §3.5 | R3 (EU framework reference) | ✓ verified | EU framework dla polish consumer law |
| EU Modernisation Directive | EU (2019) *Modernisation Directive 2019/2161 → polish "Omnibus" implementation* | literature_deep §3.5 | R3 + R8 | ✓ verified | Source dla DARK patterns regulations |
| UOKiK Q&A prawakonsumenta.uokik.gov.pl | UOKiK (active 2025+) *Pytania i odpowiedzi prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/* [PL source] | domain_A_feasibility §2 + query_patterns §10 | R3 (CORE — gold standard ~50-200 par) | ✓ verified scrape | **JACKPOT** — UOKiK *sam* generuje (q, a, citation) pairs jako mission edukacyjna; gotowy gold standard |
| UOKiK ARBUZ AI tool | UOKiK + OPI PIB (2020-2023) *ARBUZ — Detection of abusive clauses w B2C contracts.* Operational od 2023-01-01. Per Artif Intell Law 2024, doi:10.1007/s10506-024-09408-8 | literature_deep §3.4 + §5.4 ref 47 | R2 §2.7 (legal NLP polish prior art) | 🟡 Springer 2024 | Polish legal NLP prior art; CITE jako "polish legal AI exists ale nie halu" |
| ECC Polska 2024 | ECC Polska (2024) *Raport 2024 cross-border consumer cases.* konsument.gov.pl/wp-content/uploads/2025/02/Raport-ECK-2024 [PL source] | query_patterns §1.1 + §10 | R4 (consumer query pattern stats) | ✓ verified | 5,578 cases 2024; ~50% lotnictwo; query distribution stats |
| Polish TDM exception 2024 | Sejm RP (2024) *Amendment Polish Copyright Act implementing EU DSM Directive.* Dz.U. wdrożona 20.09.2024 [PL source] | literature_deep §3.4 | R3 (legal basis dla scraping ISAP+UOKiK) | ✓ verified | **Strong legal basis** dla scraping ISAP + UOKiK — pozwala na TDM dla research/public interest |
| LRAGE Legal RAG eval 2025 | (Authors) (2025) *LRAGE: Legal Retrieval Augmented Generation Evaluation Tool.* arXiv:2504.01840 | literature_deep §3.1 + §5.4 ref 40 | R7 (legal RAG eval framework reference) | 🟡 arXiv 2025-04 | Open-source GUI+CLI eval framework dla legal RAG |
| Bridging Legal Knowledge Barron 2025 | Barron R. C., Eren M. E., Serafimova O. M., Matuszek C., Alexandrov B. S. (2025) *Bridging Legal Knowledge and AI: RAG with Vector Stores, Knowledge Graphs, and HNMFk.* ICAIL 2025, arXiv:2502.20364, doi:10.1145/3769126.3769215 | literature_deep §0 + §3.1 ref 41 | R2 §2.3 (legal RAG methodology) | 🟡 ICAIL 2025 | Full pipeline NM statutes + constitution + case law; HNMFk topic modeling + KG + RAG |
| SAT-Graph RAG Legal Norms 2025 | (Authors) (2025) *An Ontology-Driven Graph RAG for Legal Norms: A Hierarchical, Temporal, and Deterministic Approach.* arXiv:2505.00039 (v5) | literature_deep §0 + §3.1 ref 42 | R5 (chunking strategy for ISAP) | 🟡 arXiv | Structure-aware semantic segmentation; LRMoo-inspired temporal versioning; **dla autorka adaptable na ISAP** |
| LexRAG Legal Multi-Turn 2025 | CSHaitao (2025) *LexRAG: Multi-Turn Legal Retrieval.* arXiv:2502.20640 + github.com/CSHaitao/LexRAG | query_patterns §3.2 + §10 | R7 (legal retrieval baseline benchmark) | 🟡 arXiv 2025-02 | Recall@10 ≈ 33% nawet z LLM rewriting — realistic baseline expectation dla legal retrieval |
| LEGRA Polish 2025 | (Authors) (2025) *LEGRA: Polish Court Rulings GraphRAG.* preprints.org/manuscript/202511.1742 [PL source] | query_patterns §3.1 + §10 | R8 future work (GraphRAG dla ISAP) | 🟡 preprint 2025-11 | Polish court rulings GraphRAG — same direction, scope different |
| Stanford Legal Retrieval 2025 | Zheng et al. Stanford (2025) *Legal Retrieval Benchmark.* dho.stanford.edu/wp-content/uploads/Legal_Retrieval.pdf | query_patterns §3.2 + §10 | R6 (legal-issue-spotting prompt insight) | 🟡 Stanford | Structured legal reasoning query expansion outperforms naive query expansion |
| Pushshift Reddit dump | Academic Torrents (active) *Pushshift Reddit dump 2005-06 → 2025-06.* ~3.4 TB NDJSON+zstd | domain_A_feasibility §3 | R3 (data scrape methodology) | ✓ active | Top-40k subreddits selektywnie; **mitigation dla zablokowanego Reddit API** |
| AggTruth duplicate (Wrocław Tech) | Matys P. et al. (2025) — see Bucket A | poleval_2026 §5 | (cross-ref Bucket A) | 🟡 ICCS 2025 | **Główny potential konkurent** dla polish halu — mają CLARIN-PL grant 2024-2026 |

---

## Bucket G: MLOps/LLMOps modern

| Ref | Citation full | Source file | v3.2 chapter | Verify status | Contribution |
|---|---|---|---|---|---|
| Langfuse | Langfuse team (active 2025) *Langfuse — LLM observability.* langfuse.com, v3.x | halu_detection_sota §4 + (referenced multiple) | R5 + R7 (CORE — observability w stack) | ✓ active OSS | Multilingual; observability + LLM-as-judge tooling; **w stacku autorki** |
| Cleanlab TLM 2025 | Cleanlab (2025) *Trustworthy Language Model (TLM) Documentation.* help.cleanlab.ai/tlm | halu_detection_sota §4 + literature_deep §5.6 ref 65 | R7 (commercial halu detection reference) | ✓ active commercial | Combo self-reflection + sampled-consistency + probabilistic measures |
| Galileo Luna v1/v2 | Galileo (2025) *Luna v1/v2 — DeBERTa-large 440M halu detector.* | halu_detection_sota §4 | R7 (commercial reference) | 🟡 commercial | DeBERTa-large 440M fine-tuned, sub-200ms latency |
| Arize Phoenix | Arize AI (active 2025) *Phoenix — observability.* | halu_detection_sota §4 | R5 alternative | ✓ Apache 2.0 | Multilingual; observability + tracing focus |
| RAGAS framework | Es S. et al. (2024) RAGAS — see Bucket D | (multiple) | R7 (CORE eval framework) | ✓ EACL 2024 | Already CORE w autorka stack |
| DeepEval | Confident AI (active 2025) *DeepEval — pytest integration RAG eval.* | halu_detection_sota §4 | R7 alternative | ✓ Apache 2.0 | Multilingual via LLM; pytest integration |
| TruLens | TruLens (active 2025) *TruLens — RAG triad.* | halu_detection_sota §4 | R7 alternative | ✓ MIT | Context relevance, groundedness, answer relevance |
| NeMo Guardrails | NVIDIA (active 2025) *NeMo Guardrails.* | halu_detection_sota §4 | R5 alternative | ✓ Apache 2.0 | Lynx integration na lipiec 2024 |
| vLLM + structured outputs | vLLM project (2025-2026) *vLLM structured outputs.* docs.vllm.ai/en/latest/features/structured_outputs.html, v0.15+ | bielik_tools §4 | R5 (CORE serving + structured output) | ✓ active OSS | API change v0.12: `guided_json` → `structured_outputs.json` |
| SGLang | LMSYS team (active 2025) *SGLang.* docs.sglang.io | bielik_tools §1 | R5 (alternative serving) | ✓ active OSS | Default xgrammar; opt-in Outlines/llguidance; **Bielik v3 wprost dokumentowany** |

---

## Bucket M: Co NIE było w v3.1 a jest CRITICAL w v3.2 (top 15)

Lista **must-cite** refs dla R2 v3.2 — **bez nich praca nie obroni się przed Kojałowicz**. Wszystkie te pozycje były w research/*.md ALE NIE w v3.1 R1+R2 mining (round 1) bo dotyczą halu detection / citation grounding które NIE było scope v3.1.

| # | Ref | Dlaczego CRITICAL dla v3.2 defense |
|---|---|---|
| 1 | **Farquhar 2024 Nature** semantic entropy | Foundational — bez tego R2 §2.5 nie ma anchoring point dla halu detection methodology lineage |
| 2 | **Kossen 2024 SEP** | Probe lineage continuation — semantic entropy → SEP → Real-Time Probe (Obeso) → autorka linear probe; bez SEP nie da się obronić "linear probe na hidden states to mainstream 2025" |
| 3 | **Obeso 2025 Real-Time Probes** + obalcells repo | **Direct implementation reference** — autorka forkuje ten repo, AUC 0.89-0.90 baseline; bez niego nie ma defensible starting point dla R5 architecture |
| 4 | **Dubanowska 2025 OOD-fail** EMNLP Findings | **CRITICAL defensive ref** — Kojałowicz zapyta "dlaczego twój probe miałby działać OOD?" → autorka cytuje Dubanowska "OOD jest aktualnie OUT OF REACH dla wszystkich SOTA, my reportujemy honest in-distribution" |
| 5 | **Vaddi 2026 H-Neurons cross-domain** | **Wzmacnia polish-specific argument** — H-neurons NIE generalizują cross-domain (0.78→0.56); polish-specific NIE bug, feature; bez tego "po co polish probe" trudno obronić |
| 6 | **Wallat 2025 ICTIR faithfulness vs correctness** | **CORE 2-metric framework dla R7** — bez Wallat distinction, autorka miałaby tylko correctness (NIE wystarczy dla defense); 57% post-rationalized citations = strong motivator dla obu metryk |
| 7 | **Mu-SHROOM SemEval 2025** (Vázquez et al.) | **CORE polish gap evidence** — 14 langs bez PL; first-mover argument dla DEC-003; bez tego "dlaczego polish?" jest weak |
| 8 | **AggTruth Wrocław Tech 2025** ICCS | **First-mover defense** — pokazujesz że znasz polish landscape, główny competitor English-only; carve out polish niche |
| 9 | **mDeBERTa MoritzLaurer 2mil7** model card | **Primary verifier model** — bez precyzyjnego cite (MIT, 27 langs, 105k PL pairs) nie da się obronić wyboru NLI |
| 10 | **Mirage of Halu Detection 2025** Kulkarni Apple EMNLP | **Methodology critique reference** — autorka explicit address tej krytyki w R7 ("ROUGE eval przeszacowuje, używamy human-grounded eval") |
| 11 | **Bielik 11B v3 arXiv:2601.11579** | CORE generator + probe target — bez precyzyjnego tech report cite (50L × 4096, APT4 tokenizer) nie obrona R6 |
| 12 | **PIRB Dadas 2024** LREC-COLING | **Polish retrieval baseline** — bez PIRB nie ma comparison point dla retrieval quality; 41 IR tasks legal/medical |
| 13 | **mGarbowski/llm-projekt** | **DIRECT PRIOR ART defense** — Kojałowicz/recenzent znajdzie ten projekt na GitHub; **MUST cite + explicit wyróżnij kontrybucję** (Bielik 11B vs 1.5B; full thesis vs toy; cross-register; halu probe) |
| 14 | **Outlines + Uğur 2025 RAG benchmark** | **Decision rationale dla structured output** — Outlines vs xgrammar (97% vs 60-78% RAG success); bez Uğur 2025 wybór Outlines wygląda na arbitrary |
| 15 | **PLLuM Kocoń 2025 arXiv:2511.03823** | Judge candidate alternative — government-backed Polish LLM; cite jako "alternative judge model considered, decision rationale w DEC-X" |

**Bonus (16-20) ⭐ jeśli budżet czasu pozwala:**
- **ContextCite Cohen-Wang 2024** MIT — multi-granular post-hoc attribution (faithfulness measurement methodology)
- **FaithJudge Vectara 2025** — LLM-as-judge framework reference dla R6
- **Lynx Patronus 2024** — multilingual halu baseline dla R7 comparison
- **CCPS 2025** — calibration enhancement (Iter. 3 ablation)
- **HalluLens Meta 2025** — extrinsic vs intrinsic taxonomy
- **APT4 Bielik tokenizer 2026 arXiv:2604.10799** — krytyczne dla R6 modele defense polish-specific tokenization

---

## Bucket N: Polish-specific gap papers (first-mover defense)

**Cel:** dokumentacja że Polish halu detection / faithfulness eval NIE istnieje publicznie. Te refs używane w **R1 §1.2 Motywacja** + **R8 Wnioski** jako evidence że autorka wypełnia faktyczną lukę.

| Ref | Co dokumentuje (PL gap) | Source verification |
|---|---|---|
| **Mu-SHROOM 2025** (Vázquez et al. arXiv:2504.11975) | **14 języków halu detection benchmark, POLSKI POMINIĘTY** (AR, BS, CA, ZH, CS, EN, FA, FI, FR, DE, HI, IT, ES, SV) | poleval_2026 §4 + halu_detection_sota §1 — verified Helsinki-NLP/mu-shroom official |
| **MultiHal 2025** (Vatsal et al. arXiv:2505.14101) | **5 EU lang KG-grounded halu (DE, IT, FR, PT, ES + EN), POLSKI BRAK** | poleval_2026 §4 + halu_detection_sota §6.3 |
| **AggTruth 2025** (Matys et al. ICCS, arXiv:2506.18628) | **Wrocław Tech CLARIN-PL grant halu detection ENGLISH-only** (NQ, HotPotQA, CNN/DM, XSum) — naturalny next step polish ALE jeszcze NIE zrobiony | poleval_2026 §5 |
| **PolEval 2017-2025 (8 edycji)** | **Zero halu/faithfulness/RAG-end-to-end tasków** w 8 edycjach; PolEval 2025 = 4 taski (MGT detection, gender bias, layout, speech emotion) — żaden o halu | poleval_2026 §2 — verified poleval.pl |
| **HHEM Vectara EN-only (open variant)** | HHEM 2.1 EN/DE/FR; HHEM 2.3 ma 11 langs ALE polish status 🟡 (sprawdzić) | halu_detection_sota §4 |
| **Lynx Patronus EN-only** | 8B/70B EN-only; brak polish-fine-tuned faithfulness scorer | halu_detection_sota §4 + literature_deep §5.1 ref 6 |
| **Multilingual TruthfulQA HiTZ 2025** (arXiv:2502.09387) | **EU + CA + GL + ES + EN, POLSKI BRAK** | poleval_2026 §4 |
| **HalluHard 2026** (arXiv:2602.01031) | **English-only multi-turn medical/legal/research/code** — kolejny brakuje PL | poleval_2026 §4 |
| **TruthfulQA-PL** | **NIE ISTNIEJE** — brak professional translation TruthfulQA do polish | poleval_2026 §4 |
| **Polish HaluBench-equivalent** | **BRAK** — żaden lab w Polsce nie zwołał Patronus-style modelu | halu_detection_sota §5.2 |
| **Polish-fine-tuned faithfulness scorer (Lynx-equivalent)** | **BRAK** | halu_detection_sota §5.2 |
| **Polish hidden-states halu probe** | **0 publikacji** — verified search "Bielik" / "PLLuM" probing classifier hallucination zwraca 0 wyników; **first-mover potential HIGH** | probes_polish §1 |
| **Polish LegalBERT-equivalent** | **BRAK** (LegalBERT to EN-only per iliaschalkidis homepage) | literature_deep §3.4 |
| **Polish legal NER comprehensive** | **BRAK** (spaCy-pl ma generic, NIE legal) | literature_deep §3.4 |
| **Polish legal NLI benchmark** | **BRAK** (CDSC-E general domain; Sieczkowska factivity = lingwistyka) | literature_deep §3.4 + §4.3 |
| **Polish ContractNLI-equivalent** | **BRAK** (Stanford ContractNLI = EN NDAs only) | literature_deep §3.4 |
| **Polish legal RAG benchmark** | **BRAK** | literature_deep §3.4 |
| **Polish citation grounding eval na statutes** | **BRAK** | literature_deep §3.4 |
| **Polish factuality / halu detection landscape** | **EMPTY SPACE** — Bielik/PLLuM tech reports wspominają eval (MMLU-pl, CPTUB tricky questions) ALE NIE dedicated faithfulness/halu eval | literature_deep §4.5 |

**Defense narrative consolidation (do R1 §1.2 + R8):**
> "Polish NLP landscape 2024-2026 jest dojrzały w generic LLM/embedding/QA (Bielik v3, PLLuM, sdadas stack), **ALE ma realne luki w faithfulness/halu detection**: Mu-SHROOM 2025 pomija polski (14 langs bez PL), PolEval 2017-2025 ma 0 halu tasków, MultiHal/HalluHard/Multilingual TruthfulQA pomijają polski, Wrocław Tech AggTruth English-only mimo CLARIN-PL grant, brak polish HaluBench/Lynx-equivalent, **0 publikacji hidden-states probes na polish LLM**. Praca dyplomowa wprost adresuje te luki w niche legal/consumer rights, leveraging strong polish stack jako baseline + adding faithfulness/citation/probe layer."

---

## Sumary statistics — round 2 mining

| Metryka | Wartość |
|---|---|
| **Total extracted refs (Buckets A-G)** | ~80 refs |
| **Unique modern (2024-2026) refs** | ~70 |
| **CRITICAL must-cite (Bucket M top 15)** | 15 |
| **Polish-specific gap papers (Bucket N)** | 19 |
| **Refs verified ✓ peer-reviewed** | ~25 |
| **Refs 🟡 needs verify before cite** | ~55 |
| **Polish-language sources [PL source]** | 6 (ELI API, UPK, KC, Omnibus, UOKiK Q&A, ECC Polska, LEGRA, TDM exception) |
| **Source files mined** | 9 plików, ~4200 LOC |
| **Total mining time est.** | ~25 min focused work |

**Top 5 critical missing z v3.1 (round 1) — ranked by defensibility impact:**
1. **Farquhar 2024 Nature semantic entropy** — bez tego cała halu detection lineage w R2 §2.5 wisi w powietrzu
2. **Wallat 2025 ICTIR faithfulness vs correctness** — bez 2-metric framework R7 nie obroni się
3. **Mu-SHROOM 2025** + AggTruth 2025 (paired) — bez polish gap evidence cała motywacja DEC-003 jest weak
4. **Obeso 2025 Real-Time Probes + obalcells repo** — bez direct implementation reference R5 architecture nie jest defensible
5. **mDeBERTa MoritzLaurer 2mil7** — bez precyzyjnego cite (MIT, 27 langs, 105k PL pairs) decyzja NLI verifier wygląda na arbitrary

**Action items dla autorki post-mining:**
- [ ] Re-verify wszystkie 🟡 refs przed włączeniem do bibliografii (uruchomić citation-checker subagent na R2 v3.2 draft)
- [ ] Wszystkie "Authors TBD" z literature_deep §5 — re-verify abstracts i wyciągnij autorów
- [ ] arXiv IDs w formacie 26XX (2026) — sprawdzić czy paper jest publicly available i nie został withdrawn
- [ ] Decision dla R5/R6: czy wybrać Outlines (97% RAG success) vs xgrammar (3.5-14× szybsze) — Iter. 0b POC
- [ ] Decision dla judge model: Bielik 11B vs PLLuM 12B vs Gemma 3 27B vs Claude Haiku — DEC w Iter. 0
- [ ] Cross-check Bucket N polish gap claims przed final R1 §1.2 motywacja write-up

---

## NLI models update 2026 (Magda 2026-05-16 leads)

**Trigger:** Magdy odkrycie nowych modeli/datasetów po DEC-003 pivot — request: czy aktualizować 3-tier NLI verifier strategy?
**Pełny research:** `D:\diplomma\thesis_research\research\nli_models_2026_update.md`

### TLDR (3 zdania)

1. **TRZYMAĆ current 3-tier plan** — żaden z 6 ocenianych modeli/datasetów (gliclass-multilang-ultra, gliclass-v3 collection, finecat-nli, ModernCE, EttinX, all-nli) nie pokonuje `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` dla polish citation grounding na łącznym kryterium polish coverage + license + battle-tested adoption (275k dl/mo, MIT).
2. **DODAĆ `knowledgator/gliclass-multilang-ultra` jako Tier 0 ablation w R7** — native multi-class output (1.7B params, Apache 2.0, 20 langs incl. PL) bezpośrednio maps na 6-poziomową taksonomię halu types z `CLAUDE.md` § Defense scaffolding. Komplementarne, NIE replacement.
3. **ZAPRZYJAŹNIĆ dleemiller methodology** — blog "Ways to use NLI cross-encoder" zawiera reusable patterns dla R2/R3/R5: hybrid scoring formula `0.5 * neutral + entailment - contradiction`, claim extraction guidelines (direct/unambiguous statements), NLI cross-encoder Swiss-Army-knife framing.

### Key findings

| # | Finding | Impact |
|---|---------|--------|
| 1 | `sdadas/polish-nli` NIE ISTNIEJE (verified) — phantom citation potwierdzony | Już prawidłowo w CLAUDE.md noted |
| 2 | gliclass-multilang-ultra: native multi-class halu typology = defensible R7 ablation | Dodać Tier 0 |
| 3 | finecat-nli-l: **license NIE specyfikowana** — red flag dla HF publication | NIE używać bez confirmation |
| 4 | all-nli dataset: English-only (SNLI+MultiNLI) — nieprzydatne dla polish fine-tune | Skip dla Tier 2 |
| 5 | FineCat-NLI methodology (knowledge distillation z DeBERTa-v3-large) reusable jako future work jeśli HerBERT Tier 2 zbyt wolny | R8 future work |
| 6 | dleemiller hybrid scoring formula → R5 verifier head + R6 verifier methodology | High-value cite |

### Stack proposed addition (CLAUDE.md § Stack)

```
+ knowledgator/gliclass-multilang-ultra (1.7B, Apache 2.0, 20 langs incl. PL)
+ — Tier 0 R7 ablation: native multi-class halu typology vs 2-step mDeBERTa NLI + LLM judge classify
```

### Time-to-execute estimate

~6-12h work total dla wariantu 1+2 (TRZYMAĆ + DODAĆ gliclass ablation):
- Update CLAUDE.md + 02_konspekt R7 sub-section: ~20 min
- Iter. 0b POC gliclass batch eval na CDSC-E 1k par + 100 manual gold: 5-10h
- R5 FIG-3 add hybrid scoring formula: ~30 min
- R3 add claim extraction guidelines: ~20 min

**NIE blocker.** NIE scope creep (exploratory sub-RQ, NIE modyfikacja 3 main + 2 supporting RQ).
