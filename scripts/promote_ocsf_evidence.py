from __future__ import annotations

import argparse
import hmac
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from agent_recovery.ocsf_promotion import promote_ocsf_evidence_batch
from normalize_ocsf_evidence import verify_artifact, verify_evidence

SCHEMA_VERSION = "agent-recovery-ocsf-recovery-promotions/v1"


def _canonical_digest(payload: Any, label: str = "recovery mapping manifest") -> str:
    try:
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be deterministic JSON data") from error
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
    promotion_payloads = json.loads(
        json.dumps(
            [promotion.payload() for promotion in promotions],
            sort_keys=True,
        )
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "authorization_effect": "none",
        "source_evidence_schema_version": verified["schema_version"],
        "source_evidence_artifact_sha256": source_digest,
        "recovery_mapping_manifest_sha256": _canonical_digest(mappings),
        "promotion_count": len(promotions),
        "promotions": promotion_payloads,
    }


def _required_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _verify_observation(
    observation: Any,
    source_event_id: str,
    recovery_mapping: dict[str, Any],
) -> None:
    label = f"promotion[{source_event_id}].observation"
    item = _required_object(observation, label)
    required = {
        "observation_id",
        "tool_id",
        "action_type",
        "contract_version",
        "agent_id",
        "params",
        "source_system",
        "source_event_id",
        "observed_at",
        "resource_keys",
        "provenance_digest",
        "authorization_effect",
    }
    allowed = required | {"trace_id", "span_id", "authority_scope"}
    missing = sorted(required - set(item))
    unexpected = sorted(set(item) - allowed)
    if missing:
        raise ValueError(f"{label} missing fields: {', '.join(missing)}")
    if unexpected:
        raise ValueError(f"{label} unexpected fields: {', '.join(unexpected)}")
    if item["source_system"] != "ocsf":
        raise ValueError(f"{label} source_system must be ocsf")
    if item["source_event_id"] != source_event_id:
        raise ValueError(f"{label} source_event_id mismatch")
    if item["observation_id"] != f"ocsf:{source_event_id}":
        raise ValueError(f"{label} observation_id mismatch")
    if item["authorization_effect"] != "none":
        raise ValueError(f"{label} authorization_effect must be none")

    required_mapping_fields = (
        "incident_id",
        "tool_id",
        "action_type",
        "contract_version",
        "agent_id",
    )
    normalized_text = {
        field: _required_text(
            recovery_mapping.get(field),
            f"{label} recovery_mapping.{field}",
        )
        for field in required_mapping_fields
    }
    if not isinstance(recovery_mapping.get("params"), dict):
        raise ValueError(f"{label} recovery_mapping.params must be an object")
    resource_keys = recovery_mapping.get("resource_keys", [])
    if (
        isinstance(resource_keys, (str, bytes, bytearray))
        or not isinstance(resource_keys, list)
        or any(not isinstance(key, str) or not key.strip() for key in resource_keys)
    ):
        raise ValueError(
            f"{label} recovery_mapping.resource_keys must be unique non-empty strings"
        )
    normalized_resource_keys = [key.strip() for key in resource_keys]
    if len(set(normalized_resource_keys)) != len(normalized_resource_keys):
        raise ValueError(
            f"{label} recovery_mapping.resource_keys must be unique non-empty strings"
        )

    for field in ("tool_id", "action_type", "contract_version", "agent_id"):
        if item[field] != normalized_text[field]:
            raise ValueError(f"{label} {field} does not match recovery_mapping")
    if item["params"] != recovery_mapping["params"]:
        raise ValueError(f"{label} params does not match recovery_mapping")
    if item["resource_keys"] != sorted(normalized_resource_keys):
        raise ValueError(f"{label} resource_keys do not match recovery_mapping")
    for field in ("trace_id", "span_id", "authority_scope"):
        expected = recovery_mapping.get(field)
        if expected is None:
            if field in item:
                raise ValueError(f"{label} unexpected {field}")
        else:
            normalized_expected = _required_text(
                expected,
                f"{label} recovery_mapping.{field}",
            )
            if item.get(field) != normalized_expected:
                raise ValueError(f"{label} {field} does not match recovery_mapping")
    if "observed_at" in recovery_mapping:
        normalized_observed_at = _required_text(
            recovery_mapping["observed_at"],
            f"{label} recovery_mapping.observed_at",
        )
        if item["observed_at"] != normalized_observed_at:
            raise ValueError(f"{label} observed_at does not match recovery_mapping")

    supplied_digest = _required_sha256(
        item["provenance_digest"],
        f"{label} provenance_digest",
    )
    evidence_payload = {
        key: value
        for key, value in item.items()
        if key not in {"provenance_digest", "authorization_effect"}
    }
    expected_digest = _canonical_digest(evidence_payload, f"{label} evidence")
    if not hmac.compare_digest(supplied_digest, expected_digest):
        raise ValueError(f"{label} provenance_digest mismatch")


def _verify_promotion(promotion: Any, index: int) -> tuple[str, dict[str, Any]]:
    label = f"promotion[{index}]"
    item = _required_object(promotion, label)
    expected_fields = {
        "source_system",
        "source_event_id",
        "source_provenance_digest",
        "recovery_mapping_digest",
        "recovery_mapping",
        "observation",
        "authorization_effect",
    }
    if set(item) != expected_fields:
        missing = sorted(expected_fields - set(item))
        unexpected = sorted(set(item) - expected_fields)
        detail = []
        if missing:
            detail.append("missing: " + ", ".join(missing))
        if unexpected:
            detail.append("unexpected: " + ", ".join(unexpected))
        raise ValueError(f"{label} fields mismatch ({'; '.join(detail)})")
    if item["source_system"] != "ocsf":
        raise ValueError(f"{label} source_system must be ocsf")
    if item["authorization_effect"] != "none":
        raise ValueError(f"{label} authorization_effect must be none")

    source_event_id = _required_text(item["source_event_id"], f"{label} source_event_id")
    _required_sha256(
        item["source_provenance_digest"],
        f"{label} source_provenance_digest",
    )
    mapping = _required_object(item["recovery_mapping"], f"{label} recovery_mapping")
    supplied_mapping_digest = _required_sha256(
        item["recovery_mapping_digest"],
        f"{label} recovery_mapping_digest",
    )
    expected_mapping_digest = _canonical_digest(mapping, f"{label} recovery_mapping")
    if not hmac.compare_digest(supplied_mapping_digest, expected_mapping_digest):
        raise ValueError(f"{label} recovery_mapping_digest mismatch")
    _verify_observation(item["observation"], source_event_id, mapping)
    return source_event_id, mapping


def verify_promotion_artifact(artifact: Any) -> dict[str, Any]:
    """Fail closed unless a received OCSF promotion artifact is self-consistent."""

    item = _required_object(artifact, "OCSF promotion artifact")
    expected_fields = {
        "schema_version",
        "authorization_effect",
        "source_evidence_schema_version",
        "source_evidence_artifact_sha256",
        "recovery_mapping_manifest_sha256",
        "promotion_count",
        "promotions",
    }
    if set(item) != expected_fields:
        raise ValueError("OCSF promotion artifact fields mismatch")
    if item["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if item["authorization_effect"] != "none":
        raise ValueError("artifact authorization_effect must be none")
    if item["source_evidence_schema_version"] != "agent-recovery-ocsf-evidence/v1":
        raise ValueError("source_evidence_schema_version mismatch")
    _required_sha256(
        item["source_evidence_artifact_sha256"],
        "source_evidence_artifact_sha256",
    )
    supplied_manifest_digest = _required_sha256(
        item["recovery_mapping_manifest_sha256"],
        "recovery_mapping_manifest_sha256",
    )

    count = item["promotion_count"]
    promotions = item["promotions"]
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("promotion_count must be a non-negative integer")
    if not isinstance(promotions, list):
        raise ValueError("promotions must be an array")
    if count != len(promotions):
        raise ValueError("promotion_count does not match promotions")

    manifest: dict[str, dict[str, Any]] = {}
    for index, promotion in enumerate(promotions):
        source_event_id, mapping = _verify_promotion(promotion, index)
        if source_event_id in manifest:
            raise ValueError(f"duplicate promotion source_event_id: {source_event_id}")
        manifest[source_event_id] = mapping
    expected_manifest_digest = _canonical_digest(manifest)
    if not hmac.compare_digest(supplied_manifest_digest, expected_manifest_digest):
        raise ValueError("recovery_mapping_manifest_sha256 mismatch")
    return item


def verify_promotion_artifact_file(
    path: Path,
    expected_artifact_sha256: str | None = None,
) -> dict[str, Any]:
    artifact_bytes = path.read_bytes()
    if expected_artifact_sha256 is not None:
        expected_digest = expected_artifact_sha256.strip().lower()
        _required_sha256(expected_digest, "expected promotion artifact SHA-256")
        actual_digest = sha256(artifact_bytes).hexdigest()
        if not hmac.compare_digest(actual_digest, expected_digest):
            raise ValueError("OCSF promotion artifact digest mismatch")
    return verify_promotion_artifact(json.loads(artifact_bytes.decode("utf-8")))


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
    parser.add_argument("evidence_path", nargs="?", type=Path)
    parser.add_argument("mappings_path", nargs="?", type=Path)
    parser.add_argument("output_path", nargs="?", type=Path)
    parser.add_argument(
        "--expected-evidence-artifact-sha256",
        help=(
            "Fail closed unless evidence_path is the exact independently identified "
            "OCSF evidence artifact."
        ),
    )
    parser.add_argument(
        "--verify-only",
        type=Path,
        help="Verify one received OCSF promotion artifact without granting authority.",
    )
    parser.add_argument(
        "--expected-promotion-artifact-sha256",
        help=(
            "Fail closed unless --verify-only reads the exact promotion artifact "
            "identified by this independently obtained SHA-256 digest."
        ),
    )
    args = parser.parse_args()
    if args.verify_only is not None:
        if any(
            path is not None
            for path in (args.evidence_path, args.mappings_path, args.output_path)
        ):
            parser.error("--verify-only cannot be combined with positional paths")
        if args.expected_evidence_artifact_sha256 is not None:
            parser.error(
                "--expected-evidence-artifact-sha256 cannot be used with --verify-only"
            )
        artifact = verify_promotion_artifact_file(
            args.verify_only,
            expected_artifact_sha256=args.expected_promotion_artifact_sha256,
        )
    else:
        if args.expected_promotion_artifact_sha256 is not None:
            parser.error(
                "--expected-promotion-artifact-sha256 requires --verify-only"
            )
        if any(
            path is None
            for path in (args.evidence_path, args.mappings_path, args.output_path)
        ):
            parser.error(
                "evidence_path, mappings_path and output_path are required"
            )
        artifact = reproduce(
            args.evidence_path,
            args.mappings_path,
            args.output_path,
            expected_evidence_artifact_sha256=args.expected_evidence_artifact_sha256,
        )
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
