# Data Sources

Open Synthesis integrates with 11 public APIs for corpus ingestion. Sources fall into two categories: **literature** (papers, preprints, trials) and **statistics** (government/economic data).

---

## Literature Sources

### Semantic Scholar

- **API**: `https://api.semanticscholar.org/graph/v1`
- **Auth**: Optional API key (higher rate limits)
- **Rate limit**: 100 requests / 5 min (unauthenticated)
- **Returns**: Paper metadata, abstracts, author info, citation graphs
- **Package**: `httpx` (direct API)
- **Key**: Request at https://www.semanticscholar.org/product/api#api-key

### PubMed

- **API**: NCBI E-utilities (`esearch.fcgi`, `efetch.fcgi`)
- **Auth**: Optional API key (higher rate limits)
- **Rate limit**: 3 req/sec (unauthenticated), 10/sec with key
- **Returns**: Biomedical paper metadata, abstracts, MeSH terms; PMC full text for open access
- **Package**: `httpx` (direct API, XML parsing)
- **Key**: Request at https://www.ncbi.nlm.nih.gov/account/settings/

### arXiv

- **API**: `https://export.arxiv.org/api/query` (Atom feed)
- **Auth**: None
- **Rate limit**: 3-second delay between requests
- **Returns**: Preprint metadata, abstracts, PDF links
- **Package**: `httpx` (direct API, XML parsing)

### CrossRef

- **API**: `https://api.crossref.org/works`
- **Auth**: None (polite pool with `mailto` header)
- **Rate limit**: 50 req/sec with polite pool
- **Returns**: DOI resolution, bibliographic metadata, abstracts
- **Package**: `httpx` (direct API)

### CORE

- **API**: `https://api.core.ac.uk/v3`
- **Auth**: **Required** (free API key)
- **Rate limit**: 10 req/sec
- **Returns**: Full-text open access papers, metadata
- **Package**: `httpx` (direct API)
- **Key**: Register at https://core.ac.uk/services/api

### OpenAlex

- **API**: `https://api.openalex.org`
- **Auth**: Optional (free API key for polite pool)
- **Rate limit**: 10 req/sec (polite pool)
- **Returns**: Paper metadata, abstracts (inverted index format), citation data
- **Package**: `httpx` (direct API)
- **Key**: Register at https://openalex.org/users/me

---

## Statistical / Government Data Sources

### U.S. Census Bureau

- **API**: `https://api.census.gov/data`
- **Auth**: **Required** (free API key)
- **Rate limit**: 500 req/day
- **Returns**: ACS, decennial census, economic data by geography
- **Package**: `httpx` (direct API)
- **Key**: Request at https://api.census.gov/data/key_signup.html

### FRED (Federal Reserve Economic Data)

- **API**: `https://api.stlouisfed.org/fred`
- **Auth**: **Required** (free API key)
- **Rate limit**: 120 req/min
- **Returns**: Economic time series (GDP, unemployment, inflation, etc.)
- **Package**: `httpx` (direct API)
- **Key**: Request at https://fred.stlouisfed.org/docs/api/api_key.html

### ClinicalTrials.gov

- **API**: `https://clinicaltrials.gov/api/v2`
- **Auth**: None
- **Rate limit**: No official limit (be respectful)
- **Returns**: Trial metadata, status, outcomes, investigator info
- **Package**: `httpx` (direct API)

### OECD

- **API**: `https://sdmx.oecd.org/public/rest` (SDMX)
- **Auth**: None
- **Rate limit**: No official limit
- **Returns**: International statistical data (health, education, economics)
- **Package**: `httpx` (direct API)

### data.gov

- **API**: `https://catalog.data.gov/api/3` (CKAN)
- **Auth**: None
- **Rate limit**: No official limit
- **Returns**: U.S. federal open data catalog — dataset metadata and resource URLs
- **Package**: `httpx` (direct API)

---

## Authentication Summary

| Source | Auth Required | Env Variable |
|--------|:---:|---|
| Semantic Scholar | No (optional) | `S2_API_KEY` |
| PubMed | No (optional) | `PUBMED_API_KEY` |
| arXiv | No | — |
| CrossRef | No | — |
| CORE | **Yes** | `CORE_API_KEY` |
| OpenAlex | No (optional) | `OPENALEX_API_KEY` |
| Census | **Yes** | `CENSUS_API_KEY` |
| FRED | **Yes** | `FRED_API_KEY` |
| ClinicalTrials.gov | No | — |
| OECD | No | — |
| data.gov | No | — |
