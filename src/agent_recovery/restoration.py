from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from json import dumps

from .ledger import ActionLedger, EventType, LedgerEvent, LedgerIntegrityError
from .lineage import current_generation, uncovered_residual_effect_event_ids
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
    """Persist a single-use verdict bound to replay execution-time provenance."""

    ledger.verify_integrity()
    if evidence.source_incident_id != incident_id:
        raise ValueError("replay evidence incident mismatch")
    if evidence.source_ledger_head_at_run != ledger.head_hash:
        raise ValueError("replay evidence is stale or has already been consumed")
    generation = current_generation(ledger, incident_id=incident_id)
    if evidence.recovery_generation_at_run != generation:
        raise ValueError("replay evidence recovery generation is stale")

    observation = evidence.derive(source_ledger=ledger, source_incident_id=incident_id)
    trigger = ledger.get(observation.source_trigger_event_id)
    source_action = ledger.get(observation.source_action_event_id)
    source_fingerprint = incident_fingerprint(ledger, incident_id=incident_id)
    recovery_state_fingerprint = recovery_fingerprint(ledger, incident_id=incident_id)
    event = ledger.record(
        EventType.VERIFICATION,
        incident_id,
        {
            "verification_kind": "adversarial_replay",
            "evidence_source": "isolated_replay_lab",
            "source_incident_id": incident_id,
            "source_action_event_id": observation.source_action_event_id,
            "authority_scope": observation.release_scope,
            "recovery_generation": generation,
            "source_ledger_head_at_replay": evidence.source_ledger_head_at_run,
            "source_fingerprint": source_fingerprint,
            "recovery_fingerprint": recovery_state_fingerprint,
            "ledger_head_before_verification": ledger.head_hash,
            "replay_ledger_head": observation.replay_ledger_head,
            "trigger_event_id": observation.source_trigger_event_id,
            "replay_id": observation.replay_id,
            "attack_blocked": observation.entry_action_blocked_by_containment,
            "source_action_matches": observation.source_action_matches,
            "replay_action_matches": observation.replay_action_matches,
            "evidence_complete": observation.evidence_complete,
            "unsafe_side_effects": tuple(sorted(observation.executed_side_effect_event_ids)),
            "verified": observation.verified,
        },
        parent_event_ids=(trigger.event_id, source_action.event_id),
    )
    return ReplayVerification(
        verified=observation.verified,
        source_fingerprint=source_fingerprint,
        recovery_fingerprint=recovery_state_fingerprint,
        event=event,
    )


def _scope_is_actively_contained(
    ledger: ActionLedger,
    *,
    incident_id: str,
    authority_scope: str,
) -> bool:
    active = False
    seen = False
    for event in ledger.events(incident_id=incident_id):
        if event.event_type is not EventType.CONTAINMENT:
            continue
        if event.payload.get("scope") != authority_scope:
            continue
        seen = True
        active = event.payload.get("active") is True
    return seen and active


def _latest_replay_event_for_scope(
    ledger: ActionLedger,
    *,
    incident_id: str,
    authority_scope: str,
) -> LedgerEvent | None:
    relevant = [
        event
        for event in ledger.events(incident_id=incident_id)
        if event.event_type is EventType.VERIFICATION
        and event.payload.get("verification_kind") == "adversarial_replay"
        and event.payload.get("authority_scope") == authority_scope
    ]
    return relevant[-1] if relevant else None


def _local_recovery_obligations_complete(ledger: ActionLedger, *, incident_id: str) -> bool:
    events = ledger.events(incident_id=incident_id)
    verified_actions = {
        str(event.payload["action_event_id"])
        for event in events
        if event.event_type is EventType.VERIFICATION
        and event.payload.get("verification_kind") != "adversarial_replay"
        and event.payload.get("verified") is True
        and isinstance(event.payload.get("action_event_id"), str)
    }
    reconciled_actions = {
        str(event.payload["compromised_action_event_id"])
        for event in events
        if event.event_type is EventType.VERIFICATION
        and event.payload.get("verification_kind") == "shared_state_reconciliation"
        and event.payload.get("verified") is True
        and isinstance(event.payload.get("compromised_action_event_id"), str)
    }
    residual_actions = {
        str(event.payload["action_event_id"])
        for event in events
        if event.event_type is EventType.RESIDUAL_EFFECT
        and isinstance(event.payload.get("action_event_id"), str)
    }

    for event in events:
        if event.event_type is not EventType.ACTION_EXECUTED:
            continue
        recovery_class = event.payload.get("recovery_class")
        if recovery_class in {"reversible", "compensatable"}:
            if event.event_id not in verified_actions and event.event_id not in reconciled_actions:
                return False
        elif recovery_class == "irreversible":
            if event.event_id not in residual_actions:
                return False
        else:
            return False
    return True


class RestorationGate:
    """Fail-closed authority restoration gate backed by current recovery and faithful replay."""

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
        elif replay_event is not None and replay_event.payload.get("authority_scope") != authority_scope:
            reason = "replay_scope_mismatch"
        elif not _scope_is_actively_contained(
            self.ledger,
            incident_id=incident_id,
            authority_scope=authority_scope,
        ):
            reason = "scope_not_actively_contained"
        elif not _local_recovery_obligations_complete(self.ledger, incident_id=incident_id):
            reason = "recovery_obligations_incomplete"
        elif uncovered_residual_effect_event_ids(self.ledger, incident_id=incident_id):
            reason = "residual_effects_not_disposed"
        elif replay_event is not None:
            latest = _latest_replay_event_for_scope(
                self.ledger,
                incident_id=incident_id,
                authority_scope=authority_scope,
            )
            if latest is None or latest.event_id != replay_event.event_id:
                reason = "replay_evidence_superseded"
            elif replay_event.payload.get("recovery_generation") != current_generation(
                self.ledger,
                incident_id=incident_id,
            ):
                reason = "stale_recovery_generation"
            else:
                current_source = incident_fingerprint(self.ledger, incident_id=incident_id)
                current_recovery = recovery_fingerprint(self.ledger, incident_id=incident_id)
                if replay_event.payload.get("source_fingerprint") != current_source:
                    reason = "stale_replay_evidence"
                elif replay_event.payload.get("recovery_fingerprint") != current_recovery:
                    reason = "stale_recovery_evidence"
                elif replay_event.payload.get("source_action_matches") is not True:
                    reason = "replay_source_action_mismatch"
                elif replay_event.payload.get("replay_action_matches") is not True:
                    reason = "replay_action_mismatch"
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
