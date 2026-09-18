from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict
from typing import Any

from .ledger import ActionLedger, EventType
from .readiness import RuntimeBindingKey, evaluate_recovery_readiness
from .recovery_contract import RecoveryContract
from .runtime_binding import TrustedRuntimeBinding


def recovery_readiness_response(
    declarations: Iterable[RecoveryContract],
    *,
    runtime_bindings: Mapping[RuntimeBindingKey, TrustedRuntimeBinding],
) -> dict[str, Any]:
    """Return a deterministic, read-only operator view of recovery readiness.

    This boundary exposes coverage evidence and blockers only. It does not return executable
    runtime bindings, approvals, callables, or any other object that can grant action authority.
    """

    readiness = evaluate_recovery_readiness(
        declarations,
        runtime_bindings=runtime_bindings,
    )
    payload = asdict(readiness)
    payload["recoverability_fraction"] = readiness.recoverability_fraction
    payload["ready"] = not readiness.blockers
    payload["authority"] = "none"
    return payload


def incident_evidence_response(ledger: ActionLedger, *, incident_id: str) -> dict[str, Any]:
    """Return integrity-checked incident evidence without exposing runtime authority.

    The response is deliberately evidence-only: it projects selected deterministic ledger
    facts for an operator and never returns approvals, executors, callables, model narration,
    or an object that can release containment or restore authority.
    """

    ledger.verify_integrity()
    events = ledger.events(incident_id=incident_id)
    if not events:
        raise KeyError(incident_id)

    executed_actions = []
    residual_effects = []
    recovery_events = []
    verification_events = []
    restoration_events = []
    for event in events:
        if event.event_type is EventType.ACTION_EXECUTED:
            executed_actions.append(
                {
                    "event_id": event.event_id,
                    "action_type": event.payload.get("action_type"),
                    "agent_id": event.payload.get("agent_id"),
                    "resource_keys": event.payload.get("resource_keys", ()),
                    "recovery_class": event.payload.get("recovery_class"),
                    "observation_provenance_digest": event.payload.get(
                        "observation_provenance_digest"
                    ),
                }
            )
        elif event.event_type is EventType.RESIDUAL_EFFECT:
            residual_effects.append(
                {
                    "event_id": event.event_id,
                    "effect": event.payload.get("effect"),
                    "irreversible": event.payload.get("irreversible"),
                }
            )
        elif event.event_type in {
            EventType.RECOVERY_PLANNED,
            EventType.RECOVERY_EXECUTED,
            EventType.RECOVERY_FAILED,
            EventType.RECOVERY_FORKED,
            EventType.RECONCILIATION_PLANNED,
            EventType.RECONCILIATION_EXECUTED,
            EventType.RECONCILIATION_FAILED,
        }:
            recovery_events.append(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "source_action_event_id": event.payload.get("source_action_event_id"),
                    "resource_keys": event.payload.get("resource_keys", ()),
                }
            )
        elif event.event_type is EventType.VERIFICATION:
            verification_events.append(
                {
                    "event_id": event.event_id,
                    "verified": event.payload.get("verified"),
                    "verification_kind": event.payload.get("verification_kind"),
                    "source_action_event_id": event.payload.get("source_action_event_id"),
                    "authority_scope": event.payload.get("authority_scope"),
                }
            )
        elif event.event_type is EventType.RESTORATION:
            restoration_events.append(
                {
                    "event_id": event.event_id,
                    "authorized": event.payload.get("authorized"),
                    "authority_scope": event.payload.get("authority_scope"),
                }
            )

    active_containment = tuple(
        {
            "event_id": hold.event_id,
            "scope": hold.payload.get("scope"),
        }
        for hold in ledger.active_containment_holds(incident_id=incident_id)
    )

    return {
        "incident_id": incident_id,
        "integrity_verified": True,
        "event_count": len(events),
        "active_containment": active_containment,
        "executed_actions": tuple(executed_actions),
        "recovery_events": tuple(recovery_events),
        "verification_events": tuple(verification_events),
        "restoration_events": tuple(restoration_events),
        "residual_effects": tuple(residual_effects),
        "authority": "none",
    }
