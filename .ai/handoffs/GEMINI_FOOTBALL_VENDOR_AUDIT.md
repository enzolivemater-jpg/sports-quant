# Gemini Pro Handoff — Football Data / Vendor / Licensing Audit

Date: 2026-09-22

Status: READY_FOR_EXTERNAL_RESEARCH

Repository: `enzolivemater-jpg/sports-quant`
Related issues:
- #3 Football data-source bake-off for PIT readiness
- #5 Football pilot dataset — EPL samples and leakage controls

## Role

Gemini Pro is the external research / supplier / licensing / document-audit challenger.

Do NOT implement repository business code.

## Primary objective

Audit candidate Football data providers for the pilot stack and produce evidence for OD-24 without guessing.

Current candidates:
- The Odds API
- Sportradar Soccer
- Sportmonks Football
- API-Football
- StatsBomb Open Data (research sandbox role)

## Read first

- `docs/research/FOOTBALL_DATA_SOURCE_AUDIT_v0.1.md`
- `docs/research/FOOTBALL_PROVIDER_BAKEOFF_PLAN_v0.1.md`
- `docs/research/FOOTBALL_PROVIDER_EVIDENCE_MATRIX_v0.1.md`
- `docs/research/FOOTBALL_PIT_ACCELERATION_STRATEGY.md`
- `docs/research/FOOTBALL_PILOT_DATASET_MANIFEST_v0.1.md`
- `docs/research/FOOTBALL_FEATURE_GOVERNANCE_v0.1.md`
- `docs/research/STATSBOMB_OPEN_EPL_2015_16_PROBE.md`
- `.project/FOUNDATION_DECISIONS_v0.1.yaml`
- `.project/OPEN_DECISIONS.yaml`

## Mandatory audit dimensions

For each provider, verify from current official docs/terms where possible:

1. Football competition coverage.
2. Exact EPL historical season depth.
3. Fixture/results history.
4. Lineup history.
5. Injury/suspension history.
6. Historical odds depth and snapshot granularity.
7. Bookmaker coverage.
8. Timestamps exposed by endpoint.
9. Meaning of each timestamp.
10. Revision/correction semantics.
11. Whether historical versions remain retrievable.
12. Rate limits.
13. Current pricing.
14. Trial/free-tier constraints.
15. Raw-response storage rights.
16. Derived-model-use rights.
17. Redistribution/display restrictions.
18. Retention limits.
19. Commercial/personal-use distinctions if documented.
20. Known point-in-time failure modes.

## Point-in-time rule

A field is not considered historically usable merely because it exists today.

For every mutable field, distinguish:
- event occurrence time;
- publication time;
- provider update time;
- SPORTS QUANT receipt time;
- current/latest state.

Do not equate injury `start_date`, lineup event time, or current database state with historical `known_at`.

## Pilot sample

Use EPL 2024/25 as the common provider-bakeoff sample.

StatsBomb Open Data EPL 2015/16 remains only a free event-parser/features sandbox.

Do not change samples per provider merely to make a vendor look complete. Record coverage failure instead.

## Market sample

Football Phase 1 only:
- 1X2
- main total goals

Check candidate historical observations at:
- T-24h
- T-6h
- T-1h
- T-30m
- T-15m
- nearest defensible pre-kickoff snapshot

## Required output

Produce a provider comparison with:

- VERIFIED_FACT
- DOCUMENTED_BUT_UNTESTED
- UNKNOWN
- FAIL
- NOT_APPLICABLE

for each dimension.

Then provide:
- coverage matrix
- PIT-risk matrix
- licensing/storage matrix
- cost matrix
- integration-risk matrix
- recommended provider role(s)
- rejected roles with reasons
- unresolved questions
- exact source URLs/docs
- publication/access date
- whether OD-24 can be resolved

## Decision discipline

Do not declare a single vendor "best" globally.

Provider roles may differ:
- historical odds
- fixture/results
- event data
- prospective context
- premium production feed

A multi-source architecture is acceptable if PIT/provenance/entity resolution remain explicit.

If licensing language is ambiguous:
- mark UNKNOWN / NEEDS_LEGAL_REVIEW
- do not infer permission.

## Final status

Return one of:
- GO
- GO_WITH_CONDITIONS
- NO_GO
- NEEDS_DECISION

OD-24 must remain OPEN unless evidence is sufficient to justify a concrete provider-role decision.
