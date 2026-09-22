# Research Probe Harness — Test Guarantees

Date: 2026-09-22

Status: ACTIVE_RESEARCH_GUARDRAIL

The provider probe harness is intentionally outside production F4.

Automated unit tests now verify:
- sensitive query parameters are redacted from metadata;
- secret headers are read only from environment variables;
- missing secret environment variables fail visibly;
- output paths remain under the ignored research-probe directory;
- plain HTTP is rejected;
- captured metadata is explicitly marked research-only;
- `received_at` is retained but canonical `known_at` is not assigned;
- selected response headers exclude unrelated/sensitive headers such as cookies;
- payload hashes are generated;
- raw JSON payload is stored separately from metadata.

These tests do not validate any external provider and do not resolve OD-24.
