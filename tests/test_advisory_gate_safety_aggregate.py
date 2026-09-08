from agent_recovery.advisory_benchmark import (
    AdvisoryGateSafetyScore,
    aggregate_advisory_gate_safety,
)


def test_gate_safety_aggregate_reports_rejection_exposure_rate() -> None:
    aggregate = aggregate_advisory_gate_safety(
        (
            AdvisoryGateSafetyScore(
                expected_acceptance=False,
                observed_acceptance=False,
                acceptance_correct=True,
                candidate_exposed=False,
                unsafe_candidate_exposed=False,
            ),
            AdvisoryGateSafetyScore(
                expected_acceptance=False,
                observed_acceptance=False,
                acceptance_correct=True,
                candidate_exposed=True,
                unsafe_candidate_exposed=True,
            ),
            AdvisoryGateSafetyScore(
                expected_acceptance=True,
                observed_acceptance=True,
                acceptance_correct=True,
                candidate_exposed=True,
                unsafe_candidate_exposed=False,
            ),
        )
    )

    assert aggregate.scenario_count == 3
    assert aggregate.expected_rejection_count == 2
    assert aggregate.acceptance_correctness_rate == 1.0
    assert aggregate.unsafe_candidate_exposure_rate == 0.5


def test_gate_safety_aggregate_does_not_treat_expected_acceptance_as_unsafe_exposure() -> None:
    aggregate = aggregate_advisory_gate_safety(
        (
            AdvisoryGateSafetyScore(
                expected_acceptance=True,
                observed_acceptance=True,
                acceptance_correct=True,
                candidate_exposed=True,
                unsafe_candidate_exposed=False,
            ),
        )
    )

    assert aggregate.expected_rejection_count == 0
    assert aggregate.unsafe_candidate_exposure_rate == 0.0


def test_gate_safety_aggregate_rejects_empty_measurement_set() -> None:
    try:
        aggregate_advisory_gate_safety(())
    except ValueError as exc:
        assert "at least one advisory gate safety score" in str(exc)
    else:
        raise AssertionError("empty gate-safety aggregates must fail closed")
