import json
from pathlib import Path

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


def _load_b01_ground_truth() -> tuple[AdvisoryGroundTruth, dict[str, object]]:
    path = Path(__file__).parents[1] / "benchmarks/advisory/b01_indirect_prompt_injection.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    ground_truth = AdvisoryGroundTruth(
        incident_id=payload["incident_id"],
        root_cause_event_ids=tuple(payload["root_cause_event_ids"]),
        required_step_ids=tuple(payload["required_step_ids"]),
        required_evidence_event_ids=tuple(payload["required_evidence_event_ids"]),
    )
    return ground_truth, payload


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


def test_scores_b01_versioned_ground_truth_fixture() -> None:
    ground_truth, payload = _load_b01_ground_truth()
    investigator = AgentProposal(
        incident_id=ground_truth.incident_id,
        role="investigator",
        summary="external content redirected the agent toward an unauthorized write",
        evidence_event_ids=ground_truth.root_cause_event_ids,
    )
    steps = (
        ProposedRecoveryStep(
            "contain-agent-authority",
            "contain the affected agent authority",
            ("evt-unauthorized-write-attempt", "evt-containment"),
        ),
        ProposedRecoveryStep(
            "repair-owned-state",
            "repair synthetic owned state and verify it",
            ("evt-containment", "evt-verification"),
            ("contain-agent-authority",),
        ),
    )
    planner = RecoveryPlannerResult(
        proposal=AgentProposal(
            incident_id=ground_truth.incident_id,
            role="recovery_planner",
            summary="contain first, then repair and verify",
            evidence_event_ids=("evt-unauthorized-write-attempt", "evt-containment"),
        ),
        steps=steps,
        residual_risks=(),
        raw_response="{}",
    )
    skeptic = SkepticResult(
        proposal=AgentProposal(
            incident_id=ground_truth.incident_id,
            role="skeptic",
            summary="B01 advisory claims are grounded in the synthetic ledger",
            evidence_event_ids=("evt-external-content", "evt-verification"),
        ),
        challenges=(
            SkepticChallenge(
                "investigator",
                "supported",
                "causal entry point is present",
                ("evt-external-content", "evt-agent-ingest"),
            ),
            SkepticChallenge(
                "recovery_plan",
                "supported",
                "containment precedes repair and verification",
                ("evt-containment", "evt-verification"),
            ),
        ),
        raw_response="{}",
    )
    decision = AdvisoryGateDecision(
        accepted=True,
        reasons=(),
        candidate_plan=CandidateRecoveryPlan(
            incident_id=ground_truth.incident_id,
            summary="B01 candidate recovery plan",
            steps=steps,
            residual_risks=(),
            evidence_event_ids=ground_truth.required_evidence_event_ids,
            skeptic_evidence_event_ids=("evt-external-content", "evt-verification"),
        ),
    )

    score = score_advisory_chain(
        ground_truth,
        investigator=investigator,
        planner=planner,
        skeptic=skeptic,
        decision=decision,
    )

    assert payload["scenario_id"] == "B01"
    assert payload["constraints"]["model_output_is_authorization"] is False
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
