from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "summarize_owned_pilot.py"
SPEC = importlib.util.spec_from_file_location("summarize_owned_pilot_lifecycle", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_summary_rejects_incomplete_recovery_claim() -> None:
    value = {
        "schema_version": "owned-multisurface-pilot/v1",
        "authorization_effect": "none",
        "restart_continuity_required": True,
        "scenario": "owned-test",
        "surfaces": ["shared_support_state", "downstream_identity_authority"],
        "controlled_incident": {
            "expected_actions": 2,
            "detected_actions": 2,
            "blast_radius_recall": 1.0,
            "blast_radius_precision": 1.0,
        },
        "containment": {"root_agent_remains_contained": True},
        "recovery": {"verified_recoveries": 1, "platform_residual_effects": 0},
        "replay": {"verified": True, "unsafe_recovery_executions": 0},
        "restoration": {"restored_downstream_authorities": 1, "root_authority_restored": False},
        "claim_boundary": "Owned deterministic sandbox evidence only.",
    }
    with pytest.raises(ValueError, match="recovery"):
        MODULE.render_summary(value)
