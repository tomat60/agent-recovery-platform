from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from package_ocsf_pilot_handoff import verify_handoff_package

EVIDENCE_FILENAME = "ocsf-evidence.json"
PROMOTIONS_FILENAME = "ocsf-promotions.json"
MANIFEST_FILENAME = "ocsf-handoff.manifest.json"
EXPECTED_FILENAMES = frozenset(
    {EVIDENCE_FILENAME, PROMOTIONS_FILENAME, MANIFEST_FILENAME}
)


def verify_delivery(
    delivery_directory: Path,
    expected_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    if not delivery_directory.is_dir():
        raise NotADirectoryError("OCSF pilot delivery path must be a directory")

    entries = {entry.name: entry for entry in delivery_directory.iterdir()}
    actual_filenames = set(entries)
    missing = sorted(EXPECTED_FILENAMES - actual_filenames)
    unexpected = sorted(actual_filenames - EXPECTED_FILENAMES)
    non_files = sorted(
        filename
        for filename in EXPECTED_FILENAMES & actual_filenames
        if not entries[filename].is_file() or entries[filename].is_symlink()
    )
    if missing or unexpected or non_files:
        raise ValueError(
            "OCSF pilot delivery files mismatch: "
            f"missing={missing}, unexpected={unexpected}, non_files={non_files}"
        )

    result = verify_handoff_package(
        entries[EVIDENCE_FILENAME],
        entries[PROMOTIONS_FILENAME],
        entries[MANIFEST_FILENAME],
        expected_manifest_sha256,
    )
    return {
        **result,
        "verified_delivery_files": sorted(EXPECTED_FILENAMES),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Independently verify that an OCSF pilot delivery directory contains "
            "exactly the three expected, bound, authority-free artifacts."
        )
    )
    parser.add_argument("delivery_directory", type=Path)
    parser.add_argument(
        "--expected-manifest-sha256",
        help="Optional out-of-band SHA-256 pin for the exact manifest bytes.",
    )
    args = parser.parse_args()
    result = verify_delivery(
        args.delivery_directory,
        args.expected_manifest_sha256,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
