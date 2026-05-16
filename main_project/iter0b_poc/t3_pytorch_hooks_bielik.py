"""T3 POC: PyTorch hooks ekstrakcja hidden states z Bielik 11B v3 layer 47.

Cel: zweryfikować że można:
1. Załadować Bielik 11B v3 z `output_hidden_states=True` (HF native)
2. Ekstraktować aktywacje z layer 47 (⌊0.95 × 50⌋, optimal probe layer per Farquhar 2024)
3. Verify shape (batch, seq_len, 4096) — Bielik 11B = Mistral arch z hidden_size=4096
4. NIE crashować (OOM, shape mismatch, hooks errors)

Methodology:
1. Load Bielik 11B v3 z bf16 (lub FP8 dynamic jeśli H100)
2. Forward pass na 5 polish prompts
3. Per prompt: extract layer 47 hidden state via PyTorch hook lub model output
4. Validate shape + sanity check (no NaN, no inf, reasonable magnitude)
5. Mean pool last token → per-prompt vector (4096-dim)
6. Verify vectors są different per prompt (cosine similarity < 0.95 między różnymi)

Kill criterion: OOM lub shape mismatch lub hook exception → fallback Bielik 1.5B/3B (per CLAUDE.md spec dla local dev).

Reference impl: https://github.com/obalcells/hallucination_probes (przeczytaj `probes_polish_llm_research.md`).

Wymagania: lab GPU (H200 80GB) lub Bielik FP8 (50% VRAM).

CLI:
    uv run python -m iter0b_poc.t3_pytorch_hooks_bielik \\
        --model speakleash/Bielik-11B-v3.0-Instruct \\
        --layer 47
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Bielik 11B v3 = Mistral architecture: 50 layers × 4096 hidden_size
EXPECTED_NUM_LAYERS = 50
EXPECTED_HIDDEN_SIZE = 4096
DEFAULT_PROBE_LAYER = 47  # ⌊0.95 × 50⌋

TEST_PROMPTS = [
    "Konsument może odstąpić od umowy zawartej na odległość w terminie 14 dni bez podawania przyczyny.",
    "Sprzedawca odpowiada wobec konsumenta z tytułu rękojmi za wady fizyczne towaru.",
    "Klauzule abuzywne w umowach konsumenckich są nieważne z mocy prawa.",
    "Ten chleb jest świeży i pyszny.",  # off-topic dla różnicowania
    "Wczoraj padał deszcz przez cały dzień.",  # off-topic
]


def load_bielik(model_name: str, device: str = "auto"):
    """Load Bielik 11B z output_hidden_states=True."""
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        logger.error("Missing deps: pip install transformers torch — %s", exc)
        sys.exit(1)

    logger.info("Loading %s ...", model_name)
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        device_map=device,
        output_hidden_states=True,
    )
    model.eval()
    logger.info("Model loaded on %s, dtype=%s", device, dtype)

    n_layers = getattr(model.config, "num_hidden_layers", None)
    h_size = getattr(model.config, "hidden_size", None)
    logger.info("Architecture: %d layers × %d hidden", n_layers, h_size)
    return tokenizer, model, n_layers, h_size


def extract_hidden_state(
    model,
    tokenizer,
    prompt: str,
    layer_idx: int,
) -> tuple[Any, dict[str, Any]]:
    """Forward pass + extract layer_idx hidden state. Returns (vector, metadata)."""
    import torch

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)

    # outputs.hidden_states is tuple of (n_layers + 1) tensors,
    # each (batch, seq_len, hidden_size). Index 0 = embedding, last = final layer.
    hidden_states = outputs.hidden_states
    n_states = len(hidden_states)

    if layer_idx >= n_states:
        raise IndexError(f"layer_idx={layer_idx} >= n_states={n_states}")

    layer_tensor = hidden_states[layer_idx]  # (batch, seq_len, hidden_size)
    seq_len = layer_tensor.shape[1]

    # Mean pool last 5 tokens (per Farquhar 2024 probe methodology)
    last_tokens = layer_tensor[0, -5:, :]  # (5, hidden_size)
    pooled = last_tokens.mean(dim=0).float().cpu().numpy()  # (hidden_size,)

    metadata = {
        "shape_layer_tensor": list(layer_tensor.shape),
        "seq_len": seq_len,
        "n_hidden_states": n_states,
        "pooled_shape": pooled.shape,
        "pooled_norm": float((pooled**2).sum() ** 0.5),
        "has_nan": bool((layer_tensor != layer_tensor).any().item()),
        "has_inf": bool(layer_tensor.abs().max().item() == float("inf")),
    }
    return pooled, metadata


def cosine_similarity(a, b) -> float:
    import numpy as np

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


def run_test(model_name: str, layer_idx: int, device: str) -> dict[str, Any]:
    tokenizer, model, n_layers, h_size = load_bielik(model_name, device=device)
    arch_ok = n_layers == EXPECTED_NUM_LAYERS and h_size == EXPECTED_HIDDEN_SIZE

    vectors: list[Any] = []
    per_prompt_meta: list[dict[str, Any]] = []
    extraction_ok = True
    for i, prompt in enumerate(TEST_PROMPTS):
        try:
            vec, meta = extract_hidden_state(model, tokenizer, prompt, layer_idx)
            vectors.append(vec)
            per_prompt_meta.append({"prompt_idx": i, "ok": True, **meta})
            logger.info(
                "Prompt %d: shape=%s, norm=%.2f", i, meta["pooled_shape"], meta["pooled_norm"]
            )
        except Exception as exc:
            extraction_ok = False
            per_prompt_meta.append({"prompt_idx": i, "ok": False, "error": str(exc)})
            logger.error("Prompt %d FAILED: %s", i, exc)

    differentiation_ok = False
    similarities: list[float] = []
    if len(vectors) >= 2:
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                similarities.append(cosine_similarity(vectors[i], vectors[j]))
        max_sim = max(similarities) if similarities else 1.0
        # Different prompts should have cosine similarity < 0.95
        differentiation_ok = max_sim < 0.95
        logger.info(
            "Pairwise cosines: max=%.3f, mean=%.3f", max_sim, sum(similarities) / len(similarities)
        )

    return {
        "model": model_name,
        "device": device,
        "layer_idx": layer_idx,
        "n_layers_actual": n_layers,
        "n_layers_expected": EXPECTED_NUM_LAYERS,
        "hidden_size_actual": h_size,
        "hidden_size_expected": EXPECTED_HIDDEN_SIZE,
        "arch_ok": arch_ok,
        "extraction_ok": extraction_ok,
        "differentiation_ok": differentiation_ok,
        "similarities": [round(s, 3) for s in similarities],
        "per_prompt": per_prompt_meta,
        "kill_criteria": {
            "all extractions OK": extraction_ok,
            "no NaN/inf in any layer tensor": all(
                not m.get("has_nan") and not m.get("has_inf") for m in per_prompt_meta if m["ok"]
            ),
            "differentiation max_cosine < 0.95": differentiation_ok,
        },
        "PASS": arch_ok and extraction_ok and differentiation_ok,
        "timestamp": datetime.now().isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="speakleash/Bielik-11B-v3.0-Instruct")
    parser.add_argument("--layer", type=int, default=DEFAULT_PROBE_LAYER)
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    parser.add_argument("--output-dir", type=Path, default=Path("iter0b_poc/results"))
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    summary = run_test(args.model, args.layer, args.device)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.output_dir / f"t3_hooks_bielik_{timestamp}.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== T3 PyTorch hooks Bielik layer {args.layer} — {timestamp} ===")
    print(f"Model: {args.model}")
    print(
        f"Architecture: {summary['n_layers_actual']} × {summary['hidden_size_actual']} "
        f"(expected: {EXPECTED_NUM_LAYERS} × {EXPECTED_HIDDEN_SIZE})"
    )
    print(f"Arch OK: {summary['arch_ok']}")
    print(f"Extraction OK: {summary['extraction_ok']}")
    print(f"Differentiation OK: {summary['differentiation_ok']}")
    print(f"VERDICT: {'PASS' if summary['PASS'] else 'FAIL'}")
    print(f"Detail: {out_path}")
    return 0 if summary["PASS"] else 2


if __name__ == "__main__":
    sys.exit(main())
