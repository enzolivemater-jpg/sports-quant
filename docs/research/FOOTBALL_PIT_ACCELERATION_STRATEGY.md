# Football PIT Acceleration Strategy

Date: 2026-09-22

Status: RESEARCH_DESIGN__NO_F2_CODE

## Goal

Reach a valid Football model and paper-betting pipeline quickly without weakening point-in-time integrity.

The project must not wait for a mythical single vendor that perfectly reconstructs every historical injury, lineup, news item, statistic and bookmaker price with defensible publication timestamps.

Instead, use two data lanes.

## Lane A — Retrospective PIT-safe core

Purpose:
- train models;
- run walk-forward validation;
- calibrate;
- backtest;
- compare against historical market prices.

Initial feature classes should be limited to information that can be reconstructed without future leakage.

Examples:
- completed results prior to the decision cutoff;
- goals scored/conceded known before the fixture;
- rolling form computed exclusively from earlier matches;
- home/away splits computed exclusively from earlier matches;
- opponent-adjusted ratings derived only from prior events;
- Elo/Bradley-Terry style ratings updated sequentially;
- league-table state as reconstructible from prior results;
- historical bookmaker-odds snapshots with explicit observation timestamps.

Do not add historical injuries, lineups, coach/news context, or other mutable information unless the source provides a defensible as-of timestamp or immutable historical snapshot proving availability before the simulated cutoff.

### Market reconstruction

Current strongest candidate from reviewed documentation:
The Odds API.

Documented properties:
- historical snapshots for covered sports/bookmakers;
- featured-market history from 2020-06-06;
- 10-minute snapshot spacing historically;
- 5-minute spacing from September 2022;
- additional-market history from May 2023;
- paid historical access.

This temporal resolution must be modeled explicitly. A five-minute odds snapshot is not equivalent to continuous tick data.

## Lane B — Prospective context capture

Purpose:
- enrich live qualification and paper betting;
- build a genuinely point-in-time context dataset for future retraining.

Potential sources include Sportmonks, Sportradar, API-Football and official/trusted sources according to the canonical source hierarchy.

For every captured response retain at minimum:
- provider/source;
- external entity IDs;
- payload or content hash;
- provider timestamp if present;
- SPORTS QUANT received_at;
- canonical known_at and known_at_basis;
- ingestion version;
- quality/freshness/verification/conflict states.

Candidate context:
- official/expected lineups;
- injuries;
- suspensions;
- squad availability;
- manager/coach changes;
- weather;
- structured trusted news/context;
- odds movements if provider coverage is suitable.

## Why this is faster

A strict historical-context requirement can stall the project because many current APIs expose a player's current/historical status without proving when each old value first became knowable.

The two-lane design lets SPORTS QUANT:
1. validate the quantitative core on defensible historical data;
2. start paper betting;
3. accumulate its own immutable context snapshots;
4. later measure whether contextual features actually improve OOS calibration/skill.

This preserves the no-leakage rule while avoiding fabricated historical `known_at`.

## Football pilot dataset recommendation

For the earliest baseline, prefer a well-covered top domestic league and a period where historical odds snapshot quality is sufficient.

The competition is not canonically selected by this document.

Selection criteria:
- stable competition format;
- sufficient seasons and sample size;
- consistent team/entity IDs;
- high result/stat coverage;
- strong bookmaker coverage;
- low missingness;
- reconstructible pre-match feature state;
- usable odds timestamps.

Do not choose the pilot league based on perceived betting profitability.

## Provider-role hypothesis for bake-off

This is a hypothesis to test, not an OD-24 decision.

- The Odds API: historical market snapshot candidate.
- StatsBomb Open Data: event-feature research/prototyping candidate.
- Sportradar: premium comprehensive sports-data candidate.
- Sportmonks: broad single-API feature/context candidate.
- API-Football: lower-cost prospective/live context candidate; not suitable as sole long-history odds source because official docs describe seven-day pre-match odds retention.

## Acceptance evidence before OD-24 resolution

For each proposed provider role, collect concrete evidence for:
- supported competitions/seasons;
- timestamp fields and semantics;
- historical revision behavior;
- query reproducibility;
- missingness;
- entity stability;
- rate limits;
- cost;
- storage/derivative-use licensing;
- PIT failure modes.

No vendor should be approved only from marketing claims or endpoint breadth.
