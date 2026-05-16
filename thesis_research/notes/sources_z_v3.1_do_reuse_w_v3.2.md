# Sources do reuse z v3.1 (R1+R2) → v3.2 (RAG halu detection)

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
