**Story 0.2 — Containerization & env**

Goal: Reproducible container images (API + worker) runnable together via a single `docker compose up`, with correctly injected environment variables and documented configuration.

**Acceptance Criteria (AC):**
1. `docker compose up` (no extra flags) starts: api, worker (and an optional supporting service if needed, e.g., ephemeral cache) and both reach healthy state.
2. `.env.example` contains and documents: `LLM_PROVIDER`, `LLM_API_KEY`, `ARTIFACTORY_URL`, `API_TOKEN`, `POLICY_THRESHOLD` plus any new vars introduced (LOG_LEVEL, etc.).
3. API container responds 200 on `/health` from host (curl to mapped port) after compose reports healthy.
4. Worker container starts successfully and logs a startup message (placeholder loop OK).
5. Images are multi-stage, slim (< ~250MB each uncompressed target stage if feasible) and do not include build toolchain unnecessary at runtime.
6. Non-root execution inside containers (drop privileges) unless a blocker is documented.
7. Config settings in `backend/config.py` sourced from environment (with defaults) with no mypy regressions.
8. Makefile has convenient targets: `docker-build`, `docker-run-api`, `compose-up`, `compose-down`, `compose-logs`.
9. Basic container lint (hadolint) optionally integrated or deferred with documented rationale.

**Estimate:** 3 pts

---

## Execution Plan Checklist

### 1. Repository Prep [DONE]
- [DONE] Confirm existing `infra/Dockerfile.api` & `infra/Dockerfile.worker` baseline state.
- [DONE] Add/verify `.dockerignore` excludes: `.venv`, `__pycache__`, `*.pyc`, `.mypy_cache`, `.ruff_cache`, `.git`, `tests/__pycache__`, `dist`, `build`.

### 2. Base Image & Multi-Stage Strategy [DONE]
- [DONE] Choose base: `python:3.11-slim` for both stages.
- [DONE] Stage names: `builder` (install build deps, compile wheels) -> `runtime` (copy wheels/site-packages + source minimal).
- [DONE] Use `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` envs.
- [DONE] Install build essentials (`build-essential`, `gcc`) only in builder stage; omit from runtime.

### 3. Node / Diff Tooling Integration
- [ ] Decide minimal Node install approach: Debian package (`nodejs`) or `corepack enable` if we later need pnpm; keep simple now.
- [ ] Install Node only in worker image (unless API later needs it) to minimize API image size.
- [ ] Document reason for Node dependency in file header comment (used for npm package tarball diff).

### 4. Python Dependency Layer Optimization
- [ ] Export locked dependencies if needed (reuse `pyproject.toml` + `pip install .[dev]` in builder; runtime only prod deps via `pip install .`).
- [ ] Consider producing a `requirements.lock` (optional; may defer to later story) and note decision.
- [ ] Copy only necessary app directories (`backend`, `diff_worker`) + `pyproject.toml` into runtime.

### 5. API Dockerfile Implementation
- [ ] Implement multi-stage with build then runtime.
- [ ] Create non-root user (`appuser`) and switch in final stage.
- [ ] Set working directory `/app`.
- [ ] Expose port 8000 (FastAPI default in Makefile doc) or confirm chosen port.
- [ ] Entrypoint/CMD executes uvicorn via module: `uvicorn backend.app:app --host 0.0.0.0 --port 8000`.

### 6. Worker Dockerfile Implementation
- [ ] Mirror multi-stage pattern from API but include Node install.
- [ ] Non-root user also used.
- [ ] Provide CMD `python -m diff_worker.worker`.

### 7. docker compose Configuration
- [ ] Update/replace `infra/docker-compose.yml` with services: `api`, `worker`.
- [ ] Use build contexts pointing to repo root with Dockerfiles `infra/Dockerfile.api` & `infra/Dockerfile.worker`.
- [ ] Define `env_file: .env` for both services.
- [ ] Map API service port `8000:8000`.
- [ ] Add healthcheck for API: `curl -f http://localhost:8000/health || exit 1` with interval/retries.
- [ ] Add simple healthcheck for worker (e.g., python inline check writing a heartbeat file) or just a `CMD test` script placeholder.
- [ ] Define restart policy `unless-stopped` (optional) or leave default; document decision.

### 8. Environment Variables & .env.example
- [ ] Expand `.env.example` to include: `LLM_PROVIDER=`, `LLM_API_KEY=`, `ARTIFACTORY_URL=`, `API_TOKEN=`, `POLICY_THRESHOLD=0.75`.
- [ ] Add supporting vars: `LOG_LEVEL=info`, `WORKER_POLL_INTERVAL=5` (if used) with comments.
- [ ] Add comment header explaining copy pattern: `cp .env.example .env`.
- [ ] Ensure secrets are not committed (validated via `.gitignore`).

### 9. Config Loader Alignment
- [ ] Verify `backend/config.py` reads newly added env vars with sane defaults.
- [ ] Add any missing fields to `Settings` dataclass/pydantic model.
- [ ] Run mypy to ensure no new issues.
- [ ] Add test ensuring `POLICY_THRESHOLD` default applied when unset.

### 10. Makefile Enhancements
- [ ] Add `docker-build-api` & `docker-build-worker` targets.
- [ ] Add aggregate `docker-build` (depends on both).
- [ ] Add `docker-run-api` (local ephemeral) for quick test.
- [ ] Add `compose-up` & `compose-down` targets (with `--remove-orphans`).
- [ ] Add `compose-logs` streaming logs for both services.
- [ ] Ensure phony declarations updated.

### 11. Local Development Parity Docs
- [ ] Update `README.md` with container workflow section: build vs compose.
- [ ] Document environment variable usage & overriding via `docker compose run -e VAR=...`.
- [ ] Add note about non-root user and file permission considerations (volumes if later added).

### 12. Security & Image Hygiene
- [ ] Use `--no-cache-dir` in pip installs.
- [ ] Strip build deps from runtime stage (verify with `dpkg -l` optional or doc only).
- [ ] Ensure no secret ARGs left in layers.
- [ ] Run (optional) `hadolint` locally; if not added as dev dependency, document deferment.

### 13. Testing Containerization
- [ ] Build images locally and record resulting sizes (approximate) in Story file.
- [ ] `docker compose up --build -d` then curl health endpoint.
- [ ] Confirm worker logs expected startup message.
- [ ] (Optional) Exec into worker and run a placeholder diff function to ensure Node present.
- [ ] Add simple pytest invoking settings defaults inside a container (optional; may defer).

### 14. CI Enhancements (Optional This Story)
- [ ] (Optional) Add workflow step to build images on PR (API + worker) without push.
- [ ] (Optional) Add hadolint GitHub Action (document skip if omitted to keep scope).

### 15. Definition of Done Validation
- [ ] `docker compose up` healthy API + worker.
- [ ] `.env.example` complete & documented.
- [ ] Makefile targets functional.
- [ ] Non-root containers confirmed (`id -u` != 0 inside running service).
- [ ] Health endpoint reachable from host.
- [ ] Story checklist updated to reflect completion.

### 16. Risks & Mitigations
- [ ] Image bloat risk: verify layer ordering (requirements before code) to leverage cache.
- [ ] Node supply chain risk: restrict to official Debian repo for now; future: pinned version.
- [ ] Secrets leakage risk: validate `docker history` does not expose secrets.
- [ ] Divergent dev vs prod config risk: ensure `.env.example` parity with compose.
- [ ] Startup race conditions: confirm worker does not depend on API readiness beyond network (document if needed).

---

Notes / Decisions Log (add as executed):
- (pending) Decision on hadolint inclusion.
- (pending) Decision on optional cache mount for pip (speed vs deterministic layering).

(End of Execution Plan)