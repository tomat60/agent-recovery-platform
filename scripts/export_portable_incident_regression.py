from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from agent_recovery.regression import verify_portable_incident_regression
from build_recoverability_assessment import validate_assessment


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _validate_digest(value: str, label: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{label} must be 64 hexadecimal characters")
    return normalized


def _publish_without_overwrite(output_path: Path, content: bytes) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output_path}")

    descriptor, temporary_name = tempfile.mkstemp(
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def export_regression_package(
    assessment_path: Path,
    output_path: Path,
    expected_assessment_sha256: str | None = None,
) -> dict[str, Any]:
    assessment_bytes = assessment_path.read_bytes()
    assessment_sha256 = _sha256(assessment_bytes)
    if expected_assessment_sha256 is not None:
        expected = _validate_digest(
            expected_assessment_sha256,
            "expected assessment SHA-256",
        )
        if not hmac.compare_digest(assessment_sha256, expected):
            raise ValueError("recoverability assessment digest mismatch")

    assessment = json.loads(assessment_bytes)
    if not isinstance(assessment, dict):
        raise TypeError("recoverability assessment must be a JSON object")
    validate_assessment(assessment)

    package_payload = assessment.get("incident_regression_package")
    if not isinstance(package_payload, dict):
        raise TypeError("assessment incident regression package must be an object")
    verified = verify_portable_incident_regression(package_payload)
    package_bytes = (
        json.dumps(package_payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    _publish_without_overwrite(output_path, package_bytes)

    return {
        "ok": True,
        "authorization_effect": "none",
        "source_assessment_sha256": assessment_sha256,
        "source_assessment_pin_verified": expected_assessment_sha256 is not None,
        "package_sha256": _sha256(package_bytes),
        "regression_id": verified.regression_id,
        "fingerprint": verified.fingerprint,
        "output_path": str(output_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Export the validated portable incident-regression package embedded "
            "in an Agent Recoverability Assessment."
        )
    )
    parser.add_argument("assessment_path", type=Path)
    parser.add_argument("output_path", type=Path)
    parser.add_argument(
        "--expected-assessment-sha256",
        help="Optional independently obtained SHA-256 pin for the assessment bytes.",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            export_regression_package(
                args.assessment_path,
                args.output_path,
                args.expected_assessment_sha256,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
