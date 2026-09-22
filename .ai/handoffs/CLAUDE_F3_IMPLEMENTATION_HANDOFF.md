# Claude Pro Handoff — F3 Point-in-Time Kernel

Date: 2026-09-22

Status: READY_AFTER_F2_ACCEPTANCE

Repository: `enzolivemater-jpg/sports-quant`
Implementation issue: #6
Pilot sport: FOOTBALL

## Start condition

Do not begin F3 unless:
1. F0 independent review gate is closed acceptably;
2. F2 is merged;
3. F2 CI/Security are green;
4. F2 critical contract review has no unresolved P0/P1;
5. current main is green.

If any condition is false: STOP.

## Primary spec

Implement exactly:
`docs/contracts/F3_POINT_IN_TIME_KERNEL_SPEC_DRAFT.md`

Also read:
- F2 contract implementation and tests
- `.project/FOUNDATION_DECISIONS_v0.1.yaml`
- `.project/OPEN_DECISIONS.yaml`
- `docs/research/FOOTBALL_PIT_ACCELERATION_STRATEGY.md`
- `docs/research/FOOTBALL_PILOT_DATASET_MANIFEST_v0.1.md`
- `docs/research/STATSBOMB_OPEN_EPL_2015_16_PROBE.md`

## Objective

Implement reusable, sport-agnostic deterministic point-in-time logic.

Football is the first consumer.

F3 must answer:
"Could this exact record/version legitimately have been used at this exact historical decision cutoff?"

## Must implement

- PIT eligibility
- as-of version selection
- validity-window enforcement
- deterministic historical revision selection
- snapshot/replay manifest
- explicit rejection reasons
- timezone-safe handling
- raw snapshot lineage hooks

## Hard invariant

Critical historical use requires:

`known_at <= decision_cutoff_at`

Missing defensible `known_at` must not silently become eligible.

## Critical revision behavior

If V1 was known before cutoff and V2 was corrected after cutoff:
- replay before correction returns V1
- replay must never return V2

If only V2 exists today and no defensible V1 historical version exists:
- historical reconstruction for that mutable field is not valid.

## Do not implement

- provider fetching
- Football feature engineering
- model training
- no-vig
- P_safe
- S-Tier
- optimizer
- frontend

## Required tests

At minimum:
- known_at < cutoff
- known_at == cutoff
- known_at > cutoff
- missing known_at critical rejection
- naive datetime rejection
- valid_from after cutoff rejection
- expired record rejection
- multi-version as-of selection
- later correction cannot leak backward
- deterministic replay
- current-state-only provider data cannot masquerade as historical
- DST/offset regression
- conflict/quality blocking semantics
- complete snapshot manifest
- regression test for every future leakage defect

## Design constraints

- domain layer only
- no FastAPI dependency
- no frontend dependency
- no provider-specific shortcuts
- no duplicated/weaker PIT logic inside adapters
- prefer small explicit pure functions/services where practical
- preserve deterministic reason codes

## Completion

F3 may be proposed as TECHNICALLY_GREEN only when:
- all PIT/revision/replay tests pass
- CI/Security pass
- deterministic replay is demonstrated
- no speculative timestamps are introduced
- no F4+ ingestion/model logic leaks in
- independent critical review requested

Do not start F4 in the same PR.
