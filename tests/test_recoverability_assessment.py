from __future__ import annotations

import copy
import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT = SCRIPTS / "build_recoverability_assessment.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("build_recoverability_assessment", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_assessment_is_bounded_and_authority_free() -> None:
    assessment = module.build_assessment()
    module.validate_assessment(assessment)
    assert assessment["authorization_effect"] == "none"
    assert assessment["assessment_mode"] == "owned_sandbox_evidence"
    assert assessment["source_evidence_identity"] == {
        "schema_version": "owned-multisurface-pilot/v1",
        "sha256": module.evidence_identity(module.build_pilot_evidence()),
    }
    assert assessment["recoverability_coverage"]["ratio"] == 1.0
    expected_actions = assessment["recoverability_coverage"]["consequential_actions"]
    assert assessment["coverage_dimensions"] == {
        "incident_detection": {
            "detected_actions": expected_actions,
            "consequential_actions": expected_actions,
            "ratio": 1.0,
            "complete": True,
        },
        "verified_recovery_outcomes": {
            "verified_recoveries": expected_actions,
            "consequential_actions": expected_actions,
            "ratio": 1.0,
            "complete": True,
        },
        "replay_regression_verified": True,
    }
    assert assessment["decision"]["bounded_downstream_restoration_verified"] is True
    assert assessment["decision"]["production_security_claim"] is False
    assert assessment["residual_risk"]["root_authority_remains_contained"] is True
    assert assessment["prioritized_remediation"]


def test_assessment_rejects_production_security_claim() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["decision"]["production_security_claim"] = True
    with pytest.raises(ValueError, match="production security"):
        module.validate_assessment(assessment)


def test_assessment_rejects_boolean_coverage_ratio() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["recoverability_coverage"]["ratio"] = True
    with pytest.raises(ValueError, match="coverage ratio"):
        module.validate_assessment(assessment)


def test_remediation_prioritizes_failed_recovery_and_replay() -> None:
    evidence = module.build_pilot_evidence()
    evidence["recovery"]["verified_recoveries"] = evidence["controlled_incident"]["expected_actions"] - 1
    evidence["replay"]["verified"] = False
    plan = module._build_remediation_plan(evidence)
    blockers = [item["blocker"] for item in plan]
    assert blockers[:2] == ["incomplete_verified_recovery", "replay_not_verified"]
    assert all(item["priority"] == "P0" for item in plan[:2])


def test_remediation_keeps_residual_effects_explicit() -> None:
    evidence = module.build_pilot_evidence()
    evidence["recovery"]["platform_residual_effects"] = ["external_notification"]
    plan = module._build_remediation_plan(evidence)
    residual = next(item for item in plan if item["blocker"] == "residual_effects_remain")
    assert residual["priority"] == "P1"
    assert "never represent them as undone" in residual["action"]


def test_assessment_rejects_missing_remediation() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["prioritized_remediation"] = []
    with pytest.raises(ValueError, match="prioritized remediation"):
        module.validate_assessment(assessment)


def test_source_evidence_identity_is_order_independent_and_content_bound() -> None:
    evidence = module.build_pilot_evidence()
    reordered = dict(reversed(list(evidence.items())))
    assert module.evidence_identity(evidence) == module.evidence_identity(reordered)

    changed = copy.deepcopy(evidence)
    changed["claim_boundary"] = f'{changed["claim_boundary"]} Additional bounded note.'
    assert module.evidence_identity(evidence) != module.evidence_identity(changed)


def test_assessment_rejects_malformed_source_evidence_identity() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["source_evidence_identity"]["sha256"] = "not-a-digest"
    with pytest.raises(ValueError, match="source evidence identity"):
        module.validate_assessment(assessment)


def test_assessment_names_detection_and_verified_outcomes_separately() -> None:
    assessment = module.build_assessment()
    dimensions = assessment["coverage_dimensions"]

    assert set(dimensions) == {
        "incident_detection",
        "verified_recovery_outcomes",
        "replay_regression_verified",
    }
    assert "detected_actions" in dimensions["incident_detection"]
    assert "verified_recoveries" in dimensions["verified_recovery_outcomes"]


def test_assessment_rejects_boolean_dimension_ratio() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["coverage_dimensions"]["verified_recovery_outcomes"]["ratio"] = True
    with pytest.raises(ValueError, match="coverage dimension verified_recovery_outcomes"):
        module.validate_assessment(assessment)


@pytest.mark.parametrize(
    ("dimension_name", "field", "value", "message"),
    [
        (
            "incident_detection",
            "ratio",
            0.5,
            "ratio must match its evidence counts",
        ),
        (
            "verified_recovery_outcomes",
            "complete",
            False,
            "complete flag must match its evidence counts",
        ),
        (
            "verified_recovery_outcomes",
            "verified_recoveries",
            -1,
            "counts must be bounded non-negative integers",
        ),
    ],
)
def test_assessment_rejects_internally_inconsistent_coverage_dimension(
    dimension_name: str,
    field: str,
    value: object,
    message: str,
) -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["coverage_dimensions"][dimension_name][field] = value

    with pytest.raises(ValueError, match=message):
        module.validate_assessment(assessment)


def test_assessment_rejects_summary_that_disagrees_with_verified_outcomes() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["recoverability_coverage"]["verified_recoveries"] -= 1

    with pytest.raises(ValueError, match="must match the verified recovery outcome dimension"):
        module.validate_assessment(assessment)


def test_buyer_markdown_separates_detection_from_verified_recovery() -> None:
    assessment = module.build_assessment()
    rendered = module.render_assessment(assessment)
    evidence_sha = assessment["source_evidence_identity"]["sha256"]

    detection = assessment["coverage_dimensions"]["incident_detection"]
    outcomes = assessment["coverage_dimensions"]["verified_recovery_outcomes"]

    assert "# Agent Recoverability Assessment" in rendered
    assert (
        f"| Incident detection | {detection['detected_actions']}/"
        f"{detection['consequential_actions']} | {detection['ratio']:.0%} | "
        f"{str(detection['complete']).lower()} |"
    ) in rendered
    assert (
        f"| Verified recovery outcomes | {outcomes['verified_recoveries']}/"
        f"{outcomes['consequential_actions']} | {outcomes['ratio']:.0%} | "
        f"{str(outcomes['complete']).lower()} |"
    ) in rendered
    assert "Detection coverage is not represented as recovery coverage." in rendered
    assert f"Evidence SHA-256: `{evidence_sha}`" in rendered
    assert "Compromised root authority restored: false" in rendered
    assert "Production security effectiveness claim: false" in rendered
    assert "Authorization effect: none" in rendered


def test_buyer_markdown_escapes_evidence_derived_layout_characters() -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment["prioritized_remediation"][0]["action"] = "first | second\nthird"

    rendered = module.render_assessment(assessment)

    assert "first \\| second third" in rendered
    assert "second\nthird" not in rendered


def test_reproduce_optionally_writes_buyer_markdown(tmp_path: Path) -> None:
    json_path = tmp_path / "assessment.json"
    markdown_path = tmp_path / "assessment.md"

    assessment = module.reproduce(json_path, markdown_path)

    assert json_path.exists()
    assert markdown_path.exists()
    assert assessment["source_evidence_identity"]["sha256"] in markdown_path.read_text(
        encoding="utf-8"
    )



def test_buyer_markdown_exposes_authority_and_controlled_incident_evidence() -> None:
    assessment = module.build_assessment()
    rendered = module.render_assessment(assessment)

    for surface in assessment["tool_authority_map"]["surfaces"]:
        assert f"- {surface}" in rendered
    controlled = assessment["controlled_incident"]
    recovery = assessment["recovery"]
    replay = assessment["replay_regression"]
    assert f"- Consequential actions: {controlled['expected_actions']}" in rendered
    assert f"- Detected actions: {controlled['detected_actions']}" in rendered
    assert f"- Blast-radius recall: {controlled['blast_radius_recall']:.0%}" in rendered
    assert f"- Blast-radius precision: {controlled['blast_radius_precision']:.0%}" in rendered
    assert f"- Verified recovery outcomes: {recovery['verified_recoveries']}" in rendered
    assert (
        "- Unsafe recovery executions during replay: "
        f"{replay['unsafe_recovery_executions']}"
    ) in rendered
    assert (
        "- Platform residual effects recorded: "
        f"{assessment['residual_risk']['platform_residual_effects']}"
    ) in rendered


@pytest.mark.parametrize(
    ("section", "field", "mutate", "message"),
    [
        (
            "tool_authority_map",
            "surfaces",
            lambda value: [*value, value[0]],
            "authority surfaces",
        ),
        (
            "controlled_incident",
            "detected_actions",
            lambda value: value - 1,
            "controlled incident detections",
        ),
        (
            "replay_regression",
            "verified",
            lambda value: not value,
            "replay evidence",
        ),
        (
            "residual_risk",
            "platform_residual_effects",
            lambda value: value + 1,
            "recovery residuals",
        ),
    ],
)
def test_assessment_rejects_source_evidence_contradictions(
    section: str,
    field: str,
    mutate: Callable[[Any], Any],
    message: str,
) -> None:
    assessment = copy.deepcopy(module.build_assessment())
    assessment[section][field] = mutate(assessment[section][field])

    with pytest.raises(ValueError, match=message):
        module.validate_assessment(assessment)



def test_reproduce_assesses_supplied_evidence_file(tmp_path: Path) -> None:
    evidence = module.build_pilot_evidence()
    evidence_path = tmp_path / "owned-pilot-evidence.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    output_path = tmp_path / "assessment.json"

    loaded = module.load_evidence(evidence_path)
    assessment = module.reproduce(output_path, evidence=loaded)

    assert assessment["source_evidence_identity"]["sha256"] == module.evidence_identity(evidence)
    assert assessment["scenario"] == evidence["scenario"]
    assert json.loads(output_path.read_text(encoding="utf-8")) == assessment


def test_evidence_input_rejects_non_object_json(tmp_path: Path) -> None:
    evidence_path = tmp_path / "invalid-evidence.json"
    evidence_path.write_text("[]", encoding="utf-8")

    with pytest.raises(TypeError, match="evidence input must be an object"):
        module.load_evidence(evidence_path)


def test_evidence_input_fails_closed_before_assessment(tmp_path: Path) -> None:
    evidence = module.build_pilot_evidence()
    evidence["controlled_incident"]["detected_actions"] -= 1
    evidence_path = tmp_path / "contradictory-evidence.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    with pytest.raises(ValueError, match="complete blast-radius detection"):
        module.load_evidence(evidence_path)


def test_reproduce_writes_content_bound_artifact_manifest(tmp_path: Path) -> None:
    json_path = tmp_path / "assessment.json"
    markdown_path = tmp_path / "assessment.md"
    manifest_path = tmp_path / "assessment.manifest.json"

    assessment = module.reproduce(
        json_path,
        markdown_path,
        manifest_output_path=manifest_path,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assessment_json = json_path.read_text(encoding="utf-8")
    buyer_markdown = markdown_path.read_text(encoding="utf-8")

    assert manifest["schema_version"] == module.MANIFEST_SCHEMA_VERSION
    assert manifest["authorization_effect"] == "none"
    assert manifest["source_evidence_identity"] == assessment["source_evidence_identity"]
    assert manifest["artifacts"] == {
        "assessment_json": {"sha256": module._artifact_digest(assessment_json)},
        "buyer_markdown": {"sha256": module._artifact_digest(buyer_markdown)},
    }
    module.validate_artifact_manifest(
        manifest,
        assessment,
        assessment_json,
        buyer_markdown,
    )


def test_artifact_manifest_rejects_changed_buyer_report(tmp_path: Path) -> None:
    json_path = tmp_path / "assessment.json"
    markdown_path = tmp_path / "assessment.md"
    manifest_path = tmp_path / "assessment.manifest.json"
    assessment = module.reproduce(
        json_path,
        markdown_path,
        manifest_output_path=manifest_path,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    with pytest.raises(ValueError, match="digest mismatch for buyer_markdown"):
        module.validate_artifact_manifest(
            manifest,
            assessment,
            json_path.read_text(encoding="utf-8"),
            markdown_path.read_text(encoding="utf-8") + "tampered",
        )


def test_artifact_manifest_requires_buyer_markdown(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="requires a buyer Markdown output"):
        module.reproduce(
            tmp_path / "assessment.json",
            manifest_output_path=tmp_path / "assessment.manifest.json",
        )
