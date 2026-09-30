from __future__ import annotations

import argparse
import hmac
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from agent_recovery.ingestion import IngestionError
from agent_recovery.ocsf_adapter import (
    normalize_ocsf_evidence_event,
    normalize_ocsf_json_events,
)

SCHEMA_VERSION = "agent-recovery-ocsf-evidence/v1"


def _source_events(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        events = payload.get("events")
        if isinstance(events, list):
            return events
    raise TypeError("OCSF evidence input must be an array or an object with an events array")


def build_evidence(payload: Any) -> dict[str, Any]:
    """Normalize OCSF events into deterministic evidence with zero authority effect."""

    envelopes = normalize_ocsf_json_events(_source_events(payload))
    events = []
    for envelope in envelopes:
        item = envelope.evidence_payload()
        item["provenance_digest"] = envelope.provenance_digest()
        events.append(item)
    return {
        "schema_version": SCHEMA_VERSION,
        "authorization_effect": "none",
        "event_count": len(events),
        "events": events,
    }


def _required_text(payload: dict[str, Any], key: str, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} {key} must be a non-empty string")
    return value


def _verify_event(event: Any, index: int) -> str:
    label = f"event[{index}]"
    if not isinstance(event, dict):
        raise ValueError(f"{label} must be an object")
    if event.get("source_system") != "ocsf":
        raise ValueError(f"{label} source_system must be ocsf")
    if event.get("authorization_effect") != "none":
        raise ValueError(f"{label} authorization_effect must be none")

    source_event_id = _required_text(event, "source_event_id", label)
    supplied_digest = _required_text(event, "provenance_digest", label)
    if len(supplied_digest) != 64 or any(
        character not in "0123456789abcdef" for character in supplied_digest
    ):
        raise ValueError(f"{label} provenance_digest must be lowercase SHA-256")

    raw_event = event.get("raw_event")
    if not isinstance(raw_event, dict):
        raise ValueError(f"{label} raw_event must be an object")
    try:
        envelope = normalize_ocsf_evidence_event(raw_event)
    except IngestionError as error:
        raise ValueError(f"{label} raw_event is invalid: {error}") from error

    expected_payload = envelope.evidence_payload()
    supplied_payload = {
        key: value for key, value in event.items() if key != "provenance_digest"
    }
    if supplied_payload != expected_payload:
        raise ValueError(f"{label} normalized payload does not match raw_event")
    if source_event_id != envelope.event_uid:
        raise ValueError(f"{label} source_event_id does not match raw_event identity")
    if not hmac.compare_digest(supplied_digest, envelope.provenance_digest()):
        raise ValueError(f"{label} provenance_digest mismatch")
    return source_event_id


def verify_evidence(evidence: Any) -> dict[str, Any]:
    """Fail closed unless an exported OCSF evidence artifact is internally consistent."""

    if not isinstance(evidence, dict):
        raise ValueError("OCSF evidence artifact must be an object")
    if evidence.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if evidence.get("authorization_effect") != "none":
        raise ValueError("artifact authorization_effect must be none")

    count = evidence.get("event_count")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("event_count must be a non-negative integer")
    events = evidence.get("events")
    if not isinstance(events, list):
        raise ValueError("events must be an array")
    if count != len(events):
        raise ValueError("event_count does not match events")

    source_event_ids = [
        _verify_event(event, index) for index, event in enumerate(events)
    ]
    if len(set(source_event_ids)) != len(source_event_ids):
        raise ValueError("source_event_id values must be unique")
    return evidence


def verify_artifact(
    path: Path, expected_artifact_sha256: str | None = None
) -> dict[str, Any]:
    artifact_bytes = path.read_bytes()
    if expected_artifact_sha256 is not None:
        expected_digest = expected_artifact_sha256.strip().lower()
        if len(expected_digest) != 64 or any(
            character not in "0123456789abcdef" for character in expected_digest
        ):
            raise ValueError(
                "expected OCSF evidence artifact SHA-256 must be 64 hexadecimal characters"
            )
        artifact_digest = sha256(artifact_bytes).hexdigest()
        if not hmac.compare_digest(artifact_digest, expected_digest):
            raise ValueError("OCSF evidence artifact digest mismatch")
    return verify_evidence(json.loads(artifact_bytes.decode("utf-8")))


def reproduce(input_path: Path, output_path: Path) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    evidence = verify_evidence(build_evidence(payload))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize or verify non-authorizing OCSF runtime evidence."
    )
    parser.add_argument("input_path", nargs="?", type=Path)
    parser.add_argument("output_path", nargs="?", type=Path)
    parser.add_argument(
        "--verify-only",
        type=Path,
        help="Verify one previously generated evidence artifact without granting authority.",
    )
    parser.add_argument(
        "--expected-artifact-sha256",
        help=(
            "Fail closed unless --verify-only reads the exact artifact identified by "
            "this independently obtained SHA-256 digest."
        ),
    )
    args = parser.parse_args()
    if args.verify_only is not None:
        if args.input_path is not None or args.output_path is not None:
            parser.error("--verify-only cannot be combined with input or output paths")
        evidence = verify_artifact(
            args.verify_only,
            expected_artifact_sha256=args.expected_artifact_sha256,
        )
    else:
        if args.expected_artifact_sha256 is not None:
            parser.error("--expected-artifact-sha256 requires --verify-only")
        if args.input_path is None or args.output_path is None:
            parser.error("input_path and output_path are required unless --verify-only is used")
        evidence = reproduce(args.input_path, args.output_path)
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
