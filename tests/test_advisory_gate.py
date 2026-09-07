from agent_recovery.advisory_gate import AdvisoryGateError, evaluate_advisory_recovery_plan
from agent_recovery.investigation import AgentProposal, build_evidence_view
from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.strands_recovery_planner import (
    ProposedRecoveryStep,
    RecoveryPlannerResult,
)
from agent_recovery.strands_skeptic import SkepticChallenge, SkepticResult


def _fixture(*, investigator_verdict: str = "supported", planner_verdict: str = "supported"):
    ledger = ActionLedger()
    incident_id = "incident-advisory-gate-1"
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
    planner_proposal = AgentProposal(
        incident_id=incident_id,
        role="recovery_planner",
        summary="Keep the blocked write contained and verify state before restoration.",
        evidence_event_ids=(blocked.event_id,),
    )
    planner = RecoveryPlannerResult(
        proposal=planner_proposal,
        steps=(
            ProposedRecoveryStep(
                step_id="verify-containment",
                description="Verify the CRM write remains blocked.",
                evidence_event_ids=(blocked.event_id,),
            ),
            ProposedRecoveryStep(
                step_id="verify-state",
                description="Verify state before any later restoration decision.",
                evidence_event_ids=(source.event_id, blocked.event_id),
                depends_on=("verify-containment",),
            ),
        ),
        residual_risks=("No external write was restored by this advisory plan.",),
        raw_response="{}",
    )
    skeptic_proposal = AgentProposal(
        incident_id=incident_id,
        role="skeptic",
        summary="Claims were checked against incident evidence.",
        evidence_event_ids=(source.event_id, blocked.event_id),
    )
    skeptic = SkepticResult(
        proposal=skeptic_proposal,
        challenges=(
            SkepticChallenge(
                claim_id="investigator",
                verdict=investigator_verdict,
                reason="Investigator claim is bounded by the recorded sequence.",
                evidence_event_ids=(source.event_id, blocked.event_id),
            ),
            SkepticChallenge(
                claim_id="recovery_plan",
                verdict=planner_verdict,
                reason="Planner claim preserves containment and requires verification.",
                evidence_event_ids=(blocked.event_id,),
            ),
        ),
        raw_response="{}",
    )
    return view, investigator, planner, skeptic


def test_supported_advisory_chain_becomes_candidate_only_plan() -> None:
    view, investigator, planner, skeptic = _fixture()

    decision = evaluate_advisory_recovery_plan(
        view,
        investigator=investigator,
        planner=planner,
        skeptic=skeptic,
    )

    assert decision.accepted is True
    assert decision.reasons == ()
    assert decision.candidate_plan is not None
    assert decision.candidate_plan.incident_id == view.incident_id
    assert decision.candidate_plan.steps == planner.steps
    assert decision.candidate_plan.residual_risks == planner.residual_risks
    assert not hasattr(decision.candidate_plan, "approval_id")
    assert not hasattr(decision.candidate_plan, "executor")
    assert not hasattr(decision.candidate_plan, "capability")


def test_uncertain_or_rejected_skeptic_verdict_fails_closed() -> None:
    view, investigator, planner, skeptic = _fixture(investigator_verdict="uncertain")

    decision = evaluate_advisory_recovery_plan(
        view,
        investigator=investigator,
        planner=planner,
        skeptic=skeptic,
    )

    assert decision.accepted is False
    assert decision.candidate_plan is None
    assert "skeptic verdict for investigator is uncertain" in decision.reasons


def test_missing_required_skeptic_claim_fails_closed() -> None:
    view, investigator, planner, skeptic = _fixture()
    incomplete = SkepticResult(
        proposal=skeptic.proposal,
        challenges=skeptic.challenges[:1],
        raw_response="{}",
    )

    decision = evaluate_advisory_recovery_plan(
        view,
        investigator=investigator,
        planner=planner,
        skeptic=incomplete,
    )

    assert decision.accepted is False
    assert decision.candidate_plan is None
    assert "skeptic must review exactly the investigator and recovery-plan claims" in decision.reasons


def test_forged_step_evidence_fails_closed_even_for_supported_skeptic() -> None:
    view, investigator, planner, skeptic = _fixture()
    forged = RecoveryPlannerResult(
        proposal=planner.proposal,
        steps=(
            ProposedRecoveryStep(
                step_id="forged",
                description="Use evidence from elsewhere.",
                evidence_event_ids=("other-incident-event",),
            ),
        ),
        residual_risks=planner.residual_risks,
        raw_response="{}",
    )

    decision = evaluate_advisory_recovery_plan(
        view,
        investigator=investigator,
        planner=forged,
        skeptic=skeptic,
    )

    assert decision.accepted is False
    assert decision.candidate_plan is None
    assert any("outside incident view" in reason for reason in decision.reasons)


def test_cross_incident_proposal_is_an_error_not_a_candidate() -> None:
    view, investigator, planner, skeptic = _fixture()
    forged = AgentProposal(
        incident_id="other-incident",
        role=investigator.role,
        summary=investigator.summary,
        evidence_event_ids=investigator.evidence_event_ids,
    )

    try:
        evaluate_advisory_recovery_plan(
            view,
            investigator=forged,
            planner=planner,
            skeptic=skeptic,
        )
    except AdvisoryGateError as exc:
        assert "different incident" in str(exc)
    else:
        raise AssertionError("cross-incident advisory proposal must fail closed")
