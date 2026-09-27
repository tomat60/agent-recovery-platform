from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

from build_recoverability_assessment import validate_artifact_manifest


def _load_object(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be a JSON object")
    return value


def verify_assessment_package(
    assessment_path: Path,
    markdown_path: Path,
    manifest_path: Path,
    expected_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if expected_manifest_sha256 is not None:
        normalized_expected = expected_manifest_sha256.strip().lower()
        if len(normalized_expected) != 64 or any(
            character not in "0123456789abcdef" for character in normalized_expected
        ):
            raise ValueError("expected manifest SHA-256 must be 64 hexadecimal characters")
        if not hmac.compare_digest(manifest_sha256, normalized_expected):
            raise ValueError("assessment artifact manifest digest mismatch")

    assessment_json = assessment_path.read_text(encoding="utf-8")
    buyer_markdown = markdown_path.read_text(encoding="utf-8")
    assessment = _load_object(assessment_path, "assessment")
    manifest = _load_object(manifest_path, "assessment artifact manifest")

    validate_artifact_manifest(
        manifest,
        assessment,
        assessment_json,
        buyer_markdown,
    )
    return {
        "ok": True,
        "authorization_effect": "none",
        "manifest_sha256": manifest_sha256,
        "manifest_pin_verified": expected_manifest_sha256 is not None,
        "source_evidence_identity": dict(assessment["source_evidence_identity"]),
        "verified_artifacts": sorted(manifest["artifacts"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verify an Agent Recoverability Assessment JSON, buyer Markdown report, "
            "and integrity manifest without granting authority."
        )
    )
    parser.add_argument("assessment_path", type=Path)
    parser.add_argument("markdown_path", type=Path)
    parser.add_argument("manifest_path", type=Path)
    parser.add_argument(
        "--expected-manifest-sha256",
        help=(
            "Optional out-of-band SHA-256 pin for the exact manifest bytes. "
            "When supplied, verification fails closed if the delivered manifest changed."
        ),
    )
    args = parser.parse_args()

    print(
        json.dumps(
            verify_assessment_package(
                args.assessment_path,
                args.markdown_path,
                args.manifest_path,
                args.expected_manifest_sha256,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
