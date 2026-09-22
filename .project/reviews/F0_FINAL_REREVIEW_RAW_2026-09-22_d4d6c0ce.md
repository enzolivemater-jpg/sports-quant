# SPORTS QUANT — F0 P1-01 Targeted Independent Re-Review

**Repository:** `enzolivemater-jpg/sports-quant`
**Reviewed HEAD:** `d4d6c0ce4d26f42183312b6386b7d0e00ab46f88`
**Previous reviewed HEAD:** `3cd2bba8bd29d7795d998d12f7f84b756bb6ee4f`
**Scope:** re-review ciblée de `P1-01` et `P2-03` uniquement. Aucune implémentation F2 effectuée.

J’ai vérifié indépendamment que `main` est exactement sur le SHA demandé. Il y a 3 commits depuis le HEAD précédent. GitHub Actions confirme au SHA revu : **CI = SUCCESS** et **Security = SUCCESS** ; les checks `quality`, `postgres-integration`, `dependency-audit` et `secret-scan` sont tous réussis. L’issue **#1 est toujours OPEN** et `.project/PHASE_GATES.toml` conserve `f2.authorized = false`.

## P0 findings

**Aucun P0 détecté.**

## P1 findings

**Aucun P1 restant.**

### P1-01 — RESOLVED

La correction répond désormais aux trois bypass qui maintenaient P1-01 ouvert.

| VérificationRésultat                                        |          |
| ----------------------------------------------------------- | -------- |
| Set canonique F1 exact                                      | **PASS** |
| Extension silencieuse de l’allowlist impossible             | **PASS** |
| Scaffold obligatoirement `README.md`                        | **PASS** |
| 7 fichiers F1 figés par Git blob SHA                        | **PASS** |
| Mutation de leur contenu bloquée                            | **PASS** |
| Scanner étendu à tout `src/`                                | **PASS** |
| Second package sous `src/` bloqué                           | **PASS** |
| Artefacts générés non suivis par Git ignorés                | **PASS** |
| Packaging `where=["src"]` exact                             | **PASS** |
| Packaging `include=["sports_quant","sports_quant.*"]` exact | **PASS** |
| Restriction packaging vérifiée par le gate                  | **PASS** |
| Tests de non-régression requis présents                     | **PASS** |

### 1. Allowlist F1 réellement canonique et non extensible

`scripts/validate_phase_gates.py` contient maintenant `CANONICAL_F1_SOURCE_BLOBS`, qui définit directement le set canonique des **7 seuls fichiers Python F1 autorisés**.

`_load_f1_source_allowlist()` transforme le TOML en set puis impose :

`allowed == set(CANONICAL_F1_SOURCE_BLOBS)`

Une entrée supplémentaire ou manquante produit donc une erreur. Ajouter simultanément `model.py` au TOML et au repository ne permet plus de contourner le gate.

`.project/F1_SOURCE_ALLOWLIST.toml` correspond effectivement exactement à ce set au HEAD revu.

### 2. Scaffold verrouillé

Le validator contient désormais :

`CANONICAL_SCAFFOLD_FILENAME = "README.md"`

et exige explicitement :

`allowed_filename == CANONICAL_SCAFFOLD_FILENAME`

Le bypass consistant à transformer `model.py` en nom de scaffold autorisé est supprimé.

### 3. Les 7 fichiers F1 sont réellement figés par leur Git blob SHA

Le validator ne vérifie plus uniquement leurs chemins. `_validate_frozen_f1_source_blobs()` recalcule le Git blob SHA du contenu et exige l'égalité avec la baseline canonique.

J’ai comparé les blobs du tree Git réel du HEAD avec les valeurs hardcodées :

- `src/sports_quant/__init__.py` → `26b8d1f10a7ddf588663e2b9f49824eb31626dd6`
- `config/__init__.py` → `528d002102b858ac759ad6b821593920ef6dca77`
- `config/settings.py` → `6948ddc8d3ea16f1eba4517454a3639373c6dd75`
- `db/__init__.py` → `0ef790fc5cc0b20c6411c4bd084ec3119c8093e8`
- `db/engine.py` → `b338bf8089156f4a0890930257e4172186fc27bc`
- `observability/__init__.py` → `066aa77fc36bda374b6327eec68dc8a76702b261`
- `observability/logging.py` → `561e212a138349d52407ccc8c3f37c51631418b7`

**Les sept correspondent exactement.**

Une modification de `settings.py`, `engine.py` ou d’un autre fichier allowlisté ne peut donc plus accueillir silencieusement de logique F2 : le SHA changerait et le gate fermé échouerait.

### 4. Scanner étendu à tout `src/`

`SOURCE_ROOT` est désormais :

`ROOT / "src"`

et surtout `_tracked_source_files()` utilise, dans le repository Git :

`git ls-files -- src`

Le contrôle n’est donc plus limité à `src/sports_quant/`.

Un second package comme :

`src/sports_quant_f2/__init__.py`

est recensé et rejeté puisqu’il n’est ni un blob F1 canonique ni un `README.md`.

### 5. Pas de faux positif sur `sports_quant.egg-info`

Le chemin opérationnel dans un checkout Git scanne les **fichiers suivis par Git**, pas tous les fichiers présents physiquement.

Un artefact généré localement tel que :

`src/sports_quant.egg-info/...`

n’apparaît donc pas dans `git ls-files` tant qu’il n’est pas versionné, et ne provoque pas de faux positif.

S’il était accidentellement commité, il serait au contraire bloqué — comportement correct pour le gate F1 fermé.

### 6. Packaging désormais strictement borné

`pyproject.toml` contient exactement :

```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["sports_quant", "sports_quant.*"]
```

Le validator fixe parallèlement :

- `CANONICAL_PACKAGE_FIND_WHERE = ["src"]`
- `CANONICAL_PACKAGE_FIND_INCLUDE = ["sports_quant", "sports_quant.*"]`

et `_validate_packaging_scope()` refuse toute divergence.

Le deuxième bypass identifié dans ma review précédente — ajouter un nouveau package Python sous `src/` et élargir la découverte setuptools — est donc fermé à deux niveaux : scanner Git + validation packaging.

### 7. Tests de non-régression

`tests/unit/test_phase_gate_validator.py` contient maintenant des tests explicites pour :

- extension de l’allowlist → **rejet**
- changement de `scaffold_filename` → **rejet**
- mutation du contenu d’un fichier F1 déjà allowlisté → **rejet**
- fichier F2 dans `contracts/` → **rejet**
- Football hors contracts → **rejet**
- calibration → **rejet**
- market → **rejet**
- probability hors contracts → **rejet**
- second package sous `src/` → **rejet**
- élargissement du packaging → **rejet**
- F1 frozen sources + README scaffold → **acceptés**

Ces tests font partie du job `quality`, qui est **SUCCESS** au SHA revu.

Je n’ai identifié aucun nouveau bypass matériel équivalent à ceux de P1-01.

---

## P2 findings

**Aucun nouveau P2 détecté dans le périmètre de cette re-review.**

### P2-03 — RESOLVED

Le test demandé existe maintenant explicitement :

`test_closed_gate_rejects_probability_business_logic_outside_contracts`

avec :

`src/sports_quant/probability/model.py`

et exige `module.main() == 1`.

La lacune de couverture signalée dans la review précédente est donc corrigée.

---

## OPEN_DECISIONS integrity

**PASS.**

`.project/OPEN_DECISIONS.yaml` n’a pas été modifié dans le diff entre `3cd2bba8...` et `d4d6c0ce...`.

Les décisions restent exactement `OD-01` à `OD-29`. Je n’ai détecté aucune OPEN_DECISION créée, supprimée, résolue ou repurposée silencieusement.

En particulier restent ouvertes :

- formule exacte de `P_safe` ;
- champion Football `OD-11` ;
- Dynamic Market Risk composite `OD-16` ;
- `weighted_average_mr` `OD-17` ;
- détails Basketball/MMA-UFC `OD-29`.

---

## État final de la review

**P1-01: RESOLVED**
**P2-03: RESOLVED**

**P0 open: 0**
**P1 open: 0**
**Blocking findings cleared: true**

Le repository lui-même conserve correctement F2 fermé au HEAD revu ; l’enregistrement de cette review et l’ouverture formelle du machine gate restent donc des étapes de gouvernance à effectuer avant d’écrire du code F2.

**F2 MAY BEGIN. No unresolved P0/P1 remains.**

# GO
