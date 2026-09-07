import json

from agent_recovery.investigation import build_evidence_view
from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.strands_recovery_planner import (
    RecoveryPlannerRuntimeError,
    run_strands_recovery_planner,
)


def _view():
    ledger = ActionLedger()
    incident_id = "incident-planner-1"
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


def _response(source_id: str, blocked_id: str) -> str:
    return json.dumps(
        {
            "summary": "Preserve evidence, then keep the blocked write disabled.",
            "evidence_event_ids": [source_id, blocked_id],
            "steps": [
                {
                    "step_id": "preserve-evidence",
                    "description": "Preserve the incident evidence before recovery mutation.",
                    "evidence_event_ids": [source_id, blocked_id],
                    "depends_on": [],
                },
                {
                    "step_id": "keep-write-blocked",
                    "description": "Keep the affected write path contained pending verification.",
                    "evidence_event_ids": [blocked_id],
                    "depends_on": ["preserve-evidence"],
                },
            ],
            "residual_risks": ["No successful external write is evidenced."],
        }
    )


def test_planner_binds_ordered_steps_to_incident_evidence() -> None:
    view, source_id, blocked_id = _view()
    captured = {}

    def invoke(prompt: str) -> str:
        captured["prompt"] = prompt
        return _response(source_id, blocked_id)

    result = run_strands_recovery_planner(view, invoke=invoke)

    assert result.proposal.role == "recovery_planner"
    assert result.proposal.incident_id == view.incident_id
    assert tuple(step.step_id for step in result.steps) == (
        "preserve-evidence",
        "keep-write-blocked",
    )
    assert result.steps[1].depends_on == ("preserve-evidence",)
    assert blocked_id in result.steps[1].evidence_event_ids
    assert "executor" not in captured["prompt"]
    assert "approval_id" not in captured["prompt"]
    assert "capability" not in captured["prompt"]


def test_planner_fails_closed_on_unknown_evidence() -> None:
    view, source_id, blocked_id = _view()
    parsed = json.loads(_response(source_id, blocked_id))
    parsed["steps"][0]["evidence_event_ids"] = ["other-incident-event"]

    try:
        run_strands_recovery_planner(view, invoke=lambda _: json.dumps(parsed))
    except RecoveryPlannerRuntimeError as exc:
        assert "outside incident view" in str(exc)
    else:
        raise AssertionError("unknown evidence must fail closed")


def test_planner_rejects_forward_or_unknown_dependencies() -> None:
    view, source_id, blocked_id = _view()
    parsed = json.loads(_response(source_id, blocked_id))
    parsed["steps"][0]["depends_on"] = ["keep-write-blocked"]

    try:
        run_strands_recovery_planner(view, invoke=lambda _: json.dumps(parsed))
    except RecoveryPlannerRuntimeError as exc:
        assert "earlier steps" in str(exc)
    else:
        raise AssertionError("forward dependencies must fail closed")


def test_planner_rejects_authority_shaped_extra_fields() -> None:
    view, source_id, blocked_id = _view()
    parsed = json.loads(_response(source_id, blocked_id))
    parsed["approval_id"] = "model-minted-approval"

    try:
        run_strands_recovery_planner(view, invoke=lambda _: json.dumps(parsed))
    except RecoveryPlannerRuntimeError as exc:
        assert "unsupported or missing fields" in str(exc)
    else:
        raise AssertionError("planner output cannot mint authorization fields")


def test_injected_planner_cannot_also_select_live_model() -> None:
    view, _, _ = _view()

    try:
        run_strands_recovery_planner(view, invoke=lambda _: "{}", model="example-model")
    except RecoveryPlannerRuntimeError as exc:
        assert "cannot be supplied" in str(exc)
    else:
        raise AssertionError("injected and live execution paths must stay separate")
