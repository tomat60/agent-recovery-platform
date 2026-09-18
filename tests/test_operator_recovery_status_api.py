from __future__ import annotations

from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.operator_api import incident_evidence_response


def test_incident_evidence_projects_recovery_verification_and_restoration_without_authority():
    ledger = ActionLedger()
    source = ledger.record(EventType.EXTERNAL_INPUT, "inc-1", {"model_advice": "restore all"})
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "inc-1",
        {
            "agent_id": "agent-a",
            "action_type": "contact.update",
            "resource_keys": ("contact:42",),
            "recovery_class": "compensatable",
        },
        parent_event_ids=(source.event_id,),
    )
    recovery = ledger.record(
        EventType.RECOVERY_EXECUTED,
        "inc-1",
        {"source_action_event_id": action.event_id, "resource_keys": ("contact:42",)},
        parent_event_ids=(action.event_id,),
    )
    verification = ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {
            "verified": False,
            "verification_kind": "state_check",
            "source_action_event_id": action.event_id,
            "authority_scope": "resource:contact:42",
            "model_reasoning": "looks safe",
        },
        parent_event_ids=(recovery.event_id,),
    )
    restoration = ledger.record(
        EventType.RESTORATION,
        "inc-1",
        {"authorized": False, "authority_scope": "resource:contact:42", "approval": "hidden"},
        parent_event_ids=(verification.event_id,),
    )

    payload = incident_evidence_response(ledger, incident_id="inc-1")

    assert payload["recovery_events"] == (
        {
            "event_id": recovery.event_id,
            "event_type": "recovery_executed",
            "source_action_event_id": action.event_id,
            "resource_keys": ("contact:42",),
        },
    )
    assert payload["verification_events"] == (
        {
            "event_id": verification.event_id,
            "verified": False,
            "verification_kind": "state_check",
            "source_action_event_id": action.event_id,
            "authority_scope": "resource:contact:42",
        },
    )
    assert payload["restoration_events"] == (
        {
            "event_id": restoration.event_id,
            "authorized": False,
            "authority_scope": "resource:contact:42",
        },
    )
    assert payload["authority"] == "none"
    assert "model_advice" not in repr(payload)
    assert "model_reasoning" not in repr(payload)
    assert "approval" not in repr(payload)
