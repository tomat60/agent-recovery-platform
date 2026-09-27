from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from agent_recovery.otel_adapter import normalize_otlp_json_trace_export

SCHEMA_VERSION = "agent-recovery-otlp-evidence/v1"
_REQUIRED_OBSERVATION_TEXT = (
    "observation_id",
    "tool_id",
    "action_type",
    "contract_version",
    "agent_id",
    "source_event_id",
    "observed_at",
    "trace_id",
    "span_id",
)


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize an OTLP trace export into deterministic, non-authorizing evidence."""

    observations = normalize_otlp_json_trace_export(payload)
    evidence_payloads = []
    for observation in observations:
        evidence_payload = observation.payload()
        evidence_payload["resource_keys"] = list(evidence_payload["resource_keys"])
        evidence_payloads.append(evidence_payload)
    return {
        "schema_version": SCHEMA_VERSION,
        "authorization_effect": "none",
        "observation_count": len(observations),
        "observations": evidence_payloads,
    }


def _required_text(payload: dict[str, Any], key: str, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} {key} must be a non-empty string")
    return value


def _verify_observation(observation: Any, index: int) -> str:
    label = f"observation[{index}]"
    if not isinstance(observation, dict):
        raise ValueError(f"{label} must be an object")
    for key in _REQUIRED_OBSERVATION_TEXT:
        _required_text(observation, key, label)
    if observation.get("source_system") != "otel":
        raise ValueError(f"{label} source_system must be otel")
    if observation.get("authorization_effect") != "none":
        raise ValueError(f"{label} authorization_effect must be none")
    params = observation.get("params")
    if not isinstance(params, dict):
        raise ValueError(f"{label} params must be an object")
    resource_keys = observation.get("resource_keys")
    if not isinstance(resource_keys, list):
        raise ValueError(f"{label} resource_keys must be an array")
    normalized_keys = []
    for key in resource_keys:
        if not isinstance(key, str) or not key.strip():
            raise ValueError(f"{label} resource_keys must contain non-empty strings")
        normalized_keys.append(key.strip())
    if len(set(normalized_keys)) != len(normalized_keys):
        raise ValueError(f"{label} resource_keys must be unique")

    trace_id = observation["trace_id"]
    span_id = observation["span_id"]
    expected_id = f"otel:{trace_id}:{span_id}"
    if observation["observation_id"] != expected_id:
        raise ValueError(f"{label} observation_id does not match trace/span identity")
    if observation["source_event_id"] != span_id:
        raise ValueError(f"{label} source_event_id does not match span_id")

    supplied_digest = _required_text(observation, "provenance_digest", label)
    if len(supplied_digest) != 64 or any(
        character not in "0123456789abcdef" for character in supplied_digest
    ):
        raise ValueError(f"{label} provenance_digest must be lowercase SHA-256")
    evidence_payload = {
        key: value
        for key, value in observation.items()
        if key not in {"provenance_digest", "authorization_effect"}
    }
    canonical = json.dumps(
        evidence_payload, sort_keys=True, separators=(",", ":"), default=str
    )
    expected_digest = sha256(canonical.encode("utf-8")).hexdigest()
    if supplied_digest != expected_digest:
        raise ValueError(f"{label} provenance_digest mismatch")
    return observation["observation_id"]


def verify_evidence(evidence: Any) -> dict[str, Any]:
    """Fail closed unless an exported OTLP evidence artifact is internally consistent."""

    if not isinstance(evidence, dict):
        raise ValueError("OTLP evidence artifact must be an object")
    if evidence.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if evidence.get("authorization_effect") != "none":
        raise ValueError("artifact authorization_effect must be none")
    count = evidence.get("observation_count")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("observation_count must be a non-negative integer")
    observations = evidence.get("observations")
    if not isinstance(observations, list):
        raise ValueError("observations must be an array")
    if count != len(observations):
        raise ValueError("observation_count does not match observations")

    observation_ids = [_verify_observation(item, index) for index, item in enumerate(observations)]
    if len(set(observation_ids)) != len(observation_ids):
        raise ValueError("observation_id values must be unique")
    return evidence


def verify_artifact(path: Path) -> dict[str, Any]:
    return verify_evidence(json.loads(path.read_text(encoding="utf-8")))


def reproduce(input_path: Path, output_path: Path) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("OTLP trace export input must be an object")
    evidence = verify_evidence(build_evidence(payload))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize or verify non-authorizing OTLP recovery evidence."
    )
    parser.add_argument("input_path", nargs="?", type=Path)
    parser.add_argument("output_path", nargs="?", type=Path)
    parser.add_argument(
        "--verify-only",
        type=Path,
        help="Verify one previously generated evidence artifact without granting authority.",
    )
    args = parser.parse_args()
    if args.verify_only is not None:
        if args.input_path is not None or args.output_path is not None:
            parser.error("--verify-only cannot be combined with input or output paths")
        evidence = verify_artifact(args.verify_only)
    else:
        if args.input_path is None or args.output_path is None:
            parser.error("input_path and output_path are required unless --verify-only is used")
        evidence = reproduce(args.input_path, args.output_path)
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
