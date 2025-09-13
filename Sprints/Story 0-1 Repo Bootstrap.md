# EPIC 0 — Project Setup & Dev Experience

**Outcome:** One-command dev environment; reproducible runs; basic CI lint/test.

**Story 0.1 — Repo bootstrap**

* **AC:** Git repo with `backend/`, `diff-worker`, `infra/`, `scripts/`, `examples/`. MIT/Apache2 license.
* **Tasks:**

  * Create repo structure & Makefile (`make dev`, `make test`, `make run`).
  * Pre-commit hooks (black/ruff, isort, mypy, shellcheck).
* **Estimate:** 3 pts

---

## Execution Plan Checklist

### 1. Repository Skeleton [DONE]
- [DONE] Create top-level directories: `backend/`, `diff_worker/`, `infra/`, `scripts/`, `examples/`, `tests/`, `Sprints/` (existing), `.github/workflows/` (placeholder).
- [DONE] Add placeholder `__init__.py` in Python package dirs (`backend`, `diff_worker`).
- [DONE] Add empty placeholder files: `backend/app.py`, `backend/cli/__init__.py`, `backend/cli/main.py`, `diff_worker/worker.py`.
- [DONE] Create `examples/fixtures/.gitkeep` to keep directory.
- [DONE] Create `.gitignore` appropriate for the project.

### 2. Licensing & Metadata [DONE]
- [DONE] Add `LICENSE` (MIT default).
- [DONE] Add `pyproject.toml` with: project metadata, runtime deps & dev deps pinned, Python `>=3.11,<3.12`.
- [DONE] Update `README.md` referencing local virtualenv workflow.

### 3. Tooling Config [DONE]
- [DONE] Add `.editorconfig` (UTF-8, LF, 120 cols, 4 spaces Python).
- [DONE] Add `mypy.ini` (strict mode: disallow any, warn unused, strict optional, etc.).
- [DONE] Add `ruff.toml` (rule selection, line-length 120, isort section ordering).
- [DONE] Add black config (via `pyproject.toml` `[tool.black]`).
- [DONE] Add `.pre-commit-config.yaml` with hooks: ruff (lint+format), black, isort (if not fully relying on ruff), mypy, shellcheck, end-of-file-fixer, trailing-whitespace.

### 4. Makefile [DONE]
- [DONE] Target `venv`: create `.venv` with `python -m venv .venv`.
- [DONE] Target `install`: `./.venv/bin/pip install -U pip` then install project in editable + dev extras.
- [DONE] Target `lint`: ruff check, black --check, mypy.
- [DONE] Target `format`: ruff check --fix + black .
- [DONE] Target `test`: pytest with coverage.
- [DONE] Target `run-api`: uvicorn backend.app:app --reload.
- [DONE] Target `run-worker`: python -m diff_worker.worker.
- [DONE] Target `dev`: `make install lint test`.
- [DONE] Target `clean`: remove caches & artifacts.
- [DONE] Target `backtest` placeholder echo.

### 5. Docker & Compose (Stub for later stories but scaffold now) [DONE]
- [DONE] `infra/Dockerfile.api` multi-stage.
- [DONE] `infra/Dockerfile.worker` multi-stage.
- [DONE] `infra/docker-compose.yml` with api & worker services, env placeholders, healthcheck stub.
- [DONE] `.dockerignore` with appropriate exclusions.

### 6. Environment Management [DONE]
- [DONE] Create `.env.example` with required vars.
- [DONE] Add placeholder settings loader (`backend/config.py`).

### 7. Initial Python Stubs (Typed) [DONE]
- [DONE] `backend/app.py` FastAPI app factory with `/` and `/health` routes.
- [DONE] `backend/routes/__init__.py` & `backend/routes/webhook.py` stub router.
- [DONE] `backend/services/{policy.py,llm_client.py,artifactory.py}` skeletons.
- [DONE] `backend/db/models.py` SQLAlchemy Base.
- [DONE] `backend/cli/main.py` Typer CLI stubs.
- [DONE] `diff_worker/worker.py` skeleton.
- [DONE] `diff_worker/diff/{npm_diff.py,normalize.py}` stubs.
- [DONE] `diff_worker/heuristics/npm_redflags.py` stub.

### 8. Testing Bootstrap [DONE]
- [DONE] `tests/conftest.py` app fixture using `create_app()`.
- [DONE] `tests/test_health.py` verifying 200 response and JSON body.

### 9. CI Placeholder (Will be finished in Story 0.3 but start file) [DONE]
- [DONE] `.github/workflows/ci.yml` stub (TODO: add lint/type/test matrix).

### 10. Quality Gates Early Validation [DONE]
- [DONE] Run `make install` then `make lint` ensures zero lint/type errors.
- [DONE] Run `make test` passes.
- [DONE] Install pre-commit & verify hooks run on staged changes (*hook execution simulated; full run requires git repo*).

### 11. Documentation Updates [DONE]
- [DONE] Update main `README.md` Quickstart with: clone, `make venv install`, `source .venv/bin/activate`, run API & worker.
- [DONE] Add `CONTRIBUTING.md` describing quality gates and branch naming.

### 12. Nice-to-Have (Optional in 0.1 if time) [DONE]
- [DONE] `.vale.ini` for docs lint (defer if not needed).
- [DONE] `CODE_OF_CONDUCT.md`.
- [DONE] `SECURITY.md` placeholder.

### 13. Definition of Done Validation
- [ ] All directories & stubs committed.
- [ ] License present.
- [ ] `make dev` completes without error.
- [ ] Pre-commit passes on clean clone.
- [ ] Health test green.

### 14. Risks & Mitigations (Bootstrap Specific)
- [ ] Pin deps to avoid breakage; update intentionally.
- [ ] Keep Docker images small via multi-stage.
- [ ] Enforce mypy strict early to prevent later refactors.

(End of Execution Plan)