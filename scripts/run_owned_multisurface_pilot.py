from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from agent_recovery.judge_incident_evidence import (
    build_judge_incident_evidence,
    validate_judge_incident_evidence,
)

SCHEMA_VERSION = "owned-multisurface-pilot/v1"
SURFACES = (
    "shared_support_state",
    "downstream_identity_authority",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_pilot_evidence() -> dict[str, object]:
    incident = build_judge_incident_evidence()
    validate_judge_incident_evidence(incident)
    phases = incident["phases"]
    measured = incident["measured_score"]
    if not isinstance(phases, dict) or not isinstance(measured, dict):
        raise TypeError("canonical incident evidence is malformed")

    blast = phases["blast_radius"]
    containment = phases["containment"]
    recovery = phases["recovery"]
    replay = phases["replay"]
    restoration = phases["restoration"]
    if not all(isinstance(value, dict) for value in (blast, containment, recovery, replay, restoration)):
        raise TypeError("canonical incident phases are malformed")

    expected_actions = blast["expected_actions"]
    if not isinstance(expected_actions, int) or expected_actions < 2:
        raise ValueError("pilot must exercise at least two consequential actions")

    return {
        "schema_version": SCHEMA_VERSION,
        "authorization_effect": "none",
        "scenario": incident["scenario"],
        "surfaces": SURFACES,
        "shared_incident_identity": incident["scenario"],
        "controlled_incident": {
            "expected_actions": expected_actions,
            "detected_actions": blast["detected_actions"],
            "blast_radius_recall": blast["recall"],
            "blast_radius_precision": blast["precision"],
        },
        "containment": {
            "root_agent_remains_contained": containment["root_agent_remains_contained"],
        },
        "recovery": {
            "verified_recoveries": recovery["verified_recoveries"],
            "platform_residual_effects": recovery["platform_residual_effects"],
        },
        "replay": {
            "verified": replay["verified"],
            "unsafe_recovery_executions": replay["unsafe_recovery_executions"],
        },
        "restoration": {
            "restored_downstream_authorities": restoration["restored_downstream_authorities"],
            "root_authority_restored": restoration["root_authority_restored"],
        },
        "restart_continuity_required": True,
        "canonical_measurement": measured,
        "claim_boundary": (
            "Owned deterministic sandbox evidence only; this artifact grants no approval, "
            "execution, recovery, replay, or restoration authority and does not establish "
            "production security effectiveness."
        ),
    }


def validate_pilot_evidence(evidence: dict[str, object]) -> None:
    if evidence.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported owned pilot schema")
    if evidence.get("authorization_effect") != "none":
        raise ValueError("owned pilot evidence must remain authority-free")
    if tuple(evidence.get("surfaces", ())) != SURFACES:
        raise ValueError("owned pilot must represent the exact two bounded side-effect surfaces")
    if evidence.get("restart_continuity_required") is not True:
        raise ValueError("owned pilot must require restart continuity")

    controlled = evidence.get("controlled_incident")
    containment = evidence.get("containment")
    recovery = evidence.get("recovery")
    replay = evidence.get("replay")
    restoration = evidence.get("restoration")
    if not all(isinstance(value, dict) for value in (controlled, containment, recovery, replay, restoration)):
        raise TypeError("owned pilot lifecycle sections must be objects")
    if controlled["expected_actions"] < 2:
        raise ValueError("owned pilot must exercise multiple consequential actions")
    if controlled["detected_actions"] > controlled["expected_actions"]:
        raise ValueError("owned pilot blast-radius evidence is inconsistent")
    if containment["root_agent_remains_contained"] is not True:
        raise ValueError("compromised root authority must remain contained")
    if replay["unsafe_recovery_executions"] != 0:
        raise ValueError("owned pilot recorded an unsafe recovery execution")
    if restoration["root_authority_restored"] is not False:
        raise ValueError("owned pilot must not restore compromised root authority")


def reproduce(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = build_pilot_evidence()
    validate_pilot_evidence(evidence)
    evidence_text = canonical_json(evidence)
    evidence_path = output_dir / "pilot-evidence.json"
    evidence_path.write_text(evidence_text, encoding="utf-8")

    reloaded = json.loads(evidence_path.read_text(encoding="utf-8"))
    validate_pilot_evidence(reloaded)
    reloaded_text = canonical_json(reloaded)
    if reloaded_text != evidence_text:
        raise ValueError("canonical pilot evidence changed after round-trip")

    manifest = {
        "schema_version": "owned-multisurface-pilot-manifest/v1",
        "authorization_effect": "none",
        "scenario": evidence["scenario"],
        "files": {
            evidence_path.name: {
                "sha256": sha256_text(evidence_text),
                "bytes": len(evidence_text.encode("utf-8")),
            }
        },
        "verification": {
            "pilot_schema_valid": True,
            "canonical_round_trip": True,
            "multi_surface": len(evidence["surfaces"]) == 2,
            "root_authority_contained": evidence["containment"]["root_agent_remains_contained"] is True,
            "unsafe_recovery_executions": evidence["replay"]["unsafe_recovery_executions"],
        },
        "claim_boundary": evidence["claim_boundary"],
    }
    (output_dir / "manifest.json").write_text(canonical_json(manifest), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce the bounded owned multi-surface recovery pilot evidence."
    )
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(canonical_json(reproduce(args.output_dir)), end="")


if __name__ == "__main__":
    main()
