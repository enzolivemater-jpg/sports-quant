"""Shared primitives for SPORTS QUANT domain contracts.

Every contract is an immutable, keyword-only dataclass without field defaults, so no
value (and in particular no provenance or temporal value) is ever filled in implicitly.
Field types are enforced at construction, timestamps must be timezone-aware, and
serialization is deterministic. Deserialization is strict: unknown keys, missing keys,
unknown enum values and naive timestamps are rejected.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import re
import types
from collections.abc import Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Self, Union, get_args, get_origin, get_type_hints

_IDENTIFIER_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


class ContractError(ValueError):
    """Raised when a value violates a domain contract.

    ``code`` is a stable, machine-readable identifier of the violated rule.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


class CanonicalEnum(StrEnum):
    """String enum whose serialized form is exactly its canonical value."""

    @classmethod
    def parse(cls, value: object) -> Self:
        """Return the member whose value is exactly ``value``; reject anything else.

        No case folding, trimming or alias resolution happens here. Legacy aliases,
        where approved, are handled by dedicated normalization functions.
        """

        if isinstance(value, cls):
            return value
        if isinstance(value, str) and not isinstance(value, CanonicalEnum):
            try:
                return cls(value)
            except ValueError:
                pass
        raise ContractError(
            "UNKNOWN_ENUM_VALUE",
            f"{value!r} is not a canonical {cls.__name__} value",
        )


def require_aware_datetime(value: object, field: str) -> datetime:
    if not isinstance(value, datetime):
        raise ContractError("INVALID_TYPE", f"{field} must be a datetime, got {value!r}")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ContractError("NAIVE_DATETIME", f"{field} must be timezone-aware")
    return value


def instant(value: datetime) -> datetime:
    """Return ``value`` as a UTC instant for ordering/equality comparisons.

    Python compares two aware datetimes that share the same ``tzinfo`` object by wall
    time, ignoring ``fold``, so two readings inside a DST fall-back hour can compare
    in the wrong order or as equal. Every temporal comparison in the contracts goes
    through this function so that it is instant-based.
    """

    return value.astimezone(UTC)


def require_non_empty(value: str, field: str) -> None:
    if not value.strip():
        raise ContractError("EMPTY_VALUE", f"{field} must be a non-empty string")


def require_probability(value: float, field: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ContractError("PROBABILITY_OUT_OF_BOUNDS", f"{field} must be in [0, 1]")


def require_identifier(value: str, field: str) -> None:
    """Deterministic identifier: UPPER_SNAKE_CASE, e.g. reason codes and gate ids."""

    if not _IDENTIFIER_RE.fullmatch(value):
        raise ContractError(
            "INVALID_IDENTIFIER",
            f"{field} must be an UPPER_SNAKE_CASE identifier, got {value!r}",
        )


def require_unique(values: tuple[Any, ...], field: str) -> None:
    if len(set(values)) != len(values):
        raise ContractError("DUPLICATE_VALUE", f"{field} must not contain duplicates")


_FIELD_TYPES: dict[type, dict[str, Any]] = {}


def _field_types(cls: type) -> dict[str, Any]:
    cached = _FIELD_TYPES.get(cls)
    if cached is None:
        hints = get_type_hints(cls)
        cached = {field.name: hints[field.name] for field in dataclasses.fields(cls)}
        _FIELD_TYPES[cls] = cached
    return cached


def _is_optional(tp: Any) -> bool:
    return get_origin(tp) in (Union, types.UnionType)


def _check_value(tp: Any, value: object, path: str) -> None:
    if _is_optional(tp):
        if value is None:
            return
        (inner,) = (arg for arg in get_args(tp) if arg is not type(None))
        _check_value(inner, value, path)
        return
    if get_origin(tp) is tuple:
        if not isinstance(value, tuple):
            raise ContractError("INVALID_TYPE", f"{path} must be a tuple")
        (item_type, _ellipsis) = get_args(tp)
        for index, item in enumerate(value):
            _check_value(item_type, item, f"{path}[{index}]")
        return
    if tp is datetime:
        require_aware_datetime(value, path)
        return
    if tp is float:
        if type(value) is not float:
            raise ContractError("INVALID_TYPE", f"{path} must be a float, got {value!r}")
        if not math.isfinite(value):
            raise ContractError("NON_FINITE_NUMBER", f"{path} must be finite")
        return
    if tp is int:
        if type(value) is not int:
            raise ContractError("INVALID_TYPE", f"{path} must be an int, got {value!r}")
        return
    if tp is bool:
        if type(value) is not bool:
            raise ContractError("INVALID_TYPE", f"{path} must be a bool, got {value!r}")
        return
    if tp is str:
        if type(value) is not str:
            raise ContractError("INVALID_TYPE", f"{path} must be a str, got {value!r}")
        return
    if isinstance(tp, type) and issubclass(tp, (CanonicalEnum, Contract)):
        if not isinstance(value, tp):
            raise ContractError("INVALID_TYPE", f"{path} must be a {tp.__name__}, got {value!r}")
        return
    raise TypeError(f"Unsupported contract field type at {path}: {tp!r}")


def _encode(value: object) -> Any:
    if isinstance(value, Contract):
        return {
            field.name: _encode(getattr(value, field.name))
            for field in dataclasses.fields(value)  # type: ignore[arg-type]
        }
    if isinstance(value, CanonicalEnum):
        return value.value
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    if isinstance(value, float):
        # Normalizes -0.0 to 0.0 so equal contracts always serialize identically.
        return value + 0.0
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, tuple):
        return [_encode(item) for item in value]
    raise TypeError(f"Unsupported contract value: {value!r}")


def _decode(tp: Any, value: object, path: str) -> Any:
    if _is_optional(tp):
        if value is None:
            return None
        (inner,) = (arg for arg in get_args(tp) if arg is not type(None))
        return _decode(inner, value, path)
    if get_origin(tp) is tuple:
        if not isinstance(value, list):
            raise ContractError("INVALID_TYPE", f"{path} must be a list")
        (item_type, _ellipsis) = get_args(tp)
        return tuple(
            _decode(item_type, item, f"{path}[{index}]") for index, item in enumerate(value)
        )
    if tp is datetime:
        if not isinstance(value, str):
            raise ContractError("INVALID_TYPE", f"{path} must be an ISO-8601 string")
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ContractError("INVALID_TIMESTAMP", f"{path} is not ISO-8601") from exc
        return require_aware_datetime(parsed, path)
    if isinstance(tp, type) and issubclass(tp, CanonicalEnum):
        return tp.parse(value)
    if isinstance(tp, type) and issubclass(tp, Contract):
        if not isinstance(value, Mapping):
            raise ContractError("INVALID_TYPE", f"{path} must be an object")
        return tp._from_mapping(value, path)
    # Scalars are validated by the constructed contract's own type checks.
    return value


class Contract:
    """Base class for immutable, validated, deterministically serializable contracts."""

    def __post_init__(self) -> None:
        for name, tp in _field_types(type(self)).items():
            _check_value(tp, getattr(self, name), f"{type(self).__name__}.{name}")
        self._validate()

    def _validate(self) -> None:
        """Contract-specific invariants; runs after field types are enforced."""

    def to_dict(self) -> dict[str, Any]:
        encoded: dict[str, Any] = _encode(self)
        return encoded

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

    def content_digest(self) -> str:
        """SHA-256 of the canonical JSON form; stable across processes and hosts."""

        return hashlib.sha256(self.to_json().encode("ascii")).hexdigest()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        return cls._from_mapping(data, cls.__name__)

    @classmethod
    def from_json(cls, text: str) -> Self:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ContractError("INVALID_TYPE", f"{cls.__name__} JSON must be an object")
        return cls.from_dict(data)

    @classmethod
    def _from_mapping(cls, data: Mapping[str, Any], path: str) -> Self:
        types_by_name = _field_types(cls)
        unknown = sorted(set(data) - set(types_by_name))
        if unknown:
            raise ContractError("UNKNOWN_FIELD", f"{path} has unknown fields {unknown}")
        missing = sorted(set(types_by_name) - set(data))
        if missing:
            raise ContractError("MISSING_FIELD", f"{path} is missing fields {missing}")
        kwargs = {
            name: _decode(tp, data[name], f"{path}.{name}") for name, tp in types_by_name.items()
        }
        return cls(**kwargs)
