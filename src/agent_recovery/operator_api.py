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
    """Return integrity-checked incident evidence without exposing runtime authority."""

    ledger.verify_integrity()
    events = ledger.events(incident_id=incident_id)
    if not events:
        raise KeyError(incident_id)

    incident_event_ids = {event.event_id for event in events}
    causal_nodes = tuple(
        {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "parent_event_ids": tuple(
                parent_id for parent_id in event.parent_event_ids if parent_id in incident_event_ids
            ),
        }
        for event in events
    )
    causal_edges = tuple(
        {"parent_event_id": parent_id, "event_id": event.event_id}
        for event in events
        for parent_id in event.parent_event_ids
        if parent_id in incident_event_ids
    )

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
                    "observation_provenance_digest": event.payload.get("observation_provenance_digest"),
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
        {"event_id": hold.event_id, "scope": hold.payload.get("scope")}
        for hold in ledger.active_containment_holds(incident_id=incident_id)
    )

    return {
        "incident_id": incident_id,
        "integrity_verified": True,
        "event_count": len(events),
        "causal_graph": {"nodes": causal_nodes, "edges": causal_edges},
        "active_containment": active_containment,
        "executed_actions": tuple(executed_actions),
        "recovery_events": tuple(recovery_events),
        "verification_events": tuple(verification_events),
        "restoration_events": tuple(restoration_events),
        "residual_effects": tuple(residual_effects),
        "authority": "none",
    }


def incident_status_summary(ledger: ActionLedger, *, incident_id: str) -> dict[str, Any]:
    """Project compact operator workflow status from verified incident evidence only."""

    evidence = incident_evidence_response(ledger, incident_id=incident_id)
    recovery_events = evidence["recovery_events"]
    verification_events = evidence["verification_events"]
    restoration_events = evidence["restoration_events"]

    recovery_status = "not_started"
    if recovery_events:
        latest_recovery_type = recovery_events[-1]["event_type"]
        if latest_recovery_type in {"recovery_failed", "reconciliation_failed"}:
            recovery_status = "failed"
        elif latest_recovery_type in {"recovery_executed", "reconciliation_executed"}:
            recovery_status = "executed"
        else:
            recovery_status = "planned"

    verification_status = "not_recorded"
    if verification_events:
        verification_status = (
            "verified" if verification_events[-1]["verified"] is True else "failed_or_unverified"
        )

    restoration_status = "not_recorded"
    if restoration_events:
        restoration_status = (
            "recorded_authorized" if restoration_events[-1]["authorized"] is True else "recorded_denied"
        )

    return {
        "incident_id": incident_id,
        "integrity_verified": evidence["integrity_verified"],
        "containment_active": bool(evidence["active_containment"]),
        "executed_action_count": len(evidence["executed_actions"]),
        "recovery_status": recovery_status,
        "verification_status": verification_status,
        "restoration_status": restoration_status,
        "irreversible_residual_count": sum(
            residual["irreversible"] is True for residual in evidence["residual_effects"]
        ),
        "authority": "none",
    }


def _operator_next_action(summary: Mapping[str, Any]) -> dict[str, str]:
    """Return deterministic workflow guidance, never executable authority."""

    if summary["recovery_status"] == "failed":
        action = "investigate_recovery_failure"
    elif summary["recovery_status"] in {"not_started", "planned"}:
        action = "complete_recovery"
    elif summary["verification_status"] != "verified":
        action = "verify_recovered_state"
    elif summary["irreversible_residual_count"]:
        action = "review_irreversible_residuals"
    elif summary["restoration_status"] == "not_recorded":
        action = "evaluate_restoration"
    elif summary["restoration_status"] == "recorded_denied":
        action = "keep_contained"
    else:
        action = "monitor_restored_scope"
    return {"action": action, "authority": "none"}


def incident_operator_detail(ledger: ActionLedger, *, incident_id: str) -> dict[str, Any]:
    """Compose the incident-response detail surface from verified evidence only.

    The detail is intentionally a read model. Recorded restoration decisions remain evidence and
    never become executable authority through this boundary.
    """

    evidence = incident_evidence_response(ledger, incident_id=incident_id)
    summary = incident_status_summary(ledger, incident_id=incident_id)
    return {
        "incident_id": incident_id,
        "status": summary,
        "next_action": _operator_next_action(summary),
        "causal_graph": evidence["causal_graph"],
        "active_containment": evidence["active_containment"],
        "side_effects": evidence["executed_actions"],
        "recovery": evidence["recovery_events"],
        "verification": evidence["verification_events"],
        "residuals": evidence["residual_effects"],
        "restoration": evidence["restoration_events"],
        "authority": "none",
    }
