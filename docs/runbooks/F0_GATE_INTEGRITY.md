# F0 Gate Integrity Requirements

Date: 2026-09-22

Status: ACTIVE

The machine gate does not replace independent review. It prevents repository state from claiming F2 authorization without a minimally auditable review record.

When F2 is authorized, CI now requires:

- Foundation review status is `PASS` or `PASS_WITH_P2`;
- independent reviewer identifier is non-empty;
- review artifact exists under `.project/reviews/`;
- review artifact is not the template;
- `Reviewed HEAD` is a full 40-character commit SHA;
- artifact records `P0 open: 0`;
- artifact records `P1 open: 0`;
- artifact records `Blocking findings cleared: true`;
- final review status is `GO` or `GO_WITH_CONDITIONS`;
- artifact explicitly states `F2 MAY BEGIN. No unresolved P0/P1 remains.`;
- template placeholders have been replaced;
- phase-gate TOML also records zero open P0/P1 and cleared blocking findings;
- `f2.authorization_basis` is explicit and no longer says the review is pending;
- the reviewed HEAD exists in Git and is an ancestor of current HEAD;
- protected F0 files have not changed since that reviewed HEAD.

If F0 is marked PASS but F2 remains unauthorized, CI fails as an inconsistent half-open gate.

If F2 is not authorized, non-scaffold implementation files under `src/sports_quant/contracts/` remain prohibited.

This is governance tooling only. It does not approve F0, F2, any model, any provider, or any betting decision.


Protected review scope currently includes Foundation decisions, OPEN_DECISIONS, Sport Predictability policy, Project Profile, ADR-0001 through ADR-0004, AI charter/decisions, and the F0 review handoff. Any change to one of these after review requires a new independent review before F2 can be authorized.
