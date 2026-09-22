# F1 Validation Report

Phase: `F1 — Repository Skeleton`

Status: `BLOCKED_ON_ENVIRONMENT_VALIDATION`

## Implemented

- repository tree;
- Python packaging metadata;
- GitHub CI and security workflows;
- `.env` secret-handling convention;
- PostgreSQL local/test Compose plumbing;
- Alembic migration skeleton with no domain revisions;
- minimal structured JSON logging with OpenTelemetry trace/span correlation;
- unit/smoke tests and PostgreSQL integration smoke test;
- mechanical F1 scope validator.

## Actually executed

- `python -m compileall -q src scripts migrations tests` — PASS
- `pytest -q -m 'not integration'` — PASS, 4 passed
- `pytest -q -m integration` — SKIPPED, PostgreSQL URL not configured
- `alembic heads` — PASS, no domain revisions as expected in F1
- YAML parsing — PASS, 24 files
- TOML parsing — PASS
- wheel build with local setuptools — PASS
- `.env` ignore check — PASS
- high-signal local secret regex scan — PASS
- `git diff --check` — PASS

## Not successfully executed

### Dependency lock

`uv lock` failed because the execution environment could not resolve `pypi.org`.
No `uv.lock` was fabricated manually. The F1 scope validator therefore intentionally remains red on the missing lockfile.

### PostgreSQL integration

Docker is not available in the execution environment. The integration test exists but was skipped locally because no test database was available.

### Ruff / mypy

The binaries are not installed in the execution environment and cannot be resolved without package-index access. Their CI steps are defined but were not executed locally.

### Security workflow

GitHub Actions was not available locally, so Gitleaks and `pip-audit` were not executed.

## Scope check

No F2 contracts, point-in-time kernel, Tennis/Football models, market engine, calibration/P_safe implementation, dependency logic, optimizer logic, or frontend implementation was added.
