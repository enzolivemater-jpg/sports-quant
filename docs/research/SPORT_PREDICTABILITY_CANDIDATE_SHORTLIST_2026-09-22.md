# Sport Predictability — Approved Additional Disciplines

Date: 2026-09-22

Status: ENZO_APPROVED_VALIDATION_SCOPE

Mandatory core sports remain:
- Basketball
- Football
- MMA, with UFC as the mandatory initial MMA competition scope

The only additional disciplines approved for SPORTS QUANT validation are:
1. Handball
2. Volleyball
3. Tennis

All other non-core sports are excluded from the current roadmap unless Enzo explicitly changes the scope.

## Important distinction

Approval for validation is not an empirical SP1–SP5 classification and is not automatic promotion into production modeling.

Each approved additional sport must still pass SPORTS QUANT's own point-in-time, out-of-sample Sport Predictability assessment at SPORT × MARKET_FAMILY scope before model promotion.

## Handball

Research prior: STRONG.

External research motivating validation includes:
- a 2024 cross-discipline study of more than 300,000 matches across nine sports that ranked handball as the most predictable discipline under multiple rating approaches;
- Spanish and German handball leagues among the more predictable competitions in that study;
- a 2025 handball prediction study reporting >80% classification accuracy on its female-club dataset after adding statistically estimated team strengths.

No empirical SPORTS QUANT SP class is assigned yet.

## Volleyball

Research prior: STRONG.

External research motivating validation includes:
- second-highest predictability in the 2024 cross-discipline study;
- an increasing predictability trend over the study period;
- relatively low underdog achievement in a 2025 cross-sport analysis compared with higher-randomness sports.

No empirical SPORTS QUANT SP class is assigned yet.

## Tennis

Research prior: MODERATE_TO_STRONG.

External research motivating validation includes:
- extensive historical modeling literature;
- roughly 69% out-of-sample accuracy in a 2021 ATP/WTA study;
- approximately 69.5–69.8% accuracy for leading models in a 2024 comparative study;
- large event volume and a binary match-winner structure.

Important: tennis market efficiency may be high, so predictability must not be confused with exploitable edge.

No empirical SPORTS QUANT SP class is assigned yet.

## Explicitly removed from the current additional-sport roadmap

- Rugby Union
- Futsal
- Lacrosse
- Roller Hockey
- all other non-core sports

## Evidence references

- Coscia, M. (2024), "Which sport is becoming more predictable? A cross-discipline analysis of predictability in team sports", EPJ Data Science.
- Vicente et al. (2025), "Why is soccer so popular: Understanding underdog achievement and randomness in team ball sports", Journal of Sports Analytics.
- Felice & Ley (2025), "Predicting handball matches with machine learning and statistically estimated team strengths".
- Wilkens (2021), "Sports prediction and betting models in the machine learning age: The case of tennis".
- Bunker et al. (2024), "A comparative evaluation of Elo ratings- and machine learning-based methods for tennis match result prediction".
