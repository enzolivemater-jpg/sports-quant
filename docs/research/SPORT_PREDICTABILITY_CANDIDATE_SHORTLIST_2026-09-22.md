# Sport Predictability — Candidate Shortlist

Date: 2026-09-22

Status: RESEARCH_SHORTLIST_ONLY

This document does not change the mandatory sport scope and does not assign any SP1–SP5 empirical class.
Mandatory sports remain Basketball, Football and MMA/UFC under ADR-0002.

## Purpose

Identify additional sports whose match-outcome structures appear comparatively predictable in external research and therefore deserve empirical SPORTS QUANT validation.

Admission still requires SPORTS QUANT point-in-time, out-of-sample evidence at SPORT × MARKET_FAMILY scope.

## Primary candidates for validation

### Handball

External evidence is unusually strong.

- A 2024 cross-discipline study using more than 300,000 matches across nine sports found handball to be the most predictable discipline under PageRank-, Elo- and naive-strength predictors.
- The same study found Spanish and German handball leagues among the most predictable leagues.
- A 2025 handball prediction study reported >80% classification accuracy on its female club dataset when statistically estimated team strengths were added.

Research prior: STRONG.

### Volleyball

- The 2024 cross-discipline study found volleyball to be the second most predictable discipline.
- The same paper found volleyball predictability increasing over time.
- A 2025 cross-sport underdog study reported relatively low underdog achievement for volleyball compared with high-randomness sports such as soccer, ice hockey and water polo.

Research prior: STRONG.

### Rugby Union

- A 2025 cross-sport study reported very low underdog achievement for rugby international competition.
- A separate skill/chance study characterized international rugby as relatively neither competitively balanced nor outcome-uncertain, implying relatively little is left to chance.
- Predictability is competition-dependent and strong home-advantage effects require explicit context handling.

Research prior: STRONG_BUT_COMPETITION_DEPENDENT.

### Tennis

- Professional tennis has a binary match-winner structure and extensive historical research.
- A 2021 study covering ATP/WTA 2010–2019 found roughly 69% out-of-sample prediction accuracy and AUC around 0.7.
- A 2024 comparative study reported about 69.5–69.8% accuracy for its best models, comparable to betting-odds-derived predictions.
- A 2026 benchmark on 133,138 ATP matches found 65.9–67.5% accuracy for general-purpose models, while bookmaker probabilities remain stronger.
- Current odds-market coverage is broad and event volume is high.

Research prior: MODERATE_TO_STRONG.
Important: strong market efficiency may mean low exploitable edge even when outcomes are relatively predictable.

## Secondary / research-only candidates

### Lacrosse
Very low underdog achievement in a 2025 international-competition study, but data volume, professional coverage and market depth require separate validation.

### Roller Hockey
Extremely low underdog achievement in the same study, but practical data/market coverage is likely a larger constraint than raw predictability.

### Futsal
Lower underdog achievement than soccer in the 2025 study and structurally higher scoring, but evidence is not as strong as for handball/volleyball/rugby.

## Do not prioritize from current evidence

- Baseball: among the least predictable disciplines in the 2024 cross-sport study.
- Ice hockey: also among the least predictable and high-randomness sports.
- Water polo: high underdog achievement in the 2025 cross-sport study.
- Table tennis: a 2026 Elo study reported only about 56% accuracy, insufficient to justify high-priority admission from current evidence alone.
- Cricket: some evidence of low underdog achievement, but predictability is highly format-dependent and the 2024 cross-discipline study found a declining predictability trend.

## Proposed SPORTS QUANT validation order

1. Handball
2. Volleyball
3. Rugby Union
4. Tennis
5. Futsal
6. Lacrosse / Roller Hockey only if data + market coverage justify the engineering cost

This order is a research-validation priority only. It is not an SP classification, market recommendation, or betting recommendation.

## Evidence references

- Coscia, M. (2024), "Which sport is becoming more predictable? A cross-discipline analysis of predictability in team sports", EPJ Data Science.
- Vicente et al. (2025), "Why is soccer so popular: Understanding underdog achievement and randomness in team ball sports", Journal of Sports Analytics.
- Felice & Ley (2025), "Predicting handball matches with machine learning and statistically estimated team strengths".
- Wilkens (2021), "Sports prediction and betting models in the machine learning age: The case of tennis".
- Bunker et al. (2024), "A comparative evaluation of Elo ratings- and machine learning-based methods for tennis match result prediction".
- 2026 ATP unified benchmark of Elo/ML/deep learning models.
- The Odds API documentation was checked only as a current market-data feasibility signal; it is not an approved SPORTS QUANT provider decision.
