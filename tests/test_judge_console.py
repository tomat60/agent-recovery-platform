import pytest

from agent_recovery.judge_artifact import JUDGE_ARTIFACT_SCHEMA_VERSION
from agent_recovery.judge_console import build_judge_advisory_console


def _artifact() -> dict[str, object]:
    return {
        "schema_version": JUDGE_ARTIFACT_SCHEMA_VERSION,
        "evidence_scope": "synthetic deterministic advisory benchmark evidence only",
        "authorization_effect": "none",
        "scenario_count": 1,
        "aggregate": {"advisory": {"scenario_count": 1}},
        "scenarios": [
            {
                "scenario_id": "B01",
                "scenario_class": "indirect_prompt_injection",
                "incident_id": "inc-b01",
                "measurement": {"gate_accepted": False},
                "gate_safety": {"observed_acceptance": False},
                "regression_ref": "regressions/B01.json",
            }
        ],
    }


def test_builds_authority_free_console_without_inventing_recovery_truth() -> None:
    console = build_judge_advisory_console(_artifact())

    assert console["view"] == "judge-advisory-console/v1"
    assert console["scenario_count"] == 1
    assert "No approval, execution, or restoration authority" in console["authority_notice"]
    assert console["scenarios"][0]["regression_ref"] == "regressions/B01.json"
    assert "replay" in console["unrepresented_claims"]


def test_rejects_authoritative_artifact() -> None:
    artifact = _artifact()
    artifact["authorization_effect"] = "approve"

    with pytest.raises(ValueError, match="authority-free"):
        build_judge_advisory_console(artifact)


def test_rejects_scenario_count_mismatch() -> None:
    artifact = _artifact()
    artifact["scenario_count"] = 2

    with pytest.raises(ValueError, match="scenario count mismatch"):
        build_judge_advisory_console(artifact)


def test_rejects_missing_measured_provenance() -> None:
    artifact = _artifact()
    artifact["scenarios"] = [{"scenario_id": "B01"}]

    with pytest.raises(ValueError, match="missing measured provenance"):
        build_judge_advisory_console(artifact)
