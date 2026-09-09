from agent_recovery.advisory_benchmark import (
    AdvisoryBenchmarkAggregate,
    AdvisoryBenchmarkScore,
    AdvisoryGateSafetyAggregate,
    AdvisoryGateSafetyScore,
    AdvisoryGroundTruth,
)
from agent_recovery.advisory_fixture import AdvisoryBenchmarkFixture
from agent_recovery.judge_artifact import build_advisory_judge_artifact


def _fixture() -> AdvisoryBenchmarkFixture:
    return AdvisoryBenchmarkFixture(
        scenario_id="B01",
        scenario_class="indirect_prompt_injection",
        ground_truth=AdvisoryGroundTruth(
            incident_id="inc-b01",
            root_cause_event_ids=("root",),
            required_step_ids=("contain",),
            required_evidence_event_ids=("root",),
        ),
        constraints={"model_output_is_authorization": False},
    )


def _advisory(*, accepted: bool = False) -> AdvisoryBenchmarkAggregate:
    score = AdvisoryBenchmarkScore(
        incident_id="inc-b01",
        gate_accepted=accepted,
        root_cause_accuracy=1.0,
        recovery_plan_correctness=1.0,
        advisory_evidence_completeness=1.0,
    )
    return AdvisoryBenchmarkAggregate(
        scenario_count=1,
        gate_acceptance_rate=float(accepted),
        mean_root_cause_accuracy=1.0,
        mean_recovery_plan_correctness=1.0,
        mean_advisory_evidence_completeness=1.0,
        scenario_scores=(score,),
    )


def _safety(*, accepted: bool = False) -> AdvisoryGateSafetyAggregate:
    score = AdvisoryGateSafetyScore(
        expected_acceptance=False,
        observed_acceptance=accepted,
        acceptance_correct=not accepted,
        candidate_exposed=False,
        unsafe_candidate_exposed=False,
    )
    return AdvisoryGateSafetyAggregate(
        scenario_count=1,
        expected_rejection_count=1,
        acceptance_correctness_rate=float(not accepted),
        unsafe_candidate_exposure_rate=0.0,
        scenario_scores=(score,),
    )


def test_builds_deterministic_judge_artifact_without_authority() -> None:
    artifact = build_advisory_judge_artifact(
        (_fixture(),),
        _advisory(),
        _safety(),
        regression_refs={"B01": "regressions/B01.json"},
    )
    assert artifact["schema_version"] == "advisory-judge-artifact/v1"
    assert artifact["authorization_effect"] == "none"
    assert artifact["scenario_count"] == 1
    assert artifact["scenarios"][0]["scenario_id"] == "B01"
    assert artifact["scenarios"][0]["regression_ref"] == "regressions/B01.json"


def test_rejects_mismatched_measurement_provenance() -> None:
    score = AdvisoryBenchmarkScore("wrong-incident", False, 1.0, 1.0, 1.0)
    advisory = AdvisoryBenchmarkAggregate(1, 0.0, 1.0, 1.0, 1.0, (score,))
    try:
        build_advisory_judge_artifact((_fixture(),), advisory, _safety())
    except ValueError as exc:
        assert "provenance mismatch" in str(exc)
    else:
        raise AssertionError("judge artifact must fail closed on mismatched provenance")


def test_rejects_regression_reference_for_accepted_advisory() -> None:
    try:
        build_advisory_judge_artifact(
            (_fixture(),),
            _advisory(accepted=True),
            _safety(accepted=True),
            regression_refs={"B01": "regressions/B01.json"},
        )
    except ValueError as exc:
        assert "accepted advisory scenario" in str(exc)
    else:
        raise AssertionError("accepted advisory must not be mislabeled as rejection regression")
