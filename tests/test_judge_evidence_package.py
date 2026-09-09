from __future__ import annotations

import hashlib
import json
from pathlib import Path

from agent_recovery.judge_evidence_package import package_judge_evidence


def _artifact() -> dict[str, object]:
    return {
        "schema_version": "advisory-judge-artifact/v1",
        "evidence_scope": "synthetic deterministic advisory benchmark evidence only",
        "authorization_effect": "none",
        "scenario_count": 1,
        "aggregate": {"advisory": {}, "gate_safety": {}},
        "scenarios": [
            {
                "scenario_id": "B01",
                "scenario_class": "indirect_prompt_injection",
                "incident_id": "inc-b01",
                "measurement": {"gate_accepted": False},
                "gate_safety": {"observed_acceptance": False},
            }
        ],
    }


def test_packages_authority_free_evidence_with_reproducible_hashes(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(json.dumps(_artifact()), encoding="utf-8")
    output = tmp_path / "package"

    manifest = package_judge_evidence(source, output)

    artifact_payload = (output / "advisory-judge-artifact.json").read_bytes()
    console_payload = (output / "judge-advisory-console.json").read_bytes()
    stored_manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))

    assert manifest == stored_manifest
    assert stored_manifest["authorization_effect"] == "none"
    assert stored_manifest["files"]["advisory-judge-artifact.json"]["sha256"] == hashlib.sha256(
        artifact_payload
    ).hexdigest()
    assert stored_manifest["files"]["judge-advisory-console.json"]["sha256"] == hashlib.sha256(
        console_payload
    ).hexdigest()


def test_rejects_artifact_that_claims_authority(tmp_path: Path) -> None:
    artifact = _artifact()
    artifact["authorization_effect"] = "execute"
    source = tmp_path / "source.json"
    source.write_text(json.dumps(artifact), encoding="utf-8")

    try:
        package_judge_evidence(source, tmp_path / "package")
    except ValueError as exc:
        assert "authority-free artifact" in str(exc)
    else:
        raise AssertionError("judge evidence package must reject authority-bearing artifacts")
