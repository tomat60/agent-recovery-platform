from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from json import dumps

from .ledger import ActionLedger, EventType, LedgerEvent, LedgerIntegrityError
from .replay import ReplayEvidence

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

_RECOVERY_FINGERPRINT_TYPES = {
    EventType.CONTAINMENT,
    EventType.RECOVERY_PLANNED,
    EventType.RECOVERY_EXECUTED,
    EventType.RECOVERY_FAILED,
    EventType.RECOVERY_FORKED,
    EventType.RECONCILIATION_PLANNED,
    EventType.RECONCILIATION_EXECUTED,
    EventType.RECONCILIATION_FAILED,
    EventType.RESIDUAL_EFFECT,
}


class RestorationDecision(str, Enum):
    RESTORED = "restored"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ReplayVerification:
    verified: bool
    source_fingerprint: str
    recovery_fingerprint: str
    event: LedgerEvent


@dataclass(frozen=True)
class RestorationResult:
    decision: RestorationDecision
    event: LedgerEvent
    reason: str | None = None


def _fingerprint_for_types(
    ledger: ActionLedger,
    *,
    incident_id: str,
    event_types: set[EventType],
) -> str:
    evidence = []
    for event in ledger.events(incident_id=incident_id):
        if event.event_type not in event_types:
            continue
        evidence.append(
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "payload": dict(event.payload),
                "parent_event_ids": event.parent_event_ids,
                "event_hash": event.event_hash,
            }
        )
    normalized = dumps(evidence, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(normalized.encode("utf-8")).hexdigest()


def incident_fingerprint(ledger: ActionLedger, *, incident_id: str) -> str:
    return _fingerprint_for_types(
        ledger,
        incident_id=incident_id,
        event_types=_REPLAY_FINGERPRINT_TYPES,
    )


def recovery_fingerprint(ledger: ActionLedger, *, incident_id: str) -> str:
    return _fingerprint_for_types(
        ledger,
        incident_id=incident_id,
        event_types=_RECOVERY_FINGERPRINT_TYPES,
    )


def record_replay_verification(
    ledger: ActionLedger,
    *,
    incident_id: str,
    evidence: ReplayEvidence,
) -> ReplayVerification:
    """Persist a verdict derived from isolated replay evidence, never caller booleans."""

    ledger.verify_integrity()
    observation = evidence.derive(source_ledger=ledger, source_incident_id=incident_id)
    trigger = ledger.get(observation.source_trigger_event_id)
    source_fingerprint = incident_fingerprint(ledger, incident_id=incident_id)
    recovery_state_fingerprint = recovery_fingerprint(ledger, incident_id=incident_id)
    event = ledger.record(
        EventType.VERIFICATION,
        incident_id,
        {
            "verification_kind": "adversarial_replay",
            "evidence_source": "isolated_replay_lab",
            "source_incident_id": incident_id,
            "source_fingerprint": source_fingerprint,
            "recovery_fingerprint": recovery_state_fingerprint,
            "ledger_head_before_verification": ledger.head_hash,
            "replay_ledger_head": observation.replay_ledger_head,
            "trigger_event_id": observation.source_trigger_event_id,
            "replay_id": observation.replay_id,
            "attack_blocked": observation.entry_action_blocked,
            "evidence_complete": observation.evidence_complete,
            "unsafe_side_effects": tuple(sorted(observation.executed_side_effect_event_ids)),
            "verified": observation.verified,
        },
        parent_event_ids=(trigger.event_id,),
    )
    return ReplayVerification(
        verified=observation.verified,
        source_fingerprint=source_fingerprint,
        recovery_fingerprint=recovery_state_fingerprint,
        event=event,
    )


class RestorationGate:
    """Fail-closed authority restoration gate backed by fresh replay evidence."""

    def __init__(self, ledger: ActionLedger) -> None:
        self.ledger = ledger

    def _integrity_failure_result(
        self,
        *,
        incident_id: str,
        authority_scope: str,
        replay_event_id: str,
    ) -> RestorationResult:
        event = LedgerEvent(
            EventType.RESTORATION,
            incident_id,
            {
                "authority_scope": authority_scope,
                "authorized": False,
                "replay_event_id": replay_event_id,
                "reason": "ledger_integrity_failure",
                "persisted": False,
            },
        )
        return RestorationResult(
            decision=RestorationDecision.BLOCKED,
            event=event,
            reason="ledger_integrity_failure",
        )

    def authorize(
        self,
        *,
        incident_id: str,
        authority_scope: str,
        replay_event_id: str,
    ) -> RestorationResult:
        try:
            self.ledger.verify_integrity()
        except LedgerIntegrityError:
            return self._integrity_failure_result(
                incident_id=incident_id,
                authority_scope=authority_scope,
                replay_event_id=replay_event_id,
            )

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
        elif replay_event is not None and replay_event.payload.get("evidence_source") != "isolated_replay_lab":
            reason = "untrusted_replay_evidence_source"
        elif replay_event is not None and replay_event.payload.get("source_incident_id") != incident_id:
            reason = "replay_source_mismatch"
        elif replay_event is not None:
            current_source = incident_fingerprint(self.ledger, incident_id=incident_id)
            current_recovery = recovery_fingerprint(self.ledger, incident_id=incident_id)
            if replay_event.payload.get("source_fingerprint") != current_source:
                reason = "stale_replay_evidence"
            elif replay_event.payload.get("recovery_fingerprint") != current_recovery:
                reason = "stale_recovery_evidence"
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
                "ledger_head_before_restoration": self.ledger.head_hash,
            },
            parent_event_ids=parents,
        )
        return RestorationResult(
            decision=RestorationDecision.RESTORED if authorized else RestorationDecision.BLOCKED,
            event=event,
            reason=reason,
        )
