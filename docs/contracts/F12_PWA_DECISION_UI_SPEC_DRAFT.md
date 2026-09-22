# F12 PWA and Decision UI — Draft Ready Specification

Date: 2026-09-22

Status: DRAFT_READY__DEFERRED_UNTIL_ENGINE_GREEN

## Objective

Deliver a responsive installable PWA for SPORTS QUANT without moving any critical probability, calibration, market, gate or optimizer logic into the frontend.

The PWA is a view/control surface over one canonical backend API and one source of truth.

## Product rule

Frontend displays and requests decisions.

Frontend does not compute:
- P_raw
- P_calibrated
- P_safe
- no-vig
- edge
- Sport Predictability
- Market Risk
- S-Tier status
- dependency-adjusted parlay probability
- model calibration
- stake sizing

Any such value must arrive from backend APIs with version/provenance metadata.

## Initial Football views

### Today

Show:
- scheduled Football events in supported competitions;
- current evaluation state;
- last evaluation time;
- major missing-context warnings;
- QUALIFIED / WAIT / REVIEW / NO_BET / BLOCKED.

Do not visually bias toward QUALIFIED as if more bets were desirable.

### Opportunity detail

Show:
- event
- market
- bookmaker/market reference
- P_raw
- P_calibrated
- P_safe
- probability band
- no-vig market probability
- edge_calibrated
- edge_safe
- MR_base
- Sport Predictability evidence state
- gate results
- context evidence
- decision cutoff
- model/calibrator versions
- reason codes

### Parlay Lab

When F10 is green:
- candidate legs
- individual P_safe
- combined P_safe
- combined odds
- P/L/R notation
- MR summary
- dependency profile
- marginal contribution
- mono/multi-sport marker
- rejection reasons

NO_BET must render as a first-class normal result.

### History

Show immutable prior decision snapshots and later settlement separately.

User must be able to distinguish:
- what was known before event;
- what happened afterward.

### Monitoring

Show:
- Log Loss
- Brier
- calibration/ECE
- sample size
- CLV
- paper ROI
- yield
- drawdown
- decision-state rates
- drift alerts

Never present paper ROI alone as system quality.

## Desktop

Target:
- complete terminal
- model/backtest diagnostics
- data-quality inspection
- market view
- Parlay Lab
- monitoring
- historical decision replay

## Mobile

Prioritize:
- Today
- qualified opportunities
- NO_BET / WAIT / REVIEW / BLOCKED explanations
- S-Tier alerts
- parlay summary
- history
- concise monitoring

## API boundary

PWA communicates only through versioned backend endpoints.

API responses for critical decisions must include:
- decision snapshot ID
- created_at
- decision_cutoff_at
- model/calibrator/gate versions
- dataset/snapshot reference where appropriate
- status
- reason codes

Frontend may format values but must not recalculate them.

## State freshness

UI must expose:
- last backend evaluation time
- freshness/age of critical market/context inputs
- whether a newer reevaluation is pending

A stale display must not look current.

## WAIT / REVIEW

WAIT:
- display the expected missing information/reason when available;
- allow later refresh/re-evaluation.

REVIEW:
- display source conflict/ambiguity;
- no UI action may manually override P_safe.

## Security

- no provider secrets in browser bundle;
- no database service keys in frontend;
- backend authorizes privileged operations;
- environment-specific configuration;
- CSP/security headers later as appropriate;
- no raw provider credentials sent to client.

## Installability

PWA target:
- responsive web
- desktop/mobile installable
- offline shell may be supported for historical views

Do not display stale cached live decisions as if they were current.

Offline live-decision actions must fail safely.

## Accessibility

Minimum:
- keyboard navigation
- semantic status text, not color-only
- readable probability/odds formatting
- accessible tables/cards
- mobile touch targets

## Required tests

1. frontend contains no critical probability formula.
2. P_safe displayed exactly as backend response.
3. stale decision visually identified.
4. NO_BET renders normally.
5. WAIT/REVIEW/BLOCKED not collapsed into NO_BET.
6. settlement data cannot overwrite historical decision snapshot.
7. provider secrets absent from client assets.
8. offline cached live state cannot masquerade as current.
9. P/L/R/MR/SP labels map exactly to backend values.
10. parlay combined probability never calculated client-side.
11. API version incompatibility fails visibly.
12. accessibility smoke tests.

## Implementation technology

Target architecture permits Next.js/TypeScript when this phase becomes active.

Do not introduce frontend implementation before core engine/paper workflow has stable API contracts unless a minimal internal diagnostic UI is explicitly justified.

## Acceptance

F12 is green when:
- one API/source of truth is enforced;
- desktop/mobile responsive views work;
- critical numbers are backend authoritative;
- immutable decision history is visible;
- live freshness is visible;
- no secret or critical quant logic exists in frontend.

## Priority rule

PWA polish must never delay or weaken:
- data integrity
- PIT
- calibration
- P_safe validation
- backtesting
- paper betting
- monitoring
