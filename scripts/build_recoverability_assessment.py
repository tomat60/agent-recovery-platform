from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from run_owned_multisurface_pilot import build_pilot_evidence, validate_pilot_evidence

SCHEMA_VERSION = "agent-recoverability-assessment/v1"


def evidence_identity(evidence: dict[str, Any]) -> str:
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _build_remediation_plan(evidence: dict[str, Any]) -> list[dict[str, str]]:
    controlled = evidence["controlled_incident"]
    containment = evidence["containment"]
    recovery = evidence["recovery"]
    replay = evidence["replay"]
    restoration = evidence["restoration"]

    priorities: list[dict[str, str]] = []
    if recovery["verified_recoveries"] < controlled["expected_actions"]:
        priorities.append({
            "priority": "P0",
            "blocker": "incomplete_verified_recovery",
            "action": "Complete and independently verify every represented consequential recovery before restoration.",
        })
    if replay["verified"] is not True:
        priorities.append({
            "priority": "P0",
            "blocker": "replay_not_verified",
            "action": "Repair the control and obtain a current positive scope-bound replay before authority release.",
        })
    if restoration["root_authority_restored"] is True or containment["root_agent_remains_contained"] is not True:
        priorities.append({
            "priority": "P0",
            "blocker": "root_containment_not_preserved",
            "action": "Re-establish the independent incident hold; do not restore the compromised root authority.",
        })
    if recovery["platform_residual_effects"]:
        priorities.append({
            "priority": "P1",
            "blocker": "residual_effects_remain",
            "action": "Record residual effects explicitly and assign operator remediation; never represent them as undone.",
        })
    if not priorities:
        priorities.append({
            "priority": "P2",
            "blocker": "no_evidence_blocker_in_owned_sandbox",
            "action": "Preserve the verified recovery/replay controls and validate them against the next bounded pilot scenario.",
        })
    return priorities


def build_assessment(evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    evidence = build_pilot_evidence() if evidence is None else evidence
    validate_pilot_evidence(evidence)

    controlled = evidence["controlled_incident"]
    recovery = evidence["recovery"]
    replay = evidence["replay"]
    restoration = evidence["restoration"]

    expected = controlled["expected_actions"]
    verified = recovery["verified_recoveries"]
    coverage = verified / expected if expected else 0.0

    return {
        "schema_version": SCHEMA_VERSION,
        "authorization_effect": "none",
        "assessment_mode": "owned_sandbox_evidence",
        "scenario": evidence["scenario"],
        "source_evidence_identity": {
            "schema_version": evidence["schema_version"],
            "sha256": evidence_identity(evidence),
        },
        "tool_authority_map": {
            "surfaces": list(evidence["surfaces"]),
            "consequential_actions": expected,
        },
        "recoverability_coverage": {
            "verified_recoveries": verified,
            "consequential_actions": expected,
            "ratio": coverage,
        },
        "controlled_incident": controlled,
        "containment": evidence["containment"],
        "recovery": recovery,
        "replay_regression": replay,
        "restoration": restoration,
        "residual_risk": {
            "platform_residual_effects": recovery["platform_residual_effects"],
            "root_authority_remains_contained": evidence["containment"]["root_agent_remains_contained"],
        },
        "prioritized_remediation": _build_remediation_plan(evidence),
        "decision": {
            "bounded_downstream_restoration_verified": (
                replay["verified"] is True
                and restoration["restored_downstream_authorities"] >= 1
                and restoration["root_authority_restored"] is False
            ),
            "production_security_claim": False,
        },
        "claim_boundary": evidence["claim_boundary"],
    }


def validate_assessment(assessment: dict[str, Any]) -> None:
    if assessment.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported recoverability assessment schema")
    if assessment.get("authorization_effect") != "none":
        raise ValueError("assessment must not grant authority")
    if assessment.get("assessment_mode") != "owned_sandbox_evidence":
        raise ValueError("assessment must remain scoped to owned sandbox evidence")
    coverage = assessment.get("recoverability_coverage")
    source_identity = assessment.get("source_evidence_identity")
    decision = assessment.get("decision")
    remediation = assessment.get("prioritized_remediation")
    if not isinstance(coverage, dict) or not isinstance(decision, dict):
        raise TypeError("assessment coverage and decision must be objects")
    if not isinstance(source_identity, dict):
        raise TypeError("assessment source evidence identity must be an object")
    if source_identity.get("schema_version") != "owned-multisurface-pilot/v1":
        raise ValueError("assessment source evidence schema must match the owned pilot")
    source_sha = source_identity.get("sha256")
    if (
        not isinstance(source_sha, str)
        or len(source_sha) != 64
        or any(char not in "0123456789abcdef" for char in source_sha)
    ):
        raise ValueError("assessment source evidence identity must be a lowercase SHA-256 digest")
    if not isinstance(remediation, list) or not remediation:
        raise ValueError("assessment must include prioritized remediation")
    for item in remediation:
        if not isinstance(item, dict) or item.get("priority") not in {"P0", "P1", "P2"}:
            raise ValueError("assessment remediation entries must have bounded priorities")
        if not isinstance(item.get("blocker"), str) or not isinstance(item.get("action"), str):
            raise ValueError("assessment remediation entries must be evidence-readable")
    ratio = coverage.get("ratio")
    if not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or not 0 <= ratio <= 1:
        raise ValueError("recoverability coverage ratio must be numeric in [0, 1]")
    if decision.get("production_security_claim") is not False:
        raise ValueError("assessment must not claim production security effectiveness")


def reproduce(output_path: Path) -> dict[str, Any]:
    assessment = build_assessment()
    validate_assessment(assessment)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(assessment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reloaded = json.loads(output_path.read_text(encoding="utf-8"))
    validate_assessment(reloaded)
    return reloaded


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a bounded Agent Recoverability Assessment artifact.")
    parser.add_argument("output_path", type=Path)
    args = parser.parse_args()
    print(json.dumps(reproduce(args.output_path), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
