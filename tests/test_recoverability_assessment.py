from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT = SCRIPTS / "build_recoverability_assessment.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("build_recoverability_assessment", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_assessment_is_bounded_and_authority_free() -> None:
    assessment = module.build_assessment()
    module.validate_assessment(assessment)
    assert assessment["authorization_effect"] == "none"
    assert assessment["assessment_mode"] == "owned_sandbox_evidence"
    assert assessment["source_evidence_identity"] == {
        "schema_version": "owned-multisurface-pilot/v1",
        "sha256": module.evidence_identity(module.build_pilot_evidence()),
    }
    assert assessment["recoverability_coverage"]["ratio"] == 1.0
    assert assessment["coverage_dimensions"] == {
        "incident_detection": {
            "detected_actions": 2,
            "consequential_actions": 2,
            "ratio": 1.0,
            "complete": True,
        },
        "verified_recovery_outcomes": {
            "verified_recoveries": 2,
            "consequential_actions": 2,
            "ratio": 1.0,
            "complete": True,
        },
        "replay_regression_verified": True,
    }
    assert assessment["decision"]["bounded_downstream_restoration_verified"] is True
    assert assessment["decision"]["production_security_claim"] is False
    assert assessment["residual_risk"]["root_authority_remains_contained"] is True
    assert assessment["prioritized_remediation"]


def test_assessment_rejects_production_security_claim() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["decision"]["production_security_claim"] = True
    with pytest.raises(ValueError, match="production security"):
        module.validate_assessment(assessment)


def test_assessment_rejects_boolean_coverage_ratio() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["recoverability_coverage"]["ratio"] = True
    with pytest.raises(ValueError, match="coverage ratio"):
        module.validate_assessment(assessment)


def test_remediation_prioritizes_failed_recovery_and_replay() -> None:
    evidence = module.build_pilot_evidence()
    evidence["recovery"]["verified_recoveries"] = evidence["controlled_incident"]["expected_actions"] - 1
    evidence["replay"]["verified"] = False
    plan = module._build_remediation_plan(evidence)
    blockers = [item["blocker"] for item in plan]
    assert blockers[:2] == ["incomplete_verified_recovery", "replay_not_verified"]
    assert all(item["priority"] == "P0" for item in plan[:2])


def test_remediation_keeps_residual_effects_explicit() -> None:
    evidence = module.build_pilot_evidence()
    evidence["recovery"]["platform_residual_effects"] = ["external_notification"]
    plan = module._build_remediation_plan(evidence)
    residual = next(item for item in plan if item["blocker"] == "residual_effects_remain")
    assert residual["priority"] == "P1"
    assert "never represent them as undone" in residual["action"]


def test_assessment_rejects_missing_remediation() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["prioritized_remediation"] = []
    with pytest.raises(ValueError, match="prioritized remediation"):
        module.validate_assessment(assessment)


def test_source_evidence_identity_is_order_independent_and_content_bound() -> None:
    evidence = module.build_pilot_evidence()
    reordered = dict(reversed(list(evidence.items())))
    assert module.evidence_identity(evidence) == module.evidence_identity(reordered)

    changed = copy.deepcopy(evidence)
    changed["claim_boundary"] = f'{changed["claim_boundary"]} Additional bounded note.'
    assert module.evidence_identity(evidence) != module.evidence_identity(changed)


def test_assessment_rejects_malformed_source_evidence_identity() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["source_evidence_identity"]["sha256"] = "not-a-digest"
    with pytest.raises(ValueError, match="source evidence identity"):
        module.validate_assessment(assessment)


def test_assessment_names_detection_and_verified_outcomes_separately() -> None:
    assessment = module.build_assessment()
    dimensions = assessment["coverage_dimensions"]

    assert set(dimensions) == {
        "incident_detection",
        "verified_recovery_outcomes",
        "replay_regression_verified",
    }
    assert "detected_actions" in dimensions["incident_detection"]
    assert "verified_recoveries" in dimensions["verified_recovery_outcomes"]


def test_assessment_rejects_boolean_dimension_ratio() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["coverage_dimensions"]["verified_recovery_outcomes"]["ratio"] = True
    with pytest.raises(ValueError, match="coverage dimension verified_recovery_outcomes"):
        module.validate_assessment(assessment)
