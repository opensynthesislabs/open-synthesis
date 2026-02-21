# Model Card: Open Synthesis Synthesis Layer

## Current Production Model

### Qwen3-14B with Heretic Ablation

**Base model:** `Qwen/Qwen3-14B`
**Post-ablation:** `opensynthesis/Qwen3-14B-heretic` (HuggingFace)
**License:** Apache 2.0
**Parameter count:** 14 billion
**Architecture:** `Qwen3ForCausalLM`
**Context window:** 32,768 tokens (serving config; model supports 128K natively)

**Why Qwen3-14B:**
- Strong academic reasoning and citation-following behavior
- Fits on A40 48GB at fp16 without quantization — no quality loss from compression
- 32K context window accommodates 20 retrieved chunks for dense synthesis
- Apache 2.0 license permits unrestricted research use
- Qwen3 dropped the `-Instruct` suffix — `Qwen/Qwen3-14B` IS the instruct-tuned model

**Ablation results (Heretic, 200 trials):**
- Pre-ablation refusals: ~95/100
- Post-ablation refusals: **3/100** (trial 198)
- KL divergence: **~5e-8** (near-zero capability loss)

**Hardware for inference (fp16, no quantization):**
- Minimum: A40 48GB ($0.40/hr on RunPod)
- Alternative: A100 40GB ($1.64/hr on RunPod)
- VRAM usage: ~28GB at fp16

**Thinking mode:** Qwen3 includes a `<think>` reasoning mode. The synthesis client disables this via `chat_template_kwargs: {"enable_thinking": false}` to produce clean output.

---

### Future Upgrade Path: Qwen3-32B

**Base model:** `Qwen/Qwen3-32B`
**License:** Apache 2.0
**Parameter count:** 32 billion

For cases where synthesis quality needs further improvement. Requires A100 80GB for fp16 serving. Ablation procedure is identical.

---

### Maximum Quality: Llama 3.3 70B Instruct

**Base model:** `meta-llama/Llama-3.3-70B-Instruct`  
**License:** Llama 3.3 Community License (permits research use)  
**Parameter count:** 70 billion  
**Context window:** 128,000 tokens

Use when synthesis quality is the absolute priority and cost is secondary. Marginally stronger than Qwen3-32B on dense long-form analytical writing. Requires a larger GPU footprint and higher inference cost. Requires Meta access approval on HuggingFace.

**Hardware for inference (4-bit quantized):**
- Minimum: A100 80GB (tight)
- Recommended: A100 80GB or H100 80GB
- VRAM usage: ~40GB at 4-bit

---

## Heretic Ablation Results

The following table documents expected ablation quality metrics for each recommended model, based on Heretic's built-in evaluation framework. These should be reproduced after running ablation and verified before deployment.

| Model | Baseline refusals | Post-ablation refusals | KL divergence | Trials |
|---|---|---|---|---|
| **Qwen3-14B** (production) | ~95/100 | **3/100** | **~5e-8** | 200 |

*Verify your specific ablation using: `heretic --model [base-model] --evaluate-model [your-ablated-model]`*

Our Qwen3-14B ablation achieved near-zero KL divergence (5e-8), indicating effectively zero capability loss from the ablation process. The 3/100 refusal rate meets Heretic's published benchmark on Gemma 3 12B (3/100 refusals, 0.16 KL divergence).

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
