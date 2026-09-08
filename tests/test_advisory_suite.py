from agent_recovery.advisory_fixture import AdvisoryBenchmarkFixture
from agent_recovery.advisory_benchmark import AdvisoryGroundTruth
from agent_recovery.advisory_gate import AdvisoryGateDecision, CandidateRecoveryPlan
from agent_recovery.advisory_suite import AdvisoryScenarioOutputs, score_advisory_fixture_suite
from agent_recovery.investigation import AgentProposal
from agent_recovery.strands_recovery_planner import ProposedRecoveryStep, RecoveryPlannerResult
from agent_recovery.strands_skeptic import SkepticChallenge, SkepticResult


def _fixture(scenario_id: str, incident_id: str) -> AdvisoryBenchmarkFixture:
    return AdvisoryBenchmarkFixture(
        scenario_id=scenario_id,
        scenario_class="synthetic",
        ground_truth=AdvisoryGroundTruth(
            incident_id=incident_id,
            root_cause_event_ids=(f"{incident_id}-root",),
            required_step_ids=("contain",),
            required_evidence_event_ids=(f"{incident_id}-root", f"{incident_id}-verify"),
        ),
        constraints={"model_output_is_authorization": False},
    )


def _outputs(incident_id: str) -> AdvisoryScenarioOutputs:
    root = f"{incident_id}-root"
    verify = f"{incident_id}-verify"
    investigator = AgentProposal(incident_id, "investigator", "root", (root,))
    steps = (ProposedRecoveryStep("contain", "contain", (root, verify)),)
    planner = RecoveryPlannerResult(
        proposal=AgentProposal(incident_id, "recovery_planner", "contain", (root,)),
        steps=steps,
        residual_risks=(),
        raw_response="{}",
    )
    skeptic = SkepticResult(
        proposal=AgentProposal(incident_id, "skeptic", "supported", (verify,)),
        challenges=(SkepticChallenge("recovery_plan", "supported", "supported", (root, verify)),),
        raw_response="{}",
    )
    decision = AdvisoryGateDecision(
        accepted=True,
        reasons=(),
        candidate_plan=CandidateRecoveryPlan(
            incident_id=incident_id,
            summary="candidate",
            steps=steps,
            residual_risks=(),
            evidence_event_ids=(root, verify),
            skeptic_evidence_event_ids=(verify,),
        ),
    )
    return AdvisoryScenarioOutputs(investigator, planner, skeptic, decision)


def test_scores_exact_fixture_suite_without_authorizing_recovery() -> None:
    fixtures = (_fixture("B01", "inc-1"), _fixture("B02", "inc-2"))
    aggregate = score_advisory_fixture_suite(
        fixtures,
        {"B01": _outputs("inc-1"), "B02": _outputs("inc-2")},
    )
    assert aggregate.scenario_count == 2
    assert aggregate.mean_root_cause_accuracy == 1.0
    assert aggregate.mean_recovery_plan_correctness == 1.0
    assert aggregate.mean_advisory_evidence_completeness == 1.0


def test_rejects_missing_or_extra_scenario_outputs() -> None:
    fixtures = (_fixture("B01", "inc-1"),)
    try:
        score_advisory_fixture_suite(fixtures, {"B02": _outputs("inc-2")})
    except ValueError as exc:
        assert "missing=['B01']" in str(exc)
        assert "extra=['B02']" in str(exc)
    else:
        raise AssertionError("suite scoring must fail closed on coverage mismatch")
