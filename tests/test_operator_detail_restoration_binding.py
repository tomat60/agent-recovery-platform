from __future__ import annotations

from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.operator_api import incident_operator_detail


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


def test_detail_does_not_promote_unbound_restoration():
    ledger = ActionLedger()
    action, _verification = _verified_recovery(ledger)
    ledger.record(
        EventType.RESTORATION,
        "inc-1",
        {"authorized": True, "authority_scope": "resource:other:99"},
        parent_event_ids=(action.event_id,),
    )

    detail = incident_operator_detail(ledger, incident_id="inc-1")

    assert detail["status"]["restoration_status"] == "not_recorded"
    assert detail["next_action"] == {"action": "evaluate_restoration", "authority": "none"}


def test_detail_advances_after_causally_bound_authorized_restoration():
    ledger = ActionLedger()
    _action, verification = _verified_recovery(ledger)
    ledger.record(
        EventType.RESTORATION,
        "inc-1",
        {"authorized": True, "authority_scope": "resource:contact:42"},
        parent_event_ids=(verification.event_id,),
    )

    detail = incident_operator_detail(ledger, incident_id="inc-1")

    assert detail["status"]["restoration_status"] == "recorded_authorized"
    assert detail["next_action"] == {"action": "monitor_restored_scope", "authority": "none"}
