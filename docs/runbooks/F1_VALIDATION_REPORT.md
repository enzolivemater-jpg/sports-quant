# F1 Validation Report

Phase: `F1 — Repository Skeleton`

Technical status: `GREEN`

Governance promotion status: `BLOCKED_PENDING_INDEPENDENT_F0_REVIEW`

## Implemented

- repository tree;
- Python packaging metadata;
- committed reproducible `uv.lock`;
- GitHub CI and security workflows;
- `.env` secret-handling convention;
- PostgreSQL local/test Compose plumbing;
- Alembic migration skeleton with no domain revisions;
- minimal structured JSON logging with OpenTelemetry trace/span correlation;
- unit/smoke tests and PostgreSQL integration smoke test;
- mechanical F1 scope validator.

## Initial local validation

Actually executed locally before GitHub publication:

- `python -m compileall -q src scripts migrations tests` — PASS;
- unit/smoke tests — PASS, 4 passed;
- YAML parsing — PASS;
- TOML parsing — PASS;
- Alembic skeleton validation — PASS;
- wheel build with local setuptools — PASS;
- `.env` ignore check — PASS;
- high-signal local secret regex scan — PASS;
- `git diff --check` — PASS.

Local environment limitations at that time:

- PyPI/DNS unavailable, so `uv.lock` could not be generated locally;
- Docker unavailable, so real PostgreSQL integration could not be executed locally;
- Ruff/mypy/pip-audit could not be fully executed locally without resolved dependencies.

Those limitations were later closed by GitHub Actions and are not represented as successful local checks.

## GitHub validation sequence

### First published run

Commit `988e75e5df0cf5bfd73dd8c2a06cd2f963a688b4` published the full F0/F1 tree.

CI/Security initially failed because `uv.lock` was absent. Logs explicitly reported:

`Unable to find lockfile at uv.lock, but --frozen was provided.`

Gitleaks already passed.

### Lockfile bootstrap

A temporary GitHub Actions workflow generated and committed `uv.lock`. The bootstrap workflow was then removed.

After lock generation, PostgreSQL integration passed, while two new actionable findings were exposed:

1. Ruff I001 in `scripts/validate_f1.py` — import ordering;
2. pip-audit identified `pytest 8.4.2` as affected by `PYSEC-2026-1845`, with fixed release `9.0.3`.

Both were corrected:
- imports reordered;
- pytest constraint changed to `pytest>=9.0.3,<10`;
- lockfile regenerated; current resolved pytest version is `9.1.1`;
- temporary lock bootstrap workflow removed again.

## Final GitHub validation

Reference commit: `079099ddeac1e96d4943530690136008769a5465`.

### CI run 35728820181 — SUCCESS

Quality job:
- checkout — SUCCESS;
- Python setup — SUCCESS;
- uv installation — SUCCESS;
- locked environment sync — SUCCESS;
- F1 repository-boundary validator — SUCCESS;
- Ruff format check — SUCCESS;
- Ruff lint — SUCCESS;
- mypy type check — SUCCESS;
- unit/smoke tests — SUCCESS;
- Alembic migration skeleton validation — SUCCESS.

PostgreSQL integration job:
- PostgreSQL service initialization — SUCCESS;
- locked environment sync — SUCCESS;
- PostgreSQL integration smoke test — SUCCESS.

### Security run 35728820172 — SUCCESS

- Gitleaks secret scan — SUCCESS;
- locked dependency sync — SUCCESS;
- pip-audit — SUCCESS.

## Scope check

No F2 contracts, point-in-time kernel, Tennis/Football model, market engine, calibration/P_safe implementation, dependency logic, optimizer logic, or frontend implementation was added.

## Governance caveat

Technical validation of F1 is complete, but F0 has not received the independent critical review required by the canonical governance. F1 implementation having occurred does not waive or retroactively satisfy that gate. Promotion to F2 remains blocked until that governance requirement is resolved.
