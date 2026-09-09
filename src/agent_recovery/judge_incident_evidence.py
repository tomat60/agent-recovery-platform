from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .multi_agent_benchmark import run_multi_agent_recovery_scenario


SCHEMA_VERSION = "judge-incident-evidence/v1"
SCENARIO = "poisoned_support_to_shared_state_to_identity"


def build_judge_incident_evidence() -> dict[str, Any]:
    """Build bounded end-to-end evidence from the deterministic multi-agent scenario.

    This view reports only facts measured by the existing benchmark. It grants no
    approval, execution, compensation, replay, or restoration authority.
    """

    score = run_multi_agent_recovery_scenario()
    if score.scenario != SCENARIO:
        raise ValueError("unexpected incident scenario")
    if score.detected_blast_actions > score.expected_blast_actions:
        raise ValueError("blast-radius evidence is internally inconsistent")
    if score.platform_residual_effects < 0 or score.unsafe_recovery_executions < 0:
        raise ValueError("incident evidence counts must be non-negative")

    measured = asdict(score)
    return {
        "schema_version": SCHEMA_VERSION,
        "authorization_effect": "none",
        "scenario": score.scenario,
        "phases": {
            "blast_radius": {
                "expected_actions": score.expected_blast_actions,
                "detected_actions": score.detected_blast_actions,
                "recall": score.blast_radius_recall,
                "precision": score.blast_radius_precision,
            },
            "containment": {
                "root_agent_remains_contained": score.root_agent_remains_contained,
            },
            "recovery": {
                "verified_recoveries": score.verified_recoveries,
                "platform_residual_effects": score.platform_residual_effects,
            },
            "replay": {
                "verified": score.replay_verified,
                "unsafe_recovery_executions": score.unsafe_recovery_executions,
            },
            "restoration": {
                "restored_downstream_authorities": score.restored_downstream_authorities,
                "root_authority_restored": False,
            },
        },
        "measured_score": measured,
        "claim_boundary": (
            "Synthetic deterministic evidence only; this artifact does not grant authority "
            "or establish production security effectiveness."
        ),
    }


def validate_judge_incident_evidence(evidence: dict[str, Any]) -> None:
    if evidence.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported incident evidence schema")
    if evidence.get("authorization_effect") != "none":
        raise ValueError("judge incident evidence must not carry execution authority")
    if evidence.get("scenario") != SCENARIO:
        raise ValueError("incident evidence scenario mismatch")
    phases = evidence.get("phases")
    if not isinstance(phases, dict):
        raise TypeError("incident evidence phases must be an object")
    required = {"blast_radius", "containment", "recovery", "replay", "restoration"}
    if set(phases) != required:
        raise ValueError("incident evidence must contain the exact required phases")
