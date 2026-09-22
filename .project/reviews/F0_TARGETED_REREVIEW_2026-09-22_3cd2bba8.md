# SPORTS QUANT — F0 Targeted Independent Re-Review

**Repository:** `enzolivemater-jpg/sports-quant`
**Reviewed HEAD:** `3cd2bba8bd29d7795d998d12f7f84b756bb6ee4f`
**Baseline précédente:** `f7be5354f0cb50cd82617571485c2d2fab6d7fa4`
**Scope:** re-review ciblée F0 uniquement. **Aucune implémentation F2 n’a été commencée.**

J’ai vérifié indépendamment que `main` est exactement sur le HEAD demandé. Le nouveau HEAD est à **2 commits** du HEAD précédemment revu. J’ai également vérifié les GitHub Actions du SHA : **CI = success** et **Security = success** ; les checks `quality`, `postgres-integration`, `dependency-audit` et `secret-scan` sont tous `success`. Le job `quality` confirme notamment le succès de `Validate phase gates`, `Validate governance invariants`, `Validate F1 repository foundation`, Ruff, mypy et des tests unitaires.

F2 reste bien explicitement fermé dans `.project/PHASE_GATES.toml` avec `f2.authorized = false`.

## P0 findings

**Aucun P0 détecté.**

**P0 open: 0**

## P1 findings

### P1-01 — OPEN — le gate a été fortement amélioré, mais il n’est toujours pas exhaustif contre toute logique F2/F3+ prématurée

Fichiers concernés :
- `.project/F1_SOURCE_ALLOWLIST.toml`
- `scripts/validate_phase_gates.py`
- `tests/unit/test_phase_gate_validator.py`
- `pyproject.toml`
- `docs/runbooks/GOVERNANCE_DEVIATION_F1_BEFORE_F0_REVIEW.md`

La correction précédente bloque correctement les nouveaux fichiers dans contracts, Football, calibration et market, mais quatre bypass restent :

1. l’allowlist peut être étendue sans invariant imposant exactement les 7 chemins F1 ;
2. `scaffold.allowed_filename` n’est pas figé à `README.md` ;
3. le contenu d’un fichier déjà allowlisté peut être transformé en logique F2/F3+ sans être détecté ;
4. un deuxième package Python sous `src/` peut échapper au scanner limité à `src/sports_quant/`, alors que setuptools découvre depuis `src`.

Correction demandée :
- imposer exactement l’allowlist F1 canonique ;
- imposer `README.md` comme seul nom de scaffold ;
- figer le contenu des fichiers F1 approuvés par hashes/blob SHA/baseline équivalente ;
- scanner tout code installable sous `src/` ou restreindre formellement le packaging ;
- ajouter les tests de non-régression correspondants.

**Statut P1-01 : OPEN**

## P2 findings

### P2-03 — absence de test explicitement nommé pour probability hors contracts

Le mécanisme actuel le bloquerait génériquement, mais la suite de tests doit ajouter un cas dédié de type :

`test_closed_gate_rejects_probability_business_logic_outside_contracts`

**P2 uniquement.**

## Vérification des anciennes P2

**P2-01 ADR-0001 : RESOLVED.**

**P2-02 make check : RESOLVED.**

## OPEN_DECISIONS

Les décisions restent exactement `OD-01` à `OD-29`.
Aucune résolution ou modification silencieuse détectée.

## Blocking findings state

**P1-01: OPEN**

**P0 open: 0**
**P1 open: 1**
**Blocking findings cleared: false**

F2 doit rester bloqué.

# NO_GO
