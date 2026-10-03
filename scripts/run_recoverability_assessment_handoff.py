from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from build_recoverability_assessment import load_evidence, reproduce
from export_portable_incident_regression import export_regression_package
from verify_portable_incident_regression import verify_regression_package
from verify_recoverability_assessment_package import verify_assessment_package

ASSESSMENT_FILENAME = "recoverability-assessment.json"
REPORT_FILENAME = "recoverability-assessment.md"
MANIFEST_FILENAME = "recoverability-assessment.manifest.json"
REGRESSION_FILENAME = "portable-incident-regression.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_handoff(
    evidence_path: Path,
    output_directory: Path,
    expected_evidence_sha256: str | None = None,
) -> dict[str, Any]:
    """Build and self-verify one non-authorizing recoverability handoff."""

    if output_directory.exists() or output_directory.is_symlink():
        raise FileExistsError(
            "output directory already exists; refusing to overwrite assessment evidence"
        )
    output_directory.parent.mkdir(parents=True, exist_ok=True)
    evidence = load_evidence(evidence_path, expected_evidence_sha256)

    with tempfile.TemporaryDirectory(
        prefix=".recoverability-handoff-",
        dir=output_directory.parent,
    ) as temporary:
        staging = Path(temporary)
        assessment_path = staging / ASSESSMENT_FILENAME
        report_path = staging / REPORT_FILENAME
        manifest_path = staging / MANIFEST_FILENAME
        regression_path = staging / REGRESSION_FILENAME

        reproduce(
            assessment_path,
            report_path,
            evidence,
            manifest_path,
        )
        manifest_sha256 = _sha256(manifest_path)
        assessment_verification = verify_assessment_package(
            assessment_path,
            report_path,
            manifest_path,
            manifest_sha256,
        )

        assessment_sha256 = _sha256(assessment_path)
        export_result = export_regression_package(
            assessment_path,
            regression_path,
            assessment_sha256,
        )
        regression_verification = verify_regression_package(
            regression_path,
            export_result["package_sha256"],
        )

        output_directory.mkdir()
        try:
            for filename in (
                ASSESSMENT_FILENAME,
                REPORT_FILENAME,
                MANIFEST_FILENAME,
                REGRESSION_FILENAME,
            ):
                shutil.move(str(staging / filename), output_directory / filename)
        except Exception:
            shutil.rmtree(output_directory, ignore_errors=True)
            raise

    return {
        "ok": True,
        "authorization_effect": "none",
        "output_directory": str(output_directory),
        "artifacts": [
            ASSESSMENT_FILENAME,
            REPORT_FILENAME,
            MANIFEST_FILENAME,
            REGRESSION_FILENAME,
        ],
        "assessment_sha256": assessment_sha256,
        "assessment_manifest_sha256": manifest_sha256,
        "portable_regression_sha256": export_result["package_sha256"],
        "source_evidence_identity": assessment_verification[
            "source_evidence_identity"
        ],
        "self_verification": {
            "assessment": assessment_verification,
            "portable_regression": regression_verification,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build and self-verify a complete, non-authorizing Agent "
            "Recoverability Assessment handoff from owned-pilot evidence."
        )
    )
    parser.add_argument("evidence_path", type=Path)
    parser.add_argument("output_directory", type=Path)
    parser.add_argument(
        "--expected-evidence-sha256",
        help=(
            "Optional independently obtained canonical SHA-256 identity for "
            "the owned-pilot evidence."
        ),
    )
    args = parser.parse_args()
    print(
        json.dumps(
            run_handoff(
                args.evidence_path,
                args.output_directory,
                args.expected_evidence_sha256,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
