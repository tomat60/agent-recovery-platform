from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from agent_recovery.ingestion import IngestionError

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SCRIPT = SCRIPT_DIR / "promote_ocsf_evidence.py"
spec = importlib.util.spec_from_file_location("promote_ocsf_evidence", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

NORMALIZE_SCRIPT = SCRIPT_DIR / "normalize_ocsf_evidence.py"
normalize_spec = importlib.util.spec_from_file_location(
    "normalize_ocsf_evidence_fixture",
    NORMALIZE_SCRIPT,
)
assert normalize_spec and normalize_spec.loader
normalize = importlib.util.module_from_spec(normalize_spec)
normalize_spec.loader.exec_module(normalize)


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


def _mapping(contact_id: str = "c-1") -> dict[str, object]:
    return {
        "incident_id": "inc-1",
        "tool_id": "crm.contacts",
        "action_type": "contact.update",
        "contract_version": "1",
        "agent_id": "support-agent",
        "params": {"contact_id": contact_id, "status": "vip"},
        "authority_scope": "integration:crm",
        "resource_keys": [f"crm:contact:{contact_id}"],
    }


def _write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        json.dumps(normalize.build_evidence([_event()]), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    mappings_path = tmp_path / "mappings.json"
    mappings_path.write_text(
        json.dumps({"recovery_mappings": {"openshell-event-42": _mapping()}}),
        encoding="utf-8",
    )
    return evidence_path, mappings_path


def test_reproduce_binds_exact_evidence_and_mapping_manifest(tmp_path: Path) -> None:
    evidence_path, mappings_path = _write_inputs(tmp_path)
    output_path = tmp_path / "promotions.json"
    evidence_digest = sha256(evidence_path.read_bytes()).hexdigest()

    artifact = module.reproduce(
        evidence_path,
        mappings_path,
        output_path,
        expected_evidence_artifact_sha256=evidence_digest,
    )

    assert json.loads(output_path.read_text(encoding="utf-8")) == artifact
    assert artifact["schema_version"] == (
        "agent-recovery-ocsf-recovery-promotions/v1"
    )
    assert artifact["authorization_effect"] == "none"
    assert artifact["source_evidence_artifact_sha256"] == evidence_digest
    assert len(artifact["recovery_mapping_manifest_sha256"]) == 64
    assert artifact["promotion_count"] == 1
    promotion = artifact["promotions"][0]
    assert promotion["source_event_id"] == "openshell-event-42"
    assert promotion["authorization_effect"] == "none"
    assert promotion["observation"]["authorization_effect"] == "none"


def test_reproduce_rejects_changed_evidence_against_trusted_digest(
    tmp_path: Path,
) -> None:
    evidence_path, mappings_path = _write_inputs(tmp_path)
    trusted_digest = sha256(evidence_path.read_bytes()).hexdigest()
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["events"][0]["raw_event"]["action"] = "Blocked"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    with pytest.raises(ValueError, match="OCSF evidence artifact digest mismatch"):
        module.reproduce(
            evidence_path,
            mappings_path,
            tmp_path / "promotions.json",
            expected_evidence_artifact_sha256=trusted_digest,
        )


def test_build_promotion_artifact_requires_exact_mapping_manifest() -> None:
    evidence = normalize.build_evidence([_event()])

    with pytest.raises(IngestionError, match="missing OCSF recovery mappings"):
        module.build_promotion_artifact(
            evidence,
            {"recovery_mappings": {}},
            source_evidence_artifact_sha256="0" * 64,
        )


def test_mapping_manifest_digest_changes_without_source_identity_drift() -> None:
    evidence = normalize.build_evidence([_event()])
    first = module.build_promotion_artifact(
        evidence,
        {"openshell-event-42": _mapping("c-1")},
        source_evidence_artifact_sha256="1" * 64,
    )
    second = module.build_promotion_artifact(
        deepcopy(evidence),
        {"openshell-event-42": _mapping("c-2")},
        source_evidence_artifact_sha256="1" * 64,
    )

    assert first["source_evidence_artifact_sha256"] == (
        second["source_evidence_artifact_sha256"]
    )
    assert first["recovery_mapping_manifest_sha256"] != (
        second["recovery_mapping_manifest_sha256"]
    )


def test_build_promotion_artifact_rejects_nondeterministic_manifest() -> None:
    evidence = normalize.build_evidence([_event()])
    mapping = _mapping()
    mapping["params"] = {"contact_id": object()}

    with pytest.raises(
        (ValueError, IngestionError),
        match="deterministic JSON data",
    ):
        module.build_promotion_artifact(
            evidence,
            {"openshell-event-42": mapping},
            source_evidence_artifact_sha256="2" * 64,
        )


@pytest.mark.parametrize("digest", ["abc", "Z" * 64])
def test_build_promotion_artifact_rejects_malformed_source_digest(
    digest: str,
) -> None:
    with pytest.raises(ValueError, match="source_evidence_artifact_sha256"):
        module.build_promotion_artifact(
            normalize.build_evidence([_event()]),
            {"openshell-event-42": _mapping()},
            source_evidence_artifact_sha256=digest,
        )


def test_build_promotion_artifact_rejects_ambiguous_manifest_wrapper() -> None:
    with pytest.raises(ValueError, match="may only contain recovery_mappings"):
        module.build_promotion_artifact(
            normalize.build_evidence([_event()]),
            {
                "recovery_mappings": {"openshell-event-42": _mapping()},
                "unbound_context": {"approved": True},
            },
            source_evidence_artifact_sha256="3" * 64,
        )


def _write_promotion_artifact(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    evidence_path, mappings_path = _write_inputs(tmp_path)
    output_path = tmp_path / "promotions.json"
    artifact = module.reproduce(evidence_path, mappings_path, output_path)
    return output_path, artifact


def test_receiver_verifies_exact_promotion_artifact(tmp_path: Path) -> None:
    output_path, artifact = _write_promotion_artifact(tmp_path)
    artifact_digest = sha256(output_path.read_bytes()).hexdigest()

    assert module.verify_promotion_artifact_file(
        output_path,
        expected_artifact_sha256=artifact_digest.upper(),
    ) == artifact


def test_receiver_rejects_changed_promotion_file_against_trusted_digest(
    tmp_path: Path,
) -> None:
    output_path, _ = _write_promotion_artifact(tmp_path)
    artifact_digest = sha256(output_path.read_bytes()).hexdigest()
    output_path.write_text(
        output_path.read_text(encoding="utf-8") + " ",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="OCSF promotion artifact digest mismatch"):
        module.verify_promotion_artifact_file(
            output_path,
            expected_artifact_sha256=artifact_digest,
        )


def test_receiver_rejects_observation_tampering() -> None:
    evidence = normalize.build_evidence([_event()])
    artifact = module.build_promotion_artifact(
        evidence,
        {"openshell-event-42": _mapping()},
        source_evidence_artifact_sha256="4" * 64,
    )
    artifact["promotions"][0]["observation"]["params"]["status"] = "tampered"

    with pytest.raises(ValueError, match="params does not match recovery_mapping"):
        module.verify_promotion_artifact(artifact)


def test_receiver_rejects_recovery_mapping_tampering() -> None:
    evidence = normalize.build_evidence([_event()])
    artifact = module.build_promotion_artifact(
        evidence,
        {"openshell-event-42": _mapping()},
        source_evidence_artifact_sha256="5" * 64,
    )
    artifact["promotions"][0]["recovery_mapping"]["params"]["status"] = "tampered"

    with pytest.raises(ValueError, match="recovery_mapping_digest mismatch"):
        module.verify_promotion_artifact(artifact)


def test_receiver_rejects_authorization_claim() -> None:
    evidence = normalize.build_evidence([_event()])
    artifact = module.build_promotion_artifact(
        evidence,
        {"openshell-event-42": _mapping()},
        source_evidence_artifact_sha256="6" * 64,
    )
    artifact["promotions"][0]["authorization_effect"] = "restore"

    with pytest.raises(ValueError, match="authorization_effect must be none"):
        module.verify_promotion_artifact(artifact)


def test_receiver_rejects_manifest_identity_drift() -> None:
    evidence = normalize.build_evidence([_event()])
    artifact = module.build_promotion_artifact(
        evidence,
        {"openshell-event-42": _mapping()},
        source_evidence_artifact_sha256="7" * 64,
    )
    artifact["recovery_mapping_manifest_sha256"] = "8" * 64

    with pytest.raises(ValueError, match="recovery_mapping_manifest_sha256 mismatch"):
        module.verify_promotion_artifact(artifact)


def test_receiver_matches_producer_text_normalization() -> None:
    mapping = _mapping()
    for field in (
        "incident_id",
        "tool_id",
        "action_type",
        "contract_version",
        "agent_id",
        "authority_scope",
    ):
        mapping[field] = f"  {mapping[field]}  "
    mapping["resource_keys"] = ["  crm:contact:c-1  "]
    artifact = module.build_promotion_artifact(
        normalize.build_evidence([_event()]),
        {"openshell-event-42": mapping},
        source_evidence_artifact_sha256="9" * 64,
    )

    assert module.verify_promotion_artifact(artifact) == artifact
