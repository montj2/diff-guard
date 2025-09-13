Heck yes—let’s turn DiffGuard into a demo-able MVP. Below is a **ready-to-paste engineering backlog** (JIRA-style) with epics → stories → tasks, acceptance criteria, estimates, and a short demo script. It stays **narrow (npm + Artifactory)** and **shippable in \~2 sprints**.

---

# MVP Scope (what we will actually demo)

**Goal:** On npm package upload to an **Artifactory staging repo**, run a diff against the prior version, get an **LLM safety score + rationale**, and **auto-promote or quarantine** based on policy.
**Stack:** Python (FastAPI) microservice + Node CLI for diffs (`npm diff`) + SQLite for logs + simple CLI dashboard; containerized; GitHub Actions optional.

**Non-goals (MVP):** PyPI/Maven; Docker images; multi-model ensembles; SSO; fancy UI.

---

# Milestones

1. **M0 – Repo & Dev UX** (day 1–2)
2. **M1 – Diff Engine (npm)** (day 2–4)
3. **M2 – LLM Scoring Service** (day 4–7)
4. **M3 – Decision & Policy** (day 6–8)
5. **M4 – Artifactory Hook** (day 7–10)
6. **M5 – Audit Log & CLI Viewer** (day 8–11)
7. **M6 – Demo Data + Dry-Run Backtests (10–12)**
8. **M7 – Polish, Docs, Demo Script (12–14)**

> Target: **2-week sprint** for a crisp demo.

---

# EPIC 0 — Project Setup & Dev Experience

**Outcome:** One-command dev environment; reproducible runs; basic CI lint/test.

**Story 0.1 — Repo bootstrap**

* **AC:** Git repo with `backend/`, `diff-worker/`, `infra/`, `scripts/`, `examples/`. MIT/Apache2 license.
* **Tasks:**

  * Create repo structure & Makefile (`make dev`, `make test`, `make run`).
  * Add devcontainer (Python 3.11 + Node 20 + jq + bash).
  * Pre-commit hooks (black/ruff, isort, mypy, shellcheck).
* **Estimate:** 3 pts

**Story 0.2 — Containerization & env**

* **AC:** `docker-compose up` brings up API + worker; `.env.example` documented.
* **Tasks:**

  * Dockerfiles (slim), multi-stage for Python; node installed for diff.
  * Compose file; healthchecks.
  * `.env`: `LLM_PROVIDER`, `LLM_API_KEY`, `ARTIFACTORY_URL`, `API_TOKEN`, `POLICY_THRESHOLD`.
* **Estimate:** 3 pts

**Story 0.3 — CI baseline**

* **AC:** GH Actions run lint, type-check, unit tests on PR.
* **Tasks:** Set up workflow; cache deps; status badges.
* **Estimate:** 2 pts

---

# EPIC 1 — Diff Generation (npm)

**Outcome:** Given `package@newVersion`, produce a normalized diff vs previous version.

**Story 1.1 — Fetch artifacts**

* **AC:** Worker can fetch npm tarballs for `new` and `prev` from Artifactory (or npm registry for demo).
* **Tasks:**

  * Function `get_tarball(repo, name, version)` with Artifactory REST; fallback to public npm for demo.
  * Resolve `prev` via Artifactory metadata or package.json dist-tags.
* **Estimate:** 3 pts

**Story 1.2 — Produce diff**

* **AC:** `npm diff name@prev name@new` or tarball unzip + `diffoscope` path; returns unified diff text.
* **Tasks:**

  * CLI wrapper with timeouts & max output size (e.g., 200KB cap).
  * Fallback to file-by-file `git diff --no-index`.
* **Estimate:** 3 pts

**Story 1.3 — Diff normalization**

* **AC:** Noise filters reduce false positives (e.g., whitespace, lockfile hash churn, build artifacts).
* **Tasks:**

  * Strip whitespace-only changes; ignore `dist/`, `*.map`, `*.min.js`, `CHANGELOG.md`, `*.md` (configurable).
  * Limit per-file hunk length; top-N suspicious hunks only (config).
* **Estimate:** 3 pts

**Story 1.4 — Red-flag pre-parser (heuristics)**

* **AC:** Extract basic signals (e.g., added `child_process`, `net`, `http(s)`, `crypto`, `fs`, `eval`, base64 patterns).
* **Tasks:** Regex/AST sniffing; output `flags: ["adds_network_calls", "uses_eval"]` + counts.
* **Estimate:** 3 pts

---

# EPIC 2 — LLM Scoring Service

**Outcome:** API accepts diff + metadata → returns `{score, reasoning, flags}`.

**Story 2.1 — Prompt contract**

* **AC:** Single prompt template with JSON-only reply schema.
* **Tasks:** Template:

  ```
  System: You are a software supply chain security reviewer. 
  Task: Analyze this code diff for malicious or anomalous behavior.
  Consider: added network/FS/crypto, obfuscation, eval/dynamic require, suspicious lifecycle scripts, added telemetry, unrelated functionality.
  Output strictly as JSON: {"score": 0-100, "flags": string[], "reasoning": string}
  ```

  * Include few-shot examples: benign patch vs malicious backdoor.
* **Estimate:** 2 pts

**Story 2.2 — Provider adapter**

* **AC:** `llm_client.score_diff(diff, metadata, heuristics)` works for one provider (OpenAI/xAI/compatible).
* **Tasks:** HTTP client; retries; 30s timeout; token/length guards; cost/latency logging.
* **Estimate:** 3 pts

**Story 2.3 — Safety & determinism**

* **AC:** Temperature 0–0.2; enforce JSON with regex repair if needed; validate schema.
* **Tasks:** JSON schema; auto-repair; reject if invalid.
* **Estimate:** 2 pts

---

# EPIC 3 — Decision & Policy Engine

**Outcome:** Convert score+flags into promote/quarantine decision with a policy file.

**Story 3.1 — Thresholds & rules**

* **AC:** Default policy: `score >= 90 → promote`, else quarantine; override to require `score>=80 AND no critical flags`.
* **Tasks:** YAML policy (thresholds; flag severity map); evaluator module; unit tests.
* **Estimate:** 3 pts

**Story 3.2 — Human-in-the-loop**

* **AC:** Manual override via CLI: approve/reject a quarantined item.
* **Tasks:** CLI `diffguard review <analysis_id> --approve/--reject`.
* **Estimate:** 2 pts

---

# EPIC 4 — Artifactory Integration (staging→production)

**Outcome:** Webhook triggers analysis; API promotes or quarantines.

**Story 4.1 — Webhook endpoint**

* **AC:** `POST /webhook/artifactory` accepts minimal payload: name, version, repo, path, sha.
* **Tasks:** FastAPI route; HMAC/API key auth; idempotency key; 200 OK fast and enqueue job.
* **Estimate:** 3 pts

**Story 4.2 — Promotion action**

* **AC:** On “promote”, move/copy artifact from staging→production repo via Artifactory REST; set properties.
* **Tasks:** Artifactory client wrapper; set props: `diffguard.score`, `diffguard.flags`, `diffguard.reason`.
* **Estimate:** 3 pts

**Story 4.3 — Quarantine flow**

* **AC:** On “quarantine”, tag artifact `quarantine=true` and move to `staging-quarantine` repo (or keep and set prop).
* **Tasks:** REST calls; Slack/email webhook placeholder (optional).
* **Estimate:** 2 pts

---

# EPIC 5 — Persistence & CLI Viewer

**Outcome:** SQLite audit log + simple CLI to inspect results.

**Story 5.1 — Data model**

* **AC:** SQLite tables with indexes:

  * `artifacts(id, name, version, repo, sha, created_at)`
  * `analyses(id, artifact_id, score, flags_json, reasoning, policy_decision, created_at, provider_latency_ms, token_count)`
* **Tasks:** Alembic or simple migration script; CRUD helpers.
* **Estimate:** 3 pts

**Story 5.2 — CLI**

* **AC:** `diffguard list`, `diffguard show <id>`, `diffguard tail` (follow analyses), `diffguard export <id>.json`.
* **Tasks:** Typer/Click CLI; formatting; exit codes.
* **Estimate:** 3 pts

---

# EPIC 6 — Backtesting Harness (lite)

**Outcome:** Run a small library of historical diffs through the pipeline.

**Story 6.1 — Fixtures**

* **AC:** `examples/fixtures/` with 6–10 known cases (2 malicious, 8 benign); store `prev.tar.gz` + `new.tar.gz` or captured diffs.
* **Tasks:** Scripts to pull from public registry by version; cache locally.
* **Estimate:** 2 pts

**Story 6.2 — Runner & metrics**

* **AC:** `make backtest` prints TP/FP/FN, precision/recall; saves CSV.
* **Tasks:** Python script reading fixtures → pipeline → metrics.
* **Estimate:** 3 pts

---

# EPIC 7 — Observability & Guardrails

**Outcome:** Logs, metrics, and basic safeguards.

**Story 7.1 — Structured logging**

* **AC:** JSON logs; request ids; correlation ids; log levels env-configurable.
* **Estimate:** 2 pts

**Story 7.2 — Rate & size limits**

* **AC:** Reject diffs > N KB (config); chunking fallback; concurrency limit env var.
* **Estimate:** 2 pts

**Story 7.3 — Secrets & auth**

* **AC:** No secrets in logs; env var loading; optional Vault path placeholder.
* **Estimate:** 2 pts

---

# EPIC 8 — Packaging the Demo

**Outcome:** One-command demo + clear docs.

**Story 8.1 — Demo script**

* **AC:** `scripts/demo.sh` that: spins services, posts a benign package, then a malicious one; prints decisions; shows CLI viewer.
* **Estimate:** 2 pts

**Story 8.2 — README & quickstart**

* **AC:** Top-level README: install, run, demo, policy tuning, troubleshooting.
* **Estimate:** 2 pts

---

## Architecture (MVP)

```
[Artifactory Staging] --webhook--> [FastAPI Ingest]
                                   | enqueue
                             [Worker: Diff -> Normalize -> Heuristics]
                                   | LLM score (provider adapter)
                                   v
                          [Policy Decision Engine]
                           | promote        | quarantine
                   Artifactory REST        Artifactory REST
                                   \ 
                                    \--> [SQLite Audit Log] <---> [CLI]
```

**Directory skeleton**

```
/backend
  app.py (FastAPI)         /diff_worker
  routes/webhook.py          worker.py
  services/artifactory.py    diff/npm_diff.py
  services/policy.py         diff/normalize.py
  services/llm_client.py     heuristics/npm_redflags.py
  db/models.py               backtest/runner.py
  cli/main.py
/infra
  Dockerfile, compose.yml, devcontainer.json
/scripts
  demo.sh, seed_fixtures.sh
/examples/fixtures/...
```

---

## API Contracts

### Webhook (Artifactory → DiffGuard)

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

**201/200** with `{ "enqueued": true, "analysis_id": "..." }`

### LLM scoring (internal function)

Input:

```json
{
  "package": {"name":"event-stream","version_new":"3.3.6","version_prev":"3.3.5"},
  "diff": "<unified-diff-truncated>",
  "heuristics": {"adds_network_calls": 2, "uses_eval": 1, "suspicious_encoding": 0}
}
```

Output:

```json
{
  "score": 14,
  "flags": ["adds_network_calls","uses_eval","behavioral_deviation"],
  "reasoning": "New version adds outbound HTTP calls and eval-based loader..."
}
```

---

## Policy (default YAML)

```yaml
thresholds:
  promote: 90
  review_min: 70
flags:
  adds_network_calls: critical
  uses_eval: high
  obfuscation: high
  crypto_addition: medium
decision:
  - if: "score >= thresholds.promote and not any(flag in ['adds_network_calls','uses_eval','obfuscation'] for flag in flags)"
    then: promote
  - if: "score >= thresholds.review_min"
    then: quarantine
  - else: quarantine
```

---

## Prompts (MVP)

**System**

> You are a software supply chain security reviewer. Be precise and conservative.

**User**

> Analyze this code diff between versions {{prev}} → {{new}} of {{name}}. Identify indicators of malicious change: added network/FS/crypto calls, obfuscation, eval/dynamic require, suspicious lifecycle scripts (pre/postinstall), telemetry beacons, or unrelated functionality drift.
> Return strictly JSON: `{"score": 0-100, "flags": string[], "reasoning": string}`

**Few-shot benign**: small bugfix, no new imports, score \~95.
**Few-shot malicious**: adds `http.request`, base64 decode loader, score \~10–20.

---

## Testing Plan

**Unit**

* Diff normalizer drops whitespace-only changes.
* Heuristics fire on regex library of suspicious patterns.
* Policy evaluation for boundary scores (89/90).

**Integration**

* End-to-end: webhook → diff → LLM stub (fixture) → decision → Artifactory mock → SQLite log.
* Timeouts & large diffs (simulate 500KB, expect truncation).

**Backtest (lite)**

* 2 malicious (e.g., `event-stream@3.3.6`, `ua-parser-js@0.7.29` compromised variant).
* 8 benign (popular libs minor bumps).
* Report precision/recall; store CSV.

**Performance**

* Process ≤30s per artifact on laptop; cap LLM tokens; diff truncation tested.

---

## Risks & Mitigations (MVP)

* **LLM JSON wobble** → JSON schema validation + auto-repair; temp=0.1.
* **Huge diffs** → hunk truncation; top-K suspicious files only.
* **Provider outage** → retry/backoff; “review” fallback if scoring fails.
* **False positives** → start threshold at 90; allow manual approve; log for tuning.

---

## Demo Script (5 minutes)

1. **Start services**: `docker compose up -d`
2. **Show policy**: open `policy.yaml`.
3. **Benign run**: `scripts/demo.sh benign lodash 4.17.20→4.17.21`

   * Observe: CLI prints score \~95; promoted; Artifactory shows `diffguard.score=95`.
4. **Malicious run**: `scripts/demo.sh malicious event-stream 3.3.5→3.3.6`

   * Observe: score \~10–30; quarantined; flags list; reasoning.
5. **Audit**: `diffguard show <analysis_id>` → JSON reasoning; `diffguard review <id> --approve` (demonstrate override).

---

## JIRA Import-Ready Story List (compact)

* **DG-0** Repo bootstrap & devcontainer (3)
* **DG-1** Docker/compose & env (3)
* **DG-2** CI lint/type/test (2)
* **DG-3** Fetch npm tarballs (3)
* **DG-4** Generate unified diff (3)
* **DG-5** Normalize & truncate diff (3)
* **DG-6** Red-flag heuristics (3)
* **DG-7** LLM prompt & schema (2)
* **DG-8** Provider adapter + retries (3)
* **DG-9** Policy engine & YAML (3)
* **DG-10** Webhook endpoint + auth (3)
* **DG-11** Promote/quarantine via Artifactory REST (5)
* **DG-12** SQLite models & migrations (3)
* **DG-13** CLI: list/show/export/review (3)
* **DG-14** Backtest fixtures (2)
* **DG-15** Backtest runner & metrics (3)
* **DG-16** Structured logging & limits (4)
* **DG-17** Demo script & README (4)

> Total: \~52–56 pts (doable in 2 weeks for a focused single dev, or 1 week with 2 devs).

---

