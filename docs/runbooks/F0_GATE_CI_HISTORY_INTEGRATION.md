# F0 Gate CI History Integration Note

Date: 2026-09-22

Status: TARGETED_REREVIEW_REQUIRED

The accepted F0 review at HEAD `d4d6c0ce4d26f42183312b6386b7d0e00ab46f88` cleared all P0/P1 findings and authorized F2.

When the repository attempted to record that review and open F2, the machine gate failed in CI because `actions/checkout@v4` used its default shallow history. The validator intentionally verifies that protected F0 files have not changed between the reviewed HEAD and the authorization HEAD, but the reviewed commit object was unavailable in a depth-1 checkout.

Remediation:
- set `fetch-depth: 0` for CI checkout steps;
- temporarily re-close F2;
- require targeted independent re-review because `.github/workflows/ci.yml` is a protected F0 file.

No F2 implementation is included.

The reviewer should verify only that:
- full-history checkout is sufficient and appropriate for `_validate_reviewed_head_scope()`;
- no governance invariant was weakened;
- no source/model/market/P_safe logic was added;
- F2 remains closed pending re-review.
