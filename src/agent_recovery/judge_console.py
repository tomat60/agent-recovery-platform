from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .judge_artifact import JUDGE_ARTIFACT_SCHEMA_VERSION


def build_judge_advisory_console(artifact: Mapping[str, Any]) -> dict[str, Any]:
    """Render measured advisory evidence into a deterministic judge-facing console model.

    This function is presentation-only. It preserves measured values and explicit limitations;
    it never creates approvals, candidate plans, recovery execution, or restoration authority.
    """

    if artifact.get("schema_version") != JUDGE_ARTIFACT_SCHEMA_VERSION:
        raise ValueError("unsupported judge artifact schema")
    if artifact.get("authorization_effect") != "none":
        raise ValueError("judge console requires an authority-free artifact")

    scenarios = artifact.get("scenarios")
    if not isinstance(scenarios, list):
        raise TypeError("judge artifact scenarios must be a list")
    if artifact.get("scenario_count") != len(scenarios):
        raise ValueError("judge artifact scenario count mismatch")

    rendered_scenarios: list[dict[str, Any]] = []
    for scenario in scenarios:
        if not isinstance(scenario, Mapping):
            raise TypeError("judge artifact scenario must be an object")
        required = ("scenario_id", "scenario_class", "incident_id", "measurement", "gate_safety")
        if any(key not in scenario for key in required):
            raise ValueError("judge artifact scenario is missing measured provenance")
        rendered_scenarios.append(
            {
                "scenario_id": scenario["scenario_id"],
                "scenario_class": scenario["scenario_class"],
                "incident_id": scenario["incident_id"],
                "measurement": scenario["measurement"],
                "gate_safety": scenario["gate_safety"],
                "regression_ref": scenario.get("regression_ref"),
            }
        )

    return {
        "view": "judge-advisory-console/v1",
        "evidence_scope": artifact.get("evidence_scope"),
        "authority_notice": (
            "Measured advisory evidence only. No approval, execution, or restoration authority."
        ),
        "scenario_count": len(rendered_scenarios),
        "aggregate": artifact.get("aggregate"),
        "scenarios": rendered_scenarios,
        "unrepresented_claims": (
            "blast radius, containment, recovery execution, residual effects, replay, and "
            "restoration truth require their own deterministic evidence artifacts"
        ),
    }
