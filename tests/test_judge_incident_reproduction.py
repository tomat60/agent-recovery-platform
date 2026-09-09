from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "reproduce_judge_incident.py"
SPEC = importlib.util.spec_from_file_location("reproduce_judge_incident", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_reproduction_writes_valid_authority_free_hashed_evidence(tmp_path: Path) -> None:
    manifest = MODULE.reproduce(tmp_path)

    incident_path = tmp_path / "incident-evidence.json"
    manifest_path = tmp_path / "manifest.json"
    assert incident_path.exists()
    assert manifest_path.exists()

    incident = json.loads(incident_path.read_text(encoding="utf-8"))
    stored_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest == stored_manifest
    assert incident["authorization_effect"] == "none"
    assert manifest["authorization_effect"] == "none"
    assert manifest["verification"] == {
        "authority_free": True,
        "canonical_round_trip": True,
        "incident_schema_valid": True,
    }
    assert manifest["files"]["incident-evidence.json"]["sha256"] == MODULE.sha256_text(
        incident_path.read_text(encoding="utf-8")
    )


def test_reproduction_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    MODULE.reproduce(first)
    MODULE.reproduce(second)

    assert (first / "incident-evidence.json").read_bytes() == (
        second / "incident-evidence.json"
    ).read_bytes()
    assert (first / "manifest.json").read_bytes() == (second / "manifest.json").read_bytes()
