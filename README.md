# AURA — Autonomous Research & Decision Intelligence Platform

> From questions to trusted decisions.

AURA is a multi-agent **Agentic RAG + Research + Decision Intelligence** platform. Instead of a single prompt → single answer flow, AURA plans a research task, breaks it into subtasks, runs specialized agents to gather and verify evidence, resolves conflicts between sources, compares alternatives, and produces a citation-grounded report with an explicit recommendation.

The core product promise:

> AURA does not simply generate an answer — it builds an evidence-backed answer and can explain where its conclusions came from.

---

## Table of Contents

1. [Project Description](#1-project-description)
2. [Environment Setup & Usage](#2-environment-setup--usage)

---

# 1. Project Description

## 1.1 What we are building

AURA takes a complex, open-ended research question — for example:

> "Compare Qdrant, Pinecone, and Weaviate for a production RAG application. Consider cost, self-hosting, scalability, filtering, developer experience, and retrieval capabilities. Recommend the best option for a small engineering team."

...and instead of answering it directly from model knowledge, it runs the question through an evidence-driven pipeline:

```text
User Question
   ↓
Understand Intent
   ↓
Plan Research (decompose into subtasks)
   ↓
Run Specialized Agents (parallel where possible)
   ↓
Retrieve from Knowledge Base + Web
   ↓
Rerank Evidence
   ↓
Verify Claims / Detect Conflicts
   ↓
Compare & Score Alternatives
   ↓
Produce Evidence-Grounded Recommendation
   ↓
Validate Citations
   ↓
Generate Report
   ↓
Store Research Memory
   ↓
Evaluate Quality

````

## 1.2 Architecture layers

```
┌─────────────────────────────────────────────────────────────┐
│ 1. EXPERIENCE LAYER      — Web UI / API / CLI               │
│ 2. ORCHESTRATION LAYER   — Planner / State / Routing        │
│ 3. AGENT LAYER           — Research / RAG / Verification /  │
│                             Decision / Memory               │
│ 4. KNOWLEDGE LAYER       — Parsing / Chunking / Embeddings /│
│                             Hybrid Search / Reranking       │
│ 5. TOOL LAYER            — Web / URL / Academic / DB tools  │
│ 6. DATA LAYER            — Qdrant / PostgreSQL / Redis      │
│ 7. QUALITY LAYER         — Tests / Evaluation / Monitoring  │
│ 8. INFRASTRUCTURE        — Docker / CI / Secrets / Logging  │
└─────────────────────────────────────────────────────────────┘

```

## 1.3 The agents

| **Agent**                       | **Responsibility**                                                                                                                                 |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Planner / Orchestrator**      | Intent understanding, task decomposition, routing, parallel execution, retries, re-planning                                                        |
| **Research Agent**              | Web search, URL reading, academic/documentation search, source ranking                                                                             |
| **RAG Agent**                   | Document ingestion, query rewriting, hybrid (dense + keyword) retrieval, reranking, adaptive retrieval — shared infrastructure used by every agent |
| **Verification Agent**          | Claim extraction, claim ↔ evidence mapping, contradiction detection, confidence scoring, citation validation                                       |
| **Decision Intelligence Agent** | Defines decision criteria, normalizes evidence, weighted scoring, trade-off analysis, generates a traceable recommendation                         |
| **Memory Agent**                | Short/long-term memory, research history, change detection between runs, scheduled/continuous research                                             |

**Rule that governs the whole system:** every recommendation must be traceable back to specific evidence and explicit, stated criteria — no unsupported claims reach the final report.

## 1.4 Advanced RAG pipeline

**Ingestion:** `Document → Parser → Structure Detection → Cleaning → Semantic Chunking → Metadata Extraction → Embedding → Index`

**Hybrid retrieval:**

```
                 User Query
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
Dense Retrieval               BM25 Retrieval
       │                           │
       └─────────────┬─────────────┘
                     ▼
               Score Fusion
                     ▼
                 Reranker
                     ▼
             Context Selection
                     ▼
                    LLM

```

**Adaptive retrieval:** after retrieving, AURA evaluates whether the evidence is sufficient; if not, it rewrites the query, retrieves again, and falls back to external web search if needed.

## 1.5 Techniques and stack

- **Agent orchestration:** LangGraph / LangChain


- **API:** FastAPI + Pydantic


- **Retrieval-Augmented Generation:** hybrid retrieval (dense embeddings via Sentence Transformers + BM25 keyword search), cross-encoder reranking, adaptive/iterative retrieval


- **Evidence verification:** claim extraction, entailment/support checking, conflict detection, citation-coverage checks


- **Decision intelligence:** weighted multi-criteria scoring and trade-off analysis


- **Databases:** PostgreSQL (system of record — users, sessions, tasks, agent runs, documents, claims, citations, reports, evaluation records), Qdrant (vector store for embeddings + metadata), Redis (caching, temporary state, job coordination)


- **Infrastructure:** Docker Compose, GitHub Actions CI (ruff + pytest), branch-protected `main`


- **Quality:** unit tests, integration tests (`tests/integration`), evaluation lab for retrieval/agent/citation quality


## 1.6 Goal

The goal isn't to build the largest possible system — it's to demonstrate, end-to-end, modern AI engineering practice: RAG, hybrid retrieval, agent orchestration, tool calling, planning/state management, evidence verification, citation grounding, decision support, long-term memory, backend engineering, databases, Docker, testing, evaluation, and CI/CD. The project is judged on **depth, reliability, and engineering quality**, not agent count.

### Current status

- **Phase 0 — Setup:** ✅ Completed. Local Docker infrastructure (PostgreSQL, Redis, Qdrant), modular FastAPI backend with async health checks for all three databases, GitHub Actions CI (ruff + pytest), branch protection on `main`.


- **Phase 1 — MVP RAG + Agent:** 📍 Current phase. Planner agent graph, research agent, basic RAG.


- **Later phases:** Verification + Citations → Decision Intelligence → Memory + Continuous Research → Production Quality → Advanced Extensions (multimodal RAG, knowledge graph integration, browser research tools).


# 2. Environment Setup & Usage

## 2.1 Prerequisites

- **Python 3.14+**


- **Docker Desktop** (or Docker Engine + Compose plugin on Linux)


- **Windows users:** run everything inside **WSL2 (Ubuntu)** — do not run natively on Windows.


- **Git**


## 2.2 Clone the repository

```
git clone https://github.com/AbudllahTayeh/AURA.git
cd AURA

```

## 2.3 Create the Python environment

```
python -m venv .venv
source .venv/bin/activate        # Windows (WSL2/Ubuntu): same command
pip install -e ".[dev]"

```

This installs the app (FastAPI, LangGraph, Qdrant client, psycopg, redis, sentence-transformers, transformers, rank-bm25, etc.) plus dev tools (`pytest`, `pytest-asyncio`, `ruff`, `mypy`).

## 2.4 Configure environment variables

```
cp .env.example .env

```

Open `.env` and ensure the PostgreSQL credentials match your `docker-compose.yml` exactly. The API reads them from `.env` while Docker reads them from the compose file:

```
POSTGRES_DB=aura
POSTGRES_USER=aura
POSTGRES_PASSWORD=pass

```

Other variables you may set:

```
APP_NAME=AURA
APP_ENV=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
REDIS_HOST=localhost
REDIS_PORT=6379
QDRANT_HOST=localhost
QDRANT_PORT=6333
LLM_PROVIDER=local
OPENAI_API_KEY=
HUGGINGFACE_TOKEN=

```

*(Note:* *`.env`* *is git-ignored; only* *`.env.example`* *is committed.)*

## 2.5 Start the local infrastructure (containers)

```
docker compose up -d

```

This starts three containers, defined in `docker-compose.yml`:

| **Service** | **Image**              | **Container name** | **Port(s)**    | **Purpose**                                                                      |
| ----------- | ---------------------- | ------------------ | -------------- | -------------------------------------------------------------------------------- |
| `postgres`  | `postgres:18`          | `aura-postgres`    | `5432`         | System of record (users, sessions, tasks, documents, claims, citations, reports) |
| `redis`     | `redis:8-alpine`       | `aura-redis`       | `6379`         | Caching, temporary state, job coordination                                       |
| `qdrant`    | `qdrant/qdrant:latest` | (default name)     | `6333`, `6334` | Vector store for embeddings + metadata                                           |

Check that all three came up healthy:

```
docker compose ps

```

Data persists across restarts in named volumes (`postgres_data`, `redis_data`, `qdrant_data`). To wipe everything and start fresh:

```
docker compose down -v

```

## 2.6 Start the API

```
fastapi dev apps/api/main.py

```

Verify everything is wired up correctly:

```
curl http://127.0.0.1:8000/health

```

Expected response once Postgres, Redis, and Qdrant are all reachable:

```
{
  "status": "ok",
  "services": {
    "postgres": "ok",
    "redis": "ok",
    "qdrant": "ok"
  }
}

```

If any service shows `"unavailable"`, the overall `status` will read `"degraded"` — double-check the container is running (`docker compose ps`) and that the corresponding host/port/credentials in `.env` are correct.

## 2.7 Repository layout

```
AURA/
├── apps/
│   └── api/
│       ├── core/config.py       # Pydantic settings, reads .env
│       ├── db/                  # postgres.py, redis.py, qdrant.py (clients + health checks)
│       ├── routes/               # API routes (add new endpoints here)
│       ├── services/             # business logic
│       ├── dependencies/         # FastAPI dependencies
│       └── main.py               # FastAPI app entrypoint, /health
├── agents/                       # planner, researcher, verifier, decision, memory agents
├── rag/                          # ingestion, retrieval, reranking
├── tools/                        # web search, URL reading, calculators, etc.
├── memory/                       # memory/continuous-research logic
├── evaluation/                   # evaluation lab / benchmarks
├── infrastructure/docker/        # extra docker assets
├── tests/
│   └── integration/test_health.py
├── .github/workflows/ci.yml      # CI: ruff + pytest on every PR to main
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── .gitignore

```

## 2.8 Development workflow

**Branching** — never push directly to `main`:

```
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

```

Naming convention: `feature/planner-agent`, `feature/hybrid-retrieval`, `bugfix/api-connection`.

**Linting/formatting** (Ruff):

```
ruff check .
ruff check . --fix

```

**Testing** (pytest, run before every push):

```
pytest

```

**Pull requests:**

- Push your branch and open a PR into `main`.


- GitHub Actions CI automatically runs `ruff check .` and `pytest`.


- Both checks must pass, and at least one teammate must review and approve before merging (branch protection is enforced on `main`).


## 2.9 Team rules

1. No "works on my machine" — everything must run through the documented setup above.


2. No ad-hoc dependency installs — add dependencies to `pyproject.toml` via a PR.


3. No direct pushes to `main` — always use feature branches + PRs.


4. Every feature needs tests and a code review before merge.


5. Keep agents bounded (clear inputs/outputs, retry limits, no unbounded loops).


**AURA — Smarter Research. Better Decisions.**
