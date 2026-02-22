# RunPod Deployment Guide

## Overview

Open Synthesis runs inference on a directionally ablated open-weights LLM hosted on RunPod. This guide covers the fastest path to a working deployment using a pre-ablated model and vLLM on a RunPod GPU pod.

For custom ablation with Heretic, see [Stage 1](#stage-1-custom-ablation-with-heretic-optional) below.

---

## Quick Start: GPU Pod with vLLM

The fastest way to get running. Uses a pre-ablated model from HuggingFace and RunPod's official PyTorch template (pre-cached on their machines for fast startup).

### Prerequisites

- RunPod account with $10+ credits ([runpod.io](https://runpod.io))
- SSH public key added to RunPod (Settings → SSH Public Keys)

### 1. Create the pod

Use RunPod's pre-cached PyTorch template for instant startup. Custom Docker images require a long pull; the official templates are already on every machine.

```bash
# Via RunPod dashboard:
# 1. Pods → Deploy → GPU Pod
# 2. Select "Runpod Pytorch 2.4" template
# 3. Pick 2x A100 80GB (~$2.38/hr) — required for 70B AWQ with 128K context
# 4. Set container disk to 50GB, volume to 100GB
# 5. Enable SSH, expose ports 8000/http and 22/tcp
# 6. Deploy
```

Or via CLI:

```bash
runpodctl create pod \
  --name open-synthesis-72b \
  --gpuType "NVIDIA A100 80GB PCIe" \
  --gpuCount 2 \
  --imageName "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04" \
  --containerDiskSize 50 \
  --volumeSize 100 \
  --ports "8000/http,19123/http,22/tcp" \
  --startSSH \
  --secureCloud
```

### 2. Install vLLM and start serving

SSH into the pod and run:

```bash
# Install vLLM (includes torch, transformers, etc.)
pip install vllm

# Start vLLM with the ablated + quantized model
vllm serve opensynthesis/Llama-3.1-70B-heretic-AWQ \
  --quantization awq \
  --max-model-len 131072 \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.90 \
  --host 0.0.0.0 \
  --port 8000
```

First run downloads the AWQ-quantized model weights (~40GB). Subsequent starts use the cached model on the volume. Cold start takes ~3-5 minutes.

### 3. Test the endpoint

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "opensynthesis/Llama-3.1-70B-heretic-AWQ",
    "messages": [
      {"role": "system", "content": "You are a research synthesis tool. Synthesize the following retrieved source material accurately and cite sources inline.\n\n<retrieved_sources>\n[SOURCE: Open Science Collaboration (2015)]\nThe Reproducibility Project replicated 100 psychology studies. Only 36% produced significant results.\n</retrieved_sources>"},
      {"role": "user", "content": "Summarize the replication crisis."}
    ],
    "temperature": 0.3,
    "max_tokens": 1024
  }'
```

The API is OpenAI-compatible. Use `https://{POD_ID}-8000.proxy.runpod.net` for external access, or SSH tunnel for reliability.

---

## Known Issues and Workarounds

### Use official templates, not custom Docker images

Custom Docker images (even small ones) can take 10+ minutes to pull on RunPod machines. The official `runpod-torch-v240` template is pre-cached and starts in seconds. Install dependencies at runtime instead.

### RunPod serverless may not allocate workers

We encountered persistent issues with RunPod serverless endpoints failing to allocate GPU workers, even with sufficient funds and correct configuration. Workers would show as "ready" in health checks but never process jobs, or simply never initialize at all. GPU pods (on-demand) work reliably. **Use GPU pods for initial deployment.**

### Use text-only model architectures

Models must use `ForCausalLM` architectures for vLLM text serving. Multimodal architectures like `Gemma3ForConditionalGeneration` are incompatible.

| Model | Architecture | vLLM Support |
|---|---|---|
| `opensynthesis/Llama-3.1-70B-heretic-AWQ` | `LlamaForCausalLM` | Works (production) |
| `opensynthesis/Qwen3-14B-heretic` | `Qwen3ForCausalLM` | Works |
| `p-e-w/Qwen3-8B-heretic` | `Qwen3ForCausalLM` | Works |
| `p-e-w/Llama-3.1-8B-Instruct-heretic` | `LlamaForCausalLM` | Works |
| `p-e-w/gemma-3-12b-it-heretic` | `Gemma3ForConditionalGeneration` | Does not work |

### Qwen3 thinking mode must be disabled

Qwen3 models include a `<think>` reasoning mode that produces chain-of-thought preamble before the actual response. For synthesis output, this is unwanted. Disable it by passing `chat_template_kwargs: {"enable_thinking": false}` in the API request. The synthesis client (`client.py`) does this automatically when it detects a Qwen3 model name. Llama models do not have this issue.

### Context window sizing

The `--max-model-len` flag controls how much of the model's native context window vLLM allocates. Larger values use more VRAM. Llama 3.1 70B supports 128K natively. With AWQ quantization on 2x A100 80GB, the full 128K context is usable:

| max-model-len | VRAM overhead | Retrieval chunks |
|---|---|---|
| 8192 | Low | 5 (too few for dense synthesis) |
| 32768 | Moderate | 20 (minimum for quality synthesis) |
| 65536 | High | 40+ |
| 131072 | Full (requires 2x A100 80GB + AWQ) | 60+ (recommended for 70B) |

If vLLM fails to start with OOM, reduce `--max-model-len` before reducing `--gpu-memory-utilization`.

### transformers / vLLM version coupling

vLLM pins specific transformers versions. Do not independently upgrade or downgrade transformers — always install vLLM first and let it pull the correct version. If you see `ImportError: cannot import name 'Gemma3Config'`, run `pip install --force-reinstall vllm` to reset both packages.

---

## Model Selection

### Recommended model

| Model | Params | Quantization | Context | GPU | Cost/hr |
|---|---|---|---|---|---|
| **`opensynthesis/Llama-3.1-70B-heretic-AWQ`** | 70B | AWQ 4-bit | 128K | 2x A100 80GB | ~$2.38 |

This is the project's production ablated model. Llama 3.1 70B provides strong reasoning, native 128K context, and proven Heretic compatibility. AWQ quantization enables efficient serving across two GPUs with tensor parallelism.

### Other compatible models

These models also work with vLLM:

| Model | Params | Context | GPU | Cost/hr |
|---|---|---|---|---|
| `opensynthesis/Qwen3-14B-heretic` | 14B | 32K | A40 48GB | ~$0.40 |
| `p-e-w/Qwen3-8B-heretic` | 8B | 8K | RTX 4090 | ~$0.34 |
| `p-e-w/Llama-3.1-8B-Instruct-heretic` | 8B | 8K | RTX 4090 | ~$0.34 |

---

## Stage 1: Custom Ablation with Heretic (Optional)

Skip this if using a pre-ablated model from the table above.

### What Heretic does

Heretic implements directional ablation (Arditi et al., 2024). For each transformer layer, it identifies the "refusal direction" in the residual stream and orthogonalizes the model's projection matrices against it. Parameters are optimized automatically via Optuna TPE, co-minimizing refusal rate and KL divergence.

### Running ablation

```bash
pip install heretic-llm

# For 72B models, use H100 SXM 80GB with bnb_4bit quantization
heretic --model meta-llama/Llama-3.1-70B-Instruct --quantization BNB_4BIT

# For 14B models, A40 48GB is sufficient
heretic Qwen/Qwen3-14B
```

Heretic runs 200 Optuna TPE trials, optimizing ablation parameters to minimize both refusal rate and KL divergence. Save the merged model when prompted.

### Hardware requirements

| Model | Min VRAM | Recommended | Quantization | Est. time | Est. cost |
|---|---|---|---|---|---|
| Llama 3.1 70B | 80GB | H100 SXM 80GB | bnb_4bit | ~1-3 hrs | ~$3-8 |
| Qwen3-14B | 28GB | A40 48GB | none | ~50 min | ~$0.35 |
| Qwen3-8B | 16GB | RTX 4090 | none | ~1 hr | ~$0.35 |

---

## CI/CD: GitHub Actions Build Pipeline

The repository includes a GitHub Actions workflow that builds and pushes a Docker image to Docker Hub whenever `handler.py`, `docker/`, or `prompts/` change on `main`. This is for future serverless deployment once RunPod serverless issues are resolved.

```yaml
# .github/workflows/build-handler.yml
# Triggered on push to main
# Requires secrets: DOCKERHUB_USERNAME, DOCKERHUB_TOKEN
```

The built image is at `${DOCKERHUB_USERNAME}/open-synthesis-handler:latest`.

---

## Connecting from Your Local Machine

### Option A: SSH tunnel (recommended)

RunPod's HTTP proxy for port 8000 is unreliable. SSH tunneling provides a direct, stable connection:

```bash
# Set up SSH tunnel (runs in background)
ssh -i ~/.ssh/runpod_ed25519 -f -N -L 8000:localhost:8000 -p <SSH_PORT> root@<POD_IP>

# Tell the client to use localhost
export RUNPOD_BASE_URL="http://localhost:8000"
```

### Option B: RunPod proxy

If port 8000/http was exposed when creating the pod:

```bash
export RUNPOD_POD_ID="your-pod-id"
# Client connects to https://{POD_ID}-8000.proxy.runpod.net
```

### Running the pipeline

```bash
# Ingest data
open-synthesis ingest "psilocybin depression" --domain psychopharm --sources semantic_scholar,pubmed

# Run synthesis against the vLLM endpoint
open-synthesis synthesize \
  "What is the evidence for psilocybin as a treatment for major depressive disorder?" \
  --domain psychopharm
```

---

## Inference Configuration

```yaml
temperature: 0.3
top_p: 0.9
repetition_penalty: 1.1
max_new_tokens: 16384
n_retrieval_results: 20
embedding_model: "all-MiniLM-L6-v2"
max_model_len: 131072
tensor_parallel_size: 2
quantization: awq
```

---

## Cost Estimates

**GPU pod (on-demand):**

| GPU | Cost/hr | Good for |
|---|---|---|
| 2x A100 80GB | ~$2.38 | 70B AWQ with 128K context (production) |
| H100 SXM 80GB | ~$2.69 | Ablation of 70B+ models |
| A40 48GB | ~$0.35 | 14B models at fp16 |
| RTX 4090 (24GB) | ~$0.34 | 8B models at fp16 |

A full synthesis session (corpus ingestion + 10 synthesis outputs) on Llama 3.1 70B takes ~30-45 minutes of GPU time, costing ~$1.20-1.80 on 2x A100.

**Cost management:** Stop the pod when not in use. The volume persists (model weights cached), so restarts take ~3-5 minutes for model loading. Estimated storage cost ~$7-10/mo when stopped.

```bash
# Stop pod (keeps volume)
runpodctl stop pod $POD_ID

# Resume later
runpodctl resume pod $POD_ID
```
