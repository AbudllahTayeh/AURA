Here is the updated `README.md` for the team. It is stripped down to the exact commands and rules the six of you need to develop AURA moving forward.

Copy this text and replace your current `README.md` file with it, then commit and push it to `main`.

```md
# AURA 
**Autonomous Research & Decision Intelligence Platform**

AURA is a multi-agent system designed to autonomously plan, research, retrieve, and synthesize information using LangGraph, FastAPI, and a robust local infrastructure stack.

---

## 🛠 Tech Stack
*   **Orchestration:** LangGraph / LangChain
*   **API:** FastAPI
*   **Databases:** PostgreSQL (Relational), Qdrant (Vector / RAG), Redis (Caching / Memory)
*   **Infrastructure:** Docker Compose

## 🚀 Local Setup (For All Team Members)

**Prerequisites:** You must have Python 3.12+ and Docker Desktop installed. Windows users must run this inside WSL2 (Ubuntu).

**1. Clone the repository**
```bash
git clone <your-github-repo-url>
cd AURA

```

**2. Set up the Python environment**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

```

**3. Configure Environment Variables**
Copy the example environment file and ensure the passwords match the local Docker setup.

```bash
cp .env.example .env
# Open .env and ensure POSTGRES_PASSWORD is set to 'pass'

```

**4. Start the Local Infrastructure**
This creates your isolated databases.

```bash
docker compose up -d

```

**5. Start the API**

```bash
fastapi dev apps/api/main.py

```

Test the setup by visiting: `http://127.0.0.1:8000/health`. You should see `{"status": "ok"}` for PostgreSQL, Redis, and Qdrant.

---

## 💻 Development Workflow

With six developers, strict Git rules apply to prevent breaking the local environments.

**1. Branching**

* Never push directly to `main`.
* Always pull the latest `main` before creating a branch.
* Use standard feature naming: `feature/planner-agent`, `feature/hybrid-retrieval`, `bugfix/api-connection`.

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

```

**2. Linting and Formatting**
We use `ruff` to enforce a unified coding style. Code will not merge if `ruff` fails.

```bash
# Check for errors
ruff check .

# Automatically fix formatting errors
ruff check . --fix

```

**3. Testing**
We use `pytest` for integration and unit testing. Run this locally before pushing.

```bash
pytest

```

**4. Pull Requests (CI/CD)**
When your feature is complete, push your branch and open a Pull Request on GitHub.

* The GitHub Actions CI pipeline will automatically run `pytest` and `ruff`.
* Both checks must pass (✅).
* At least one other team member must review and approve the PR before merging.

```

```
