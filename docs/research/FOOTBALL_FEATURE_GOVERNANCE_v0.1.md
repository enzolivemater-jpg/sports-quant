# Football Feature Governance v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN

## Rule

A Football feature is not admitted because it sounds predictive.

A feature may enter a model candidate only when:
- its semantic definition is explicit;
- its historical value is point-in-time defensible;
- its missing-data behavior is explicit;
- its lineage is reproducible;
- it is evaluated out of sample;
- it survives leakage review.

## Feature states

Use four research states before later production contracts exist:

- ALLOWED_BASELINE
- CONDITIONAL_PIT
- PROSPECTIVE_ONLY
- REJECTED

These labels are research-governance labels only, not canonical F2 enums.

## ALLOWED_BASELINE

Candidates derivable exclusively from prior completed matches and known schedule state:

- sequential Elo/rating
- prior results
- rolling goals scored/conceded
- home/away splits
- rest days
- schedule congestion from prior/known fixtures
- reconstructed table state
- opponent-strength-adjusted rolling form

Implementation must still prove chronological computation.

## CONDITIONAL_PIT

Allowed only if timestamp/revision semantics pass provider audit:

- prior-match xG
- prior-match advanced stats
- referee assignment
- weather forecast
- historical squad availability
- manager/coach state
- market movement features
- expected lineups

## PROSPECTIVE_ONLY

Capture now for future evaluation unless defensible historical snapshots exist:

- injury news
- doubtful/fitness updates
- training-ground reports
- expected lineup reports
- tactical/contextual journalist reports
- late squad changes
- weather changes near kickoff

Prospective capture must preserve source and SPORTS QUANT receipt time.

## REJECTED

Never use in pre-match prediction:
- target-match final score
- target-match event data
- target-match post-match xG/stats
- future fixtures/results that were not known at cutoff
- final starting lineup before lineup publication
- closing market price for an earlier cutoff
- retroactively corrected context without historical revision evidence
- manually guessed historical known_at
- missing values silently replaced with zero
- any transformed feature fit using future rows

## Transformation leakage

The following objects must be fit inside each temporal training fold only:
- scalers
- encoders
- imputers
- feature selectors
- PCA/embeddings
- calibration models
- learned ensemble weights
- hyperparameter selection

## Incremental ratings

Ratings must be updated sequentially.

For fixture i:
1. compute pre-match rating features from state after fixtures < i;
2. freeze the feature row;
3. observe fixture i outcome;
4. update rating state.

Never recompute a historical pre-match rating with outcomes from later fixtures unless generating a clearly separate hindsight diagnostic.

## Rolling windows

A rolling feature for event_time T may contain only source events with legitimate known_at <= feature_cutoff_at.

Window definitions must specify:
- lookback length;
- minimum observations;
- weighting;
- treatment of season boundaries;
- promoted/new teams;
- missing values.

## Market features

Two tracks remain separate:

### Market-blind
No bookmaker probability enters sports-model features.

### Market-aware challenger
Point-in-time de-vigged market state may enter as a feature.

It must be benchmarked against the market itself and undergo ablation to prove incremental signal.

## Promotion requirement

A context/advanced feature is promoted only if it improves OOS forecasting/calibration robustly enough to justify added data complexity and uncertainty.

In-sample feature importance is not promotion evidence.
