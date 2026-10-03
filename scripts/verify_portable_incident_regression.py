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

VERIFICATION_SCHEMA_VERSION = "agent-recovery-portable-regression-verification/v1"
RECEIPT_REPLAY_SCHEMA_VERSION = (
    "agent-recovery-portable-regression-verification-replay/v1"
)


def _artifact_digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def verify_regression_package(
    package_path: Path,
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    raw = package_path.read_bytes()
    artifact_sha256 = _artifact_digest(raw)
    if expected_sha256 is not None:
        normalized = expected_sha256.strip().lower()
        if len(normalized) != 64 or any(
            character not in "0123456789abcdef" for character in normalized
        ):
            raise ValueError("expected package SHA-256 must be 64 hexadecimal characters")
        if not hmac.compare_digest(artifact_sha256, normalized):
            raise ValueError("portable regression package digest mismatch")

    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise TypeError("portable regression package must be a JSON object")
    verified = verify_portable_incident_regression(payload)
    return {
        "ok": True,
        "authorization_effect": "none",
        "verification_schema_version": VERIFICATION_SCHEMA_VERSION,
        "artifact_sha256": artifact_sha256,
        "artifact_pin_verified": expected_sha256 is not None,
        "schema_version": verified.schema_version,
        "regression_id": verified.regression_id,
        "fingerprint": verified.fingerprint,
        "source_incident_id": verified.source_incident_id,
        "restoration_scopes": list(verified.restoration_scopes),
    }


def write_verification_receipt(
    result: dict[str, Any],
    receipt_path: Path,
    package_path: Path,
) -> None:
    if receipt_path.resolve(strict=False) == package_path.resolve(strict=False):
        raise ValueError("verification receipt must not replace the verified package")
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError("refusing to overwrite existing verification receipt")

    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\\n"
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
    package_path: Path,
    expected_package_sha256: str | None = None,
    expected_receipt_sha256: str | None = None,
) -> dict[str, Any]:
    if receipt_path.resolve(strict=False) == package_path.resolve(strict=False):
        raise ValueError("verification receipt must not replace the verified package")
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise FileNotFoundError("verification receipt must be a real file, not a symlink")

    receipt_bytes = receipt_path.read_bytes()
    receipt_sha256 = _artifact_digest(receipt_bytes)
    if expected_receipt_sha256 is not None:
        normalized = expected_receipt_sha256.strip().lower()
        if len(normalized) != 64 or any(
            character not in "0123456789abcdef" for character in normalized
        ):
            raise ValueError("expected receipt SHA-256 must be 64 hexadecimal characters")
        if not hmac.compare_digest(receipt_sha256, normalized):
            raise ValueError("verification receipt digest mismatch")

    current_result = verify_regression_package(
        package_path,
        expected_package_sha256,
    )
    expected_bytes = (
        json.dumps(current_result, indent=2, sort_keys=True) + "\\n"
    ).encode("utf-8")
    if receipt_bytes != expected_bytes:
        raise ValueError(
            "verification receipt does not exactly match the current package"
        )

    return {
        "ok": True,
        "authorization_effect": "none",
        "schema_version": RECEIPT_REPLAY_SCHEMA_VERSION,
        "package_verification": current_result,
        "receipt_sha256": receipt_sha256,
        "receipt_pin_verified": expected_receipt_sha256 is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verify a portable incident regression package without granting "
            "recovery or restoration authority."
        )
    )
    parser.add_argument("package_path", type=Path)
    parser.add_argument(
        "--expected-sha256",
        help=(
            "Optional independently obtained SHA-256 pin for the exact package bytes."
        ),
    )
    receipt_mode = parser.add_mutually_exclusive_group()
    receipt_mode.add_argument(
        "--receipt-output",
        type=Path,
        help="Persist a deterministic, non-authorizing verification receipt.",
    )
    receipt_mode.add_argument(
        "--verify-receipt",
        type=Path,
        help="Replay a retained verification receipt against the current package.",
    )
    parser.add_argument(
        "--expected-receipt-sha256",
        help="Optional independently obtained SHA-256 pin for the receipt bytes.",
    )
    args = parser.parse_args()
    if args.expected_receipt_sha256 is not None and args.verify_receipt is None:
        parser.error("--expected-receipt-sha256 requires --verify-receipt")

    if args.verify_receipt is not None:
        result = verify_verification_receipt(
            args.verify_receipt,
            args.package_path,
            args.expected_sha256,
            args.expected_receipt_sha256,
        )
    else:
        result = verify_regression_package(args.package_path, args.expected_sha256)
        if args.receipt_output is not None:
            write_verification_receipt(
                result,
                args.receipt_output,
                args.package_path,
            )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
