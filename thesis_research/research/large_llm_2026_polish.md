# Large LLM 2026 dla polish RAG — research 2026-05-16

**Cel:** Audyt frontier LLMs (do ~34B params) pod kątem zastąpienia/uzupełnienia Bielik 11B v3 w pipeline halu detection. Kryteria: polish coverage, hidden-states probe compatibility, structured output, cost via OpenRouter, self-hosted feasibility w lab GPU.

**Metodologia:** Real verification — HuggingFace model cards, OpenRouter pricing pages, official tech reports (arXiv), Polish LLM Leaderboard (speakleash), benchmark agregaty (CodeSOTA, llm-stats). Data ostatniej weryfikacji: 2026-05-16.

---

## 0. Verdict + top 3 recommendations

| Use case | Recommended model | Reasoning (1 zdanie) |
|---|---|---|
| **Best overall (polish RAG, lab self-hosted)** | **Bielik 11B v3** (stay) | Najlepszy stosunek polish-native quality / VRAM / Apache 2.0 / probe-friendly Mistral arch. |
| **Best polish coverage (production)** | **Llama-PLLuM-70B-instruct** | 74 PLCC, trained na 150B PL tokens, RAG-optimized — ale 140GB VRAM bf16. |
| **Best probe target (multi-model split)** | **Qwen 3.5-27B** (dense) | 36 layers × 6144 hidden = bogata przestrzeń probe; Apache 2.0; tani na OpenRouter. |

**Główna rekomendacja dla pracy:** **Zostań przy Bielik 11B v3 jako primary generator + probe target.** Jeśli budżet czasowy pozwala dodać **secondary multi-model probe comparison** w ablation (Bielik vs Qwen 3.5-27B vs Gemma 3 27B) — to wzmocni RQ4-style robustness story. **NIE rotuj** do PLLuM-70B jeśli lab GPU nie ma 2× H100 (overhead operacyjny zabije iteration speed).

---

## 1. Bielik 11B v3 baseline (current choice)

**Status (refresh 2026-05-16):**
- **Release:** v3.0-Instruct opublikowany 2025-07-30 (base 2025-07-30, instruct kontynuacja)
- **Tech report:** arXiv:2601.11579 "Bielik 11B v3: Multilingual Large Language Model for European Languages"
- **License:** Apache 2.0 (production-friendly, brak NC)
- **HF availability:** `speakleash/Bielik-11B-v3.0-Instruct`, GGUF, FP8-Dynamic (vLLM/SGLang Ada/Hopper)

**Architecture (potwierdzone z tech report v2 + v3 lineage):**
- **Layers:** 50 (depth-upscaled z Mistral 7B v0.2; duplikacja + przycięcie 8+8)
- **Hidden size:** 4096
- **Attention heads:** 32 (Q), KV grouped
- **Intermediate size:** 14336
- **Activation:** SwiGLU
- **Position embedding:** RoPE θ=1,000,000
- **Tokenizer:** APT4 (Polish-optimized, ~10-15% lepsza kompresja PL vs Mistral)
- **Context window:** 131,072 tokens (32K natywnie, rozszerzony przez RoPE scaling)

**Training data:**
- 292B tokens (237B polish + 55B english SlimPajama)
- 20M+ instructions, 17B tokens instruct dataset
- DPO-Positive alignment + GRPO refinement

**Polish benchmarks (zweryfikowane):**
- **EQ-Bench PL:** 71.20
- **MT-Bench PL (5-shot avg):** 65.93
- **PLCC (CodeSOTA, 2026-03):** 78
- **Open PL LLM Leaderboard:** 69.48
- **CPTU-Bench:** 3.73

**Probe compatibility:** ✅ Excellent
- Mistral-derived arch → pełne wsparcie `output_hidden_states=True` w HF transformers
- 50 layers × 4096 = 204,800 features per layer per token → bogata przestrzeń probe
- PyTorch hooks działają out-of-the-box (`model.model.layers[i].register_forward_hook(...)`)
- `transformer-lens` officially supports Mistral architecture (Bielik = Mistral-compatible)

**Compute (lab self-hosted):**
- bf16 inference: ~22 GB VRAM (single A100 40GB lub RTX 4090 24GB tightly)
- FP8 (vLLM/SGLang on Hopper): ~11 GB
- Q4_K_M (GGUF): ~7 GB (RTX 3060 12GB works)

**OpenRouter:** ❌ **NIEDOSTĘPNY na 2026-05-16.** Bielik jest dostępny przez Ollama, AWS Marketplace, bielik.ai chat, PLGrid Portal, self-hosted vLLM/SGLang/TEI. **OpenRouter nie listuje speakleash** w model roster — implikacja: jeśli chcesz API-based access dla research, musisz self-host albo użyć AWS SageMaker.

**Strengths:**
- Best polish-native quality w klasie 11B
- Permissive Apache 2.0
- APT4 tokenizer: -15% input tokens dla polish
- Probe-friendly clean Mistral arch
- FP8 ready (Hopper)

**Weaknesses:**
- Bez OpenRouter — koszt operacyjny self-hostingu
- Stary baseline Mistral 7B (mniej "świeży" niż Qwen 3.5)
- Brak natywnego function calling (prompt engineering only)
- Tylko 11B params — capacity ceiling vs frontier 30B+

---

## 2. Qwen series 2025-2026

### Qwen 3 (baseline, sierpień 2025)
- Sizes: 0.6B, 1.7B, 4B, 8B, 14B, 32B (dense), 30B-A3B / 235B-A22B (MoE)
- Apache 2.0
- 119 języków (Polish included, ale weak per ONERULER)
- Hidden states: standard `output_hidden_states=True`
- **OpenRouter Qwen3-32B:** $0.08/1M input, $0.28/1M output (bardzo tanio)

### Qwen 3.5 Medium (24 lutego 2026) — **kluczowa rodzina dla pracy**
- **Sizes:** 2B, 9B, 27B (dense), 35B-A3B / 122B-A10B (MoE)
- **Flagship 397B-A17B (MoE)** — out of scope (zbyt drogi)
- **Qwen 3.5-27B dense:**
  - Layers: 36
  - Hidden size: 6144
  - Attention heads: 48 (GQA: 6 KV heads)
  - Intermediate size: 32768
  - Context: 131,072 tokens
  - SWE-bench Verified: 72.4 (matching GPT-5 mini)
- **Hybrid attention:** Gated Delta Networks (linear, Mamba2-style gated decay) + full attention w stosunku 3:1 — efficient long context
- **Languages:** 201 języków (up from 119), vocab 250K (up from 150K), Polish encoding +10-60% efficiency

### Qwen 3.5 Small (1 marca 2026)
- 0.8B, 2B, 4B, 9B — on-device focus, nie dla halu detection probe target

### Qwen 3.6 (~kwiecień 2026)
- Qwen3.6-27B dense (lepsze coding), Qwen3.6-35B-A3B MoE
- Per Qwen blog: flagship-level coding w 27B dense

**License:** Apache 2.0 dla open-weight (Qwen 3.5/3.6 medium serie). Qwen3.5-Omni, Qwen3.6-Plus = proprietary (Alibaba Cloud only).

**Polish coverage:**
- Brak dedykowanych polish benchmark scores w Qwen tech report (multilingual aggregate only: NOVA-63 = 59.1)
- **CodeSOTA 2026-03:** Qwen 3.5-27B thinking = 4.34 CPTU-Bench (#2 globally, **higher than Bielik 3.73**)
- **Qwen 2.5-72B-Instruct:** 67.92 Open PL LLM Leaderboard
- Polish per ONERULER (Qwen 2.5): highest avg accuracy mimo że nie dominuje pretraining — sugeruje że Qwen rodzina generalnie dobrze radzi sobie z PL

**OpenRouter pricing (2026-05-16):**
| Model | Input $/1M | Output $/1M | Context |
|---|---|---|---|
| Qwen3-32B | $0.08 | $0.28 | 131K |
| Qwen3.5-27B | $0.195 | $1.56 | 262K |
| Qwen3.6-27B | $0.32 | $3.20 | 262K |

**Probe compatibility:** ✅ Excellent
- HF transformers natively supports Qwen3/3.5/3.6 (`Qwen3ForCausalLM` etc.)
- `output_hidden_states=True` returns tuple per layer
- 36 layers × 6144 = 221,184 features (Qwen 3.5-27B) > Bielik 11B v3 (50 × 4096 = 204,800) per token
- **Caveat:** transformer-lens support dla Qwen 3.5 hybrid attention (Gated Delta + full) może być incomplete — verify before commit. Dla pure-attention Qwen3 dense (32B etc.) — pełne wsparcie.

**Compute (Qwen 3.5-27B):**
- bf16: ~55 GB (A100 80GB / H100 80GB)
- Q8_0: ~29 GB
- Q4_K_M: ~16.5 GB
- **Practical: bf16 NIE mieści się na single H100 z runtime overhead (~62-65 GB)** — wymaga H200 lub 2× GPU

**Structured output:**
- ✅ JSON mode (`response_format: {"type": "json_object"}`)
- ✅ Outlines/constrained decoding (vLLM + guided_json)
- ⚠ **Bug:** Qwen3 w `enable_thinking=false` + guided_json często daje invalid JSON (extra `{`, `[`, ` ``` `). Workaround: `enable_thinking=true` lub post-process strip
- Function calling: native support (qwen-agent ecosystem)

---

## 3. Gemma series 2025-2026

### Gemma 3 (12 marca 2025) — **second tier candidate**
- **Sizes:** 1B, 4B, 12B, 27B (dense, brak MoE)
- **Multimodal:** text + image (SigLip encoder) — vision-language
- **Context:** 128K tokens
- **140+ języków** training data, "out-of-the-box" support 35+ (Polish niegrundownie wymieniony w 35+ ale w 140+ tak)
- **Training data:** 27B model = 14T tokens (vs Bielik 292B → ~50× więcej, ale rozłożone na 140+ języków)

**Gemma 3 27B architecture:**
- Layers: 46
- Hidden size: 4096
- Attention heads: 64 (GQA: 16 KV heads)
- **Alternating attention:** 5× local sliding window (1024 tokens) per 1× global attention
- RMS Normalization, RoPE
- Tokenizer: SentencePiece (256K vocab, Chinese/Japanese/Korean improved)

### Gemma 3n (~maj 2025) — mobile/edge variant
- E2B, E4B effective params (sub-1B aktywowane przez Per-Layer Embeddings)
- Out of scope

### Gemma 4 (2 kwietnia 2026) — **NEW frontier**
- **Sizes:** E2B, E4B (mobile), **31B dense**, **26B A4B (MoE, 8/128 experts active)**
- **License:** Apache 2.0 (UWAGA: Google switched from Gemma Terms of Use → Apache 2.0 dla v4 — production-friendly!)
- **Multimodal:** text + image + video (all sizes) + audio (E2B/E4B natively)
- **Context:** 128K (small) / 256K (medium 31B/26B-A4B)

**Polish coverage:**
- **Gemma 3/4 NIE figuruje w CodeSOTA top 15 polish** — sygnał: polish nie jest priority dla Gemma team
- 140+ languages = covers Polish, ale jakość per-language nie zbenchmarkowana w polish dedicated suite
- Brak Gemma w Open PL LLM Leaderboard top entries (vs Bielik, PLLuM, Mistral Large, Qwen)

**License:** 
- Gemma 3: **Gemma Terms of Use** (restrictive — disallows certain use cases, requires acknowledgment of Google as licensor; bardziej restrictive niż Apache 2.0)
- **Gemma 4: Apache 2.0** (kwantowy skok permissivneness — Google response na konkurencję Qwen)

**OpenRouter pricing (2026-05-16):**
| Model | Input $/1M | Output $/1M | Context |
|---|---|---|---|
| Gemma 3 27B IT | $0.08 | $0.16 | 131K |
| Gemma 4 31B IT | ~similar (dostępny) | — | 256K |
| Gemma 3 4B IT | FREE tier available | — | — |

**Probe compatibility:** ⚠ **Komplikacje vs Mistral/Qwen**
- HF transformers wspiera Gemma 3 (`Gemma3ForCausalLM`, `output_hidden_states=True`)
- **ALE:** Alternating local/global attention (5:1) → hidden states z różnych warstw mają różne charakterystyki receptive field. Probe trenowany na "global" layer feature space może nie generalizować na "local" layers
- **Implikacja dla halu detection probe:** może wymagać per-layer-type stratification w probe training — extra complexity
- 26 hidden layers (Gemma 3 small variants) / 46 layers (Gemma 3 27B) / 31B dense (Gemma 4) — sufficient depth
- transformer-lens: officially supports Gemma 2; Gemma 3/4 support PR-merged status uncertain — **verify przed commit**

**Compute (Gemma 3 27B):**
- bf16: ~54 GB (single A100 80GB / H100 80GB)
- Q4_K_M: ~16 GB
- Multimodal vision tower: +2-3 GB jeśli używasz image input

**Structured output:**
- ✅ Function calling support (prompt-based, no special tokens — wymaga careful instruction crafting)
- ✅ JSON output via prompt engineering
- ⚠ NO Outlines-dedicated documentation; działa przez vLLM guided_json
- **FunctionGemma** (dedicated fine-tune for function calling) released — może być lepszy choice jeśli function calling kluczowy

---

## 4. Inne polish-capable LLMs 2025-2026

### PLLuM (HIVE AI consortium, OPI, Cyfronet)

**Family (per arXiv:2511.03823 + HF CYFRAGOVPL):**
| Model | Base | License | Polish PLCC | Notes |
|---|---|---|---|---|
| **PLLuM-12B-nc-chat-250715** | Mistral-Nemo | **CC-BY-NC** | **79** (#1 polish-only) | NC = NO commercial use |
| **PLLuM-12B-chat** | Mistral-Nemo | Apache 2.0 | ~75 | Production OK |
| **Llama-PLLuM-8B-instruct** | Llama 3.1 8B | Llama 3.1 license | ~65 | Llama community license restrictions |
| **Llama-PLLuM-70B-instruct** | Llama 3.1 70B | Llama 3.1 license | **74** | **140GB VRAM bf16** |

**Training:**
- ~150B tokens polish (full team, 28B fully open commercial)
- 40k+ ręcznie utworzonych instructions
- Slavic/Baltic + English aux data
- RAG-optimized (dla public administration use case)

**Polish benchmarks:**
- Llama-PLLuM-70B-chat: **74 PLCC**, **8.05 MT-Bench**, **72.56 EQ-Bench**
- PLLuM-12B-nc-chat: **79 PLCC** (TOP polish-only model, ale NC license)

**Probe compatibility:**
- Llama-PLLuM-70B = Llama 3.1 70B arch → **excellent** (transformer-lens supports Llama 3.x)
- PLLuM-12B = Mistral-Nemo arch → standard HF support, hooks działają
- 80 layers × 8192 hidden (Llama 70B) = ogromna feature space, ale compute prohibitive

**OpenRouter:** ❌ **NIEDOSTĘPNY** (jak Bielik)
- Featherless.ai hostuje PLLuM-12B-chat (serverless inference, flat-rate)
- HuggingFace Inference Endpoints możliwe
- Self-host przez vLLM/SGLang

**Compute:**
- PLLuM-12B: ~24 GB bf16 (single A100 40GB tight)
- Llama-PLLuM-70B: **140 GB bf16** → 2× H100, lub Q4 ~35 GB (single H100)

**Weakness:** Llama 3.1 license restrictions (acceptable use policy, attribution, brak prawdziwego open source). NC variant najlepszy ale unusable production.

### Mistral Large 3 / Medium 3.5 (2026)

- **Mistral Medium 3.5:** dense 128B, 256K context, adjustable reasoning, multimodal
  - "Dozens of languages" (Polish unconfirmed w official docs Medium 3.5)
  - **Mistral-Large-Instruct (2411 i nowsze):** explicit polish support
  - **CodeSOTA:** Mistral-Large-Instruct-2411 = **69.84 Open PL LLM Leaderboard** (#3 globally)
- **License:** Mistral Research License (NC) lub commercial license (paid)
- **OpenRouter:** dostępny (mistral-large endpoints), pricing premium ($2-8/1M tokens typical)
- **Probe:** Mistral architecture → excellent
- **Issue:** 128B params → impractical for lab self-hosted

### Llama 4 (5 kwietnia 2025)

- **Scout** (~17B active, 109B total MoE) + **Maverick** (~17B active, 400B total MoE) + **Behemoth** (in dev)
- **Polish: NOT in officially supported 12 języków** (Arabic, EN, FR, DE, HI, ID, IT, PT, ES, TL, TH, VI)
- Pretrained on 200 languages (100+ z >1B tokens), 10× more multilingual data niż Llama 3
- Można fine-tunować na polish, ale out-of-the-box Polish coverage prawdopodobnie weaker niż Qwen 3.5
- License: Llama 4 Community License (restrictions)

### Phi-4 (Microsoft, 14B)

- **Base Phi-4 14B:** ~8% multilingual data, **NOT intended for multilingual use** → Polish weak
- **Phi-4-Multimodal:** explicitly supports Polish (text modality, alongside 21 inne)
- **Phi-4-Mini:** 200K word vocab dla improved multilingual
- License: MIT (excellent)
- **OpenRouter:** dostępne (Microsoft preview)
- **Polish benchmark scores:** brak dedicated PL scores w Microsoft docs
- **Probe compatibility:** standard HF support (`Phi4ForCausalLM`)
- **Verdict:** Skip dla polish-first; Phi-4-mini opcją jeśli edge deployment

### DeepSeek V3.1 / V3.2 / R1

- 671B MoE (37B active), context 128K
- "100+ languages" — Polish supported ale benchmark scores missing
- **OpenRouter pricing:** V3 = $0.32/$0.89, R1 = $0.70/$2.50 per 1M (R1 5× more dla reasoning chain)
- License: DeepSeek License (custom, generally permissive)
- **Issue:** 671B params → totally impractical self-hosted (~1.5 TB bf16). Only via API.
- **Probe:** możliwe via API hidden states extraction? **NIE** — DeepSeek API nie eksponuje hidden states
- **Verdict:** Skip dla probe target (API-only no hidden states); może rozważyć jako external generator dla baseline porównania

### Aya Expanse (Cohere, paźdz 2024)

- **Sizes:** 8B, 32B
- **23 supported languages including Polish** (Polish explicit w docs)
- Aya Expanse 32B outperforms Gemma 2 27B, Mistral 8x22B, Llama 3.1 70B na multilingual benchmarks (+25% low-resource avg)
- License: **CC-BY-NC 4.0** (Cohere Labs research release — **NO commercial use**)
- Apache 2.0 enterprise version available via Cohere API (paid)
- **Probe:** Command-family architecture (Cohere proprietary), standard HF support
- **OpenRouter:** Cohere Aya endpoints dostępne via OpenRouter (sprawdź najnowsze ceny)
- **Verdict:** Strong polish performer ale **NC license = unusable jeśli praca/artefakt commercial-leaning**

---

## 5. Comparison matrix

| Model | Params | Polish PLCC | License | VRAM bf16 | OR $/1M in | OR $/1M out | Probe arch | Struct out |
|---|---|---|---|---|---|---|---|---|
| **Bielik 11B v3** | 11B | **78** | Apache 2.0 | 22 GB | N/A | N/A | ✅ Mistral | ⚠ Prompt |
| Bielik 4.5B v3 | 4.5B | 45 (Open PL LLM) | Apache 2.0 | 9 GB | N/A | N/A | ✅ Mistral | ⚠ Prompt |
| **PLLuM-12B-chat** | 12B | ~75 | Apache 2.0 | 24 GB | N/A | N/A | ✅ Mistral-Nemo | ⚠ Prompt |
| PLLuM-12B-nc-chat | 12B | **79** | **CC-BY-NC** | 24 GB | N/A | N/A | ✅ Mistral-Nemo | ⚠ Prompt |
| **Llama-PLLuM-70B** | 71B | **74** | Llama 3.1 | **140 GB** | N/A | N/A | ✅ Llama 3.1 | ⚠ Prompt |
| **Qwen 3.5-27B** | 27B | (CPTU 4.34 #2) | Apache 2.0 | **55-65 GB** | $0.195 | $1.56 | ⚠ Hybrid att | ✅ Native |
| Qwen3-32B (legacy) | 32B | ~67 (est) | Apache 2.0 | ~65 GB | **$0.08** | **$0.28** | ✅ Standard | ✅ Native |
| Qwen3.6-27B | 27B | TBD | Apache 2.0 | 55 GB | $0.32 | $3.20 | ⚠ Hybrid att | ✅ Native |
| **Gemma 3 27B** | 27B | Not top 15 PL | Gemma Terms | 54 GB | **$0.08** | **$0.16** | ⚠ Local/global | ⚠ Prompt |
| Gemma 4 31B | 31B | TBD (unranked PL) | **Apache 2.0** | ~62 GB | TBD | TBD | ⚠ TBD | ⚠ Prompt |
| Mistral-Large-Instruct-2411 | ~123B | (Open PL 69.84) | Mistral Research | 246 GB | $2-3 | $6-9 | ✅ Mistral | ✅ Native |
| Mistral Medium 3.5 | 128B | Polish unconfirmed | Commercial | 256 GB | premium | premium | ✅ Mistral | ✅ Native |
| Llama 4 Scout | 109B MoE | NOT supported | Llama 4 | 17B active | varies | varies | ✅ Llama | ⚠ Limited |
| Phi-4 14B | 14B | Weak (8% multiling) | MIT | 28 GB | low | low | ✅ Standard | ⚠ Prompt |
| Phi-4-Multimodal | 5.6B | Explicit PL | MIT | 12 GB | low | low | ✅ Standard | ✅ Native |
| DeepSeek V3.2 | 671B MoE | Unconfirmed PL | DeepSeek License | API only | $0.32 | $0.89 | ❌ no HS via API | ✅ Native |
| DeepSeek R1 | 671B MoE | Unconfirmed PL | DeepSeek License | API only | $0.70 | $2.50 | ❌ no HS via API | ✅ Native |
| Aya Expanse 32B | 32B | Top multilingual | **CC-BY-NC** | 64 GB | varies | varies | ✅ Command | ✅ Native |

**Open PL LLM Leaderboard top (5-shot, na 2026-05-16):**
1. Mistral-Large-Instruct-2411: 69.84
2. Bielik-11B-v3.0-Instruct: 69.48
3. Meta-Llama-3.1-405B-Instruct: 69.44
4. Mistral-Large-Instruct-2407: 69.11
5. Qwen 2.5-72B-Instruct: 67.92

**CodeSOTA PLCC top (2026-03):**
1. Gemini-3.1-Pro-Preview: 97
2. Gemini-3.0-Pro-Preview: 95.83
3. GPT-5.4-2026: 92.17
4. Gemini-2.5-Pro: 92.17
5. PLLuM-12B-nc-chat-250715: **79** (top open-weight polish)
6. Bielik-11B v3.0-Instruct: **78**
7. Llama-PLLuM-70B-chat: **74**

---

## 6. Recommendations per use case

### Best polish coverage (raw quality)
**PLLuM-12B-nc-chat-250715** (79 PLCC) — ALE NC license. Dla commercial-safe: **Llama-PLLuM-70B-chat** (74 PLCC, 8.05 MT-Bench).
Runner-up: **Bielik 11B v3** (78 PLCC, 69.48 Open PL) — tylko 11B i Apache 2.0.

### Best probe extraction quality (architecture richness)
**Llama-PLLuM-70B** > **Qwen 3.5-27B** > **Bielik 11B v3** > **Gemma 3 27B**

Reasoning: Hidden state expressiveness skaluje z (layers × hidden_size). Llama 70B = 80 × 8192 = 655K features/token. Qwen 3.5-27B = 36 × 6144 = 221K. Bielik = 50 × 4096 = 205K. Gemma 3 27B = 46 × 4096 = 188K ALE alternating local/global komplikuje probe.

**Practical winner dla pracy:** **Bielik 11B v3 + secondary Qwen 3.5-27B w ablation.** PLLuM-70B nie mieści się w lab compute.

### Best cost-effectiveness (heavy OpenRouter inference)
**Gemma 3 27B IT:** $0.08 in / $0.16 out per 1M — najtańszy w klasie 27B, polish via 140+ langs (jakość untested PL).
Runner-up: **Qwen3-32B (legacy):** $0.08 in / $0.28 out — Apache 2.0, more polish data than Gemma.

### Best lab self-hosted (single A100 80GB / H100 80GB)
**Bielik 11B v3** (22 GB bf16, mieści się z workspace) — primary.
Co-candidates: **PLLuM-12B-chat** (24 GB Apache 2.0 — polish quality marginally lepszy niż Bielik na specific benchmarks).
**Qwen 3.5-27B** = boundary (55-65 GB z overhead → na H100 80GB OK, ale tight). Lepiej Q8.

### Best for halu probe target (signal density w hidden states)
**Bielik 11B v3** (current choice — defensible):
- 50 layers = bogata sekwencja transformacji (więcej probe positions niż 36-layer Qwen)
- Mistral arch = brak komplikacji alternating attention (vs Gemma)
- Polish-native training → hidden states "speak polish" semantycznie
- **Probe trenowany na Bielik hidden states → expected lepszy signal niż probe na Gemma którego polish hidden states mogą być mniej "denselnie" populated**

### Best for citation generation (structured output + polish)
**Qwen 3.5-27B:** native JSON mode + Polish via 201 languages + Outlines via vLLM. **ALE caveat:** bug w `enable_thinking=false`.
Runner-up: **Bielik 11B v3 + Outlines wrapper** — wymaga prompt engineering bo brak native structured output, ale polish quality wyższa.

---

## 7. Implications dla pracy

### Stay with Bielik 11B v3? **TAK — primary recommendation.**

**Pro za pozostaniem:**
1. **78 PLCC, 69.48 Open PL** — w czołówce polish-capable LLMs w klasie compute-realistic
2. **Probe-friendly Mistral arch** — najlepsza praktyka dla halu detection probe (50 layers daje rich position selection)
3. **Apache 2.0** — defendable w pracy ("używam free/open license, nie ma vendor lock-in")
4. **APT4 tokenizer** — measurable advantage dla polish (-15% input tokens vs Mistral default)
5. **Already in stack decision** — switching cost > marginal quality gain
6. **Single A100 fit** — iteration speed maintained dla 3 cykli retreningu

**Pro za upgrade do większego (np. PLLuM-70B / Qwen 3.5-27B):**
- Hidden state richness lepszy (>2× features/token w PLLuM-70B)
- Lepsze raw polish quality (+1-3pp na PLCC)

**Kontrargumenty:**
- PLLuM-70B = 140 GB → 2× H100 ($60-100k operational cost lab time)
- Qwen 3.5-27B na single H100 80GB = tight, FP8/Q8 wymagane → quality regression nieznana
- Switching mid-thesis = scope creep red flag (DEC-001 already locked Bielik via stack)

**Verdict:** **Bielik 11B v3 zostaje primary.** Zmiana wymaga osobnej DEC-003 z mocnym ablation evidence.

### Single-model vs multi-model split?

**Rekomendacja:** **Hybrid jeśli czas pozwala** — primary single-model (Bielik), ablation multi-model w RQ4 robustness section.

**Konfiguracja proponowana:**
- **Primary generator + halu probe target:** Bielik 11B v3 (self-hosted)
- **Judge model (separate decision, Iteracja 0):** `<judge_model>` z kandydatów {Bielik 11B v3, Gemma 3 27B via OpenRouter $0.08/$0.16, Qwen 3.5-27B via OpenRouter $0.195/$1.56, Claude Haiku 4.5}
- **Optional ablation w R7 results:** probe trenowany NA Bielik hidden states, evaluated tego samego probe na Qwen 3.5-27B hidden states (cross-model probe transferability — bonus contribution dla R8)

**NIE rekomenduję:** rotacja generator → Qwen/Gemma. Polish quality lepsza w Bielik dla 11B klasy.

### Specific actionable next steps (Iteracja 0 dla Magdy)

1. **Verify Bielik 11B v3 dostępność na FP8 (Hopper/Ada)** — wymaga GPU check w lab. Jeśli H100 dostępne → użyj FP8 → 11 GB VRAM, więcej miejsca na workspace.
2. **Test probe extraction na Bielik:** `model.model.layers[i].register_forward_hook(...)` na warstwach {12, 25, 38, 49} (early, mid, late, final). Confirm hidden states shape `(batch, seq, 4096)`.
3. **Cost estimate dla 3 cykli retreningu z OpenRouter judge:** assume 200 gold pairs × 3 cykli × Bielik generation (free, self-hosted) × judge eval na Gemma 3 27B OR ($0.08 in + $0.16 out) → szacunek $5-20 total. **Bardzo tanie**, nie ogranicza decyzji.
4. **NIE potwierdzaj PLLuM-12B-nc** mimo top PLCC — NC = unusable w pracy.
5. **Verify transformer-lens Bielik support** — sanity check `tl.HookedTransformer.from_pretrained("speakleash/Bielik-11B-v3.0-Instruct")` przed commitowaniem probe codebase.

---

## Sources

- [Qwen 3.5 release MarkTechPost 2026-03](https://www.marktechpost.com/2026/03/02/alibaba-just-released-qwen-3-5-small-models-a-family-of-0-8b-to-9b-parameters-built-for-on-device-applications/)
- [Qwen 3.5 Medium digitalapplied benchmarks pricing](https://www.digitalapplied.com/blog/qwen-3-5-medium-model-series-benchmarks-pricing-guide)
- [Qwen 3.5-27B OpenRouter pricing](https://openrouter.ai/qwen/qwen3.5-27b)
- [Qwen 3.5-27B HuggingFace](https://huggingface.co/Qwen/Qwen3.5-27B)
- [Qwen 3.5 license Apache 2.0](https://huggingface.co/Qwen/Qwen3.5-35B-A3B/blob/main/LICENSE)
- [Gemma 3 model card Google AI](https://ai.google.dev/gemma/docs/core/model_card_3)
- [Gemma 3 27B OpenRouter pricing](https://openrouter.ai/google/gemma-3-27b-it)
- [Gemma 4 Google blog 2026-04](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)
- [Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4)
- [Gemma 3 HF transformers docs](https://huggingface.co/docs/transformers/en/model_doc/gemma3)
- [Bielik 11B v3 Instruct HF](https://huggingface.co/speakleash/Bielik-11B-v3.0-Instruct)
- [Bielik 11B v3 arXiv 2601.11579](https://arxiv.org/abs/2601.11579)
- [Bielik v3 Small Tech Report](https://arxiv.org/html/2505.02550v1)
- [Bielik 11B v2 Tech Report arXiv 2505.02410](https://arxiv.org/pdf/2505.02410)
- [PLLuM 12B-nc-chat HF](https://huggingface.co/CYFRAGOVPL/pllum-12b-nc-chat-250715)
- [Llama-PLLuM-70B-instruct HF](https://huggingface.co/CYFRAGOVPL/Llama-PLLuM-70B-instruct)
- [PLLuM arXiv 2511.03823](https://arxiv.org/abs/2511.03823)
- [PLLuM 12B-chat Featherless serving](https://featherless.ai/models/CYFRAGOVPL/PLLuM-12B-chat)
- [CodeSOTA Polish LLM Leaderboard 2026](https://www.codesota.com/polish-llm)
- [Polish EQ-Bench HF Space](https://huggingface.co/spaces/speakleash/polish_eq-bench)
- [Open PL LLM Leaderboard HF Space](https://huggingface.co/spaces/speakleash/open_pl_llm_leaderboard)
- [Bielik vs PLLuM 2026 comparison](https://trend-rays.com/bielik-11b-v3-vs-pllum-the-definitive-2026-polish-ai-guide/)
- [Bielik AI 2026 prosteit](https://prosteit.pl/en/news/white-tailed-eagle-ai-in-2026-comparison/)
- [Mistral Medium 3.5 docs](https://docs.mistral.ai/models/overview)
- [Llama 4 official Meta](https://www.llama.com/models/llama-4/)
- [Aya Expanse 32B HF Cohere](https://huggingface.co/CohereLabs/aya-expanse-32b)
- [DeepSeek V3 OpenRouter](https://openrouter.ai/deepseek/deepseek-chat)
- [Phi-4 HF Microsoft](https://huggingface.co/microsoft/phi-4)
- [Phi-4 multimodal](https://huggingface.co/microsoft/Phi-4-multimodal-instruct)
- [vLLM SGLang Bielik FP8 compatibility](https://huggingface.co/speakleash/Bielik-11B-v2.0-Instruct-FP8)
- [Qwen3.5-27B architecture config](https://huggingface.co/Qwen/Qwen3.5-27B)
- [Qwen 3 structured output vLLM](https://github.com/vllm-project/vllm/issues/18819)
- [Gemma 3 Function Calling](https://blog.google/innovation-and-ai/technology/developers-tools/functiongemma/)
- [Qwen 3.5 27B VRAM apxml](https://apxml.com/posts/qwen-3-5-system-requirement-vram-guide)
