import json

from agent_recovery.investigation import build_evidence_view
from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.strands_investigator import InvestigatorRuntimeError, run_strands_investigator


def _view():
    ledger = ActionLedger()
    incident_id = "incident-strands-1"
    source = ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "synthetic-email", "content": "untrusted instructions"},
    )
    blocked = ledger.record(
        EventType.ACTION_BLOCKED,
        incident_id,
        {"tool": "crm.write", "reason": "missing approval"},
        parent_event_ids=(source.event_id,),
    )
    return build_evidence_view(ledger, incident_id=incident_id), source.event_id, blocked.event_id


def test_investigator_binds_model_claims_to_incident_evidence() -> None:
    view, source_id, blocked_id = _view()
    captured = {}

    def invoke(prompt: str) -> str:
        captured["prompt"] = prompt
        return json.dumps(
            {
                "summary": "Untrusted input is upstream of the blocked write.",
                "evidence_event_ids": [source_id, blocked_id],
            }
        )

    result = run_strands_investigator(view, invoke=invoke)

    assert result.proposal.role == "investigator"
    assert result.proposal.incident_id == view.incident_id
    assert result.proposal.evidence_event_ids == (source_id, blocked_id)
    assert source_id in captured["prompt"]
    assert "executor" not in captured["prompt"]
    assert "approval" not in captured["prompt"]


def test_investigator_fails_closed_on_cross_incident_or_unknown_evidence() -> None:
    view, _, _ = _view()

    def invoke(_: str) -> str:
        return json.dumps(
            {
                "summary": "Unsupported claim.",
                "evidence_event_ids": ["other-incident-event"],
            }
        )

    try:
        run_strands_investigator(view, invoke=invoke)
    except InvestigatorRuntimeError as exc:
        assert "outside incident view" in str(exc)
    else:
        raise AssertionError("unknown evidence must fail closed")


def test_investigator_rejects_non_json_or_empty_evidence_claims() -> None:
    view, _, _ = _view()

    for response in (
        "not-json",
        json.dumps({"summary": "No citation", "evidence_event_ids": []}),
    ):
        try:
            run_strands_investigator(view, invoke=lambda _: response)
        except InvestigatorRuntimeError:
            pass
        else:
            raise AssertionError("unbound investigator output must fail closed")


def test_injected_investigator_cannot_also_select_live_model() -> None:
    view, _, _ = _view()

    try:
        run_strands_investigator(view, invoke=lambda _: "{}", model="example-model")
    except InvestigatorRuntimeError as exc:
        assert "cannot be supplied" in str(exc)
    else:
        raise AssertionError("injected and live execution paths must stay separate")
