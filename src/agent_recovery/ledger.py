from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Mapping
from uuid import uuid4


class EventType(str, Enum):
    ACTION_INTENT = "action_intent"
    ACTION_EXECUTED = "action_executed"
    ACTION_BLOCKED = "action_blocked"
    CONTAINMENT = "containment"
    RECOVERY_PLANNED = "recovery_planned"
    RECOVERY_EXECUTED = "recovery_executed"
    RECOVERY_FAILED = "recovery_failed"
    VERIFICATION = "verification"
    RESIDUAL_EFFECT = "residual_effect"
    RESTORATION = "restoration"


@dataclass(frozen=True)
class LedgerEvent:
    event_type: EventType
    incident_id: str
    payload: Mapping[str, Any]
    parent_event_ids: tuple[str, ...] = ()
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    )


class LedgerIntegrityError(ValueError):
    """Raised when an event refers to invalid causal evidence."""


class ActionLedger:
    """Append-only in-memory ledger used by the first deterministic benchmark."""

    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []
        self._ids: set[str] = set()

    def append(self, event: LedgerEvent) -> LedgerEvent:
        if event.event_id in self._ids:
            raise LedgerIntegrityError(f"duplicate event_id: {event.event_id}")
        missing_parents = [parent for parent in event.parent_event_ids if parent not in self._ids]
        if missing_parents:
            raise LedgerIntegrityError(f"missing parent event(s): {missing_parents}")
        self._events.append(event)
        self._ids.add(event.event_id)
        return event

    def record(
        self,
        event_type: EventType,
        incident_id: str,
        payload: Mapping[str, Any],
        *,
        parent_event_ids: Iterable[str] = (),
    ) -> LedgerEvent:
        return self.append(
            LedgerEvent(
                event_type=event_type,
                incident_id=incident_id,
                payload=dict(payload),
                parent_event_ids=tuple(parent_event_ids),
            )
        )

    def events(self, *, incident_id: str | None = None) -> tuple[LedgerEvent, ...]:
        if incident_id is None:
            return tuple(self._events)
        return tuple(event for event in self._events if event.incident_id == incident_id)

    def get(self, event_id: str) -> LedgerEvent:
        for event in self._events:
            if event.event_id == event_id:
                return event
        raise KeyError(event_id)
