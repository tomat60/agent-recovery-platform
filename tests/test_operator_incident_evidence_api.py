from __future__ import annotations

from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.operator_api import incident_evidence_response


def test_incident_evidence_response_is_deterministic_and_non_authorizing():
    ledger = ActionLedger()
    source = ledger.record(
        EventType.EXTERNAL_INPUT,
        "inc-1",
        {"source": "sandbox", "model_advice": "restore everything"},
    )
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "inc-1",
        {
            "agent_id": "agent-a",
            "action_type": "contact.update",
            "resource_keys": ("contact:42",),
            "recovery_class": "reversible",
            "observation_provenance_digest": "sha256:abc",
        },
        parent_event_ids=(source.event_id,),
    )
    hold = ledger.record(
        EventType.CONTAINMENT,
        "inc-1",
        {"active": True, "scope": "resource:contact:42"},
        parent_event_ids=(action.event_id,),
    )
    ledger.record(
        EventType.RESIDUAL_EFFECT,
        "inc-1",
        {"effect": "notification_already_sent", "irreversible": True},
        parent_event_ids=(action.event_id,),
    )
    ledger.record(EventType.EXTERNAL_INPUT, "inc-2", {"source": "other"})

    payload = incident_evidence_response(ledger, incident_id="inc-1")

    assert payload["incident_id"] == "inc-1"
    assert payload["authority"] == "none"
    assert payload["integrity_verified"] is True
    assert payload["event_count"] == 4
    assert payload["active_containment"] == (
        {"event_id": hold.event_id, "scope": "resource:contact:42"},
    )
    assert payload["executed_actions"] == (
        {
            "event_id": action.event_id,
            "action_type": "contact.update",
            "agent_id": "agent-a",
            "resource_keys": ("contact:42",),
            "recovery_class": "reversible",
            "observation_provenance_digest": "sha256:abc",
        },
    )
    assert payload["residual_effects"] == (
        {
            "event_id": payload["residual_effects"][0]["event_id"],
            "effect": "notification_already_sent",
            "irreversible": True,
        },
    )
    assert "model_advice" not in repr(payload)
    assert all(not callable(value) for value in payload.values())


def test_incident_evidence_response_fails_closed_for_unknown_incident():
    ledger = ActionLedger()
    ledger.record(EventType.EXTERNAL_INPUT, "inc-1", {"source": "sandbox"})

    try:
        incident_evidence_response(ledger, incident_id="missing")
    except KeyError as exc:
        assert exc.args == ("missing",)
    else:
        raise AssertionError("unknown incident must fail closed")
