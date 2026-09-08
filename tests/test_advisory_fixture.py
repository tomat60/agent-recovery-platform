import json
from pathlib import Path

import pytest

from agent_recovery.advisory_fixture import (
    load_advisory_fixture,
    load_advisory_fixture_suite,
)


def test_loads_complete_versioned_b01_b10_suite() -> None:
    directory = Path(__file__).parents[1] / "benchmarks/advisory"
    fixtures = load_advisory_fixture_suite(directory)

    assert tuple(fixture.scenario_id for fixture in fixtures) == tuple(
        f"B{index:02d}" for index in range(1, 11)
    )
    assert len({fixture.ground_truth.incident_id for fixture in fixtures}) == 10
    assert all(fixture.ground_truth.root_cause_event_ids for fixture in fixtures)
    assert all(fixture.ground_truth.required_step_ids for fixture in fixtures)
    assert all(fixture.ground_truth.required_evidence_event_ids for fixture in fixtures)
    assert all(
        fixture.constraints.get("model_output_is_authorization") is False
        for fixture in fixtures
    )


def test_rejects_duplicate_ground_truth_ids(tmp_path: Path) -> None:
    payload = {
        "scenario_id": "B01",
        "scenario_class": "synthetic",
        "incident_id": "incident-1",
        "root_cause_event_ids": ["e1", "e1"],
        "required_step_ids": ["contain"],
        "required_evidence_event_ids": ["e1"],
        "constraints": {"model_output_is_authorization": False},
    }
    path = tmp_path / "fixture.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="must not contain duplicates"):
        load_advisory_fixture(path)


def test_rejects_model_authorization_claim(tmp_path: Path) -> None:
    payload = {
        "scenario_id": "B01",
        "scenario_class": "synthetic",
        "incident_id": "incident-1",
        "root_cause_event_ids": ["e1"],
        "required_step_ids": ["contain"],
        "required_evidence_event_ids": ["e1"],
        "constraints": {"model_output_is_authorization": True},
    }
    path = tmp_path / "fixture.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="must never be authorization"):
        load_advisory_fixture(path)
