# Iter. 0b POC — 4 kill-criteria tests

**Cel:** zweryfikować przed build full pipeline że 4 fundamenty działają. Te są **kill criteria** z `thesis_research/decisions/DEC-003_pivot-na-halu-detection.md`. Jeśli któryś fail — pivot lub re-scope.

## Tests overview

| Test | Co weryfikuje | Time | GPU? | Output if PASS |
|---|---|---|---|---|
| **T1: mDeBERTa NLI sanity** | Czy `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` poprawnie klasyfikuje (claim, evidence) → entailed/contradicted/neutral na 50 par UOKiK | 5-15 min | NIE (CPU OK) | accuracy ≥70% na sample |
| **T2: Outlines + Bielik z polish diakrytyki** | Czy structured output (Outlines/JSON schema) na Bielik 11B v3 zachowuje polish diakrytyki + valid JSON | 30 min | TAK (lab) | 95%+ valid JSON, 100% diakrytyki preserved |
| **T3: PyTorch hooks na Bielik layer 47** | Czy można ekstraktować hidden states z Bielik 11B layer 47 (⌊0.95 × 50⌋) bez crashu, shape (batch, seq_len, 4096) | 30-60 min | TAK (lab) | tensor extracted, shape verified, no OOM |
| **T4: Lab GPU verify** | SSH access + Bielik 11B v3 download + smoke inference | 60 min | TAK (lab) | ssh + load + 1 prompt response |

## Prerequisites

```bash
cd /d/diplomma
uv sync                                    # install deps (z pyproject)
huggingface-cli login                      # HF token z .env
huggingface-cli download speakleash/Bielik-11B-v3.0-Instruct  # ~22 GB bf16
huggingface-cli download MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
```

## Run order

1. **T1 first** (CPU, fastest) — jeśli mDeBERTa NLI nie działa na polish, to verifier R3 cały re-think
2. **T4 second** (lab access first thing) — bez GPU reszta blocked
3. **T3 third** (probe extraction is RQ1 core)
4. **T2 last** (Outlines structured output dla generation, mniej critical)

## Kill criteria per test

- **T1 fails** (accuracy < 50% = random) → upgrade Tier 2 verifier (HerBERT-large + CDSC-E fine-tune) earlier
- **T2 fails** (broken JSON > 20% lub diakrytyki gone > 5%) → switch z Outlines na xgrammar lub plain prompt+regex
- **T3 fails** (OOM / shape mismatch / hooks crash) → fallback Bielik 1.5B/3B dla local CPU dev (per CLAUDE.md spec)
- **T4 fails** (no SSH / no model load) → re-negotiate lab access lub Colab Pro+ alternative

## Files

- `t1_mdeberta_nli_sanity.py` — T1 script
- `t2_outlines_bielik_diakrytyki.py` — T2 script
- `t3_pytorch_hooks_bielik.py` — T3 script
- `t4_lab_gpu_verify.py` — T4 script
- `expected_outputs/` — sample expected JSON dla diff
- `results/` — per-run output JSONL z timestamp

## After all 4 PASS

- Sign-off w `thesis_research/decisions/DEC-004_iter0b_poc_results.md`
- Then start Iter. 1 (probe training pipeline + RAG demo)
