# Football Baseline Model Mathematics v0.1

Date: 2026-09-22

Status: RESEARCH_SPEC__NO_CHAMPION_SELECTED__NO_F5_CODE

Pilot sport: FOOTBALL

Purpose:
define mathematically coherent baseline/challenger families so implementation does not invent formulas ad hoc.

This document does not resolve OD-11.

## 1. Naive empirical baselines

### 1X2 class-frequency baseline

Estimate only from the permitted training window:

- p_home = historical home-win frequency
- p_draw = historical draw frequency
- p_away = historical away-win frequency

with:

p_home + p_draw + p_away = 1

Use as a minimum forecasting baseline.

Never estimate these frequencies using validation/calibration/test outcomes.

### Goal-rate baseline

Estimate training-only home and away scoring rates.

This baseline is deliberately simple and exists to prove that richer score models add predictive value.

## 2. Sequential Elo rating

Elo is primarily a sequential team-strength baseline/feature.

For home team h and away team a:

d = (R_h + H) - R_a

where:
- R_h = pre-match home rating
- R_a = pre-match away rating
- H = home-advantage parameter

Two-outcome-style expected score:

E_h = 1 / (1 + 10^(-d / S))

where S is a rating-scale parameter.

Observed Elo score:

- S_h = 1 for home win
- S_h = 0.5 for draw
- S_h = 0 for away win

Update only after the fixture result is observed:

R_h' = R_h + K * (S_h - E_h)

R_a' = R_a - K * (S_h - E_h)

Important:
this E_h is not automatically a calibrated 1X2 probability because the draw is embedded as a half-score rather than modeled as its own probability mass.

Therefore Elo may be used as:
- team-strength state;
- model feature;
- separate rating benchmark only with an explicit 3-outcome mapping.

Do not silently report E_h as P(home win).

Unresolved parameters:
- initial rating
- K
- home advantage H
- scale S
- season carry-over/shrinkage

All are selected only through temporal OOS validation.

## 3. Bradley-Terry / Davidson draw model

Classic Bradley-Terry is binary and is insufficient by itself for football 1X2 because draws are material.

A valid challenger is a Davidson-style extension.

Let latent team strengths be:

x = exp(theta_h + h)
y = exp(theta_a)

where:
- theta_h = home team latent strength
- theta_a = away team latent strength
- h = home-advantage parameter

Let nu >= 0 be a draw-intensity parameter.

Define denominator:

D = x + y + nu * sqrt(x * y)

Then:

P(home) = x / D

P(away) = y / D

P(draw) = nu * sqrt(x * y) / D

These probabilities sum to 1.

Implementation must use identifiability constraints/regularization because adding a common constant to all latent strengths otherwise leaves relative comparisons unchanged.

No specific regularization or prior is selected here.

## 4. Independent Poisson goal model

Let:

X = home goals
Y = away goals

Baseline assumption:

X ~ Poisson(lambda_h)
Y ~ Poisson(lambda_a)

A standard log-linear parameterization:

log(lambda_h) = mu + home_adv + attack_h - defence_a

log(lambda_a) = mu + attack_a - defence_h

where:
- mu = competition scoring intercept
- home_adv = home scoring advantage
- attack_t = team attack parameter
- defence_t = team defence parameter

Use explicit identifiability constraints, for example centered attack/defence parameters.

### Score probability

P(X=x, Y=y)
= Pois(x; lambda_h) * Pois(y; lambda_a)

under the independence baseline.

### Derive 1X2

P(home win) = sum over x>y of P(X=x,Y=y)

P(draw) = sum over x=y of P(X=x,Y=y)

P(away win) = sum over x<y of P(X=x,Y=y)

### Derive total goals

For an event total T = X + Y, derive probabilities from the score distribution.

For a half-goal line L such as 2.5:

P(over L) = P(T > L)

P(under L) = P(T < L)

Integer/quarter-line settlement requires explicit market-instance handling in the Market Engine and must not be collapsed into a naive binary probability.

### Finite score grid

If implementation truncates score enumeration at a finite max-goals value:
- residual probability mass must be measured;
- output must be renormalized or the truncation must be proven negligible under an explicit tolerance;
- tolerance belongs in tested implementation configuration.

Do not silently drop tail mass.

## 5. Dixon-Coles low-score adjustment

Dixon-Coles modifies the independent Poisson joint distribution for low scores.

Let lambda = lambda_h
and mu_a = lambda_a.

Adjustment tau(x,y):

- x=0,y=0:
  tau = 1 - lambda * mu_a * rho
- x=0,y=1:
  tau = 1 + lambda * rho
- x=1,y=0:
  tau = 1 + mu_a * rho
- x=1,y=1:
  tau = 1 - rho
- otherwise:
  tau = 1

Joint probability:

P_DC(X=x,Y=y)
= tau(x,y;lambda,mu_a,rho)
  * Pois(x;lambda)
  * Pois(y;mu_a)

Constraints must keep adjusted probabilities non-negative.

The score matrix must be checked/normalized consistently when finite truncation is used.

rho is estimated only from training data.

## 6. Time weighting

Possible challengers:
- no time decay
- exponential recency weighting

Generic exponential weight:

w_i = exp(-xi * age_i)

where xi >= 0 and age_i is defined in a documented unit.

No xi value is fixed here.

Compare decay choices OOS.

Do not pick a half-life from intuition.

## 7. Season transition

Candidate policies to compare OOS:

### Elo
- full carry-over
- shrink toward competition mean
- other explicitly parameterized carry-over

### Poisson/Dixon-Coles
- continuous team parameters with shrinkage
- season-specific reset/partial pooling
- promoted-team initialization policy

Promoted-team handling must be explicit.

Never silently initialize a promoted club from future-season performance.

## 8. Multinomial logistic challenger

For 1X2 classes k in {home, draw, away}:

z_k = beta_k^T x

P(Y=k) = exp(z_k) / sum_j exp(z_j)

Features must be PIT-safe.

Regularization strength and feature set are selected only within temporal train/validation boundaries.

## 9. Gradient boosting challenger

Boosting is a nonlinear challenger, not a presumed Champion.

Requirements:
- same PIT-safe feature rows;
- temporal folds;
- probability outputs;
- calibration evaluated separately;
- explicit random seed;
- hyperparameter search bounded and recorded.

Candidate library remains an implementation decision subject to actual need.

## 10. Market baseline

At each permitted historical cutoff:

raw implied probability:

q_i = 1 / odds_i

For proportional research no-vig baseline:

p_i = q_i / sum_j q_j

This is a market benchmark, not a sports model and not necessarily the final no-vig Champion.

The market-aware model track must be evaluated separately from the market-blind track.

## 11. Comparison discipline

Compare candidates on identical eligible fixtures whenever making direct metric claims.

Primary evidence:
- Log Loss
- Brier Score
- calibration / ECE
- sample size
- temporal stability

Additional:
- RPS for 1X2
- calibration slope/intercept
- confidence intervals

Accuracy alone cannot select Champion.

## 12. Parameter selection

The following are intentionally NOT fixed by this document:

- Elo K
- Elo home advantage
- Elo rating scale
- Elo initial ratings
- season shrinkage
- Davidson draw parameter
- Poisson time weighting
- Dixon-Coles rho policy
- score-grid truncation tolerance
- logistic regularization
- boosting hyperparameters
- ensemble weights

These belong to governed OOS model selection.

## 13. Leakage invariants

For every target fixture:
- rating/attack/defence state is computed before target outcome;
- target result is observed only after prediction;
- rolling features contain only earlier eligible records;
- scalers/imputers/encoders fit only inside the training boundary;
- calibration fits only calibration data;
- final test cannot influence formula or hyperparameter selection.

## 14. Champion rule

No formula in this document is the Champion.

OD-11 remains OPEN until:
- PIT-safe data exists;
- walk-forward comparison exists;
- calibration is evaluated;
- frozen final test exists;
- independent review is complete.
