from __future__ import annotations

import json
import os
from pathlib import Path
from threading import RLock
from typing import Any

from .ledger import ActionLedger, EventType, LedgerEvent


class EvidenceStoreError(ValueError):
    """Raised when persisted evidence cannot be trusted or reconstructed."""


class JsonlEvidenceStore:
    """Small pilot-grade durable store for the deterministic evidence ledger.

    The file is append-only from this API's perspective. Each row contains the complete
    chained LedgerEvent, so restart reconstruction re-runs ledger integrity and causal
    validation. This is intentionally not an authorization store or a production WORM log.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = RLock()

    def append(self, event: LedgerEvent) -> None:
        row = {
            "event_type": event.event_type.value,
            "incident_id": event.incident_id,
            "payload": dict(event.payload),
            "parent_event_ids": list(event.parent_event_ids),
            "event_id": event.event_id,
            "occurred_at": event.occurred_at,
            "previous_hash": event.previous_hash,
            "event_hash": event.event_hash,
        }
        encoded = json.dumps(row, sort_keys=True, separators=(",", ":"), default=str)
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(encoded + "\n")
                handle.flush()
                os.fsync(handle.fileno())

    def load_ledger(self) -> ActionLedger:
        ledger = ActionLedger()
        if not self.path.exists():
            return ledger
        with self._lock:
            try:
                rows = self.path.read_text(encoding="utf-8").splitlines()
            except OSError as exc:
                raise EvidenceStoreError("unable to read persisted evidence") from exc

        for line_number, line in enumerate(rows, start=1):
            if not line.strip():
                raise EvidenceStoreError(f"blank evidence row at line {line_number}")
            try:
                raw: dict[str, Any] = json.loads(line)
                event = LedgerEvent(
                    event_type=EventType(raw["event_type"]),
                    incident_id=raw["incident_id"],
                    payload=raw["payload"],
                    parent_event_ids=tuple(raw.get("parent_event_ids", ())),
                    event_id=raw["event_id"],
                    occurred_at=raw["occurred_at"],
                    previous_hash=raw["previous_hash"],
                    event_hash=raw["event_hash"],
                )
                ledger.append(event)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise EvidenceStoreError(
                    f"invalid or tampered evidence at line {line_number}"
                ) from exc
        ledger.verify_integrity()
        return ledger

    def append_from_ledger(self, ledger: ActionLedger, event_id: str) -> LedgerEvent:
        """Persist one already-admitted event without granting or changing authority."""

        ledger.verify_integrity()
        event = ledger.get(event_id)
        self.append(event)
        return event
