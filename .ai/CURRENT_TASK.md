# CURRENT TASK

Phase: `F1 — Repository Skeleton`

Status: `BLOCKED_ON_ENVIRONMENT_VALIDATION`

Implemented scope:
- repository tree;
- packaging;
- CI;
- secret handling;
- PostgreSQL local/test plumbing;
- migrations skeleton;
- minimal structured observability.

Validation blockers:
- `uv.lock` cannot be generated because PyPI/DNS access is unavailable in the execution environment;
- real PostgreSQL integration cannot be executed because Docker is unavailable;
- Ruff/mypy and GitHub security workflow cannot be executed locally without the missing tooling/network.

Explicitly NOT STARTED:
- F2 contracts;
- point-in-time kernel;
- data ingestion business logic;
- Tennis/Football models;
- market/no-vig engine;
- calibration or production P_safe logic;
- dependency/optimizer logic;
- frontend implementation.

Governance note: this repository does not claim that F0 received an independent critical review.
