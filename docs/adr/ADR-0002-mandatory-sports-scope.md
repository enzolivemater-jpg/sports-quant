# ADR-0002 — Mandatory Sports Scope and Predictability-Gated Expansion

- **Status:** APPROVED
- **Authority:** Enzo
- **Date:** 2026-09-22
- **Scope:** Foundation v0.1 amendment
- **Criticality:** C2 — Decision Support

## Decision

The mandatory active sport scope of SPORTS QUANT is:

1. **Basketball**
2. **Football**
3. **MMA**, with **UFC** as the mandatory initial competition scope.

This supersedes the earlier Foundation assumption that Tennis + Football were the mandatory V1 sports and that Basketball/MMA were future-only expansions.

UFC is treated as a competition/promotion scope under the sport **MMA**, not as a separate sport.

## Optional sports

Every sport outside the mandatory set is optional and must not be added merely because it appears intuitively easy to predict.

Admission must be based on empirical **Sport Predictability**, evaluated at least at:

`SPORT × MARKET_FAMILY`

and optionally at competition level when evidence supports it.

Relevant evidence remains the Foundation Sport Predictability evidence set, including out-of-sample Brier Score, Log Loss, ECE, skill versus baseline, sample size, stability, data quality, drift, lineage and point-in-time integrity.

No optional sport is pre-approved. Tennis therefore becomes a candidate only and may return to the active roadmap only if its relevant market families satisfy the future empirical admission rule.

## Markets

This ADR does **not** invent Basketball or MMA/UFC market families.

- Football retains the previously approved Phase 1 / Phase 2 catalog.
- Basketball Phase 1 / Phase 2 market families remain `NOT_DEFINED_DO_NOT_IMPLEMENT`.
- MMA/UFC Phase 1 / Phase 2 market families remain `NOT_DEFINED_DO_NOT_IMPLEMENT`.
- Exact Basketball competition scope also remains undefined.

Those unresolved implementation details are tracked through the existing OD-29 identifier rather than creating a new numbered OPEN_DECISION.

## Model architecture

Each mandatory sport receives its own sport-specific modeling engine in its authorized phase. No universal cross-sport model is permitted.

The order of Basketball, Football and MMA/UFC model implementation is **not fixed by this ADR**. It should later reflect data readiness, point-in-time integrity, licensing, validation feasibility and project priorities.

## Consequences

- Tennis is removed from mandatory V1 scope.
- Basketball and MMA/UFC are no longer future-only sports.
- The repository skeleton must reserve Basketball and MMA package boundaries.
- Additional sports are admitted only through validated empirical Sport Predictability evidence.
- High predictability does not imply edge, profitability or qualification.
- This amendment must be included in the independent Foundation review before promotion to F2.
