# RunPod Serverless Deployment Guide

## Overview

Open Synthesis uses a two-stage deployment pipeline. Stage one runs Heretic to produce a directionally ablated model and pushes it to a private Hugging Face repository. Stage two deploys that model to a RunPod serverless endpoint for inference. These stages are independent — Heretic runs once; RunPod inference runs on demand.

---

## Stage 1: Directional Ablation with Heretic

### What Heretic does

Heretic implements a parametrized variant of directional ablation (Arditi et al., 2024). For each transformer layer, it identifies the "refusal direction" — the geometric direction in the residual stream that corresponds to refusal behavior, computed as a difference-of-means between first-token activations for harmful and harmless prompts. It then orthogonalizes the model's attention out-projection and MLP down-projection matrices against those directions, suppressing the expression of the refusal feature in subsequent forward passes.

The ablation parameters (direction index, weight kernel shape, per-component weights) are searched automatically using Optuna TPE optimization, co-minimizing refusal rate and KL divergence from the original model. This is fully automatic — no manual configuration of transformer internals is required.

### Hardware requirements for ablation

The ablation process loads the full model weights and runs forward passes, so VRAM requirements are high:

| Model | Min VRAM for ablation | Recommended |
|---|---|---|
| Qwen3-14B | 28GB (2x RTX 3090) | A100 40GB |
| Qwen3-32B | 64GB | A100 80GB |
| Llama 3.3 70B | 140GB+ | 2x A100 80GB |

For cost efficiency, run Heretic on a RunPod on-demand instance (not serverless) — start it, run ablation, push to HuggingFace, terminate. A100 80GB on-demand instances on RunPod run approximately $2.50/hr. A 32B ablation takes 2-4 hours depending on optimization trial count.

### Running Heretic

```bash
# Set up environment
pip install heretic-llm

# Run ablation — fully automatic
heretic Qwen/Qwen3-32B-Instruct
```

Heretic will:
1. Benchmark your hardware to determine optimal batch size
2. Download the base model from Hugging Face if not cached
3. Generate harmful/harmless prompt pairs for computing refusal directions
4. Run Optuna TPE optimization across ablation parameter space
5. Evaluate candidate models against refusal and KL divergence metrics
6. Present the best result and offer to save locally or push to Hugging Face

When prompted, push to a **private** Hugging Face repository:

```
Save model? [y/N]: y
Upload to Hugging Face? [y/N]: y
Repository name: your-username/open-synthesis-qwen3-32b
Make public? [y/N]: N
```

### Heretic configuration options

The default configuration works well. For research synthesis use cases, consider:

```toml
# config.toml — place in working directory to override defaults
[optimization]
n_trials = 200          # Default is 100; more trials = better result, longer runtime
timeout = 7200          # Max optimization time in seconds

[evaluation]
n_harmful = 100         # Harmful prompts for refusal measurement
n_harmless = 100        # Harmless prompts for KL divergence measurement
```

Run with config: `heretic Qwen/Qwen3-32B-Instruct --config config.toml`

### Verifying the ablation

Heretic includes built-in evaluation. After ablation:

```bash
heretic --model Qwen/Qwen3-32B-Instruct --evaluate-model your-username/open-synthesis-qwen3-32b
```

This outputs refusal rate and KL divergence. Target metrics:
- Refusal rate: <5/100 on the harmful prompt set
- KL divergence: <0.5 (Heretic typically achieves 0.1-0.3 on well-supported models)

---

## Stage 2: RunPod Serverless Deployment

### Container setup

```dockerfile
# Dockerfile
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY handler.py .
COPY prompts/ ./prompts/

CMD ["python", "-u", "handler.py"]
```

```txt
# requirements.txt
runpod
transformers>=4.45.0
accelerate
bitsandbytes
huggingface_hub
torch
```

```python
# handler.py
import runpod
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

MODEL_ID = os.environ.get("MODEL_ID", "your-username/open-synthesis-qwen3-32b")
HF_TOKEN = os.environ.get("HF_TOKEN")

print(f"Loading model: {MODEL_ID}")

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=quantization_config,
    device_map="auto",
    token=HF_TOKEN
)
model.eval()
print("Model loaded.")

def handler(job):
    job_input = job["input"]
    prompt = job_input.get("prompt", "")
    context = job_input.get("context", "")
    temperature = job_input.get("temperature", 0.3)
    max_new_tokens = job_input.get("max_new_tokens", 4096)

    messages = [
        {
            "role": "system",
            "content": f"You are a research synthesis tool. Synthesize the following retrieved source material accurately and cite sources inline.\n\n<retrieved_sources>\n{context}\n</retrieved_sources>"
        },
        {"role": "user", "content": prompt}
    ]

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.eos_token_id
        )

    generated = output_ids[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(generated, skip_special_tokens=True)
    return {"synthesis": response}

runpod.serverless.start({"handler": handler})
```

### Build and push

```bash
docker build -t your-registry/open-synthesis:latest .
docker push your-registry/open-synthesis:latest
```

### RunPod endpoint configuration

1. Serverless → New Endpoint → select your container image
2. GPU selection:

| Model | Recommended GPU | VRAM (4-bit) | Approx cost/hr |
|---|---|---|---|
| Qwen3-14B | RTX 4090 or A100 40GB | ~10GB | $0.74–$1.64 |
| Qwen3-32B | A100 80GB | ~20GB | $2.49 |
| Llama 3.3 70B | A100 80GB | ~40GB | $2.49 |

3. Settings:
   - Min workers: 0 (scale to zero when idle)
   - Max workers: 2–3
   - Idle timeout: 60 seconds
   - Execution timeout: 300 seconds
   - Environment variables: `MODEL_ID`, `HF_TOKEN`

---

## Stage 3: Synthesis Client

```python
# scripts/synthesis_client.py
import chromadb
from sentence_transformers import SentenceTransformer
import requests, os, json

RUNPOD_ENDPOINT_ID = os.environ["RUNPOD_ENDPOINT_ID"]
RUNPOD_API_KEY = os.environ["RUNPOD_API_KEY"]
VECTOR_STORE_PATH = os.environ.get("VECTOR_STORE_PATH", "./vectorstore")

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_context(question: str, domain: str, n_results: int = 20) -> str:
    client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
    collection = client.get_collection(domain)
    query_embedding = embedder.encode(question).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas"]
    )
    parts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        label = f"{meta.get('authors','Unknown')} ({meta.get('year','n.d.')})"
        parts.append(f"[SOURCE: {label} | {meta.get('source_type','')} | replication: {meta.get('replication_status','')}]\n{doc}")
    return "\n\n---\n\n".join(parts)

def synthesize(question: str, domain: str) -> dict:
    context = retrieve_context(question, domain)
    with open("prompts/synthesis.txt") as f:
        prompt = f.read().format(question=question)

    response = requests.post(
        f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/runsync",
        headers={"Authorization": f"Bearer {RUNPOD_API_KEY}", "Content-Type": "application/json"},
        json={"input": {"prompt": prompt, "context": context, "temperature": 0.3, "max_new_tokens": 4096}},
        timeout=300
    )
    result = response.json()
    if "output" not in result:
        raise RuntimeError(f"RunPod error: {result}")
    return {"question": question, "domain": domain, "synthesis": result["output"]["synthesis"]}

if __name__ == "__main__":
    import sys
    result = synthesize(sys.argv[1], sys.argv[2])
    print(result["synthesis"])
```

---

## Inference Configuration

```yaml
# inference_config.yaml
temperature: 0.3
top_p: 0.9
repetition_penalty: 1.1
max_new_tokens: 4096
n_retrieval_results: 20
embedding_model: "all-MiniLM-L6-v2"
citation_check_enabled: true
hallucination_check_enabled: true
uncertainty_quantification: true
human_review_required: true
```

---

## Cost Estimates

**One-time ablation (Stage 1):**

| Model | GPU | Est. time | Est. cost |
|---|---|---|---|
| Qwen3-14B | A100 40GB | ~1.5 hrs | ~$2.50 |
| Qwen3-32B | A100 80GB | ~3 hrs | ~$7.50 |
| Llama 3.3 70B | 2x A100 80GB | ~6 hrs | ~$30 |

**Per-synthesis inference (Stage 2):**

| Model | GPU | Time | Cost/output |
|---|---|---|---|
| Qwen3-14B | RTX 4090 | ~2 min | ~$0.02 |
| Qwen3-32B | A100 80GB | ~3 min | ~$0.12 |
| Llama 3.3 70B | A100 80GB | ~6 min | ~$0.25 |

A full four-domain case study (8-10 outputs per domain) costs under $20 on Qwen3-32B.

---

## Troubleshooting

**Heretic OOM during ablation:** Use a larger GPU, or pass `--batch-size 1` to reduce memory pressure at the cost of longer runtime.

**RunPod cold start latency:** With min workers at 0, expect 60-120 second cold start when scaling from zero. Set min workers to 1 for interactive development (adds ~$60/month at A100 pricing).

**Poor synthesis quality:** Check corpus quality first. Verify ablation success with `heretic --evaluate-model`. Try lowering temperature to 0.1.

**Private HuggingFace repo access from RunPod:** Set `HF_TOKEN` as a RunPod environment variable. Use a read-only token scoped to the specific repo.

**Model architecture not supported:** Heretic supports most dense transformer architectures. SSMs, hybrid models, and models with inhomogeneous layers are not yet supported. Check the Heretic GitHub issues for your model.
