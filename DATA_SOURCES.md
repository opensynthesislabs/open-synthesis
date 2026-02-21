# Data Sources

Open Synthesis integrates with 31 public APIs for corpus ingestion. Sources fall into four categories: **literature & preprints**, **biomedical & chemical**, **statistics**, and **government data**.

---

## Literature & Preprints

### Semantic Scholar

- **API**: `https://api.semanticscholar.org/graph/v1`
- **Auth**: Optional API key (higher rate limits)
- **Rate limit**: 100 requests / 5 min (unauthenticated)
- **Returns**: Paper metadata, abstracts, author info, citation graphs
- **Key**: Request at https://www.semanticscholar.org/product/api#api-key

### PubMed

- **API**: NCBI E-utilities (`esearch.fcgi`, `efetch.fcgi`)
- **Auth**: Optional API key (higher rate limits)
- **Rate limit**: 3 req/sec (unauthenticated), 10/sec with key
- **Returns**: Biomedical paper metadata, abstracts, MeSH terms; PMC full text for open access
- **Key**: Request at https://www.ncbi.nlm.nih.gov/account/settings/

### arXiv

- **API**: `https://export.arxiv.org/api/query` (Atom feed)
- **Auth**: None
- **Rate limit**: 3-second delay between requests
- **Returns**: Preprint metadata, abstracts, PDF links

### bioRxiv / medRxiv

- **API**: `https://api.biorxiv.org`
- **Auth**: None
- **Rate limit**: Not documented; reasonable use expected
- **Returns**: Biology and health science preprints with title, authors, abstract, DOI, category

### Europe PMC

- **API**: `https://www.ebi.ac.uk/europepmc/webservices/rest`
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: 40M+ life science articles, OA full-text, text mining annotations

### CrossRef

- **API**: `https://api.crossref.org/works`
- **Auth**: None (polite pool with `mailto` header)
- **Rate limit**: 50 req/sec with polite pool
- **Returns**: DOI resolution, bibliographic metadata, abstracts

### CORE

- **API**: `https://api.core.ac.uk/v3`
- **Auth**: **Required** (free API key)
- **Rate limit**: 10 req/sec
- **Returns**: Full-text open access papers, metadata
- **Key**: Register at https://core.ac.uk/services/api

### OpenAlex

- **API**: `https://api.openalex.org`
- **Auth**: Optional (free API key for polite pool)
- **Rate limit**: 10 req/sec (polite pool)
- **Returns**: Paper metadata, abstracts (inverted index format), citation data
- **Key**: Register at https://openalex.org/users/me

### Unpaywall

- **API**: `https://api.unpaywall.org/v2`
- **Auth**: Email parameter only
- **Rate limit**: <100K calls/day suggested
- **Returns**: OA status and direct PDF/HTML links for articles by DOI

### OpenCitations

- **API**: `https://opencitations.net/index/api/v2`
- **Auth**: None
- **Rate limit**: 180 req/min
- **Returns**: Citation graph (600M+ links), bibliographic metadata by DOI

### Springer Nature

- **API**: `https://api.springernature.com/meta/v2/json`
- **Auth**: **Required** (free API key)
- **Rate limit**: 100 req/min
- **Returns**: 14M documents, OA full-text for open access articles
- **Key**: Register at https://dev.springernature.com

### OpenAIRE

- **API**: `https://api.openaire.eu/search`
- **Auth**: None (token for higher limits)
- **Rate limit**: Not documented
- **Returns**: 170M+ European research publications with grant/funder linkage

### OSF Preprints

- **API**: `https://api.osf.io/v2/preprints` (JSON:API)
- **Auth**: None for public data
- **Rate limit**: Not documented
- **Returns**: Preprints from 25+ communities (PsyArXiv, SocArXiv, EarthArXiv, etc.)

### ClinicalTrials.gov

- **API**: `https://clinicaltrials.gov/api/v2`
- **Auth**: None
- **Rate limit**: No official limit (be respectful)
- **Returns**: Trial metadata, status, outcomes, investigator info

---

## Biomedical & Chemical

### OpenFDA

- **API**: `https://api.fda.gov`
- **Auth**: Optional API key (higher rate limits)
- **Rate limit**: 40 req/min (without key), 240/min (with key)
- **Returns**: Drug labels, adverse event reports, device recalls

### CDC Open Data

- **API**: `https://data.cdc.gov` (Socrata API)
- **Auth**: None
- **Rate limit**: Socrata default limits
- **Returns**: U.S. public health surveillance datasets

### PubChem

- **API**: `https://pubchem.ncbi.nlm.nih.gov/rest/pug`
- **Auth**: None (API key recommended)
- **Rate limit**: 5 req/sec, 400 req/min
- **Returns**: 115M compounds, bioactivity records, descriptions, toxicology

### ChEMBL

- **API**: `https://www.ebi.ac.uk/chembl/api/data`
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: 2.4M compounds, drug mechanisms, bioactivity assays

### Open Targets

- **API**: `https://api.platform.opentargets.org/api/v4/graphql` (GraphQL)
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: Drug-target-disease associations integrating GWAS, ChEMBL, clinical trials

### NCBI Gene

- **API**: NCBI E-utilities (`esearch.fcgi`, `esummary.fcgi` on `db=gene`)
- **Auth**: Optional API key (higher rate limits)
- **Rate limit**: 3 req/sec (unauthenticated), 10/sec with key
- **Returns**: Gene records, summaries, genomic annotations
- **Key**: Request at https://www.ncbi.nlm.nih.gov/account/settings/

### GWAS Catalog

- **API**: `https://www.ebi.ac.uk/gwas/rest/api`
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: 400K+ SNP-trait associations, ancestry data, genomic context

### WHO Global Health Observatory

- **API**: `https://ghoapi.azureedge.net/api` (OData)
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: 2,000+ indicators across 194 countries (mortality, disease burden, risk factors)

---

## Statistics & Government Data

### U.S. Census Bureau

- **API**: `https://api.census.gov/data`
- **Auth**: **Required** (free API key)
- **Rate limit**: 500 req/day
- **Returns**: ACS, decennial census, economic data by geography
- **Key**: Request at https://api.census.gov/data/key_signup.html

### FRED (Federal Reserve Economic Data)

- **API**: `https://api.stlouisfed.org/fred`
- **Auth**: **Required** (free API key)
- **Rate limit**: 120 req/min
- **Returns**: Economic time series (GDP, unemployment, inflation, etc.)
- **Key**: Request at https://fred.stlouisfed.org/docs/api/api_key.html

### OECD

- **API**: `https://sdmx.oecd.org/public/rest` (SDMX)
- **Auth**: None
- **Rate limit**: No official limit
- **Returns**: International statistical data (health, education, economics)

### World Bank

- **API**: `https://api.worldbank.org/v2`
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: 16K development indicators across 200+ countries

### Eurostat

- **API**: `https://ec.europa.eu/eurostat/api/dissemination`
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: EU demographics, economy, labor, health, environment statistics

### IMF

- **API**: `http://dataservices.imf.org/REST/SDMX_JSON.svc`
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: Global macroeconomic data (WEO, IFS, balance of payments, trade)

### UN SDG

- **API**: `https://unstats.un.org/sdgapi/v1`
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: Sustainable Development Goal indicators across 200+ countries

### data.gov

- **API**: `https://catalog.data.gov/api/3` (CKAN)
- **Auth**: None
- **Rate limit**: No official limit
- **Returns**: U.S. federal open data catalog — dataset metadata and resource URLs

### GBIF

- **API**: `https://api.gbif.org/v1`
- **Auth**: None
- **Rate limit**: Not documented
- **Returns**: 2.4B species occurrence records, taxonomic backbone, biodiversity datasets

---

## Authentication Summary

| Source | Auth Required | Env Variable |
|--------|:---:|---|
| Semantic Scholar | No (optional) | `S2_API_KEY` |
| PubMed | No (optional) | `PUBMED_API_KEY` |
| arXiv | No | — |
| bioRxiv / medRxiv | No | — |
| Europe PMC | No | — |
| CrossRef | No | — |
| CORE | **Yes** | `CORE_API_KEY` |
| OpenAlex | No (optional) | `OPENALEX_API_KEY` |
| Unpaywall | No (email only) | — |
| OpenCitations | No | — |
| Springer Nature | **Yes** | `SPRINGER_API_KEY` |
| OpenAIRE | No | — |
| OSF Preprints | No | — |
| ClinicalTrials.gov | No | — |
| OpenFDA | No (optional) | `OPENFDA_API_KEY` |
| CDC Open Data | No | — |
| PubChem | No | — |
| ChEMBL | No | — |
| Open Targets | No | — |
| NCBI Gene | No (optional) | `NCBI_API_KEY` |
| GWAS Catalog | No | — |
| WHO GHO | No | — |
| Census | **Yes** | `CENSUS_API_KEY` |
| FRED | **Yes** | `FRED_API_KEY` |
| OECD | No | — |
| World Bank | No | — |
| Eurostat | No | — |
| IMF | No | — |
| UN SDG | No | — |
| data.gov | No | — |
| GBIF | No | — |
