# `contracts` — F2 domain contracts

Stable, serializable domain contracts and their validation. Contracts only: no
ingestion, PIT kernel, models, calibration, P_safe formula, no-vig, S-Tier,
backtests, optimizer or API logic.

Specification: `docs/contracts/F2_READY_TO_IMPLEMENT_SPEC.md`.

| Module | Contents |
| --- | --- |
| `common.py` | `Contract` base, `CanonicalEnum`, `ContractError`, strict deterministic (de)serialization |
| `time.py` | `KnownAtBasis`, `TemporalMetadata`, critical `known_at <= decision_cutoff_at` validation |
| `source.py` | `SourceTier`, legacy normalization, `SourceRef` |
| `data_state.py` | four orthogonal axes: quality, freshness, verification, conflict |
| `entity.py` | `Sport`, `EntityKind`, canonical and provider identifiers |
| `provenance.py` | `Provenance` |
| `sports_intelligence.py` | `ClaimType`, `EffectChannel`, `SportsIntelligenceClaim` |
| `market_risk.py` | `MarketRiskClass` (MR1–MR6), `MarketRiskMode` |
| `market.py` | `MarketFamily`, frozen Football catalog, `MarketDescriptor` |
| `probability.py` | `ProbabilityEstimate` (P_raw / P_calibrated / P_safe) |
| `edge.py` | `EdgeAssessment` (edge_calibrated / edge_safe) |
| `dependency.py` | `DependencyClass`, `DependencyAssertion` |
| `decision.py` | `DecisionState`, precedence, `require_edge_permits_state` (edge_safe < 0 ⇒ not QUALIFIED) |
| `gates.py` | `GateResult`, `GateEvidenceRef` (serializable surface only; no aggregation) |
| `reproducibility.py` | `CodeVersion`, `ArtifactRef`, `ReproducibilityRef` |
| `predictability.py` | `PredictabilityAssessment` (catalog-independent scope) and SP enums |
