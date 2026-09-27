from __future__ import annotations

import hashlib
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
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "manifest_pin_verified": False,
        "source_evidence_identity": assessment["source_evidence_identity"],
        "verified_artifacts": ["assessment_json", "buyer_markdown"],
    }


def test_verifies_package_against_out_of_band_manifest_pin(tmp_path: Path) -> None:
    assessment_path, markdown_path, manifest_path = _package(tmp_path)
    manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    result = verifier.verify_assessment_package(
        assessment_path,
        markdown_path,
        manifest_path,
        manifest_sha256.upper(),
    )

    assert result["manifest_sha256"] == manifest_sha256
    assert result["manifest_pin_verified"] is True


def test_rejects_changed_manifest_against_out_of_band_pin(tmp_path: Path) -> None:
    assessment_path, markdown_path, manifest_path = _package(tmp_path)
    manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"]["buyer_markdown"]["sha256"] = "0" * 64
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="manifest digest mismatch"):
        verifier.verify_assessment_package(
            assessment_path,
            markdown_path,
            manifest_path,
            manifest_sha256,
        )


@pytest.mark.parametrize("expected", ["abc", "z" * 64])
def test_rejects_malformed_manifest_pin(tmp_path: Path, expected: str) -> None:
    assessment_path, markdown_path, manifest_path = _package(tmp_path)

    with pytest.raises(ValueError, match="64 hexadecimal characters"):
        verifier.verify_assessment_package(
            assessment_path,
            markdown_path,
            manifest_path,
            expected,
        )


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
