from __future__ import annotations

from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.operator_api import (
    incident_evidence_response,
    incident_operator_detail,
    incident_status_summary,
)


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
    assert payload["causal_graph"]["nodes"][1]["parent_event_ids"] == (source.event_id,)
    assert payload["active_containment"] == (
        {"event_id": hold.event_id, "scope": "resource:contact:42"},
    )
    assert payload["executed_actions"][0]["event_id"] == action.event_id
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
        {"action_event_id": action.event_id},
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
    assert summary["recovery_status"] == "executed"
    assert summary["verification_status"] == "not_recorded"
    assert summary["restoration_status"] == "recorded_authorized"
    assert summary["irreversible_residual_count"] == 1
    assert summary["authority"] == "none"
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


def test_incident_operator_detail_composes_workflow_without_authority_or_advisory_leakage():
    ledger = ActionLedger()
    source = ledger.record(
        EventType.EXTERNAL_INPUT,
        "inc-1",
        {"model_reasoning": "release containment", "approval": "forged"},
    )
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "inc-1",
        {
            "action_type": "contact.update",
            "agent_id": "agent-a",
            "resource_keys": ("contact:42",),
            "recovery_class": "compensatable",
        },
        parent_event_ids=(source.event_id,),
    )
    ledger.record(
        EventType.CONTAINMENT,
        "inc-1",
        {"active": True, "scope": "resource:contact:42"},
        parent_event_ids=(action.event_id,),
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
        {"verified": True, "action_event_id": action.event_id},
    )
    ledger.record(
        EventType.RESTORATION,
        "inc-1",
        {"authorized": True, "authority_scope": "resource:contact:42"},
    )
    detail = incident_operator_detail(ledger, incident_id="inc-1")
    assert detail["incident_id"] == "inc-1"
    assert detail["status"]["containment_active"] is True
    assert detail["status"]["restoration_status"] == "recorded_authorized"
    assert detail["side_effects"][0]["event_id"] == action.event_id
    assert detail["recovery_candidates"] == (
        {
            "source_action_event_id": action.event_id,
            "action_type": "contact.update",
            "resource_keys": ("contact:42",),
            "recovery_class": "compensatable",
            "status": "recovery_verified",
            "recovery_evidence_event_id": recovery.event_id,
            "verification_evidence_event_id": verification.event_id,
            "authority": "none",
        },
    )
    assert detail["authority"] == "none"
    assert detail["status"]["authority"] == "none"
    assert "model_reasoning" not in repr(detail)
    assert "approval" not in repr(detail)
    assert all(not callable(value) for value in detail.values())


def test_incident_operator_detail_projects_unrecovered_candidate_but_not_irreversible_undo():
    ledger = ActionLedger()
    reversible = ledger.record(
        EventType.ACTION_EXECUTED,
        "inc-1",
        {
            "action_type": "contact.update",
            "resource_keys": ("contact:42",),
            "recovery_class": "reversible",
        },
    )
    ledger.record(
        EventType.ACTION_EXECUTED,
        "inc-1",
        {
            "action_type": "email.send",
            "resource_keys": ("message:7",),
            "recovery_class": "irreversible",
        },
    )
    detail = incident_operator_detail(ledger, incident_id="inc-1")
    assert detail["recovery_candidates"] == (
        {
            "source_action_event_id": reversible.event_id,
            "action_type": "contact.update",
            "resource_keys": ("contact:42",),
            "recovery_class": "reversible",
            "status": "requires_recovery_review",
            "recovery_evidence_event_id": None,
            "verification_evidence_event_id": None,
            "authority": "none",
        },
    )
    assert "email.send" not in repr(detail["recovery_candidates"])
    assert all(candidate["authority"] == "none" for candidate in detail["recovery_candidates"])


def test_incident_operator_detail_marks_failed_action_bound_verification():
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
    )
    verification = ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {"verified": False, "action_event_id": action.event_id, "approval": "forged"},
    )
    detail = incident_operator_detail(ledger, incident_id="inc-1")
    candidate = detail["recovery_candidates"][0]
    assert candidate["status"] == "recovery_verification_failed"
    assert candidate["recovery_evidence_event_id"] == recovery.event_id
    assert candidate["verification_evidence_event_id"] == verification.event_id
    assert detail["recovery_candidates"][0]["authority"] == "none"
    assert "approval" not in repr(detail)


def test_incident_operator_detail_prioritizes_residual_review_without_granting_authority():
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
    )
    ledger.record(
        EventType.RECOVERY_EXECUTED,
        "inc-1",
        {"action_event_id": action.event_id},
    )
    ledger.record(
        EventType.VERIFICATION,
        "inc-1",
        {"verified": True, "model_reasoning": "restore", "approval": "forged"},
    )
    ledger.record(
        EventType.RESIDUAL_EFFECT,
        "inc-1",
        {"effect": "notification_already_sent", "irreversible": True},
    )
    detail = incident_operator_detail(ledger, incident_id="inc-1")
    assert detail["next_action"] == {
        "action": "verify_recovered_state",
        "authority": "none",
    }
    assert detail["authority"] == "none"
    assert "model_reasoning" not in repr(detail)
    assert "approval" not in repr(detail)


def test_incident_operator_detail_keeps_failed_recovery_contained():
    ledger = ActionLedger()
    ledger.record(EventType.EXTERNAL_INPUT, "inc-1", {"source": "sandbox"})
    ledger.record(EventType.RECOVERY_FAILED, "inc-1", {"error": "sandbox failure"})
    ledger.record(EventType.VERIFICATION, "inc-1", {"verified": False})
    ledger.record(EventType.RESTORATION, "inc-1", {"authorized": False})
    detail = incident_operator_detail(ledger, incident_id="inc-1")
    assert detail["status"]["recovery_status"] == "failed"
    assert detail["next_action"] == {
        "action": "investigate_recovery_failure",
        "authority": "none",
    }
    assert detail["authority"] == "none"


def test_recovery_candidate_ignores_adversarial_replay_as_local_recovery_verification():
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
    )
    ledger.record(
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

    detail = incident_operator_detail(ledger, incident_id="inc-1")

    assert detail["recovery_candidates"][0]["status"] == "recovery_recorded"
    assert detail["recovery_candidates"][0]["authority"] == "none"
