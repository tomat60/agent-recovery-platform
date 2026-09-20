from __future__ import annotations

from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.operator_status_evidence import incident_status_evidence_response


def test_status_evidence_refs_are_local_and_non_authorizing():
    ledger = ActionLedger()
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
    replay = ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {
            "verification_kind": "adversarial_replay",
            "verified": True,
            "source_action_event_id": action.event_id,
            "authority_scope": "resource:contact:42",
            "source_incident_id": "inc-1",
        },
        parent_event_ids=(action.event_id,),
    )
    verification = ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {
            "verification_kind": "state_check",
            "verified": True,
            "source_action_event_id": action.event_id,
            "approval": "must-not-leak",
        },
        parent_event_ids=(recovery.event_id,),
    )
    restoration = ledger.record(
        EventType.RESTORATION,
        "inc-1",
        {"authorized": True, "authority_scope": "resource:contact:42"},
        parent_event_ids=(verification.event_id,),
    )

    payload = incident_status_evidence_response(ledger, incident_id="inc-1")

    assert payload["status"]["verification_status"] == "verified"
    assert payload["evidence_refs"] == {
        "recovery_event_id": recovery.event_id,
        "verification_event_id": verification.event_id,
        "restoration_event_id": restoration.event_id,
    }
    assert payload["evidence_refs"]["verification_event_id"] != replay.event_id
    assert payload["authority"] == "none"
    assert "must-not-leak" not in repr(payload)


def test_status_evidence_refs_do_not_promote_replay_or_unbound_verification():
    ledger = ActionLedger()
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
    ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {
            "verification_kind": "adversarial_replay",
            "verified": True,
            "source_action_event_id": action.event_id,
            "authority_scope": "resource:contact:42",
            "source_incident_id": "inc-1",
        },
        parent_event_ids=(action.event_id,),
    )
    ledger.record(EventType.VERIFICATION, "inc-1", {"verified": True})

    payload = incident_status_evidence_response(ledger, incident_id="inc-1")

    assert payload["status"]["verification_status"] == "not_recorded"
    assert payload["evidence_refs"] == {
        "recovery_event_id": recovery.event_id,
        "verification_event_id": None,
        "restoration_event_id": None,
    }
    assert payload["authority"] == "none"


def test_status_evidence_refs_reject_unbound_restoration():
    ledger = ActionLedger()
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
    unrelated = ledger.record(
        EventType.RESTORATION,
        "inc-1",
        {"authorized": True, "authority_scope": "resource:other:99"},
        parent_event_ids=(action.event_id,),
    )

    payload = incident_status_evidence_response(ledger, incident_id="inc-1")

    assert payload["evidence_refs"]["verification_event_id"] == verification.event_id
    assert payload["evidence_refs"]["restoration_event_id"] is None
    assert unrelated.event_id not in payload["evidence_refs"].values()
