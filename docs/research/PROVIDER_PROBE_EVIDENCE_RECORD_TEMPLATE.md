# Provider Probe Evidence Record

Provider:
Probe date:
Probe operator/context:
Provider plan/trial:
Research role tested:
Repository HEAD:
Harness version / commit:
Local raw-capture location:
Secrets committed: NO

## Probe scope

Competition:
Season:
Fixture/event sample:
Endpoint/resource:
Cutoff/observation time:
Request parameters summary excluding secrets:

## Raw capture evidence

HTTP status:
Provider response timestamp fields:
SPORTS QUANT received_at:
Payload SHA-256:
Payload bytes:
Rate-limit metadata:
Pagination metadata:
Raw capture retained locally: YES / NO

## Identity

Stable event ID:
Stable team IDs:
Stable player IDs if applicable:
Competition/season IDs:
Entity collisions observed:

Result:
- VERIFIED_PASS / VERIFIED_FAIL / PARTIAL / DOCUMENTED_NOT_PROBED / UNKNOWN / NOT_APPLICABLE

## Timestamp semantics

List every timestamp field and its documented/observed meaning.

For each field state whether it is:
- event time
- validity time
- provider processing/update time
- retrieval time
- publication/availability time
- unclear

Any field defensibly usable as historical known_at:
- YES / NO / UNKNOWN

Evidence:

## Historical as-of behavior

Historical query supported:
Old versions/revisions retrievable:
Current state overwrites old state:
Returned snapshot guaranteed <= requested cutoff:
Observed contradictions:

Result:
- VERIFIED_PASS / VERIFIED_FAIL / PARTIAL / DOCUMENTED_NOT_PROBED / UNKNOWN / NOT_APPLICABLE

## Coverage and missingness

Requested records:
Returned records:
Missing fixtures:
Missing markets/context:
Unsupported vs empty distinguishable:
Pagination complete:
Observed data gaps:

Result:
- VERIFIED_PASS / VERIFIED_FAIL / PARTIAL / DOCUMENTED_NOT_PROBED / UNKNOWN / NOT_APPLICABLE

## Corrections / revisions

Repeat retrieval performed:
Payload changed:
Old payload retained locally:
Provider exposes revision identity/time:
Historical previous version retrievable:

Result:
- VERIFIED_PASS / VERIFIED_FAIL / PARTIAL / DOCUMENTED_NOT_PROBED / UNKNOWN / NOT_APPLICABLE

## Licensing / storage

Official terms/docs reviewed:
Raw storage allowed:
Retention limit:
Derived model use:
Decision-support/betting use:
Redistribution/display:
Ambiguities requiring written confirmation:

Result:
- VERIFIED_PASS / VERIFIED_FAIL / PARTIAL / DOCUMENTED_NOT_PROBED / UNKNOWN / NOT_APPLICABLE

## Cost / quota

Requests consumed:
Credits consumed:
Rate-limit behavior:
Observed marginal cost:
Projected pilot cost:
Projected scale risk:

## Security

Key only from environment/secret store:
Secret absent from committed files:
Secret absent from captured metadata:
Secret absent from issue/report:

Security result:
- VERIFIED_PASS / VERIFIED_FAIL

## Proposed role outcome

Role tested:
Outcome:
- VERIFIED_PASS / VERIFIED_FAIL / PARTIAL / UNKNOWN

Residual risks:

## OD-24 impact

Does this probe justify resolving any provider role?
- YES / NO

If YES:
exact proposed role and conditions:

If NO:
remaining evidence required:
