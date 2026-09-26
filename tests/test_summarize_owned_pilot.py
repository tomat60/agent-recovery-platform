from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "summarize_owned_pilot.py"
SPEC = importlib.util.spec_from_file_location("summarize_owned_pilot", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def evidence() -> dict[str, object]:
    return {
        "schema_version": "owned-multisurface-pilot/v1",
        "authorization_effect": "none",
        "scenario": "owned-test",
        "surfaces": ["shared_support_state", "downstream_identity_authority"],
        "controlled_incident": {
            "expected_actions": 2,
            "detected_actions": 2,
            "blast_radius_recall": 1.0,
            "blast_radius_precision": 1.0,
        },
        "containment": {"root_agent_remains_contained": True},
        "recovery": {"verified_recoveries": 2, "platform_residual_effects": 0},
        "replay": {"verified": True, "unsafe_recovery_executions": 0},
        "restoration": {"restored_downstream_authorities": 1, "root_authority_restored": False},
        "restart_continuity_required": True,
        "claim_boundary": "Owned deterministic sandbox evidence only.",
    }


def test_summary_preserves_claim_boundary_and_residual_truth() -> None:
    summary = MODULE.render_summary(evidence())
    assert "Consequential actions detected: 2/2" in summary
    assert "Verified recoveries: 2/2" in summary
    assert "Platform residual effects: none recorded" in summary
    assert "Owned deterministic sandbox evidence only." in summary
    assert "Evidence schema: `owned-multisurface-pilot/v1`" in summary
    assert f"Evidence identity (SHA-256): `{MODULE.evidence_identity(evidence())}`" in summary
    assert "not a production-security claim" in summary


def test_loader_rejects_authority_bearing_artifact(tmp_path: Path) -> None:
    import json

    value = evidence()
    value["authorization_effect"] = "restore"
    path = tmp_path / "pilot.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="authority-free"):
        MODULE.load_evidence(path)


def test_loader_rejects_missing_restart_continuity_contract(tmp_path: Path) -> None:
    import json

    value = evidence()
    value["restart_continuity_required"] = False
    path = tmp_path / "pilot.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="restart continuity"):
        MODULE.load_evidence(path)


def test_renderer_rejects_direct_authority_bypass() -> None:
    value = evidence()
    value["authorization_effect"] = "restore"
    with pytest.raises(ValueError, match="authority-free"):
        MODULE.render_summary(value)


def test_renderer_rejects_direct_restart_continuity_bypass() -> None:
    value = evidence()
    value["restart_continuity_required"] = False
    with pytest.raises(ValueError, match="restart continuity"):
        MODULE.render_summary(value)


def test_evidence_identity_is_order_independent_and_content_bound() -> None:
    value = evidence()
    reordered = dict(reversed(list(value.items())))
    assert MODULE.evidence_identity(value) == MODULE.evidence_identity(reordered)

    changed = evidence()
    changed["scenario"] = "different-owned-test"
    assert MODULE.evidence_identity(value) != MODULE.evidence_identity(changed)
