from __future__ import annotations

from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.operator_api import incident_operator_detail, incident_status_summary


def test_adversarial_replay_does_not_satisfy_local_recovery_verification():
    ledger = ActionLedger()
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "inc-1",
        {"action_type": "contact.update", "recovery_class": "reversible"},
    )
    ledger.record(
        EventType.RECOVERY_EXECUTED,
        "inc-1",
        {"action_event_id": action.event_id},
        parent_event_ids=(action.event_id,),
    )
    replay = ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {
            "verification_kind": "adversarial_replay",
            "verified": True,
            "source_action_event_id": action.event_id,
            "source_incident_id": "inc-1",
            "authority_scope": "resource:contact:42",
        },
        parent_event_ids=(action.event_id,),
    )

    summary = incident_status_summary(ledger, incident_id="inc-1")
    detail = incident_operator_detail(ledger, incident_id="inc-1")

    assert summary["verification_status"] == "not_recorded"
    assert detail["next_action"] == {
        "action": "verify_recovered_state",
        "authority": "none",
    }
    assert detail["recovery_candidates"][0]["status"] == "recovery_recorded"
    assert replay.event_id in {event["event_id"] for event in detail["verification"]}
    assert detail["authority"] == "none"


def test_unbound_positive_verification_does_not_satisfy_recovered_action_verification():
    ledger = ActionLedger()
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "inc-1",
        {"action_type": "contact.update", "recovery_class": "reversible"},
    )
    ledger.record(
        EventType.RECOVERY_EXECUTED,
        "inc-1",
        {"action_event_id": action.event_id},
        parent_event_ids=(action.event_id,),
    )
    ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {"verified": True, "model_reasoning": "looks safe"},
    )

    summary = incident_status_summary(ledger, incident_id="inc-1")
    detail = incident_operator_detail(ledger, incident_id="inc-1")

    assert summary["verification_status"] == "not_recorded"
    assert detail["next_action"] == {
        "action": "verify_recovered_state",
        "authority": "none",
    }
    assert detail["recovery_candidates"][0]["status"] == "recovery_recorded"
    assert "model_reasoning" not in repr(detail)
