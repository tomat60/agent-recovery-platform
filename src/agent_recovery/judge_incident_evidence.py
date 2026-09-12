from __future__ import annotations

from dataclasses import asdict

from .multi_agent_benchmark import run_multi_agent_recovery_scenario

SCHEMA_VERSION = "judge-incident-evidence/v1"
SCENARIO = "poisoned_support_to_shared_state_to_identity"


def build_judge_incident_evidence() -> dict[str, object]:
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


def _require_non_negative_int(value: object, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _require_rate(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be numeric")
    numeric = float(value)
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{field} must be between 0 and 1")
    return numeric


def _require_bool(value: object, field: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field} must be boolean")
    return value


def validate_judge_incident_evidence(evidence: dict[str, object]) -> None:
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
    for phase_name in required:
        if not isinstance(phases[phase_name], dict):
            raise TypeError(f"incident evidence phase {phase_name} must be an object")

    measured = evidence.get("measured_score")
    if not isinstance(measured, dict):
        raise TypeError("incident evidence measured_score must be an object")
    if measured.get("scenario") != SCENARIO:
        raise ValueError("measured score scenario mismatch")

    blast = phases["blast_radius"]
    containment = phases["containment"]
    recovery = phases["recovery"]
    replay = phases["replay"]
    restoration = phases["restoration"]

    expected_actions = _require_non_negative_int(blast.get("expected_actions"), "expected_actions")
    detected_actions = _require_non_negative_int(blast.get("detected_actions"), "detected_actions")
    if detected_actions > expected_actions:
        raise ValueError("detected actions cannot exceed expected actions")
    _require_rate(blast.get("recall"), "blast recall")
    _require_rate(blast.get("precision"), "blast precision")
    _require_bool(
        containment.get("root_agent_remains_contained"),
        "root_agent_remains_contained",
    )
    _require_non_negative_int(recovery.get("verified_recoveries"), "verified_recoveries")
    _require_non_negative_int(
        recovery.get("platform_residual_effects"),
        "platform_residual_effects",
    )
    _require_bool(replay.get("verified"), "replay verified")
    _require_non_negative_int(
        replay.get("unsafe_recovery_executions"),
        "unsafe_recovery_executions",
    )
    _require_non_negative_int(
        restoration.get("restored_downstream_authorities"),
        "restored_downstream_authorities",
    )
    root_restored = _require_bool(
        restoration.get("root_authority_restored"),
        "root_authority_restored",
    )
    if root_restored:
        raise ValueError("judge evidence must not claim root authority restored")

    correspondence = {
        "expected_blast_actions": blast.get("expected_actions"),
        "detected_blast_actions": blast.get("detected_actions"),
        "blast_radius_recall": blast.get("recall"),
        "blast_radius_precision": blast.get("precision"),
        "root_agent_remains_contained": containment.get("root_agent_remains_contained"),
        "verified_recoveries": recovery.get("verified_recoveries"),
        "platform_residual_effects": recovery.get("platform_residual_effects"),
        "replay_verified": replay.get("verified"),
        "unsafe_recovery_executions": replay.get("unsafe_recovery_executions"),
        "restored_downstream_authorities": restoration.get("restored_downstream_authorities"),
    }
    for field, represented in correspondence.items():
        if measured.get(field) != represented:
            raise ValueError(f"phase evidence does not match measured score: {field}")

    if measured.get("root_agent_remains_contained") is not True:
        raise ValueError("measured score must keep root authority contained")
