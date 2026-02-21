# Open Synthesis

**RAG pipeline for synthesizing peer-reviewed scientific literature using open-source LLMs with directional ablation, deployed on private infrastructure.**

[opensynthesis.dev](https://opensynthesis.dev)

---

## What This Does

Open Synthesis ingests peer-reviewed papers and government data from 11 public APIs, stores them in a vector database, and synthesizes answers to research questions using an open-weights LLM that has been processed with [Heretic](https://github.com/0bserver07/heretic-llm) to remove refusal behavior. Every output is citation-grounded, validated for hallucinations, and tagged with a confidence level.

```
[CORPUS] → [RETRIEVAL] → [SYNTHESIS] → [VALIDATION]
 11 APIs    hybrid BM25    RunPod        citation check
 ChromaDB   + dense        serverless    hallucination detect
 embeddings reranking      ablated LLM   uncertainty scoring
```

## Quickstart

```bash
# Install with uv
uv sync

# List available data sources
open-synthesis sources

# Ingest papers on a topic
open-synthesis ingest "psilocybin depression" --domain psychopharm --sources semantic_scholar,pubmed

# Run a synthesis (requires RunPod endpoint)
export RUNPOD_ENDPOINT_ID="your-endpoint-id"
export RUNPOD_API_KEY="your-api-key"
open-synthesis synthesize "What is the evidence for psilocybin as a treatment for major depressive disorder?" --domain psychopharm
```

## Architecture

### Four Layers

1. **Corpus** — Ingest from 11 public APIs (Semantic Scholar, PubMed, arXiv, CrossRef, CORE, OpenAlex, Census, FRED, ClinicalTrials.gov, OECD, data.gov). Documents are chunked at paragraph level and embedded with `all-MiniLM-L6-v2` into ChromaDB.

2. **Retrieval** — Hybrid search combining dense vector similarity and BM25 keyword matching via reciprocal rank fusion. Cross-encoder reranking placeholder for production use.

3. **Synthesis** — Research questions are sent with retrieved context to an ablated open-weights LLM running on RunPod serverless. The model produces inline-cited synthesis with falsifiability criteria.

4. **Validation** — Three-pass validation: citation verification (are claims supported by cited sources?), hallucination detection (fabricated stats, names, or overstatements?), and uncertainty quantification (well-supported / limited / contested / insufficient).

### Two-Stage Deployment

**Stage 1 — Ablation (one-time):** Run [Heretic](https://github.com/0bserver07/heretic-llm) on an open-weights model to remove refusal behavior. Push to private HuggingFace repo.

**Stage 2 — Inference (on-demand):** Deploy ablated model to RunPod serverless with scale-to-zero. 4-bit NF4 quantization for cost efficiency.

See [runpod_deployment.md](runpod_deployment.md) for detailed deployment instructions.

## Configuration

Copy `config/default.toml` and customize:

```toml
vector_store_path = "./vectorstore"

[inference]
temperature = 0.3
max_new_tokens = 4096

[retrieval]
n_results = 20
dense_weight = 0.6
sparse_weight = 0.4
```

Or use environment variables with `RUNPOD_` prefix for RunPod settings, `OSYN_` prefix for general settings.

## Data Sources

See [DATA_SOURCES.md](DATA_SOURCES.md) for complete API documentation, auth requirements, and rate limits.

Sources requiring API keys: **CORE**, **Census**, **FRED**. All others work without authentication.

## Project Structure

```
src/open_synthesis/
├── cli.py              # Typer CLI (ingest, synthesize, validate, sources)
├── config.py           # Pydantic settings + TOML loader
├── types.py            # Domain models (Document, Chunk, SynthesisResult)
├── corpus/             # Ingestion layer
│   ├── base.py         # DataSource ABC
│   ├── manager.py      # Orchestrator (search → dedupe → chunk → embed → store)
│   ├── chunker.py      # Paragraph-level text splitting
│   ├── store.py        # ChromaDB wrapper
│   └── sources/        # 11 API integrations
├── retrieval/          # Hybrid retrieval
│   ├── dense.py        # Sentence-transformer vector search
│   ├── sparse.py       # BM25 keyword search
│   ├── hybrid.py       # Reciprocal rank fusion
│   └── reranker.py     # Cross-encoder placeholder
├── synthesis/          # LLM inference
│   ├── client.py       # RunPod API client
│   ├── prompts.py      # Template loader
│   └── pipeline.py     # End-to-end orchestration
├── validation/         # Output verification
│   ├── citation.py     # Citation check parsing
│   ├── hallucination.py # Hallucination flag parsing
│   └── uncertainty.py  # Confidence level assessment
└── handler.py          # RunPod serverless handler (self-contained)
```

## Development

```bash
uv sync --extra dev
pytest
```

## Documentation

- [WHITEPAPER.md](WHITEPAPER.md) — Full technical paper (Parts I–VII)
- [model_card.md](model_card.md) — Model selection guide and ablation metrics
- [runpod_deployment.md](runpod_deployment.md) — Deployment pipeline with reference code
- [DATA_SOURCES.md](DATA_SOURCES.md) — API documentation for all 11 data sources
- [REFERENCES.md](REFERENCES.md) — Bibliography

## License

MIT
