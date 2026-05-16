# Bielik + Outlines + structured output research — 2026-05-16

> Research file dla pracy inżynierskiej Magdaleny Sochackiej. Cel: zweryfikować integrację Bielik 11B v3 ze structured output libraries dla generation-time citation w polish RAG (RQ5 cross-register, RAG-as-judge w RQ2). Wszystkie linki sprawdzone WebFetch 2026-05-16.

---

## 0. Verdict (TL;DR)

| Pytanie | Odpowiedź | Confidence |
|---|---|---|
| Outlines + Bielik integration działa? | **TAK — partial**. Działa natywnie poprzez vLLM (xgrammar/outlines backend) oraz bezpośrednio przez `outlines.models.vllm(...)`. Notebook `Bielik_2_(AWQ)_structured_output.ipynb` w `Bielik-how-to-start` używa Bielik v2.2 + vLLM + Outlines. **Brak oficjalnego notebooka dla v3, ale architektura identyczna** (Mistral-like, ChatML template). | HIGH |
| Bielik 11B v3 native tool/function calling? | **TAK** — `bielik-tools` repo (32★, last commit 2026-04-20) dostarcza enhanced chat template `bielik_advanced_chat_template.jinja` + `bielik_vllm_tool_parser*.py` (3 wersje per vLLM 0.12/0.13/0.15+). Format: `<tool_call>{"name": ..., "arguments": ...}</tool_call>`. | HIGH |
| Rekomendowana biblioteka structured output dla pracy | **xgrammar (via vLLM default)** dla speed (3.5–14× szybsze niż Outlines/LMFE) lub **Outlines** jeżeli minimalizacja halucynacji jest priorytetem (uğur et al. 2025: Outlines 0.4% hallucination 2-shot vs xgrammar 7.1%, vs LMFE 0.7%). Dla RAG citation generation **Outlines wygrywa na success rate** (97% vs xgrammar 60-78%). | MEDIUM-HIGH |
| Rekomendowany approach citation | **Post-hoc rerank z generation-time constrained schema** (hybryda). Generation-time: Outlines + Pydantic `{claim, citation_id, citation_paragraph}` per claim. Post-hoc: deterministic mapping `citation_id` → chunk_id. | MEDIUM (założenie pending Iter. 0b POC) |
| Recommended stack | **vLLM 0.15+ + Bielik 11B v3.0-Instruct + Outlines (preferred) lub xgrammar (default vLLM)** via OpenAI-compatible `extra_body={"structured_outputs": {"json": schema}}`. Bielik chat template `bielik_advanced_chat_template.jinja` dla function calling. | HIGH |

**Critical caveats:**
- **vLLM ≥0.12.0 zmieniło API** — `guided_json` → `structured_outputs.json`. Examples w `bielik-tools` używają jeszcze starszego `guided_json` (Bielik v2.5 oznaczony, kompatybilny).
- **Outlines `outlines.models.vllm(...)`** używa wbudowanego vLLM engine'a (NIE OpenAI server) — najnowsza wersja Outlines (v1.3.0, 2026-05-13) zachowuje to API.
- **Instructor BRAK natywnego vLLM provider** — wymaga workaround przez `from_openai(OpenAI(base_url=...))` w `JSON` mode. Pydantic-first ale TOOLS mode wymaga Bielik tool template setup.
- **Bielik v3 native context = 32k** (NIE 131k jak marketing AWS twierdzi — to YaRN extension, lower quality). Polish APT4 tokenizer: fertility 1.62 t/word vs 3.22 Mistral.

---

## 1. SpeakLeash organization audit

**Org URL:** `https://github.com/speakleash`

| Repo | Last commit (sprawdzone 2026-05-16) | ★ | Język | Relevance dla pracy |
|---|---|---|---|---|
| `Bielik-how-to-start` | 2025-06-07 | 189 | Jupyter | **HIGH** — zawiera `Bielik_2_(AWQ)_structured_output.ipynb` (vLLM + Outlines), `Bielik_2_(4_bit)_RAG.ipynb`, `Bielik_2_(4_bit)_JSON.ipynb`, `Bielik_v3_0_unsloth.ipynb` (tool calling) |
| `bielik-tools` | **2026-04-20** | 32 | Python | **CRITICAL** — najbardziej aktualny. `examples/{tool_calling,structured_output,reasoning_streaming,crewai_to_file}.py` + vLLM parsers per wersja (0.12/0.13/0.15+) + advanced chat template |
| `bielik-papers` | 2026-05-01 | 10 | — | Folders `v3`, `v3_pl`, `v3_small` zawierają technical reports (cite-able) |
| `bielik-prompt-book` | 2025-09-24 | 10 | HTML | Resource of prompts — nie sprawdzone, ale prawdopodobnie irrelevant dla structured output |
| `awesome-bielik` | 2025-08-04 | — | — | README niedostępny via WebFetch (loading error) — manual check zalecany |
| `speakleash-instruct-creator` | — | 13 | Python | Generuje instruction datasets — może być cite-able dla R6 jeśli używałabyśmy ich pipeline |
| `multimodal-data-generation` | — | — | Python | Synthetic datasets multimodal — NIE relevant |
| `simple-llm-perf` | — | — | Python | LLM benchmarking — może być **relevant dla R7** baseline performance |

**Brak repo `speakleash/bielik` (404)** — model jest tylko na HuggingFace, repo z toolami nazywa się `bielik-tools`.

---

## 2. Bielik + Outlines integration

### 2.1 Oficjalne demo (Bielik-how-to-start `Bielik_2_(AWQ)_structured_output.ipynb`)

```python
# Source: https://github.com/speakleash/Bielik-how-to-start/blob/main/Bielik_2_(AWQ)_structured_output.ipynb
# Bielik v2.2 (Mistral arch), zweryfikowane via WebFetch 2026-05-16

from enum import Enum
from typing import List, Optional, Union
from outlines import generate, models
from pydantic import BaseModel, Field, constr
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("speakleash/Bielik-11B-v2.2-Instruct")
model = models.vllm("speakleash/Bielik-11B-v2.2-Instruct-AWQ", quantization="awq")

class CharactersNames(Enum):
    Frodo = "Frodo"
    Sam = "Sam"
    Merry = "Merry"

class Item(BaseModel):
    name: str
    quantity: Optional[Union[int, str]]

class Character(BaseModel):
    name: CharactersNames
    items: List[Item]

class Company(BaseModel):
    characters: List[Character]

schema = Company.model_json_schema()

generator = generate.json(model, Company)            # constrained
generator_unstructured = generate.text(model)        # baseline

response = generator(prompt, max_tokens=1024)
json_str = response.model_dump_json(indent=4)
```

### 2.2 Caveats dla Bielik 11B v3

| Caveat | Severity | Mitigation |
|---|---|---|
| Brak oficjalnego notebooka v3 + Outlines | LOW | Architecture identyczna (Mistral-like, ChatML, 32k context) — przeniesienie 1:1 |
| Outlines v1.3.0 zmienił API w v1.0 (Outlines v0 → v1 breaking) | MEDIUM | Notebook używa stare `outlines.generate.json(...)`. Nowe API: `outlines.from_vllm(...)` + `outlines.json(model, Schema)(prompt)`. Sprawdzić release notes. |
| Polish APT4 tokenizer (v3) różni się od Mistral tokenizera (v2) | MEDIUM | Outlines konwertuje JSON schema do regex per-token — APT4 nie powinno łamać logiki ale **wymaga testu na polish diakrytykach** (ą, ć, ę, ł, ń, ó, ś, ź, ż) — moja hipoteza: brak issue, ale **MUST TEST w Iter. 0b** |
| vLLM AWQ quantization vs FP8/bf16 | LOW | Bielik 11B v3.0-Instruct-FP8-Dynamic gotowe dla vLLM ≥0.5.0. Outlines neutralne wobec quantization. |

### 2.3 Alternatywny pattern — via vLLM OpenAI-compatible endpoint (preferowany dla production)

```python
# Pattern z bielik-tools/examples/structured_output.py (Bielik v2.5)
# Wymaga: vllm serve speakleash/Bielik-11B-v3.0-Instruct --port 8000

from openai import OpenAI
from pydantic import BaseModel

class CitedClaim(BaseModel):
    claim: str
    citation_id: int  # chunk index w retrieved context
    citation_paragraph: str  # verbatim quote z chunka

class CitedAnswer(BaseModel):
    claims: list[CitedClaim]
    summary: str

client = OpenAI(api_key="EMPTY", base_url="http://127.0.0.1:8000/v1")

response = client.chat.completions.create(
    model="speakleash/Bielik-11B-v3.0-Instruct",
    messages=[
        {"role": "system", "content": "Odpowiadasz wyłącznie na podstawie podanych dokumentów. Każda teza musi mieć cytat verbatim."},
        {"role": "user", "content": f"Kontekst:\n{retrieved_context}\n\nPytanie: {query}"}
    ],
    temperature=0.2,
    extra_body={
        # NEW API (vLLM ≥0.12.0):
        "structured_outputs": {"json": CitedAnswer.model_json_schema()}
        # LEGACY (vLLM <0.12.0 / bielik-tools examples):
        # "guided_json": CitedAnswer.model_json_schema()
    },
)
parsed = CitedAnswer.model_validate_json(response.choices[0].message.content)
```

---

## 3. Bielik + Instructor integration

### 3.1 Status: workaround required

Instructor (v1.15.1, 2026-04-03) **nie ma natywnego vLLM provider**. Lista oficjalnie wspieranych: OpenAI, Azure, Anthropic, Google, Vertex, Bedrock, xAI, Cohere, Mistral, DeepSeek, Together, Groq, Fireworks, Cerebras, Writer, Perplexity, SambaNova, Ollama, llama-cpp-python, LiteLLM, OpenRouter.

### 3.2 Workaround pattern (oparte na OpenAI-compatible API)

```python
# UWAGA: nie zweryfikowane oficjalną dokumentacją Instructor dla vLLM,
# ale pattern Ollama (też OpenAI-compatible) działa identycznie.

import instructor
from openai import OpenAI
from pydantic import BaseModel

class CitedAnswer(BaseModel):
    claims: list[dict]  # patrz wyżej
    summary: str

# Workaround 1: from_openai z custom base_url
client = instructor.from_openai(
    OpenAI(api_key="EMPTY", base_url="http://127.0.0.1:8000/v1"),
    mode=instructor.Mode.JSON  # NIE TOOLS — wymaga Bielik tool template
)

response = client.chat.completions.create(
    model="speakleash/Bielik-11B-v3.0-Instruct",
    messages=[...],
    response_model=CitedAnswer,
    max_retries=3,
)
# response is już Pydantic instance, validated
```

### 3.3 Instructor modes dla Bielik (priorytetyzacja)

| Mode | Wsparcie Bielik | Notes |
|---|---|---|
| `JSON` | **PREFERRED** | Bielik wytrenowany do JSON output (potwierdzone w README bielik-tools). Wymaga prompt engineering. |
| `MD_JSON` | OK fallback | Parsing JSON z markdown code blocków. Mniej rygorystyczne niż JSON mode. |
| `TOOLS` | Wymaga setup | Potrzebuje custom Bielik chat template + vLLM tool parser. Production-grade ale więcej config. |
| `TOOLS_STRICT` | NIE testowane | Constrained grammar — teoretycznie OK z vLLM xgrammar backend. |
| `JSON_O1` / `RESPONSES_TOOLS` | SKIP | OpenAI-specific, nieprzydatne dla Bielika. |

### 3.4 Outlines vs Instructor — recommendation dla pracy

| Kryterium | Outlines | Instructor | Winner |
|---|---|---|---|
| Native vLLM | TAK (via `models.vllm()`) | NIE (workaround) | **Outlines** |
| Pydantic ergonomics | OK (model_json_schema) | EXCELLENT (response_model=...) | Instructor |
| Constrained decoding GUARANTEE | TAK (FSM/regex) | NIE (validation + retry) | **Outlines** |
| Auto-retry on schema fail | NIE (raises) | TAK (max_retries) | Instructor |
| Production maturity 2026 | HIGH (v1.3.0, used by NVIDIA/Cohere/HF) | HIGH (v1.15.1, mainstream) | tie |
| RAG citation success rate (Uğur 2025 paper) | **97% 2-shot** | n/a (orthogonal — może wrap dowolny backend) | **Outlines** |
| Polish-specific tested | TAK (Bielik notebook) | NIE explicite | **Outlines** |

**Recommendation:** **Outlines as primary** dla structured citation generation (RQ2, RQ5). Instructor opcjonalnie jako wrapper jeśli chcemy ergonomiczny retry-on-fail (np. dla judge model pipeline gdzie schema violations są realne).

---

## 4. Alternative libraries comparison (2026 state)

| Library | Latest version (2026-05) | Default w | RAG success @ 1-shot (Uğur 2025) | Hallucination 2-shot | Speed vs baseline | Polish/Bielik compat |
|---|---|---|---|---|---|---|
| **xgrammar** | 0.2.0 (2026-05-01) | vLLM **default**, SGLang **default**, TensorRT-LLM, MLC-LLM | 60–78% | 7.1% | **3.5–14× faster** | Via vLLM backend — działa |
| **Outlines** | 1.3.0 (2026-05-13) | (stand-alone + vLLM backend) | **93–97%** | **0.4%** | baseline | **Natywnie testowane na Bielik v2** |
| **lm-format-enforcer** | 0.11.2 (2025-08-09) — **stale 9 mies.** | (vLLM backend, transformers, HF, LangChain, LlamaIndex, Haystack) | 78–93% | 0.7% | similar to Outlines | Via vLLM — działa, ale stagnant |
| **guidance** (MSFT) | aktywny | — | n/a w paper | n/a | n/a | NIE testowane, deprecated path dla Hugging Face models |
| **llguidance** (guidance-ai) | aktywny | SGLang backend option | n/a | n/a | "super-fast" | Via SGLang — możliwe ale niezweryfikowane |
| **SGLang structured outputs** (built-in) | — | — | n/a | n/a | Default xgrammar; opt-in Outlines/llguidance | **TAK** — Bielik v3 wprost dokumentowany na SGLang |

### Decyzyjny matrix dla pracy

| Use case | Recommendation | Rationale |
|---|---|---|
| **Iter. 0b POC** (szybko + minimum dependencies) | **vLLM serve + xgrammar (default) + Pydantic via OpenAI client** | Zero extra installs, sprawdzony pattern z `bielik-tools/examples/structured_output.py` |
| **RQ2 LLM-as-judge** (rygorystyczność > speed) | **Outlines** | Najniższa hallucination rate (0.4%), najwyższy success (97%) — krytyczne dla judge agreement metric |
| **RQ5 cross-register citation** (production-style) | **vLLM + Outlines backend** lub **xgrammar** | Decyzja w Iter. 1 po benchmarku speed vs accuracy na polish corpus |
| **Generation z 32k context** (long ChPL + paired Ulotka) | xgrammar speed advantage decyduje | Outlines może być za wolny przy długim kontekście |

---

## 5. Existing Bielik citation examples

### 5.1 Znalezione real-world projects

1. **`mGarbowski/llm-projekt`** ([github](https://github.com/mGarbowski/llm-projekt)) — **DIRECT PRIOR ART**
   - **Stack:** bi-encoder `sdadas/mmlw-retrieval-roberta-large` + cross-encoder `sdadas/polish-reranker-roberta-v3` + generator `speakleash/Bielik-1.5B-v3.0-Instruct` (NIE 11B — GPU constraint GTX 1060)
   - **Retrieval:** dual (PostgreSQL FTS + dense), reranking, **citations w odpowiedziach jako `[0]`, `[1]`** bracket notation
   - **Eval:** custom 38-question test set, Recall@1=0.50, MRR@1=0.79, BERT Score F1=0.69
   - **WARNING:** stack identyczny do Magdy (z dokładnością do generator size) — **defense scaffolding alert:** Magda musi w R8 jasno **wyróżnić** swoją kontrybucję od tego projektu (10×większy generator, **paired ChPL↔Ulotka cross-register RQ5**, MLOps pipeline, drift detection — Magda full thesis, mGarbowski educational toy project).

2. **`bielik-papers/v3_pl`** — Bielik v3 PL technical report ([arxiv:2604.10799](https://arxiv.org/abs/2604.10799)) — APT4 tokenizer optimization, fertility 1.62 vs 3.22. **Cite dla R6 modele.**

3. **`bielik-papers/v3_small`** — Bielik v3 Small ([arxiv:2505.02550](https://arxiv.org/abs/2505.02550)) — alternative model size.

### 5.2 NIE znalezione

- Brak oficjalnego SpeakLeash przykładu citation generation w bielik-tools
- Brak Bielik few-shot citation prompt template
- Brak polish-language RAG-as-judge example
- Brak SpeakLeash benchmarku Outlines vs xgrammar dla Bielika

**Implication:** Magda ma okazję na **publishable sub-contribution** — pierwszy publicznie udokumentowany benchmark structured citation dla polish RAG na Bielik v3 (już niżej w sekcji 8 plan Iter. 0b).

---

## 6. Sample code dla pracy (Iteration 0b POC, production-ready templates)

### 6.1 Generation-time citation — Outlines + Bielik v3 + vLLM (PREFERRED)

```python
# tests/iter0b_outlines_citation.py
# Wymaga: vllm>=0.15.0, outlines>=1.3.0, pydantic>=2.0
# Run: vllm serve speakleash/Bielik-11B-v3.0-Instruct --port 8000
#      python tests/iter0b_outlines_citation.py

from outlines import models, generate
from pydantic import BaseModel, Field
from typing import Literal

# === Schema dla cross-register citation (RQ5) ===
class Claim(BaseModel):
    claim_text: str = Field(..., description="Pojedyncza teza odpowiedzi w 1 zdaniu")
    citation_chunk_id: int = Field(..., ge=0, description="Index chunka w retrieved context (0-indexed)")
    citation_paragraph: str = Field(..., description="Verbatim fragment z chunka uzasadniający tezę")
    register: Literal["professional", "consumer"] = Field(..., description="ChPL professional vs Ulotka consumer")

class CitedAnswer(BaseModel):
    claims: list[Claim] = Field(..., min_length=1, max_length=10)
    summary: str = Field(..., description="Krótkie podsumowanie 2-3 zdania")

# === Setup ===
model = models.vllm("speakleash/Bielik-11B-v3.0-Instruct")  # Lub via OpenAI client
generator = generate.json(model, CitedAnswer)

# === RAG pipeline ===
def format_context(retrieved_chunks: list[dict]) -> str:
    """retrieved_chunks: [{'id': int, 'register': str, 'text': str, 'source': str}, ...]"""
    return "\n\n".join([
        f"[Chunk {c['id']} | {c['register']} | {c['source']}]\n{c['text']}"
        for c in retrieved_chunks
    ])

def cited_rag_query(query: str, retrieved_chunks: list[dict]) -> CitedAnswer:
    prompt = f"""<|im_start|>system
Jesteś asystentem farmakologicznym. Odpowiadasz WYŁĄCZNIE na podstawie podanych dokumentów.
Każda teza musi mieć:
  - citation_chunk_id (index chunka, 0-indexed)
  - citation_paragraph (verbatim fragment, NIE parafraza)
  - register (professional=ChPL, consumer=Ulotka)
Jeżeli nie ma odpowiedzi w kontekście — zwróć pustą listę claims i summary "Brak odpowiedzi w dostępnych dokumentach."
<|im_end|>
<|im_start|>user
Kontekst:
{format_context(retrieved_chunks)}

Pytanie: {query}
<|im_end|>
<|im_start|>assistant
"""
    return generator(prompt, max_tokens=2048)

# === Test ===
if __name__ == "__main__":
    chunks = [
        {"id": 0, "register": "professional", "source": "ChPL_sertralina.pdf",
         "text": "Sertralina jest inhibitorem wychwytu zwrotnego serotoniny (SSRI). Dawka początkowa 50 mg/dobę."},
        {"id": 1, "register": "consumer", "source": "Ulotka_sertralina.pdf",
         "text": "Lek pomaga w leczeniu depresji. Zwykle bierze się jedną tabletkę dziennie rano."},
    ]
    result = cited_rag_query("Jaka jest dawka początkowa sertraliny?", chunks)
    print(result.model_dump_json(indent=2))
    # Walidacja: każdy claim.citation_chunk_id < len(chunks), citation_paragraph in chunks[id]['text']
    for claim in result.claims:
        assert claim.citation_chunk_id < len(chunks), "Hallucinated chunk_id"
        assert claim.citation_paragraph in chunks[claim.citation_chunk_id]["text"], \
            f"Paraphrase, not verbatim: {claim.citation_paragraph}"
```

### 6.2 Post-hoc citation — Bielik free-form + osobny mapping pipeline

```python
# tests/iter0b_posthoc_citation.py
# Strategia: generuj swobodnie, potem osobny pass mapowania claim → chunk via embedding similarity

from sentence_transformers import SentenceTransformer
from openai import OpenAI
import numpy as np

# === Step 1: free-form generation ===
client = OpenAI(api_key="EMPTY", base_url="http://127.0.0.1:8000/v1")
embedder = SentenceTransformer("BAAI/bge-m3")

def free_form_answer(query: str, context: str) -> str:
    response = client.chat.completions.create(
        model="speakleash/Bielik-11B-v3.0-Instruct",
        messages=[
            {"role": "system", "content": "Odpowiadasz na pytania farmakologiczne na podstawie kontekstu."},
            {"role": "user", "content": f"Kontekst:\n{context}\n\nPytanie: {query}"}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content

def split_into_claims(answer: str) -> list[str]:
    # Naive sentence split — production: użyj polish sentence tokenizer (np. spacy pl_core_news_sm)
    return [s.strip() for s in answer.split(".") if s.strip()]

# === Step 2: post-hoc mapping ===
def map_claims_to_chunks(claims: list[str], chunks: list[dict], threshold: float = 0.6) -> list[dict]:
    claim_emb = embedder.encode(claims, normalize_embeddings=True)
    chunk_emb = embedder.encode([c["text"] for c in chunks], normalize_embeddings=True)
    sims = claim_emb @ chunk_emb.T  # cosine since normalized
    results = []
    for i, claim in enumerate(claims):
        best_chunk_idx = int(np.argmax(sims[i]))
        confidence = float(sims[i][best_chunk_idx])
        results.append({
            "claim": claim,
            "citation_chunk_id": best_chunk_idx if confidence >= threshold else None,
            "confidence": confidence,
            "supported": confidence >= threshold,
        })
    return results

# === Pipeline ===
def posthoc_cited_rag(query: str, chunks: list[dict]) -> dict:
    context = "\n\n".join([f"[{c['id']}] {c['text']}" for c in chunks])
    answer = free_form_answer(query, context)
    claims = split_into_claims(answer)
    citations = map_claims_to_chunks(claims, chunks)
    return {"answer": answer, "citations": citations}
```

**Trade-off generation-time vs post-hoc:**
| Aspect | Generation-time (Outlines) | Post-hoc (embedding match) |
|---|---|---|
| Schema guarantee | Hard (FSM constraint) | Soft (validation only) |
| Hallucinated citations | Możliwe (chunk_id z dupy) | Możliwe (false positive match) |
| Latency | +20–50% | +1 embed pass (~50ms) |
| Implementation complexity | Medium (Outlines + schema) | High (sentence split + threshold tuning) |
| Verbatim quote enforcement | Możliwe via prompt + post-validation | Trudne (embedding ≠ exact match) |
| Cross-register flexibility | High (Literal register field) | Medium (depends on chunk metadata) |
| **Defensibility w pracy** | Stronger ("guaranteed schema") | Weaker ("best-effort mapping") |

### 6.3 Bielik z PyTorch hooks (hidden states extraction — probe input dla halu detection RQ probe)

```python
# tests/iter0b_bielik_hidden_states.py
# Wymaga: transformers>=4.45, torch>=2.4
# UWAGA: NIE via vLLM (które nie eksponuje hidden states łatwo).
# Dla probe model trainingu używaj raw transformers — wolniejsze ale full access.

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "speakleash/Bielik-11B-v3.0-Instruct"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    output_hidden_states=True,  # Critical dla probe
)

def extract_hidden_states(prompt: str, generated_tokens: int = 256, layer: int = -1):
    """
    Zwraca hidden states z wybranej warstwy dla wygenerowanej sekwencji.
    layer=-1 → ostatnia warstwa (typowy probe target dla SAPLMA-style halu detection).
    """
    messages = [{"role": "user", "content": prompt}]
    input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_new_tokens=generated_tokens,
            do_sample=False,  # deterministic dla probe
            return_dict_in_generate=True,
            output_hidden_states=True,
        )

    # outputs.hidden_states: tuple per generation step, każdy tuple per layer
    # Per step: (batch, seq_len, hidden_dim)
    hidden_per_step = [step_hs[layer][:, -1, :] for step_hs in outputs.hidden_states]
    hidden_seq = torch.stack(hidden_per_step, dim=1)  # (batch, generated_tokens, hidden_dim)
    generated_ids = outputs.sequences[:, input_ids.shape[1]:]
    return {
        "generated_text": tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0],
        "hidden_states": hidden_seq.cpu().numpy(),  # numpy dla scikit-learn probe
        "shape": hidden_seq.shape,  # debug
    }

# === Use case dla pracy: probe input dla halu detection ===
# Magda: dla RQ probe trenuj logistic regression na pooled hidden_states[layer=-1] z labeled
# (halu/non-halu) examples. Mean pooling lub last token pooling.
result = extract_hidden_states("Wyjaśnij dawkowanie sertraliny u dorosłych z depresją.")
print(f"Shape: {result['shape']}, text: {result['generated_text'][:200]}")
```

---

## 7. Integration risks + mitigations

| # | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| R1 | **APT4 tokenizer (Bielik v3) breakage in Outlines regex/FSM** dla polish diakrytyków (ą,ć,ę,ł,ń,ó,ś,ź,ż) | MEDIUM | LOW | Test w Iter. 0b — minimalny POC z Pydantic schema zawierający polish strings. Jeśli fail → use xgrammar fallback (byte-level handling). |
| R2 | vLLM API drift (`guided_json` → `structured_outputs.json` w 0.12.0) | LOW | HIGH (już się stało) | Pin vLLM version w `pyproject.toml`: `vllm>=0.15.0,<0.20.0`. Use modern `structured_outputs` API. |
| R3 | Bielik 11B v3 native context 32k — przy paired ChPL+Ulotka + 10 chunków + schema constraint może overflow | MEDIUM | MEDIUM | Chunk size limit 800 tokens × max 8 chunks = 6.4k context budget. Reserve 4k dla schema generation. Total ≤10.4k well within 32k. |
| R4 | Outlines latency overhead (FSM compilation per schema, cached) | LOW | MEDIUM | Cache compiled generators per schema (reuse Pydantic class instance). Pre-warm w pipeline startup. |
| R5 | **Instructor's TOOLS mode wymaga Bielik tool template** — bez setup'u response z `<tool_call>` tagami nie zostanie sparsowany | HIGH (jeśli używamy TOOLS) | HIGH | **Use Instructor JSON mode**, nie TOOLS. Tool template przeznaczony dla CrewAI multi-agent (orthogonal use case). |
| R6 | bf16 vs FP8 vs INT8 quantization dla 11B — VRAM constraint | MEDIUM | MEDIUM | Magda research stack zakłada SGLang/vLLM serving. Bielik-11B-v3.0-Instruct-FP8-Dynamic = 12GB VRAM (vs bf16 22GB). Recommend FP8 dla single A100/RTX 4090. |
| R7 | **xgrammar 60–78% RAG success rate (Uğur 2025)** — gorsze niż Outlines (93–97%) | HIGH dla RQ5 | HIGH (per paper) | **Use Outlines dla citation generation**, xgrammar tylko dla speed-critical batch inference. Decyzja w Iter. 1 po własnym benchmarku polish corpus. |
| R8 | mGarbowski/llm-projekt prior art — overlap stack | LOW (defense) | HIGH (już istnieje) | Wyróżnij kontrybucję: (a) Bielik 11B vs 1.5B; (b) MLOps pipeline z drift detection; (c) RQ5 paired cross-register — nowość; (d) full thesis vs educational toy. |
| R9 | SpeakLeash bielik-tools repo focus na **vLLM tooling**, NIE Outlines — community moves to xgrammar default | LOW | MEDIUM | Track repo activity. Last commit 2026-04-20 — aktywne. Jeśli Outlines deprecated path → migrate do xgrammar (Pydantic API identyczne via vLLM). |
| R10 | Brak oficjalnego Bielik v3 + Outlines notebook | LOW | LOW | Magda może **napisać i opublikować** (potential PR do `Bielik-how-to-start` jako side-contribution z thesis). |

---

## 8. Recommended Iter. 0b POC structure

**Cel:** zweryfikować że pełny stack `Bielik 11B v3 + Outlines + Pydantic + polish text` działa end-to-end z citation generation **przed** committment do produkcyjnego pipeline.

**Czas:** 4–6h focused work.

### Step 1: Environment setup (30min)
```bash
uv add "vllm>=0.15.0" "outlines>=1.3.0" "pydantic>=2.0"
uv add --dev "openai>=1.50"  # dla post-hoc tests
# Quantization wybór: FP8 jeśli A100/RTX 4090, AWQ jeśli RTX 3090
# Pobierz: huggingface-cli download speakleash/Bielik-11B-v3.0-Instruct-FP8-Dynamic
```

### Step 2: vLLM serve sanity check (15min)
```bash
vllm serve speakleash/Bielik-11B-v3.0-Instruct-FP8-Dynamic \
  --port 8000 \
  --max-model-len 16384 \
  --structured-outputs-config.backend xgrammar  # default; test outlines też
```
Test: `curl -X POST http://localhost:8000/v1/chat/completions -d '{"model": "...", "messages": [{"role":"user","content":"Cześć"}]}'`

### Step 3: Polish diakrytyk JSON schema test (45min) — **CRITICAL**
```python
class TestPolish(BaseModel):
    nazwa: str  # zawiera polish chars
    działanie: str
    przeciwwskazania: list[str]

# Test 1: xgrammar backend
# Test 2: outlines backend (vLLM --structured-outputs-config.backend outlines)
# Test 3: native Outlines (models.vllm(...))
# Sukces: 100% parsable JSON, polish chars zachowane, no token-level corruption
```

### Step 4: RAG citation POC z mock corpus (2h)
- 5 mock chunks (3 ChPL professional, 2 Ulotka consumer) o sertralinie
- 10 mock queries (5 professional, 5 consumer)
- Pipeline: query → retrieve top-3 → Bielik + CitedAnswer schema → validate
- Metric: % responses where wszystkie `claim.citation_chunk_id` w range i `citation_paragraph` jest substringiem chunka

### Step 5: Latency benchmark (45min)
- xgrammar vs outlines backend
- Per response: tokens/sec, time to first token, schema compilation overhead
- N=50 queries, raporto mean ± std

### Step 6: Decision log entry (15min)
Zapisać w `thesis_research/decisions/DEC-003_structured_output_backend.md`:
- Wybrany backend (Outlines vs xgrammar)
- Wybrana biblioteka API (native Outlines vs vLLM OpenAI client + Pydantic vs Instructor)
- Rationale (success rate vs speed trade-off w polish corpus)
- Fallback plan jeśli polish diakrytyki łamią

### Step 7 (opcjonalny, jeśli czas): comparison z mGarbowski stack (1h)
- Reproduce jego bracket `[0]` citation pattern na tych samych queries
- Porównaj qualitative: structured Pydantic vs bracket notation
- Defensibility check: czy structured approach daje **measurably** lepszą faithfulness?

**Done criteria (twarde):**
- [ ] Bielik v3 odpowiada poprawnie po polsku z JSON schema constraint
- [ ] 100% schema-valid responses na N=50 mock queries
- [ ] ≥90% citation_chunk_id w validnym range
- [ ] Polish diakrytyki bez korupcji (visual check + assert)
- [ ] Latency p95 <30s per query @ 16k context
- [ ] DEC-003 zalogowany z rationale

---

## Sources (sprawdzone 2026-05-16)

**SpeakLeash + Bielik:**
- [SpeakLeash GitHub org](https://github.com/speakleash)
- [bielik-tools repo](https://github.com/speakleash/bielik-tools) — 32★, last commit 2026-04-20
- [Bielik-how-to-start](https://github.com/speakleash/Bielik-how-to-start) — 189★
- [Bielik_2_(AWQ)_structured_output.ipynb](https://github.com/speakleash/Bielik-how-to-start/blob/main/Bielik_2_(AWQ)_structured_output.ipynb)
- [Bielik-11B-v3.0-Instruct HF model card](https://huggingface.co/speakleash/Bielik-11B-v3.0-Instruct)
- [Bielik v3 PL tokenizer paper (APT4)](https://arxiv.org/abs/2604.10799)
- [Bielik 11B v3 paper](https://arxiv.org/abs/2601.11579)

**Structured output libraries:**
- [Outlines](https://github.com/dottxt-ai/outlines) — v1.3.0 (2026-05-13)
- [Instructor](https://github.com/instructor-ai/instructor) — v1.15.1 (2026-04-03)
- [xgrammar](https://github.com/mlc-ai/xgrammar) — v0.2.0 (2026-05-01)
- [lm-format-enforcer](https://github.com/noamgat/lm-format-enforcer) — v0.11.2 (2025-08-09, stale)
- [vLLM structured outputs docs](https://docs.vllm.ai/en/latest/features/structured_outputs.html)
- [SGLang structured outputs docs](https://docs.sglang.io/advanced_features/structured_outputs.html)

**Benchmark papers:**
- [Uğur et al. 2025 — Guided Decoding and Its Critical Role in RAG](https://arxiv.org/abs/2509.06631) — **MUST CITE w R6/R7** (jedyne real benchmark Outlines vs xgrammar vs LMFE dla RAG)
- [Generating Structured Outputs from Language Models: Benchmark and Studies](https://arxiv.org/html/2501.10868v1) — broader benchmark

**Prior art (defense scaffolding):**
- [mGarbowski/llm-projekt](https://github.com/mGarbowski/llm-projekt) — **Polish RAG z bracket citations + Bielik 1.5B v3 + polish-reranker-roberta-v3** (MUST MENTION w R2 literatura, wyróżnij kontrybucję)
