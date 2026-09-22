# Football Provider Licensing / Usage Audit v0.1

Date: 2026-09-22

Status: DOCUMENTARY_AUDIT__OD-24_REMAINS_OPEN

Purpose:
Evaluate whether candidate providers permit the storage, historical retention, modeling and product use required by SPORTS QUANT.

This is not legal advice. Ambiguous rights are marked as requiring written confirmation.

## The Odds API

Official sources reviewed:
- https://the-odds-api.com/terms-and-conditions.html
- https://the-odds-api.com/historical-odds-data/
- https://the-odds-api.com/liveapi/guides/v4/
- https://the-odds-api.com/

Current documentary findings:
- Terms last updated 2026-08-31.
- Explicitly permits storing data and retaining it indefinitely.
- Explicitly permits research/analytics.
- Explicitly permits calculating/displaying derived values.
- Explicitly permits training statistical and machine-learning models.
- Commercial applications are permitted.
- Raw-feed resale / competing redistribution is prohibited.
- Historical featured-market snapshots are available from 2020-06-06.
- Historical snapshot spacing: 10 minutes historically, 5 minutes from September 2022.
- Historical queries return the closest snapshot at or before the requested timestamp.
- Historical access requires a paid plan.
- Current entry paid historical plan shown publicly: USD 30/month, 20,000 credits.
- Historical featured-market requests cost 10 credits per region per market.

SPORTS QUANT assessment:
- storage fit: VERIFIED_GO
- ML/modeling fit: VERIFIED_GO
- historical PIT market role: STRONG_CANDIDATE
- raw redistribution: PROHIBITED
- exact EPL 2024/25 Phase-1 bookmaker/market coverage: UNTESTED
- provider correction/revision semantics: PARTIALLY_DOCUMENTED__MUST_TEST

Provisional role:
PREFERRED_FIRST_BAKEOFF_FOR_HISTORICAL_ODDS

OD-24 is not closed until an authenticated EPL sample is tested.

---

## API-Football / API-Sports

Official sources reviewed:
- https://www.api-football.com/terms
- https://www.api-football.com/pricing
- https://www.api-football.com/news/post/how-to-get-started-with-api-football-the-complete-beginners-guide
- API-Sports storage/integration tutorials on api-football.com

Current documentary findings:
- Current direct pricing publicly shows:
  - Free: USD 0, 100 requests/day
  - Pro: USD 19/month, 7,500 requests/day
  - Ultra: USD 29/month, 75,000 requests/day
  - Mega: USD 39/month, 150,000 requests/day
- All plans advertise all endpoint families; free plan has season limitations.
- Football endpoints include fixtures/results, events, lineups, sidelined/injuries, stats, predictions and odds.
- Pre-match odds retain only the last 7 days.
- Current official guide states odds update approximately every 3 hours.
- Live odds have no historical retention.
- Lineups are typically available around 30–60 minutes pre-kickoff.
- Injuries are described as updating approximately every 4 hours.
- Direct resale of API data is prohibited.
- Terms state users may build projects/applications on top of the data.
- Terms explicitly warn that API-Football does not grant competition/publication rights; additional rights from leagues/federations/rights holders may be required.
- Official tutorials demonstrate persisting API responses into databases/caches.
- Explicit ML-training rights were not found in the reviewed terms.

SPORTS QUANT assessment:
- prospective internal context capture: CANDIDATE_GO_WITH_CONDITIONS
- long-horizon historical odds: FAIL_AS_PRIMARY_SOURCE
- storage for internal integration: DOCUMENTED_IN_PRACTICE
- explicit ML-training right: UNKNOWN
- public/commercial publication rights: NEEDS_RIGHTS_CONFIRMATION
- historical mutable-context PIT semantics: UNTESTED

Provisional role:
LOW_COST_PROSPECTIVE_CONTEXT_CANDIDATE

Do not rely on API-Football as the historical odds backbone.

---

## Sportmonks

Official sources reviewed:
- https://www.sportmonks.com/integrity-support/
- https://www.sportmonks.com/football-api/plans-pricing/
- https://www.sportmonks.com/football-api/enterprise-plan-v2/
- current Football API glossary/coverage pages

Current documentary findings:
- Explicitly permits building applications/products on top of the data.
- Explicitly permits commercial use.
- Explicitly permits storage/caching in the customer's own database.
- Explicitly permits betting/trading products while noting regulation/licensing remains the customer's responsibility.
- Raw-feed resale/redistribution requires written approval.
- Sportmonks states it is not an official league rights holder.
- Historical seasons older than the most recent three require a historical-data add-on on self-service plans.
- Current public pricing advertises historical data add-on from EUR 29 one-time.
- Current Starter pricing is advertised from EUR 29/month.
- Full historical access is included on Enterprise; self-service older history is add-on based.
- Premium odds and other add-ons are separately priced.
- Sportmonks states corrections are made in the source data and propagate into the historical record.

Critical PIT implication:
If corrections overwrite the current historical record and old revisions are not queryable, SPORTS QUANT must preserve its own immutable raw snapshots prospectively. Historical as-of reconstruction of mutable context must not assume the current corrected value existed before the correction.

SPORTS QUANT assessment:
- own-database storage: VERIFIED_GO
- application/product use: VERIFIED_GO
- betting/trading product use: DOCUMENTED_GO, subject to external legal/regulatory requirements
- raw-feed resale: REQUIRES_WRITTEN_APPROVAL
- official league-rights status: NOT_OFFICIAL_RIGHTS_HOLDER
- broad Football data/context: STRONG_CANDIDATE
- historical revision PIT semantics: MATERIAL_UNKNOWN
- historical odds granularity: MATERIAL_UNKNOWN

Provisional role:
STRONG_BROAD_DATA_AND_PROSPECTIVE_CONTEXT_CANDIDATE

Must test update/revision semantics before historical decision-critical use.

---

## Sportradar

Official sources reviewed:
- https://developer.sportradar.com/sportradar-updates/page/terms-and-conditions
- https://developer.sportradar.com/getting-started/docs/your-account

Current documentary findings:
- Current master terms last updated 2026-08-05.
- Free Trial is defined as non-commercial internal testing/evaluation.
- Default current trial limits:
  - 30 days
  - 1,000 requests per rolling 30 days
  - 1 QPS
- Terms define Core History as current season plus prior two years.
- Expanded/Complete History may exist depending on order form/product.
- Service architecture explicitly contemplates API data being stored on customer servers.
- Paid-service use is tightly governed by the Order Form and specified Properties.
- Terms contain significant restrictions on uses beyond the licensed display/use scope.
- Terms require prior written consent for prediction-market, trading-platform, financial-product or similar use.
- Whether SPORTS QUANT's sports-betting decision-support use falls into a restricted category must be confirmed in writing rather than assumed.
- Trial data cannot be used commercially or publicly.
- On termination/expiry, current terms require destruction/sanitization of licensed data and databases, including historical data and derivatives/copies/extracts/compilations, subject to stated exceptions and certificate-of-destruction requirements.
- The reviewed terms do not provide a clean, general permission comparable to The Odds API's explicit machine-learning-training permission.

Critical SPORTS QUANT implications:
- Long-term reproducible research depends on retaining exact historical source snapshots and derived artifacts.
- Mandatory destruction after termination can conflict with reproducibility requirements unless a negotiated agreement expressly allows required retention.
- ML/model-training and betting decision-support rights should be written into the commercial agreement before reliance on Sportradar as a core research/modeling source.

SPORTS QUANT assessment:
- trial for schema/coverage evaluation: GO
- long-term raw retention under standard reviewed terms: HIGH_FRICTION
- ML training right: NEEDS_WRITTEN_CONFIRMATION
- betting/decision-support use: NEEDS_WRITTEN_CONFIRMATION
- reproducibility after contract termination: POTENTIAL_CONFLICT
- production source: POSSIBLE_ONLY_WITH_CONTRACT_REVIEW

Provisional role:
EVALUATE_TECHNICALLY_BUT_DO_NOT_SELECT_AS_DEFAULT_PILOT_PROVIDER_WITHOUT_WRITTEN_TERMS

---

## Current evidence-based provider role order

### Historical odds
1. The Odds API — strongest documentary fit.
2. Sportmonks — only after historical odds granularity/revision tests.
3. Sportradar — only with explicit commercial rights/retention terms.
4. API-Football — unsuitable as long-history odds backbone under 7-day retention.

### Broad Football/context
1. Sportmonks — strong documented storage/product fit; PIT revision semantics still need testing.
2. API-Football — low-cost prospective capture candidate; rights/publication/ML scope needs care.
3. Sportradar — potentially high-quality licensed feed but materially higher contractual friction.

### Free parser/event research
- StatsBomb Open Data remains the current sandbox role.

## OD-24 state

OPEN.

What can now be said:
- The Odds API has the strongest documented fit for historical odds + ML/storage.
- Sportmonks has the strongest documented general-purpose storage/product permission among the broad Football providers reviewed.
- API-Football is attractive for inexpensive prospective capture but cannot replace a historical odds archive.
- Sportradar requires written commercial/use/retention clarification before becoming a default core provider.

What is still required:
1. authenticated EPL 2024/25 coverage test;
2. exact Phase-1 market availability test;
3. bookmaker continuity test;
4. update/revision behavior test;
5. entity-ID stability test;
6. raw response reproducibility test;
7. confirmation of any ambiguous licensing terms;
8. cost calculation for the actual extraction plan.

No provider is finally approved by this document.
