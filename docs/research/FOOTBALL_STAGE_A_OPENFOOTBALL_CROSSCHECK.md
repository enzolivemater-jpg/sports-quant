# EPL Stage A — OpenFootball Cross-Source Verification

Date: 2026-09-22

Status: VERIFIED_RESEARCH_EVIDENCE__NO_F4_APPROVAL

## Purpose

Cross-check the Stage A EPL 2024/25 fixture identity manifest against an independent zero-cost results source before spending historical-odds quota.

Sources compared:

1. SPORTS QUANT Stage A fixture manifest:
   `data/manifests/football_odds_stage_a_epl_2024_25_fixtures.json`

2. OpenFootball:
   repository `openfootball/england`
   path `2024-25/1-premierleague.txt`
   observed blob SHA:
   `ca0fe4923f0164d0f879f796ab0759253e13bc06`

## Verified source coverage

OpenFootball parser-equivalent probe observed:
- 380 EPL 2024/25 completed match records;
- 40 records across Matchweeks 1–4;
- Stage A manifest contains 40 fixtures across Matchweeks 1–4.

## Reconciliation basis

Comparison dimensions:
- matchweek;
- local calendar date;
- local kickoff time;
- home team identity key;
- away team identity key.

OpenFootball club labels were translated only through the explicit research alias map:

`data/manifests/football_openfootball_stage_a_aliases.json`

No fuzzy matching was used.

No canonical SPORTS QUANT entity IDs were assigned.

## Result

For the 40 Stage A fixtures:

- matchweek mismatches: 0
- local kickoff mismatches: 0
- home-team identity mismatches: 0
- away-team identity mismatches: 0
- OpenFootball labels without an explicit alias: 0
- total fixture mismatches: **0 / 40**

Result:
**VERIFIED_PASS**

## Why this matters

The paid historical-odds Stage A probe can use the existing 40-fixture manifest with stronger confidence that:
- fixture identities are internally coherent;
- kickoff groups are cross-source consistent;
- official-source naming can be reconciled to an independent results source without fuzzy matching;
- baseline result labels can later be cross-checked independently.

This reduces the chance of spending odds quota on a bad fixture manifest.

## PIT limitation

This verification does **not** establish historical `known_at`.

OpenFootball's current repository state does not prove:
- when an original fixture was first published;
- when a kickoff reschedule became public;
- when a correction was first available.

Therefore this evidence is suitable for:
- historical result labels;
- prior-match sporting-history research;
- fixture identity cross-checks.

It is not suitable by itself for:
- historical mutable context;
- historical schedule publication chronology;
- bookmaker market state.

## Governance impact

This verification:
- does not resolve OD-24;
- does not authorize The Odds API spend;
- does not authorize F4;
- does not create canonical team/event IDs;
- does not authorize F5 modeling before the phase gates.

It strengthens Stage A research readiness only.
