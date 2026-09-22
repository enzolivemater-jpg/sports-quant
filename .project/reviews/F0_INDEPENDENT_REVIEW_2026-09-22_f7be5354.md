# SPORTS QUANT — F0 Independent Critical Review

**Reviewed repository:** `enzolivemater-jpg/sports-quant`
**Reviewed HEAD:** `f7be5354f0cb50cd82617571485c2d2fab6d7fa4`
**Review type:** `INDEPENDENT_CRITICAL_REVIEW`
**Scope:** F0 only. **Aucune implémentation F2 n’a été commencée ou modifiée pendant cette review.**

J’ai vérifié que `main` est **identique** au SHA fourni : `ahead_by=0`, `behind_by=0`, aucun commit d’écart.

## P0 findings

**Aucun P0 détecté.**

Je n’ai trouvé aucun défaut F0 compromettant directement les invariants probabilistes, le Point-in-Time, `known_at`, la séparation `P_raw / P_calibrated / P_safe`, le scope sportif ou l’interdiction d’automatisation de paris réels.

## P1 findings

### P1-01 — Le machine gate F0→F2 ne détecte pas exhaustivement une implémentation F2/F3+ prématurée

**Fichiers concernés :**

- `scripts/validate_phase_gates.py`
- `docs/runbooks/GOVERNANCE_DEVIATION_F1_BEFORE_F0_REVIEW.md`

**Élément précis :** fonction `_f2_implementation_files()` et branche `if not authorized:`.

**Problème :** le contrôle d’implémentation F2 fermée inspecte uniquement :

`src/sports_quant/contracts/`

et considère seulement `README.md` / `__init__.py` comme scaffold autorisé.

C’est cohérent avec le futur F2 Contracts, mais ce n’est **pas équivalent** à l’affirmation de gouvernance selon laquelle le gate empêche l’apparition de toute logique F2+ avant autorisation. Une logique métier pourrait être ajoutée ailleurs — par exemple dans un futur package football, market, prediction, calibration ou autre emplacement — sans être vue par `_f2_implementation_files()`.

Le runbook affirme pourtant que `validate_phase_gates.py` « makes CI fail if F2 implementation appears while unauthorized ». Cette garantie est actuellement plus forte que ce que le code assure.

**Conséquence :** une PR pourrait introduire prématurément du code métier F2/F3+ hors de `contracts/`, tout en conservant :

- `foundation_review.status = PENDING`
- `f2.authorized = false`
- un `Phase gate: PASS`

Cela affaiblit précisément le mécanisme censé contenir la déviation historique F1-before-review.

**Correction nécessaire :** rendre le gate exhaustif pendant la fermeture de F2. La solution préférable est un **allowlist F1 explicite** ou une définition exhaustive des zones interdites, plutôt qu’un simple scan de `contracts/`.

Ajouter obligatoirement des tests de non-régression prouvant au minimum que :

- un fichier F2 dans `contracts/` bloque ;
- une logique métier football hors `contracts/` bloque ;
- une logique probability/calibration/market hors `contracts/` bloque ;
- le scaffold F1 autorisé continue de passer.

Tant que ce finding n’est pas corrigé et re-reviewé, je ne considère pas la containment F2 comme suffisamment robuste.

---

## P2 findings

### P2-01 — ADR-0001 conserve des formulations actives devenues historiquement fausses

**Fichier :** `docs/adr/ADR-0001-foundation-v0.1.md`

**Éléments précis :**

- métadonnée `V1 sports: Tennis + Football`
- section « Architecture and scope » : `V1 scope is Tennis + Football only`
- section « Superseded Foundation interpretations » mentionnant de ne pas implémenter `NBA/MMA packages`

**Problème :** le bloc de supersession en tête de fichier explique correctement qu’ADR-0002/3/4 ont priorité. Le repo actuel est donc interprétable sans ambiguïté par un reviewer attentif. Cependant plusieurs affirmations historiques restent formulées comme règles actives dans le corps du même ADR.

**Conséquence :** risque de confusion pour un agent, un nouvel implémenteur ou un système de retrieval qui extrait une section sans le header de supersession.

**Correction nécessaire :** conserver l’historique, mais marquer ces assertions directement comme `HISTORICAL / SUPERSEDED`, ou déplacer la version historique dans une section clairement non normative.

**Non bloquant F2 à lui seul.**

### P2-02 — `make check` n’exécute pas les validations de gouvernance/phase

**Fichiers :**

- `Makefile`
- `.github/workflows/ci.yml`

**Problème :** CI exécute correctement :

- `scripts/validate_phase_gates.py`
- `scripts/validate_governance.py`
- `scripts/validate_f1.py`

mais `make check`, recommandé dans le README pour le bootstrap local, n’appelle que `validate-f1`, lint, typecheck et tests unitaires.

**Conséquence :** un développeur peut avoir un `make check` local vert alors qu’une violation de gouvernance serait détectée seulement par GitHub Actions.

**Correction nécessaire :** faire de `make check` un miroir raisonnable du quality gate CI en ajoutant `validate-phase-gates` et `validate-governance`.

**Non bloquant.**

---

# OPEN_DECISIONS integrity

**Exactement OD-01 à OD-29 présents : OUI.**

Je n’ai détecté **aucune nouvelle OPEN_DECISION numérotée**.

Je n’ai pas non plus détecté de décision ouverte silencieusement transformée en décision fermée :

- `OD-11` reste explicitement ouverte : Football est le premier pilot, mais le champion model reste non sélectionné.
- `OD-16` composite Dynamic Market Risk reste `DEFERRED`.
- `OD-17` `weighted_average_mr` reste `DEFERRED`.
- `OD-29` a été **explicitement**, et non silencieusement, réorientée après l’amendement de scope : l’appartenance Basketball/MMA au scope est décidée, mais leurs catalogues/scope compétition restant à définir sont toujours ouverts.
- la situation Tennis a été adaptée à son statut validation-only après ADR-0002/0003, sans prétendre qu’un modèle champion ou une admission production aurait été décidé.

**OPEN_DECISION modifiée/résolue silencieusement : NON détecté.**

---

# Canonical consistency checks

| ContrôleRésultat                                                 |                  |
| ---------------------------------------------------------------- | ---------------- |
| Rôles Enzo / GPT-Codex / Claude / Gemini                         | **PASS**         |
| C2 actif                                                         | **PASS**         |
| C2+ différé                                                      | **PASS**         |
| Automated real-money wagering interdit                           | **PASS**         |
| `NO_BET` résultat natif                                          | **PASS**         |
| `P_raw`, `P_calibrated`, `P_safe` distincts                      | **PASS**         |
| `0 <= P_safe <= P_calibrated <= 1`                               | **PASS**         |
| Attribution directe finale de `P_safe` par humain/LLM interdite  | **PASS**         |
| Formule production `P_safe` laissée ouverte                      | **PASS**         |
| `known_at` explicitement défini                                  | **PASS**         |
| Reconstruction spéculative de `known_at` interdite               | **PASS**         |
| `known_at <= decision_cutoff_at` pour donnée critique simulée    | **PASS**         |
| Donnée critique sans `known_at` défendable inutilisable          | **PASS**         |
| Taxonomie sources normalisée                                     | **PASS**         |
| 4 axes data-state orthogonaux                                    | **PASS**         |
| `edge_calibrated` / `edge_safe` distincts                        | **PASS**         |
| `edge_safe < 0 => not QUALIFIED`                                 | **PASS**         |
| Market Risk ≠ probabilité                                        | **PASS**         |
| Market Risk ne modifie pas directement `P_safe`                  | **PASS**         |
| Sport Predictability ≠ P/MR/edge/odds/profitabilité              | **PASS**         |
| SP PIT/OOS/versionné                                             | **PASS**         |
| Seuils SP evidence gate non inventés                             | **PASS**         |
| `weighted_average_mr` différé                                    | **PASS**         |
| Dynamic Market Risk composite différé                            | **PASS**         |
| Mandatory sports = Basketball / Football / MMA                   | **PASS**         |
| UFC = scope compétition MMA initial                              | **PASS**         |
| Additional validation = Handball / Volleyball / Tennis seulement | **PASS**         |
| Tous autres sports exclus sans décision Enzo                     | **PASS**         |
| Football = premier pilot                                         | **PASS**         |
| ADR-0004 ne choisit aucun champion model                         | **PASS**         |
| Football Phase 1 exact                                           | **PASS**         |
| Football Phase 2 exact                                           | **PASS**         |
| Basketball catalog non défini                                    | **PASS**         |
| MMA/UFC catalog non défini                                       | **PASS**         |
| OD-01…OD-29 exactement                                           | **PASS**         |
| Déviation F1-before-review documentée honnêtement                | **PASS**         |
| Containment machine F2 exhaustive                                | **FAIL — P1-01** |

Le catalogue Football est bien exactement :

**Phase 1**

- `FOOTBALL_1X2 / MR2`
- `FOOTBALL_TOTAL_GOALS_MAIN / MR2`

**Phase 2**

- `FOOTBALL_ASIAN_HANDICAP / MR2`
- `FOOTBALL_BTTS / MR2`
- `FOOTBALL_TEAM_TOTALS / MR2`

Basketball et MMA/UFC restent bien `NOT_DEFINED_DO_NOT_IMPLEMENT`.

---

# Vérification de l’absence de F2 actuelle

Dans le package F2 prévu `src/sports_quant/contracts/`, j’ai vérifié les modules annoncés par `F2_READY_TO_IMPLEMENT_SPEC.md`.

Ils sont **tous absents** au HEAD revu : `common.py`, `time.py`, `source.py`, `data_state.py`, `entity.py`, `provenance.py`, `sports_intelligence.py`, `market.py`, `market_risk.py`, `probability.py`, `edge.py`, `dependency.py`, `gates.py`, `decision.py`, `reproducibility.py`, `predictability.py`.

Le répertoire ne contient, dans ce que j’ai vérifié, que son README de réservation F1.

Je n’ai donc trouvé **aucune preuve qu’une implémentation F2 Contracts ait déjà démarré**. Le problème P1 porte sur la robustesse du mécanisme qui doit garantir que cela reste vrai.

---

# Blocking findings state

**P0 open: 0**
**P1 open: 1**
**Blocking findings cleared: false**

### Réponses explicites demandées

1. **Reste-t-il des P0 ?** **NON.**
2. **Reste-t-il des P1 ?** **OUI — 1.**
3. **Une OPEN_DECISION a-t-elle été modifiée/résolue silencieusement ?** **NON détecté.**
4. **F2 peut-il commencer ?** **NON.**

Correction de `P1-01` → tests de non-régression → nouvelle review ciblée du gate → enregistrement de l’artifact F0 → ouverture explicite de `.project/PHASE_GATES.toml`.

**F2 MUST REMAIN BLOCKED.**

# NO_GO
