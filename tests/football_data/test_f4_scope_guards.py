"""F4 scope guards: no F5+ logic, no network code, Phase 1 markets only, odds block evidence."""

from __future__ import annotations

import ast
from pathlib import Path

from sports_quant.contracts.market import MarketFamily
from sports_quant.data.canonical.football import PHASE_1_MARKET_FAMILIES
from sports_quant.data.provenance.sources import source_descriptor

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "sports_quant"
F4_PACKAGES = (
    "canonical",
    "entity_resolution",
    "ingestion",
    "normalization",
    "provenance",
    "snapshots",
)

# Packages owned by F5+ phases: they must stay README-only scaffolds in F4.
LATER_PHASE_PACKAGES = (
    "backtesting",
    "calibration",
    "dependency",
    "market/consensus",
    "market/edge",
    "market/no_vig",
    "modeling",
    "optimizer",
    "risk",
    "sports_intelligence",
    "uncertainty",
)
FORBIDDEN_IMPORTS = ("sports_quant." + p.replace("/", ".") for p in LATER_PHASE_PACKAGES)
NETWORK_MODULES = {"urllib.request", "http.client", "requests", "httpx", "aiohttp", "socket"}


def _f4_modules() -> list[Path]:
    return sorted(p for package in F4_PACKAGES for p in (SRC / "data" / package).glob("*.py"))


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_no_later_phase_package_gained_code() -> None:
    for package in LATER_PHASE_PACKAGES:
        code = sorted((SRC / package).rglob("*.py"))
        assert code == [], f"{package} must remain a scaffold in F4: {code}"


def test_f4_modules_import_no_later_phase_package() -> None:
    forbidden = tuple(FORBIDDEN_IMPORTS)
    assert _f4_modules()
    for module in _f4_modules():
        bad = {name for name in _imports(module) if name.startswith(forbidden)}
        assert not bad, f"{module.name} imports {bad}"


def test_f4_data_layer_contains_no_network_client() -> None:
    for module in _f4_modules():
        assert not (_imports(module) & NETWORK_MODULES), module.name
    for script in (ROOT / "scripts" / "data").glob("*.py"):
        assert not (_imports(script) & NETWORK_MODULES), script.name


def test_only_phase_1_markets_are_canonical() -> None:
    assert {
        MarketFamily.FOOTBALL_1X2,
        MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN,
    } == PHASE_1_MARKET_FAMILIES


def test_historical_odds_block_evidence_exists() -> None:
    evidence = ROOT / source_descriptor("the_odds_api").evidence
    text = evidence.read_text(encoding="utf-8")
    assert "EXPLICITLY_BLOCKED_WITH_EVIDENCE" in text
    assert "OD-24" in text
