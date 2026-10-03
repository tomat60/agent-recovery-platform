from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

ASSESSMENT_SCRIPT = SCRIPTS / "build_recoverability_assessment.py"
assessment_spec = importlib.util.spec_from_file_location(
    "build_recoverability_assessment",
    ASSESSMENT_SCRIPT,
)
assert assessment_spec and assessment_spec.loader
assessment_module = importlib.util.module_from_spec(assessment_spec)
assessment_spec.loader.exec_module(assessment_module)

EXPORT_SCRIPT = SCRIPTS / "export_portable_incident_regression.py"
export_spec = importlib.util.spec_from_file_location(
    "export_portable_incident_regression",
    EXPORT_SCRIPT,
)
assert export_spec and export_spec.loader
export_module = importlib.util.module_from_spec(export_spec)
export_spec.loader.exec_module(export_module)


def _write_assessment(tmp_path: Path) -> tuple[Path, bytes, dict[str, object]]:
    assessment = assessment_module.build_assessment()
    raw = (json.dumps(assessment, indent=2, sort_keys=True) + "\n").encode()
    path = tmp_path / "assessment.json"
    path.write_bytes(raw)
    return path, raw, assessment


def test_exports_exact_embedded_package_with_source_pin(tmp_path: Path) -> None:
    assessment_path, assessment_bytes, assessment = _write_assessment(tmp_path)
    output_path = tmp_path / "portable-regression.json"
    assessment_sha = hashlib.sha256(assessment_bytes).hexdigest()

    result = export_module.export_regression_package(
        assessment_path,
        output_path,
        assessment_sha.upper(),
    )

    exported = json.loads(output_path.read_text(encoding="utf-8"))
    assert exported == assessment["incident_regression_package"]
    assert result["authorization_effect"] == "none"
    assert result["source_assessment_sha256"] == assessment_sha
    assert result["source_assessment_pin_verified"] is True
    assert result["package_sha256"] == hashlib.sha256(
        output_path.read_bytes()
    ).hexdigest()
    assert result["regression_id"] == exported["regression_id"]


def test_rejects_wrong_source_pin_before_assessment_validation(tmp_path: Path) -> None:
    assessment_path = tmp_path / "assessment.json"
    assessment_path.write_text('{"malformed": true}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="assessment digest mismatch"):
        export_module.export_regression_package(
            assessment_path,
            tmp_path / "portable-regression.json",
            "0" * 64,
        )


def test_rejects_tampered_embedded_package(tmp_path: Path) -> None:
    assessment_path, _, assessment = _write_assessment(tmp_path)
    assessment["incident_regression_package"]["restoration_scopes"] = [
        "surface:root_authority"
    ]
    assessment_path.write_text(
        json.dumps(assessment, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="package mismatch"):
        export_module.export_regression_package(
            assessment_path,
            tmp_path / "portable-regression.json",
        )


def test_refuses_to_overwrite_existing_export(tmp_path: Path) -> None:
    assessment_path, _, _ = _write_assessment(tmp_path)
    output_path = tmp_path / "portable-regression.json"
    output_path.write_text("retained evidence\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        export_module.export_regression_package(assessment_path, output_path)
    assert output_path.read_text(encoding="utf-8") == "retained evidence\n"
