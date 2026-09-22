from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "run_owned_multisurface_pilot.py"
SPEC = importlib.util.spec_from_file_location("owned_multisurface_pilot", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


def test_owned_pilot_is_repeatable_and_authority_free(tmp_path):
    first = pilot.reproduce(tmp_path / "first")
    second = pilot.reproduce(tmp_path / "second")

    assert first == second
    assert first["authorization_effect"] == "none"
    assert first["verification"]["multi_surface"] is True
    assert first["verification"]["root_authority_contained"] is True
    assert first["verification"]["unsafe_recovery_executions"] == 0

    evidence = json.loads((tmp_path / "first" / "pilot-evidence.json").read_text(encoding="utf-8"))
    assert evidence["restart_continuity_required"] is True
    assert evidence["surfaces"] == ["shared_support_state", "downstream_identity_authority"]
    assert evidence["restoration"]["root_authority_restored"] is False


def test_owned_pilot_rejects_authority_or_scope_drift():
    evidence = pilot.build_pilot_evidence()

    evidence["authorization_effect"] = "restore"
    with pytest.raises(ValueError, match="authority-free"):
        pilot.validate_pilot_evidence(evidence)

    evidence = pilot.build_pilot_evidence()
    evidence["surfaces"] = ("shared_support_state",)
    with pytest.raises(ValueError, match="exact two bounded"):
        pilot.validate_pilot_evidence(evidence)


def test_owned_pilot_rejects_unsafe_recovery_or_root_restoration():
    evidence = pilot.build_pilot_evidence()
    evidence["replay"]["unsafe_recovery_executions"] = 1
    with pytest.raises(ValueError, match="unsafe recovery"):
        pilot.validate_pilot_evidence(evidence)

    evidence = pilot.build_pilot_evidence()
    evidence["restoration"]["root_authority_restored"] = True
    with pytest.raises(ValueError, match="must not restore"):
        pilot.validate_pilot_evidence(evidence)


def test_owned_pilot_rejects_incomplete_detection_recovery_or_replay():
    evidence = pilot.build_pilot_evidence()
    evidence["controlled_incident"]["detected_actions"] -= 1
    with pytest.raises(ValueError, match="complete blast-radius"):
        pilot.validate_pilot_evidence(evidence)

    evidence = pilot.build_pilot_evidence()
    evidence["recovery"]["verified_recoveries"] -= 1
    with pytest.raises(ValueError, match="every consequential action"):
        pilot.validate_pilot_evidence(evidence)

    evidence = pilot.build_pilot_evidence()
    evidence["replay"]["verified"] = False
    with pytest.raises(ValueError, match="positive replay"):
        pilot.validate_pilot_evidence(evidence)


def test_owned_pilot_rejects_missing_or_overbroad_downstream_restoration():
    evidence = pilot.build_pilot_evidence()
    evidence["restoration"]["restored_downstream_authorities"] = 0
    with pytest.raises(ValueError, match="bounded downstream restoration"):
        pilot.validate_pilot_evidence(evidence)

    evidence = pilot.build_pilot_evidence()
    evidence["restoration"]["restored_downstream_authorities"] = (
        evidence["controlled_incident"]["expected_actions"] + 1
    )
    with pytest.raises(ValueError, match="bounded downstream restoration"):
        pilot.validate_pilot_evidence(evidence)


def test_owned_pilot_rejects_malformed_lifecycle_counts():
    evidence = pilot.build_pilot_evidence()
    evidence["controlled_incident"]["expected_actions"] = True
    with pytest.raises(ValueError, match="multiple consequential actions"):
        pilot.validate_pilot_evidence(evidence)

    evidence = pilot.build_pilot_evidence()
    evidence["recovery"]["verified_recoveries"] = True
    with pytest.raises(TypeError, match="verified recovery count"):
        pilot.validate_pilot_evidence(evidence)

    evidence = pilot.build_pilot_evidence()
    evidence["replay"]["verified"] = 1
    with pytest.raises(TypeError, match="replay verification"):
        pilot.validate_pilot_evidence(evidence)

    evidence = pilot.build_pilot_evidence()
    evidence["replay"]["unsafe_recovery_executions"] = False
    with pytest.raises(TypeError, match="unsafe recovery execution count"):
        pilot.validate_pilot_evidence(evidence)
