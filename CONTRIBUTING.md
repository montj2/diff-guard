# Contributing to DiffGuard

Thanks for your interest in improving DiffGuard! This document describes the development workflow, quality bars, and guidelines for submitting changes.

## Branching & Workflow

1. Fork or create a feature branch from `main`.
2. Branch name format:
   - `feat/<short-purpose>` for new features
   - `fix/<short-purpose>` for bug fixes
   - `chore/<task>` for maintenance/tooling
   - `docs/<area>` for documentation-only
3. Keep changes focused; large refactors + features should be split.
4. Open a Pull Request early (draft) for feedback.

## Commit Style

Use conventional style (not strictly enforced yet):
```
feat: add policy engine thresholds
fix: handle missing diff gracefully
refactor: simplify LLM retry logic
chore: bump fastapi version
```

## Quality Gates (All Required)

Before pushing or opening PR:
- `make format` (auto-fixes ruff + black)
- `make lint` (must pass: ruff, black --check, mypy strict)
- `make test` (pytest green)
- Ensure pre-commit hooks installed: `pre-commit install`

CI runs the same gates.

## Adding Dependencies

- Prefer the standard library first.
- Pin with compatible release `~=`, avoid unbounded versions.
- If adding a heavy dep, justify in PR description.

## Code Style & Patterns

- Pure functions where practical (side effects isolated).
- All public functions & methods: explicit return types.
- No bare `except:`; catch the narrowest exception.
- Use Pydantic models for any external I/O (API payloads, LLM JSON, YAML configs).
- Use `structlog` (JSON) for runtime logging (TBD instrumentation scaffolding).
- Keep functions < ~40 lines; break apart complex logic.

## Testing Guidelines

Minimum per PR:
- New logic: add unit tests.
- Branch conditions: boundary cases for scores/flags.
- Avoid network calls (mock or fixture).
- Use factories/fixtures for repeated objects.

Coverage target will be introduced later; aim for critical path first.

## Policy & LLM Areas

- Policy evaluations must be deterministic and side-effect free.
- LLM client must validate JSON strictly and degrade safely: return `score=None` + `flags=["llm_error"]` on failure.

## Documentation

- Update README if user-facing behavior or setup changes.
- Add docstrings to new modules, especially service layers.

## Security Mindset

- Treat all external inputs as untrusted (validate & sanitize).
- Timeouts & retries for HTTP calls (default 10s, 3 attempts backoff).
- Avoid executing arbitrary code from artifacts; only parse diff text.

## PR Checklist (copy into description)

- [ ] Feature / Fix described clearly
- [ ] Tests added/updated
- [ ] `make format` executed
- [ ] `make lint` passes
- [ ] `make test` passes
- [ ] README / docs updated (if needed)
- [ ] No secrets or credentials committed

---

Questions? Open an issue or start a draft PR with commentary.

Happy diff-guarding!
