![Lumen](asset/lumen_logo.svg)
> An interface-agnostic recommendation engine built on Pandas and Parquet. Features a streaming ETL pipeline, in-memory Bayesian scoring, and a Flask API fortified by a 3-layer security model utilizing bcrypt, self-verifying HS256 JWTs, and secure refresh tokens.

[![.github/workflows/ci.yml](https://github.com/bugra-ozer/lumen/actions/workflows/ci.yml/badge.svg)](https://github.com/bugra-ozer/lumen/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/v3.1%2B-3776AB?style=flat&logo=Flask&label=Flask)
![PostgreSQL](https://img.shields.io/badge/v18.4%2B-000000?style=flat&logo=PostgreSQL&label=PostgreSQL)
![Docker](https://img.shields.io/badge/v29.5.2%2B-000000?style=flat&logo=Docker&label=Docker)
![Pandas](https://img.shields.io/badge/v3.0%2B-000000?style=flat&logo=Pandas&label=Pandas)
![IMDB](https://img.shields.io/badge/Data-000000?style=flat&logo=IMDb)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)
---

## What is it?

Lumen is an intelligent movie recommendation engine designed to filter through thousands of titles and deliver tailored suggestions.

Powered by the public IMDb dataset, Lumen evaluates films using a Bayesian averaging algorithm—the same statistical methodology utilized by IMDb's Top 250 list. This approach corrects for vote-count bias, ensuring that statistically significant ratings (e.g., an 8.5 rating across 50,000 votes) appropriately outrank skewed outliers (e.g., a 9.0 rating with only 50 votes).

The core engine is served through a **Flask REST API** with JWT-based authentication, and allows users to dynamically query by genre and rating per request. Additionally, a Command Line Interface (CLI) is provided for local deployment and testing.

---

## Architecture

```
AppManager                        ← Orchestrates CLI vs API entry points
  └── AppService                ← Core business logic, interface-agnostic
        ├── DataContainer            ← DataFrame container
        │     └── DataPipeline    ← Load, merge, cache IMDB TSV
        │           └── DataLoader  ← business agnostic SQL read/write and file I/O
        ├── BayesianScorer           ← Bayesian scoring (scorer/bayesian_algorithm.py)
        ├── DataFilter           ← Filter and rank candidate DataFrame
        └── StateStore            ← Persist recommendation history (Parquet)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| API | Flask |
| Database | PostgreSQL, Flask-SQLAlchemy |
| Data processing | Pandas, PyArrow|
| Dataset | IMDB public TSV datasets |
| Authentication | PyJWT, bcrypt |
| CLI | Custom terminal UI |

### Dependencies

**Third-party:** Flask, PyJWT, bcrypt, pandas, pyarrow, requests, tqdm

**Standard library:** pathlib, gzip, json, logging, datetime, os

---

## ETL Pipeline

IMDB distributes its dataset as gzip-compressed TSV files. On first run, Lumen:

1. **Streams** the compressed files from IMDB using `requests` — no full download into memory
2. **Decompresses** on the fly with `gzip`
3. **Parses and merges** multiple TSV files into a single DataFrame with `pandas`
4. **Caches** the result as a Parquet file via `pyarrow` for fast subsequent loads

Progress is tracked with `tqdm`. On subsequent runs, the pipeline skips straight to loading from Parquet — significantly faster startup.

---

## API Endpoints

```
POST  /login            → Returns JWT access token + refresh token
POST  /refresh          → Exchanges refresh token for new access token
POST  /recommendations  → Returns scored, filtered movie list (protected)
GET   /health           → Service health check
```

All protected routes require `Authorization: Bearer <token>`.

---

## Auth Design

Three-layer security stack:

- **bcrypt** (cost factor 12) — password hashing. ~33 brute-force attempts/sec ceiling without rate limiting
- **JWT (HS256)** — self-verifying signed access tokens, 15-minute expiry, no DB lookup required per request
- **secrets.token_hex** — cryptographically random refresh tokens, 30-day expiry, server-side dictionary lookup

---

## Bayesian Scoring

Standard weighted rating formula:

$$Score = \left(\frac{v}{v + m}\right) r + \left(\frac{m}{v + m}\right) c$$

Where `v` = vote count, `m` = minimum votes threshold, `r` = movie average, `c` = global average. Scores are computed once at startup across the full dataset and held in memory.

---

## Folder Structure

```
lumen/
├── main.py               ← Core classes (DataContainer, AppService, AppManager...)
├── scorer/
│   └── bayesian_algorithm.py
├── persist/
│   └── state_store.py
├── api/
│   └── api.py            ← Flask server
├── downloader/
│   └── downloader.py     ← IMDB dataset streaming + decompression
├── ui/
│   └── cli.py
├── cons/
│   └── constants.py
├── config/               ← JSON config files
├── data/                 ← TSV (gitignored)
└── logs/
```

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/bugra-ozer/lumen
cd lumen

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env  # add your SECRET_KEY

# Run the API
python api/api.py

# Or run the CLI
python main.py
```

---

## Roadmap

- [ ] Rate limiting (Flask-Limiter)
- [ ] HTTPS (Flask-Talisman)
- [ ] OMDB API integration for live metadata
- [ ] OpenAPI / Swagger docs

---

## Author

**Bugra Ozer** — [github.com/bugra-ozer](https://github.com/bugra-ozer)
