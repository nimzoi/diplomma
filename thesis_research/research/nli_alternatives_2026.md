# NLI alternatives dla polish citation grounding — research 2026

**Data:** 2026-05-16
**Cel:** Wybór najlepszego modelu NLI/entailment dla polskiego (claim, evidence) → entailed/contradicted/neutral classification w kontekście citation-grounded RAG halu detection (legal/regulatory polish text — ChPL, Ulotki, AOTMiT, NFZ).
**Kontekst:** Praca inżynierska MLOps RAG retrieval retraining (M. Sochacka, PJATK).

---

## 0. Executive summary + top 3 recommendations

**Stan landscape NLI dla polskiego (2026-05):**
- **Brak dedykowanego polskiego NLI modelu publicznie dostępnego z dobrym tracked record** — `izaitova/herbert-large-cased_nli` istnieje (val acc 0.77) ale ma minimalną dokumentację, tylko 6 downloads/miesiąc, nieznane training data. To ryzyko reproducibility.
- **Multilingual NLI dominuje** — `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` jest de facto standardem dla low-resource langs (275k downloads/mo, polski w 27 lang training data, MIT).
- **Polish NIE jest w XNLI 15-lang test set** — wszystkie publiczne XNLI per-lang accuracies dla polskiego to estymaty z cross-lingual transfer (~0.78-0.80 jako proxy z innych Slavic — RU, BG).
- **Custom fine-tune HerBERT-large + CDSC-E** to praktycznie 1-2h na A100 i KLEJ leaderboard pokazuje 96.4% accuracy — najsilniejszy upper bound dla polish-specific NLI, **ALE** CDSC-E jest na image captions (out-of-domain względem leku/legal).

### Top 3 rekomendacje

| # | Model | Use case | Reasoning |
|---|-------|----------|-----------|
| **1** | **`MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`** | Default out-of-the-box | Polish w training data (1 z 27 langs), MIT, 275k downloads/mo (battle-tested), 0.3B params (production-friendly), avg XNLI 0.80 (cross-lingual proxy ≈ 0.78-0.81 dla pl). **Defensible w pracy bo industry-standard.** |
| **2** | **HerBERT-large fine-tune na CDSC-E (custom)** | Best accuracy ścieżka jeśli zaakceptujesz trade-off | Upper bound 96.4% accuracy na CDSC-E test (KLEJ leaderboard). 4-8h na A100 (40 epochs, 32 batch). **Caveat:** CDSC-E jest na image captions — domain shift do leku może obniżyć realne accuracy do ~80-85%. Wymaga ablation. |
| **3** | **Bielik-11B-v3 + few-shot NLI prompting** | Fallback gdyby (1) i (2) nie spełniły kappa ≥0.50 vs manual | Apache 2.0, native polish reasoning, ChatML format. **Cost** ~10-50× drożej per inference niż mDeBERTa (11B vs 0.3B). Acceptable jeśli use case = retraining loop (low frequency, NIE production demo). |

**Anti-recommendation:** Unikaj `MoritzLaurer/deberta-v3-large-zeroshot-v2.0` (English-only), `cross-encoder/nli-deberta-v3-large` (English-only), `tasksource/ModernBERT-base-nli` (English-only), `MoritzLaurer/xlm-v-base-mnli-xnli` (Polski poza XNLI 15 → tylko cross-lingual transfer, 0.8B params bez Polish accuracy benefit).

---

## 1. Primary candidate verification: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`

**URL:** https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7

### Specs (verified z model card)

| Field | Value |
|-------|-------|
| Params | 0.3B (300M) |
| Base model | mDeBERTa-v3-base (Microsoft, pre-trained na CC100 100 langs) |
| License | **MIT** ✅ |
| Tensor type | F32 (BF16 nie wspierany) |
| Context window | 512 tokens |
| Polish coverage | **TAK** — explicit w training: 1 z 27 langs (`pl` w `multilingual-nli-26lang-2mil7` dataset) |
| Downloads (last month, 2026-05) | 275,378 |
| Training data | 3,287,280 hypothesis-premise pairs: MultiNLI, Fever-NLI, ANLI, LingNLI, WANLI (EN) + machine-translated 26 langs |
| Training data quality caveat | "Dataset created using machine translation, reducing quality for complex NLI tasks" (cytat z model card) |

### Polish accuracy — bezpośrednio NIE reportowana, estymaty:

- **XNLI 15-lang average (z model card):** ~0.80
- **Polish NIE jest w XNLI 15-lang test set** (XNLI obejmuje: ar, bg, de, el, en, es, fr, hi, ru, sw, th, tr, ur, vi, zh)
- **Proxy estymaty dla polskiego** (na podstawie similar Slavic langs w XNLI):
  - Russian (ru): 0.803
  - Bulgarian (bg): 0.829
  - **Estymata polskiego: 0.78-0.81** (cross-lingual transfer + pl w training data daje boost)

### Inference speed estimate

- **GPU (A100):** ~3000-5000 texts/sec (batch=32, fp16 NIE wspierany — mniej memory-efficient niż XLM-V)
- **CPU:** ~20-50 texts/sec (single-threaded, batch=1)
- **Memory footprint:** ~1.1 GB (fp32 weights), ~600 MB (bf16 jeśli załadowane jako bf16, ale model nie był trained w bf16 → możliwa utrata accuracy)

### Sample usage code (z model card)

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model_name = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)

# Polish example dla citation grounding
premise = "Lek X jest wskazany do leczenia depresji u dorosłych."
hypothesis = "Lek X może być stosowany u dzieci."

inputs = tokenizer(premise, hypothesis, truncation=True, return_tensors="pt").to(device)
output = model(inputs["input_ids"])
prediction = torch.softmax(output["logits"][0], -1).tolist()
label_names = ["entailment", "neutral", "contradiction"]
prediction = {name: round(float(pred) * 100, 1) for pred, name in zip(prediction, label_names)}
print(prediction)
# Expected: {'entailment': 5.x, 'neutral': 10.x, 'contradiction': 84.x}
```

### Recommended training hyperparameters (jeśli dalsze fine-tune)

```python
training_args = TrainingArguments(
    num_train_epochs=3,
    learning_rate=2e-05,
    per_device_train_batch_size=32,
    gradient_accumulation_steps=2,
    warmup_ratio=0.06,
    weight_decay=0.01,
    fp16=False  # ⚠ mDeBERTa-v3 NIE wspiera FP16
)
```

---

## 2. Multilingual NLI alternatives

| Model ID | Params | License | Polish coverage | Estimated polish accuracy | Inference (texts/sec, A100) | HF downloads/mo (2026-05) |
|----------|--------|---------|-----------------|---------------------------|------------------------------|---------------------------|
| **MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7** | 0.3B | MIT | ✅ pl w 27 langs training | ~0.78-0.81 (proxy) | ~3000-5000 | **275,378** |
| MoritzLaurer/mDeBERTa-v3-base-mnli-xnli | 0.3B | MIT | ⚠ tylko XNLI 15 (pl NIE) → cross-lingual | ~0.75-0.78 (cross-lingual only) | ~3000-5000 | 208,431 |
| joeddav/xlm-roberta-large-xnli | 0.6B | MIT | ⚠ pl NIE w XNLI 15 → cross-lingual transfer (XLM-R supports 100 langs) | ~0.75-0.79 (proxy) | ~1500-2500 | 112,110 |
| MoritzLaurer/bge-m3-zeroshot-v2.0 | 0.6B | MIT | ✅ multilingual (BGE-M3 base supports pl) | ~0.65-0.75 (zero-shot, niższy niż dedicated NLI) | ~1500-2500 | 60,355 |
| MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli | 0.1B | MIT | ⚠ XNLI 15 only → cross-lingual (pl NIE w training) | ~0.65-0.70 (small + cross-lingual) | **~6000+ (najszybszy)** | 6,538 |
| MoritzLaurer/xlm-v-base-mnli-xnli | 0.8B | MIT | ⚠ pl NIE w XNLI 15 → cross-lingual transfer | ~0.74-0.78 (XLM-V ma 1M vocab — lepsza tokenization pl ale brak NLI training na pl) | ~3300 | 247 |
| sileod/mdeberta-v3-base-tasksource-nli | 0.3B | Apache 2.0 | ✅ multilingual (ten sam mDeBERTa-v3-base) | ~0.75-0.80 (multi-task trained na 30 datasets) | ~3000-5000 | 45 |
| knowledgator/comprehend_it-multilingual-t5-base | 0.39B | Apache 2.0 | ✅ ~100 langs (mT5-base) | ~0.70-0.78 (encoder-decoder, T5 zero-shot, wymaga LiqFit lib) | ~1000-2000 (slower — encoder-decoder) | 80 |
| DAMO-NLP-SG/zero-shot-classify-SSTuning-XLM-R | 0.28B | MIT | ⚠ trained na 20.48M EN samples → cross-lingual via XLM-R-base | ~0.65-0.70 (cross-lingual only, EN training) | ~3000-5000 | 25 |
| MoritzLaurer/deberta-v3-large-zeroshot-v2.0 | 0.4B | MIT | ❌ **English-only** | N/A | ~2000-3000 | 39,775 |
| cross-encoder/nli-deberta-v3-large | 0.4B | Apache 2.0 | ❌ **English-only** | N/A | ~2000-3000 | 77,785 |
| tasksource/ModernBERT-base-nli | 0.1B | Apache 2.0 | ❌ **English-only** | N/A | ~5000+ | 4,168 |
| MoritzLaurer/ModernBERT-large-zeroshot-v2.0 | 0.4B | Apache 2.0 | ❌ **English-only** | N/A | ~1000-1300 | TBD |

### Key insights z porównania

1. **Tylko 4 modele mają explicitly polish w training data:** `mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (27 langs), `sileod/mdeberta-v3-base-tasksource-nli` (multilingual), `knowledgator/comprehend_it-multilingual-t5-base` (~100 langs), `bge-m3-zeroshot-v2.0` (multilingual). Reszta polega na cross-lingual transfer.
2. **mDeBERTa-v3 dominuje multi-language NLI landscape** — 3 z top 5 modeli w mojej tabeli używają tej bazy. To industry default.
3. **English-only "v2.0" Moritz Laurer modele nie nadają się** — mimo że są SOTA w EN, brak jakiegokolwiek pl coverage.
4. **XLM-V miał obietnicę większego vocab** (1M vs 250k) co teoretycznie pomaga slavic langs, ale **brak NLI training na pl** ⇒ accuracy gain znika.

---

## 3. Polish-specific NLI options

| Model / Source | Status | Params | Notes |
|----------------|--------|--------|-------|
| **`izaitova/herbert-large-cased_nli`** | ⚠ Public, ale ryzykowne | 0.4B (HerBERT-large) | Val accuracy 0.77 (low). Training data UNKNOWN (model card pusty). Tylko 6 downloads/mo. License CC-BY-4.0. **Reproducibility risk** — nie wiemy na czym trained, label format niejasny. |
| **CLARIN-PL** | ❌ Brak NLI modelu | - | Mają `roberta-polish-kgr10` (base LM), `FastPDN` (NER), ale brak dedicated NLI fine-tune publicly. |
| **IPI PAN** | ❌ Brak NLI modelu | - | `ipipan/silver-retriever-base-v1` to retriever (HerBERT-base + PolQA/MAUPQA fine-tune), `ipipan/pl_nask` to NER/POS spaCy model. **Brak NLI**. |
| **sdadas** | ❌ Brak NLI modelu (verified 2026-05) | - | 44 modeli published — wszystkie embeddings/retrievers/MLM (mmlw, stella-pl, polish-roberta-base-8k). Most recent: `sdadas/unpad-impl` (Mar 29, 2026). **Verified: brak NLI w 2025-2026**. |
| **Allegro** | ❌ Brak public NLI | - | HerBERT-base/large są public, ale Allegro NIE wypuścił NLI fine-tune'a. CDSC-E dataset jest theirs (`allegro/klej-cdsc-e`) ale brak modelu zwracanego z fine-tune'u. |
| **PJATK** | ❌ Brak public NLI | - | Brak organizational HF presence dla NLI. |
| **NASK-PIB** | ❌ Brak NLI (mają safety classifier) | - | `NASK-PIB/HerBERT-PL-Guard` (2025) — safety classification, NIE NLI. |
| **PolEval 2024/2025** | ❌ Brak NLI tasku | - | PolEval 2024: emotion/sentiment, PolEval 2025: machine-generated text detection (ŚMIGIEL). **Brak NLI tasku w ostatnich 2 latach**. |
| **Polish NLI dataset (CDSC-E)** | ✅ Public | - | `allegro/klej-cdsc-e` — 10k Polish sentence pairs (8k train / 1k val / 1k test). Domain: image captions. Labels: ENTAILMENT (18%), NEUTRAL (74%), CONTRADICTION (7%). License CC-BY-NC-SA-4.0 ⚠ **NonCommercial**. |
| **Polish NLI w factivity dataset (Ziembicki et al., 2022)** | ✅ Paper exists, dataset hosting unclear | - | 2,432 verb-complement pairs, 309 unique verbs ze NKJP. BERT-based ~89% F1, +manual features ~91%. Bardzo niche (factivity-specific), nie general NLI. |

### Bottom line dla polish-specific options

**Brak production-ready polish NLI modelu w 2026.** Najbliższy candidate (`izaitova/herbert-large-cased_nli`) ma critical reproducibility issues. Ścieżka realna = **custom fine-tune HerBERT-large na CDSC-E** (KLEJ leaderboard pokazuje 96.4% achievable z HerBERT-large), ale:
- CDSC-E to image captions → **domain shift do legal/regulatory polish** może uciąć accuracy do ~80-85%
- License CC-BY-NC-SA-4.0 ⚠ utrudnia ewentualną komercjalizację (NIE blokuje pracy badawczej / engineering thesis)

---

## 4. LLM-as-NLI fallback

### Bielik-11B-v3 z few-shot prompting

**Model:** `speakleash/Bielik-11B-v3.0-Instruct`
**License:** Apache 2.0 ✅ (commercial use OK)
**Base:** Mistral 7B v0.2 + depth up-scaling do 11B
**Polish corpus:** 292B+ tokens, 41M dokumentów

**Estimated NLI agreement vs manual** (extrapolacja z polish benchmarks):
- Bielik-11B-v3 osiąga SOTA na CPTUB, Polish EQ-Bench, Polish Medical Leaderboard
- Cross-lingual NLI literature pokazuje że LLMs >7B z 5-15 few-shot examples dorównują/przewyższają fine-tuned PLMs w low-resource langs (Bangla, Vietnamese — proxy dla polish)
- **Estymata: 0.75-0.85 agreement vs manual NLI** (lower bound z few-shot, upper bound z 15+ examples)
- **Cohen's kappa estymata: 0.55-0.70** (depending on prompt engineering)

### Cost overhead

| Metric | mDeBERTa-v3-base | Bielik-11B-v3 | Ratio |
|--------|------------------|---------------|-------|
| Params | 0.3B | 11B | **37×** |
| VRAM (fp16) | ~600 MB | ~22 GB | 37× |
| Inference latency (single pair, A100) | ~5-10 ms | ~200-500 ms (zależy od prompt length) | **30-50×** |
| Throughput (batch, A100) | 3000-5000 texts/sec | 20-50 inferences/sec (z few-shot prompts) | **100-200× wolniej** |
| Token cost per inference | 0 (fixed batch) | ~500-1500 input + 50-200 output tokens (z few-shot context) | N/A — Bielik jest open-source self-hosted, NIE billed per token |

### Verdict

**Acceptable jako:**
- Cycle-time judge (raz na cykl retreningu, na 1000-5000 par eval set) — koszt 5-30 min na A100 per cycle
- Initial bootstrap dla annotation tasku (semi-supervised seeding manual labels)

**NIE acceptable jako:**
- Production demo (Gradio inference real-time) — 200-500ms latency to UX killer
- Continuous improvement loop na hundreds-of-thousands par — ekonomicznie nieopłacalne mimo open-source (compute time)

**Rekomendacja:** Bielik-11B-v3 = **"oracle" baseline w ablation studies**, NIE production NLI model. Użyj do walidacji że dedicated NLI (mDeBERTa lub fine-tuned HerBERT) NIE traci 10pp+ vs LLM judge.

---

## 5. Benchmark ranking

### XNLI multilingual (per-lang accuracy, gdzie reportowane)

**⚠ Polish NIE jest w XNLI 15-lang test set.** Wszystkie poniższe accuracies są dla "comparable Slavic" jako proxy.

| Model | Avg XNLI 15-lang | Russian (proxy) | Bulgarian (proxy) | Estimated Polish |
|-------|-------------------|------------------|---------------------|-------------------|
| mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 | ~0.80 | 0.803 | (not listed in detail) | **~0.78-0.81** (pl w training) |
| mDeBERTa-v3-base-mnli-xnli | 0.808 | 0.813 | 0.829 | ~0.75-0.80 (cross-lingual only) |
| xlm-v-base-mnli-xnli | 0.780 | 0.782 | 0.808 | ~0.74-0.78 (cross-lingual only) |
| multilingual-MiniLMv2-L6 | 0.713 | 0.714 | (not listed) | ~0.65-0.70 (cross-lingual only) |
| xlm-roberta-large-xnli | unreported (paper) | unreported | unreported | ~0.75-0.79 (XLM-R-large strong base) |

### CDSC-E (Polish NLI, KLEJ benchmark) — verified leaderboard top 10

| Rank | Model | CDSC-E accuracy |
|------|-------|------------------|
| 1 | HerBERT (large) | **96.4%** |
| 2 | Polish RoBERTa-v2 (large) | 95.8% |
| 3 | XLM-RoBERTa (large) | 94.6% |
| 4 | Polish RoBERTa (large) | 94.5% |
| 5 | HerBERT (base) | 94.5% |
| 6 | XLM-RoBERTa (large) | 94.4% |
| 7 | TrelBERT | 94.4% |
| 8 | Polish RoBERTa-v2 (base) | 94.3% |
| 9 | XLM-RoBERTa (large) + NKJP | 94.2% |
| 10 | Polish RoBERTa (base) | 93.9% |

**Insight:** mDeBERTa NIE jest na KLEJ leaderboard (nikt nie zgłosił results). HerBERT-large dominuje na CDSC-E z 96.4%. **Custom fine-tune HerBERT-large = realistyczny upper bound dla polish NLI**, ale CDSC-E jest na image captions → domain shift do legal text.

### Manual annotation (polish legal/medical NLI)

**Brak publicznego benchmark.** Wszystkie poniższe estymaty są moimi educated guess based on cross-lingual literature i KLEJ:

| Model | Estimated accuracy na polish legal NLI | Confidence |
|-------|-----------------------------------------|------------|
| mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 (out-of-the-box) | **70-78%** | Medium (multilingual but no domain-specific) |
| HerBERT-large fine-tuned na CDSC-E (transfer to legal) | **75-85%** | Medium-low (CDSC-E image captions ≠ legal) |
| HerBERT-large fine-tuned na CDSC-E + adaptation na 100-500 pol legal pairs | **82-90%** | Low-medium (extrapolation) |
| Bielik-11B-v3 z 5-shot prompting | **75-85%** | Medium (LLM-as-judge literature) |
| Bielik-11B-v3 z 15+ shot prompting | **80-88%** | Low-medium (extrapolation) |

---

## 6. Recommendations per use case

### Out-of-the-box dla polish legal text (Twoja domena ChPL/Ulotka/AOTMiT)

**Wybierz: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`**

**Reasoning:**
- ✅ Polish explicitly w training data (1 z 27 langs, ~100k pairs PL z multilingual-nli-26lang-2mil7)
- ✅ MIT license — pełna zgodność z thesis + ewentualna komercjalizacja
- ✅ 275k downloads/mo — battle-tested, łatwy support, dużo tutoriali
- ✅ 0.3B params — production-friendly latency (~5-10ms na A100)
- ⚠ Caveat: machine-translated training data (jakość pl pairs niższa niż EN) → spodziewaj się 70-78% real accuracy na legal text
- ⚠ Caveat: 512 token context window — wystarczy dla typical (claim, evidence) par ale chunk evidence jeśli >400 tokens

### Best accuracy (jeśli compute nie jest constraint)

**Wybierz: HerBERT-large + custom fine-tune na CDSC-E** (lub Polish RoBERTa-v2-large jako alternatywa)

**Reasoning:**
- ✅ KLEJ leaderboard CDSC-E top: 96.4% (HerBERT-large)
- ✅ Polish-native pretraining (NIE machine translation jak mDeBERTa)
- ⚠ Caveat: CDSC-E ≠ legal domain → spodziewaj się drop do 80-85% real polish legal NLI
- ⚠ Caveat: Wymaga +100-500 own labeled pairs dla domain adaptation (manual cost)

**Cost estimate dla fine-tune HerBERT-large + CDSC-E:**
- Hardware: 1× A100 40GB (lub 2× RTX 4090 24GB z gradient accumulation)
- Hyperparams: lr=2e-5, batch=16-32, epochs=10-15 (CDSC-E mały, NIE 40 jak `izaitova` over-trained), warmup_ratio=0.1
- **Wall-clock time: 1-2h na A100** (dataset 8k train pairs)
- **GPU hours estimate: 1-2h** (~$1-5 jeśli rented A100, free jeśli local)
- **Reference notebook:** brak dedykowanego dla CDSC-E na HF, ale standard `transformers` SequenceClassification fine-tune workflow z `allegro/herbert-large-cased` + `allegro/klej-cdsc-e` dataset ⇒ ~50 lines of code (custom)

### Best latency (production demo, Gradio inference)

**Wybierz: `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli`** (jeśli akceptujesz cross-lingual transfer dla pl)

**Reasoning:**
- ✅ 0.1B params (3× mniejszy niż mDeBERTa-base)
- ✅ ~6000+ texts/sec na A100 (~2× szybszy niż mDeBERTa-v3-base)
- ✅ MIT
- ⚠ Caveat: pl NIE w XNLI 15 training → tylko cross-lingual transfer, accuracy spadek ~5-10pp vs mDeBERTa
- ⚠ Caveat: Avg XNLI 0.713 (dużo niżej niż 0.808 mDeBERTa-v3-base)
- **Alternative:** mDeBERTa-v3-base z ONNX export + INT8 quantization → ~2× speedup z minimal accuracy loss, lepsza opcja niż MiniLM

**Lepszy choice dla latency w prawdziwym scenariuszu:** mDeBERTa-v3-base + ONNX Runtime + INT8 quantization (~50% accuracy zachowany przy 2× throughput).

### Best cost dla continuous improvement loop (re-run NLI na thousands pairs)

**Wybierz: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`** (ten sam jak default)

**Reasoning:**
- 0.3B params → na 1× A100 możesz przetworzyć **~3-5M par/godzinę** (batch=64, sequence_length=128)
- Per-cycle cost dla 10k par: <1 minuta na A100
- Bielik-11B-v3 dla porównania: **~3-5h dla 10k par** (15-shot prompting, batch=4)
- Cost ratio: **~100-200× cheaper** mDeBERTa vs LLM-as-judge

---

## 7. Custom fine-tune feasibility

### HerBERT-large + CDSC-E — szczegóły implementacji

**Prerequisites:**
```bash
uv pip install transformers>=4.39 datasets>=2.20 torch accelerate
```

**Reference workflow** (estymata kosztów na A100 40GB):

```python
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer
)
from datasets import load_dataset

# 1. Load dataset (10k pairs, 8k train)
dataset = load_dataset("allegro/klej-cdsc-e")

# 2. Tokenize
model_name = "allegro/herbert-large-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize(example):
    return tokenizer(
        example["sentence_A"], example["sentence_B"],
        truncation=True, padding="max_length", max_length=128
    )
dataset = dataset.map(tokenize, batched=True)

# 3. Model (3-class: entailment/neutral/contradiction)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=3
)

# 4. Train
training_args = TrainingArguments(
    output_dir="./herbert-large-cdsce-nli",
    num_train_epochs=10,        # NIE 40 (over-fit ryzyko, izaitova robił błąd)
    learning_rate=2e-05,
    per_device_train_batch_size=16,  # HerBERT-large ~1.6 GB → bezpieczne
    per_device_eval_batch_size=32,
    warmup_ratio=0.1,
    weight_decay=0.01,
    fp16=True,                  # HerBERT-large supports fp16 (unlike mDeBERTa-v3)
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
)

trainer = Trainer(
    model=model, args=training_args,
    train_dataset=dataset["train"], eval_dataset=dataset["validation"],
    tokenizer=tokenizer,
)
trainer.train()
trainer.evaluate(dataset["test"])  # Expected: ~95-96% accuracy (KLEJ-comparable)
```

**Expected results:**
- **Training time:** 1-2h na A100 40GB (8k samples × 10 epochs × ~2 sec/step at batch=16)
- **Final test accuracy:** ~95-96% (KLEJ leaderboard reference: HerBERT-large ⇒ 96.4%)
- **GPU hours:** ~2h
- **Cost (rented A100):** ~$2-5 (RunPod/Vast.ai), free jeśli lokalna karta lub PJATK access

### Reference notebooks / code

- **Brak dedykowanego HF notebook** dla `allegro/klej-cdsc-e` w 2026-05
- **Standard reference:** [HuggingFace Trainer NLI tutorial](https://huggingface.co/docs/transformers/tasks/sequence_classification) — uniwersalny, action ~30 min adaptation pod CDSC-E
- **HerBERT GitHub:** https://github.com/allegro/HerBERT — ma fine-tune scripts dla KLEJ, ale stare (PyTorch 1.x era), wymaga port do nowych transformers

### Expected accuracy improvement vs frozen mDeBERTa

| Model | Estimated accuracy na **CDSC-E** test | Estimated accuracy na **polish legal NLI** (Twoja domena) |
|-------|----------------------------------------|------------------------------------------------------------|
| Frozen `mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (zero-shot) | ~75-82% | **~70-78%** |
| Fine-tuned HerBERT-large na CDSC-E | **~95-96%** (KLEJ-verified) | **~75-85%** (domain shift penalty) |
| Fine-tuned HerBERT-large na CDSC-E + 200 own legal pairs | (out-of-scope — CDSC-E test się starzeje) | **~82-90%** (estymata) |

**⚠ Honest disclaimer:** Polish legal NLI accuracy estymaty są extrapolation z cross-lingual NLI literature. Brak public benchmark dla polish legal/medical NLI w 2026. **Prawdziwa walidacja wymaga manual annotation 100-500 par z Twojego korpusu** (ChPL+Ulotka+AOTMiT) jako gold standard test set.

---

## 8. Decision rationale dla pracy inżynierskiej

**Rekomendowany stack dla M. Sochackiej (RAG halu detection):**

1. **Default model:** `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`
   - Industry standard, defensible w pracy ("most-downloaded multilingual NLI w 2026")
   - MIT compliance OK
   - 70-78% expected accuracy na polish legal — sufficient dla **first iteration baseline**

2. **Iteration 2 enhancement:** Custom HerBERT-large fine-tune na CDSC-E
   - Tylko jeśli iteration 1 metrics pokażą NLI bottleneck (kappa <0.50 vs manual)
   - Cost: 1-2h compute + 1 dzień engineering
   - Expected lift: +5-10pp na polish legal

3. **Bielik-11B-v3 jako "oracle baseline"** w ablation studies (RQ2 H2 — judge agreement)
   - NIE używaj w production loop (cost prohibitive)
   - Użyj do walidacji że dedicated NLI nie zostaje 10pp+ za LLM judge
   - Mówi w R8: "future work — instruction-tuned LLM-as-judge może zastąpić dedicated NLI gdy compute budget nie limitujący"

**Anti-recommendation:**
- NIE inwestuj w `izaitova/herbert-large-cased_nli` (reproducibility gap, undocumented)
- NIE używaj English-only modeli (deberta-v3-large-zeroshot-v2.0, ModernBERT-NLI, cross-encoder/nli-deberta-v3-large) — żaden polish coverage
- NIE marnuj compute na xlm-v-base (0.8B params bez Polish accuracy benefit vs mDeBERTa-base 0.3B)

---

## Sources

- [MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)
- [MoritzLaurer/mDeBERTa-v3-base-mnli-xnli](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli)
- [MoritzLaurer/xlm-v-base-mnli-xnli](https://huggingface.co/MoritzLaurer/xlm-v-base-mnli-xnli)
- [MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli](https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli)
- [MoritzLaurer/bge-m3-zeroshot-v2.0](https://huggingface.co/MoritzLaurer/bge-m3-zeroshot-v2.0)
- [MoritzLaurer/deberta-v3-large-zeroshot-v2.0](https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v2.0)
- [MoritzLaurer/ModernBERT-large-zeroshot-v2.0](https://huggingface.co/MoritzLaurer/ModernBERT-large-zeroshot-v2.0)
- [sileod/mdeberta-v3-base-tasksource-nli](https://huggingface.co/sileod/mdeberta-v3-base-tasksource-nli)
- [knowledgator/comprehend_it-multilingual-t5-base](https://huggingface.co/knowledgator/comprehend_it-multilingual-t5-base)
- [DAMO-NLP-SG/zero-shot-classify-SSTuning-XLM-R](https://huggingface.co/DAMO-NLP-SG/zero-shot-classify-SSTuning-XLM-R)
- [cross-encoder/nli-deberta-v3-large](https://huggingface.co/cross-encoder/nli-deberta-v3-large)
- [tasksource/ModernBERT-base-nli](https://huggingface.co/tasksource/ModernBERT-base-nli)
- [joeddav/xlm-roberta-large-xnli](https://huggingface.co/joeddav/xlm-roberta-large-xnli)
- [izaitova/herbert-large-cased_nli](https://huggingface.co/izaitova/herbert-large-cased_nli)
- [allegro/herbert-large-cased](https://huggingface.co/allegro/herbert-large-cased)
- [allegro/klej-cdsc-e (dataset)](https://huggingface.co/datasets/allegro/klej-cdsc-e)
- [KLEJ Benchmark Leaderboard](https://klejbenchmark.com/leaderboard/)
- [sdadas Hugging Face profile](https://huggingface.co/sdadas)
- [CYFRAGOVPL/PLLuM-12B-instruct](https://huggingface.co/CYFRAGOVPL/PLLuM-12B-instruct)
- [speakleash/Bielik-11B-v3.0-Instruct](https://huggingface.co/speakleash/Bielik-11B-v3.0-Instruct)
- [ipipan/pl_nask](https://huggingface.co/ipipan/pl_nask)
- [Polish Natural Language Inference and Factivity (Ziembicki et al., arXiv 2201.03521)](https://arxiv.org/abs/2201.03521)
- [PolEval 2025 Tasks](https://poleval.pl/tasks/)
- [PLLuM: A Family of Polish Large Language Models (arXiv 2511.03823)](https://arxiv.org/abs/2511.03823)
- [Bielik 11B v2 Technical Report (arXiv 2505.02410)](https://arxiv.org/pdf/2505.02410)
