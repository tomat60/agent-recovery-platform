from __future__ import annotations

import importlib.util
import json
import sys
from hashlib import sha256
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def _load(name: str):
    path = SCRIPT_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


normalize = _load("normalize_ocsf_evidence")
promote = _load("promote_ocsf_evidence")
package = _load("package_ocsf_pilot_handoff")


def _event(uid: str = "openshell-event-42") -> dict[str, object]:
    return {
        "class_uid": 4002,
        "activity_id": 1,
        "time": 1790751000000,
        "metadata": {
            "uid": uid,
            "version": "1.8.0",
            "product": {"name": "OpenShell Sandbox Supervisor"},
        },
        "container": {"uid": "sandbox-7"},
        "action": "Allowed",
        "disposition": "Allowed",
        "dst_endpoint": {"domain": "crm.example.test", "port": 443},
    }


def _mapping() -> dict[str, object]:
    return {
        "incident_id": "inc-1",
        "tool_id": "crm.contacts",
        "action_type": "contact.update",
        "contract_version": "1",
        "agent_id": "support-agent",
        "params": {"contact_id": "c-1", "status": "vip"},
        "authority_scope": "integration:crm",
        "resource_keys": ["crm:contact:c-1"],
    }


def _write_handoff_inputs(tmp_path: Path) -> tuple[Path, Path]:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        json.dumps(normalize.build_evidence([_event()]), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    mapping_path = tmp_path / "mappings.json"
    mapping_path.write_text(
        json.dumps({"recovery_mappings": {"openshell-event-42": _mapping()}}),
        encoding="utf-8",
    )
    promotion_path = tmp_path / "promotions.json"
    promote.reproduce(evidence_path, mapping_path, promotion_path)
    return evidence_path, promotion_path


def test_package_and_verify_exact_handoff_with_manifest_pin(tmp_path: Path) -> None:
    evidence_path, promotion_path = _write_handoff_inputs(tmp_path)
    manifest_path = tmp_path / "handoff.manifest.json"

    manifest = package.package_handoff(
        evidence_path,
        promotion_path,
        manifest_path,
    )
    manifest_digest = sha256(manifest_path.read_bytes()).hexdigest()
    result = package.verify_handoff_package(
        evidence_path,
        promotion_path,
        manifest_path,
        manifest_digest.upper(),
    )

    assert manifest["authorization_effect"] == "none"
    assert manifest["artifacts"]["evidence"]["sha256"] == sha256(
        evidence_path.read_bytes()
    ).hexdigest()
    assert result == {
        "ok": True,
        "authorization_effect": "none",
        "manifest_sha256": manifest_digest,
        "manifest_pin_verified": True,
        "verified_artifacts": ["evidence", "promotions"],
        "source_event_count": 1,
        "promotion_count": 1,
    }


def test_package_rejects_promotion_bound_to_different_evidence(tmp_path: Path) -> None:
    _, promotion_path = _write_handoff_inputs(tmp_path)
    changed_evidence_path = tmp_path / "other-evidence.json"
    changed_evidence_path.write_text(
        json.dumps(normalize.build_evidence([_event("openshell-event-99")])),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="not bound to the supplied evidence"):
        package.package_handoff(
            changed_evidence_path,
            promotion_path,
            tmp_path / "handoff.manifest.json",
        )


def test_receiver_rejects_changed_artifact_bytes(tmp_path: Path) -> None:
    evidence_path, promotion_path = _write_handoff_inputs(tmp_path)
    manifest_path = tmp_path / "handoff.manifest.json"
    package.package_handoff(evidence_path, promotion_path, manifest_path)
    promotion_path.write_text(
        promotion_path.read_text(encoding="utf-8") + " ",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="promotion artifact byte length mismatch"):
        package.verify_handoff_package(
            evidence_path,
            promotion_path,
            manifest_path,
        )


def test_receiver_rejects_manifest_authority_claim(tmp_path: Path) -> None:
    evidence_path, promotion_path = _write_handoff_inputs(tmp_path)
    manifest_path = tmp_path / "handoff.manifest.json"
    manifest = package.package_handoff(evidence_path, promotion_path, manifest_path)
    manifest["authorization_effect"] = "restore"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="authorization_effect must be none"):
        package.verify_handoff_package(
            evidence_path,
            promotion_path,
            manifest_path,
        )
