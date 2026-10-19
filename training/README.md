# Hugging Face training pilot

Status: **prepared, not submitted; no trained model exists from this task yet**.

The connected `AGIbuild` Pro account can submit Jobs, but its OAuth scopes include `read-repos` and do not include repository write. The training skill requires durable Hub persistence. A paid GPU run has therefore not been launched with credentials that cannot save results. Reconnect Hugging Face with repository-write access and a writable `HF_TOKEN` secret for Jobs. Do not paste a token into chat or commit it.

## Concrete run configuration

- Base: `Qwen/Qwen2.5-0.5B-Instruct` (Apache 2.0), a small baseline, not a claim of optimal Hindi quality.
- NVIDIA T4 (`t4-small`) via Hugging Face Jobs, 2-hour hard timeout, two epochs, LoRA rank 8.
- 104 synthetic training examples and 28 held-out examples, generated from the existing illustrative lesson pack. Split by topic, including refusals. This small set tests tutoring style and pipeline viability; it cannot establish teaching quality.
- Private output target: `AGIbuild/indigloo-mentor-qwen-0.5b-pilot`.
- Trackio training logs; checkpoints and evaluation metrics uploaded to the Hub.
- Resource use/cost depends on current Hugging Face pricing and queue time; no job has been billed by this workflow.

`prepare_data.py` regenerates the JSONL files. `train.py` is a PEP 723 UV script with pinned dependencies and a Hub-write preflight. `job.json` contains the complete script and inline training/evaluation data, so it does not depend on publishing this repository. Submit it through the Hugging Face Jobs tool after repository-write credentials are available.

After training, inspect both baseline and adapter outputs on the topic holdout plus teacher-written Hindi/English questions. Record factual errors, refusal false positives, age appropriateness, answer leakage in hint mode, and Hindi fluency. Evaluation loss alone is not an acceptance gate. Keep model inference opt-in until this review passes.

## Serving and Android

The output is a **LoRA adapter**, not a standalone Android model. For server use, deploy the base+adapter with a compatible Hugging Face endpoint. For a future offline model, merge/convert using the target runtime's supported architecture, quantize, check the license, then measure peak RSS, cold load, tokens/sec, battery and thermal behaviour on real low-end phones. No GGUF/LiteRT compatibility or memory target is assumed.

Official references: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct and https://huggingface.co/docs/trl/sft_trainer
