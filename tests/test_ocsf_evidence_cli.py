from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from agent_recovery.ingestion import IngestionError

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "normalize_ocsf_evidence.py"
spec = importlib.util.spec_from_file_location("normalize_ocsf_evidence", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _event(uid: str = "openshell-event-42") -> dict[str, object]:
    return {
        "class_uid": 4002,
        "class_name": "HTTP Activity",
        "activity_id": 1,
        "activity_name": "Request",
        "time": 1790751000000,
        "metadata": {
            "uid": uid,
            "version": "1.8.0",
            "product": {
                "name": "OpenShell Sandbox Supervisor",
                "vendor_name": "NVIDIA",
                "version": "0.3.0",
            },
        },
        "container": {"uid": "sandbox-7"},
        "action": "Allowed",
        "disposition": "Allowed",
        "http_request": {"http_method": "POST"},
        "dst_endpoint": {"domain": "crm.example.test", "port": 443},
    }


def test_build_evidence_is_deterministic_and_non_authorizing() -> None:
    evidence = module.build_evidence({"events": [_event()]})

    assert evidence["schema_version"] == "agent-recovery-ocsf-evidence/v1"
    assert evidence["authorization_effect"] == "none"
    assert evidence["event_count"] == 1
    event = evidence["events"][0]
    assert event["source_event_id"] == "openshell-event-42"
    assert event["source_system"] == "ocsf"
    assert event["authorization_effect"] == "none"
    assert len(event["provenance_digest"]) == 64
    assert module.build_evidence([deepcopy(_event())]) == evidence


def test_reproduce_writes_the_exact_evidence_artifact(tmp_path: Path) -> None:
    source = tmp_path / "ocsf.json"
    output = tmp_path / "evidence.json"
    source.write_text(json.dumps([_event()]), encoding="utf-8")

    evidence = module.reproduce(source, output)

    assert json.loads(output.read_text(encoding="utf-8")) == evidence
    assert module.verify_artifact(output) == evidence


def test_verify_artifact_accepts_independently_obtained_digest(
    tmp_path: Path,
) -> None:
    source = tmp_path / "ocsf.json"
    output = tmp_path / "evidence.json"
    source.write_text(json.dumps([_event()]), encoding="utf-8")
    evidence = module.reproduce(source, output)
    artifact_digest = sha256(output.read_bytes()).hexdigest()

    assert module.verify_artifact(
        output, expected_artifact_sha256=artifact_digest.upper()
    ) == evidence


def test_verify_artifact_rejects_changed_file_against_prior_digest(
    tmp_path: Path,
) -> None:
    source = tmp_path / "ocsf.json"
    output = tmp_path / "evidence.json"
    source.write_text(json.dumps([_event()]), encoding="utf-8")
    module.reproduce(source, output)
    artifact_digest = sha256(output.read_bytes()).hexdigest()
    output.write_text(output.read_text(encoding="utf-8") + " ", encoding="utf-8")

    with pytest.raises(ValueError, match="OCSF evidence artifact digest mismatch"):
        module.verify_artifact(output, expected_artifact_sha256=artifact_digest)


@pytest.mark.parametrize("artifact_digest", ["abc", "z" * 64])
def test_verify_artifact_rejects_malformed_expected_digest(
    tmp_path: Path, artifact_digest: str
) -> None:
    output = tmp_path / "evidence.json"
    output.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="64 hexadecimal characters"):
        module.verify_artifact(
            output, expected_artifact_sha256=artifact_digest
        )


def test_build_evidence_rejects_duplicate_source_identity() -> None:
    with pytest.raises(IngestionError, match="duplicate OCSF source event"):
        module.build_evidence([_event(), deepcopy(_event())])


def test_verify_evidence_rejects_raw_event_tampering() -> None:
    evidence = deepcopy(module.build_evidence([_event()]))
    evidence["events"][0]["raw_event"]["dst_endpoint"]["domain"] = (
        "billing.example.test"
    )

    with pytest.raises(ValueError, match="normalized payload does not match raw_event"):
        module.verify_evidence(evidence)


def test_verify_evidence_rejects_normalized_identity_drift() -> None:
    evidence = deepcopy(module.build_evidence([_event()]))
    evidence["events"][0]["source_event_id"] = "different-event"

    with pytest.raises(ValueError, match="normalized payload does not match raw_event"):
        module.verify_evidence(evidence)


def test_verify_evidence_rejects_authorization_claim() -> None:
    evidence = deepcopy(module.build_evidence([_event()]))
    evidence["events"][0]["authorization_effect"] = "restore"

    with pytest.raises(ValueError, match="authorization_effect must be none"):
        module.verify_evidence(evidence)


def test_verify_evidence_rejects_count_drift() -> None:
    evidence = deepcopy(module.build_evidence([_event()]))
    evidence["event_count"] = 2

    with pytest.raises(ValueError, match="event_count does not match"):
        module.verify_evidence(evidence)


@pytest.mark.parametrize("payload", [{}, {"events": {}}, "not-an-export"])
def test_build_evidence_rejects_ambiguous_input(payload: object) -> None:
    with pytest.raises(
        TypeError,
        match="array or an object with an events array",
    ):
        module.build_evidence(payload)
