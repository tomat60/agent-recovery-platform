from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from run_owned_multisurface_pilot import build_pilot_evidence, validate_pilot_evidence

SCHEMA_VERSION = "agent-recoverability-assessment/v1"
MANIFEST_SCHEMA_VERSION = "agent-recoverability-assessment-manifest/v1"


def evidence_identity(evidence: dict[str, Any]) -> str:
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _artifact_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_artifact_manifest(
    assessment: dict[str, Any],
    assessment_json: str,
    buyer_markdown: str,
) -> dict[str, Any]:
    validate_assessment(assessment)
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "authorization_effect": "none",
        "source_evidence_identity": dict(assessment["source_evidence_identity"]),
        "artifacts": {
            "assessment_json": {"sha256": _artifact_digest(assessment_json)},
            "buyer_markdown": {"sha256": _artifact_digest(buyer_markdown)},
        },
    }


def validate_artifact_manifest(
    manifest: dict[str, Any],
    assessment: dict[str, Any],
    assessment_json: str,
    buyer_markdown: str,
) -> None:
    validate_assessment(assessment)
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ValueError("unsupported assessment artifact manifest schema")
    if manifest.get("authorization_effect") != "none":
        raise ValueError("assessment artifact manifest must not grant authority")
    if manifest.get("source_evidence_identity") != assessment["source_evidence_identity"]:
        raise ValueError("assessment artifact manifest must match source evidence identity")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != {
        "assessment_json",
        "buyer_markdown",
    }:
        raise ValueError("assessment artifact manifest must bind the complete artifact set")

    expected = {
        "assessment_json": _artifact_digest(assessment_json),
        "buyer_markdown": _artifact_digest(buyer_markdown),
    }
    for name, digest in expected.items():
        entry = artifacts.get(name)
        if not isinstance(entry, dict) or entry.get("sha256") != digest:
            raise ValueError(f"assessment artifact manifest digest mismatch for {name}")


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


def _markdown_text(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def render_assessment(assessment: dict[str, Any]) -> str:
    """Render a deterministic buyer-readable view without granting authority."""

    validate_assessment(assessment)
    dimensions = assessment["coverage_dimensions"]
    detection = dimensions["incident_detection"]
    outcomes = dimensions["verified_recovery_outcomes"]
    source_identity = assessment["source_evidence_identity"]
    restoration = assessment["restoration"]
    residual_effect_count = assessment["residual_risk"]["platform_residual_effects"]

    lines = [
        "# Agent Recoverability Assessment",
        "",
        "## Scope and evidence identity",
        "",
        f"- Scenario: {_markdown_text(assessment['scenario'])}",
        f"- Assessment schema: {_markdown_text(assessment['schema_version'])}",
        f"- Evidence schema: {_markdown_text(source_identity['schema_version'])}",
        f"- Evidence SHA-256: `{source_identity['sha256']}`",
        "- Environment: owned synthetic sandbox",
        "- Authorization effect: none",
        "",
        "## Measured coverage",
        "",
        "| Dimension | Evidence | Coverage | Complete |",
        "| --- | ---: | ---: | --- |",
        (
            "| Incident detection | "
            f"{detection['detected_actions']}/{detection['consequential_actions']} | "
            f"{detection['ratio']:.0%} | {str(detection['complete']).lower()} |"
        ),
        (
            "| Verified recovery outcomes | "
            f"{outcomes['verified_recoveries']}/{outcomes['consequential_actions']} | "
            f"{outcomes['ratio']:.0%} | {str(outcomes['complete']).lower()} |"
        ),
        (
            "| Replay and regression | current bounded replay | "
            f"{'verified' if dimensions['replay_regression_verified'] else 'not verified'} | "
            f"{str(dimensions['replay_regression_verified']).lower()} |"
        ),
        "",
        "Detection coverage is not represented as recovery coverage.",
        "",
        "## Affected authority surfaces",
        "",
    ]
    lines.extend(
        f"- {_markdown_text(surface)}"
        for surface in assessment["tool_authority_map"]["surfaces"]
    )
    lines.extend(
        [
            "",
            "## Controlled incident evidence",
            "",
            (
                "- Consequential actions: "
                f"{assessment['controlled_incident']['expected_actions']}"
            ),
            (
                "- Detected actions: "
                f"{assessment['controlled_incident']['detected_actions']}"
            ),
            (
                "- Blast-radius recall: "
                f"{assessment['controlled_incident']['blast_radius_recall']:.0%}"
            ),
            (
                "- Blast-radius precision: "
                f"{assessment['controlled_incident']['blast_radius_precision']:.0%}"
            ),
            (
                "- Verified recovery outcomes: "
                f"{assessment['recovery']['verified_recoveries']}"
            ),
            (
                "- Unsafe recovery executions during replay: "
                f"{assessment['replay_regression']['unsafe_recovery_executions']}"
            ),
            "",
            "## Restoration decision",
        "",
        (
            "- Bounded downstream restoration verified: "
            f"{str(assessment['decision']['bounded_downstream_restoration_verified']).lower()}"
        ),
        (
            "- Restored downstream authorities: "
            f"{restoration['restored_downstream_authorities']}"
        ),
        (
            "- Compromised root authority restored: "
            f"{str(restoration['root_authority_restored']).lower()}"
        ),
        (
            "- Compromised root authority remains contained: "
            f"{str(assessment['residual_risk']['root_authority_remains_contained']).lower()}"
        ),
        "- Production security effectiveness claim: false",
        "",
        "## Residual risk",
        "",
        ]
    )
    lines.append(f"- Platform residual effects recorded: {residual_effect_count}")

    lines.extend(["", "## Prioritized remediation", ""])
    for item in assessment["prioritized_remediation"]:
        lines.append(
            f"- {item['priority']} {_markdown_text(item['blocker'])}: "
            f"{_markdown_text(item['action'])}"
        )

    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            _markdown_text(assessment["claim_boundary"]),
            "",
            (
                "This document summarizes deterministic owned-sandbox evidence. "
                "It does not authorize any write or claim production security effectiveness."
            ),
            "",
        ]
    )
    return "\n".join(lines)


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
    authority_map = assessment.get("tool_authority_map")
    controlled = assessment.get("controlled_incident")
    containment = assessment.get("containment")
    recovery = assessment.get("recovery")
    replay = assessment.get("replay_regression")
    restoration = assessment.get("restoration")
    residual = assessment.get("residual_risk")
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
    evidence_sections = {
        "tool_authority_map": authority_map,
        "controlled_incident": controlled,
        "containment": containment,
        "recovery": recovery,
        "replay_regression": replay,
        "restoration": restoration,
        "residual_risk": residual,
    }
    for name, section in evidence_sections.items():
        if not isinstance(section, dict):
            raise TypeError(f"assessment {name} must be an object")

    surfaces = authority_map.get("surfaces")
    if (
        not isinstance(surfaces, list)
        or not surfaces
        or any(not isinstance(surface, str) or not surface.strip() for surface in surfaces)
        or len(surfaces) != len(set(surfaces))
    ):
        raise ValueError("assessment authority surfaces must be unique non-empty strings")
    if authority_map.get("consequential_actions") != controlled.get("expected_actions"):
        raise ValueError("assessment authority map must match controlled incident action count")
    if controlled.get("expected_actions") != dimensions["incident_detection"]["consequential_actions"]:
        raise ValueError("controlled incident action count must match coverage evidence")
    if controlled.get("detected_actions") != dimensions["incident_detection"]["detected_actions"]:
        raise ValueError("controlled incident detections must match coverage evidence")
    for metric in ("blast_radius_recall", "blast_radius_precision"):
        value = controlled.get(metric)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not 0 <= value <= 1
        ):
            raise ValueError(f"controlled incident {metric} must be numeric in [0, 1]")
    if (
        recovery.get("verified_recoveries")
        != dimensions["verified_recovery_outcomes"]["verified_recoveries"]
    ):
        raise ValueError("recovery evidence must match verified recovery outcome coverage")
    if replay.get("verified") is not dimensions["replay_regression_verified"]:
        raise ValueError("replay evidence must match replay regression coverage")
    unsafe_executions = replay.get("unsafe_recovery_executions")
    if (
        not isinstance(unsafe_executions, int)
        or isinstance(unsafe_executions, bool)
        or unsafe_executions < 0
    ):
        raise ValueError("unsafe recovery execution count must be a non-negative integer")
    if containment.get("root_agent_remains_contained") is not residual.get(
        "root_authority_remains_contained"
    ):
        raise ValueError("containment evidence must match residual root-authority truth")
    residual_effect_count = residual.get("platform_residual_effects")
    if (
        not isinstance(residual_effect_count, int)
        or isinstance(residual_effect_count, bool)
        or residual_effect_count < 0
    ):
        raise ValueError("platform residual effect count must be a non-negative integer")
    if recovery.get("platform_residual_effects") != residual_effect_count:
        raise ValueError("recovery residuals must match the residual-risk register")
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


def load_evidence(evidence_path: Path) -> dict[str, Any]:
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if not isinstance(evidence, dict):
        raise TypeError("recoverability assessment evidence input must be an object")
    validate_pilot_evidence(evidence)
    return evidence


def reproduce(
    output_path: Path,
    markdown_output_path: Path | None = None,
    evidence: dict[str, Any] | None = None,
    manifest_output_path: Path | None = None,
) -> dict[str, Any]:
    if manifest_output_path is not None and markdown_output_path is None:
        raise ValueError("artifact manifest requires a buyer Markdown output")

    assessment = build_assessment(evidence)
    validate_assessment(assessment)
    assessment_json = json.dumps(assessment, indent=2, sort_keys=True) + "\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(assessment_json, encoding="utf-8")
    reloaded = json.loads(output_path.read_text(encoding="utf-8"))
    validate_assessment(reloaded)

    buyer_markdown = render_assessment(reloaded)
    if markdown_output_path is not None:
        markdown_output_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_output_path.write_text(buyer_markdown, encoding="utf-8")

    if manifest_output_path is not None:
        manifest = build_artifact_manifest(reloaded, assessment_json, buyer_markdown)
        validate_artifact_manifest(manifest, reloaded, assessment_json, buyer_markdown)
        manifest_output_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_output_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        reloaded_manifest = json.loads(manifest_output_path.read_text(encoding="utf-8"))
        validate_artifact_manifest(
            reloaded_manifest,
            reloaded,
            output_path.read_text(encoding="utf-8"),
            markdown_output_path.read_text(encoding="utf-8"),
        )
    return reloaded


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a bounded Agent Recoverability Assessment artifact."
    )
    parser.add_argument("output_path", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument(
        "--manifest-output",
        type=Path,
        help="Optional integrity manifest binding the exact JSON and buyer Markdown artifacts.",
    )
    parser.add_argument(
        "--evidence-input",
        type=Path,
        help="Validated owned-pilot evidence JSON to assess instead of the canonical fixture.",
    )
    args = parser.parse_args()
    evidence = load_evidence(args.evidence_input) if args.evidence_input is not None else None
    print(
        json.dumps(
            reproduce(
                args.output_path,
                args.markdown_output,
                evidence,
                args.manifest_output,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
