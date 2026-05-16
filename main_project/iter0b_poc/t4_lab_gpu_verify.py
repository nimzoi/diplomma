"""T4 POC: lab GPU verify — SSH access + Bielik download + smoke inference.

Cel: zweryfikować że lab GPU (SP7 H200 80GB lub equivalent) jest:
1. Accessible via SSH (config + key + reachable)
2. Ma wystarczająco VRAM (≥40 GB free) dla Bielik 11B v3 bf16
3. CUDA visible + nvidia-smi działa
4. Bielik 11B v3 załaduje się + zwróci sensowny output dla 1 prompt
5. Inference time per prompt < 30s (sanity check)

Methodology:
- Local script: SSH command z hostname → uruchomić smoke test na lab
- Lab side: Python z transformers + torch + load Bielik + 1 inference + report

Kill criterion:
- SSH unreachable → re-negotiate lab access (Magdy ZAiAI@LAB)
- Bielik OOM → switch FP8 dynamic variant (50% VRAM) lub Bielik 1.5B/3B local fallback
- Inference > 60s/prompt → sequence parallelism / vLLM serving zamiast bare HF

CLI:
    # Local — invokes SSH:
    uv run python -m iter0b_poc.t4_lab_gpu_verify \\
        --ssh-host magma@lab.pjwstk.edu.pl \\
        --remote-workdir /home/magma/diplomma

    # Lab side — direct invocation (after ssh/scp):
    uv run python -m iter0b_poc.t4_lab_gpu_verify --mode lab-side
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

LAB_SIDE_PYTHON = """
import json, time, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

result = {"timestamp": "{ts}"}

# 1. CUDA check
result["cuda_available"] = torch.cuda.is_available()
result["cuda_device_count"] = torch.cuda.device_count()
if torch.cuda.is_available():
    result["cuda_device_name"] = torch.cuda.get_device_name(0)
    props = torch.cuda.get_device_properties(0)
    result["vram_total_gb"] = round(props.total_memory / 1e9, 1)
    result["compute_capability"] = f"{props.major}.{props.minor}"

# 2. Load Bielik 11B v3
model_name = "speakleash/Bielik-11B-v3.0-Instruct"
print(f"[lab] Loading {model_name} ...")
t0 = time.time()
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="cuda",
)
result["load_time_sec"] = round(time.time() - t0, 1)
result["model_dtype"] = str(model.dtype)
result["model_n_params_M"] = sum(p.numel() for p in model.parameters()) / 1e6

# 3. Smoke inference
prompt = (
    "Konsument zawarł umowę na odległość. Czy może odstąpić w 14 dni bez "
    "podawania przyczyny? Odpowiedz krótko."
)
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
t0 = time.time()
with torch.no_grad():
    output_ids = model.generate(
        **inputs, max_new_tokens=200, do_sample=False, temperature=1.0,
    )
result["inference_time_sec"] = round(time.time() - t0, 1)
output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
result["output_text"] = output_text[:500]
result["output_len_chars"] = len(output_text)

# 4. VRAM after
if torch.cuda.is_available():
    result["vram_used_gb"] = round(torch.cuda.memory_allocated() / 1e9, 1)
    result["vram_reserved_gb"] = round(torch.cuda.memory_reserved() / 1e9, 1)

# 5. Kill criteria check
result["PASS"] = (
    result["cuda_available"]
    and result.get("vram_total_gb", 0) >= 40
    and result["inference_time_sec"] < 60
    and len(output_text) > 30
)

print(json.dumps(result, ensure_ascii=False, indent=2))
"""


def run_local_ssh(ssh_host: str, remote_workdir: str, output_dir: Path) -> dict[str, Any]:
    """Invoke lab-side script via SSH."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_content = LAB_SIDE_PYTHON.replace("{ts}", timestamp)

    # Write temp script
    tmp_script = output_dir / f"_t4_lab_script_{timestamp}.py"
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_script.write_text(script_content, encoding="utf-8")

    # SCP + SSH execute
    remote_script = f"{remote_workdir}/iter0b_poc/_t4_lab_script_{timestamp}.py"

    logger.info("Copying script to %s:%s", ssh_host, remote_script)
    scp = subprocess.run(
        ["scp", str(tmp_script), f"{ssh_host}:{remote_script}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if scp.returncode != 0:
        return {
            "PASS": False,
            "error": "scp_failed",
            "stderr": scp.stderr,
            "ssh_host": ssh_host,
        }

    logger.info("Executing remote script ...")
    cmd = f"cd {remote_workdir} && uv run python {remote_script}"
    ssh = subprocess.run(
        ["ssh", ssh_host, cmd],
        capture_output=True,
        text=True,
        timeout=600,
    )

    # Try parse JSON from output
    try:
        # Find first { in stdout (lab script prints JSON at end)
        out = ssh.stdout
        start = out.find("{")
        end = out.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(out[start:end])
    except Exception as exc:
        logger.error("JSON parse failed: %s", exc)

    return {
        "PASS": False,
        "error": "remote_exec_or_json_parse_failed",
        "stdout": ssh.stdout[:2000],
        "stderr": ssh.stderr[:2000],
    }


def run_lab_side(output_dir: Path) -> dict[str, Any]:
    """Direct invocation when running on lab GPU."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_content = LAB_SIDE_PYTHON.replace("{ts}", timestamp)
    namespace: dict[str, Any] = {}
    exec(script_content, namespace)  # noqa: S102 — controlled local code
    return namespace.get("result", {"PASS": False, "error": "no_result"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["ssh", "lab-side"], default="ssh")
    parser.add_argument("--ssh-host", help="user@host dla SSH (np. magma@lab.pjwstk.edu.pl)")
    parser.add_argument(
        "--remote-workdir",
        default="/home/magma/diplomma",
        help="Remote project root na lab",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("iter0b_poc/results"))
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.mode == "ssh":
        if not args.ssh_host:
            logger.error("--ssh-host required for ssh mode")
            return 1
        summary = run_local_ssh(args.ssh_host, args.remote_workdir, args.output_dir)
    else:
        summary = run_lab_side(args.output_dir)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.output_dir / f"t4_lab_gpu_{timestamp}.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== T4 Lab GPU verify — {timestamp} ===")
    print(f"CUDA: {summary.get('cuda_available')} | VRAM: {summary.get('vram_total_gb')} GB")
    print(
        f"Load time: {summary.get('load_time_sec')}s | Inference: "
        f"{summary.get('inference_time_sec')}s"
    )
    print(f"Output: {summary.get('output_text', summary.get('error', '?'))[:200]}")
    print(f"VERDICT: {'PASS' if summary.get('PASS') else 'FAIL'}")
    print(f"Detail: {out_path}")
    return 0 if summary.get("PASS") else 2


if __name__ == "__main__":
    sys.exit(main())
