# ADR-0001 — SPORTS QUANT Foundation v0.1 Governance Canonicalization

> **Partially superseded by ADR-0002 (2026-09-22)** for the active sport scope. Tennis is no longer a mandatory V1 sport; Basketball, Football and MMA are mandatory, with UFC as the mandatory initial MMA competition scope.

- **Status:** APPROVED
- **Authority:** Enzo
- **Scope:** F0 — Governance Canonicalization only
- **Criticality:** C2 — Decision Support
- **V1 sports:** Tennis + Football
- **Architecture:** Modular Monolith
- **Promotion constraint:** independent REVIEW required before F1

## Context

SPORTS QUANT is a selective quantitative decision-support system. It is not required to produce a bet. `NO_BET` is a valid normal result. The Foundation must preserve point-in-time correctness, calibration discipline, provenance, explicit uncertainty, separation of market/context/model evidence, and independent review.

The canonical governance needed normalization before implementation because earlier source documents used overlapping names for source tiers and data states, contained C2/C2+ ambiguity, described a future `weighted_average_mr` and composite Dynamic Market Risk without validated formulas, and did not initially include the final approved Sport Predictability amendment.

## Decision

### 1. Architecture and scope

Foundation v0.1 uses a **Modular Monolith**. Microservices, Kubernetes, Kafka and a dedicated feature store are not part of Foundation. V1 scope is Tennis + Football only. Active criticality is **C2 Decision Support**. C2+ and automated wagering are deferred/prohibited for the active Foundation scope.

### 2. Point-in-time semantics

Canonical temporal semantics include `known_at`, `known_at_basis` and `decision_cutoff_at`. `known_at` is the earliest verifiable instant at which information could legitimately be used. It must not be reconstructed speculatively. Critical simulated decisions require `known_at <= decision_cutoff_at`.

### 3. Canonical source names

The canonical source taxonomy is:

`OFFICIAL`, `LICENSED_PRO`, `TRUSTED_SPECIALIST`, `TRUSTED_JOURNALIST`, `AGGREGATOR`, `SOCIAL_UNVERIFIED`.

Legacy labels are normalized to these values before canonical storage.

### 4. Orthogonal data-state axes

The four independent dimensions are:

- `quality_state`: VALID / PARTIAL / UNAVAILABLE / ERROR
- `freshness_state`: LIVE / RECENT / DELAYED / STALE / SUPERSEDED
- `verification_state`: NOT_REQUIRED / UNVERIFIED / VERIFIED / CROSS_CONFIRMED
- `conflict_state`: NONE / OPEN / RESOLVED

`claim_type=CONFLICT` remains a Sports Intelligence information type and is not the same as operational `conflict_state`.

### 5. Probability and edge invariants

`P_raw`, `P_calibrated` and `P_safe` remain distinct. The hard invariant is `0 <= P_safe <= P_calibrated <= 1`. `P_safe` is the decision authority; no LLM or human directly assigns final `P_safe`.

Market comparison is after no-vig:

- `edge_calibrated = P_calibrated - P_market_no_vig`
- `edge_safe = P_safe - P_market_no_vig`

S-Tier evaluates `edge_safe`. `edge_safe < 0` cannot be `QUALIFIED`. A stricter positive threshold remains deferred.

### 6. Market Risk

Market Risk remains structural and separate from probability and odds. Sport-specific maps take precedence over generic examples. Dynamic factors may be retained individually, but **composite Dynamic Market Risk Score** and **`weighted_average_mr` are DEFERRED** pending empirical validation.

Canonical parlay MR summary is limited to `max_mr`, `count_by_mr`, `count_mr4_plus`, `market_risk_mode`, and `dependency_profile`.

### 7. Frozen Phase 1 / Phase 2 market catalog

**Tennis Phase 1:** `TENNIS_MATCH_WINNER` (MR1).

**Tennis Phase 2:** `TENNIS_TOTAL_GAMES` (MR2), `TENNIS_GAME_HANDICAP` (MR2).

**Football Phase 1:** `FOOTBALL_1X2` (MR2), `FOOTBALL_TOTAL_GOALS_MAIN` (MR2).

**Football Phase 2:** `FOOTBALL_ASIAN_HANDICAP` (MR2), `FOOTBALL_BTTS` (MR2), `FOOTBALL_TEAM_TOTALS` (MR2).

Other set/player/exact-score/timing/micro markets are deferred as recorded in the Foundation Decision Record.

### 8. Business decision states

Canonical states are `QUALIFIED`, `WAIT`, `REVIEW`, `NO_BET`, `BLOCKED`, with operational precedence:

`BLOCKED > REVIEW > WAIT > NO_BET > QUALIFIED`.

Decision evaluations are immutable snapshots. At cutoff, unresolved WAIT/decision-critical REVIEW becomes `NO_BET`, except technical/integrity/licensing/PIT impossibility, which is `BLOCKED`.

### 9. Sport Predictability amendment

Sport Predictability is an orthogonal dimension classified primarily at `SPORT × MARKET_FAMILY`, optionally competition. It uses SP1–SP5 and keeps `predictability_prior` separate from `predictability_empirical`.

A `PredictabilityAssessment` is versioned, immutable and point-in-time retrievable. Its evidence includes out-of-sample Brier, Log Loss, ECE, skill, sample sizes, evaluation period, stability, data quality, drift, baseline/model scope, dataset/code lineage and `known_at`.

SP never directly changes `P_safe`, edge, uncertainty or Market Risk and never bypasses gates. The S-Tier governance includes a `predictability_evidence_gate`; F0 defines no empirical numeric threshold for that gate. No arbitrary numerical SP score and no parlay SP aggregation are implemented in F0. PIT-valid empirical SP may only be used secondarily after qualification in later phases.

## Consequences

- Governance semantics are explicit before business code exists.
- F1 may implement repository skeleton/packaging/CI only after independent review of this F0 output.
- Model formulas, calibrator thresholds, provider choices, optimizer methods and other items listed in `OPEN_DECISIONS.yaml` remain unresolved by design.
- No business code, model, optimizer, data adapter, CI pipeline, database setup or PWA is created by this ADR/F0 implementation.

## Superseded Foundation interpretations

For Foundation v0.1, do not implement: active C2+, NBA/MMA packages, ambiguous generic `edge`, combined quality/freshness/conflict state, legacy source names, `weighted_average_mr`, or a composite Dynamic Market Risk Score.

## Review requirement

The implementer of F0 cannot be its sole critical reviewer. This ADR and the canonical YAML records must be reviewed independently in a separate REVIEW chat. Any P0/P1 disagreement becomes `NEEDS_DECISION`; Enzo remains final authority.
