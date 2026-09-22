# Football Modeling Dataset Scaling Plan v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN__OD-04_REMAINS_OPEN

## Purpose

Separate engineering samples from statistical model-validation datasets.

EPL 2024/25 was selected as an engineering/provider testbed. It must not silently become the entire model-validation dataset.

## Dataset layers

### E0 — Parser / event-feature sandbox

Example:
- StatsBomb Open EPL 2015/16

Purpose:
- parser development
- event schema exploration
- feature R&D

Not sufficient by itself for production PIT context.

### E1 — Provider / pipeline sample

Current:
- EPL 2024/25

Purpose:
- provider bake-off
- entity resolution
- historical odds reconstruction
- PIT plumbing
- canonical schema
- deterministic rebuild

This layer may be only one season.

### E2 — Modeling historical pool

Purpose:
- train Football candidate models
- walk-forward OOS comparison
- create calibration candidates

Must contain multiple chronological periods whenever provider/data quality allows.

Exact season count is NOT fixed here because OD-04 controls minimum sample requirements.

Selection priorities:
1. PIT defensibility
2. consistent competition definitions
3. stable entity mapping
4. historical odds coverage
5. feature availability
6. missingness/revision quality
7. sufficient sample size

Do not add seasons merely to increase N when data semantics differ materially.

### E3 — Frozen final test

A later chronological period must be isolated before final Champion promotion.

Rules:
- no hyperparameter tuning on it
- no feature-selection decisions from it
- no calibration fitting on it
- no repeated peeking followed by redevelopment

If it is opened for development, it loses frozen-test status and a new untouched period is required.

### E4 — Prospective paper dataset

Built forward from actual live decision-time snapshots.

Purpose:
- validate unseen real-world performance
- collect honest context history
- monitor calibration/drift/CLV

This is required before real-money readiness review.

## Single-league versus multi-league

Start modeling with one competition when this keeps semantics clean.

Add leagues only after validating:
- competition/entity normalization
- promotion/relegation handling
- schedule/format differences
- model transferability
- calibration by competition
- market coverage comparability

A larger multi-league dataset is not automatically better.

## Historical feature tiers

### Tier A — safest retrospective features

- prior results
- sequential ratings
- prior goals for/against
- reconstructible table state
- rest days
- schedule congestion
- home/away state
- opponent-adjusted history

### Tier B — conditional historical features

Only when historical PIT is defensible:
- xG
- advanced stats
- referee assignment
- historical lineups
- injuries/suspensions
- weather forecasts
- manager/context state

### Tier C — prospective-only initially

When historical publication time cannot be proven:
- injury news
- expected lineups
- journalist/context claims
- late fitness updates
- last-minute tactical/context information

Collect these prospectively instead of fabricating history.

## Market-blind / market-aware datasets

Maintain two explicit feature views:

### Market-blind
No bookmaker probability used as model feature.

### Market-aware challenger
Point-in-time no-vig market state may be included later.

Both use the same underlying event identity and temporal split framework.

## Split planning

Required order:
- train
- validation
- calibration
- final_test

Plus repeated walk-forward folds.

Exact boundaries remain data-dependent and cannot be finalized until coverage/sample-size audit is complete.

OD-04 remains OPEN.

## Data sufficiency reporting

Before F5 model comparison, report:
- matches per period
- labels per outcome
- competitions/seasons
- missingness by feature
- odds coverage by cutoff
- bookmaker coverage
- feature availability
- PIT rejection rate
- entity-resolution failures
- provider revision rate

No model Champion decision may be made without this table.

## Key rule

Engineering success on EPL 2024/25 does not equal statistical validation.

The project may move quickly through plumbing while preserving the time needed for enough historical and prospective evidence.
