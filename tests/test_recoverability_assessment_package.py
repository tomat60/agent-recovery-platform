from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

builder = importlib.import_module("build_recoverability_assessment")
verifier = importlib.import_module("verify_recoverability_assessment_package")


def _package(tmp_path: Path) -> tuple[Path, Path, Path]:
    assessment_path = tmp_path / "assessment.json"
    markdown_path = tmp_path / "assessment.md"
    manifest_path = tmp_path / "assessment.manifest.json"
    builder.reproduce(
        assessment_path,
        markdown_path,
        manifest_output_path=manifest_path,
    )
    return assessment_path, markdown_path, manifest_path


def test_verifies_delivered_assessment_package(tmp_path: Path) -> None:
    assessment_path, markdown_path, manifest_path = _package(tmp_path)

    result = verifier.verify_assessment_package(
        assessment_path,
        markdown_path,
        manifest_path,
    )

    assessment = json.loads(assessment_path.read_text(encoding="utf-8"))
    assert result == {
        "ok": True,
        "authorization_effect": "none",
        "source_evidence_identity": assessment["source_evidence_identity"],
        "verified_artifacts": ["assessment_json", "buyer_markdown"],
    }


@pytest.mark.parametrize("artifact", ["assessment_json", "buyer_markdown"])
def test_rejects_changed_delivered_artifact(tmp_path: Path, artifact: str) -> None:
    assessment_path, markdown_path, manifest_path = _package(tmp_path)
    if artifact == "assessment_json":
        assessment = json.loads(assessment_path.read_text(encoding="utf-8"))
        assessment["scenario"] = f"{assessment['scenario']} tampered"
        assessment_path.write_text(
            json.dumps(assessment, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        markdown_path.write_text(
            markdown_path.read_text(encoding="utf-8") + "tampered",
            encoding="utf-8",
        )

    with pytest.raises(ValueError, match=f"digest mismatch for {artifact}"):
        verifier.verify_assessment_package(
            assessment_path,
            markdown_path,
            manifest_path,
        )


def test_rejects_non_object_manifest(tmp_path: Path) -> None:
    assessment_path, markdown_path, manifest_path = _package(tmp_path)
    manifest_path.write_text("[]", encoding="utf-8")

    with pytest.raises(TypeError, match="assessment artifact manifest must be a JSON object"):
        verifier.verify_assessment_package(
            assessment_path,
            markdown_path,
            manifest_path,
        )
