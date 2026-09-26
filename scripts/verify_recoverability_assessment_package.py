from __future__ import annotations

import argparse
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
) -> dict[str, Any]:
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
    args = parser.parse_args()

    print(
        json.dumps(
            verify_assessment_package(
                args.assessment_path,
                args.markdown_path,
                args.manifest_path,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
