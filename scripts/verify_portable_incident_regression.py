from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

from agent_recovery.regression import verify_portable_incident_regression


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
        "artifact_sha256": artifact_sha256,
        "artifact_pin_verified": expected_sha256 is not None,
        "schema_version": verified.schema_version,
        "regression_id": verified.regression_id,
        "fingerprint": verified.fingerprint,
        "source_incident_id": verified.source_incident_id,
        "restoration_scopes": list(verified.restoration_scopes),
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
    args = parser.parse_args()
    print(
        json.dumps(
            verify_regression_package(args.package_path, args.expected_sha256),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
