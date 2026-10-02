from __future__ import annotations

import argparse
import hashlib
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
RECEIPT_REPLAY_SCHEMA_VERSION = (
    "agent-recovery-ocsf-pilot-delivery-verification-replay/v1"
)
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


def verify_verification_receipt(
    receipt_path: Path,
    delivery_directory: Path,
    expected_manifest_sha256: str | None = None,
    expected_receipt_sha256: str | None = None,
) -> dict[str, Any]:
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

    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise FileNotFoundError(
            "verification receipt must be a real file, not a symlink"
        )

    receipt_bytes = receipt_path.read_bytes()
    receipt_sha256 = hashlib.sha256(receipt_bytes).hexdigest()
    if (
        expected_receipt_sha256 is not None
        and receipt_sha256 != expected_receipt_sha256.lower()
    ):
        raise ValueError("verification receipt digest mismatch")

    current_result = verify_delivery(
        delivery_directory,
        expected_manifest_sha256,
    )
    expected_bytes = (
        json.dumps(current_result, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if receipt_bytes != expected_bytes:
        raise ValueError(
            "verification receipt does not exactly match the current delivery"
        )

    return {
        "authorization_effect": "none",
        "delivery_verification": current_result,
        "ok": True,
        "receipt_pin_verified": expected_receipt_sha256 is not None,
        "receipt_schema_version": current_result["schema_version"],
        "receipt_sha256": receipt_sha256,
        "schema_version": RECEIPT_REPLAY_SCHEMA_VERSION,
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
    receipt_mode = parser.add_mutually_exclusive_group()
    receipt_mode.add_argument(
        "--receipt-output",
        type=Path,
        help=(
            "Optional path outside the delivery directory for a deterministic, "
            "non-authorizing verification receipt. Existing files are never overwritten."
        ),
    )
    receipt_mode.add_argument(
        "--verify-receipt",
        type=Path,
        help=(
            "Replay a retained receiver receipt against the current delivery. "
            "The receipt must remain byte-for-byte canonical and external."
        ),
    )
    parser.add_argument(
        "--expected-receipt-sha256",
        help="Optional out-of-band SHA-256 pin for the exact retained receipt bytes.",
    )
    args = parser.parse_args()
    if (
        args.expected_receipt_sha256 is not None
        and args.verify_receipt is None
    ):
        parser.error("--expected-receipt-sha256 requires --verify-receipt")

    if args.verify_receipt is not None:
        result = verify_verification_receipt(
            args.verify_receipt,
            args.delivery_directory,
            args.expected_manifest_sha256,
            args.expected_receipt_sha256,
        )
    else:
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
