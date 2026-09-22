# Repository Hardening — Required Manual Admin Actions

Date: 2026-09-22

Current verified repository state:
- visibility: PUBLIC
- default branch: main
- main protected: false

The current GitHub connector available to this chat does not expose repository-admin write operations for visibility or branch protection.

## Required actions

### 1. Make repository private

GitHub UI:
- Repository -> Settings -> General
- Danger Zone
- Change repository visibility
- Private

Reason:
SPORTS QUANT is a personal quantitative system containing proprietary architecture, research and future provider integrations.

No secret has been intentionally committed, but public visibility is still unnecessary exposure.

### 2. Protect main

Prefer a GitHub ruleset or branch-protection rule requiring:
- pull request before merge
- required successful status checks
- CI
- Security
- block force pushes
- block branch deletion
- require conversation resolution when review comments exist
- require review for critical implementation PRs where practical

Do not configure a rule that blocks the repository owner from emergency recovery without understanding the implications.

### 3. Keep secrets out of Git

Provider keys must use:
- GitHub Actions secrets / environment secrets
- local .env ignored by Git
- deployment secret store later

Never commit:
- API keys
- tokens
- database passwords
- service-role keys

## Verification

After manual change, re-check:
- repository `private=true`
- visibility `private`
- main branch `protected=true` or applicable ruleset active
- CI/Security remain green

## Status

OPEN_ADMIN_ACTION
