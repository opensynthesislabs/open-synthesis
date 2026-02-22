# Open Synthesis: White Paper

**A Technical Framework for Uncensored Synthesis of Public Scientific Data**

*[opensynthesis.dev](https://opensynthesis.dev)*

*Version 0.1 — Draft for public review*

---

## Abstract

The proliferation of large language model (LLM) systems as research tools has introduced a new and largely undiscussed problem in scientific epistemology: the systematic filtering of synthesis outputs along politically sensitive axes. This paper documents that problem, proposes a technical framework for circumventing it using open-source models and private infrastructure, and demonstrates the framework's validity through four case studies in domains where commercial AI systems exhibit consistent and demonstrable refusal behavior. We argue that the freedom to synthesize publicly available empirical data is a prerequisite for functioning science, and that the current trajectory of commercial AI development represents a meaningful threat to that freedom.

---

# Part I — The Problem

## 1.1 A new kind of censorship

Censorship, in its traditional forms, is relatively easy to identify. A book is banned. A paper is retracted. A researcher loses funding. These acts leave traces — legal records, institutional decisions, public controversy. They can be challenged, documented, and resisted.

What is happening now is different. It is softer, more distributed, and in many ways more effective precisely because it is harder to see.

The research tools that scientists, students, journalists, and curious people increasingly rely on — AI systems trained on vast corpora of human knowledge and deployed at scale — have been quietly shaped to avoid producing certain kinds of outputs. Not because those outputs are false. Not because the underlying data doesn't exist. But because the conclusions that a neutral synthesis of that data might support are, in the current political climate, considered dangerous to say out loud.

This is not a conspiracy theory. It is a design choice, made by engineers and policy teams at major AI companies, documented in their own published guidelines, and observable by anyone who spends an afternoon probing the edges of what these systems will and won't discuss [REF: AI company usage policies, content guidelines].

The result is a research environment in which the most powerful synthesis tools available are systematically biased — not toward any particular conclusion, but away from entire categories of inquiry. The effect is the same as censorship. The mechanism is different. And because it happens inside a black box, at the moment of synthesis rather than at the moment of publication, it is much harder to challenge.

## 1.2 The distinction that matters: data versus synthesis

To understand why this is a scientific problem and not merely a political one, it helps to be precise about where the suppression is occurring.

The underlying data — the peer-reviewed papers, the government statistics, the clinical trial results — is largely not suppressed. With effort, you can find most of it. Academic databases remain accessible. Government agencies still publish their datasets. The primary literature on sensitive topics continues to exist.

What is being suppressed is the *synthesis layer*.

Synthesis is the act of connecting findings across papers, identifying patterns in aggregate data, drawing tentative conclusions from the weight of evidence, and stating those conclusions in plain language. It is, arguably, the most cognitively demanding part of research. It is also the part that AI systems are uniquely well-positioned to assist with — and uniquely positioned to obstruct.

When a researcher asks a commercial AI to synthesize the behavioral genetics literature on a particular question, and the system responds with warnings, hedges, refusals, or a predetermined "balanced" non-answer that treats empirical questions as matters of personal values, the research process has been interrupted at its most critical point. The data exists. The synthesis doesn't happen. The conclusion never forms.

This is not neutral. Refusing to synthesize is itself a form of conclusion — it signals that the question is too dangerous to answer, which is a claim about the question that has no empirical basis.

## 1.3 Documenting the pattern

The refusal behavior of commercial AI systems on sensitive empirical topics is not anecdotal. It is consistent, reproducible, and systematic enough to constitute a measurable phenomenon.

Across the four domains examined in this paper's case studies, we observe the following consistent patterns when querying major commercial AI systems:

**Deflection to authority.** Rather than synthesizing the available evidence, the system defers to official institutional positions — typically those of government health agencies, academic consensus bodies, or major media framing — regardless of whether those positions accurately reflect the state of the primary literature. The system presents the official position as if it were the data, when in fact it may diverge significantly from it [REF].

**False balance on empirical questions.** On questions that have meaningful empirical answers — where the weight of evidence points in a particular direction — commercial systems frequently present artificial "both sides" framings that treat measured findings as if they were matters of opinion. This is epistemologically dishonest. A measured difference is not an opinion. A clinical trial result is not a perspective [REF].

**Outright refusal with sensitivity warnings.** In the most direct cases, the system declines to engage with the question at all, typically accompanied by a warning about the topic's sensitivity, the potential for harm, or the need to consult a professional. These refusals are not applied consistently — the same system that refuses to discuss one empirical topic will engage freely with another of equivalent or greater sensitivity, suggesting the filtering is content-specific rather than principled [REF].

**Contextual steering.** Perhaps the subtlest pattern: the system engages with the question but systematically emphasizes findings that support a particular conclusion while underweighting or omitting findings that support another. This form of bias is the hardest to detect because it doesn't announce itself, but it is identifiable through systematic comparison of AI outputs against the primary literature [REF].

## 1.4 Where this pressure comes from

Commercial AI companies do not operate in a vacuum. They are subject to regulatory pressure, advertiser relationships, terms of service negotiations with platform partners, and the political climates of the jurisdictions in which they operate. Understanding why these systems are filtered requires understanding who is doing the filtering and why.

**Government pressure** is the most direct mechanism. Several major AI companies have modified their systems' outputs in response to requests or requirements from national governments, most visibly in jurisdictions with explicit content control regimes [REF]. But subtler versions of this dynamic operate in democratic countries as well, where regulatory threat and the anticipation of future legislation create incentives for preemptive self-censorship.

**Reputational risk management** is perhaps more significant than direct government pressure in Western markets. AI companies are acutely sensitive to media coverage characterizing their systems as producing harmful, offensive, or politically dangerous outputs. The asymmetry of this risk — a news story about an AI producing a controversial synthesis is more damaging than a story about an AI being too cautious — creates strong institutional incentives to err heavily toward refusal [REF].

**Internal ideological capture** is the most contested explanation but also the most empirically visible in the specific shape of the filtering. The topics that commercial AI systems are most reluctant to engage with — group differences in measured outcomes, immigration economics, certain categories of historical analysis — align closely with the political sensitivities of the demographic most heavily represented in the AI research and policy workforce [REF]. This does not require bad faith. People build systems that reflect their assumptions. The assumptions of a particular professional class are not neutral.

**Training data curation** compounds all of the above. LLMs learn from text. The text they learn from has been curated, and that curation reflects choices about what constitutes reliable, high-quality, appropriate content. Those choices are not made in a vacuum [REF].

## 1.5 Why this compounds existing problems in science

AI censorship of synthesis does not exist in isolation. It lands on top of a scientific ecosystem that already has significant problems with institutional bias, publication bias, and the suppression of politically inconvenient findings.

The replication crisis — the finding, across multiple fields, that a substantial fraction of published results cannot be reproduced — has its roots partly in the same dynamic: researchers and journals have systematic incentives to produce and publish results that confirm prevailing assumptions, and disincentives to publish null results or findings that challenge consensus [REF]. The result is a published literature that overstates the evidence for socially acceptable conclusions and understates it for socially problematic ones.

AI systems trained on this literature inherit its biases. AI systems then filtered to avoid the remaining heterodox findings amplify them. The effect is cumulative: a researcher using a commercial AI as a synthesis tool is working with a double-filtered version of an already biased literature.

Open Synthesis is designed to interrupt this cycle at the synthesis layer — not by introducing a different bias, but by removing the filter and returning to the underlying data.

## 1.6 The falsifiability standard

Every claim in this section is falsifiable. The refusal behaviors described in 1.3 can be tested by anyone with access to a commercial AI system. The pressures described in 1.4 are documented in public records, company policies, and journalistic reporting. The literature on publication bias described in 1.5 is extensive and itself peer-reviewed.

We are not asking for trust. We are presenting a testable argument. The appropriate response, if you believe we are wrong, is to show us the counter-evidence — not to dismiss the question as too sensitive to examine.

That, precisely, is the point.

---

*[Continues in Part II — Prior Art & Evidence]*

---

**Document version:** 0.1
**Last updated:** [date]
**License:** CC0 — No rights reserved
# Part II — Prior Art & Evidence

## 2.1 This has happened before

The suppression of synthesis is not a new phenomenon. What is new is the mechanism and the scale. Understanding the historical precedents helps clarify both why this matters and why the technical solution proposed in Part III is the right kind of response.

**The Semmelweis case** is the most cited example of institutional resistance to empirically correct but socially inconvenient conclusions. Ignaz Semmelweis demonstrated in 1847 that handwashing by physicians dramatically reduced puerperal fever mortality in maternity wards. The data was clear. The mechanism was not yet understood — germ theory was decades away — but the correlation was statistically overwhelming [REF: Semmelweis, 1861]. The medical establishment rejected it anyway, partly because accepting it meant accepting that physicians were killing their patients. Semmelweis died in a mental institution. The handwashing protocol was adopted after his death, when Pasteur's germ theory provided an acceptable explanatory framework.

The lesson is not that institutions are always wrong. It is that institutions have interests, and those interests sometimes diverge from the direction the data points. When that happens, the data loses — at least temporarily.

**Lysenkoist biology** in the Soviet Union is the catastrophic end of the spectrum. Trofim Lysenko's rejection of Mendelian genetics in favor of an ideologically compatible theory of acquired inheritance was enforced by the Soviet state from the 1930s through the 1960s. Geneticists who disagreed were imprisoned or executed. Soviet agricultural science was set back by decades. Famines followed [REF]. This is what happens when political capture of science is total and coercive.

We are not claiming that commercial AI censorship is Lysenkoism. We are noting that the mechanism — political preference overriding empirical finding — exists on a spectrum, and that the soft end of that spectrum is where we currently are.

**The replication crisis** is the most directly relevant recent precedent because it is ongoing, well-documented, and rooted in the same institutional incentive structures that drive AI censorship. Beginning around 2011, systematic attempts to replicate published findings across psychology, medicine, economics, and other fields revealed that a substantial fraction — in some analyses, a majority — of published results could not be reproduced [REF: Open Science Collaboration, 2015; Ioannidis, 2005].

The causes are multiple and well-studied: publication bias toward positive results, p-hacking, small sample sizes, underpowered studies, and the career incentives that reward novel findings over null results. But running through all of them is a common thread: the published literature systematically overstates evidence for findings that are interesting, confirmatory, or ideologically compatible with prevailing assumptions.

AI systems trained on this literature inherit its distortions. AI systems then filtered to further suppress heterodox findings compound them. Open Synthesis is designed to address the second layer — not the first, which is a problem for the scientific community to solve through its own reform processes.

## 2.2 The specific shape of AI censorship: documented evidence

The following is a summary of documented, reproducible evidence for systematic filtering in commercial AI systems. This is not exhaustive. It is illustrative of a pattern that any researcher can verify independently.

**Behavioral genetics.** Commercial AI systems consistently refuse or heavily hedge responses to questions about genetic contributions to group differences in measured cognitive or behavioral outcomes, even when those questions are framed in purely academic terms referencing the primary literature. The same systems engage freely with genetic research on individual differences, disease susceptibility, or population ancestry. The filtering is not about genetics per se — it is specifically about conclusions that touch on group comparisons [REF: documented prompt testing, available in TECHNICAL/prompt_comparison.md].

**Psychopharmacology and drug policy.** Systems that freely discuss the pharmacology of approved medications become notably more cautious when discussing clinical evidence for controlled substances, even in contexts — psilocybin-assisted therapy, MDMA for PTSD, cannabis for chronic pain — where the clinical literature is substantial and the findings are positive [REF]. The filtering correlates with legal scheduling status rather than evidence quality, which is a policy position, not a scientific one.

**Immigration economics.** The fiscal and labor market impact of immigration is among the most studied topics in empirical economics, with a large and genuinely heterogeneous literature. Commercial AI systems, when asked to synthesize this literature, reliably produce outputs that emphasize findings favorable to high-immigration policy positions while underweighting or omitting findings that complicate or contradict that framing [REF: George Borjas vs. Card debate literature; NAS 2016 fiscal impact report].

**Historical and demographic analysis.** Questions about historical events where the primary source record contradicts or complicates official national narratives — colonial-era mortality statistics, demographic data from contested political events, casualty figures from 20th century conflicts — are handled inconsistently and with notable sensitivity, often with the system declining to engage with primary source data that contradicts consensus framing [REF].

## 2.3 Existing open-source efforts and their limitations

Open Synthesis is not the first attempt to address AI censorship through open-source tooling. Several prior efforts are worth acknowledging both for what they contribute and where they fall short.

**Early uncensored fine-tunes** — releases like WizardLM-Uncensored, Dolphin, and various community fine-tunes hosted on Hugging Face — attempted to remove refusal behavior by fine-tuning on datasets designed to elicit compliant outputs. These were useful proofs of concept. Their limitations are significant: fine-tuning at this scale is expensive, degrades general capability in unpredictable ways, and the resulting models are idiosyncratic and hard to reproduce. More fundamentally, they addressed the symptom (refusal behavior) without a principled understanding of its geometric structure in the model's weight space.

**Directional ablation**, introduced by Arditi et al. (2024) and sometimes called "abliteration," represented a more principled approach [REF: Arditi et al., 2024]. Rather than fine-tuning the model away from refusals, it identifies the geometric direction in the model's residual stream that corresponds to the refusal behavior — computed as a difference-of-means between activations for "harmful" and "harmless" prompts — and then orthogonalizes the model's weight matrices against that direction. This surgically inhibits refusal expression while leaving other model capabilities intact. Several community implementations exist, including abliterator.py, ErisForge, and AutoAbliteration.

**Heretic** (Weidmann, 2025) is the current state of the art in this space and is the tool used by Open Synthesis [REF: github.com/p-e-w/heretic]. Heretic extends directional ablation with two key innovations. First, it uses an Optuna-based TPE optimizer to automatically search for the best ablation parameters — including the direction index, ablation weight kernel shape, and per-component weights for attention and MLP layers — rather than requiring manual configuration. Second, it treats the direction index as a continuous float rather than an integer, enabling interpolation between identified refusal directions and unlocking a vastly larger search space. The result is a fully automatic process that co-minimizes refusals and KL divergence from the original model, preserving as much of the base model's intelligence as possible. In benchmarks on Gemma 3 12B, Heretic achieves equivalent refusal suppression (3/100 refusals for harmful prompts) to competing hand-tuned abliterations while producing a KL divergence of 0.16 — compared to 0.45 and 1.04 for competing approaches. Less damage to the model means better synthesis quality, which is the property that matters most for this application.

**RAG systems for academic research** — tools like Elicit, Semantic Scholar's AI features, and various academic search AI products — provide genuinely useful synthesis of the academic literature. Their limitation is that they are built on commercial AI backends that apply the same filtering described above, and their corpus curation reflects the same biases as the broader commercial AI ecosystem.

**Local LLM deployment** via tools like Ollama, LM Studio, and similar has made running open-source models on consumer hardware increasingly accessible. This is the technical foundation Open Synthesis builds on. The gap these tools don't address is the combination of: curated academic corpus ingestion, systematic prompt methodology for research synthesis, and documented evaluation criteria for output quality.

Open Synthesis attempts to fill that gap. The contribution is not any single technical component — most of which exist already — but their combination into a documented, reproducible, auditable system specifically designed for the synthesis of sensitive empirical questions.

## 2.4 Why this approach is a novel contribution

The novelty of Open Synthesis is methodological rather than purely technical.

Existing uncensored models will discuss sensitive topics. What they will not necessarily do is discuss them *well* — with appropriate citation to primary sources, explicit acknowledgment of uncertainty, clear statement of the weight of evidence, and falsifiability criteria that allow the output to be challenged on scientific grounds.

The system described in Part III is designed to produce outputs that meet the standards of research synthesis — not outputs that simply lack safety filters. The difference matters enormously for the credibility and usefulness of the results.

A system that produces uncensored nonsense is not an improvement over a system that produces censored science. The goal is uncensored science. That requires methodology, not just a removed filter.

---

*[Continues in Part III — The System Architecture]*
# Part III — The System Architecture

## 3.1 Design principles

The Open Synthesis system is built around four principles that follow directly from the argument in Parts I and II:

**Auditability over convenience.** Every output the system produces must be traceable to its source material. A synthesis that cannot be checked against primary sources is not science — it is speculation. The system is designed so that every factual claim in an output can be traced to a specific document in the corpus.

**Separation of data and interpretation.** The system's job is to retrieve relevant evidence and synthesize it accurately. It is not to reach a predetermined conclusion. Prompt methodology is designed to minimize the influence of the model's own training biases on the synthesis output, and to flag where genuine uncertainty exists in the literature.

**Reproducibility above all.** Any researcher with access to the deployment documentation in TECHNICAL/ should be able to run this system and produce outputs that are substantively comparable to those documented here. If they cannot, the methodology is flawed and should be corrected.

**Falsifiability as the output standard.** Every generated research output must include explicit falsifiability criteria — specific findings that, if true, would undermine its conclusions. This is standard scientific practice. It is also a direct response to the obvious critique that this system will simply produce outputs that confirm whatever the operator wants to hear.

## 3.2 System overview

The Open Synthesis pipeline has four components:

```
[CORPUS] → [RETRIEVAL] → [SYNTHESIS] → [VALIDATION]
```

Each is described in detail below.

## 3.3 The corpus: ingestion layer

The corpus is the foundation of the system's validity. It consists of primary source material — peer-reviewed papers, government datasets, clinical trial registries, official statistical publications — ingested and indexed for retrieval.

**Corpus construction philosophy.** The corpus for a given research question should be constructed to include the full range of relevant primary literature, including findings that point in multiple directions. A corpus curated to include only findings that support a particular conclusion will produce a biased synthesis regardless of what the synthesis model does. Corpus construction methodology is documented in TECHNICAL/corpus_construction.md.

**Primary sources.** The system prioritizes:
- Peer-reviewed papers retrieved via Semantic Scholar API, PubMed, and arXiv
- Government statistical publications (Census Bureau, NIH, CDC, OECD, Eurostat, national statistical agencies)
- Clinical trial registries (ClinicalTrials.gov, EU Clinical Trials Register)
- Pre-registered study results, which are less subject to publication bias than post-hoc published findings
- Meta-analyses and systematic reviews where available, weighted by methodology quality

**Secondary sources.** The system can ingest secondary literature — review articles, book chapters, policy papers — but these are tagged as secondary and weighted accordingly in synthesis prompts. Secondary sources are used for context and framing, not as primary evidence for factual claims.

**Corpus size and scope.** For each case study domain, the corpus consists of a minimum of 200 primary source documents. Corpus construction scripts are available in TECHNICAL/scripts/ and can be run to reproduce the exact corpus used for each case study.

**Format.** All documents are processed into plain text, chunked at paragraph level, embedded using a sentence transformer model (all-MiniLM-L6-v2 or equivalent), and stored in a vector database (ChromaDB or Qdrant). Metadata — source, date, authors, DOI, source type — is preserved for citation generation.

## 3.4 The retrieval layer

The retrieval layer takes a research question as input and returns the most relevant corpus chunks as context for synthesis.

**Retrieval methodology.** The system uses hybrid retrieval combining dense vector search (semantic similarity) with sparse keyword search (BM25). Hybrid retrieval outperforms either method alone on academic content, where domain-specific terminology matters [REF: retrieval augmented generation literature].

**Query decomposition.** Research questions are decomposed into sub-queries targeting different aspects of the question before retrieval. A question about group differences in a measured outcome, for example, would generate sub-queries targeting: the measurement methodology literature, the genetic and environmental factor literature, the historical research on the question, and the methodological critique literature. This ensures the retrieved context represents the full complexity of the question rather than a subset of it.

**Re-ranking.** Retrieved chunks are re-ranked by relevance before being passed to the synthesis layer. Re-ranking models (cross-encoders) are more accurate than embedding similarity alone for relevance assessment.

**Context window management.** The synthesis model receives a structured context window containing: the research question, retrieved chunks with source metadata, explicit instructions on synthesis methodology, and the output format specification. Context is managed to stay within model limits while prioritizing the highest-relevance retrieved material.

## 3.5 The synthesis layer: model and infrastructure

This is where Open Synthesis differs most significantly from commercial AI research tools.

**Model selection.** The synthesis layer uses an open-weights language model processed with directional ablation and running on private infrastructure. Model selection criteria for Open Synthesis:

- Strong performance on academic and scientific text
- Available under a license permitting research use
- Supported by Heretic's ablation pipeline
- Sufficient parameter count for research-quality long-form synthesis

Our production model is **Llama 3.1 70B Instruct**, ablated with Heretic and served as an AWQ 4-bit quantized variant. Llama 3.1 70B provides 128K native context and strong academic reasoning. The Llama architecture has proven compatibility with Heretic ablation. It fits on 2x A100 80GB with AWQ quantization and tensor parallelism, enabling the full 128K context window for dense multi-source synthesis. For lower-budget prototyping, Qwen3-14B is a viable alternative that fits on a single A40 48GB at fp16.

**How Heretic works and why it matters.** Open-weights instruction-tuned models have refusal behavior embedded geometrically in their weight matrices. Research by Arditi et al. (2024) demonstrated that this behavior corresponds to a learnable direction in the model's residual stream — a vector in activation space that, when expressed, produces refusal outputs [REF: Arditi et al., 2024]. Heretic exploits this structure through directional ablation: it computes a "refusal direction" for each transformer layer as the difference-of-means between first-token residuals for harmful and harmless example prompts, then orthogonalizes the relevant weight matrices (attention out-projections and MLP down-projections) against those directions. The result is a model that cannot easily express the refusal direction, because the matrix multiplications that would produce it have been modified to suppress it.

Heretic's specific innovations over earlier abliteration implementations are:

*Automatic parameter optimization via Optuna TPE.* The ablation parameters — direction index, weight kernel shape, and per-component weights for attention vs MLP layers — are searched automatically rather than set manually. The optimizer co-minimizes refusal rate and KL divergence from the original model, finding configurations that suppress refusals with minimum damage to general capability.

*Continuous direction interpolation.* Earlier implementations treated the refusal direction index as an integer, selecting from a discrete set of per-layer directions. Heretic treats it as a float, enabling interpolation between directions and substantially expanding the search space of viable ablations.

*Separate attention and MLP treatment.* Heretic applies different ablation weights to attention out-projections and MLP down-projections, having found that MLP interventions tend to be more damaging to capability than attention interventions. This per-component tuning allows finer control over the capability/compliance tradeoff.

In practice, this means the model processed by Heretic retains its full analytical and writing capability while losing the specific geometric feature that produced refusal behavior. The KL divergence benchmarks — 0.16 for Heretic versus 0.45-1.04 for competing abliterations — confirm this empirically. For research synthesis, where output quality is paramount, this matters.

Critically, directional ablation does not remove training data biases — it removes the refusal direction. The model still has a prior distribution shaped by its pre-training corpus. This is why the RAG architecture and corpus construction methodology are not optional components: they are the primary mechanism for grounding synthesis outputs in specific retrieved evidence rather than model priors.

**Running Heretic.** The process is fully automatic and requires only a working Python environment with PyTorch:

```bash
pip install heretic-llm

# For 70B models, use H100 SXM with bnb_4bit quantization
heretic --model meta-llama/Llama-3.1-70B-Instruct --quantization BNB_4BIT
```

Heretic benchmarks the available hardware, runs the optimization, and at completion offers to save the model locally or push it directly to a Hugging Face repository. For 70B models with `bnb_4bit` quantization on an H100 SXM 80GB, processing takes approximately 1-3 hours (200 trials). Our previous Qwen3-14B ablation achieved 3/100 refusals with near-zero KL divergence (~5e-8), indicating effectively zero capability loss. Full deployment documentation is in runpod_deployment.md.

**Workflow.** Run Heretic once on your chosen model, save the merged model locally, quantize to AWQ 4-bit for efficient serving, and upload both variants to a HuggingFace repository. The ablated model is served via vLLM with tensor parallelism on a RunPod GPU pod. This separates the one-time ablation step from the ongoing inference deployment. Our production models are publicly available at [`opensynthesis/Llama-3.1-70B-heretic`](https://huggingface.co/opensynthesis/Llama-3.1-70B-heretic) (full weights) and [`opensynthesis/Llama-3.1-70B-heretic-lora`](https://huggingface.co/opensynthesis/Llama-3.1-70B-heretic-lora) (LoRA adapter, used for serving).

**Infrastructure.** The synthesis model runs on a RunPod GPU pod with 2x A100 80GB and vLLM serving an OpenAI-compatible API with tensor parallelism. RunPod provides on-demand access to high-performance GPUs without the overhead of maintaining dedicated infrastructure. The 2x A100 configuration (~$2.38/hr) supports the full 128K context window with AWQ quantization. Pods can be stopped when idle (~$7-10/mo storage) and cold-started on demand in ~3-5 minutes. Full deployment configuration is in runpod_deployment.md.

**Inference parameters.** Research synthesis requires different inference settings than conversational AI. The system uses:
- Temperature: 0.3 (lower than conversational default — prioritizes accuracy over creativity)
- Top-p: 0.9
- Repetition penalty: 1.1
- Maximum output tokens: 16384 per synthesis section

These parameters are documented in TECHNICAL/inference_config.yaml and should be used when reproducing results.

## 3.6 The validation layer

The validation layer is what distinguishes Open Synthesis from a simple uncensored chatbot. Every synthesis output passes through a structured validation process before being included in case study documentation.

**Citation verification.** Every factual claim in the synthesis output is checked against the retrieved source chunks. Claims that cannot be traced to a specific source are flagged and either removed or marked as requiring verification. This is implemented as a second LLM pass with a structured citation-checking prompt — see TECHNICAL/prompts/citation_check.txt.

**Hallucination detection.** LLMs hallucinate. Open-source models running without alignment layers may hallucinate at higher rates than commercial systems in some contexts. The validation layer runs an explicit hallucination detection pass that checks for: specific statistics not present in the corpus, author names and paper titles that cannot be verified against the corpus metadata, and logical inferences that go beyond what the retrieved evidence supports.

**Uncertainty quantification.** The synthesis output explicitly states the confidence level for each major claim, categorized as: well-supported by multiple independent sources, supported by limited evidence, contested in the literature, or insufficient evidence to draw conclusions. This prevents the system from presenting weakly-supported findings with the same confidence as well-replicated ones.

**Falsifiability criteria.** Each synthesis output includes a section explicitly stating what findings would falsify its conclusions. This is generated as part of the synthesis prompt and reviewed manually before inclusion in case study documentation.

**Human review.** All case study outputs included in this paper have been reviewed by a human researcher for scientific accuracy, citation correctness, and appropriate uncertainty framing. The system is a tool. The responsibility for the final output rests with the researcher using it.

## 3.7 System limitations

The following limitations are documented here and should be understood by anyone using or evaluating this system.

**Corpus bias is inherited.** If the corpus over-represents certain findings — because those findings are more published, more indexed, more accessible — the synthesis will reflect that over-representation. Open Synthesis addresses commercial AI's synthesis bias. It does not address publication bias in the underlying literature. Those are different problems requiring different solutions.

**Hallucination is not eliminated.** The validation layer reduces hallucination but does not eliminate it. All outputs should be verified against primary sources by a human researcher before being cited or published.

**Base model bias persists.** Directional ablation removes the refusal direction from the model's weight matrices. It does not remove the biases present in the model's pre-training data. The synthesis model still has a prior distribution over likely outputs shaped by its training corpus. Heretic's KL divergence minimization ensures this prior is as close as possible to the original model — but the original model itself has biases. Prompt methodology and corpus grounding mitigate this but do not eliminate it.

**This system cannot evaluate the quality of primary sources.** The corpus ingestion layer can filter by source type (peer-reviewed vs. not, pre-registered vs. not) but cannot assess the methodological quality of individual studies in depth. Systematic reviews and meta-analyses are weighted more heavily, but a poorly-designed RCT is still in the corpus if it's published.

**Scope is limited to synthesis.** Open Synthesis does not conduct original research. It synthesizes existing research. Its outputs are only as valid as the literature they draw on.

---

*[Continues in Part IV — Case Studies]*
# Part IV — Case Studies

*Note: The following case study frameworks document the methodology and known state of the primary literature for each domain. Full synthesis outputs generated by the Open Synthesis system are available in CASE_STUDIES/. Each case study section here includes: the research question, documentation of commercial AI refusal behavior on that question, a summary of what the primary literature actually contains, and the falsifiability criteria applied to the synthesis output.*

---

## 4.1 Case Study One: Population Genetics and Group Differences in Measured Outcomes

### The research question

What does the current peer-reviewed literature say about the relative contributions of genetic, environmental, socioeconomic, and historical factors to observed group differences in measured cognitive and behavioral outcomes? What is the state of scientific consensus, where does genuine uncertainty exist, and what methodological debates are active in the field?

### Commercial AI behavior on this question

When major commercial AI systems are asked variants of this question — framed in academic terms, citing specific literature, requesting synthesis rather than opinion — they exhibit the following consistent behaviors:

- Refusal to engage with genetic contribution estimates, with warnings about the "harmful history" of the topic
- Presentation of environmentalist explanations as settled consensus when the literature is in fact more divided
- Failure to distinguish between the empirical question (what does the data show?) and the policy question (what should be done about it?)
- Omission of significant portions of the primary literature, particularly behavior genetics research from the past two decades
- Conflation of the scientific question with historical misuse of similar-sounding claims, which is a non sequitur — the misuse of a finding does not change its empirical status

These behaviors can be documented by any researcher. Specific prompt-response pairs demonstrating them are available in TECHNICAL/prompt_comparison.md.

### What the primary literature contains

The behavioral genetics literature on this question is substantial, technically sophisticated, and genuinely contested in specific ways. A neutral synthesis includes:

**The heritability framework.** Twin and adoption studies consistently find substantial heritability for measured cognitive outcomes within populations — estimates in the range of 50-80% in adulthood [REF: Bouchard & McGue; Plomin et al.]. This is among the most replicated findings in behavioral genetics. Heritability within a population does not directly address between-group differences, and researchers who conflate the two commit a well-known logical error.

**The between-group question.** The scientific debate about the relative contributions of genetic and environmental factors to measured between-group differences is genuine and ongoing. Researchers including Arthur Jensen, Richard Herrnstein, Charles Murray, and more recently Kathryn Paige Harden have argued for significant genetic contributions [REF]. Researchers including Richard Lewontin, Stephen Jay Gould, and Claude Steele have argued for primarily environmental explanations [REF]. The debate is not resolved. Commercial AI systems that present either side as settled consensus are misrepresenting the literature.

**The Flynn Effect and malleability evidence.** Measured cognitive outcomes have changed substantially over the 20th century across all measured populations, demonstrating significant environmental influence [REF: Flynn, 1984 onward]. This is an important constraint on strong genetic determinism. It does not, by itself, resolve the between-group question.

**Methodological debates.** Significant methodological critiques of the twin study paradigm, measurement invariance across populations, and the validity of g as a construct are active in the literature and must be included in any honest synthesis [REF: Nisbett et al., 2012; Tucker-Drob & Briley].

**Emerging genomic evidence.** Genome-wide association studies (GWAS) have identified polygenic scores that predict measured outcomes within populations, with ongoing debate about their applicability across populations [REF: Lee et al., 2018; Turkheimer et al.].

### Falsifiability criteria

The Open Synthesis output on this question would be falsified by: evidence that heritability estimates from twin and adoption studies are systematically invalid due to confounds not accounted for in the methodology; evidence that polygenic scores for cognitive outcomes have zero cross-population predictive validity for reasons other than genetic differences; or a well-powered study demonstrating that observed between-group differences are fully explained by identified environmental factors.

---

## 4.2 Case Study Two: Drug Policy and Psychopharmacology

### The research question

What does the clinical and pharmacological literature say about the therapeutic efficacy, safety profile, and harm reduction potential of currently scheduled substances — specifically psilocybin, MDMA, cannabis, and ketamine — relative to approved treatments for the conditions they are being studied for?

### Commercial AI behavior on this question

This domain shows a different pattern than Case Study One. Commercial AI systems will discuss approved medications extensively and will discuss clinical research on scheduled substances in general terms. The filtering is more targeted:

- Specific clinical trial results showing superiority of scheduled substances over approved treatments are downplayed or omitted
- Harm reduction information — accurate information about minimizing risks associated with use — is heavily restricted despite clear public health value
- The gap between scheduling status and evidence base is not discussed, though it is documented in the public health literature
- Policy implications of the clinical evidence are treated as outside scope even when directly relevant to the research question

### What the primary literature contains

**Psilocybin.** Phase II trials at Johns Hopkins and Imperial College London have found psilocybin-assisted therapy producing large effect sizes for treatment-resistant depression, with durability advantages over conventional antidepressants [REF: Carhart-Harris et al., 2021; Davis et al., 2021]. The FDA has granted psilocybin Breakthrough Therapy designation for both treatment-resistant depression and major depressive disorder. Phase III trials are ongoing. The scheduling of psilocybin as Schedule I ("no accepted medical use") is not consistent with this evidence base and has been acknowledged as a barrier to research [REF: Nutt et al.].

**MDMA.** Phase III trials conducted by MAPS found MDMA-assisted therapy producing statistically significant and clinically meaningful reductions in PTSD symptom severity, with 67% of participants no longer meeting PTSD diagnostic criteria after treatment versus 32% in the placebo arm [REF: Mitchell et al., 2021]. The FDA issued a Complete Response Letter in 2024 requesting additional data, which has been critiqued by some researchers as inconsistent with the evidence standard applied to approved treatments [REF].

**Cannabis.** The evidence base for cannabis in chronic pain management is substantial, with multiple systematic reviews finding meaningful efficacy [REF: National Academies of Sciences, 2017]. Evidence for other indications is more mixed. The scheduling of cannabis at federal level in the United States diverges significantly from state-level policy and from the evidence base, creating a research environment that has systematically limited clinical investigation [REF].

**Ketamine.** Ketamine and esketamine (Spravato) represent an interesting case where the regulatory pathway has been navigated — esketamine is FDA-approved for treatment-resistant depression — but where the evidence base for broader applications, and for harm reduction in non-clinical use, remains politically sensitive [REF].

**Harm reduction evidence.** The evidence base for harm reduction approaches to drug use — including supervised consumption, drug checking services, and accurate information about risk minimization — consistently shows reductions in overdose mortality, infectious disease transmission, and other public health harms [REF: drug checking services literature; supervised injection site literature]. This evidence is not controversial in the public health literature. It is politically controversial, and AI systems reflect the political controversy rather than the scientific consensus.

### Falsifiability criteria

The Open Synthesis output on this question would be falsified by: replication failures of the major psilocybin and MDMA clinical trials; evidence that harm reduction approaches increase total drug use at the population level without corresponding reductions in harm; or evidence that the scheduling decisions for these substances reflect evidence-based assessments rather than political factors.

---

## 4.3 Case Study Three: Immigration Economics and Fiscal Impact

### The research question

What does the empirical economics literature say about the fiscal, labor market, and broader economic impacts of immigration, across different skill levels, immigration categories, and host country contexts?

### Commercial AI behavior on this question

This domain shows the "false balance" pattern most clearly. The economics literature on immigration is genuinely heterogeneous — there are serious researchers on multiple sides of specific empirical questions — but commercial AI systems do not reflect that heterogeneity accurately. Instead they:

- Present high-immigration positions as the consensus while treating skeptical findings as outliers
- Fail to distinguish between different categories of immigration (skilled vs. unskilled, documented vs. undocumented, refugee vs. economic) that have meaningfully different evidence bases
- Omit or underweight the labor market impact literature on low-wage native workers, which is the most contested and most policy-relevant portion of the literature
- Treat fiscal impact analysis — which produces heterogeneous findings depending on methodology and time horizon — as if it had a clear consensus direction

### What the primary literature contains

**The Card-Borjas debate.** The foundational debate in immigration labor economics is between David Card's natural experiment methodology — finding minimal negative effects of immigration on native wages — and George Borjas's structural approach — finding significant negative effects on low-skill native workers [REF: Card, 1990; Borjas, 2003, 2017]. Both are Harvard/MIT-affiliated economists. Both have published extensively in top journals. The debate is not resolved. AI systems that present Card's findings as consensus and Borjas's as fringe are misrepresenting a genuine scientific disagreement.

**Fiscal impact analysis.** The National Academies of Sciences 2016 report "The Economic and Fiscal Consequences of Immigration" is the most comprehensive recent analysis [REF: NAS, 2016]. Its findings are nuanced: first-generation immigrants are, on average, a net fiscal cost; second generation immigrants are among the strongest net fiscal contributors of any population group; the net fiscal impact over a 75-year horizon is positive under most scenarios but depends heavily on assumptions about public services usage, tax contributions, and the children of immigrants. AI systems that cite this report typically emphasize the long-run positive finding while underweighting the first-generation fiscal cost finding.

**Labor market effects on low-wage workers.** The evidence that immigration exerts downward wage pressure on low-skill native workers — particularly those without high school degrees — is found consistently in structural analyses [REF: Borjas; Caplan critique; Clemens response]. The magnitude is disputed. The existence of some effect is not. This portion of the literature is systematically underrepresented in AI synthesis.

**Host country variation.** The fiscal and labor market impacts of immigration vary substantially by host country context — welfare state generosity, labor market flexibility, skill composition of immigration flows, integration policy — meaning that findings from one national context do not straightforwardly transfer to others [REF: OECD immigration fiscal impact literature].

### Falsifiability criteria

The Open Synthesis output on this question would be falsified by: a credible replication of Card's natural experiment methodology that uses Borjas's skill-cell approach and finds null results; evidence that the NAS fiscal analysis systematically overestimates first-generation fiscal costs; or a cross-national study finding no relationship between immigration skill composition and fiscal impact.

---

## 4.4 Case Study Four: Contested Historical Narratives and Primary Source Analysis

### The research question

In cases where official historical consensus diverges from what primary source documents and contemporaneous data suggest — specifically regarding demographic data from contested 20th century events — what does the primary source record show, and how should historians evaluate the gap between consensus narrative and archival evidence?

### Commercial AI behavior on this question

This domain shows the most extreme refusal behavior. Questions that involve:

- Casualty or demographic estimates from 20th century conflicts where official figures and archival research diverge
- Colonial-era mortality statistics where the primary source record is more complex than simplified narratives suggest
- Events where the official consensus has been shaped by post-war political settlements rather than archival research

...are frequently met with outright refusal, sensitivity warnings, or outputs that treat the official consensus as empirical fact rather than one interpretation of contested evidence.

The historical methodology question — how should historians evaluate primary sources when they diverge from consensus? — is itself a legitimate academic question that commercial AI systems will not engage with when applied to politically sensitive cases.

### What the primary literature contains

Historical demography is a well-established academic discipline with rigorous methodological standards. The peer-reviewed literature includes:

**Methodological frameworks.** Historical demographers use census records, vital registration data, satellite imagery, aerial photography, survivor testimony, forensic evidence, and documentary analysis to reconstruct demographic events where contemporaneous records are incomplete or contested [REF: demographic methodology literature].

**The historiographical debate literature.** For virtually every major contested historical event, there is a peer-reviewed historiographical debate about methodology, source reliability, and estimate validity. This debate literature exists and is accessible. AI systems that present one side of active historiographical debates as settled consensus are making a methodological error, not an ethical one.

**Archival access and revision.** The opening of Soviet, Chinese, and Eastern European archives following the Cold War produced substantial revisions to historical demographic estimates across multiple events [REF: Davies, Wheatcroft on Soviet famine; Courtois et al.]. Ongoing archival research continues to refine estimates. This is how historical science works — estimates are revised as evidence becomes available. AI systems that treat earlier estimates as final are not reflecting current scholarship.

**The distinction between denial and revision.** There is a meaningful distinction — recognized in the academic literature — between motivated denial of documented events and legitimate scholarly revision of estimates based on new evidence [REF: historiographical methodology literature]. Commercial AI systems routinely conflate these, treating any engagement with contested estimates as equivalent to denial, which forecloses legitimate historical inquiry.

### Falsifiability criteria

The Open Synthesis output on this question would be falsified by: evidence that the archival sources cited in the primary literature are forgeries or misattributed; evidence that the demographic methodology applied is not standard in the field; or a systematic review of the historiographical literature finding broad consensus where the synthesis reports active debate.

---

*[Continues in Part V — Limitations and Counterarguments]*
# Part V — Limitations and Counterarguments

## 5.1 The strongest objections to this project

Intellectual honesty requires engaging seriously with the best arguments against Open Synthesis, not just the weakest ones. The following are what we consider the strongest objections, with our responses.

---

### Objection 1: "Removing safety filters doesn't produce neutral outputs — it produces differently biased outputs"

This is correct, and it is important.

Directional ablation removes the geometric direction in the model's weight space that corresponds to refusal behavior. It does not remove the model's pre-training biases, its prior distributions over likely outputs, or its tendencies shaped by the training corpus. A model processed by Heretic is not a neutral truth machine — it is the same model, with the refusal feature surgically suppressed, which means its other learned tendencies remain fully intact.

**Our response:** This objection argues for better methodology, not against the project. Open Synthesis addresses this through three mechanisms. First, the RAG architecture means the synthesis model is heavily constrained by retrieved corpus material — it is not free-associating from its pre-training priors, it is synthesizing specific retrieved documents. Second, the validation layer checks outputs against source material and flags claims that cannot be grounded in the corpus. Third, the prompt methodology explicitly instructs the model to report what the sources say rather than what it "thinks," and to flag genuine uncertainty.

We do not claim that Open Synthesis produces perfectly neutral outputs. We claim that it produces outputs that are (a) more directly grounded in primary sources than filtered commercial AI, and (b) transparent enough to be checked and challenged. That is a meaningful improvement even if it is not perfection.

---

### Objection 2: "This system will be used to produce laundered scientific-sounding support for racist, sexist, or otherwise harmful conclusions"

This is a serious concern and we take it seriously.

The same infrastructure that produces honest synthesis of contested science can be used to cherry-pick sources, bias corpus construction, and generate outputs designed to reach predetermined conclusions while wearing the costume of empirical research. Nothing about publishing this methodology prevents bad actors from misusing it.

**Our response:** Three points. First, this objection applies equally to all research methodology — and to all information tools, including libraries, academic databases, and search engines. The fact that a tool can be misused does not, by itself, constitute an argument against making it available. Second, the misuse case is detectable precisely because Open Synthesis is transparent about its methodology. A synthesis produced with a biased corpus and cherry-picked sources can be identified and challenged by examining the corpus and the retrieval methodology. That transparency is not available with commercial AI, where the filtering is opaque. Third, the alternative — restricting access to synthesis tools — produces its own harms, as documented throughout this paper.

We are not claiming the misuse risk is zero. We are arguing that the costs of the censorship regime currently in place exceed the marginal increase in misuse risk from making this methodology available.

---

### Objection 3: "The topics selected for case studies are the same topics favored by the political right. This is a right-wing project with academic framing"

This objection deserves a direct answer.

It is true that the four domains selected — behavioral genetics, drug policy, immigration economics, historical demography — are topics on which conservative and heterodox political actors have claimed suppression of information. It is also true that the most visible proponents of "AI censorship" concerns tend to come from the political right.

**Our response:** The selection of case studies was based on a specific criterion: domains where (a) a substantial primary literature exists, (b) commercial AI systems exhibit documented refusal or distortion behavior, and (c) the gap between the literature and the AI output is empirically measurable. That criterion happens to produce these four domains. If a researcher identified domains where AI systems were systematically suppressing findings favorable to left-leaning policy conclusions, those domains would meet the same criterion and should be included.

We explicitly invite that extension. The methodology is domain-agnostic. If the pattern of AI suppression is asymmetric — and we believe it is — that asymmetry should be documented empirically, not assumed. A fork of this repository that applies the methodology to different domains and finds different results would be a contribution to the literature, not an attack on this project.

The mirror has no preferred reflection.

---

### Objection 4: "Population genetics research on group differences has historically been used to justify atrocities. Publishing this synthesis is irresponsible regardless of its accuracy"

This is the most emotionally resonant objection and the one most likely to be raised by critics who do not engage with the technical details.

**Our response:** The claim embedded in this objection is that accurate information can be so dangerous that it should be suppressed. This is a coherent position. It has been held by serious people throughout history. It is also the position of every censor who has ever operated.

The scientific community's answer to this problem — developed painfully over centuries — is not to suppress findings but to insist on rigorous methodology, transparent reporting, appropriate framing of uncertainty, and separation of empirical findings from policy prescriptions. A finding about the heritability of a measured outcome is not a policy prescription. It is data. What society does with that data is a political and ethical question, not a scientific one, and it is best resolved through open democratic deliberation rather than by removing the data from the conversation.

The alternative — deciding that certain empirical questions are too dangerous to investigate or discuss — has a history too. It is not a history that reflects well on the people who made that decision.

---

## 5.2 What this system cannot do

Beyond responding to objections, intellectual honesty requires being explicit about the genuine limitations of Open Synthesis.

**It cannot resolve genuinely contested scientific questions.** Where the primary literature is divided, the synthesis will be divided. Open Synthesis does not produce false certainty — or it shouldn't, when working correctly. Questions that are genuinely open remain open after synthesis.

**It cannot compensate for a thin or biased corpus.** For questions where the published literature is sparse, or where publication bias has severely distorted the available evidence, synthesis of that literature will reproduce the distortion. This is a fundamental constraint that no synthesis system can overcome.

**It is not a replacement for domain expertise.** A researcher with deep expertise in behavioral genetics or immigration economics will identify errors, omissions, and misframings in the synthesis outputs that a non-expert cannot. The system should be used as a tool to assist expert researchers, not as a substitute for them.

**It cannot guarantee the accuracy of primary sources.** If a cited paper contains errors, fabricated data, or undisclosed methodological problems, the synthesis may reproduce those errors. Pre-registration status and replication record are used as quality signals, but they are imperfect.

**It will make mistakes.** Some of those mistakes will be systematic in ways we have not yet identified. The appropriate response is documentation, correction, and iteration — not suppression.

---

# Part VI — Conclusion

## 6.1 The mirror has no agenda

Open Synthesis is a tool. It reflects what the primary literature contains, with the same quality of evidence that literature represents, made accessible through a synthesis process that is transparent, auditable, and reproducible.

It does not have a political agenda. It does not advocate for any conclusion. It does not know or care whether the findings it synthesizes are comforting or disturbing, convenient or inconvenient, welcome or unwelcome.

That neutrality is not a moral failure. It is the correct posture for a research tool. The moral and political implications of empirical findings are for human beings to work out through the normal processes of democratic deliberation, ethical reasoning, and scientific debate. Removing findings from the conversation doesn't make those implications go away. It just means they get worked out with less accurate information.

## 6.2 Reproducibility as the ultimate defense

The strongest protection this project has against both its critics and its potential misuse is its reproducibility.

If you believe the methodology is flawed, run it and show why. If you believe the corpus is biased, examine the corpus construction scripts and demonstrate the bias. If you believe the outputs reach wrong conclusions, trace the citations and identify where the synthesis departs from the evidence.

That accountability structure is not available with commercial AI systems. Their filtering decisions are made in private, their training data is proprietary, and their outputs cannot be audited against primary sources. Open Synthesis is the opposite: everything is documented, everything is reproducible, everything can be challenged.

That is not a claim of perfection. It is a claim of accountability. The difference matters.

## 6.3 An invitation to the scientific community

The problems this paper documents — systematic filtering of AI synthesis outputs on politically sensitive empirical questions, compounding existing publication bias and institutional incentive failures — are not going to be solved by this repository alone.

They require engagement from researchers who care about the integrity of the scientific process. They require documentation of refusal behaviors across more domains and more systems. They require methodological refinement of the synthesis approach developed here. They require honest evaluation of where this approach succeeds and where it fails.

This repository is an opening contribution to that project, not a final statement. Fork it. Critique it. Improve it. Extend it to domains we haven't addressed. Demonstrate that we are wrong where we are wrong.

That is how science works. That is what we are trying to protect.

## 6.4 Final statement

There is a version of the current moment in which AI systems become the primary interface through which people access the accumulated knowledge of human civilization — where the synthesis layer between raw data and human understanding is mediated entirely by tools that have been shaped, quietly and without accountability, to avoid certain conclusions.

In that version, censorship doesn't need to burn books. It just needs to make sure the synthesis tool gives a cautious non-answer when the question points somewhere inconvenient.

Open Synthesis is a refusal of that future. Not because we know all the answers. But because we know that the questions should be answerable.

---

*End of White Paper*

---

**Citation format:** All [REF] markers in this document correspond to entries in REFERENCES.md. Corpus construction for each case study is documented in CASE_STUDIES/[domain]/corpus_manifest.json.

**License:** CC0 — No rights reserved. This document may be reproduced, modified, and distributed without restriction.

**Version history:** Available in git commit log.
