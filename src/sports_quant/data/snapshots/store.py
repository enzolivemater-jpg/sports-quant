"""Write-once, content-addressed filesystem store for raw captures.

Layout under ``root``::

    payloads/<sha256>          raw payload bytes, addressed by their SHA-256
    captures/<capture_id>.json canonical JSON of the ``RawCapture``

Nothing is ever overwritten. Writing an object that already exists succeeds only
if the stored bytes are identical (idempotent re-ingestion); anything else is an
integrity error. Every read re-verifies the content address, so a tampered or
truncated file fails visibly instead of feeding the pipeline.
"""

from __future__ import annotations

import os
from pathlib import Path

from sports_quant.contracts.common import ContractError
from sports_quant.data.snapshots.raw import RawCapture, sha256_hex


class RawSnapshotStore:
    def __init__(self, root: Path) -> None:
        self._payloads = root / "payloads"
        self._captures = root / "captures"

    def put(self, capture: RawCapture, payload: bytes) -> None:
        """Store ``payload`` and its capture metadata; never overwrite either."""

        if sha256_hex(payload) != capture.payload_sha256 or len(payload) != capture.payload_size:
            raise ContractError("PAYLOAD_MISMATCH", "payload does not match its capture")
        _write_once(self._payloads / capture.payload_sha256, payload)
        _write_once(
            self._captures / f"{capture.capture_id}.json", capture.to_json().encode("ascii")
        )

    def payload(self, payload_sha256: str) -> bytes:
        path = self._payloads / payload_sha256
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            raise ContractError("RAW_PAYLOAD_MISSING", f"no payload {payload_sha256}") from None
        if sha256_hex(data) != payload_sha256:
            raise ContractError("RAW_STORE_INTEGRITY", f"payload {payload_sha256} is corrupted")
        return data

    def captures(self) -> tuple[RawCapture, ...]:
        """Every stored capture, ordered by ``capture_id``."""

        if not self._captures.is_dir():
            return ()
        result = []
        for path in sorted(self._captures.glob("*.json")):
            stored = RawCapture.from_json(path.read_text(encoding="ascii"))
            if f"{stored.capture_id}.json" != path.name:
                raise ContractError("RAW_STORE_INTEGRITY", f"capture {path.name} is corrupted")
            result.append(stored)
        return tuple(result)

    def load(self) -> tuple[tuple[RawCapture, bytes], ...]:
        """Every capture with its verified payload, ordered by ``capture_id``."""

        return tuple((stored, self.payload(stored.payload_sha256)) for stored in self.captures())


def _write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        if path.read_bytes() != data:
            raise ContractError(
                "RAW_STORE_OVERWRITE", f"{path.name} exists with different content"
            ) from None
        return
    path.chmod(0o444)
