# ADR-0004 — Football as First Pilot Sport

- **Status:** APPROVED
- **Authority:** Enzo
- **Date:** 2026-09-22
- **Scope:** Implementation sequencing
- **Criticality:** C2 — Decision Support

## Decision

Football is the first SPORTS QUANT sport to be implemented and validated end to end.

The pilot must exercise the complete quantitative chain:

`data -> point-in-time integrity -> feature materialization -> sport-specific model -> calibration -> uncertainty/P_safe -> market/no-vig -> qualification gates -> backtest/reproducibility`

## Why this is a sequencing decision

This ADR changes implementation order only.

It does **not**:
- change the mandatory sport scope;
- remove Basketball or MMA/UFC;
- promote Handball, Volleyball or Tennis beyond their approved validation status;
- select a Football model champion;
- resolve OD-11;
- define Football calibration thresholds;
- define P_safe;
- select data providers;
- bypass independent review or any validation gate.

## Consequence

Football becomes the reference vertical for testing the architecture before the common infrastructure is reused by Basketball, MMA/UFC, Handball, Volleyball and Tennis.

The project should generalize proven common infrastructure from Football, not copy Football-specific modeling assumptions into other sports.

## Governance constraint

F2+ work remains blocked until the independent F0 review gate is resolved.
