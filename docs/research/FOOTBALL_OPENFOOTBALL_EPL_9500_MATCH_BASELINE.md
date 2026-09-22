# OpenFootball EPL Multi-Season Baseline Verification

Date: 2026-09-22

Status: VERIFIED_RESEARCH_EVIDENCE__NOT_F4_DATASET

## Scope

Repository:
`openfootball/england`

Competition:
English Premier League

Completed seasons checked:
- 2000/01 through 2024/25
- 25 consecutive seasons

Machine manifest:
`data/manifests/football_openfootball_epl_2000_2025_verified.json`

## Result

Every inspected completed season contains:
- source header `# Matches 380`;
- 380 match records detectable under the observed Football.TXT formats.

Total verified baseline volume:

**25 × 380 = 9,500 EPL matches**

No season in the 2000/01→2024/25 range failed the count check.

## Reproducibility

The machine manifest freezes:
- season;
- source path;
- exact source blob SHA;
- detected match count;
- header match count.

This means later research can detect an upstream source revision instead of silently training on a moving dataset.

## Parser compatibility

Direct inspection found:
- legacy `home score away` format across older/recent historical files inspected through 2023/24;
- modern `home v away score` format in 2024/25.

The research parser now supports both formats and season-year rollover behavior.

See:
`docs/research/OPENFOOTBALL_FORMAT_COMPATIBILITY.md`

## Intended use

This 9,500-match corpus is suitable for preparing:
- sequential Elo/rating baseline research;
- Poisson/Dixon-Coles baseline research;
- result-label validation;
- team-name/entity-resolution research;
- chronological walk-forward plumbing.

It does **not** by itself provide:
- historical odds;
- historical lineups at decision time;
- historical injury publication timing;
- bookmaker market state;
- defensible publication-time `known_at` for mutable context.

## Leakage rule

For a target fixture, only prior completed fixtures may contribute to historical sporting features.

A target fixture result remains a label/update observed after the prediction point.

Git commit/blob time must not be treated as historical `known_at`.

## What this changes

It means SPORTS QUANT does not need to purchase a broad provider merely to obtain enough EPL result history for the first simple model baselines.

Paid/provider effort can remain focused on the harder missing layers:
- historical odds;
- point-in-time context;
- prospective lineups/injuries;
- production-grade coverage.

## What this does not change

This evidence:
- does not start F4 or F5;
- does not resolve OD-11;
- does not resolve OD-24;
- does not define train/validation/calibration/test boundaries;
- does not define minimum sample size under OD-04;
- does not establish profitability.
