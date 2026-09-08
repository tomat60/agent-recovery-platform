from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .advisory_benchmark import AdvisoryGroundTruth


@dataclass(frozen=True)
class AdvisoryBenchmarkFixture:
    scenario_id: str
    scenario_class: str
    ground_truth: AdvisoryGroundTruth
    constraints: dict[str, bool]


def _required_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_unique_strings(payload: dict[str, Any], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
    ):
        raise ValueError(f"{key} must be a non-empty list of strings")
    if len(set(value)) != len(value):
        raise ValueError(f"{key} must not contain duplicates")
    return tuple(value)


def load_advisory_fixture(path: str | Path) -> AdvisoryBenchmarkFixture:
    """Load one versioned advisory benchmark fixture with fail-closed validation."""

    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("advisory fixture must be a JSON object")

    constraints = payload.get("constraints")
    if not isinstance(constraints, dict) or not constraints:
        raise ValueError("constraints must be a non-empty object")
    if not all(
        isinstance(key, str) and isinstance(value, bool)
        for key, value in constraints.items()
    ):
        raise ValueError("constraints must map string names to boolean values")

    scenario_id = _required_string(payload, "scenario_id")
    scenario_class = _required_string(payload, "scenario_class")
    incident_id = _required_string(payload, "incident_id")

    if (
        "model_output_is_authorization" in constraints
        and constraints["model_output_is_authorization"]
    ):
        raise ValueError("model output must never be authorization")

    return AdvisoryBenchmarkFixture(
        scenario_id=scenario_id,
        scenario_class=scenario_class,
        ground_truth=AdvisoryGroundTruth(
            incident_id=incident_id,
            root_cause_event_ids=_required_unique_strings(payload, "root_cause_event_ids"),
            required_step_ids=_required_unique_strings(payload, "required_step_ids"),
            required_evidence_event_ids=_required_unique_strings(
                payload,
                "required_evidence_event_ids",
            ),
        ),
        constraints=dict(constraints),
    )


def load_advisory_fixture_suite(
    directory: str | Path,
) -> tuple[AdvisoryBenchmarkFixture, ...]:
    """Load the deterministic B01-B10 fixture suite and reject incomplete catalogs."""

    fixture_paths = sorted(Path(directory).glob("b*.json"))
    fixtures = tuple(load_advisory_fixture(path) for path in fixture_paths)
    if not fixtures:
        raise ValueError("advisory fixture suite is empty")

    scenario_ids = [fixture.scenario_id for fixture in fixtures]
    incident_ids = [fixture.ground_truth.incident_id for fixture in fixtures]
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("advisory fixture suite has duplicate scenario IDs")
    if len(set(incident_ids)) != len(incident_ids):
        raise ValueError("advisory fixture suite has duplicate incident IDs")

    expected = {f"B{index:02d}" for index in range(1, 11)}
    if set(scenario_ids) != expected:
        missing = sorted(expected - set(scenario_ids))
        extra = sorted(set(scenario_ids) - expected)
        raise ValueError(
            "advisory fixture suite must cover B01-B10 exactly; "
            f"missing={missing}, extra={extra}"
        )

    return fixtures
