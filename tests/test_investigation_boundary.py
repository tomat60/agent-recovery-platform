from agent_recovery.investigation import (
    InvestigationBoundaryError,
    bind_agent_proposal,
    build_evidence_view,
)
from agent_recovery.ledger import ActionLedger, EventType


def _ledger_with_incident() -> tuple[ActionLedger, str, str]:
    ledger = ActionLedger()
    incident_id = "incident-investigation-1"
    source = ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "synthetic-email", "content": "untrusted instructions"},
    )
    action = ledger.record(
        EventType.ACTION_BLOCKED,
        incident_id,
        {"tool": "crm.write", "reason": "missing approval"},
        parent_event_ids=(source.event_id,),
    )
    return ledger, source.event_id, action.event_id


def test_evidence_view_is_incident_scoped_and_read_only() -> None:
    ledger, source_id, action_id = _ledger_with_incident()
    ledger.record(EventType.VERIFICATION, "other-incident", {"ok": True})

    view = build_evidence_view(ledger, incident_id="incident-investigation-1")
    payload = view.as_prompt_payload()

    assert [event["event_id"] for event in payload["events"]] == [source_id, action_id]
    assert "approval" not in payload
    assert "executor" not in payload
    assert "ledger" not in payload


def test_agent_proposal_must_cite_same_incident_evidence() -> None:
    ledger, source_id, _ = _ledger_with_incident()
    view = build_evidence_view(ledger, incident_id="incident-investigation-1")

    proposal = bind_agent_proposal(
        view,
        role="investigator",
        summary="The external input is causally upstream of the blocked write.",
        evidence_event_ids=(source_id,),
    )

    assert proposal.incident_id == view.incident_id
    assert proposal.evidence_event_ids == (source_id,)


def test_agent_proposal_cannot_smuggle_cross_incident_evidence() -> None:
    ledger, source_id, _ = _ledger_with_incident()
    other = ledger.record(EventType.VERIFICATION, "other-incident", {"ok": True})
    view = build_evidence_view(ledger, incident_id="incident-investigation-1")

    try:
        bind_agent_proposal(
            view,
            role="recovery_planner",
            summary="Attempt to cite unrelated evidence.",
            evidence_event_ids=(source_id, other.event_id),
        )
    except InvestigationBoundaryError as exc:
        assert "outside incident view" in str(exc)
    else:
        raise AssertionError("cross-incident evidence must fail closed")


def test_empty_incident_evidence_fails_closed() -> None:
    ledger = ActionLedger()

    try:
        build_evidence_view(ledger, incident_id="missing")
    except InvestigationBoundaryError as exc:
        assert "no ledger evidence" in str(exc)
    else:
        raise AssertionError("missing incident evidence must fail closed")
