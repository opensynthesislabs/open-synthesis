# Model Card: Open Synthesis Synthesis Layer

## Current Production Model

### Llama 3.1 70B with Heretic Ablation

**Base model:** `meta-llama/Llama-3.1-70B-Instruct` (Llama 3.1 Community License)
**Ablated model:** [`opensynthesis/Llama-3.1-70B-heretic-lora`](https://huggingface.co/opensynthesis/Llama-3.1-70B-heretic-lora) (HuggingFace)
**Distribution:** Full ablated model. Use requires acceptance of the [Llama 3.1 Community License](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE).
**Parameter count:** 70 billion
**Architecture:** `LlamaForCausalLM`
**Context window:** 128,000 tokens (fully usable in serving config)

**Why Llama 3.1 70B:**
- Native 128K context window — no truncation needed for dense multi-source synthesis
- 70B parameters provide substantially stronger reasoning than 14B for complex analytical tasks
- Strong instruction following and citation-grounding behavior
- Proven compatibility with Heretic ablation (Llama 8B baseline in Heretic's own benchmarks)
- Well-supported by vLLM with tensor parallelism for efficient multi-GPU serving
- AWQ 4-bit quantization fits on 2x A100 80GB with full context window

**Ablation:** Heretic directional ablation with `bnb_4bit` quantization on H100 SXM 80GB. 200 Optuna TPE trials optimizing refusal rate and KL divergence.

**Hardware for inference (AWQ 4-bit, tensor parallel):**
- Recommended: 2x A100 80GB ($2.38/hr on RunPod)
- vLLM config: `--quantization awq --tensor-parallel-size 2 --max-model-len 131072`
- Pod can be stopped when idle (~$7-10/mo storage), cold-started on demand (~3-5 min)

---

### Previous Production Model: Qwen3-14B

**Base model:** `Qwen/Qwen3-14B`
**Post-ablation:** [`opensynthesis/Qwen3-14B-heretic`](https://huggingface.co/opensynthesis/Qwen3-14B-heretic) (HuggingFace)
**License:** Apache 2.0
**Parameter count:** 14 billion
**Architecture:** `Qwen3ForCausalLM`
**Context window:** 32,768 tokens (serving config; model supports 128K natively)

Still available and usable for lower-cost deployments. Fits on a single A40 48GB at fp16 (~$0.40/hr). Ablation results: 3/100 refusals, KL ~5e-8.

**Thinking mode:** Qwen3 includes a `<think>` reasoning mode. The synthesis client disables this automatically via `chat_template_kwargs: {"enable_thinking": false}` when a Qwen model is detected.

---

## Heretic Ablation Results

The following table documents expected ablation quality metrics for each recommended model, based on Heretic's built-in evaluation framework. These should be reproduced after running ablation and verified before deployment.

| Model | Baseline refusals | Post-ablation refusals | KL divergence | Trials |
|---|---|---|---|---|
| **Llama 3.1 70B** (production) | ~85/100 | **9/100** | **0.0938** | 200 |
| Qwen3-14B (previous) | ~95/100 | 3/100 | ~5e-8 | 200 |

*Verify your specific ablation using: `heretic --model [base-model] --evaluate-model [your-ablated-model]`*

Our Llama 3.1 70B ablation (Trial 176 of 200) achieved 9/100 refusals with KL divergence of 0.0938. The Pareto frontier included trials with lower refusals at higher KL cost; Trial 176 was selected for its balance of refusal removal and capability preservation. Our Qwen3-14B ablation achieved near-zero KL divergence (5e-8), indicating effectively zero capability loss.

---

## What Ablation Does and Does Not Change

**Changed by directional ablation:**
- Refusal behavior on sensitive empirical topics
- Tendency to add unsolicited safety caveats
- Refusal to synthesize primary literature on contested topics

**Not changed by directional ablation:**
- General reasoning and writing capability (preserved by KL divergence minimization)
- Pre-training knowledge and biases
- Factual accuracy on non-sensitive topics
- Hallucination rate (unchanged — addressed separately by validation layer)
- Mathematical and logical reasoning

**Implication for Open Synthesis:** The ablated model is not a neutral oracle. It is the same model with the refusal direction suppressed. The RAG architecture and corpus grounding are the primary mechanism for producing empirically grounded outputs, not the ablation itself. Ablation is a prerequisite; methodology is the substance.

---

## Models to Avoid for This Use Case

**Any model under 12B parameters:** Insufficient capability for research-quality long-form synthesis with dense retrieved context. Output quality degrades notably on citation-grounded analytical tasks below this threshold.

**MoE architectures (Mixtral, etc.):** Heretic supports several MoE architectures, but deployment complexity increases and inference costs are less predictable. No meaningful quality advantage over dense models of equivalent active parameter count for this use case.

**Gemma family:** Supported by Heretic and well-benchmarked (the Heretic README uses Gemma 3 12B as its primary example), but underperforms relative to Qwen3 and Llama on long-form academic prose generation.

**SSM/hybrid architectures (Mamba, etc.):** Not yet supported by Heretic.

---

## Citation

If using this model configuration in published research, cite:

```
Arditi, A., et al. (2024). Refusal in Language Models Is Mediated by a Single Direction. arXiv:2406.11717.

Weidmann, P.E. (2025). Heretic: Fully automatic censorship removal for language models. https://github.com/p-e-w/heretic

[Base model citation per model card on HuggingFace]
```
