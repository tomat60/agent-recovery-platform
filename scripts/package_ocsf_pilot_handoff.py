from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

from normalize_ocsf_evidence import verify_artifact as verify_evidence_artifact
from promote_ocsf_evidence import verify_promotion_artifact_file

SCHEMA_VERSION = "agent-recovery-ocsf-pilot-handoff/v1"


def _file_identity(path: Path, schema_version: str) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "filename": path.name,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "schema_version": schema_version,
    }


def _load_object(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _required_sha256(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} must be lowercase SHA-256")
    return value


def build_manifest(
    evidence_path: Path,
    promotion_path: Path,
) -> dict[str, Any]:
    evidence = verify_evidence_artifact(evidence_path)
    promotions = verify_promotion_artifact_file(promotion_path)
    evidence_identity = _file_identity(evidence_path, evidence["schema_version"])
    promotion_identity = _file_identity(promotion_path, promotions["schema_version"])
    if promotions["source_evidence_artifact_sha256"] != evidence_identity["sha256"]:
        raise ValueError("promotion artifact is not bound to the supplied evidence artifact")
    return {
        "schema_version": SCHEMA_VERSION,
        "authorization_effect": "none",
        "artifacts": {
            "evidence": evidence_identity,
            "promotions": promotion_identity,
        },
        "binding": {
            "promotion_source_evidence_artifact_sha256": evidence_identity["sha256"],
        },
    }


def package_handoff(
    evidence_path: Path,
    promotion_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    manifest = build_manifest(evidence_path, promotion_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def _verify_file_identity(
    identity: Any,
    path: Path,
    expected_schema_version: str,
    label: str,
) -> None:
    if not isinstance(identity, dict):
        raise ValueError(f"{label} identity must be an object")
    if set(identity) != {"filename", "bytes", "sha256", "schema_version"}:
        raise ValueError(f"{label} identity fields mismatch")
    if identity["filename"] != path.name:
        raise ValueError(f"{label} filename mismatch")
    if identity["schema_version"] != expected_schema_version:
        raise ValueError(f"{label} schema_version mismatch")
    supplied_digest = _required_sha256(identity["sha256"], f"{label} sha256")
    payload = path.read_bytes()
    if (
        isinstance(identity["bytes"], bool)
        or not isinstance(identity["bytes"], int)
        or identity["bytes"] != len(payload)
    ):
        raise ValueError(f"{label} byte length mismatch")
    if not hmac.compare_digest(supplied_digest, hashlib.sha256(payload).hexdigest()):
        raise ValueError(f"{label} digest mismatch")


def verify_handoff_package(
    evidence_path: Path,
    promotion_path: Path,
    manifest_path: Path,
    expected_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    manifest_bytes = manifest_path.read_bytes()
    manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()
    if expected_manifest_sha256 is not None:
        expected_digest = _required_sha256(
            expected_manifest_sha256.strip().lower(),
            "expected manifest SHA-256",
        )
        if not hmac.compare_digest(manifest_digest, expected_digest):
            raise ValueError("OCSF pilot handoff manifest digest mismatch")

    manifest = _load_object(manifest_path, "OCSF pilot handoff manifest")
    if set(manifest) != {
        "schema_version",
        "authorization_effect",
        "artifacts",
        "binding",
    }:
        raise ValueError("OCSF pilot handoff manifest fields mismatch")
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if manifest["authorization_effect"] != "none":
        raise ValueError("manifest authorization_effect must be none")
    if not isinstance(manifest["artifacts"], dict) or set(manifest["artifacts"]) != {
        "evidence",
        "promotions",
    }:
        raise ValueError("manifest artifacts must contain evidence and promotions")

    evidence = verify_evidence_artifact(evidence_path)
    promotions = verify_promotion_artifact_file(promotion_path)
    _verify_file_identity(
        manifest["artifacts"]["evidence"],
        evidence_path,
        evidence["schema_version"],
        "evidence artifact",
    )
    _verify_file_identity(
        manifest["artifacts"]["promotions"],
        promotion_path,
        promotions["schema_version"],
        "promotion artifact",
    )

    binding = manifest["binding"]
    if not isinstance(binding, dict) or set(binding) != {
        "promotion_source_evidence_artifact_sha256"
    }:
        raise ValueError("manifest binding fields mismatch")
    evidence_digest = manifest["artifacts"]["evidence"]["sha256"]
    bound_digest = _required_sha256(
        binding["promotion_source_evidence_artifact_sha256"],
        "promotion source evidence digest",
    )
    if not hmac.compare_digest(bound_digest, evidence_digest):
        raise ValueError("manifest evidence binding mismatch")
    if not hmac.compare_digest(
        promotions["source_evidence_artifact_sha256"],
        evidence_digest,
    ):
        raise ValueError("promotion artifact is not bound to the supplied evidence artifact")

    return {
        "ok": True,
        "authorization_effect": "none",
        "manifest_sha256": manifest_digest,
        "manifest_pin_verified": expected_manifest_sha256 is not None,
        "verified_artifacts": ["evidence", "promotions"],
        "source_event_count": evidence["event_count"],
        "promotion_count": promotions["promotion_count"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Package or independently verify an authority-free OCSF pilot handoff "
            "containing exact evidence and promotion artifacts."
        )
    )
    parser.add_argument("evidence_path", type=Path)
    parser.add_argument("promotion_path", type=Path)
    parser.add_argument("manifest_path", type=Path)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify the delivered evidence, promotions and manifest without rewriting them.",
    )
    parser.add_argument(
        "--expected-manifest-sha256",
        help="Optional out-of-band SHA-256 pin for the exact manifest bytes.",
    )
    args = parser.parse_args()
    if args.verify_only:
        result = verify_handoff_package(
            args.evidence_path,
            args.promotion_path,
            args.manifest_path,
            args.expected_manifest_sha256,
        )
    else:
        if args.expected_manifest_sha256 is not None:
            parser.error("--expected-manifest-sha256 requires --verify-only")
        result = package_handoff(
            args.evidence_path,
            args.promotion_path,
            args.manifest_path,
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
