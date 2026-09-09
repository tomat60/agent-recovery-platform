from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent_recovery.advisory_benchmark import (
    AdvisoryBenchmarkAggregate,
    AdvisoryGateSafetyAggregate,
)
from agent_recovery.advisory_fixture import AdvisoryBenchmarkFixture


JUDGE_ARTIFACT_SCHEMA_VERSION = "advisory-judge-artifact/v1"


def build_advisory_judge_artifact(
    fixtures: tuple[AdvisoryBenchmarkFixture, ...],
    advisory: AdvisoryBenchmarkAggregate,
    gate_safety: AdvisoryGateSafetyAggregate,
    *,
    regression_refs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic judge-facing artifact from already-measured evidence.

    The builder is serialization-only. It cannot create model outputs, approvals, candidate plans,
    recovery execution, or restoration authority. It also refuses incomplete or reordered evidence
    instead of silently producing a judge artifact with mismatched scenario provenance.
    """

    if not fixtures:
        raise ValueError("judge artifact requires at least one advisory fixture")
    if advisory.scenario_count != len(fixtures):
        raise ValueError("advisory aggregate count must match fixture count")
    if gate_safety.scenario_count != len(fixtures):
        raise ValueError("gate-safety aggregate count must match fixture count")
    if len(advisory.scenario_scores) != len(fixtures):
        raise ValueError("advisory scenario scores must match fixture count")
    if len(gate_safety.scenario_scores) != len(fixtures):
        raise ValueError("gate-safety scenario scores must match fixture count")

    regression_refs = dict(regression_refs or {})
    fixture_ids = {fixture.scenario_id for fixture in fixtures}
    unknown_regressions = sorted(set(regression_refs) - fixture_ids)
    if unknown_regressions:
        raise ValueError(f"regression references target unknown scenarios: {unknown_regressions}")

    scenarios: list[dict[str, Any]] = []
    for fixture, score, safety in zip(
        fixtures,
        advisory.scenario_scores,
        gate_safety.scenario_scores,
        strict=True,
    ):
        incident_id = fixture.ground_truth.incident_id
        if score.incident_id != incident_id:
            raise ValueError(
                "advisory score order/provenance mismatch: "
                f"scenario={fixture.scenario_id}, fixture_incident={incident_id}, "
                f"score_incident={score.incident_id}"
            )
        if score.gate_accepted is not safety.observed_acceptance:
            raise ValueError(
                "gate acceptance mismatch between advisory and safety measurements: "
                f"scenario={fixture.scenario_id}"
            )

        scenario: dict[str, Any] = {
            "scenario_id": fixture.scenario_id,
            "scenario_class": fixture.scenario_class,
            "incident_id": incident_id,
            "measurement": score.to_dict(),
            "gate_safety": safety.to_dict(),
            "constraints": dict(sorted(fixture.constraints.items())),
        }
        regression_ref = regression_refs.get(fixture.scenario_id)
        if regression_ref is not None:
            if safety.observed_acceptance:
                raise ValueError(
                    "accepted advisory scenario cannot be presented as a rejection regression: "
                    f"scenario={fixture.scenario_id}"
                )
            scenario["regression_ref"] = regression_ref
        scenarios.append(scenario)

    return {
        "schema_version": JUDGE_ARTIFACT_SCHEMA_VERSION,
        "evidence_scope": "synthetic deterministic advisory benchmark evidence only",
        "authorization_effect": "none",
        "scenario_count": len(scenarios),
        "aggregate": {
            "advisory": advisory.to_dict(),
            "gate_safety": gate_safety.to_dict(),
        },
        "scenarios": scenarios,
    }
