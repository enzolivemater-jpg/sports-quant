# SPORTS QUANT — F0 CI-History Micro Re-Review

**Repository:** `enzolivemater-jpg/sports-quant`
**Reviewed HEAD:** `e5220707b018dee501a2a9757c3e31d5bb41683a`
**Previous independently reviewed HEAD:** `d4d6c0ce4d26f42183312b6386b7d0e00ab46f88`
**Scope:** uniquement l’intégration CI `fetch-depth: 0` et ses conséquences de gouvernance. Aucune implémentation F2 effectuée.

J’ai vérifié que `main` est exactement sur le HEAD demandé. `d4d6c0ce...` est bien un ancêtre de `e5220707...` avec 2 commits d’écart et aucun divergence.

## P0 findings

**Aucun P0.**

## P1 findings

**Aucun P1.**

La correction CI est appropriée.

Dans le job `quality`, `actions/checkout@v4` utilise désormais :

```yaml
with:
  fetch-depth: 0
```

Cela fournit l’historique Git complet nécessaire aux trois opérations de `_validate_reviewed_head_scope()` :

- `git cat-file -e <reviewed_head>^{commit}` : le commit reviewé peut être résolu ;
- `git merge-base --is-ancestor <reviewed_head> HEAD` : l’ancestry peut être contrôlée ;
- `git diff <reviewed_head>..HEAD -- <protected paths>` : les fichiers F0 protégés peuvent être comparés.

Le problème d’intégration qui existait avec un clone depth=1 est donc réellement supprimé.

### Aucun affaiblissement du gate

`fetch-depth: 0` n’enlève aucune validation et n’assouplit aucun invariant. Il donne uniquement au validator les objets Git dont ses vérifications avaient déjà besoin.

`scripts/validate_phase_gates.py` reste inchangé sur le mécanisme critique : il vérifie toujours existence du reviewed HEAD, ancestry puis drift des `REVIEW_PROTECTED_PATHS`.

Le fait que `.github/workflows/ci.yml` appartienne lui-même aux fichiers protégés est également cohérent : le changement depuis `d4d6...` impose justement cette micro re-review. Après enregistrement de cette nouvelle review sur `e522...`, une future modification d’un fichier protégé exigera à nouveau une review.

## Vérifications ciblées

| ContrôleRésultat                                         |                      |
| -------------------------------------------------------- | -------------------- |
| `fetch-depth: 0` présent dans le checkout CI quality     | **PASS**             |
| Reviewed HEAD accessible avec historique complet         | **PASS**             |
| `d4d6...` ancêtre de `e522...`                           | **PASS**             |
| Comparaison des protected files reste opérationnelle     | **PASS**             |
| Aucune protection supprimée/affaiblie                    | **PASS**             |
| F2 actuellement `authorized = false`                     | **PASS**             |
| Phase gate actuel                                        | **PASS — F2 closed** |
| Aucun fichier `src/` modifié depuis la review précédente | **PASS**             |
| Aucune logique F2/F3+ ajoutée                            | **PASS**             |
| Aucun modèle ajouté                                      | **PASS**             |
| Aucun code `P_safe` ajouté                               | **PASS**             |
| Aucun market/calibration/Football ajouté                 | **PASS**             |
| OPEN_DECISIONS inchangées                                | **PASS**             |
| CI au HEAD exact                                         | **SUCCESS**          |
| PostgreSQL integration                                   | **SUCCESS**          |
| Security                                                 | **SUCCESS**          |
| Dependency audit                                         | **SUCCESS**          |
| Secret scan                                              | **SUCCESS**          |

Le diff depuis `d4d6c0ce...` ne contient aucun changement sous `src/`. Les changements concernent uniquement la gouvernance/review, le workflow CI, le phase gate temporairement refermé et la documentation associée.

`.project/OPEN_DECISIONS.yaml` n’a pas été modifié. Je ne détecte aucune décision ouverte silencieusement résolue ou repurposée.

Le log CI du HEAD confirme explicitement :

`Phase gate: PASS (F2 closed; F0 review status=BLOCKED)`

ainsi que :

- `Governance validation: PASS`
- `F1 repository-foundation validation: PASS`
- `81 passed, 1 deselected`

## P2 findings

**Aucun P2 nouveau détecté dans ce périmètre.**

Une précision de procédure seulement : le review artifact actuellement référencé dans `PHASE_GATES.toml` pointe encore sur la review du HEAD `d4d6...`. Cette micro-review doit donc être enregistrée comme nouvel artifact/review basis avant l’ouverture effective du gate. Ce n’est pas un défaut du changement examiné ; F2 est volontairement refermé pour cette étape.

## Blocking state

**P0 open: 0**
**P1 open: 0**
**Blocking findings cleared: true**

La correction `fetch-depth: 0` est compatible avec la gouvernance existante et restaure la capacité du machine gate à effectuer la vérification historique pour laquelle il a été conçu.

**F2 MAY BEGIN. No unresolved P0/P1 remains.**

**GO**
