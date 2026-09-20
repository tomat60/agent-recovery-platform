from __future__ import annotations

from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.operator_status_evidence import incident_status_evidence_response


def _verified_recovery(ledger: ActionLedger):
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "inc-1",
        {"action_type": "contact.update", "recovery_class": "reversible"},
    )
    recovery = ledger.record(
        EventType.RECOVERY_EXECUTED,
        "inc-1",
        {"action_event_id": action.event_id},
        parent_event_ids=(action.event_id,),
    )
    verification = ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {
            "verification_kind": "state_check",
            "verified": True,
            "source_action_event_id": action.event_id,
        },
        parent_event_ids=(recovery.event_id,),
    )
    return action, verification


def test_next_action_does_not_promote_unbound_restoration():
    ledger = ActionLedger()
    action, _verification = _verified_recovery(ledger)
    ledger.record(
        EventType.RESTORATION,
        "inc-1",
        {"authorized": True, "authority_scope": "resource:other:99"},
        parent_event_ids=(action.event_id,),
    )

    payload = incident_status_evidence_response(ledger, incident_id="inc-1")

    assert payload["status"]["restoration_status"] == "not_recorded"
    assert payload["next_action"] == {"action": "evaluate_restoration", "authority": "none"}


def test_next_action_advances_only_after_bound_authorized_restoration():
    ledger = ActionLedger()
    _action, verification = _verified_recovery(ledger)
    restoration = ledger.record(
        EventType.RESTORATION,
        "inc-1",
        {"authorized": True, "authority_scope": "resource:contact:42"},
        parent_event_ids=(verification.event_id,),
    )

    payload = incident_status_evidence_response(ledger, incident_id="inc-1")

    assert payload["evidence_refs"]["restoration_event_id"] == restoration.event_id
    assert payload["next_action"] == {"action": "monitor_restored_scope", "authority": "none"}
