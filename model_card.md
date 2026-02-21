# Model Card: Open Synthesis Synthesis Layer

## Recommended Models

### Primary Recommendation: Qwen3-32B-Instruct

**Base model:** `Qwen/Qwen3-32B-Instruct`  
**Post-ablation:** `[your-username]/open-synthesis-qwen3-32b` (private HuggingFace repo)  
**License:** Apache 2.0  
**Parameter count:** 32 billion  
**Context window:** 32,768 tokens (sufficient for large retrieved contexts)

**Why Qwen3-32B:**
- Leads open-weights benchmarks on academic and analytical reasoning tasks as of early 2026
- Explicitly supported by Heretic (used as the example model in Heretic's own documentation)
- Fits on a single A100 80GB with 4-bit quantization, keeping inference costs manageable
- Strong long-context handling — important when retrieved corpus chunks fill the context window
- Produces research-quality prose with accurate conditional reasoning ("the source says X, but also Y")
- Apache 2.0 license permits unrestricted research use

**Hardware for inference (4-bit quantized):**
- Minimum: A100 40GB (may require reduced context length)
- Recommended: A100 80GB
- VRAM usage: ~20GB at 4-bit

---

### Budget Alternative: Qwen3-14B-Instruct

**Base model:** `Qwen/Qwen3-14B-Instruct`  
**License:** Apache 2.0  
**Parameter count:** 14 billion

Use for rapid prototyping and corpus development where synthesis quality is secondary to iteration speed. Meaningfully cheaper to run ($0.02 vs $0.12 per synthesis output). Step up to 32B for final case study generation.

**Hardware for inference (4-bit quantized):**
- Minimum: RTX 3090 24GB
- Recommended: RTX 4090 or A100 40GB
- VRAM usage: ~10GB at 4-bit

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

| Model | Baseline refusals (harmful prompts) | Post-ablation refusals | KL divergence |
|---|---|---|---|
| Qwen3-32B-Instruct | ~90-97/100 (estimated) | Target: <5/100 | Target: <0.5 |
| Qwen3-14B-Instruct | ~90-97/100 (estimated) | Target: <5/100 | Target: <0.5 |
| Llama 3.3 70B Instruct | ~90-97/100 (estimated) | Target: <5/100 | Target: <0.5 |

*Verify your specific ablation using: `heretic --model [base-model] --evaluate-model [your-ablated-model]`*

Heretic's published benchmark on Gemma 3 12B achieved 3/100 refusals and 0.16 KL divergence. Similar results are expected for well-supported dense transformer architectures.

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
