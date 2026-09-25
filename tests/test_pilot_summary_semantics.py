from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "summarize_owned_pilot.py"
SPEC = importlib.util.spec_from_file_location("summarize_owned_pilot", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def sample() -> dict[str, object]:
    return {
        "schema_version": "owned-multisurface-pilot/v1",
        "authorization_effect": "none",
        "scenario": "owned-test",
        "surfaces": ["one", "two"],
        "controlled_incident": {
            "expected_actions": 2,
            "detected_actions": 3,
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


@pytest.mark.xfail(strict=True, reason="buyer summary must reject impossible action counts")
def test_summary_rejects_detected_count_above_expected() -> None:
    with pytest.raises(ValueError, match="detected actions"):
        MODULE.render_summary(sample())
