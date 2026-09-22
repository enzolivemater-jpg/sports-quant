# SPORTS QUANT — F0 Targeted Independent Re-Review

**Repository:** `enzolivemater-jpg/sports-quant`
**Reviewed HEAD:** `3cd2bba8bd29d7795d998d12f7f84b756bb6ee4f`
**Baseline précédente:** `f7be5354f0cb50cd82617571485c2d2fab6d7fa4`
**Scope:** re-review ciblée F0 uniquement. **Aucune implémentation F2 n’a été commencée.**

J’ai vérifié indépendamment que `main` est exactement sur le HEAD demandé. Le nouveau HEAD est à **2 commits** du HEAD précédemment revu. J’ai également vérifié les GitHub Actions du SHA : **CI = success** et **Security = success** ; les checks `quality`, `postgres-integration`, `dependency-audit` et `secret-scan` sont tous `success`. Le job `quality` confirme notamment le succès de `Validate phase gates`, `Validate governance invariants`, `Validate F1 repository foundation`, Ruff, mypy et des tests unitaires.

F2 reste bien explicitement fermé dans `.project/PHASE_GATES.toml` avec `f2.authorized = false`.

---

## P0 findings

**Aucun P0 détecté.**

**P0 open: 0**

---

## P1 findings

### P1-01 — OPEN — le gate a été fortement amélioré, mais il n’est toujours pas exhaustif contre toute logique F2/F3+ prématurée

**Fichiers concernés :**

- `.project/F1_SOURCE_ALLOWLIST.toml`
- `scripts/validate_phase_gates.py`
- `tests/unit/test_phase_gate_validator.py`
- `pyproject.toml`
- `docs/runbooks/GOVERNANCE_DEVIATION_F1_BEFORE_F0_REVIEW.md`

**Sections précises :**

- `_load_f1_source_allowlist()`
- `_unauthorized_pre_f2_source_files()`
- branche `if not authorized:`
- `SOURCE_ROOT = ROOT / "src" / "sports_quant"`
- `[scaffold].allowed_filename`
- `[tool.setuptools.packages.find] where = ["src"]`

### Ce qui est désormais correctement corrigé

La correction résout bien une grande partie du finding précédent.

Au HEAD actuel, l’allowlist ne contient que les 7 fichiers F1 légitimes :

`src/sports_quant/__init__.py`, configuration runtime, DB infrastructure et observability.

J’ai inspecté leur contenu : aucun modèle, aucune logique `P_safe`, aucune calibration, aucun moteur market et aucune logique Football n’y est actuellement présente.

Le tree Git complet de `src/sports_quant/` confirme aussi que les autres zones ne contiennent que des `README.md` de réservation. `contracts/` ne contient actuellement que son README.

Les tests couvrent effectivement :

- `contracts/probability.py` → bloqué ;
- `modeling/football/model.py` → bloqué ;
- `calibration/platt.py` → bloqué ;
- `market/no_vig/proportional.py` → bloqué ;
- F1 `settings.py`, `db/engine.py` et un README de scaffold → autorisés.

Ces tests ont réellement tourné dans le CI vert du HEAD.

### Défaut restant n°1 — l’allowlist est elle-même extensible sans invariant canonique

`_load_f1_source_allowlist()` accepte n’importe quel nouveau chemin tant qu’il est sous :

`src/sports_quant/`

Il n’existe pas de contrôle imposant que la liste chargée soit **exactement** les 7 chemins actuellement approuvés.

Donc une modification future peut faire simultanément :

- ajouter `src/sports_quant/modeling/football/model.py` à `F1_SOURCE_ALLOWLIST.toml` ;
- créer ce fichier ;
- laisser `f2.authorized = false`.

Le scanner considérerait alors `model.py` comme autorisé.

Même problème pour `[scaffold].allowed_filename` : le validator vérifie seulement qu’il s’agit d’une chaîne non vide. Il ne vérifie pas qu’elle est obligatoirement égale à `README.md`.

Une modification vers, par exemple, `allowed_filename = "model.py"` transformerait tous les fichiers nommés `model.py` sous `src/sports_quant` en exceptions au gate.

### Défaut restant n°2 — les fichiers F1 autorisés sont contrôlés par chemin, pas par contenu

Le gate valide :

> « ce chemin fait partie de l’allowlist »

mais pas :

> « ce fichier contient toujours uniquement le code F1 qui a été approuvé ».

Ainsi, une future modification pourrait mettre une fonction de calcul probabiliste, market ou Football directement dans :

`src/sports_quant/config/settings.py`

ou un autre fichier déjà allowlisté.

Le gate continuerait de passer car le chemin reste autorisé.

Cela signifie que l’affirmation demandée :

> « bloquer toute logique F2/F3+ prématurée dans `src/sports_quant/` »

n’est pas encore vraie. Il bloque aujourd’hui **les nouveaux chemins hors allowlist**, pas toute nouvelle logique métier.

### Défaut restant n°3 — un deuxième package Python sous `src/` n’est pas couvert

Le scanner est limité à :

`src/sports_quant/`

mais `pyproject.toml` utilise une découverte de packages depuis :

`where = ["src"]`

sans restriction à `sports_quant`.

Un package tel que :

`src/sports_quant_f2/__init__.py`

ou un autre package Python sous `src/` peut donc se trouver hors du `SOURCE_ROOT` inspecté par le gate tout en appartenant potentiellement au code packagé.

### Pourquoi `REVIEW_PROTECTED_PATHS` ne suffit pas

`F1_SOURCE_ALLOWLIST.toml` est désormais correctement ajouté aux chemins protégés, ce qui est utile **après qu’une review acceptée serve à autoriser F2**.

Mais `_validate_reviewed_head_scope()` n’est exécutée que dans le chemin d’autorisation F2.

Tant que `f2.authorized=false`, le gate fermé peut donc encore accepter les scénarios ci-dessus.

### Conséquence

Le P1 initial a été **substantiellement réduit**, mais sa propriété essentielle — containment machine exhaustif de F2/F3+ pendant que F2 est fermé — n’est pas encore démontrée.

Un CI vert confirme que le HEAD actuel est propre selon les règles actuelles ; il ne prouve pas que ces règles sont impossibles à contourner par les mécanismes décrits.

### Correction nécessaire

Avant de fermer P1-01 :

1. imposer que `F1_SOURCE_ALLOWLIST.toml` contienne **exactement** la liste F1 canonique attendue, sans entrée supplémentaire ;
2. imposer `scaffold.allowed_filename == "README.md"` ;
3. figer également le **contenu** des fichiers `.py` F1 approuvés pendant le gate fermé — par hashes/blob SHA, baseline-tree approuvée ou mécanisme équivalent ;
4. scanner tout code Python installable sous `src/`, ou restreindre formellement le packaging à `sports_quant` et valider cette restriction ;
5. ajouter des tests de non-régression pour :
   - extension frauduleuse/accidentelle de l’allowlist ;
   - modification de `allowed_filename` ;
   - insertion de logique métier dans un fichier déjà allowlisté ;
   - création d’un second package Python sous `src/`.

**Statut P1-01 : OPEN**

---

## P2 findings

### P2-03 — absence de test explicitement nommé pour `probability` hors `contracts/`

**Fichier :** `tests/unit/test_phase_gate_validator.py`

Le mécanisme actuel bloquerait bien un chemin tel que :

`src/sports_quant/probability/model.py`

car il n’est pas allowlisté.

Mais la suite de non-régression contient un cas explicite pour :

- Football ;
- calibration ;
- market ;
- contracts/probability ;

et pas pour une logique `probability` **hors contracts**, alors que ce cas figurait explicitement dans la demande de re-review.

**Conséquence :** faible ; la propriété découle déjà du mécanisme générique.

**Correction :** ajouter un test dédié du type `test_closed_gate_rejects_probability_business_logic_outside_contracts`.

**P2 uniquement, non bloquant par lui-même.**

---

# Vérification des anciennes P2

**P2-01 ADR-0001 : RESOLVED.**

Les anciennes assertions Tennis + Football sont maintenant explicitement marquées :

`HISTORICAL / SUPERSEDED`

et la section courante renvoie correctement ADR-0002/0003/0004. La mention historique de `NBA/MMA packages` est également explicitement neutralisée et remplacée par le scope actuel Basketball + MMA/UFC.

**P2-02 `make check` : RESOLVED.**

Le `Makefile` contient désormais :

`check: validate-phase-gates validate-governance validate-f1 lint typecheck test-unit`

Le problème local-vs-CI identifié lors de la première review est donc corrigé.

---

# Autres contrôles demandés

| ContrôleRésultat                                              |                                   |
| ------------------------------------------------------------- | --------------------------------- |
| HEAD demandé = `main`                                         | **PASS**                          |
| CI GitHub Actions                                             | **PASS vérifié**                  |
| Security GitHub Actions                                       | **PASS vérifié**                  |
| F2 explicitement non autorisé                                 | **PASS**                          |
| Allowlist actuelle = uniquement fichiers F1 légitimes         | **PASS au HEAD actuel**           |
| Contenu actuel des fichiers allowlistés = F1 uniquement       | **PASS**                          |
| Fichier F2 dans `contracts/` bloqué                           | **PASS**                          |
| Football hors `contracts/` bloqué                             | **PASS**                          |
| Calibration hors `contracts/` bloquée                         | **PASS**                          |
| Market hors `contracts/` bloqué                               | **PASS**                          |
| Probability hors `contracts/` bloquée par mécanisme générique | **PASS**, test explicite manquant |
| README scaffold autorisé                                      | **PASS**                          |
| Fichiers F1 légitimes actuels autorisés                       | **PASS**                          |
| Allowlist impossible à élargir silencieusement                | **FAIL — P1-01**                  |
| Logique F2 injectée dans fichier déjà allowlisté bloquée      | **FAIL — P1-01**                  |
| Code Python dans second package sous `src/` bloqué            | **FAIL — P1-01**                  |
| P2-01                                                         | **RESOLVED**                      |
| P2-02                                                         | **RESOLVED**                      |
| OPEN_DECISIONS intactes                                       | **PASS**                          |

`.project/OPEN_DECISIONS.yaml` n’a pas été modifié entre les deux HEADs. Les décisions restent exactement `OD-01` à `OD-29`. Je n’ai détecté **aucune résolution ou modification silencieuse d’une OPEN_DECISION**.

Les décisions sensibles restent notamment ouvertes : formule `P_safe`, champion Football OD-11, Dynamic Market Risk OD-16, `weighted_average_mr` OD-17 et détails Basketball/MMA OD-29.

---

## Blocking findings state

**P1-01: OPEN**

**P0 open: 0**
**P1 open: 1**
**Blocking findings cleared: false**

F2 doit donc rester bloqué. La correction actuelle est nettement meilleure que celle du HEAD précédent, mais elle ne satisfait pas encore la garantie d’exhaustivité demandée.

# NO_GO