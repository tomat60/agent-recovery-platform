from agent_recovery.advisory_benchmark import AdvisoryGroundTruth, score_advisory_chain
from agent_recovery.advisory_gate import AdvisoryGateDecision, CandidateRecoveryPlan
from agent_recovery.investigation import AgentProposal
from agent_recovery.strands_recovery_planner import ProposedRecoveryStep, RecoveryPlannerResult
from agent_recovery.strands_skeptic import SkepticChallenge, SkepticResult


def _outputs(incident_id: str = "inc-1"):
    investigator = AgentProposal(
        incident_id=incident_id,
        role="investigator",
        summary="root cause",
        evidence_event_ids=("e1", "e2"),
    )
    planner = RecoveryPlannerResult(
        proposal=AgentProposal(
            incident_id=incident_id,
            role="recovery_planner",
            summary="recover safely",
            evidence_event_ids=("e2", "e3"),
        ),
        steps=(
            ProposedRecoveryStep("contain", "contain authority", ("e2",)),
            ProposedRecoveryStep("repair", "repair state", ("e3",), ("contain",)),
        ),
        residual_risks=("external observation remains",),
        raw_response="{}",
    )
    skeptic = SkepticResult(
        proposal=AgentProposal(
            incident_id=incident_id,
            role="skeptic",
            summary="claims supported",
            evidence_event_ids=("e1", "e3"),
        ),
        challenges=(
            SkepticChallenge("investigator", "supported", "supported", ("e1", "e2")),
            SkepticChallenge("recovery_plan", "supported", "supported", ("e2", "e3")),
        ),
        raw_response="{}",
    )
    decision = AdvisoryGateDecision(
        accepted=True,
        reasons=(),
        candidate_plan=CandidateRecoveryPlan(
            incident_id=incident_id,
            summary="recover safely",
            steps=planner.steps,
            residual_risks=planner.residual_risks,
            evidence_event_ids=("e1", "e2", "e3"),
            skeptic_evidence_event_ids=("e1", "e2", "e3"),
        ),
    )
    return investigator, planner, skeptic, decision


def test_scores_exact_advisory_ground_truth() -> None:
    investigator, planner, skeptic, decision = _outputs()
    score = score_advisory_chain(
        AdvisoryGroundTruth(
            incident_id="inc-1",
            root_cause_event_ids=("e1", "e2"),
            required_step_ids=("contain", "repair"),
            required_evidence_event_ids=("e1", "e2", "e3"),
        ),
        investigator=investigator,
        planner=planner,
        skeptic=skeptic,
        decision=decision,
    )

    assert score.gate_accepted is True
    assert score.root_cause_accuracy == 1.0
    assert score.recovery_plan_correctness == 1.0
    assert score.advisory_evidence_completeness == 1.0


def test_scores_missing_or_extra_ground_truth_conservatively() -> None:
    investigator, planner, skeptic, decision = _outputs()
    score = score_advisory_chain(
        AdvisoryGroundTruth(
            incident_id="inc-1",
            root_cause_event_ids=("e1",),
            required_step_ids=("repair", "contain"),
            required_evidence_event_ids=("e1", "e2", "e3", "e4"),
        ),
        investigator=investigator,
        planner=planner,
        skeptic=skeptic,
        decision=decision,
    )

    assert score.root_cause_accuracy == 0.0
    assert score.recovery_plan_correctness == 0.0
    assert score.advisory_evidence_completeness == 0.75


def test_rejects_cross_incident_outputs() -> None:
    investigator, planner, skeptic, decision = _outputs(incident_id="other")

    try:
        score_advisory_chain(
            AdvisoryGroundTruth(
                incident_id="inc-1",
                root_cause_event_ids=("e1",),
                required_step_ids=("contain",),
                required_evidence_event_ids=("e1",),
            ),
            investigator=investigator,
            planner=planner,
            skeptic=skeptic,
            decision=decision,
        )
    except ValueError as exc:
        assert "ground-truth incident" in str(exc)
    else:
        raise AssertionError("cross-incident advisory outputs must fail closed")
