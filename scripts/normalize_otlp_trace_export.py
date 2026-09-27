from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agent_recovery.otel_adapter import normalize_otlp_json_trace_export

SCHEMA_VERSION = "agent-recovery-otlp-evidence/v1"


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


def reproduce(input_path: Path, output_path: Path) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("OTLP trace export input must be an object")
    evidence = build_evidence(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize an OTLP/HTTP JSON trace export into recovery evidence."
    )
    parser.add_argument("input_path", type=Path)
    parser.add_argument("output_path", type=Path)
    args = parser.parse_args()
    print(json.dumps(reproduce(args.input_path, args.output_path), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
