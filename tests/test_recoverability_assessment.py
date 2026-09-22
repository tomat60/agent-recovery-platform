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
    assert assessment["recoverability_coverage"]["ratio"] == 1.0
    assert assessment["decision"]["bounded_downstream_restoration_verified"] is True
    assert assessment["decision"]["production_security_claim"] is False
    assert assessment["residual_risk"]["root_authority_remains_contained"] is True


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
