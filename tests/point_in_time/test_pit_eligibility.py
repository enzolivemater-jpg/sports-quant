"""PIT eligibility of single versions."""

from __future__ import annotations

import itertools
from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from pit_builders import CUTOFF, at, data_state, version

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.data_state import (
    ConflictState,
    FreshnessState,
    QualityState,
    VerificationState,
)
from sports_quant.contracts.time import CriticalInformationUse, KnownAtBasis
from sports_quant.data.point_in_time.eligibility import (
    F2_KNOWN_AT_CODE_TO_REASON,
    PitEligibility,
    PitRejectionReason,
    evaluate_eligibility,
    rejection_reasons,
)

R = PitRejectionReason


def test_known_before_cutoff_is_eligible() -> None:
    result = evaluate_eligibility(version(at(10)), CUTOFF)
    assert result.eligible and result.reasons == ()
    assert result.known_at == at(10)
    assert result.known_at_basis is KnownAtBasis.SYSTEM_RECEIPT


def test_known_exactly_at_cutoff_is_eligible() -> None:
    assert evaluate_eligibility(version(CUTOFF), CUTOFF).eligible


def test_known_after_cutoff_is_rejected() -> None:
    result = evaluate_eligibility(version(CUTOFF + timedelta(microseconds=1)), CUTOFF)
    assert not result.eligible
    assert result.reasons == (R.KNOWN_AFTER_CUTOFF,)


def test_missing_known_at_is_rejected() -> None:
    record = version(None)
    assert record.provenance.temporal.known_at is None
    assert rejection_reasons(record, CUTOFF) == (R.MISSING_KNOWN_AT,)


def test_missing_known_at_is_never_substituted_by_other_timestamps() -> None:
    record = version(None, received_at=at(1), published_at=at(1), valid_from=at(1))
    result = evaluate_eligibility(record, CUTOFF)
    assert not result.eligible and result.known_at is None
    assert R.MISSING_KNOWN_AT in result.reasons


def test_naive_cutoff_is_rejected() -> None:
    with pytest.raises(ContractError) as excinfo:
        evaluate_eligibility(version(at(10)), CUTOFF.replace(tzinfo=None))
    assert excinfo.value.code == "NAIVE_DATETIME"


def test_naive_record_timestamps_cannot_reach_the_kernel() -> None:
    with pytest.raises(ContractError) as excinfo:
        version(at(10).replace(tzinfo=None))
    assert excinfo.value.code == "NAIVE_DATETIME"


def test_cutoff_comparison_is_instant_based_across_offsets() -> None:
    plus_two = timezone(timedelta(hours=2))
    before = datetime(2024, 8, 16, 13, 59, tzinfo=plus_two)  # 11:59Z
    after = datetime(2024, 8, 16, 14, 1, tzinfo=plus_two)  # 12:01Z
    assert evaluate_eligibility(version(before), CUTOFF).eligible
    assert not evaluate_eligibility(version(after), CUTOFF).eligible
    cutoff_plus_two = CUTOFF.astimezone(plus_two)
    assert evaluate_eligibility(version(at(11)), cutoff_plus_two).eligible


def test_dst_fold_known_after_cutoff_is_rejected() -> None:
    # Regression (see contracts DST fold fix): same ZoneInfo, fall-back hour.
    london = ZoneInfo("Europe/London")
    cutoff = datetime(2024, 10, 27, 1, 45, fold=0, tzinfo=london)  # 00:45Z
    known = datetime(2024, 10, 27, 1, 15, fold=1, tzinfo=london)  # 01:15Z
    assert rejection_reasons(version(known), cutoff) == (R.KNOWN_AFTER_CUTOFF,)
    assert evaluate_eligibility(version(cutoff), known).eligible


def test_dst_fold_validity_bounds_are_instant_based() -> None:
    london = ZoneInfo("Europe/London")
    cutoff = datetime(2024, 10, 27, 1, 45, fold=0, tzinfo=london)  # 00:45Z
    later = datetime(2024, 10, 27, 1, 15, fold=1, tzinfo=london)  # 01:15Z
    earlier = cutoff - timedelta(hours=2)
    assert rejection_reasons(version(earlier, valid_from=later), cutoff) == (
        R.NOT_YET_VALID_AT_CUTOFF,
    )
    assert rejection_reasons(version(earlier, expires_at=later), cutoff) == ()


def test_valid_from_after_cutoff_is_rejected_and_inclusive_at_cutoff() -> None:
    assert rejection_reasons(version(at(10), valid_from=at(13)), CUTOFF) == (
        R.NOT_YET_VALID_AT_CUTOFF,
    )
    assert rejection_reasons(version(at(10), valid_from=CUTOFF), CUTOFF) == ()


def test_valid_to_is_inclusive() -> None:
    assert rejection_reasons(version(at(10), valid_to=CUTOFF), CUTOFF) == ()
    assert rejection_reasons(version(at(10), valid_to=at(11.99)), CUTOFF) == (R.EXPIRED_AT_CUTOFF,)


def test_expires_at_is_exclusive() -> None:
    assert rejection_reasons(version(at(10), expires_at=CUTOFF), CUTOFF) == (R.EXPIRED_AT_CUTOFF,)
    assert (
        rejection_reasons(version(at(10), expires_at=CUTOFF + timedelta(microseconds=1)), CUTOFF)
        == ()
    )


def test_valid_to_and_expires_at_report_one_expiry_reason() -> None:
    record = version(at(10), valid_to=at(11), expires_at=at(11))
    assert rejection_reasons(record, CUTOFF) == (R.EXPIRED_AT_CUTOFF,)


def test_absent_validity_bounds_impose_nothing() -> None:
    record = version(at(10))
    temporal = record.provenance.temporal
    assert (temporal.valid_from, temporal.valid_to, temporal.expires_at) == (None, None, None)
    assert evaluate_eligibility(record, CUTOFF).eligible


def test_missing_revision_identity_is_unresolved() -> None:
    assert rejection_reasons(version(at(10), revision_id=None), CUTOFF) == (
        R.SOURCE_VERSION_UNRESOLVED,
    )


def test_all_reasons_are_collected_in_canonical_order() -> None:
    record = version(None, revision_id=None, valid_from=at(13), valid_to=at(14), received_at=at(1))
    assert rejection_reasons(record, CUTOFF) == (
        R.MISSING_KNOWN_AT,
        R.NOT_YET_VALID_AT_CUTOFF,
        R.SOURCE_VERSION_UNRESOLVED,
    )
    late = version(at(15), revision_id=None, expires_at=at(11))
    assert rejection_reasons(late, CUTOFF) == (
        R.KNOWN_AFTER_CUTOFF,
        R.EXPIRED_AT_CUTOFF,
        R.SOURCE_VERSION_UNRESOLVED,
    )


def test_current_state_snapshot_cannot_masquerade_as_historical() -> None:
    # Fetched today; the provider claims historical publication/validity. Only known_at
    # counts, and a SYSTEM_RECEIPT known_at is the fetch time.
    fetched_today = datetime(2026, 9, 23, 9, 0, tzinfo=UTC)
    record = version(fetched_today, published_at=at(8), valid_from=at(8))
    assert rejection_reasons(record, CUTOFF) == (R.KNOWN_AFTER_CUTOFF,)


def test_kernel_known_at_rule_is_exactly_f2_rule() -> None:
    assert set(F2_KNOWN_AT_CODE_TO_REASON.values()) == {R.MISSING_KNOWN_AT, R.KNOWN_AFTER_CUTOFF}
    offsets = [timedelta(hours=h) for h in (-5, -1)] + [
        timedelta(0),
        timedelta(microseconds=1),
        timedelta(hours=3),
    ]
    for offset in offsets:
        record = version(CUTOFF + offset)
        try:
            CriticalInformationUse(temporal=record.provenance.temporal, decision_cutoff_at=CUTOFF)
            f2_usable = True
        except ContractError:
            f2_usable = False
        assert f2_usable == evaluate_eligibility(record, CUTOFF).eligible


ALL_STATES = list(itertools.product(QualityState, FreshnessState, VerificationState, ConflictState))


@pytest.mark.parametrize(
    "template",
    [
        {"known_at": at(10)},
        {"known_at": at(13)},
        {"known_at": None},
        {"known_at": at(10), "valid_from": at(13)},
        {"known_at": at(10), "expires_at": at(11)},
        {"known_at": at(10), "revision_id": None},
    ],
    ids=["eligible", "late", "missing", "not-yet-valid", "expired", "unresolved"],
)
def test_data_state_never_changes_eligibility(template: dict[str, object]) -> None:
    template = dict(template)
    known_at = template.pop("known_at")
    assert known_at is None or isinstance(known_at, datetime)
    outcomes = {
        rejection_reasons(
            version(known_at, state=data_state(*axes), **template),  # type: ignore[arg-type]
            CUTOFF,
        )
        for axes in ALL_STATES
    }
    assert len(outcomes) == 1


def test_pit_eligibility_contract_invariants() -> None:
    result = evaluate_eligibility(version(at(13)), CUTOFF)
    payload = result.to_dict()
    payload["eligible"] = True
    with pytest.raises(ContractError):
        PitEligibility.from_dict(payload)
    payload = result.to_dict()
    payload["reasons"] = ["SOURCE_VERSION_UNRESOLVED", "KNOWN_AFTER_CUTOFF"]
    with pytest.raises(ContractError):
        PitEligibility.from_dict(payload)
    assert PitEligibility.from_json(result.to_json()) == result
