from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from normalize_ocsf_evidence import reproduce as normalize_ocsf
from package_ocsf_pilot_handoff import (
    package_handoff,
    verify_handoff_package,
)
from promote_ocsf_evidence import reproduce as promote_ocsf

EVIDENCE_FILENAME = "ocsf-evidence.json"
PROMOTIONS_FILENAME = "ocsf-promotions.json"
MANIFEST_FILENAME = "ocsf-handoff.manifest.json"


def run_handoff(
    source_events_path: Path,
    recovery_mappings_path: Path,
    output_directory: Path,
) -> dict[str, Any]:
    """Build and self-verify one authority-free OCSF pilot delivery."""

    if output_directory.exists():
        raise FileExistsError(
            "output directory already exists; refusing to overwrite pilot evidence"
        )
    output_directory.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix=".ocsf-handoff-",
        dir=output_directory.parent,
    ) as temporary:
        staging = Path(temporary)
        evidence_path = staging / EVIDENCE_FILENAME
        promotions_path = staging / PROMOTIONS_FILENAME
        manifest_path = staging / MANIFEST_FILENAME

        evidence = normalize_ocsf(source_events_path, evidence_path)
        evidence_digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        promotions = promote_ocsf(
            evidence_path,
            recovery_mappings_path,
            promotions_path,
            expected_evidence_artifact_sha256=evidence_digest,
        )
        package_handoff(evidence_path, promotions_path, manifest_path)
        manifest_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        verification = verify_handoff_package(
            evidence_path,
            promotions_path,
            manifest_path,
            manifest_digest,
        )

        output_directory.mkdir()
        for filename in (
            EVIDENCE_FILENAME,
            PROMOTIONS_FILENAME,
            MANIFEST_FILENAME,
        ):
            shutil.move(str(staging / filename), output_directory / filename)

    return {
        "ok": True,
        "authorization_effect": "none",
        "output_directory": str(output_directory),
        "artifacts": [
            EVIDENCE_FILENAME,
            PROMOTIONS_FILENAME,
            MANIFEST_FILENAME,
        ],
        "evidence_artifact_sha256": evidence_digest,
        "manifest_sha256": manifest_digest,
        "source_event_count": evidence["event_count"],
        "promotion_count": promotions["promotion_count"],
        "self_verification": verification,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build and self-verify one deterministic, non-authorizing OCSF pilot "
            "handoff from raw events and exact recovery mappings."
        )
    )
    parser.add_argument("source_events_path", type=Path)
    parser.add_argument("recovery_mappings_path", type=Path)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            run_handoff(
                args.source_events_path,
                args.recovery_mappings_path,
                args.output_directory,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
