# SPORTS QUANT

SPORTS QUANT is a selective sports decision-support system. Its default valid outcome can be `NO_BET`.

## Current implementation phase

- F0 — Governance canonicalization: implemented, pending independent critical review.
- F1 — Repository skeleton: current implementation scope.
- F2+ — NOT STARTED.

F1 contains repository structure, Python packaging, CI, secret-handling conventions, PostgreSQL local/test plumbing, an Alembic migration skeleton, and minimal structured observability only. It intentionally contains no probability model, no Basketball/Football/MMA-UFC engine, no optimizer, and no production `P_safe` formula.

## Non-negotiable boundaries

- C2 Decision Support only.
- No automated real-money wagering.
- No direct LLM assignment of final `P_safe`.
- No future information in backtests.
- Mandatory V1 sports: Basketball, Football and MMA; UFC is the mandatory initial MMA competition scope.
- Additional sports are admitted only through PIT-valid empirical Sport Predictability evidence; no optional sport is pre-approved.
- `NO_BET` is a native outcome.

## Local bootstrap

```bash
uv sync --all-groups
cp .env.example .env
make check
```

PostgreSQL local development:

```bash
make db-up
```

Ephemeral PostgreSQL test service:

```bash
make db-test-up
```

No production credentials belong in this repository.
