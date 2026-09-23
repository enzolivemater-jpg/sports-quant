"""Reproducibility references, deterministic serialization and strict deserialization.

Also guards serialization hazards identified while designing F2 (-0.0, int vs float,
raw strings vs enum members, mutable lists).
"""

from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from contract_builders import (
    COMMIT,
    CUTOFF,
    artifact,
    assessment,
    data_state,
    entity,
    evaluation,
    gate,
    market,
    probability,
    provenance,
    reproducibility,
    temporal,
)

from sports_quant.contracts.common import Contract, ContractError
from sports_quant.contracts.edge import EdgeAssessment
from sports_quant.contracts.entity import EntityKind, EntityRef, ProviderEntityRef
from sports_quant.contracts.reproducibility import (
    ArtifactKind,
    CodeVersion,
    ReproducibilityRef,
)
from sports_quant.contracts.time import CriticalInformationUse


def _samples() -> list[Contract]:
    return [
        temporal(),
        data_state(),
        provenance(),
        entity(),
        EntityRef(
            canonical_id=entity(),
            provider_refs=(
                ProviderEntityRef(provider_id="p", kind=EntityKind.TEAM, external_id="1"),
            ),
        ),
        CriticalInformationUse(temporal=temporal(), decision_cutoff_at=CUTOFF),
        market(),
        probability(),
        EdgeAssessment.from_probabilities(probability(), 0.5),
        gate(),
        reproducibility(),
        evaluation(),
        assessment(),
    ]


@pytest.mark.parametrize("contract", _samples(), ids=lambda contract: type(contract).__name__)
def test_json_round_trip_is_lossless_and_stable(contract: Contract) -> None:
    text = contract.to_json()
    restored = type(contract).from_json(text)
    assert restored == contract
    assert restored.to_json() == text
    assert restored.content_digest() == contract.content_digest()


@pytest.mark.parametrize("contract", _samples(), ids=lambda contract: type(contract).__name__)
def test_serialization_is_canonical_json(contract: Contract) -> None:
    text = contract.to_json()
    assert text == json.dumps(json.loads(text), sort_keys=True, separators=(",", ":"))
    assert text.isascii()


@pytest.mark.parametrize("contract", _samples(), ids=lambda contract: type(contract).__name__)
def test_unknown_fields_are_rejected(contract: Contract) -> None:
    payload = contract.to_dict()
    payload["unexpected"] = 1
    with pytest.raises(ContractError) as excinfo:
        type(contract).from_dict(payload)
    assert excinfo.value.code == "UNKNOWN_FIELD"


def test_digest_is_stable_across_processes() -> None:
    script = (
        "import sys; sys.path.insert(0, 'tests/contracts');"
        "from contract_builders import evaluation; print(evaluation().content_digest())"
    )
    outputs = {
        subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=True,
            env={"PYTHONHASHSEED": seed, "PATH": ""},
            cwd=Path(__file__).resolve().parents[2],
        ).stdout.strip()
        for seed in ("0", "1", "12345")
    }
    assert outputs == {evaluation().content_digest()}


def test_equal_instants_in_different_timezones_serialize_identically() -> None:
    plus_two = timezone(timedelta(hours=2))
    utc_value = temporal()
    shifted = dataclasses.replace(
        utc_value,
        known_at=utc_value.known_at.astimezone(plus_two) if utc_value.known_at else None,
    )
    assert shifted == utc_value
    assert shifted.to_json() == utc_value.to_json()


def test_naive_timestamp_string_is_rejected_on_deserialization() -> None:
    payload = temporal().to_dict()
    payload["known_at"] = "2026-09-20T16:00:00"
    with pytest.raises(ContractError) as excinfo:
        type(temporal()).from_dict(payload)
    assert excinfo.value.code == "NAIVE_DATETIME"


def test_malformed_timestamp_string_is_rejected() -> None:
    payload = temporal().to_dict()
    payload["known_at"] = "yesterday"
    with pytest.raises(ContractError) as excinfo:
        type(temporal()).from_dict(payload)
    assert excinfo.value.code == "INVALID_TIMESTAMP"


def test_missing_nested_field_is_rejected() -> None:
    payload = provenance().to_dict()
    del payload["temporal"]["known_at_basis"]
    with pytest.raises(ContractError) as excinfo:
        type(provenance()).from_dict(payload)
    assert excinfo.value.code == "MISSING_FIELD"


def test_reproducibility_reference_serialization() -> None:
    ref = reproducibility()
    assert ref.to_dict() == {
        "run_id": "run-1",
        "code_version": {"commit": COMMIT},
        "data_ref": {"kind": "SNAPSHOT", "identifier": "snapshot", "version": "1"},
        "config_ref": {"kind": "CONFIGURATION", "identifier": "config", "version": "1"},
        "model_refs": [{"kind": "MODEL", "identifier": "model", "version": "1"}],
    }
    assert ReproducibilityRef.from_dict(ref.to_dict()) == ref


@pytest.mark.parametrize("commit", ["abc123", COMMIT.upper(), COMMIT + "0", "main", ""])
def test_code_version_requires_full_commit_sha(commit: str) -> None:
    with pytest.raises(ContractError) as excinfo:
        CodeVersion(commit=commit)
    assert excinfo.value.code == "INVALID_COMMIT_REF"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("data_ref", artifact(ArtifactKind.MODEL)),
        ("config_ref", artifact(ArtifactKind.DATASET)),
        ("model_refs", (artifact(ArtifactKind.CONFIGURATION),)),
    ],
)
def test_reproducibility_reference_kinds_are_enforced(field: str, value: object) -> None:
    with pytest.raises(ContractError) as excinfo:
        dataclasses.replace(reproducibility(), **{field: value})
    assert excinfo.value.code == "ARTIFACT_KIND_MISMATCH"


def test_model_refs_may_be_empty_before_models_exist() -> None:
    assert dataclasses.replace(reproducibility(), model_refs=()).model_refs == ()


# --- Serialization hazard guards -----------------------------------------------------


def test_negative_zero_serializes_like_zero() -> None:
    # -0.0 == 0.0 but json.dumps(-0.0) == "-0.0"; equal contracts must share one JSON form.
    zero = EdgeAssessment.from_probabilities(probability(p_calibrated=0.5, p_safe=0.5), 0.5)
    negative_zero = dataclasses.replace(
        zero, p_market_no_vig=0.5, edge_calibrated=-0.0, edge_safe=-0.0
    )
    assert negative_zero == zero
    assert negative_zero.to_json() == zero.to_json()


def test_int_and_bool_are_rejected_for_float_fields() -> None:
    # int 1 == float 1.0 but they serialize differently; bool is an int subclass.
    for value in (1, 0, True):
        with pytest.raises(ContractError) as excinfo:
            probability(p_raw=value)
        assert excinfo.value.code == "INVALID_TYPE"


def test_raw_string_is_rejected_where_enum_member_is_required() -> None:
    # StrEnum members compare equal to plain strings; raw strings must not bypass parsing.
    with pytest.raises(ContractError):
        data_state(quality="VALID")


def test_list_is_rejected_where_immutable_tuple_is_required() -> None:
    with pytest.raises(ContractError):
        dataclasses.replace(reproducibility(), model_refs=[artifact(ArtifactKind.MODEL)])


def test_decoded_datetime_preserves_the_instant() -> None:
    value = CriticalInformationUse(temporal=temporal(), decision_cutoff_at=CUTOFF)
    restored = CriticalInformationUse.from_json(value.to_json())
    assert restored.decision_cutoff_at == CUTOFF
    assert isinstance(restored.decision_cutoff_at, datetime)
