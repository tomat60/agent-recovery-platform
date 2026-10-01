from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from package_ocsf_pilot_handoff import verify_handoff_package

EVIDENCE_FILENAME = "ocsf-evidence.json"
PROMOTIONS_FILENAME = "ocsf-promotions.json"
MANIFEST_FILENAME = "ocsf-handoff.manifest.json"
VERIFICATION_SCHEMA_VERSION = "agent-recovery-ocsf-pilot-delivery-verification/v1"
EXPECTED_FILENAMES = frozenset(
    {EVIDENCE_FILENAME, PROMOTIONS_FILENAME, MANIFEST_FILENAME}
)


def verify_delivery(
    delivery_directory: Path,
    expected_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    if delivery_directory.is_symlink() or not delivery_directory.is_dir():
        raise NotADirectoryError(
            "OCSF pilot delivery path must be a real directory, not a symlink"
        )

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
        "schema_version": VERIFICATION_SCHEMA_VERSION,
        "verified_delivery_files": sorted(EXPECTED_FILENAMES),
    }


def write_verification_receipt(
    result: dict[str, Any],
    receipt_path: Path,
    delivery_directory: Path,
) -> None:
    delivery_root = delivery_directory.resolve()
    resolved_receipt = receipt_path.resolve(strict=False)
    try:
        resolved_receipt.relative_to(delivery_root)
    except ValueError:
        pass
    else:
        raise ValueError(
            "verification receipt must be stored outside the verified delivery directory"
        )

    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError("refusing to overwrite existing verification receipt")

    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=receipt_path.parent,
            prefix=f".{receipt_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.link(temporary_path, receipt_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


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
    parser.add_argument(
        "--receipt-output",
        type=Path,
        help=(
            "Optional path outside the delivery directory for a deterministic, "
            "non-authorizing verification receipt. Existing files are never overwritten."
        ),
    )
    args = parser.parse_args()
    result = verify_delivery(
        args.delivery_directory,
        args.expected_manifest_sha256,
    )
    if args.receipt_output is not None:
        write_verification_receipt(
            result,
            args.receipt_output,
            args.delivery_directory,
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
