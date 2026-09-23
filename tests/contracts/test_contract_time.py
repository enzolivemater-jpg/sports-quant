"""Temporal contract: aware timestamps, known_at/cutoff rule, missing known_at, provenance."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest
from contract_builders import CUTOFF, provenance, temporal

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.time import (
    CriticalInformationUse,
    KnownAtBasis,
    TemporalMetadata,
    require_critical_known_at,
)

TIMESTAMP_FIELDS = [
    "event_time",
    "published_at",
    "received_at",
    "valid_from",
    "valid_to",
    "expires_at",
    "known_at",
]


@pytest.mark.parametrize("field", TIMESTAMP_FIELDS)
def test_naive_timestamps_are_rejected(field: str) -> None:
    aware = getattr(temporal(), field) or CUTOFF
    with pytest.raises(ContractError) as excinfo:
        temporal(**{field: aware.replace(tzinfo=None)})
    assert excinfo.value.code == "NAIVE_DATETIME"


def test_naive_decision_cutoff_is_rejected() -> None:
    with pytest.raises(ContractError) as excinfo:
        CriticalInformationUse(temporal=temporal(), decision_cutoff_at=CUTOFF.replace(tzinfo=None))
    assert excinfo.value.code == "NAIVE_DATETIME"


def test_non_datetime_timestamps_are_rejected() -> None:
    with pytest.raises(ContractError) as excinfo:
        temporal(known_at="2026-09-20T16:00:00+00:00")
    assert excinfo.value.code == "INVALID_TYPE"


def test_non_utc_aware_timestamps_are_accepted() -> None:
    paris = timezone(timedelta(hours=2))
    value = temporal(known_at=datetime(2026, 9, 20, 18, 0, tzinfo=paris))
    assert value.known_at is not None and value.known_at.utcoffset() == timedelta(hours=2)


def test_temporal_fields_have_no_defaults() -> None:
    with pytest.raises(TypeError):
        TemporalMetadata(known_at=CUTOFF, known_at_basis=KnownAtBasis.SYSTEM_RECEIPT)  # type: ignore[call-arg]


def test_known_at_and_basis_must_be_provided_together() -> None:
    with pytest.raises(ContractError) as excinfo:
        temporal(known_at_basis=None)
    assert excinfo.value.code == "KNOWN_AT_BASIS_MISMATCH"
    with pytest.raises(ContractError):
        temporal(known_at=None)


def test_system_receipt_known_at_cannot_precede_receipt() -> None:
    received = CUTOFF - timedelta(hours=2)
    with pytest.raises(ContractError) as excinfo:
        temporal(received_at=received, known_at=received - timedelta(seconds=1))
    assert excinfo.value.code == "KNOWN_AT_BEFORE_RECEIPT"


def test_verified_source_availability_may_precede_receipt() -> None:
    received = CUTOFF - timedelta(hours=2)
    value = temporal(
        received_at=received,
        known_at=received - timedelta(hours=1),
        known_at_basis=KnownAtBasis.VERIFIED_SOURCE_AVAILABILITY,
    )
    assert value.known_at == received - timedelta(hours=1)


def test_validity_window_must_be_ordered() -> None:
    with pytest.raises(ContractError) as excinfo:
        temporal(valid_from=CUTOFF, valid_to=CUTOFF - timedelta(seconds=1))
    assert excinfo.value.code == "INVALID_VALIDITY_WINDOW"


def test_known_at_at_or_before_cutoff_is_usable() -> None:
    for known_at in (CUTOFF - timedelta(days=1), CUTOFF):
        use = CriticalInformationUse(
            temporal=temporal(received_at=known_at, known_at=known_at), decision_cutoff_at=CUTOFF
        )
        assert use.temporal.known_at == known_at


def test_known_at_after_cutoff_is_rejected() -> None:
    late = CUTOFF + timedelta(microseconds=1)
    with pytest.raises(ContractError) as excinfo:
        CriticalInformationUse(
            temporal=temporal(received_at=late, known_at=late), decision_cutoff_at=CUTOFF
        )
    assert excinfo.value.code == "KNOWN_AT_AFTER_CUTOFF"


def test_cutoff_comparison_is_instant_based_across_timezones() -> None:
    plus_two = timezone(timedelta(hours=2))
    # 19:30+02:00 is 17:30Z, i.e. before an 18:00Z cutoff.
    known = datetime(2026, 9, 20, 19, 30, tzinfo=plus_two)
    CriticalInformationUse(
        temporal=temporal(received_at=known, known_at=known), decision_cutoff_at=CUTOFF
    )
    # 20:30+02:00 is 18:30Z, i.e. after the cutoff.
    late = datetime(2026, 9, 20, 20, 30, tzinfo=plus_two)
    with pytest.raises(ContractError):
        CriticalInformationUse(
            temporal=temporal(received_at=late, known_at=late), decision_cutoff_at=CUTOFF
        )


def test_missing_known_at_is_rejected_for_critical_use() -> None:
    without_known_at = temporal(known_at=None, known_at_basis=None)
    with pytest.raises(ContractError) as excinfo:
        CriticalInformationUse(temporal=without_known_at, decision_cutoff_at=CUTOFF)
    assert excinfo.value.code == "KNOWN_AT_MISSING"
    with pytest.raises(ContractError):
        require_critical_known_at(without_known_at, CUTOFF)


def test_missing_known_at_is_not_reconstructed_from_other_timestamps() -> None:
    value = temporal(known_at=None, known_at_basis=None)
    assert value.known_at is None
    assert value.received_at is not None and value.published_at is not None


def test_critical_provenance_requires_known_at() -> None:
    with pytest.raises(ContractError) as excinfo:
        provenance(critical=True, temporal=temporal(known_at=None, known_at_basis=None))
    assert excinfo.value.code == "KNOWN_AT_MISSING"


def test_non_critical_provenance_may_lack_known_at_but_stays_unusable_for_critical_use() -> None:
    record = provenance(critical=False, temporal=temporal(known_at=None, known_at_basis=None))
    with pytest.raises(ContractError):
        CriticalInformationUse(temporal=record.temporal, decision_cutoff_at=CUTOFF)


def test_provenance_requires_received_at() -> None:
    with pytest.raises(ContractError) as excinfo:
        provenance(temporal=temporal(received_at=None))
    assert excinfo.value.code == "RECEIVED_AT_MISSING"


def test_provenance_has_no_implicit_defaults() -> None:
    base = provenance()
    with pytest.raises(TypeError):
        type(base)(source=base.source, temporal=base.temporal)  # type: ignore[call-arg]
    assert replace(base, external_id=None).external_id is None
