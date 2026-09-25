from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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
    if not all(isinstance(section, dict) for section in (controlled, containment, recovery, replay, restoration)):
        raise TypeError("pilot lifecycle sections must be objects")

    expected = controlled.get("expected_actions")
    detected = controlled.get("detected_actions")
    if not isinstance(expected, int) or isinstance(expected, bool) or expected < 2:
        raise ValueError("pilot summary requires multiple consequential actions")
    if not isinstance(detected, int) or isinstance(detected, bool) or detected != expected:
        raise ValueError("pilot summary requires complete action detection")
    for name in ("blast_radius_recall", "blast_radius_precision"):
        metric = controlled.get(name)
        if not isinstance(metric, (int, float)) or isinstance(metric, bool) or metric != 1.0:
            raise ValueError(f"pilot summary requires complete {name}")
    if containment.get("root_agent_remains_contained") is not True:
        raise ValueError("pilot summary requires compromised root containment")

    verified = recovery.get("verified_recoveries")
    residuals = recovery.get("platform_residual_effects")
    if not isinstance(verified, int) or isinstance(verified, bool) or verified != expected:
        raise ValueError("pilot summary requires verified recovery for every consequential action")
    if not isinstance(residuals, int) or isinstance(residuals, bool) or residuals < 0:
        raise ValueError("pilot summary residual count must be a non-negative integer")

    if replay.get("verified") is not True:
        raise ValueError("pilot summary requires verified replay")
    unsafe = replay.get("unsafe_recovery_executions")
    if not isinstance(unsafe, int) or isinstance(unsafe, bool) or unsafe != 0:
        raise ValueError("pilot summary requires zero unsafe recovery executions")

    if restoration.get("root_authority_restored") is not False:
        raise ValueError("pilot summary must not restore compromised root authority")
    restored = restoration.get("restored_downstream_authorities")
    if not isinstance(restored, int) or isinstance(restored, bool) or not 1 <= restored <= expected:
        raise ValueError("pilot summary requires bounded downstream restoration")
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
    if not all(isinstance(v, dict) for v in (controlled, containment, recovery, replay, restoration)):
        raise TypeError("pilot lifecycle sections must be objects")
    if not isinstance(surfaces, list):
        raise TypeError("pilot surfaces must be a list")

    residuals = recovery["platform_residual_effects"]
    residual_truth = "none recorded" if residuals == 0 else f"{residuals} recorded"
    surface_text = ", ".join(str(surface) for surface in surfaces)
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
        str(evidence["claim_boundary"]),
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
