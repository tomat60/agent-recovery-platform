from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from agent_recovery.judge_console import build_judge_advisory_console


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def package_judge_evidence(artifact_path: Path, output_dir: Path) -> dict[str, Any]:
    """Validate and package an existing authority-free judge artifact deterministically."""

    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if not isinstance(artifact, dict):
        raise TypeError("judge artifact root must be an object")

    console = build_judge_advisory_console(artifact)
    artifact_bytes = _canonical_json(artifact)
    console_bytes = _canonical_json(console)

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_output = output_dir / "advisory-judge-artifact.json"
    console_output = output_dir / "judge-advisory-console.json"
    manifest_output = output_dir / "manifest.json"

    artifact_output.write_bytes(artifact_bytes)
    console_output.write_bytes(console_bytes)

    manifest = {
        "schema_version": "judge-evidence-package/v1",
        "authorization_effect": "none",
        "source_artifact": artifact_path.name,
        "files": {
            artifact_output.name: {"sha256": _sha256(artifact_bytes)},
            console_output.name: {"sha256": _sha256(console_bytes)},
        },
    }
    manifest_bytes = _canonical_json(manifest)
    manifest_output.write_bytes(manifest_bytes)
    return manifest
