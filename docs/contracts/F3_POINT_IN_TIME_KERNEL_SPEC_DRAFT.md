# F3 Point-in-Time Kernel — Draft Ready Specification

Date: 2026-09-22

Status: READY_TO_IMPLEMENT

## Objective

Implement a reusable point-in-time kernel that decides whether a record could legitimately have been used at a given decision cutoff.

F3 is sport-agnostic infrastructure. Football is the first consumer.

## Canonical inputs

The kernel must operate on F2 contracts and must never redefine them locally.

Required temporal fields:
- event_time
- published_at
- received_at
- valid_from
- valid_to
- expires_at
- known_at
- known_at_basis
- decision_cutoff_at

## Core rule

For decision-critical historical use:

`known_at <= decision_cutoff_at`

If `known_at` cannot be established defensibly, the record must not silently become PIT-eligible.

## Known-at basis

Initial canonical values are inherited from Foundation:
- SYSTEM_RECEIPT
- VERIFIED_SOURCE_AVAILABILITY

F3 may not invent additional canonical values without governance approval.

## Required operations

### 1. PIT eligibility check

Input:
- record temporal metadata
- decision_cutoff_at

Output:
- eligible: bool
- rejection reason(s)
- evaluated known_at
- evaluated known_at_basis

### 2. As-of selection

Given multiple versions of the same logical record:
- return the latest version that was legitimately known at or before cutoff;
- never use a revision first known after cutoff;
- preserve the selected source/version identity.

### 3. Validity-window check

If valid_from / valid_to / expires_at exist:
- enforce them in addition to known_at;
- absence of optional validity boundaries must not create fake values.

### 4. Version selection

For mutable provider data:
- distinguish logical entity identity from source record version;
- retain revision lineage;
- allow deterministic replay at an old cutoff.

### 5. Snapshot manifest

Every PIT materialization must emit:
- decision_cutoff_at
- source snapshot/version references
- row count
- rejected-row count
- rejection reasons
- code version
- dataset/source version
- created_at
- deterministic content hash where feasible

## Required rejection reasons

At minimum:
- MISSING_KNOWN_AT
- KNOWN_AFTER_CUTOFF
- INVALID_TIMEZONE
- EXPIRED_AT_CUTOFF
- NOT_YET_VALID_AT_CUTOFF
- SOURCE_VERSION_UNRESOLVED
- CONFLICT_BLOCKING
- QUALITY_BLOCKING

Exact enum placement belongs to F2/F3 implementation review.

## Timezone policy

- timezone-aware timestamps only at domain boundaries;
- canonical storage should use UTC;
- provider-local timestamps must be converted explicitly;
- ambiguous daylight-saving timestamps must not be guessed.

## Revision semantics

Example:

A provider publishes value V1 at 10:00.
The match decision cutoff is 12:00.
Provider corrects it to V2 at 14:00.

A replay at 12:00 must return V1, not V2.

If the provider exposes only V2 today and there is no stored V1 or defensible historical revision feed, that field cannot be reconstructed for the 12:00 historical decision.

## Raw snapshot rule

Prospective ingestion should store immutable raw responses or legally permitted equivalents before normalization, together with:
- received_at
- source/provider
- endpoint/request identity
- payload/content hash
- ingestion version

This gives future backtests stronger known_at evidence.

## Football examples

### Historical odds

If a historical odds provider returns the snapshot at or before requested timestamp:
- provider snapshot time is candidate source-availability evidence;
- SPORTS QUANT still records retrieval lineage;
- the exact semantics are provider-specific and must be documented.

### Lineup

A final lineup cannot be used at T-6h unless a source proves it was officially available then.

### Injury

A player's injury start_date is not automatically publication time.
If historical publication timing is unavailable, use prospectively captured snapshots or exclude the feature retrospectively.

## APIs / interface design constraints

F3 should expose domain functions/services usable from:
- data materialization;
- backtesting;
- feature building;
- live decision evaluation.

It must not depend on FastAPI or frontend code.

## Required tests

1. known_at before cutoff -> eligible.
2. known_at equal cutoff -> eligible.
3. known_at after cutoff -> rejected.
4. missing known_at on critical record -> rejected.
5. naive datetime -> rejected.
6. validity begins after cutoff -> rejected.
7. record expired before cutoff -> rejected.
8. later revision cannot overwrite earlier historical replay.
9. as-of selector returns correct version among 3+ revisions.
10. deterministic replay produces same selected records and manifest hash.
11. provider data with current-state-only semantics cannot masquerade as historical.
12. DST/offset regression cases.
13. conflict/quality blocking behavior consistent with F2 contracts.
14. snapshot manifest is complete.
15. regression test for every leakage bug found later.

## Performance target

Correctness dominates speed.

For the initial Football pilot, PIT materialization only needs to be comfortably fast enough for batch walk-forward experiments and pre-match live evaluation.

Do not introduce distributed infrastructure during F3.

## Explicit non-goals

F3 does not:
- fetch providers;
- compute football features;
- fit models;
- calibrate probabilities;
- define P_safe;
- calculate no-vig;
- select bookmakers;
- implement backtest metrics.

## Acceptance

F3 is green only when:
- F2 contracts are green;
- PIT tests pass;
- mutation/revision tests pass;
- deterministic replay passes;
- no guessed historical timestamps exist;
- independent review finds no P0/P1 leakage flaw.
