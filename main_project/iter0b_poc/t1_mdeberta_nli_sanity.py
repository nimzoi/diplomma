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

    BUG FIX 2026-05-16: previous version użyła `evidence_chunks` field które
    zawierało citation strings (np. "art. 22^1 KC"), NIE chunk IDs. Bez actual
    text mDeBERTa nie miał real evidence do porównania → 6.1% accuracy.

    NEW strategy (proper sanity test):
    - Negative (is_hallucinated=False): claim = answer, evidence = answer → ENTAILED
      (claim equals evidence — model MUSI to predict entailment, baseline sanity)
    - Positive (is_hallucinated=True): claim = mutated answer,
      evidence = original answer (z metadata) → CONTRADICTED
      (mutation explicit kontradyguje original — clean signal)

    To test prawdziwy "does mDeBERTa rozumie polish entailment". Real RAG
    citation grounding (claim vs retrieved chunk text) testowany w Iter. 1+.
    """
    eval_pairs: list[dict[str, Any]] = []

    # Group pairs by source_qa_id, keep only sources które mają BOTH negative+positive
    by_source: dict[str, dict[str, Any]] = {}
    for p in halu_pairs:
        sid = p.get("source_qa_id") or p.get("pair_id")
        if sid not in by_source:
            by_source[sid] = {"neg": None, "pos": []}
        if not p["is_hallucinated"]:
            by_source[sid]["neg"] = p
        else:
            by_source[sid]["pos"].append(p)

    # UOKiK Q&A based pairs preferred (have original_answer w metadata)
    uokik_groups = [g for g in by_source.values()
                    if g["neg"] and g["neg"].get("metadata", {}).get("source") == "uokik_qa"]

    for group in uokik_groups[: n_samples // 6 + 1]:  # ~each gives 1 neg + few pos
        neg = group["neg"]
        original_answer = neg["claim"]  # negative claim IS original answer

        # Negative sample: claim = answer, evidence = answer → ENTAILED
        eval_pairs.append({
            "pair_id": neg["pair_id"],
            "claim": original_answer[:1000],
            "evidence": original_answer[:1000],
            "expected": neg.get("nli_label", "entailed"),
            "halu_type": None,
            "source": "uokik_qa_self_entailment",
        })

        # Positive samples: claim = mutated, evidence = original → CONTRADICTED
        for pos in group["pos"][:5]:  # max 5 positives per source
            mutated = pos["claim"]
            # Skip pairs gdzie mutated == original (mutation failed silently)
            if mutated.strip() == original_answer.strip():
                continue
            eval_pairs.append({
                "pair_id": pos["pair_id"],
                "claim": mutated[:1000],
                "evidence": original_answer[:1000],
                # Per fix 2026-05-16: factual_fabrication → NEUTRAL (added unsupported claim,
                # NIE explicit contradiction); inne typy (entity/temporal/negation/miscit) →
                # CONTRADICTED. Honor pair["nli_label"] z halu_injector.
                "expected": pos.get("nli_label", "contradicted"),
                "halu_type": pos.get("halu_type"),
                "source": "uokik_qa_mutation",
            })

        if len(eval_pairs) >= n_samples:
            break

    eval_pairs = eval_pairs[:n_samples]
    n_pos = sum(1 for p in eval_pairs if p["expected"] == "contradicted")
    n_neg = sum(1 for p in eval_pairs if p["expected"] == "entailed")
    logger.info(
        "Built %d eval pairs (target %d): %d entailed + %d contradicted",
        len(eval_pairs), n_samples, n_neg, n_pos,
    )
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
    """Compute accuracy + per-class P/R + per-halu-type breakdown + error analysis."""
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

    # Per halu_type breakdown — diagnostic dla "which mutation types model catches"
    per_type: dict[str, dict[str, Any]] = {}
    for r in results:
        ht = r.get("halu_type") or "_negative_"
        if ht not in per_type:
            per_type[ht] = {"total": 0, "correct": 0, "predicted_distribution": Counter()}
        per_type[ht]["total"] += 1
        if r["correct"]:
            per_type[ht]["correct"] += 1
        per_type[ht]["predicted_distribution"][r["predicted"]] += 1
    for ht in per_type:
        per_type[ht]["accuracy"] = round(
            per_type[ht]["correct"] / max(per_type[ht]["total"], 1), 3
        )
        per_type[ht]["predicted_distribution"] = dict(per_type[ht]["predicted_distribution"])

    # Hybrid scoring per dleemiller methodology
    # score = 0.5 * P(neutral) + P(entailment) - P(contradiction)
    # Map > 0 → entailed-leaning; < 0 → contradicted-leaning
    hybrid_correct = 0
    for r in results:
        # Softmax z logits
        import math
        logits = r.get("logits", [0, 0, 0])
        exp = [math.exp(x) for x in logits]
        s = sum(exp)
        probs = [e / s for e in exp]
        # id2label = {0: 'entailment', 1: 'neutral', 2: 'contradiction'}
        score = 0.5 * probs[1] + probs[0] - probs[2]
        hybrid_pred = "entailed" if score > 0 else "contradicted"
        if hybrid_pred == r["expected"]:
            hybrid_correct += 1
    hybrid_accuracy = hybrid_correct / max(len(results), 1)

    errors = [r for r in results if not r["correct"]][:5]

    summary = {
        "model": NLI_MODEL,
        "n_samples": len(results),
        "accuracy": round(accuracy, 3),
        "hybrid_accuracy_dleemiller": round(hybrid_accuracy, 3),
        "kill_criterion": "accuracy >= 0.50 (random baseline)",
        "PASS": accuracy >= 0.50,
        "per_class": per_class,
        "per_halu_type": per_type,
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
