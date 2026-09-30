from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from agent_recovery.ocsf_promotion import promote_ocsf_evidence_batch
from normalize_ocsf_evidence import verify_artifact, verify_evidence

SCHEMA_VERSION = "agent-recovery-ocsf-recovery-promotions/v1"


def _canonical_digest(payload: Any) -> str:
    try:
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as error:
        raise ValueError("recovery mapping manifest must be deterministic JSON data") from error
    return sha256(canonical.encode("utf-8")).hexdigest()


def _required_sha256(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} must be lowercase SHA-256")
    return value


def _mapping_manifest(payload: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ValueError("recovery mapping manifest must be an object")
    if "recovery_mappings" in payload:
        if set(payload) != {"recovery_mappings"}:
            raise ValueError(
                "wrapped recovery mapping manifest may only contain recovery_mappings"
            )
        mappings = payload["recovery_mappings"]
    else:
        mappings = payload
    if not isinstance(mappings, dict):
        raise ValueError("recovery_mappings must be an object")
    return mappings


def build_promotion_artifact(
    evidence: Any,
    mapping_manifest: Any,
    *,
    source_evidence_artifact_sha256: str,
) -> dict[str, Any]:
    """Bind verified OCSF evidence to explicit recovery identity without authority."""

    verified = verify_evidence(evidence)
    source_digest = _required_sha256(
        source_evidence_artifact_sha256,
        "source_evidence_artifact_sha256",
    )
    mappings = _mapping_manifest(mapping_manifest)
    raw_events = [event["raw_event"] for event in verified["events"]]
    promotions = promote_ocsf_evidence_batch(raw_events, mappings)
    return {
        "schema_version": SCHEMA_VERSION,
        "authorization_effect": "none",
        "source_evidence_schema_version": verified["schema_version"],
        "source_evidence_artifact_sha256": source_digest,
        "recovery_mapping_manifest_sha256": _canonical_digest(mappings),
        "promotion_count": len(promotions),
        "promotions": [promotion.payload() for promotion in promotions],
    }


def reproduce(
    evidence_path: Path,
    mappings_path: Path,
    output_path: Path,
    *,
    expected_evidence_artifact_sha256: str | None = None,
) -> dict[str, Any]:
    evidence_bytes = evidence_path.read_bytes()
    evidence = verify_artifact(
        evidence_path,
        expected_artifact_sha256=expected_evidence_artifact_sha256,
    )
    mapping_manifest = json.loads(mappings_path.read_text(encoding="utf-8"))
    artifact = build_promotion_artifact(
        evidence,
        mapping_manifest,
        source_evidence_artifact_sha256=sha256(evidence_bytes).hexdigest(),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Promote verified OCSF runtime evidence through an exact recovery mapping "
            "manifest without importing runtime-policy authority."
        )
    )
    parser.add_argument("evidence_path", type=Path)
    parser.add_argument("mappings_path", type=Path)
    parser.add_argument("output_path", type=Path)
    parser.add_argument(
        "--expected-evidence-artifact-sha256",
        help=(
            "Fail closed unless evidence_path is the exact independently identified "
            "OCSF evidence artifact."
        ),
    )
    args = parser.parse_args()
    artifact = reproduce(
        args.evidence_path,
        args.mappings_path,
        args.output_path,
        expected_evidence_artifact_sha256=args.expected_evidence_artifact_sha256,
    )
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
