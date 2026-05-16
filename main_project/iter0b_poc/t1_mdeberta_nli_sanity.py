"""T1 POC: mDeBERTa NLI sanity na 50 par UOKiK Q&A.

Cel: zweryfikować że MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
poprawnie klasyfikuje (claim, evidence) → entailed/contradicted/neutral na
polskim consumer rights data PRZED inwestowaniem w pełen pipeline.

Methodology:
1. Wczytaj 50 UOKiK gold pairs (z citations) z processed dataset
2. Per pair: claim = answer paragraph, evidence = retrieved chunk text
   z citation (jeśli matchowane w cited_articles → use chunk; else skip)
3. Run mDeBERTa NLI inference per (claim, evidence) → predicted label
4. Manual ground truth: UOKiK answers SHOULD be entailed by their citations
5. Report: accuracy, per-class precision/recall, sample errors

Kill criterion: accuracy < 50% = random → upgrade Tier 2 verifier wcześniej

CLI:
    uv run python -m iter0b_poc.t1_mdeberta_nli_sanity \\
        --dataset data/processed/citationbench_v0.4_2026-05-16/chunks.jsonl \\
        --halu-pairs data/processed/citationbench_v0.4_2026-05-16/halu_pairs.jsonl \\
        --n-samples 50
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

NLI_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
LABEL_MAP = {0: "entailed", 1: "neutral", 2: "contradicted"}


def load_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if limit and i >= limit:
                break
            records.append(json.loads(line))
    return records


def build_eval_pairs(
    chunks: list[dict[str, Any]],
    halu_pairs: list[dict[str, Any]],
    n_samples: int,
) -> list[dict[str, Any]]:
    """Build (claim, evidence, expected_label) tuples.

    Strategy:
    1. Take 25 negative samples (is_hallucinated=False) → expected ENTAILED
    2. Take 25 positive samples (is_hallucinated=True) → expected CONTRADICTED
    3. Per pair: lookup evidence chunk text z chunks corpus by chunk_id
    """
    chunk_by_id = {c["chunk_id"]: c for c in chunks}
    eval_pairs: list[dict[str, Any]] = []

    negs = [p for p in halu_pairs if not p["is_hallucinated"]][: n_samples // 2]
    poss = [p for p in halu_pairs if p["is_hallucinated"]][: n_samples // 2]

    for pair in negs + poss:
        evidence_text = ""
        for chunk_id in pair.get("evidence_chunks", []):
            if chunk_id in chunk_by_id:
                evidence_text = chunk_by_id[chunk_id]["tresc"]
                break
        if not evidence_text:
            # Fallback: use cited_articles string jako evidence proxy
            evidence_text = " ; ".join(pair.get("evidence_chunks", []))[:500]
            if not evidence_text:
                continue
        expected = "entailed" if not pair["is_hallucinated"] else "contradicted"
        eval_pairs.append(
            {
                "pair_id": pair["pair_id"],
                "claim": pair["claim"][:1000],  # truncate for NLI input limit
                "evidence": evidence_text[:1000],
                "expected": expected,
                "halu_type": pair.get("halu_type"),
            }
        )

    logger.info("Built %d eval pairs (target %d)", len(eval_pairs), n_samples)
    return eval_pairs


def run_nli_inference(eval_pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Load mDeBERTa + predict per pair."""
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as exc:
        logger.error("Missing deps: pip install transformers torch sentencepiece — %s", exc)
        sys.exit(1)

    logger.info("Loading %s ...", NLI_MODEL)
    tokenizer = AutoTokenizer.from_pretrained(NLI_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL)
    model.eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    logger.info("Model loaded on %s", device)

    results: list[dict[str, Any]] = []
    for i, pair in enumerate(eval_pairs):
        # NLI input format: premise=evidence, hypothesis=claim
        inputs = tokenizer(
            pair["evidence"],
            pair["claim"],
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to(device)
        with torch.no_grad():
            logits = model(**inputs).logits
        pred_idx = int(logits.argmax(dim=-1).item())
        pred_label = LABEL_MAP[pred_idx]
        results.append(
            {
                **pair,
                "predicted": pred_label,
                "logits": logits.tolist()[0],
                "correct": pred_label == pair["expected"],
            }
        )
        if (i + 1) % 10 == 0:
            logger.info("Processed %d/%d", i + 1, len(eval_pairs))

    return results


def report(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute accuracy + per-class P/R + error analysis."""
    correct = sum(1 for r in results if r["correct"])
    accuracy = correct / max(len(results), 1)

    cm: Counter[tuple[str, str]] = Counter()
    for r in results:
        cm[(r["expected"], r["predicted"])] += 1

    per_class: dict[str, dict[str, float]] = {}
    for label in ["entailed", "neutral", "contradicted"]:
        tp = cm[(label, label)]
        fp = sum(
            cm[(other, label)]
            for other in ["entailed", "neutral", "contradicted"]
            if other != label
        )
        fn = sum(
            cm[(label, other)]
            for other in ["entailed", "neutral", "contradicted"]
            if other != label
        )
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        per_class[label] = {"precision": round(precision, 3), "recall": round(recall, 3)}

    errors = [r for r in results if not r["correct"]][:5]

    summary = {
        "model": NLI_MODEL,
        "n_samples": len(results),
        "accuracy": round(accuracy, 3),
        "kill_criterion": "accuracy >= 0.50 (random baseline)",
        "PASS": accuracy >= 0.50,
        "per_class": per_class,
        "confusion_matrix": {f"{e}->{p}": c for (e, p), c in cm.items()},
        "sample_errors": errors,
        "timestamp": datetime.now().isoformat(),
    }
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/processed/citationbench_v0.4_2026-05-16/chunks.jsonl"),
    )
    parser.add_argument(
        "--halu-pairs",
        type=Path,
        default=Path("data/processed/citationbench_v0.4_2026-05-16/halu_pairs.jsonl"),
    )
    parser.add_argument("--n-samples", type=int, default=50)
    parser.add_argument("--output-dir", type=Path, default=Path("iter0b_poc/results"))
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    chunks = load_jsonl(args.dataset)
    halu_pairs = load_jsonl(args.halu_pairs)
    logger.info("Loaded %d chunks + %d halu pairs", len(chunks), len(halu_pairs))

    eval_pairs = build_eval_pairs(chunks, halu_pairs, args.n_samples)
    if not eval_pairs:
        logger.error("No eval pairs built — check dataset paths")
        return 1

    results = run_nli_inference(eval_pairs)
    summary = report(results)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.output_dir / f"t1_mdeberta_{timestamp}.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== T1 mDeBERTa NLI sanity — {timestamp} ===")
    print(f"Model: {NLI_MODEL}")
    print(f"Samples: {summary['n_samples']}")
    print(f"Accuracy: {summary['accuracy']:.1%}")
    print(f"Kill criterion: {summary['kill_criterion']}")
    print(f"VERDICT: {'PASS' if summary['PASS'] else 'FAIL'}")
    print(f"Per-class P/R: {summary['per_class']}")
    print(f"Detail: {out_path}")
    return 0 if summary["PASS"] else 2


if __name__ == "__main__":
    sys.exit(main())
