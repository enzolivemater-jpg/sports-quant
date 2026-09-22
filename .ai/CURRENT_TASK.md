# CURRENT TASK

Phase: `F1 — Repository Skeleton`

Status: `IMPLEMENTED_TECHNICALLY_GREEN__PROMOTION_BLOCKED_PENDING_INDEPENDENT_F0_REVIEW`

Implemented scope:
- repository tree;
- reproducible Python packaging with committed `uv.lock`;
- CI;
- secret handling;
- PostgreSQL local/test plumbing;
- migrations skeleton;
- minimal structured observability.

GitHub validation:
- final reference commit before this documentation update: `079099ddeac1e96d4943530690136008769a5465`;
- CI run `35728820181`: SUCCESS;
- Security run `35728820172`: SUCCESS;
- quality job: repository-scope validator, Ruff format, Ruff lint, mypy, unit/smoke tests, Alembic heads — all SUCCESS;
- PostgreSQL integration smoke test — SUCCESS;
- Gitleaks — SUCCESS;
- pip-audit — SUCCESS.

Resolved during F1 validation:
- generated the previously missing `uv.lock` using a temporary GitHub Actions bootstrap workflow;
- fixed Ruff import ordering;
- upgraded pytest after `pip-audit` identified `PYSEC-2026-1845`; current lock resolves pytest 9.1.1;
- temporary bootstrap workflow removed after lock generation.

Explicitly NOT STARTED:
- F2 contracts;
- point-in-time kernel;
- data ingestion business logic;
- Basketball/Football/MMA-UFC models;
- market/no-vig engine;
- calibration or production P_safe logic;
- dependency/optimizer logic;
- frontend implementation.

Governance note:
- this repository does NOT claim that F0 received an independent critical review;
- F1 implementation occurred before that canonical gate was satisfied;
- technical green status does not retroactively satisfy the governance gate;
- do not promote to F2 until the independent-review requirement is resolved under project governance.


Scope amendment recorded 2026-09-22:
- mandatory sports are Basketball, Football and MMA;
- UFC is the mandatory initial MMA competition scope;
- additional sports are evidence-gated by empirical Sport Predictability;
- Tennis is no longer a mandatory V1 sport;
- Basketball and MMA/UFC market-family catalogs remain intentionally undefined until their authorized decision phase.


Additional-sports scope decision recorded 2026-09-22:
- approved additional disciplines: Handball, Volleyball and Tennis only;
- Rugby Union, Futsal, Lacrosse, Roller Hockey and every other non-core sport are excluded from the current roadmap;
- approval means "allowed into empirical validation", not automatic SP validation or production promotion;
- no SP class is assigned until PIT-valid OOS evidence exists.
