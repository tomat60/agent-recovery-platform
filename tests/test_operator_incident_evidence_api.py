from __future__ import annotations

from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.operator_api import incident_evidence_response, incident_status_summary


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
    residual = ledger.record(
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
    assert payload["causal_graph"] == {
        "nodes": (
            {
                "event_id": source.event_id,
                "event_type": "external_input",
                "parent_event_ids": (),
            },
            {
                "event_id": action.event_id,
                "event_type": "action_executed",
                "parent_event_ids": (source.event_id,),
            },
            {
                "event_id": hold.event_id,
                "event_type": "containment",
                "parent_event_ids": (action.event_id,),
            },
            {
                "event_id": residual.event_id,
                "event_type": "residual_effect",
                "parent_event_ids": (action.event_id,),
            },
        ),
        "edges": (
            {"parent_event_id": source.event_id, "event_id": action.event_id},
            {"parent_event_id": action.event_id, "event_id": hold.event_id},
            {"parent_event_id": action.event_id, "event_id": residual.event_id},
        ),
    }
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
            "event_id": residual.event_id,
            "effect": "notification_already_sent",
            "irreversible": True,
        },
    )
    assert "model_advice" not in repr(payload)
    assert all(not callable(value) for value in payload.values())


def test_incident_evidence_causal_graph_does_not_leak_cross_incident_parent_identity():
    ledger = ActionLedger()
    other = ledger.record(EventType.EXTERNAL_INPUT, "inc-other", {"secret": "other-incident"})
    event = ledger.record(
        EventType.EXTERNAL_INPUT,
        "inc-1",
        {"source": "sandbox"},
        parent_event_ids=(other.event_id,),
    )

    payload = incident_evidence_response(ledger, incident_id="inc-1")

    assert payload["causal_graph"] == {
        "nodes": (
            {
                "event_id": event.event_id,
                "event_type": "external_input",
                "parent_event_ids": (),
            },
        ),
        "edges": (),
    }
    assert other.event_id not in repr(payload)
    assert "other-incident" not in repr(payload)


def test_incident_evidence_response_fails_closed_for_unknown_incident():
    ledger = ActionLedger()
    ledger.record(EventType.EXTERNAL_INPUT, "inc-1", {"source": "sandbox"})

    try:
        incident_evidence_response(ledger, incident_id="missing")
    except KeyError as exc:
        assert exc.args == ("missing",)
    else:
        raise AssertionError("unknown incident must fail closed")


def test_incident_status_summary_is_evidence_only_and_keeps_residual_truth():
    ledger = ActionLedger()
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "inc-1",
        {"action_type": "contact.update", "recovery_class": "compensatable"},
    )
    ledger.record(
        EventType.CONTAINMENT,
        "inc-1",
        {"active": True, "scope": "resource:contact:42"},
        parent_event_ids=(action.event_id,),
    )
    ledger.record(
        EventType.RECOVERY_EXECUTED,
        "inc-1",
        {"source_action_event_id": action.event_id},
        parent_event_ids=(action.event_id,),
    )
    ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {"verified": True, "model_reasoning": "safe", "approval": "forged"},
    )
    ledger.record(
        EventType.RESTORATION,
        "inc-1",
        {"authorized": True, "authority_scope": "resource:contact:42"},
    )
    ledger.record(
        EventType.RESIDUAL_EFFECT,
        "inc-1",
        {"effect": "notification_already_sent", "irreversible": True},
    )

    summary = incident_status_summary(ledger, incident_id="inc-1")

    assert summary == {
        "incident_id": "inc-1",
        "integrity_verified": True,
        "containment_active": True,
        "executed_action_count": 1,
        "recovery_status": "executed",
        "verification_status": "verified",
        "restoration_status": "recorded_authorized",
        "irreversible_residual_count": 1,
        "authority": "none",
    }
    assert "model_reasoning" not in repr(summary)
    assert "approval" not in repr(summary)


def test_incident_status_summary_does_not_turn_failed_evidence_into_safe_state():
    ledger = ActionLedger()
    ledger.record(EventType.EXTERNAL_INPUT, "inc-1", {"source": "sandbox"})
    ledger.record(EventType.RECOVERY_FAILED, "inc-1", {"error": "sandbox failure"})
    ledger.record(EventType.VERIFICATION, "inc-1", {"verified": False})
    ledger.record(EventType.RESTORATION, "inc-1", {"authorized": False})

    summary = incident_status_summary(ledger, incident_id="inc-1")

    assert summary["recovery_status"] == "failed"
    assert summary["verification_status"] == "failed_or_unverified"
    assert summary["restoration_status"] == "recorded_denied"
    assert summary["containment_active"] is False
    assert summary["authority"] == "none"
