from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from json import dumps
from threading import RLock
from typing import Any
from uuid import uuid4


class EventType(str, Enum):
    EXTERNAL_INPUT = "external_input"
    TOOL_OUTPUT = "tool_output"
    MEMORY_READ = "memory_read"
    AGENT_HANDOFF = "agent_handoff"
    ACTION_INTENT = "action_intent"
    ACTION_EXECUTED = "action_executed"
    ACTION_BLOCKED = "action_blocked"
    AUTHORITY_CONSUMED = "authority_consumed"
    CONTAINMENT = "containment"
    RECOVERY_PLANNED = "recovery_planned"
    RECOVERY_EXECUTED = "recovery_executed"
    RECOVERY_FAILED = "recovery_failed"
    RECOVERY_FORKED = "recovery_forked"
    RECONCILIATION_PLANNED = "reconciliation_planned"
    RECONCILIATION_EXECUTED = "reconciliation_executed"
    RECONCILIATION_FAILED = "reconciliation_failed"
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
    previous_hash: str = ""
    event_hash: str = ""


class LedgerIntegrityError(ValueError):
    """Raised when an event refers to invalid causal evidence or breaks the ledger chain."""


def _event_digest(event: LedgerEvent, *, previous_hash: str) -> str:
    canonical = {
        "event_id": event.event_id,
        "event_type": event.event_type.value,
        "incident_id": event.incident_id,
        "payload": dict(event.payload),
        "parent_event_ids": tuple(event.parent_event_ids),
        "occurred_at": event.occurred_at,
        "previous_hash": previous_hash,
    }
    normalized = dumps(canonical, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(normalized.encode("utf-8")).hexdigest()


def _detached_event(event: LedgerEvent) -> LedgerEvent:
    return replace(event, payload=deepcopy(dict(event.payload)))


class ActionLedger:
    """Append-only tamper-evident ledger used by the deterministic benchmark.

    The hash chain is a prototype integrity primitive, not a replacement for a production
    WORM store, signed transparency log, or external anchoring service.
    """

    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []
        self._ids: set[str] = set()
        self._lock = RLock()

    @property
    def head_hash(self) -> str:
        with self._lock:
            return self._events[-1].event_hash if self._events else ""

    def _event_by_id_unlocked(self, event_id: str) -> LedgerEvent | None:
        return next((event for event in self._events if event.event_id == event_id), None)

    def _validate_append_policy(self, event: LedgerEvent) -> None:
        """Fail closed on security-sensitive claims regardless of append entry point."""

        payload = event.payload
        if (
            event.event_type is EventType.VERIFICATION
            and payload.get("verification_kind") == "adversarial_replay"
            and payload.get("verified") is True
        ):
            source_action_event_id = payload.get("source_action_event_id")
            authority_scope = payload.get("authority_scope")
            source_incident_id = payload.get("source_incident_id")
            if not isinstance(source_action_event_id, str) or not source_action_event_id:
                raise ValueError("positive replay requires source action identity")
            if not isinstance(authority_scope, str) or not authority_scope:
                raise ValueError("positive replay requires authority scope")
            if source_incident_id != event.incident_id:
                raise ValueError("positive replay source incident mismatch")
            source_action = self._event_by_id_unlocked(source_action_event_id)
            if source_action is None or source_action.event_type is not EventType.ACTION_EXECUTED:
                raise ValueError("positive replay requires an executed source action")
            if source_action.incident_id != event.incident_id:
                raise ValueError("positive replay source action incident mismatch")
            if source_action_event_id not in event.parent_event_ids:
                raise ValueError("positive replay must causally bind the source action")
            source_agent = source_action.payload.get("agent_id")
            if isinstance(source_agent, str) and authority_scope == f"agent:{source_agent}":
                raise ValueError("positive replay cannot authorize restoration of its source agent")

        if event.event_type is EventType.CONTAINMENT and payload.get("active") is False:
            scope = payload.get("scope")
            restoration_event_id = payload.get("restoration_event_id")
            released_hold_event_id = payload.get("released_hold_event_id")
            if not isinstance(scope, str) or not scope:
                raise ValueError("containment release requires scope")
            if not isinstance(restoration_event_id, str) or not restoration_event_id:
                raise ValueError("containment release requires restoration evidence")
            if not isinstance(released_hold_event_id, str) or not released_hold_event_id:
                raise ValueError("containment release requires exact hold identity")

            restoration = self._event_by_id_unlocked(restoration_event_id)
            hold = self._event_by_id_unlocked(released_hold_event_id)
            if restoration is None or restoration.event_type is not EventType.RESTORATION:
                raise ValueError("containment release restoration evidence is invalid")
            if restoration.incident_id != event.incident_id:
                raise ValueError("containment release restoration incident mismatch")
            if restoration.payload.get("authorized") is not True:
                raise ValueError("containment release requires authorized restoration")
            if restoration.payload.get("authority_scope") != scope:
                raise ValueError("containment release restoration scope mismatch")
            if not self._events or self._events[-1].event_hash != restoration.event_hash:
                raise ValueError("containment release restoration is stale or already consumed")

            if hold is None or hold.event_type is not EventType.CONTAINMENT:
                raise ValueError("containment release hold evidence is invalid")
            if hold.incident_id != event.incident_id:
                raise ValueError("containment release hold incident mismatch")
            if hold.payload.get("active") is not True or hold.payload.get("scope") != scope:
                raise ValueError("containment release hold does not match scope")
            if released_hold_event_id not in self._active_containment_holds_unlocked():
                raise ValueError("containment release hold is no longer active")
            if restoration_event_id not in event.parent_event_ids:
                raise ValueError("containment release must depend on restoration evidence")
            if released_hold_event_id not in event.parent_event_ids:
                raise ValueError("containment release must depend on the exact hold")

    def append(self, event: LedgerEvent) -> LedgerEvent:
        with self._lock:
            if event.event_id in self._ids:
                raise LedgerIntegrityError(f"duplicate event_id: {event.event_id}")
            missing_parents = [parent for parent in event.parent_event_ids if parent not in self._ids]
            if missing_parents:
                raise LedgerIntegrityError(f"missing parent event(s): {missing_parents}")

            self._validate_append_policy(event)

            previous_hash = self._events[-1].event_hash if self._events else ""
            if event.previous_hash not in ("", previous_hash):
                raise LedgerIntegrityError("event previous_hash does not match ledger head")

            detached = replace(event, payload=deepcopy(dict(event.payload)))
            expected_hash = _event_digest(detached, previous_hash=previous_hash)
            if detached.event_hash not in ("", expected_hash):
                raise LedgerIntegrityError("event hash does not match canonical event content")

            chained = replace(detached, previous_hash=previous_hash, event_hash=expected_hash)
            self._events.append(chained)
            self._ids.add(chained.event_id)
            return _detached_event(chained)

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
                payload=deepcopy(dict(payload)),
                parent_event_ids=tuple(parent_event_ids),
            )
        )

    def authority_consumed(self, approval_id: str) -> bool:
        with self._lock:
            return any(
                event.event_type is EventType.AUTHORITY_CONSUMED
                and event.payload.get("approval_id") == approval_id
                for event in self._events
            )

    def record_authority_consumption_once(
        self,
        incident_id: str,
        payload: Mapping[str, Any],
        *,
        parent_event_ids: Iterable[str] = (),
    ) -> LedgerEvent | None:
        approval_id = payload.get("approval_id")
        if not isinstance(approval_id, str) or not approval_id:
            raise ValueError("authority consumption requires approval_id")
        with self._lock:
            if self.authority_consumed(approval_id):
                return None
            return self.record(
                EventType.AUTHORITY_CONSUMED,
                incident_id,
                payload,
                parent_event_ids=parent_event_ids,
            )

    def _active_containment_holds_unlocked(self) -> dict[str, LedgerEvent]:
        active: dict[str, LedgerEvent] = {}
        for event in self._events:
            if event.event_type is not EventType.CONTAINMENT:
                continue
            scope = event.payload.get("scope")
            if not isinstance(scope, str) or not scope:
                continue
            if event.payload.get("active") is True:
                active[event.event_id] = event
                continue
            if event.payload.get("active") is not False:
                continue

            released_hold_id = event.payload.get("released_hold_event_id")
            if isinstance(released_hold_id, str) and released_hold_id:
                active.pop(released_hold_id, None)
                continue

            matching = [
                hold_id
                for hold_id, hold in active.items()
                if hold.incident_id == event.incident_id
                and hold.payload.get("scope") == scope
            ]
            if matching:
                active.pop(matching[-1], None)
        return active

    def active_containment_holds(
        self,
        *,
        incident_id: str | None = None,
        scope: str | None = None,
    ) -> tuple[LedgerEvent, ...]:
        """Return authoritative outstanding containment holds from retained ledger state."""

        self.verify_integrity()
        with self._lock:
            selected = []
            for hold in self._active_containment_holds_unlocked().values():
                if incident_id is not None and hold.incident_id != incident_id:
                    continue
                if scope is not None and hold.payload.get("scope") != scope:
                    continue
                selected.append(_detached_event(hold))
            return tuple(selected)

    def latest_active_containment_hold(
        self,
        *,
        incident_id: str,
        scope: str,
    ) -> LedgerEvent | None:
        holds = self.active_containment_holds(incident_id=incident_id, scope=scope)
        return holds[-1] if holds else None

    def is_scope_contained(self, scope: str) -> bool:
        """Containment is effective while any incident has an outstanding hold on scope."""

        return bool(self.active_containment_holds(scope=scope))

    def events(self, *, incident_id: str | None = None) -> tuple[LedgerEvent, ...]:
        with self._lock:
            if incident_id is None:
                selected = self._events
            else:
                selected = [event for event in self._events if event.incident_id == incident_id]
            return tuple(_detached_event(event) for event in selected)

    def get(self, event_id: str) -> LedgerEvent:
        with self._lock:
            for event in self._events:
                if event.event_id == event_id:
                    return _detached_event(event)
        raise KeyError(event_id)

    def verify_integrity(self) -> bool:
        """Verify ordering, hashes, uniqueness and causal parent existence for the full ledger."""

        with self._lock:
            seen_ids: set[str] = set()
            previous_hash = ""
            for event in self._events:
                if event.event_id in seen_ids:
                    raise LedgerIntegrityError(f"duplicate event_id: {event.event_id}")
                missing_parents = [parent for parent in event.parent_event_ids if parent not in seen_ids]
                if missing_parents:
                    raise LedgerIntegrityError(f"missing parent event(s): {missing_parents}")
                if event.previous_hash != previous_hash:
                    raise LedgerIntegrityError("ledger hash-chain discontinuity")
                expected_hash = _event_digest(event, previous_hash=previous_hash)
                if event.event_hash != expected_hash:
                    raise LedgerIntegrityError("ledger event content does not match event_hash")
                seen_ids.add(event.event_id)
                previous_hash = event.event_hash
            return True
