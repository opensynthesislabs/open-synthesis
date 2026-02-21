"""RunPod serverless handler — self-contained, zero imports from the package.

This file runs inside the RunPod container and only needs:
transformers, torch, bitsandbytes, accelerate, runpod.
"""

import os

import runpod
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_ID = os.environ.get("MODEL_ID", "your-username/open-synthesis-qwen3-32b")
HF_TOKEN = os.environ.get("HF_TOKEN")

print(f"Loading model: {MODEL_ID}")

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=quantization_config,
    device_map="auto",
    token=HF_TOKEN,
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
            "content": (
                "You are a research synthesis tool. Synthesize the following "
                "retrieved source material accurately and cite sources inline.\n\n"
                f"<retrieved_sources>\n{context}\n</retrieved_sources>"
            ),
        },
        {"role": "user", "content": prompt},
    ]

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer([text], return_tensors="pt").to(model.device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = output_ids[0][inputs["input_ids"].shape[1] :]
    response = tokenizer.decode(generated, skip_special_tokens=True)
    return {"synthesis": response}


runpod.serverless.start({"handler": handler})
