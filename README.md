# DiffGuard MVP — Project Guide

<!-- Badges -->
![CI](https://img.shields.io/github/actions/workflow/status/montj2/diff-guard/ci.yml?branch=master&label=CI)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/github/license/montj2/diff-guard)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)


> **Context for Copilot & contributors**
> **Stack:** Python 3.11, FastAPI API, worker for diffs, SQLite (SQLAlchemy), Pydantic v2, Typer CLI, requests w/ timeouts+retries, structlog for JSON logs.
> **Quality:** mypy (strict), ruff, black, pre-commit. Unit tests (pytest) for success/failure/edge.
> **Scope:** **npm + Artifactory only** for MVP. One LLM provider. Clear promote/quarantine policy.

---

## 1) Mission & Elevator Pitch

**Mission:** Stop poisoned open-source updates from entering enterprise repos.
**Pitch:** *DiffGuard* analyzes **semantic diffs** between package versions, uses an **LLM** to score safety (0–100) with **explainable reasoning**, and **gates promotion** inside Artifactory. It complements CVE scanners by catching **novel, obfuscated, or behavioral** changes.

---

## 2) MVP Goals (what we must demo)

* On **artifact upload** to **Artifactory staging**, DiffGuard:

  1. fetches current & previous **npm** tarballs,
  2. generates a **normalized diff**,
  3. gets an **LLM score + flags + reasoning (JSON)**,
  4. applies **policy** → **promote** to prod repo **or** **quarantine**,
  5. writes an **audit log** (SQLite) and **artifact properties** (score/flags).

**Definition of Done (MVP):**

* End-to-end demo: benign update auto-promoted; known malicious update quarantined.
* Logs and CLI show score, flags, and reasoning.
* Passes mypy/ruff/black; tests cover core modules.

**Explicit Non-Goals (MVP):**

* No PyPI/Maven, no Docker images, no multi-model ensembles, no SSO/UX dashboard.

---

## 3) Phases & Milestones

### Phase A — Foundations (Day 1–2)

* Repo bootstrap (FastAPI, worker, CLI, tests, pre-commit).
* Docker/Compose dev up in one command.
* CI: lint, mypy, tests.

### Phase B — Diff & Heuristics (Day 2–4)

* Fetch npm tarballs (Artifactory or public npm fallback).
* Produce unified diff (`npm diff` preferred; fallback unzip + `git diff --no-index`).
* Normalize/truncate; extract simple **red flags** (network/crypto/eval/base64/electron scripts).

### Phase C — LLM Scoring (Day 4–7)

* Single provider adapter (timeouts, retries, JSON-only schema).
* Prompt + few-shot; temperature ≤ 0.2.
* Pydantic validation and safe failure mode.

### Phase D — Policy & Actions (Day 6–8)

* YAML policy (thresholds; flag severities).
* Pure **decision engine** → **promote**/**quarantine**.
* Artifactory API: promote/move/set properties.

### Phase E — Persistence & UX (Day 8–11)

* SQLite models for artifacts/analyses.
* Typer CLI: list/show/export/review (manual override).

### Phase F — Backtests & Demo Polish (Day 11–14)

* 2 malicious + 8 benign fixtures; `make backtest` outputs precision/recall.
* `scripts/demo.sh` runs both benign/malicious paths.
* README quickstart + troubleshooting.

---

## 4) Architecture (MVP)

```
[Artifactory Staging] --webhook--> [FastAPI Ingest] -> enqueue
        |                                 |
        |                             [Worker]
        |                         Diff -> Normalize -> Heuristics
        |                               |           \
        |                               v            \
        |                           [LLM Scoring]    \
        |                               |             \
        |                            [Policy] ----> Decision
        |                               |                   \
        |              promote -> Artifactory (prod)     quarantine -> Artifactory (quarantine)
        |                               \____________________________/
                          [SQLite Audit Log] <--> [Typer CLI]
```

---

## 5) Interfaces & Schemas

### 5.1 Webhook (Artifactory → DiffGuard)

`POST /webhook/artifactory`

```json
{
  "repo": "npm-staging",
  "name": "event-stream",
  "version": "3.3.6",
  "path": "npm/event-stream/-/event-stream-3.3.6.tgz",
  "sha256": "abc...",
  "idempotency_key": "d2f3..."
}
```

**Response:** `202 Accepted` → `{ "enqueued": true, "analysis_id": "..." }`

### 5.2 LLM Output (validated)

```json
{
  "score": 0,
  "flags": ["adds_network_calls","uses_eval","obfuscation"],
  "reasoning": "New code adds outbound HTTP requests and eval-based loader in postinstall."
}
```

### 5.3 Policy (default YAML)

```yaml
thresholds: { promote: 90, review_min: 70 }
flags:
  adds_network_calls: critical
  uses_eval: high
  obfuscation: high
  crypto_addition: medium
decision:
  - if: "score >= thresholds.promote and not any(f in ['adds_network_calls','uses_eval','obfuscation'] for f in flags)"
    then: promote
  - if: "score >= thresholds.review_min"
    then: quarantine
  - else: quarantine
```

---

## 6) Repo Layout

```
/backend
  app.py                 # FastAPI app & wiring
  routes/webhook.py
  services/artifactory.py
  services/policy.py
  services/llm_client.py
  db/models.py
  cli/main.py            # Typer CLI
/diff_worker
  worker.py
  npm_diff.py
  normalize.py
  heuristics.py
/backtest
  runner.py
/examples/fixtures/...   # cached tgz or diffs (benign + malicious)
/infra
  Dockerfile, compose.yml, devcontainer.json
/scripts
  demo.sh, seed_fixtures.sh
tests/...
```

---

## 7) Dev Workflow

**Prereqs:** Docker, Python 3.11, Node 20 (optional locally).

```bash
# one-time
pip install pre-commit && pre-commit install

# run dev stack
docker compose up --build -d

# tests & quality
pytest -q
ruff check --fix .
black .
mypy .

# CLI usage (inside container)
python -m backend.cli list
```

**Env vars (`.env`)**

```
ARTIFACTORY_URL=
ARTIFACTORY_TOKEN=
STAGING_REPO=npm-staging
PROD_REPO=npm-prod
QUARANTINE_REPO=npm-quarantine
LLM_PROVIDER=openai
LLM_API_KEY=
POLICY_FILE=policy.yaml
```

---

## 8) Quality Bar (enforced)

* **mypy strict** (no `Any`, explicit return types).
* **ruff + black** (pre-commit).
* **Requests**: timeout=10s, 3 retries (exp backoff), `raise_for_status()`.
* **Pydantic**: all external I/O (webhook body, LLM JSON) validated.
* **Logs**: structlog JSON with `analysis_id`, `artifact`, `version`, `decision`.
* **Tests**: unit tests for core modules (diff, heuristics, policy, llm client), no live network.

---

## 9) Copilot Prompts (paste as needed)

**Project System Prompt (for Copilot Chat)**

> You are a senior Python engineer. All code must pass mypy strict, ruff, and black. Use Pydantic v2 for all I/O schemas, SQLAlchemy for SQLite, requests with timeouts+retries, structlog for JSON logging. Functions are small, typed, and tested with pytest. Implement modules for the DiffGuard MVP as defined in GUIDE.md. Prefer pure functions and explicit errors.

**Inline task (example: LLM client)**

```text
Implement LlmClient.score_diff(diff: str, meta: PackageMeta, heur: dict[str,int]) -> ScoringResult.
- Prompt (system+user), temperature=0.1, strict JSON.
- Validate JSON with Pydantic model: score 0..100, flags list[str], reasoning min len 10.
- 10s timeout, 3 retries with exponential backoff.
- On failure: return score=None, flags=["llm_error"], reasoning="..."
- Unit tests for valid JSON, malformed repaired, timeout path.
- mypy/ruff/black clean.
```

**Inline task (example: policy)**

```text
Create policy loader + decision engine.
- YAML schema via Pydantic; thresholds + flag severities.
- decide() is pure and deterministic.
- Rules: if score None -> quarantine; any critical flag -> quarantine; score>=promote and no high/critical -> promote; else quarantine.
- Tests: boundary scores, flags, missing score.
```

---

## 10) Backtesting (lite) & Metrics

* **Fixtures:** 2 malicious (e.g., `event-stream@3.3.6`), 8 benign popular libs.
* **Command:** `make backtest` → prints TP/FP/FN, precision/recall; writes CSV.
* **Goal (MVP):** Catch malicious fixtures; zero crashes; stable latency (<30s per analysis).

---

## 11) Demo Script (5 minutes)

1. Show `policy.yaml` and `GUIDE.md` scope.
2. Run stack: `docker compose up -d`.
3. **Benign upload** → webhook fires → **PROMOTE** (score \~90+).

   * Show CLI `diffguard list` and artifact props in Artifactory (`diffguard.score`).
4. **Malicious upload** → **QUARANTINE** (flags show network/eval/obfuscation).
5. `diffguard show <id>`: JSON reasoning.
6. Optional: `diffguard review <id> --approve` (manual override).

---

## 12) Roadmap After MVP (talk track, not scope)

* PyPI & Maven support; Docker images; queue + workers; model routing (heuristics → small LLM → large LLM).
* Enterprise dashboard; SSO; compliance packs (NIST SSDF / SLSA).
* On-prem inference; fine-tuned model on internal attack corpus.

---

## 13) Glossary

* **Artifact vending:** Publishing approved dependencies to internal repos.
* **Normalized diff:** Unified diff with noise removed (maps, minified bundles, docs).
* **Flags:** Heuristic or LLM-identified risk signals (e.g., `uses_eval`).
* **Promote/Quarantine:** Move/copy within Artifactory to production vs review repos.

---

## Quickstart (Local Dev)

```bash
# One-time setup
make venv
source .venv/bin/activate
make install  # installs runtime + dev deps
pre-commit install

# Run API (dev auto-reload)
make run-api

# Run worker (skeleton)
make run-worker

# All quality gates
make lint
make test

# Enforce minimum coverage (default 85%)
make test-strict
make test-strict COVERAGE_MIN=90  # override threshold

# Format code (ruff fix + black)
make format

# CLI usage
python -m backend.cli list
```

### Coverage Enforcement

The repository provides a `test-strict` Makefile target which adds `--cov-fail-under=$(COVERAGE_MIN)` (default 85). Override on demand:

```bash
make test-strict COVERAGE_MIN=90
```

To enforce locally before commit, you can uncomment the optional local pre-commit hook in `.pre-commit-config.yaml` (search for `pytest-strict-coverage`). CI can adopt the same by replacing the plain test step with `make test-strict COVERAGE_MIN=85`.


