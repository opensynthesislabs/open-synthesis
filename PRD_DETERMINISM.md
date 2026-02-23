# PRD: Deterministic Reproducibility for Open Synthesis

## Problem

Open Synthesis produces citation-grounded research syntheses, but the same question asked twice can produce meaningfully different outputs. This undermines the core value proposition: if the tool claims to synthesize "what the literature shows," users need to trust that the answer is stable, auditable, and reproducible. Currently, non-determinism enters at every layer of the pipeline.

## Sources of Non-Determinism

### 1. Retrieval Layer
- **Dense search** returns results based on cosine similarity with floating-point embeddings. Tie-breaking between similarly-scored chunks is arbitrary.
- **BM25 scoring** depends on the current corpus state. Adding new documents changes term frequencies and reranks existing results.
- **Reciprocal rank fusion** inherits instability from both retrieval methods.
- **No retrieval versioning.** There is no record of which chunks were retrieved for a given query, so results cannot be audited or reproduced after the corpus changes.

### 2. Inference Layer
- **Temperature 0.3** introduces sampling randomness. Even temperature 0.0 is not fully deterministic on GPU due to floating-point non-associativity in parallel reductions.
- **No seed parameter** is passed to vLLM. The `seed` field in the OpenAI-compatible API enables deterministic sampling when set.
- **top_p 0.9** further increases output variance by nucleus sampling.
- **Token-level streaming** means the same logical output can be chunked differently across runs, though this is cosmetic.

### 3. Validation Layer
- **Validation uses the same LLM** with temperature 0.1, so citation checks, hallucination detection, and uncertainty scoring can vary between runs.
- **No structured output enforcement.** Validation prompts ask for JSON but don't enforce schema, so parsing failures are non-deterministic.

### 4. Corpus Layer
- **No corpus snapshots.** The ChromaDB vectorstore is mutable. If documents are added or removed between runs, identical queries produce different results.
- **No deduplication stability guarantee.** DOI-based dedup works, but documents without DOIs may create duplicates across ingestion runs.

## Requirements

### P0: Reproducible Runs (Seed + Log)

**R1. Deterministic inference seed.**
Pass a `seed` parameter to vLLM for all inference calls (synthesis, validation). When the user does not specify a seed, generate one from the query hash and log it. When a seed is provided (e.g., `--seed 42`), use it exactly.

- Affected files: `client.py` (add `seed` to request body), `config.py` (add seed to InferenceSettings), `cli.py` (add `--seed` flag)
- vLLM docs: the `seed` field in `/v1/chat/completions` enables deterministic sampling

**R2. Temperature 0.0 mode.**
Add a `--deterministic` flag to the CLI that sets `temperature=0.0, top_p=1.0, seed=hash(query)`. This is the "same question, same answer" mode. Document that GPU floating-point means near-deterministic, not bit-identical.

- Affected files: `cli.py`, `config.py`, `client.py`

**R3. Retrieval manifest.**
Every synthesis run must produce a retrieval manifest: an ordered list of chunk IDs, scores, and retrieval method, saved alongside the output. This enables auditing which sources informed a synthesis even after the corpus changes.

- Affected files: `pipeline.py`, `server.py`, `types.py` (add manifest to SynthesisResult)
- Format: JSON sidecar file or embedded in SynthesisResult

**R4. Run metadata envelope.**
Every output (CLI and API) must include a metadata block:
```json
{
  "run_id": "uuid",
  "seed": 42,
  "temperature": 0.0,
  "model": "opensynthesis/Llama-3.1-70B-heretic-AWQ",
  "corpus_hash": "sha256:...",
  "retrieval_manifest": [...],
  "timestamp": "2026-02-23T00:00:00Z",
  "pipeline_version": "0.2.0"
}
```
This is the minimum information needed to explain why a specific output was produced.

- Affected files: `types.py`, `pipeline.py`, `server.py`, `cli.py`

### P1: Corpus Integrity

**R5. Corpus snapshot hashing.**
Compute a deterministic hash of the vectorstore state (sorted chunk IDs + content hashes) at query time. Store this in run metadata. Two runs with the same corpus hash and same seed must produce identical retrieval results.

- Affected files: `store.py` (add `corpus_hash()` method), `pipeline.py`

**R6. Immutable corpus mode.**
Add an `--immutable-corpus` flag that prevents ingestion while the server is running. This guarantees the corpus doesn't change between retrieval and synthesis within a session.

- Affected files: `server.py`, `cli.py`

**R7. Ingestion receipts.**
Each ingestion run produces a receipt: timestamp, source APIs queried, documents added (with DOIs/IDs), documents deduplicated, chunks created. Receipts are append-only and stored alongside the vectorstore.

- Affected files: `manager.py`, new file `corpus/receipts.py`

### P2: Structured Validation

**R8. Schema-enforced validation output.**
Use vLLM's structured output mode (JSON schema constraint) for validation passes. This eliminates parse failures and makes validation deterministic given the same input.

- Affected files: `client.py` (add `response_format` parameter), `pipeline.py`, validation prompt templates
- vLLM supports `response_format: {"type": "json_schema", "json_schema": {...}}`

**R9. Validation result persistence.**
Citation check, hallucination flags, and confidence level must be stored with the synthesis output, not just logged. The `SynthesisResult` already has these fields — ensure they are always populated and serialized.

- Affected files: `pipeline.py`, `cli.py` (output formatting)

### P3: Reproducibility Verification

**R10. Replay mode.**
`open-synthesis replay <run_id>` re-executes a synthesis using the saved seed, retrieval manifest, and temperature from a previous run. If the corpus hasn't changed (same corpus hash), the output should be identical. If it has changed, replay uses the manifest to reconstruct the original context from stored chunks rather than re-querying.

- New file: `synthesis/replay.py`
- Affected files: `cli.py`, `types.py`

**R11. Diff mode.**
`open-synthesis diff <run_id_a> <run_id_b>` compares two synthesis outputs, highlighting changes in text, retrieved sources, and validation results. This is the primary tool for understanding why outputs changed.

- New file: `synthesis/diff.py`
- Affected files: `cli.py`

## Non-Requirements

- **Bit-identical GPU inference.** GPU floating-point parallelism makes true bit-identical output impossible without sacrificing performance. Near-determinism (same seed = same output 99%+ of the time) is sufficient.
- **Corpus version control.** Full git-style versioning of the vectorstore is out of scope. Snapshot hashing + ingestion receipts provide sufficient auditability.
- **Multi-model consistency.** Different models (e.g., Qwen3-14B vs Llama-70B) are not expected to produce the same output for the same query.

## Implementation Order

1. **R1 + R2**: Seed parameter + deterministic mode (smallest change, biggest impact)
2. **R3 + R4**: Retrieval manifest + run metadata (auditability foundation)
3. **R5 + R7**: Corpus hashing + ingestion receipts (corpus integrity)
4. **R8 + R9**: Structured validation (reliability)
5. **R10 + R11**: Replay + diff (verification tooling)
6. **R6**: Immutable corpus mode (operational safety)

## Success Criteria

- Same query + same seed + same corpus = identical output in 10/10 runs
- Every synthesis output includes enough metadata to explain its provenance
- `replay` reproduces any previous run given an unchanged corpus
- Validation passes never fail due to parse errors (structured output enforcement)
- Ingestion history is fully auditable via receipts
