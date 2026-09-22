# ADR-0003 — Additional Sports Allowlist

- **Status:** APPROVED
- **Authority:** Enzo
- **Date:** 2026-09-22
- **Scope:** Foundation v0.1 amendment

## Decision

Outside the mandatory core defined by ADR-0002, SPORTS QUANT may validate only:

- **Handball**
- **Volleyball**
- **Tennis**

No other non-core sport is part of the current roadmap.

This explicitly removes Rugby Union, Futsal, Lacrosse, Roller Hockey and any other previously researched candidate from the current additional-sport scope.

## Validation versus promotion

This approval authorizes empirical validation work only.

It does **not**:
- assign an SP1–SP5 empirical class;
- establish edge;
- establish profitability;
- define production market families;
- waive calibration, uncertainty, data-quality or point-in-time requirements.

Production-model promotion for Handball, Volleyball or Tennis still requires PIT-valid, out-of-sample Sport Predictability evidence at SPORT × MARKET_FAMILY scope.

## Consequences

The active sport universe is now:

### Mandatory core
- Basketball
- Football
- MMA/UFC

### Approved additional validation scope
- Handball
- Volleyball
- Tennis

### Excluded unless Enzo issues a new scope decision
- every other sport

This ADR must be included in the independent Foundation review before promotion to F2.
