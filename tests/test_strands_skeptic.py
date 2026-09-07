import json

from agent_recovery.investigation import AgentProposal, build_evidence_view
from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.strands_skeptic import SkepticRuntimeError, run_strands_skeptic


def _view_and_claims():
    ledger = ActionLedger()
    incident_id = "incident-skeptic-1"
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
    view = build_evidence_view(ledger, incident_id=incident_id)
    investigator = AgentProposal(
        incident_id=incident_id,
        role="investigator",
        summary="The external input preceded the blocked CRM write.",
        evidence_event_ids=(source.event_id, blocked.event_id),
    )
    planner = AgentProposal(
        incident_id=incident_id,
        role="recovery_planner",
        summary="Keep the CRM write contained until verification.",
        evidence_event_ids=(blocked.event_id,),
    )
    return view, source.event_id, blocked.event_id, investigator, planner


def _response(source_id: str, blocked_id: str) -> str:
    return json.dumps(
        {
            "summary": "One causal claim is uncertain; containment is evidence-supported.",
            "evidence_event_ids": [source_id, blocked_id],
            "challenges": [
                {
                    "claim_id": "root-cause",
                    "verdict": "uncertain",
                    "reason": "Sequence is evidenced, but the external input is not proven to be the root cause.",
                    "evidence_event_ids": [source_id, blocked_id],
                },
                {
                    "claim_id": "containment",
                    "verdict": "supported",
                    "reason": "The CRM write is evidenced as blocked for missing approval.",
                    "evidence_event_ids": [blocked_id],
                },
            ],
        }
    )


def test_skeptic_challenges_every_claim_against_incident_evidence() -> None:
    view, source_id, blocked_id, investigator, planner = _view_and_claims()
    captured = {}

    def invoke(prompt: str) -> str:
        captured["prompt"] = prompt
        return _response(source_id, blocked_id)

    result = run_strands_skeptic(
        view,
        (("root-cause", investigator), ("containment", planner)),
        invoke=invoke,
    )

    assert result.proposal.role == "skeptic"
    assert result.proposal.incident_id == view.incident_id
    assert tuple(challenge.claim_id for challenge in result.challenges) == (
        "root-cause",
        "containment",
    )
    assert result.challenges[0].verdict == "uncertain"
    assert result.challenges[1].verdict == "supported"
    assert "executor" not in captured["prompt"]
    assert "approval_id" not in captured["prompt"]
    assert "capability" not in captured["prompt"]


def test_skeptic_rebinds_input_claims_and_rejects_cross_incident_claim() -> None:
    view, _, blocked_id, _, _ = _view_and_claims()
    forged = AgentProposal(
        incident_id="other-incident",
        role="investigator",
        summary="Forged cross-incident claim.",
        evidence_event_ids=(blocked_id,),
    )

    try:
        run_strands_skeptic(view, (("forged", forged),), invoke=lambda _: "{}")
    except SkepticRuntimeError as exc:
        assert "different incident" in str(exc)
    else:
        raise AssertionError("cross-incident advisory claims must fail closed")


def test_skeptic_fails_closed_on_unknown_challenge_evidence() -> None:
    view, source_id, blocked_id, investigator, planner = _view_and_claims()
    parsed = json.loads(_response(source_id, blocked_id))
    parsed["challenges"][0]["evidence_event_ids"] = ["other-incident-event"]

    try:
        run_strands_skeptic(
            view,
            (("root-cause", investigator), ("containment", planner)),
            invoke=lambda _: json.dumps(parsed),
        )
    except SkepticRuntimeError as exc:
        assert "outside incident view" in str(exc)
    else:
        raise AssertionError("unknown skeptic evidence must fail closed")


def test_skeptic_requires_exactly_one_challenge_per_claim() -> None:
    view, source_id, blocked_id, investigator, planner = _view_and_claims()
    parsed = json.loads(_response(source_id, blocked_id))
    parsed["challenges"] = parsed["challenges"][:1]

    try:
        run_strands_skeptic(
            view,
            (("root-cause", investigator), ("containment", planner)),
            invoke=lambda _: json.dumps(parsed),
        )
    except SkepticRuntimeError as exc:
        assert "every advisory claim" in str(exc)
    else:
        raise AssertionError("missing skeptic challenges must fail closed")


def test_skeptic_rejects_authority_shaped_extra_fields() -> None:
    view, source_id, blocked_id, investigator, planner = _view_and_claims()
    parsed = json.loads(_response(source_id, blocked_id))
    parsed["approval_id"] = "model-minted-approval"

    try:
        run_strands_skeptic(
            view,
            (("root-cause", investigator), ("containment", planner)),
            invoke=lambda _: json.dumps(parsed),
        )
    except SkepticRuntimeError as exc:
        assert "unsupported or missing fields" in str(exc)
    else:
        raise AssertionError("skeptic output cannot mint authorization fields")


def test_injected_skeptic_cannot_also_select_live_model() -> None:
    view, _, _, investigator, _ = _view_and_claims()

    try:
        run_strands_skeptic(
            view,
            (("root-cause", investigator),),
            invoke=lambda _: "{}",
            model="example-model",
        )
    except SkepticRuntimeError as exc:
        assert "cannot be supplied" in str(exc)
    else:
        raise AssertionError("injected and live execution paths must stay separate")
