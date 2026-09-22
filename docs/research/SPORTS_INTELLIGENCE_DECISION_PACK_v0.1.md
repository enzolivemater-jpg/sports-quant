# Sports Intelligence Decision Pack v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN__NO_OD_RESOLVED

Open decisions covered:
- OD-12 historical reliability scoring formula
- OD-13 numeric freshness windows by claim type
- OD-14 exact cross-confirmation thresholds
- OD-15 automatic source promotion/demotion rules

Canonical policy basis:
- source hierarchy
- source registry
- reliability dimensions
- FACT / EXPERT_ASSESSMENT / OPINION / RUMOR / CONFLICT typing
- true cross-confirmation only from independent sources
- freshness metadata
- conflict preservation
- no direct discretionary P_safe assignment
- overlap / double-counting control

## OD-12 — Historical source reliability

The canonical policy permits reliability measurement using dimensions such as:
- factual accuracy;
- speed;
- correction frequency;
- later confirmation rate;
- domain specialization;
- source transparency;
- stability over time.

The A–E reliability scale remains descriptive until empirical scoring is validated.

### Research record

For each source/claim where observable:
- source_id
- claim_type
- sport
- competition
- entity
- published_at
- SPORTS QUANT received_at
- official_confirmation_at where applicable
- final outcome: correct / incorrect / partial / unverifiable
- correction issued
- correction time
- primary-source reference
- independence group
- lead time versus official confirmation

### Candidate scoring designs

A. simple empirical rate by claim type
B. Bayesian reliability estimate with shrinkage for small samples
C. time-decayed reliability
D. hierarchical reliability by source × sport × claim type
E. multidimensional reliability profile rather than one scalar

No method is selected here.

### Hard rules

- unverifiable claims must not be counted as correct;
- repeated syndication of one original source is one evidence lineage, not multiple confirmations;
- tactical EXPERT_ASSESSMENT quality must not be mixed blindly with factual accuracy;
- small sample sizes require shrinkage/uncertainty;
- source reputation alone cannot create TRUSTED status.

## OD-13 — Freshness windows

The policy states freshness depends on information type.

Candidate claim families for Football:
- confirmed lineup
- expected lineup
- injury
- suspension
- manager/coach change
- travel
- weather forecast
- tactical tendency
- player role/minutes expectation
- schedule/rest
- official press-conference statement

Do not set one global TTL.

### Freshness experiment

For prospectively captured claims:
- observe publication/update cadence;
- observe correction frequency;
- measure how long claim state remains valid;
- record supersession frequency;
- compare decision relevance by time-to-kickoff.

Potential output per claim type:
- LIVE window
- RECENT window
- DELAYED/STALE boundary
- expiration/supersession logic

Numeric thresholds remain OD-13.

### Rules

- official confirmed lineup has different semantics from expected lineup;
- an injury report may remain valid for days but can be superseded by training/lineup information;
- tactical tendency may remain valid across multiple matches;
- weather must distinguish forecast issue time from valid/event time.

## OD-14 — Cross-confirmation

Canonical rule:
critical non-official information should seek the original source and at least one independent confirmation when it can materially change a decision.

### Independence graph

Model confirmation lineage explicitly:
- primary source
- direct independent source
- syndication/aggregator copy
- social echo
- same journalist/network family where dependence exists

Three websites repeating the same report are not three confirmations.

### Candidate cross-confirmation rules

A. source-tier dependent
B. claim-type dependent
C. materiality dependent
D. reliability-dependent
E. hybrid rule

Example structure only, not approved:
- official source may satisfy confirmation alone for a FACT;
- trusted specialist/journalist critical claim may require one independent corroboration;
- aggregator/social cannot independently upgrade a critical claim.

Exact thresholds remain OD-14.

### Validation

Track:
- false confirmation rate;
- time delay introduced by waiting;
- proportion later confirmed officially;
- impact on WAIT/REVIEW decisions;
- missed opportunities versus avoided false claims.

Do not optimize confirmation policy purely for bet frequency.

## OD-15 — Source promotion / demotion

Potential states:
- candidate
- active low-trust
- TRUSTED_JOURNALIST / TRUSTED_SPECIALIST eligible
- degraded
- inactive

Exact canonical state machine remains to be defined in implementation phase.

### Promotion evidence

Potential requirements:
- sufficient verifiable claim history;
- stable reliability by relevant domain;
- correction behavior acceptable;
- source identity/provenance clear;
- specialization demonstrated;
- no unresolved integrity issue.

### Demotion triggers

Candidates:
- repeated factual errors;
- correction frequency spike;
- source becomes secondary/aggregator only;
- material deterioration in lead-time quality;
- identity/ownership change;
- unexplained deletion/revisions;
- conflict rate deterioration.

### Automatic vs manual

Automatic system may:
- flag deterioration;
- propose promotion/demotion;
- temporarily reduce trust state;
- trigger review.

A fully automatic permanent promotion to trusted tier should require strong evidence and explicit governance acceptance during early project stages.

## Claim usage rules

Sports Intelligence may:
- create structured features;
- widen uncertainty;
- reduce confidence;
- trigger WAIT;
- trigger REVIEW;
- trigger NO_BET;
- trigger new inference after official information.

It may not:
- directly set P_safe;
- add arbitrary probability points;
- bypass calibration;
- bypass S-Tier;
- count the same underlying fact multiple times.

## Double-counting audit

For material context, check whether the information is already represented in:
- structured model features;
- market odds;
- another context claim.

Record overlap class before any additional quantitative effect.

No quantitative overlap penalty is selected here.

## Experimental order

1. start prospective source/claim capture;
2. preserve claim lineage and timestamps;
3. classify FACT/EXPERT_ASSESSMENT/OPINION/RUMOR/CONFLICT;
4. score factual outcomes retrospectively;
5. estimate reliability uncertainty;
6. study freshness by claim type;
7. study independent confirmation value;
8. simulate promotion/demotion policies;
9. freeze candidate rules;
10. independent review;
11. resolve OD-12..15 only from evidence.

## Current status

OD-12: OPEN
OD-13: OPEN
OD-14: OPEN
OD-15: OPEN
