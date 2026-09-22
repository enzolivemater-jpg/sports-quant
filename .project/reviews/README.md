# Independent review artifacts

This directory stores immutable review records used by machine-checkable phase gates.

Rules:
- preserve the reviewer result faithfully;
- include the reviewed Git HEAD;
- never overwrite an old review after material repository changes;
- create a new dated/versioned artifact for a re-review;
- P0/P1 findings must be resolved and re-reviewed before a blocked gate is opened.
