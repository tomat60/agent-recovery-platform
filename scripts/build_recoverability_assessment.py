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
    detected = controlled["detected_actions"]
    verified = recovery["verified_recoveries"]
    detected_coverage = detected / expected if expected else 0.0
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
        "coverage_dimensions": {
            "incident_detection": {
                "detected_actions": detected,
                "consequential_actions": expected,
                "ratio": detected_coverage,
                "complete": detected == expected,
            },
            "verified_recovery_outcomes": {
                "verified_recoveries": verified,
                "consequential_actions": expected,
                "ratio": coverage,
                "complete": verified == expected,
            },
            "replay_regression_verified": replay["verified"] is True,
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
    dimensions = assessment.get("coverage_dimensions")
    decision = assessment.get("decision")
    remediation = assessment.get("prioritized_remediation")
    if not isinstance(coverage, dict) or not isinstance(decision, dict):
        raise TypeError("assessment coverage and decision must be objects")
    if not isinstance(source_identity, dict):
        raise TypeError("assessment source evidence identity must be an object")
    if not isinstance(dimensions, dict):
        raise TypeError("assessment coverage dimensions must be an object")
    for name in ("incident_detection", "verified_recovery_outcomes"):
        dimension = dimensions.get(name)
        if not isinstance(dimension, dict):
            raise TypeError(f"assessment coverage dimension {name} must be an object")
        dimension_ratio = dimension.get("ratio")
        if (
            not isinstance(dimension_ratio, (int, float))
            or isinstance(dimension_ratio, bool)
            or not 0 <= dimension_ratio <= 1
        ):
            raise ValueError(f"assessment coverage dimension {name} ratio must be numeric in [0, 1]")
        if not isinstance(dimension.get("complete"), bool):
            raise TypeError(f"assessment coverage dimension {name} complete flag must be boolean")
    if not isinstance(dimensions.get("replay_regression_verified"), bool):
        raise TypeError("assessment replay regression coverage flag must be boolean")

    dimension_contracts = (
        ("incident_detection", "detected_actions"),
        ("verified_recovery_outcomes", "verified_recoveries"),
    )
    for name, numerator_name in dimension_contracts:
        dimension = dimensions[name]
        numerator = dimension.get(numerator_name)
        denominator = dimension.get("consequential_actions")
        if (
            not isinstance(numerator, int)
            or isinstance(numerator, bool)
            or not isinstance(denominator, int)
            or isinstance(denominator, bool)
            or numerator < 0
            or denominator < 0
            or numerator > denominator
        ):
            raise ValueError(
                f"assessment coverage dimension {name} counts must be bounded non-negative integers"
            )
        expected_ratio = numerator / denominator if denominator else 0.0
        if abs(dimension["ratio"] - expected_ratio) > 1e-12:
            raise ValueError(
                f"assessment coverage dimension {name} ratio must match its evidence counts"
            )
        if dimension["complete"] is not (numerator == denominator):
            raise ValueError(
                f"assessment coverage dimension {name} complete flag must match its evidence counts"
            )

    verified_dimension = dimensions["verified_recovery_outcomes"]
    for field in ("verified_recoveries", "consequential_actions"):
        if coverage.get(field) != verified_dimension[field]:
            raise ValueError(
                "recoverability coverage must match the verified recovery outcome dimension"
            )
    summary_ratio = coverage.get("ratio")
    if (
        not isinstance(summary_ratio, (int, float))
        or isinstance(summary_ratio, bool)
        or not 0 <= summary_ratio <= 1
    ):
        raise ValueError("recoverability coverage ratio must be numeric in [0, 1]")
    if abs(summary_ratio - verified_dimension["ratio"]) > 1e-12:
        raise ValueError(
            "recoverability coverage ratio must match the verified recovery outcome dimension"
        )
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
