import pytest

from agent_recovery.advisory_benchmark import (
    AdvisoryBenchmarkScore,
    aggregate_advisory_scores,
)


def score(
    incident_id: str,
    *,
    accepted: bool,
    root: float,
    plan: float,
    evidence: float,
) -> AdvisoryBenchmarkScore:
    return AdvisoryBenchmarkScore(
        incident_id=incident_id,
        gate_accepted=accepted,
        root_cause_accuracy=root,
        recovery_plan_correctness=plan,
        advisory_evidence_completeness=evidence,
    )


def test_aggregate_reports_only_measured_arithmetic_means() -> None:
    aggregate = aggregate_advisory_scores(
        [
            score("incident-b01", accepted=True, root=1.0, plan=1.0, evidence=1.0),
            score("incident-b02", accepted=False, root=0.0, plan=0.5, evidence=0.75),
        ]
    )

    assert aggregate.scenario_count == 2
    assert aggregate.gate_acceptance_rate == 0.5
    assert aggregate.mean_root_cause_accuracy == 0.5
    assert aggregate.mean_recovery_plan_correctness == 0.75
    assert aggregate.mean_advisory_evidence_completeness == 0.875
    assert [item.incident_id for item in aggregate.scenario_scores] == [
        "incident-b01",
        "incident-b02",
    ]


def test_aggregate_rejects_empty_measurements() -> None:
    with pytest.raises(ValueError, match="at least one"):
        aggregate_advisory_scores([])


def test_aggregate_rejects_duplicate_incident_identity() -> None:
    duplicate = score("incident-b01", accepted=True, root=1.0, plan=1.0, evidence=1.0)
    with pytest.raises(ValueError, match="unique incident"):
        aggregate_advisory_scores([duplicate, duplicate])
