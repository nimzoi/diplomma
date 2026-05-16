# Hidden-states halu probes na polish LLM — research 2026-05-16

**Cel:** ocena czy halu probe na ukrytych stanach Bielik / PLLuM jest feasible dla pracy inżynierskiej, recommended starting point + sample code.

---

## 0. Verdict + recommendations

- **Existing polish-specific halu probes (audyt landscape 2024-2026):** **0** publikacji robiących linear/MLP probe na hidden states Bielik / PLLuM / RoBERTa-large-PL z hallucination labels. Polish ekosystem zatrzymał się na safety classifiers (Bielik Guard — RoBERTa, NIE probe) i fake news detection (POLygraph — text-only, NIE hidden states).
- **First-mover potential dla pracy: HIGH.** Brak literatury Polish-specific = realna kontrybucja, nawet w wąskim eksperymencie pilotażowym (1 probe × 1 layer × 200 par).
- **Recommended starting point:** **fork `obalcells/hallucination_probes`** (Apache-2.0, Mistral support, LoRA + linear value head). Bielik 11B v2 to Mistral architecture (50 warstw via Depth Up-Scaling z Mistral 7B v0.2), więc adapter jest minimalny — głównie config + sprawdzić head_dim/intermediate_size.
- **Recommended layer choice dla Bielik 11B (50 warstw):** **layer 47** (= `⌊0.95 × 50⌋`), zgodnie z heurystyką Balcells et al. (arXiv:2509.03531). Fallback: ostatnie 2-3 warstwy aggregated (avg) lub Bayesian search (Liang & Wang 2025) jeśli czas pozwoli.
- **Recommended probe architecture:** **linear primary** (logistic regression na single layer activations — najprostsze, najmniej overfitting na 200 par) + **MLP fallback** (1 hidden layer 512→1, jeśli linear AUROC <0.70). NIE LoRA (wymaga regularization KL i większego data setu, ryzyko behavior drift).
- **Recommended extraction tool:** **PyTorch native `register_forward_hook`** + HF `output_hidden_states=True`. `transformer-lens` NIE obsługuje natively 50-warstwowego upscaled Mistral (lista Model Properties pokazuje tylko Mistral 32-layer); custom HookedTransformerConfig wymagałby dodatkowej pracy. `nnsight` to overhead dla małego eksperymentu pilotażowego.

**Defensibility:** Eksperyment pilotażowy (~200 par psych eval set z corpusu pharma) wyłącznie deskryptywny — *„is hidden-states probe na polish Mistral-derived model technicznie feasible?"* — NIE *„is it production-ready halu detector"*. Wynik AUROC nawet ~0.70-0.75 wystarczy jako proof-of-concept + komentarz że obalcells reportuje 0.87-0.90 na English LLM (gap-analysis dla R8).

---

## 1. Existing polish-specific halu probes

Wynik audytu (WebSearch GitHub + arXiv + HuggingFace, May 2026):

| Projekt | Co robi | Probe? | Polish LLM? | Halu? |
|---|---|---|---|---|
| `speakleash/bielik-guard` (arXiv:2602.07954) | Safety classifier (5 kategorii: hate/vulgarity/sexual/crime/self-harm) | NIE — fine-tuned RoBERTa head | tak — RoBERTa-base PL | NIE |
| `MarBry111/Fake-News-Detection-PL` | Fake news classifier (statements) | NIE — supervised BERT | tak | częściowo (fact-checking) |
| `POLygraph` (arXiv:2407.01393) | Polish fake news dataset 40k articles | NIE — dataset only | tak | NIE (fake news ≠ halu) |
| Polish NLI/Factivity (arXiv:2201.03521) | BERT factivity F1 ~0.89-0.91 | NIE — task fine-tuning | tak | NIE (factivity ≠ halu) |
| PLLuM (arXiv:2511.03823) | Polish 8-70B family Llama/Mistral pretrained | brak interpretability w paper | tak | hybrid output correction (filters + ML classifier post-gen) |
| Bielik 11B v2/v3 (arXiv:2505.02410, 2505.02550) | Polish 11B Mistral upscaled | brak hidden-states probing | tak | "Tricky Questions" benchmark behavioral, NIE internal |
| **Polish hidden-states halu probe** | — | **0 wyników** | — | — |

**Wniosek:** Polish ekosystem ma:
- (a) safety/moderation classifiers (Bielik Guard, RoBERTa-based — NIE probe)
- (b) fact-checking datasets (POLygraph — text-only)
- (c) post-generation filtering (PLLuM hybrid module)

**Nikt nie zrobił linear/MLP probe na hidden states polish LLM z hallucination labels.** Verification: search queries `"Bielik" OR "PLLuM" probing classifier hallucination`, `polish language model factuality detection internal states`, `"Bielik" arxiv 2026 evaluation hallucination` — wszystkie zwracają tylko technical reports modeli + general English papers.

**Caveat:** Mogą istnieć niepublikowane prace dyplomowe na PJATK / PW / UJ których nie ma na arXiv. Twarda weryfikacja wymagałaby przeszukania ZBC/RUJ/Cybra/biblioteki PJATK — out of scope tego researchu.

---

## 2. Reference implementations comparison

| Repo | Stars (est.) | Last commit | License | Polish-compat | Adaptation effort dla Bielik |
|---|---|---|---|---|---|
| **`obalcells/hallucination_probes`** | ~200+ | active 2025 | Apache-2.0 | Mistral Small 24B supported → **Bielik (Mistral-50L) wymaga tylko layer_idx + max_length update** | **LOW** — edit `configs/train_config.yaml` + sprawdzić head_dim |
| `collin-burns/discovering_latent_knowledge` (CCS) | 1k+ | stale 2023 | MIT | Generic transformer; brak Mistral-specific | MEDIUM — CCS unsupervised, wymaga par contrast prompts |
| `EleutherAI/elk` | 200+ | semi-active | MIT | Generic, supports HF models | MEDIUM — newer pipeline, design dla yes-no QA |
| `andyzoujm/representation-engineering` | 1k+ | 2024-25 | MIT | Generic transformer; RepReading + RepControl pipelines | MEDIUM-HIGH — broader scope, halu jako jeden z kilku zastosowań |
| `voidism/Lookback-Lens` (EMNLP 2024) | ~150 | 2024 | MIT | LLaMA-2-7B native; transfers across models 7B→13B | MEDIUM — uses attention maps NIE hidden states, inny paradygmat |
| `GaurangSriramanan/LLM_Check_Hallucination_Detection` (NeurIPS 2024) | ~50 | 2024 | MIT | Generic HF | MEDIUM — focus na metrykach detekcji, mniej infrastruktury |
| `sisinflab/HidingInTheHiddenStates` (ACL 2025) | ~20 | 2025 | MIT | Generic | MEDIUM — extends SAPLMA, factuality-encoding analiza |
| **SAPLMA (Azaria & Mitchell, EMNLP 2023)** | (kod był załączony) | 2023 | research code | Generic; 3 hidden layers MLP (256→128→64) | HIGH — stary kod, brak active maintenance |

**Rekomendacja:** `obalcells/hallucination_probes` jako **primary fork**. Powody:
1. **Mistral architecture native** — Bielik 11B v2 = upscaled Mistral 7B v0.2 (50L × 4096 hidden_size × 32 heads × 8 KV heads × intermediate 14336).
2. **Apache-2.0** — zgodne z thesis licensing.
3. **Active maintenance** + production-ready setup (Modal backend + Streamlit demo opcjonalnie).
4. **Token-level + span-level loss** — pasuje do RAG ground-truth setup (per-token labels z error annotations).
5. **Reported AUROC 0.87-0.90** na English Mistral Small 24B — daje sensowny upper bound expectation.

---

## 3. Extraction tool comparison

| Tool | API | Bielik (50L Mistral) compat | Performance overhead | Debug-friendliness | Rekomendacja |
|---|---|---|---|---|---|
| **PyTorch `register_forward_hook`** | manual, granular | **YES** — działa z dowolną nn.Module | minimalne | wysoka (full Python control) | **PRIMARY** |
| **HF `output_hidden_states=True`** | declarative `model(..., output_hidden_states=True)` zwraca tuple `(L+1) × [B, T, H]` | **YES** | umiarkowane (cały stack zachowany w pamięci) | wysoka | **PRIMARY (alternative)** |
| `transformer-lens` (HookedTransformer) | clean API (`run_with_cache`, `resid_pre/mid/post`) | **NO native** — lista wspiera tylko mistral-7b (32L). Custom 50L Mistral wymagałby ręcznego `HookedTransformerConfig` + weight remapping | wysokie (memory dla cache) | bardzo wysoka jeśli wspiera | NIE dla pilota |
| `nnsight` (NDIF/EleutherAI) | deferred execution `with model.trace(...)` + `.save()` | YES — generic LanguageModel wrapper przez HF | umiarkowane | medium (deferred = trudne stack traces) | overhead dla 200 par |
| `torch.fx` (graph rewriting) | low-level | YES ale wymaga symbolic tracing — Mistral RoPE może łamać | niskie | niska (debug graph trudny) | NO |
| RepE library (`andyzoujm/representation-engineering`) | pipelines | YES via HF | wysokie (full pipeline) | medium | overkill dla single probe |

**Rekomendacja:** **PyTorch hooks + HF `output_hidden_states=True`**. Sample code w sekcji 9.

**Memory check Bielik 11B w bf16 + 50 layers × 4096 hidden × seq_len 1024 × batch 4:**
50 × 4096 × 1024 × 4 × 2 bytes = **1.6 GB tylko same hidden states**. + ~22 GB samego modelu = ~24 GB. **L40S/A100 40GB OK, RTX 3090 24GB ryzykowne** — fallback: int8 (BnB) lub flush hidden states per batch do dysku (numpy memmap).

---

## 4. Layer choice strategy

| Heurystyka | Reasoning | Recommended dla Bielik 50L |
|---|---|---|
| **`⌊0.95 × num_layers⌋`** (Balcells et al. 2025, obalcells/hallucination_probes) | "Near-output" — model już skondensował semantykę, przed projection do vocab | **layer 47** — primary choice |
| Middle layers (~50-60%) | Burns CCS 2022, ELK — knowledge linearly probable middle | layer 25-30 fallback |
| Last layer | SAPLMA Azaria & Mitchell — final hidden | layer 49 alternative |
| Bayesian search (GP) | Liang & Wang Dec 2025 — automatically found layer 29 dla Qwen2.5-7B, layer 22 dla Llama3.1-8B (NIE near-output!) | TIME-COST — 3 init + 5 iter = ~8 trening run. Pomijać w pilocie. |
| **Aggregated last 2-3 layers** (avg or concat) | Robustness, jeśli single layer noisy | secondary — sprawdzić tylko jeśli single-layer AUROC <0.70 |
| Per-attention-head probing | RepE, EleutherAI ELK | overkill dla pilota |

**Wniosek dla pilota Iteracji 1:** Start z **layer 47** (single layer, linear probe). Jeśli AUROC ≥0.75 → done, dokumentuj. Jeśli <0.70 → spróbuj aggregated last 3 (47+48+49 avg).

**Caveat z literatury:** Liang & Wang (arXiv:2512.20949) pokazali że Bayesian search znajduje NIE near-output layers — czasem warstwy mid (Llama 22/32 = 69%, Qwen 29/35 = 83%). Dla 50L Bielik mid-late range to ~35-47. **Defensive answer dla promotora:** *„świadomie wybrałam ⌊0.95×L⌋ jako sensible default per Balcells 2025; pełna layer search out-of-scope dla pilota."*

---

## 5. Probe architecture choices

Per Liang & Wang Dec 2025 + Farquhar 2024 + obalcells 2025:

| Architecture | Param count (Bielik 4096 hidden) | AUROC range (English literature) | Risk overfitting (200 par) | Rekomendacja pilot |
|---|---|---|---|---|
| **Linear (logistic regression)** | 4097 (W + bias) | LongFact 0.82-0.90, RAGTruth in-dist 0.79 | LOW | **PRIMARY** |
| MLP 1 hidden (4096→512→1) | ~2.1M | LongFact 0.85-0.95 (+5-8pp vs linear) | MEDIUM | fallback jeśli linear <0.70 |
| SAPLMA-style MLP (4096→256→128→64→1) | ~1.1M | EMNLP 2023 promising | MEDIUM-HIGH | NIE — overengineered dla 200 par |
| Sparse autoencoder probe | depends | — | HIGH (wymaga SAE pre-training) | NIE — out of scope |
| Attention-based probe | depends | — | HIGH | NIE |
| LoRA + value head (obalcells) | LoRA r=16 α=32 across all layers + 4097 head | LongFact 0.87-0.90 | MEDIUM (KL reg λ=0.05 niezbędny) | NIE dla pilota (wymaga większego data + KL regularization tuning) |

**Defensive argument dla promotora:** *„Linear probe to baseline którego nie pominiesz w żadnej publikacji 2024-2026. Dubanowska et al. (EMNLP 2025) pokazują że logistic regression osiąga 0.79 AUROC na RAGTruth in-distribution — comparable do ReDeEP (SOTA). MLP/LoRA value head poprawia o 3-8pp tylko gdy mamy >10k examples. Dla pilota 200 par psych eval — linear unika overfitting."*

---

## 6. Training data format

| Format | Pros | Cons | Rekomendacja pilot |
|---|---|---|---|
| **Per-sequence label (sentence-level)** — `(hidden_state_at_last_token, halu_bool)` | proste; pasuje do RAG QA setup | grube; tracimy info gdzie hallucination się dzieje | **PRIMARY dla pilota** — eval set 200 par już ma sentence-level annotations |
| Per-token label — `(hidden_state_at_token_i, halu_bool_i)` | dokładne; pasuje do entity-level halu (Balcells, Liang) | wymaga manual token-level annotation = **EXPENSIVE** | NIE dla pilota (200 par × ~50 tokens = 10k labels manual) |
| Per-span label (entity/claim) | balance; HealthBench-style | annotation pipeline wymagany (Anthropic API w obalcells) | secondary |
| Contrast pairs (CCS-style) | unsupervised; nie potrzebuje labels | wymaga par yes/no o tej samej semantyce; trudne dla open-ended RAG | NIE |
| Synthetic halu via prompting | tanie; skalowalne | distribution shift vs real halu — Dubanowska 2025 pokazuje że to fail OOD | tylko jako augmentation |

**Training data dla Bielik halu probe:**

**Pozytywne (correct):**
- 100 par z eval set (psych ATC N05-N06) gdzie Bielik generuje correct retrieval-grounded answer (judge LLM ≥0.8 confidence) → zbierać hidden state @ layer 47 ostatniego non-pad tokena → label 0

**Negatywne (hallucinated):**
- 100 par z eval set gdzie Bielik generuje fact-incorrect answer (judge ≥0.8 confidence że HALU) → hidden state @ layer 47 ostatni non-pad → label 1
- ALTERNATIVE: induce halu przez ablation context (give query, withhold retrieval → model halucinuje) — ale to artificial

**Class balance:** ~50/50 ideally; jeśli unbalanced (np. baseline retrieval generuje >70% correct), użyć class_weight w logistic regression.

**Split:** 80/20 train/val z internej eval set; bez OOD test (200 par za mało żeby się dzielić jeszcze raz). **Honest framing w R8:** *„Pilot bez OOD testu — Dubanowska 2025 ostrzega że probes generalize poorly out-of-distribution, więc niezbędne future work."*

---

## 7. Evaluation methodology

Per **Dubanowska et al. (arXiv:2509.19372, EMNLP 2025)** — *„Representation-based Broad Hallucination Detectors Fail to Generalize Out of Distribution"*:

**Kluczowe findings:**
- In-distribution AUROC ~0.79-0.95 — łatwo osiągalne
- Out-of-distribution (np. RAGTruth → SQuAD) — **wszystkie metody close to random (0.50-0.52)**
- ReDeEP (SOTA) NIE outperformuje logistic regression po kontroli na spurious correlations
- Naive classifier (task-type only, NO hidden states) osiąga comparable AUROC do sophisticated methods

**Recommended evaluation dla pilota:**

| Metryka | Co liczyć | Defensive narrative |
|---|---|---|
| **AUROC** | sklearn `roc_auc_score(y_true, probe_scores)` | primary metric, comparable do literatury |
| **Bootstrap CI (95%)** | 1000 bootstrap resamples, percentile method | per "Mirage of Halu Detection" Apple 2025 — single AUROC bez CI = nieuczciwe |
| **PR-AUC + balanced accuracy** | sklearn `average_precision_score` | przy class imbalance |
| **Calibration: ECE** | reliability diagram + Expected Calibration Error | jeśli scores są kalibrowane można threshold tunować |
| **Naive baseline** | Logistic regression na long-of-query lub query-length features (NO hidden states) | per Dubanowska — must beat to show hidden states matter |
| **Comparison vs LLM-as-judge** | Probe AUROC vs Bielik judge agreement | uczciwy benchmark |

**Bootstrap CI w Python (1000 resamples):**

```python
from sklearn.utils import resample
from sklearn.metrics import roc_auc_score
import numpy as np

scores = []
for _ in range(1000):
    idx = resample(np.arange(len(y_true)))
    scores.append(roc_auc_score(y_true[idx], probe_preds[idx]))
ci_low, ci_high = np.percentile(scores, [2.5, 97.5])
print(f"AUROC: {np.mean(scores):.3f} [{ci_low:.3f}, {ci_high:.3f}]")
```

**OOD test (jeśli budżet czasu pozwoli):** trenuj probe na 80% psych eval set → test na 20% psych + dodatkowo na non-psych pharma sample (np. 50 par z kardiologii ATC C). Jeśli AUROC dropuje do ~0.55 — zgodne z Dubanowska, należy honestly fram w R8.

---

## 8. Bielik-specific considerations

**Architektura (z arXiv:2505.02410v2 Bielik 11B v2 Technical Report):**

| Parametr | Wartość |
|---|---|
| Base | Mistral 7B v0.2 |
| Layers (`num_hidden_layers`) | **50** (Depth Up-Scaling: 32→50) |
| Hidden size | **4096** |
| Attention heads | 32 |
| Key/Value heads (GQA) | 8 |
| Head dim | 128 |
| Intermediate size | 14336 |
| Activation | SwiGLU |
| Vocab size | 32128 |
| Max position | 32768 (RoPE θ=1000000) |

**Memory dla extraction:**
- Model bf16: ~22 GB VRAM
- Hidden states 50L × 4096H × seq_len × batch:
  - seq_len 512, batch 4: ~0.8 GB
  - seq_len 1024, batch 4: ~1.6 GB
  - seq_len 2048, batch 8: ~6.4 GB
- **Praktycznie:** A100 40GB / L40S 48GB komfortowo; RTX 3090 24GB wymaga batch=1-2

**Quantization:**
- **int8 (bitsandbytes)** — zmniejsza model do ~11 GB; według Bielik-Q2-Sharp paper (arXiv:2603.04162) jakość poniżej 4-bit znacząco spada → int8 OK, ale **NIE używaj 2-bit** dla halu probe (hidden states zniekształcone)
- **nf4 (QLoRA-style)** — model ~6 GB; ALE: hidden states po dequantization mogą mieć inną dystrybucję niż bf16 → probe trenowany na nf4 NIE transferuje na bf16 inference. **Rekomendacja: bf16 do extraction + int8 tylko jeśli VRAM bottleneck.**

**Tokenizer caveat:** Bielik używa custom Polish-optimized tokenizer (vocab 32128, NIE 32000 jak vanilla Mistral). Sprawdzić że `add_special_tokens=False` przy concat query+context, inaczej `<s>` na środku łamie attention.

**ChatML format:** Bielik 11B v2.2-Instruct używa ChatML. Hidden state extraction na surowych logitach (po `apply_chat_template`) — ostatni non-pad token = ostatni token wygenerowanej assistant response.

---

## 9. Sample code dla naszego use case

Working code template — extraction + linear probe training na Bielik 11B v2.2-Instruct.

### 9.1 Extraction hidden states

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from torch.nn.functional import pad

MODEL_ID = "speakleash/Bielik-11B-v2.2-Instruct"
LAYER_IDX = 47  # 0.95 * 50

tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    output_hidden_states=True,  # KEY
)
model.eval()

@torch.no_grad()
def get_hidden_at_layer(messages: list[dict], layer_idx: int = LAYER_IDX) -> torch.Tensor:
    """
    Returns hidden state @ layer_idx for the LAST non-pad token.
    Shape: [hidden_size] = [4096]
    """
    inputs = tok.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    out = model(**inputs, output_hidden_states=True)
    # out.hidden_states: tuple of (L+1) tensors, each [B, T, H]
    # idx 0 = embeddings, idx 1..L = layer outputs
    h = out.hidden_states[layer_idx + 1]  # +1 because index 0 is embeddings

    # Last non-pad token (assumes left-padding OR no padding for batch=1)
    last_idx = inputs["attention_mask"].sum(dim=-1) - 1
    return h[torch.arange(h.size(0)), last_idx].float().cpu()  # [B, H]


# Usage: build dataset
import pandas as pd
import numpy as np

records = []  # list of {"messages": [...], "label": 0/1}
# ... fill from eval set 200 par with judge LLM labels ...

X, y = [], []
for r in records:
    h = get_hidden_at_layer(r["messages"], LAYER_IDX)
    X.append(h.squeeze().numpy())
    y.append(r["label"])

X = np.stack(X)  # [N, 4096]
y = np.array(y)  # [N]
np.savez("bielik_l47_psych_halu.npz", X=X, y=y)
```

### 9.2 Linear probe training + bootstrap CI

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample

data = np.load("bielik_l47_psych_halu.npz")
X, y = data["X"], data["y"]

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

scaler = StandardScaler().fit(X_tr)
X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)

clf = LogisticRegression(
    C=1.0,
    class_weight="balanced",
    max_iter=1000,
    random_state=42,
).fit(X_tr_s, y_tr)

p_te = clf.predict_proba(X_te_s)[:, 1]

# Bootstrap CI 95%
B = 1000
aucs = []
for _ in range(B):
    idx = resample(np.arange(len(y_te)), random_state=None)
    if len(np.unique(y_te[idx])) < 2:
        continue
    aucs.append(roc_auc_score(y_te[idx], p_te[idx]))
auc_mean = np.mean(aucs)
ci_low, ci_high = np.percentile(aucs, [2.5, 97.5])

pr_auc = average_precision_score(y_te, p_te)

print(f"AUROC: {auc_mean:.3f} [95% CI: {ci_low:.3f}, {ci_high:.3f}]")
print(f"PR-AUC: {pr_auc:.3f}")
print(f"Coef norm: {np.linalg.norm(clf.coef_):.2f}")
```

### 9.3 MLP fallback (jeśli linear <0.70)

```python
import torch.nn as nn
import torch.optim as optim

class ProbeMLP(nn.Module):
    def __init__(self, hidden_size=4096, mid=512):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden_size, mid),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(mid, 1),
        )
    def forward(self, x):
        return self.net(x).squeeze(-1)

probe = ProbeMLP().cuda()
opt = optim.AdamW(probe.parameters(), lr=1e-3, weight_decay=1e-4)
crit = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([(1 - y_tr.mean()) / y_tr.mean()]).cuda())

X_tr_t = torch.from_numpy(X_tr_s).float().cuda()
y_tr_t = torch.from_numpy(y_tr).float().cuda()

for epoch in range(50):
    probe.train()
    opt.zero_grad()
    logits = probe(X_tr_t)
    loss = crit(logits, y_tr_t)
    loss.backward()
    opt.step()
    if epoch % 10 == 0:
        probe.eval()
        with torch.no_grad():
            p = torch.sigmoid(probe(torch.from_numpy(X_te_s).float().cuda())).cpu().numpy()
            print(f"Epoch {epoch}: AUROC = {roc_auc_score(y_te, p):.3f}")
```

### 9.4 Naive baseline (Dubanowska sanity check)

```python
# Probe MUST beat trivial features that have nothing to do with hidden states
from sklearn.linear_model import LogisticRegression

# Feature: query length + context length (no hidden states)
naive_features = np.array([
    [len(r["messages"][-1]["content"]), len(str(r["messages"]))]
    for r in records
])
nf_tr, nf_te = naive_features[:len(X_tr)], naive_features[len(X_tr):]

naive_clf = LogisticRegression().fit(nf_tr, y_tr)
naive_p = naive_clf.predict_proba(nf_te)[:, 1]
print(f"Naive baseline AUROC: {roc_auc_score(y_te, naive_p):.3f}")
# If naive ≈ probe AUROC → probe IS NOT learning hallucination signal
```

---

## 10. Iter. 1 recommended pipeline

**Założenie:** Iteracja 1 ma 1-2 tygodnie czasu na halu probe pilot (per plan w `02b_konspekt_v3_updates.md` II.16).

**Step-by-step:**

1. **Day 1 — Setup.**
   - Sklonować `obalcells/hallucination_probes` (Apache-2.0) → fork `magdas/hallucination_probes_bielik`
   - `uv venv --python 3.13` + `uv sync` (lub `pip install transformers torch scikit-learn bitsandbytes` jeśli minimalna ścieżka — own code z sekcji 9)
   - Sprawdzić `nvidia-smi` — wymagane ≥24 GB VRAM bf16

2. **Day 2 — Architecture check.**
   - Pobrać Bielik 11B v2.2 config.json — verify 50L × 4096H × 32 heads × 8 KV heads
   - Sanity test: załadować model w bf16 + 1 prompt forward pass + sprawdzić `out.hidden_states[48].shape == (1, T, 4096)`

3. **Day 3-4 — Data prep.**
   - Z eval set 200 par psych ATC N05-N06 wybrać ~100 correct + ~100 halu
   - **Label source:** Bielik judge LLM (kandydat z DEC `<judge_model>`) z confidence ≥0.8 (manual override 20% sample dla calibration)
   - Save `bielik_l47_psych_halu.npz` per code 9.1

4. **Day 5 — Linear probe + bootstrap CI.**
   - Trening per code 9.2
   - **Done criterion:** AUROC ≥0.70 z 95% CI lower bound ≥0.60 → success, log w MLflow
   - **Sanity:** naive baseline (code 9.4) musi być znacząco niższy (≥10pp gap) — inaczej probe nie uczy się halu signal

5. **Day 6 — Fallback (jeśli linear <0.70).**
   - MLP probe per code 9.3
   - Aggregated last 3 layers (avg 47+48+49)
   - **Done criterion:** którakolwiek wariant ≥0.70 AUROC

6. **Day 7 — Write-up dla R7.**
   - Wyniki tabela: linear AUROC + CI, MLP AUROC + CI, naive baseline, comparison z LLM-as-judge
   - **Honest framing:** *„Pilot na psych eval subset (n=200, single layer 47, linear probe). AUROC X.XX [CI low, high] comparable z literaturą English (obalcells 0.87-0.90 na English Mistral 24B). OOD testowanie poza zakresem — per Dubanowska 2025 future work wymaga cross-domain split."*
   - Decision log: czy probe wchodzi do final pipeline jako runtime detector (R5 architecture) czy zostaje analytic R7 wynik

**Total effort estimate:** ~30-40 godzin pracy realnej. Zgodne z scope inżynierki (NIE doktorat).

**Co NIE robić w Iteracji 1:**
- Bayesian layer search (czasochłonne, marginal gain)
- LoRA probe (wymaga większego data setu + KL reg tuning)
- SAE probe (wymaga pre-trening SAE — z zakresu)
- Cross-model transfer test (Bielik → PLLuM)
- Real-time integration z RAG generation (production hardening)

**Co odłożyć do future work (R8 sekcja Future Work):**
- OOD test (psych → kardio → onko)
- Cross-register probe (czy probe trenowany na ChPL hidden states detektuje halu na Ulotka context — RQ5 synergy!)
- Probe ensemble (linear + MLP + Lookback Lens attention features)
- Real-time threshold tuning per query type

---

## Bibliografia kluczowych źródeł

**Reference implementations:**
1. Balcells O. et al. (2025). *Real-Time Detection of Hallucinated Entities in Long-Form Generation.* arXiv:2509.03531. https://github.com/obalcells/hallucination_probes
2. Burns C. et al. (2022). *Discovering Latent Knowledge in Language Models Without Supervision.* arXiv:2212.03827. https://github.com/collin-burns/discovering_latent_knowledge
3. EleutherAI. *elk: Eliciting Latent Knowledge.* https://github.com/EleutherAI/elk
4. Zou A. et al. (2023). *Representation Engineering: A Top-Down Approach to AI Transparency.* arXiv:2310.01405. https://github.com/andyzoujm/representation-engineering
5. Chuang Y.-S. et al. (2024). *Lookback Lens: Detecting and Mitigating Contextual Hallucinations Using Only Attention Maps.* EMNLP 2024. https://github.com/voidism/Lookback-Lens
6. Azaria A., Mitchell T. (2023). *The Internal State of an LLM Knows When It's Lying* (SAPLMA). EMNLP 2023. arXiv:2304.13734.

**Krytyka metodologii i state-of-the-art 2025:**
7. **Dubanowska Z., Żelaszczyk M., Brzozowski M., Mandica P., Karpowicz M.** (2025). *Representation-based Broad Hallucination Detectors Fail to Generalize Out of Distribution.* EMNLP 2025 Findings. arXiv:2509.19372.
8. Kulkarni A. et al. (Apple) (2025). *Evaluating Evaluation Metrics — The Mirage of Hallucination Detection.* EMNLP 2025 Findings. arXiv:2504.18114.
9. Liang S., Wang H. (2025). *Neural Probe-Based Hallucination Detection for Large Language Models.* arXiv:2512.20949.
10. Farquhar S. et al. (2024). *Detecting Hallucinations Using Semantic Entropy.* Nature 630, 625-630.
11. Sriramanan G. et al. (2024). *LLM-Check: Investigating Detection of Hallucinations.* NeurIPS 2024. https://github.com/GaurangSriramanan/LLM_Check_Hallucination_Detection
12. Sisinflab (2025). *Are the Hidden States Hiding Something? Testing Factuality-Encoding Capabilities.* ACL 2025. arXiv:2505.16520. https://github.com/sisinflab/HidingInTheHiddenStates

**Polish LLM:**
13. SpeakLeash + ACK Cyfronet AGH (2025). *Bielik 11B v2 Technical Report.* arXiv:2505.02410.
14. SpeakLeash (2025). *Bielik v3 Small Technical Report.* arXiv:2505.02550.
15. PLLuM Consortium (2025). *PLLuM: A Family of Polish Large Language Models.* arXiv:2511.03823.
16. SpeakLeash (2026). *Bielik Guard: Efficient Polish Language Safety Classifiers.* arXiv:2602.07954.

**Tooling:**
17. TransformerLens documentation: https://transformerlensorg.github.io/TransformerLens/
18. nnsight (NDIF/EleutherAI): https://nnsight.net/
19. HuggingFace Transformers `output_hidden_states`: https://huggingface.co/docs/transformers/en/main_classes/output

**Benchmarki:**
20. RAGTruth: https://github.com/ParticleMedia/RAGTruth (arXiv:2401.00396)
21. HaluEval: https://github.com/RUCAIBox/HaluEval (EMNLP 2023)
22. LongFact (obalcells annotations on HF): https://huggingface.co/collections/obalcells/hallucination-probes
