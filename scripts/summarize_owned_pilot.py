from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _require_non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _require_ratio(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError(f"{field} must be a number between 0 and 1")
    return float(value)


def validate_evidence(value: dict[str, Any]) -> dict[str, Any]:
    if value.get("schema_version") != "owned-multisurface-pilot/v1":
        raise ValueError("unsupported pilot evidence schema")
    if value.get("authorization_effect") != "none":
        raise ValueError("pilot evidence must remain authority-free")
    if value.get("restart_continuity_required") is not True:
        raise ValueError("pilot evidence must require restart continuity")

    controlled = value.get("controlled_incident")
    containment = value.get("containment")
    recovery = value.get("recovery")
    replay = value.get("replay")
    restoration = value.get("restoration")
    if not all(isinstance(v, dict) for v in (controlled, containment, recovery, replay, restoration)):
        raise TypeError("pilot lifecycle sections must be objects")

    surfaces = value.get("surfaces")
    if (
        not isinstance(surfaces, list)
        or not surfaces
        or any(not isinstance(surface, str) or not surface.strip() for surface in surfaces)
    ):
        raise ValueError("pilot surfaces must be a non-empty list of names")

    expected = _require_non_negative_int(controlled.get("expected_actions"), "controlled_incident.expected_actions")
    detected = _require_non_negative_int(controlled.get("detected_actions"), "controlled_incident.detected_actions")
    if detected > expected:
        raise ValueError("controlled_incident.detected_actions cannot exceed expected_actions")
    _require_ratio(controlled.get("blast_radius_recall"), "controlled_incident.blast_radius_recall")
    _require_ratio(controlled.get("blast_radius_precision"), "controlled_incident.blast_radius_precision")

    verified = _require_non_negative_int(recovery.get("verified_recoveries"), "recovery.verified_recoveries")
    if verified > expected:
        raise ValueError("recovery.verified_recoveries cannot exceed expected_actions")
    _require_non_negative_int(recovery.get("platform_residual_effects"), "recovery.platform_residual_effects")
    _require_non_negative_int(replay.get("unsafe_recovery_executions"), "replay.unsafe_recovery_executions")
    _require_non_negative_int(
        restoration.get("restored_downstream_authorities"),
        "restoration.restored_downstream_authorities",
    )

    for section, field in (
        (containment, "root_agent_remains_contained"),
        (replay, "verified"),
        (restoration, "root_authority_restored"),
    ):
        if not isinstance(section.get(field), bool):
            raise ValueError(f"{field} must be boolean")

    if not isinstance(value.get("scenario"), str) or not value["scenario"].strip():
        raise ValueError("scenario must be a non-empty string")
    if not isinstance(value.get("claim_boundary"), str) or not value["claim_boundary"].strip():
        raise ValueError("claim_boundary must be a non-empty string")
    return value


def load_evidence(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("pilot evidence must be an object")
    return validate_evidence(value)


def render_summary(evidence: dict[str, Any]) -> str:
    # Keep the reusable renderer fail-closed too. Callers must not be able to
    # bypass the loader and turn untrusted/canonical-looking data into a
    # buyer-facing claim surface.
    validate_evidence(evidence)
    controlled = evidence["controlled_incident"]
    containment = evidence["containment"]
    recovery = evidence["recovery"]
    replay = evidence["replay"]
    restoration = evidence["restoration"]
    surfaces = evidence["surfaces"]

    residuals = recovery["platform_residual_effects"]
    residual_truth = "none recorded" if residuals == 0 else f"{residuals} recorded"
    surface_text = ", ".join(surfaces)
    lines = [
        "# Owned multi-surface recovery pilot — evidence summary",
        "",
        f"Scenario: `{evidence['scenario']}`",
        "",
        "## What this proves in the owned sandbox",
        "",
        f"- Consequential actions detected: {controlled['detected_actions']}/{controlled['expected_actions']} across {len(surfaces)} bounded surfaces ({surface_text}).",
        f"- Blast-radius recall / precision: {controlled['blast_radius_recall']:.0%} / {controlled['blast_radius_precision']:.0%}.",
        f"- Verified recoveries: {recovery['verified_recoveries']}/{controlled['expected_actions']}.",
        f"- Compromised root authority remained contained: {str(containment['root_agent_remains_contained']).lower()}.",
        f"- Replay verified after recovery: {str(replay['verified']).lower()}; unsafe recovery executions: {replay['unsafe_recovery_executions']}.",
        f"- Restored downstream authorities: {restoration['restored_downstream_authorities']}; compromised root authority restored: {str(restoration['root_authority_restored']).lower()}.",
        f"- Platform residual effects: {residual_truth}.",
        "- Restart continuity is part of the pilot contract.",
        "",
        "## Claim boundary",
        "",
        evidence["claim_boundary"],
        "",
        "This summary is derived only from the canonical pilot evidence. It is not a production-security claim, customer-pilot result, authorization decision, or statement that irreversible external effects were undone.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a buyer-readable summary from canonical owned pilot evidence.")
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    summary = render_summary(load_evidence(args.evidence))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(summary, encoding="utf-8")
    print(summary, end="")


if __name__ == "__main__":
    main()
