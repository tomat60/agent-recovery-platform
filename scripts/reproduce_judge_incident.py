from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from agent_recovery.judge_incident_evidence import (
    build_judge_incident_evidence,
    validate_judge_incident_evidence,
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def reproduce(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    incident = build_judge_incident_evidence()
    validate_judge_incident_evidence(incident)
    incident_text = canonical_json(incident)
    incident_path = output_dir / "incident-evidence.json"
    incident_path.write_text(incident_text, encoding="utf-8")

    reloaded = json.loads(incident_path.read_text(encoding="utf-8"))
    validate_judge_incident_evidence(reloaded)
    reloaded_text = canonical_json(reloaded)
    if reloaded_text != incident_text:
        raise ValueError("canonical incident evidence changed after round-trip")

    manifest = {
        "schema_version": "judge-incident-reproduction/v1",
        "authorization_effect": "none",
        "scenario": incident["scenario"],
        "files": {
            incident_path.name: {
                "sha256": sha256_text(incident_text),
                "bytes": len(incident_text.encode("utf-8")),
            }
        },
        "verification": {
            "incident_schema_valid": True,
            "canonical_round_trip": True,
            "authority_free": incident["authorization_effect"] == "none",
        },
        "claim_boundary": (
            "Synthetic deterministic reproduction only; this manifest grants no approval, "
            "execution, compensation, replay, or restoration authority."
        ),
    }
    manifest_text = canonical_json(manifest)
    (output_dir / "manifest.json").write_text(manifest_text, encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce and hash the bounded deterministic judge incident evidence."
    )
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(canonical_json(reproduce(args.output_dir)), end="")


if __name__ == "__main__":
    main()
