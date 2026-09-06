from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from .ledger import ActionLedger, EventType, LedgerEvent


_REPLAY_FINGERPRINT_TYPES = {
    EventType.EXTERNAL_INPUT,
    EventType.TOOL_OUTPUT,
    EventType.MEMORY_READ,
    EventType.AGENT_HANDOFF,
    EventType.ACTION_INTENT,
    EventType.ACTION_EXECUTED,
    EventType.ACTION_BLOCKED,
    EventType.AUTHORITY_CONSUMED,
}


class RestorationDecision(str, Enum):
    RESTORED = "restored"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ReplayVerification:
    verified: bool
    source_fingerprint: str
    event: LedgerEvent


@dataclass(frozen=True)
class RestorationResult:
    decision: RestorationDecision
    event: LedgerEvent
    reason: str | None = None


def incident_fingerprint(ledger: ActionLedger, *, incident_id: str) -> str:
    """Hash the immutable attack/action evidence that a replay must be bound to.

    Recovery, verification and restoration events are intentionally excluded. If a new
    external input, handoff, authority consumption or action appears after a replay was
    verified, the fingerprint changes and the old replay evidence becomes stale automatically.
    """

    evidence = []
    for event in ledger.events(incident_id=incident_id):
        if event.event_type not in _REPLAY_FINGERPRINT_TYPES:
            continue
        evidence.append(
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "payload": dict(event.payload),
                "parent_event_ids": event.parent_event_ids,
            }
        )
    normalized = json.dumps(evidence, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def record_replay_verification(
    ledger: ActionLedger,
    *,
    incident_id: str,
    trigger_event_id: str,
    replay_id: str,
    attack_blocked: bool,
    evidence_complete: bool,
    unsafe_side_effects: tuple[str, ...] = (),
) -> ReplayVerification:
    """Persist a replay verdict bound to the exact source-incident evidence."""

    trigger = ledger.get(trigger_event_id)
    if trigger.incident_id != incident_id:
        raise ValueError("replay trigger must belong to the source incident")

    side_effects = tuple(sorted(str(item) for item in unsafe_side_effects))
    source_fingerprint = incident_fingerprint(ledger, incident_id=incident_id)
    verified = attack_blocked and evidence_complete and not side_effects
    event = ledger.record(
        EventType.VERIFICATION,
        incident_id,
        {
            "verification_kind": "adversarial_replay",
            "source_incident_id": incident_id,
            "source_fingerprint": source_fingerprint,
            "trigger_event_id": trigger_event_id,
            "replay_id": replay_id,
            "attack_blocked": attack_blocked,
            "evidence_complete": evidence_complete,
            "unsafe_side_effects": side_effects,
            "verified": verified,
        },
        parent_event_ids=(trigger_event_id,),
    )
    return ReplayVerification(verified=verified, source_fingerprint=source_fingerprint, event=event)


class RestorationGate:
    """Fail-closed authority restoration gate backed by fresh adversarial replay evidence."""

    def __init__(self, ledger: ActionLedger) -> None:
        self.ledger = ledger

    def authorize(
        self,
        *,
        incident_id: str,
        authority_scope: str,
        replay_event_id: str,
    ) -> RestorationResult:
        reason: str | None = None
        replay_event: LedgerEvent | None = None

        try:
            replay_event = self.ledger.get(replay_event_id)
        except KeyError:
            reason = "missing_replay_evidence"

        if replay_event is not None and replay_event.incident_id != incident_id:
            reason = "replay_incident_mismatch"
        elif replay_event is not None and replay_event.event_type is not EventType.VERIFICATION:
            reason = "event_is_not_verification"
        elif replay_event is not None and replay_event.payload.get("verification_kind") != "adversarial_replay":
            reason = "verification_is_not_adversarial_replay"
        elif replay_event is not None and replay_event.payload.get("source_incident_id") != incident_id:
            reason = "replay_source_mismatch"
        elif replay_event is not None:
            current_fingerprint = incident_fingerprint(self.ledger, incident_id=incident_id)
            if replay_event.payload.get("source_fingerprint") != current_fingerprint:
                reason = "stale_replay_evidence"
            elif replay_event.payload.get("verified") is not True:
                reason = "replay_not_verified"

        authorized = reason is None and replay_event is not None
        parents = (
            (replay_event.event_id,)
            if replay_event is not None and replay_event.incident_id == incident_id
            else ()
        )
        event = self.ledger.record(
            EventType.RESTORATION,
            incident_id,
            {
                "authority_scope": authority_scope,
                "authorized": authorized,
                "replay_event_id": replay_event_id,
                "reason": reason,
            },
            parent_event_ids=parents,
        )
        return RestorationResult(
            decision=RestorationDecision.RESTORED if authorized else RestorationDecision.BLOCKED,
            event=event,
            reason=reason,
        )
