"""T2 POC: Outlines + Bielik 11B v3 z polish diakrytyki + structured JSON.

Cel: zweryfikować że structured output (Outlines) na Bielik 11B v3:
1. Generuje VALID JSON (parseable, conforms to Pydantic schema)
2. Zachowuje polish diakrytyki (ą, ć, ę, ł, ń, ó, ś, ź, ż) — NIE łamie ich na escape
3. NIE crashuje na polish prompts

Methodology:
1. Define Pydantic schema dla citation-grounded answer (claim + citations + reasoning)
2. Build 10 polish consumer rights prompts (z UOKiK Q&A)
3. Run Bielik 11B v3 + Outlines structured generation
4. Per response: parse JSON, count diakrytyki preservation, validate schema

Kill criterion:
- valid JSON < 80% → switch z Outlines na xgrammar lub regex extraction
- diakrytyki preservation < 95% → Bielik tokenizer issue, re-investigate

Wymagania: lab GPU (H200 80GB) lub fallback Bielik 1.5B/3B (per CLAUDE.md spec).

CLI:
    uv run python -m iter0b_poc.t2_outlines_bielik_diakrytyki \\
        --model speakleash/Bielik-11B-v3.0-Instruct \\
        --n-prompts 10
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Polish diacritics
POLISH_DIACRITICS = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
DIACRITICS_RE = re.compile(f"[{POLISH_DIACRITICS}]")


# Test prompts — 10 polish consumer rights questions z UOKiK
TEST_PROMPTS = [
    {
        "id": "p01",
        "question": "Czy konsument ma prawo zwrócić towar zakupiony w sklepie internetowym bez podawania przyczyny?",
        "expected_diacritics_min": 5,  # zwrócić, bez, działalności itd.
    },
    {
        "id": "p02",
        "question": "Jakie są zasady reklamacji produktu z tytułu rękojmi?",
        "expected_diacritics_min": 4,  # rękojmi, są
    },
    {
        "id": "p03",
        "question": "Co oznacza nieuczciwa praktyka rynkowa w rozumieniu polskiego prawa?",
        "expected_diacritics_min": 3,
    },
    {
        "id": "p04",
        "question": "W jakim terminie konsument może odstąpić od umowy zawartej na odległość?",
        "expected_diacritics_min": 4,
    },
    {
        "id": "p05",
        "question": "Czym różni się rękojmia od gwarancji?",
        "expected_diacritics_min": 4,
    },
    {
        "id": "p06",
        "question": "Jakie obowiązki ma przedsiębiorca przed zawarciem umowy z konsumentem?",
        "expected_diacritics_min": 4,
    },
    {
        "id": "p07",
        "question": "Co to są klauzule niedozwolone w umowach konsumenckich?",
        "expected_diacritics_min": 5,
    },
    {
        "id": "p08",
        "question": "Jakie informacje musi otrzymać konsument przed zawarciem umowy o kredyt konsumencki?",
        "expected_diacritics_min": 4,
    },
    {
        "id": "p09",
        "question": "Czy mogę odstąpić od umowy ubezpieczenia w terminie 30 dni?",
        "expected_diacritics_min": 4,
    },
    {
        "id": "p10",
        "question": "Jakie prawa przysługują pasażerowi w przypadku odwołania lotu przez przewoźnika?",
        "expected_diacritics_min": 5,
    },
]


# Pydantic schema dla structured output
CITATION_ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string", "minLength": 50},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim_text": {"type": "string"},
                    "supporting_citation": {"type": "string"},
                },
                "required": ["claim_text", "supporting_citation"],
            },
            "minItems": 1,
        },
        "primary_citation": {
            "type": "string",
            "description": "Główna cytacja, np. 'art. 27 ust. 1 Ustawy o prawach konsumenta'",
        },
    },
    "required": ["answer", "claims", "primary_citation"],
}


def count_diacritics(text: str) -> int:
    return len(DIACRITICS_RE.findall(text))


def run_inference_outlines(
    model_name: str,
    prompts: list[dict[str, Any]],
    device: str = "auto",
) -> list[dict[str, Any]]:
    """Run Bielik via Outlines structured generation."""
    try:
        import torch
        from outlines import generate, models
    except ImportError as exc:
        logger.error("Missing deps: pip install outlines transformers torch — %s", exc)
        sys.exit(1)

    logger.info("Loading %s ...", model_name)
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = models.transformers(model_name, device=device)
    generator = generate.json(model, CITATION_ANSWER_SCHEMA)

    results: list[dict[str, Any]] = []
    for p in prompts:
        prompt = (
            "Jesteś ekspertem polskiego prawa konsumenta. Odpowiedz na pytanie "
            "z dokładnymi cytacjami do polskich ustaw konsumenckich.\n\n"
            f"Pytanie: {p['question']}\n\n"
            "Odpowiedz w formacie JSON z polami: answer (pełna odpowiedź), "
            "claims (lista par claim_text + supporting_citation), "
            "primary_citation (główna cytacja). "
            "ZACHOWAJ POLSKIE DIAKRYTYKI (ą, ć, ę, ł, ń, ó, ś, ź, ż).\n\n"
            "JSON:"
        )
        try:
            response = generator(prompt, max_tokens=1024)
            response_text = (
                json.dumps(response, ensure_ascii=False)
                if isinstance(response, dict)
                else str(response)
            )
            valid_json = isinstance(response, dict)
        except Exception as exc:
            response_text = f"ERROR: {exc}"
            valid_json = False
        diacritics_count = count_diacritics(response_text)
        results.append(
            {
                **p,
                "response_text": response_text[:2000],
                "valid_json": valid_json,
                "diacritics_count": diacritics_count,
                "diacritics_pass": diacritics_count >= p["expected_diacritics_min"],
            }
        )
        logger.info(
            "Prompt %s: valid_json=%s, diacritics=%d", p["id"], valid_json, diacritics_count
        )

    return results


def report(results: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(results)
    valid_json_rate = sum(1 for r in results if r["valid_json"]) / max(n, 1)
    diacritics_pass_rate = sum(1 for r in results if r["diacritics_pass"]) / max(n, 1)

    return {
        "n_prompts": n,
        "valid_json_rate": round(valid_json_rate, 3),
        "diacritics_pass_rate": round(diacritics_pass_rate, 3),
        "kill_criteria": {
            "valid_json >= 0.80": valid_json_rate >= 0.80,
            "diacritics >= 0.95": diacritics_pass_rate >= 0.95,
        },
        "PASS": valid_json_rate >= 0.80 and diacritics_pass_rate >= 0.95,
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="speakleash/Bielik-11B-v3.0-Instruct")
    parser.add_argument("--n-prompts", type=int, default=10)
    parser.add_argument("--output-dir", type=Path, default=Path("iter0b_poc/results"))
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    prompts = TEST_PROMPTS[: args.n_prompts]
    results = run_inference_outlines(args.model, prompts, device=args.device)
    summary = report(results)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.output_dir / f"t2_outlines_bielik_{timestamp}.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== T2 Outlines+Bielik diakrytyki — {timestamp} ===")
    print(f"Model: {args.model}")
    print(f"Prompts: {summary['n_prompts']}")
    print(f"Valid JSON rate: {summary['valid_json_rate']:.1%} (kill: <80%)")
    print(f"Diakrytyki rate: {summary['diacritics_pass_rate']:.1%} (kill: <95%)")
    print(f"VERDICT: {'PASS' if summary['PASS'] else 'FAIL'}")
    print(f"Detail: {out_path}")
    return 0 if summary["PASS"] else 2


if __name__ == "__main__":
    sys.exit(main())
