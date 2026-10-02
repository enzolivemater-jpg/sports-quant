# F4 Historical Odds Leg — Explicit Evidence-Backed Block

Date: 2026-10-03

Status: EXPLICITLY_BLOCKED_WITH_EVIDENCE

Phase: F4_FOOTBALL_DATA_LAYER (issue #7)

OD-24: OPEN — this document approves no provider.

## What is blocked

The live ingestion leg for historical Phase 1 Football odds (`FOOTBALL_1X2`,
`FOOTBALL_TOTAL_GOALS_MAIN`). The F4 handoff accepts "one historical Phase 1 odds
source OR an explicit evidence-backed block" for the first milestone. This is that block.

## What is implemented instead

The canonical odds plumbing, end to end, without any provider call:

- `src/sports_quant/data/normalization/the_odds_api.py` — EXPERIMENTAL parser for the
  documented historical response shape (`timestamp`, `previous_timestamp`,
  `next_timestamp`, `data[]`); parses captured bytes only.
- `src/sports_quant/data/canonical/football.py` — `OddsObservationRecord` keyed by
  event, bookmaker, market, outcome and provider snapshot time.
- `src/sports_quant/data/ingestion/football.py` — mapping to Phase 1 markets, raw lineage,
  F3 `PitRecord`s; tested with SYNTHETIC payloads only (`tests/football_data/`).

No real odds are stored, generated or fabricated. The repository contains no code that
calls The Odds API from the data layer.

## Evidence for the block

1. **No legally/temporally suitable free historical odds source is in the repository.**
   - OpenFootball (CC0): results only; historical odds role `NOT_APPLICABLE`
     (`docs/research/FOOTBALL_OPENFOOTBALL_BASELINE_SOURCE_v0.1.md`).
   - StatsBomb Open Data: `VERIFIED_RESEARCH_SANDBOX`, no odds
     (`docs/research/STATSBOMB_OPEN_EPL_2015_16_PROBE.md`).
   - Football-Data.co.uk: not adopted; its usage notice excludes the required automated
     model-training use (`docs/research/FOOTBALL_OPENFOOTBALL_BASELINE_SOURCE_v0.1.md`).
   - API-Football: pre-match odds documented with seven-day retention; not a historical
     source (`docs/research/FOOTBALL_PROVIDER_EVIDENCE_MATRIX_v0.1.md`).
2. **The candidate historical source requires paid access that is not authorized.**
   The Odds API free plan excludes historical odds; Stage A requires a paid plan
   (`docs/research/FOOTBALL_ODDS_BAKEOFF_COST_PLAN_v0.1.md`,
   status `RESEARCH_PLAN__NO_PURCHASE_AUTHORIZED`). Issue #18: "No paid provider purchase
   is authorized by this issue"; the historical-enabled credential is obtained "only ...
   when Stage A spend is explicitly authorized". The Stage A runner is dry-run by default
   (`docs/research/FOOTBALL_ODDS_STAGE_A_RUNNER.md`).
3. **No credential exists in this environment, and none may be invented or committed.**
4. **The `known_at` mapping for odds snapshots is not approved.** Using
   `provider_snapshot_at` as `VERIFIED_SOURCE_AVAILABILITY` is explicitly
   `REQUIRES_BAKEOFF_VALIDATION`
   (`docs/research/FOOTBALL_ODDS_SNAPSHOT_SCHEMA_MAPPING_v0.1.md`). Until approved, F4
   assigns `SYSTEM_RECEIPT` only, so retrospectively retrieved odds would not be
   PIT-eligible at their historical cutoffs anyway.

## Unblock conditions

All of:
- explicit spend authorization for The Odds API Stage A (issue #18);
- a credential provided through the environment only;
- Stage A executed with the existing research runner and reconciled;
- a governed decision on the odds `known_at` mapping (provider snapshot semantics,
  correction behaviour), recorded before any historical odds become PIT-eligible;
- the main totals-line rule validated empirically (F4 maps a totals market to
  `FOOTBALL_TOTAL_GOALS_MAIN` only when it carries exactly one line).

None of these resolve OD-24 by themselves.
