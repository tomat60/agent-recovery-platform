from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_evidence(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("pilot evidence must be an object")
    if value.get("schema_version") != "owned-multisurface-pilot/v1":
        raise ValueError("unsupported pilot evidence schema")
    if value.get("authorization_effect") != "none":
        raise ValueError("pilot evidence must remain authority-free")
    return value


def render_summary(evidence: dict[str, Any]) -> str:
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
