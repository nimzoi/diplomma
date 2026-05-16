# NLI models update 2026 — gliclass, FineCat-NLI, dleemiller methodology

**Data:** 2026-05-16
**Autor research:** Claude (deep research agent on Magda's request)
**Trigger:** Magdy odkrycie nowych modeli/datasetów po DEC-003 pivot — request: czy aktualizować 3-tier NLI verifier strategy?
**Powiązane:**
- `D:\diplomma\thesis_research\research\nli_alternatives_2026.md` (poprzedni research, v3.1 farma — większość reusable)
- `D:\diplomma\thesis_research\research\halu_detection_sota_2024_2026.md`
- `D:\diplomma\CLAUDE.md` § Stack (Tier 1 = `MoritzLaurer/mDeBERTa`, Tier 2 = HerBERT+CDSC-E, Tier 3 = LLM-judge)

---

## 1. TLDR (3 zdania)

**(1) TRZYMAĆ current 3-tier plan** — żaden z 6 ocenianych modeli/datasetów nie pokonuje `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` dla polish citation grounding na metrykach łącznie polish coverage + license + battle-tested adoption. **(2) DODAĆ `knowledgator/gliclass-multilang-ultra` jako Tier 0 (ablation experiment) w R7** — zero-shot multi-class jest komplementarny względem 3-class NLI i może obsłużyć N citation classes simultaneously, ale ~2B params (~6× większy od mDeBERTa) i Polish benchmark NIE jest separately reported w model cardzie (tylko "20 langs trained" + multilingual avg F1 0.56). **(3) ZAPRZYJAŹNIĆ dleemiller methodology** — blog "Ways to use NLI cross-encoder" zawiera bezpośrednio reusable patterns dla naszego R5 architecture (hybrid score formuła, claim verification mapping entailment→supported / contradiction→halu / neutral→unknown), wykorzystać jako citation w R2/R5 ale NIE wybierać `finecat-nli-l` jako Tier 1 (English-only, brak polish).

**Akcja:** zaktualizuj `CLAUDE.md` § Stack jednym zdaniem — dopisać "+gliclass-multilang-ultra jako Tier 0 ablation w R7" — i dodać `dleemiller/EttinX-nli-s` jako CPU baseline ablation (English-only ale 68M params = real CPU latency baseline).

---

## 2. Per-model analysis (6 ocenianych)

### 2.1 `knowledgator/gliclass-multilang-ultra`

**URL:** https://huggingface.co/knowledgator/gliclass-multilang-ultra

| Field | Value | Komentarz |
|-------|-------|-----------|
| Architecture | DeBERTa-based + CrossAttn Scorer | Per-label cross-attention pooling, unpadding + flash-attention optimization |
| Params | **~1.7B (2B params)** | **6× większy od mDeBERTa-v3-base (0.3B)** — VRAM cost concern |
| License | **Apache 2.0** ✅ | OK dla HF dataset publication (nie blokuje commercial) |
| Polish coverage | **TAK — explicit** w 20-lang training (PL, SV, NO, CS, LT, ET, LV, ES, FI, DE, FR, RO, IT, PT, NL, UK, HI, ZH, AR, HE) | Native polish, NIE machine-translated |
| Training data | tau/commonsense_qa + knowledgator/gliclass-v3-logic-dataset + BioMike/formal-logic-reasoning-gliclass-2k | Brak NLI-specific corpus (MNLI/SNLI/ANLI nie wymienione) — risk dla strict NLI use case |
| Benchmarks | English avg F1 **0.7212** (macro), multilingual avg F1 **0.5599** (6 datasets), evaluated na MASSIVE + SIB-200 — **polish per-language F1 NIE separately reported** | ⚠ Magda będzie musiała sama zmierzyć na polish CDSC-E lub własnym eval set |
| Throughput | **200.7 samples/sec @ batch=8, RTX PRO 6000** (1 label: 308.2 sps; 256 labels: 31.5 sps — **nearly flat** scaling) | Lepiej skaluje niż classic NLI (które degraduje linearnie z label count) |
| Downloads (last month) | 1,003 | Niska adopcja vs mDeBERTa (275k/mo) — risk reproducibility |
| Last update | 16 dni temu (2026-04-30 approx) | Active development |
| Paper | arXiv:2508.07662 (2025-08-11), "GLiClass: Generalist Lightweight Model for Sequence Classification Tasks" | Verifiable, peer-able reference |

**Input format dla citation grounding:**

```python
from gliclass import GLiClassModel, ZeroShotClassificationPipeline
text = f"Evidence: {ustep_ustawy}"
labels = [f"Claim is consistent: {claim}", "Claim contradicts evidence"]
results = pipeline(text, labels, threshold=0.5)
```

Lub jako rule-following:

```python
text = f"Task: Verify if claim matches evidence\nEvidence: {evidence}\nClaim: {claim}"
labels = ["hallucinated", "not_hallucinated"]
```

**Verdict:** Multilingual coverage + zero-shot multi-class są atutami. ALE: (a) brak per-language polish accuracy w model cardzie, (b) ~6× większy od mDeBERTa, (c) training data NIE NLI-specific (logic + commonsense). **Dla Magdy:** komplementarne ablation w R7, nie replacement Tier 1.

---

### 2.2 `knowledgator/gliclass-v3` collection (6 modeli)

**URL:** https://huggingface.co/collections/knowledgator/gliclass-v3

| Model | Params | Lang coverage | Notes |
|-------|--------|---------------|-------|
| gliclass-edge-v3.0 | 32.7M | not specified | Edge/CPU variant |
| gliclass-modern-base-v3.0 | 0.2B | not specified | ModernBERT base |
| gliclass-modern-large-v3.0 | 0.4B | not specified (verified: English avg F1 0.6082) | ModernBERT large |
| gliclass-base-v3.0 | 0.2B | not specified | Standard base |
| gliclass-large-v3.0 | 0.4B | not specified | Standard large |
| gliclass-x-base | 0.3B | not specified | X variant |

**Key fact:** Collection głównie English. `gliclass-multilang-ultra` (sekcja 2.1) jest **osobnym multilingual flagship** — NIE jest w tej v3 collection. Wszystkie v3 models są zero-shot classifiers z claim "up to 50× faster than Cross-Encoders". Last update Jan 29, 2025.

**Verdict:** Dla polish citation grounding **bezużyteczne** (poza ablation z `gliclass-multilang-ultra`). NIE rekomendowane dla naszego scope.

---

### 2.3 `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (re-verification fresh model card)

**URL:** https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7

| Field | Value | Update vs poprzedni research |
|-------|-------|------------------------------|
| Params | 0.3B (300M) | confirmed |
| Base model | mDeBERTa-v3-base (Microsoft, CC100 100 langs pretrain) | confirmed |
| License | **MIT** ✅ | confirmed |
| Polish coverage | **TAK** — `pl` w 27-lang dataset (multilingual-nli-26lang-2mil7) | confirmed |
| Training size | **3,287,280** hypothesis-premise pairs (2.73M multilingual + 2,490 XNLI val) | confirmed |
| XNLI per-language reported | EN 0.871, DE 0.824, ES 0.832, FR 0.823, RU 0.803, ZH 0.803, TR 0.792, VI 0.793, AR 0.794, BG 0.822, EL 0.809, TH 0.786, UR 0.744, HI 0.769, SW 0.746 — **Polish NIE reportowane** (Polski nie jest w XNLI 15-lang test set) | confirmed |
| Speed | 877-1887 text/sec A100 | confirmed |
| Downloads (last month) | **275,224** | confirmed — **battle-tested** |
| Spaces | 39 | confirmed adoption |
| Quantization | FP16 nieobsługiwany (GitHub issue #77 — confirmed limitation) | ⚠ pamiętać o tym dla TEI deployment |
| Limitations cited by author | "MT-created training data reduces quality for complex NLI tasks" | confirmed — explicit caveat |

**Verdict:** **TRZYMAĆ jako Tier 1.** Brak alternatywy o równoważnej `polish coverage + MIT license + battle-tested adoption` triade. **Polish accuracy proxy:** estymować z BG (0.822), RU (0.803) jako sąsiednie Slavic w XNLI → realnie ~0.78-0.81 polish accuracy expected.

---

### 2.4 `sentence-transformers/all-nli` (training dataset)

**URL:** https://huggingface.co/datasets/sentence-transformers/all-nli

| Field | Value |
|-------|-------|
| Source | SNLI + MultiNLI (**brak ANLI** — to nie jest BigCat) |
| Total rows | 2,861,761 (train 314k / dev 6.81k / test 6.83k) |
| Format | 4 wariantów: `pair-class` (premise+hypothesis+label 0/1/2), `pair-score` (regression), `pair` (contrastive), `triplet` (anchor+positive+negative) |
| **Polish coverage** | **❌ ENGLISH-ONLY** |
| License | nie specyfikowana wprost w datasecie |
| Use | training/fine-tuning embedding models i NLI cross-encoders |
| Downloads | 2,634 last month |

**Verdict:** Dla Tier 2 (HerBERT fine-tune) **NIE pomocne** — English-only. CDSC-E (KLEJ, polish) zostaje jedynym viable polish NLI dataset dla custom HerBERT fine-tune.

**Akcja:** all-nli nie usuwać z mental model, ale traktować jako **bazę dla ewentualnego machine-translated polish fine-tune dataset** (gdyby autorka chciała augmentation poza CDSC-E 10k pairs). Mała szansa — out of scope dla v3.2.

---

### 2.5 `dleemiller/finecat-nli` — blog post + model

**URL blog:** https://huggingface.co/blog/dleemiller/finecat-nli
**URL model:** https://huggingface.co/dleemiller/finecat-nli-l
**URL dataset:** https://huggingface.co/datasets/dleemiller/FineCat-NLI

| Field | Value |
|-------|-------|
| Architecture | **ModernBERT-large** (answerdotai/ModernBERT-large) |
| Params | 0.4B (395M) |
| License (model) | **⚠ NIE specyfikowana wprost** w model cardzie — to **red flag** dla HF dataset publication w pracy inżynierskiej; trzeba zapytać autora przed użyciem w production |
| Training data | BigCat-NLI (1M rows after curation z MNLI + SNLI + ANLI rounds 1-3 + WANLI + LingNLI + NLI-FEVER) |
| Distillation | Teacher: `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` (z dwoma loss: cross-entropy + MSE on teacher logits, α=β=0.5) |
| **Polish coverage** | **❌ ENGLISH-ONLY** (jak source datasets) |
| Benchmarks (F1-micro) | FineCat dev 0.8227, MNLI **0.9152**, MNLI-MM **0.9265**, SNLI 0.9162, ANLI-R1 0.7480, ANLI-R2 0.5700, ANLI-R3 0.5433, WANLI **0.7706**, LingNLI 0.8742 — **competitive z teacher (0.8233 FineCat dev) ale 20% szybszy + 40% mniej memory** |
| Throughput | 539 samples/sec @ batch=32, Nvidia Blackwell PRO 6000 |
| Memory peak | 1,838 MB |
| Downloads | **62,523/month** — solid adoption |
| Last update | Oct 31, 2025 (blog post date) |

**Key insight z blog post:** "High-quality data beats quantity" — usunięcie ~60% easy examples (scores >0.9) + low-quality detection via DeepSeek-V3.2-Exp + SNLI/MNLI downsampling. Methodology reusable dla HerBERT+CDSC-E fine-tune.

**Verdict:** **NIE dla Tier 1** (English-only). ALE: (a) methodology jest reusable dla naszego Tier 2 HerBERT fine-tune (filter easy CDSC-E examples + knowledge distillation z mDeBERTa), (b) **citation w R2** § hidden-states halu detection landscape — jako evidence że "knowledge distillation NLI 2025 nadal aktywny research area".

---

### 2.6 `dleemiller/nli-xenc-ways-to-use` — blog methodology

**URL:** https://huggingface.co/blog/dleemiller/nli-xenc-ways-to-use

**6 zastosowań NLI cross-encoders (autor: Daniel Lee Miller):**

1. **Zero-Shot Classification and Tagging** — hypothesis entailment framing
2. **RAG Hallucination Detection** ← **KLUCZOWE dla nas**
3. **Question Answering** — best candidate selection
4. **Response Evaluation (Rewards)** — multi-dimensional rubrics
5. **AI Guardrails** — safety policy checks
6. **Educational Grading** — student answer scoring

**Citation grounding example (dosłownie z blog post):**

```python
source = "The Eiffel Tower was completed in 1889 and stands 324 meters tall."
claims = [
    "The Eiffel Tower was finished in 1889",            # entailment
    "The Eiffel Tower is 300 meters high",              # contradiction
    "The Eiffel Tower was designed by Gustave Eiffel",  # neutral (not mentioned)
]
```

**Mapping** (reusable as-is w naszej R5 architekturze):
- `entailment` = "true: claim supported by source"
- `contradiction` = "false: claim contradicts source"
- `neutral` = "no information: claim not addressed in source"

**Hybrid scoring formula** (z blog post):

```python
def hybrid_score(p):
    # p = [contradiction, entailment, neutral] probabilities
    # 0.5 * neutral + entailment - contradiction
    raw = 0.5 * p[2] + p[1] - p[0]
    return float(max(0.0, min(1.0, raw)))
```

**Recommended models z blog:**
- Lightweight CPU: `dleemiller/EttinX-nli-s` (xxs-s sizes, 68M params)
- Strong: `dleemiller/ModernCE-large-nli`
- Reference: tasksource collection

**Polish coverage:** **❌ NIE adresowane** w blog post. English-only examples.

**Verdict:** **High-value methodology citation dla R2/R5.** Konkretne reusable patterns:
- Hybrid scoring formula → R5 architecture diagram (citation verifier scoring head)
- Direct/unambiguous hypothesis formulation → R3 dataset annotation guidelines
- 3-label → claim status mapping → R5 halu detection pipeline + R6 verifier interpretation

---

## 3. gliclass vs classic NLI deep dive (KLUCZOWA sekcja)

### 3.1 Architectural difference

| Aspekt | Classic NLI (mDeBERTa, ModernCE, FineCat) | gliclass (GLiClass family) |
|--------|---------------------------------------------|----------------------------|
| Input format | (premise, hypothesis) — 2 segments concatenated | (text, list_of_labels) — N labels simultaneously |
| Output | 3-class softmax: entailment / neutral / contradiction | N-way multi-class lub multi-label probabilities per label |
| Inference cost | Linear w liczbie hypotheses (1 forward pass per pair) | Nearly flat w liczbie labels (cross-attention scorer reuses pooled representation) |
| Polish coverage | Implicit (mDeBERTa: PL w 27 langs) lub explicit (HerBERT: pure PL) | Explicit (gliclass-multilang-ultra: PL w 20 langs) |
| Training task | Supervised NLI (premise→hypothesis entailment) | Generalist sequence classification (logic + commonsense + classification) |

### 3.2 Citation grounding fit — concrete scenarios

**Nasz use case:** dla każdego claim w Bielikowej odpowiedzi → verify czy jest grounded w cytowanym fragmencie ISAP/UOKiK.

**Scenario A: Per-claim binary verification (NAJPROSTSZE)**

```
Claim: "Konsument ma 14 dni na odstąpienie od umowy zawartej na odległość"
Evidence: "Art. 27 ust. 1 UPK — Konsument może w terminie 14 dni odstąpić od umowy..."
Target output: entailed=True, score=0.93
```

**Classic NLI:**
```python
inputs = tokenizer(evidence, claim, ...)  # premise=evidence, hypothesis=claim
output = model(**inputs)  # [contradiction, neutral, entailment]
verified = output[2] > 0.5  # entailment threshold
```

**gliclass:**
```python
text = f"Evidence: {evidence}"
labels = ["Claim is supported", "Claim is contradicted", "Claim is unaddressed"]
results = pipeline(text + " Claim: " + claim, labels)
```

**Winner:** Classic NLI — bardziej direct (3-class output matches exact halu detection labels: entailment=not-halu, contradiction=halu, neutral=uncertain). gliclass dodaje warstwę prompt engineering (label phrasing) która wymaga tuning.

**Scenario B: Multi-evidence verification (RAG TOP-K SCENARIO)**

```
Claim: "Konsument ma 14 dni na odstąpienie od umowy zawartej na odległość"
Evidence_1: "Art. 27 UPK..." (top-1 retrieved)
Evidence_2: "Art. 28 UPK..." (top-2 retrieved)
Evidence_3: "Art. 29 UPK..." (top-3 retrieved)
Target: which evidence ACTUALLY supports? Score each.
```

**Classic NLI:** 3 forward passes (1 per evidence) → 3 entailment scores.
**gliclass:** 1 forward pass z text=claim + labels=[evidence_1_summary, evidence_2_summary, evidence_3_summary] — KOMPRESYJNIE WYDAJNIEJSZE jeśli batching = critical.

**Winner:** gliclass **w teorii**. ALE: (a) labels muszą być short (label = pre-summarized evidence), (b) Magda i tak będzie iterować per-claim w continuous loop, więc batch latency != bottleneck.

**Scenario C: Multi-class halu typology (R7 ABLATION)**

```
Claim: "Konsument ma 30 dni na odstąpienie od umowy"  ← halu (factual fabrication)
Evidence: "Art. 27 UPK — 14 dni..."
Target output: halu_type="numerical_error"
```

**Classic NLI:** Tylko 3 klasy — wymaga downstream post-processing (LLM judge lub regex parsing claim numbers).
**gliclass:** Native multi-class:
```python
labels = ["numerical_error", "entity_confusion", "temporal_drift",
          "fabrication", "negation_flip", "supported"]
```

**Winner:** gliclass **klisko** — 6-poziomowa taksonomia halu types (z `CLAUDE.md` § Defense scaffolding) idealnie maps do gliclass multi-class output bez additional model. **TO JEST KLUCZOWY ARGUMENT za dodaniem gliclass jako Tier 0 ablation w R7.**

### 3.3 Empirical comparison limits

**Brakuje:** Polish per-language XNLI benchmark dla gliclass-multilang-ultra. Reported tylko multilingual avg F1 0.5599 (na MASSIVE + SIB-200, NIE XNLI). Magda będzie musiała **sama zmierzyć** na własnym 100-par gold standard lub CDSC-E test set.

**Time-to-test estimate:** 2-4h (load model na lab GPU SP7 H200 → batch inference na 1000 par CDSC-E + 100 manual gold → compute accuracy + F1 + macro-F1 → compare z mDeBERTa baseline).

### 3.4 Verdict deep-dive

| Use case | Classic NLI (mDeBERTa) | gliclass-multilang-ultra | Rekomendacja |
|----------|------------------------|--------------------------|--------------|
| Per-claim binary | ✅ idealny | ⚠ adekwatny | **mDeBERTa** (Tier 1) |
| Multi-evidence batch | ⚠ N forward passes | ✅ 1 forward pass | mDeBERTa OK (batching nie jest bottleneck) |
| Multi-class halu typology | ❌ wymaga downstream | ✅ native | **gliclass** jako Tier 0 ablation w R7 |
| Reproducibility w pracy | ✅ 275k dl/mo industry standard | ⚠ 1k dl/mo niska adopcja | **mDeBERTa** dla R7 main result |
| License | MIT (idealny) | Apache 2.0 (OK) | tie |
| Polish accuracy verifiable | ⚠ tylko proxy z RU/BG | ❌ brak polish per-lang benchmark | mDeBERTa (lepszy reasoning po proxy) |

**Konkluzja:** classic NLI (mDeBERTa) zostaje Tier 1. gliclass dodać jako Tier 0 **ablation eksperyment** dla R7 — specifically: porównanie multi-class halu typology accuracy (gliclass native multi-class) vs sequential 3-class NLI + LLM-judge post-processing (mDeBERTa + Bielik fallback). **To jest defensible ablation, NIE replacement.**

---

## 4. dleemiller methodology insights — co reuse

### 4.1 Hybrid scoring formula (R5 verifier head)

```python
def claim_grounding_score(p):
    """p = [contradiction, entailment, neutral] z NLI verifier"""
    raw = 0.5 * p[2] + p[1] - p[0]  # neutral half-credit, entailment +, contradiction -
    return float(max(0.0, min(1.0, raw)))
```

**Reuse:** R5 architecture diagram (FIG-3 citation verifier) + R6 § verifier head methodology + R7 sensitivity analysis (threshold sweep `score > θ` dla θ ∈ {0.3, 0.5, 0.7}).

### 4.2 Direct/unambiguous hypothesis formulation

**dleemiller principle:** "Write hypotheses/rubrics as direct and unambiguous statements rather than open-ended questions."

**Reuse w R3 dataset:** annotation guidelines dla 100 par gold standard — KAŻDY claim ekstraktowany z Bielikowej odpowiedzi MUSI być reformulowany jako pojedyncze direct statement (NIE multi-clause, NIE question). Przykład:

❌ Bad: "Konsument ma prawo odstąpić od umowy ale tylko jeśli nie był informowany prawidłowo o swoich prawach"
✅ Good (2 claims):
  - claim_1: "Konsument ma prawo odstąpić od umowy zawartej na odległość"
  - claim_2: "Termin odstąpienia jest przedłużany w przypadku nieprawidłowego pouczenia"

**To jest istotny insight dla R3 § corpus construction — należy dodać sekcję "claim extraction guidelines".**

### 4.3 6 use cases NLI cross-encoder framework (R2 reframing)

Dleemiller treats NLI cross-encoder jako "Swiss Army knife of NLP". **Reuse w R2 § 2.5:** zamiast pisać tylko "NLI-based halu detection", expand do "NLI cross-encoder jako wielozastosowanie framework: zero-shot classification, halu detection, QA, response eval, guardrails, grading" — **demonstruje że Magda zna szerszy ekosystem, NIE tylko jeden use case.**

### 4.4 Knowledge distillation methodology (Tier 2 enhancement potential)

**FineCat-NLI lesson:** large NLI teacher (DeBERTa-v3-large MNLI) → smaller ModernBERT student z dual loss (CE + MSE on logits). Achieved 20% speedup + 40% memory reduction WITHOUT accuracy drop.

**Reuse dla Tier 2:** jeśli HerBERT-large+CDSC-E fine-tune (Tier 2) okaże się zbyt wolny dla production demo, distill go do HerBERT-base lub mDeBERTa-base. **To jest "future work" w R8, NIE blocker dla v3.2 deadline.**

---

## 5. Tabela porównawcza (all candidates)

| Model | Params | Polish? | License | Acc na XNLI/CDSC-E proxy | CPU latency (ms/pair) | Use case fit |
|-------|--------|---------|---------|--------------------------|------------------------|--------------|
| **mDeBERTa-v3-base-xnli-multilingual-2mil7** | 0.3B | ✅ explicit (27 langs) | **MIT** | XNLI BG 0.822, RU 0.803 → PL ~0.78-0.81 proxy | ~5-15 ms (estimate) | **Tier 1** ✅ |
| **HerBERT-large + CDSC-E custom fine-tune** | 0.4B | ✅ pure Polish | base model: CC-BY-4.0 | CDSC-E test ~96% (KLEJ leaderboard) | ~10-20 ms | **Tier 2** (fallback) ✅ |
| **Bielik 11B + few-shot NLI prompt** | 11B | ✅ native | Apache 2.0 | n/a — emergent few-shot, ~80-90% jakość | ~500-1500 ms (GPU) | **Tier 3** (LLM-as-judge ablation) ✅ |
| **gliclass-multilang-ultra** | 1.7B | ✅ explicit (20 langs) | Apache 2.0 | brak polish per-lang; multilingual avg F1 0.56 | ~5 ms @ batch=8 GPU | **Tier 0** ablation (multi-class halu typology) NEW ✅ |
| gliclass-modern-large-v3.0 | 0.4B | ❌ not specified | Apache 2.0 | EN avg F1 0.6082 | n/a | ❌ skip (English-focused) |
| **finecat-nli-l** | 0.4B | ❌ English-only | ⚠ unspecified | MNLI 0.9152 | <2 ms CPU (estimate, ModernBERT) | ❌ skip (no polish) |
| ModernCE-large-nli | 0.4B | ❌ English-only | MIT | MNLI-MM 0.9202 | ~2-5 ms CPU (ModernBERT) | ❌ skip (no polish) |
| EttinX-nli-s | 68M | ❌ English-only | MIT | MNLI-MM 0.8798 | <1 ms CPU (Ettin 68M) | ⚠ rozważ jako **CPU baseline ablation** (tylko jeśli warto cycles na English-baseline comparison) |
| all-nli (dataset) | n/a | ❌ English-only | not spec | n/a | n/a | ❌ skip dla polish fine-tune |

**Notes:**
- CPU latency estimates są szacunkowe (model cards rzadko reportują CPU benchmarks); finalna decyzja powinna być empirycznie zweryfikowana z TEI benchmark
- "Polish accuracy proxy" dla mDeBERTa = average BG (slavic) i RU (slavic) accuracy z XNLI — Magda powinna pomierzyć realnie na CDSC-E test 1k par + 100 manual gold

---

## 6. Recommendation z 3 wariantami + decision tree

### Wariant 1: TRZYMAĆ current 3-tier plan (REKOMENDOWANE) ✅

**Stack:**
- Tier 1: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`
- Tier 2: HerBERT-large + CDSC-E fine-tune (jeśli Tier 1 < 70% accuracy)
- Tier 3: Bielik 11B / PLLuM 12B LLM-as-judge (ablation only)

**Argumenty:**
- mDeBERTa jest battle-tested (275k dl/mo), MIT license, explicit polish (27 langs trained), reproducibility-friendly dla pracy inżynierskiej
- HerBERT+CDSC-E to silny upper bound z polish leaderboard (KLEJ ~96%)
- LLM-judge zapewnia explainability dla R7 error analysis

**Time-to-test:** ~0 (już planowane)

**Cons:** brak multi-class halu typology native support

---

### Wariant 2: DODAĆ gliclass jako Tier 0 ablation w R7 (REKOMENDOWANE) ✅

**Dodatkowy stack:**
- Tier 0: `knowledgator/gliclass-multilang-ultra` (zero-shot 6-class halu typology)
- Pozostałe Tiers bez zmian

**Argumenty:**
- Native multi-class output maps DOSŁOWNIE na 6-poziomową taksonomię halu types z `CLAUDE.md` § Defense scaffolding (factual fabrication / entity confusion / temporal drift / negation flip / paragraph mis-citation / ambiguous claim)
- Polish coverage explicit (20 langs trained, NIE machine-translated)
- Apache 2.0 license OK dla HF publication
- Komplementarne ablation w R7: porównanie "single-step gliclass multi-class" vs "two-step mDeBERTa NLI + LLM judge classify"
- Defensive contribution dla R8 § eksperymentalny

**Time-to-test:** ~4-8h (load model, batch eval na 100 manual gold, compare F1 macro per halu type, build R7 sub-section)

**Cons:** ~1.7B params (6× większe niż mDeBERTa) — concern dla CPU dev; brak polish per-lang benchmark w model cardzie (musisz sama zmierzyć)

**Defensiveness w R7:** "gliclass-multilang-ultra jako ablation kompletności taksonomii halu types — czy 6-class native output jest dokładniejszy niż dwustopniowy mDeBERTa NLI + Bielik judge classification?" To **defensible RQ** which Magda może dodać jako exploratory sub-question w R7 bez modyfikacji 3 main + 2 supporting RQ.

---

### Wariant 3: REPLACE Tier 1 z lepszym modelem ❌ NIE REKOMENDOWANE

**Brak basis** dla replacement. Żaden z 6 analizowanych modeli nie pokonuje mDeBERTa na łącznym kryterium:
- (a) explicit polish training data
- (b) MIT license
- (c) battle-tested adoption (>100k dl/mo)
- (d) production-friendly size (≤500M params)
- (e) per-language XNLI benchmark documented

`gliclass-multilang-ultra` pokonuje na (a) i (e tak-sobie), ALE traci na (c) i (d).
`finecat-nli-l`, `ModernCE-large-nli`, `EttinX-nli-s` tracą na (a) — English-only.

**Recommendation:** NIE replace, NIE downgrade Tier 1.

---

### Decision tree

```
START: czy plan v3.2 wymaga zmiany NLI verifier stack?
├── Pytanie 1: czy któryś z 6 nowych modeli ma BETTER polish accuracy niż mDeBERTa?
│   └── NIE (brak danych) → NIE replace Tier 1
├── Pytanie 2: czy któryś z 6 nowych modeli ma feature komplementarne do current stack?
│   ├── gliclass: TAK — native multi-class output dla halu typology
│   ├── finecat/ModernCE/EttinX: NIE — duplikują classic NLI 3-class
│   └── all-nli: NIE — English-only dataset, nieprzydatny dla polish fine-tune
├── Pytanie 3: czy gliclass jako Tier 0 ablation expands scope poza 3 main + 2 supporting RQ?
│   └── NIE — jest exploratory sub-RQ w R7, NIE central
└── DECYZJA: TRZYMAĆ Tier 1-3 + DODAĆ gliclass jako Tier 0 R7 ablation
          + ZAPRZYJAŹNIĆ dleemiller methodology dla R2/R3/R5
```

---

## 7. Cytacje z linkami

**Modele:**
1. `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` — https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
2. `knowledgator/gliclass-multilang-ultra` — https://huggingface.co/knowledgator/gliclass-multilang-ultra (paper: arXiv:2508.07662)
3. `knowledgator/gliclass-v3` collection — https://huggingface.co/collections/knowledgator/gliclass-v3
4. `knowledgator/gliclass-modern-large-v3.0` — https://huggingface.co/knowledgator/gliclass-modern-large-v3.0
5. `dleemiller/finecat-nli-l` — https://huggingface.co/dleemiller/finecat-nli-l
6. `dleemiller/ModernCE-large-nli` — https://huggingface.co/dleemiller/ModernCE-large-nli
7. `dleemiller/EttinX-nli-s` — https://huggingface.co/dleemiller/EttinX-nli-s
8. `allegro/herbert-large-cased` — https://huggingface.co/allegro/herbert-large-cased

**Datasety:**
9. `sentence-transformers/all-nli` — https://huggingface.co/datasets/sentence-transformers/all-nli
10. `dleemiller/FineCat-NLI` — https://huggingface.co/datasets/dleemiller/FineCat-NLI
11. `allegro/klej-cdsc-e` — https://huggingface.co/datasets/allegro/klej-cdsc-e

**Blog posts (dleemiller methodology):**
12. "FineCat-NLI: Curated NLI Dataset and Distilled Model" (Oct 31, 2025) — https://huggingface.co/blog/dleemiller/finecat-nli
13. "NLI Cross Encoders: Ways to Use" — https://huggingface.co/blog/dleemiller/nli-xenc-ways-to-use

**Papers:**
14. GLiClass paper (Aug 2025) — arXiv:2508.07662
15. KLEJ benchmark (Polish, ACL 2020) — https://aclanthology.org/2020.acl-main.111

**Phantom citation potwierdzony:**
- `sdadas/polish-nli` — **NIE ISTNIEJE** na HF (verified — sdadas ma polish-splade, polish-reranker, stella-pl, mmlw, ale brak polish-nli). NIE używać w pracy. Already noted w CLAUDE.md.

---

## 8. Updated 3-tier strategy proposal (post-research)

**`CLAUDE.md` § Stack proposed addition:**

```diff
- **MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7** (300M, MIT, 105k polish pairs trained) — primary verifier;
  HerBERT-large custom NLI fine-tune na CDSC-E — opcjonalny upgrade
+ **MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7** (300M, MIT, 105k polish pairs trained) — primary verifier (Tier 1);
+ HerBERT-large custom NLI fine-tune na CDSC-E — Tier 2 fallback if Tier 1 < 70% accuracy;
+ Bielik 11B v3 / PLLuM 12B few-shot NLI — Tier 3 LLM-as-judge ablation only;
+ **knowledgator/gliclass-multilang-ultra** (1.7B, Apache 2.0, 20 langs incl. PL) — Tier 0 R7 ablation:
+ native multi-class halu typology comparison vs 2-step mDeBERTa NLI + LLM judge classify
```

**`thesis_research/02_konspekt_v3.2_skeleton.md` § R7 proposed addition:**

```
### R7 § 7.4 Verifier comparison ablation
- 4-way comparison: mDeBERTa zero-shot, HerBERT+CDSC-E fine-tuned, gliclass-multilang-ultra zero-shot, Bielik 11B few-shot
- Metrics: macro-F1, accuracy per halu type (6 categories), inference latency, GPU memory
- Hypothesis: gliclass native multi-class > mDeBERTa 3-class + post-processing dla halu typology
```

**Optional reuse dla R2/R3/R5:**
- R2 § 2.5: dodać cite dleemiller blog "NLI cross-encoder Swiss Army knife framing"
- R3 § corpus construction: dodać "claim extraction guidelines" inspired dleemiller "direct/unambiguous statements"
- R5 FIG-3 verifier head: dodać hybrid scoring formula `0.5 * neutral + entailment - contradiction`
- R6 § verifier methodology: dodać FineCat-NLI knowledge distillation jako "future work" jeśli HerBERT Tier 2 będzie zbyt wolny

---

## 9. Critical findings (Top 3)

1. **Phantom citation potwierdzony:** `sdadas/polish-nli` NIE ISTNIEJE — sdadas (Sławomir Dadas) ma polish-splade, polish-reranker-roberta-v3, polish-roberta-large-v2, stella-pl, mmlw embeddings, ALE brak NLI model. Note w CLAUDE.md już prawidłowy. **Zachowaj rygor.**

2. **gliclass-multilang-ultra ma realny upside dla R7 ablation** — native multi-class output bezpośrednio maps na 6-poziomową taksonomię halu types z `CLAUDE.md` § Defense scaffolding. To jest **defensible exploratory sub-RQ** który zwiększa contributions w R8 § eksperymentalny bez modyfikacji 3 main + 2 supporting RQ.

3. **finecat-nli-l license red flag** — model card NIE specyfikuje license wprost. Pomimo strong benchmarks (MNLI 0.9152, 20% faster than teacher) **NIE używać w pracy bez explicit author confirmation**. To jest standardowy patten — wielu HF authors zapomina license tag — ale dla pracy inżynierskiej z HF publication intent **license audit jest mandatory**.

---

## 10. Time-to-execute estimates (jeśli wariant 1+2)

| Task | Czas | Output |
|------|------|--------|
| Update `CLAUDE.md` § Stack (1 zdanie) | 5 min | git commit, decision logged |
| Update `02_konspekt_v3.2_skeleton.md` § R7 (1 sub-section) | 15 min | konspekt v3.2.1 |
| Append summary do `sources_z_v3.1_do_reuse_w_v3.2.md` | 10 min | done w tym agencie |
| Iter. 0b POC: gliclass batch eval na CDSC-E test 1k par | 4-8h | F1 macro report + 1 figure dla R7 |
| Iter. 0b POC: gliclass eval na 100 manual gold (jak gotowe) | 1-2h | accuracy + halu typology confusion matrix |
| R5 architecture FIG-3 add hybrid scoring formula | 30 min | updated SVG/Mermaid |
| R3 § add claim extraction guidelines (5-10 zdań inspired dleemiller) | 20 min | done draft |
| **TOTAL** | **~6-12h work** | **incremental ulepszenie scope bez deadline impact** |

**Acceptable?** Tak — wszystkie operacje są < 1 dzień, NIE wprowadzają scope creep, dodają defensiveness do pracy.

---

**END OF RESEARCH** — gotowe do sign-off od Magdy.
