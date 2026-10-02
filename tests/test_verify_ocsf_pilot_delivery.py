from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
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


runner = _load("run_ocsf_pilot_handoff")
verifier = _load("verify_ocsf_pilot_delivery")


def _event() -> dict[str, object]:
    return {
        "class_uid": 4002,
        "activity_id": 1,
        "time": 1790751000000,
        "metadata": {
            "uid": "openshell-event-42",
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


def _delivery(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    events_path = tmp_path / "events.json"
    events_path.write_text(json.dumps([_event()]), encoding="utf-8")
    mappings_path = tmp_path / "mappings.json"
    mappings_path.write_text(
        json.dumps({"recovery_mappings": {"openshell-event-42": _mapping()}}),
        encoding="utf-8",
    )
    output = tmp_path / "handoff"
    result = runner.run_handoff(events_path, mappings_path, output)
    return output, result


def test_verify_delivery_accepts_exact_pinned_directory(tmp_path: Path) -> None:
    output, handoff = _delivery(tmp_path)

    result = verifier.verify_delivery(output, handoff["manifest_sha256"])

    assert result["ok"] is True
    assert result["schema_version"] == verifier.VERIFICATION_SCHEMA_VERSION
    assert result["authorization_effect"] == "none"
    assert result["manifest_pin_verified"] is True
    assert result["verified_delivery_files"] == sorted(verifier.EXPECTED_FILENAMES)


def test_verification_receipt_is_exact_external_and_non_overwriting(
    tmp_path: Path,
) -> None:
    output, handoff = _delivery(tmp_path)
    result = verifier.verify_delivery(output, handoff["manifest_sha256"])
    receipt = tmp_path / "receiver-evidence" / "verification-receipt.json"

    verifier.write_verification_receipt(result, receipt, output)

    assert json.loads(receipt.read_text(encoding="utf-8")) == result
    assert receipt.read_text(encoding="utf-8").endswith("\n")
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        verifier.write_verification_receipt(result, receipt, output)
    with pytest.raises(ValueError, match="outside the verified delivery"):
        verifier.write_verification_receipt(
            result,
            output / "verification-receipt.json",
            output,
        )


def test_verify_delivery_rejects_missing_artifact(tmp_path: Path) -> None:
    output, _ = _delivery(tmp_path)
    (output / verifier.PROMOTIONS_FILENAME).unlink()

    with pytest.raises(ValueError, match="missing=.*ocsf-promotions.json"):
        verifier.verify_delivery(output)


def test_verify_delivery_rejects_unexpected_entry(tmp_path: Path) -> None:
    output, _ = _delivery(tmp_path)
    (output / "notes.txt").write_text("unverified", encoding="utf-8")

    with pytest.raises(ValueError, match="unexpected=.*notes.txt"):
        verifier.verify_delivery(output)


def test_verify_delivery_rejects_expected_name_that_is_not_a_file(
    tmp_path: Path,
) -> None:
    output, _ = _delivery(tmp_path)
    manifest = output / verifier.MANIFEST_FILENAME
    manifest.unlink()
    manifest.mkdir()

    with pytest.raises(ValueError, match="non_files=.*ocsf-handoff.manifest.json"):
        verifier.verify_delivery(output)


def test_verify_delivery_rejects_wrong_pin_file_and_symlinked_directory(
    tmp_path: Path,
) -> None:
    output, _ = _delivery(tmp_path)

    with pytest.raises(ValueError, match="manifest digest mismatch"):
        verifier.verify_delivery(output, "0" * 64)

    with pytest.raises(NotADirectoryError, match="real directory"):
        verifier.verify_delivery(output / verifier.EVIDENCE_FILENAME)

    linked_output = tmp_path / "linked-handoff"
    linked_output.symlink_to(output, target_is_directory=True)
    with pytest.raises(NotADirectoryError, match="not a symlink"):
        verifier.verify_delivery(linked_output)


def test_verify_receipt_replays_exact_current_delivery_with_pin(
    tmp_path: Path,
) -> None:
    output, handoff = _delivery(tmp_path)
    verification = verifier.verify_delivery(output, handoff["manifest_sha256"])
    receipt = tmp_path / "receiver-evidence" / "verification-receipt.json"
    verifier.write_verification_receipt(verification, receipt, output)
    receipt_sha256 = hashlib.sha256(receipt.read_bytes()).hexdigest()

    replay = verifier.verify_verification_receipt(
        receipt,
        output,
        handoff["manifest_sha256"],
        receipt_sha256,
    )

    assert replay["ok"] is True
    assert replay["authorization_effect"] == "none"
    assert replay["schema_version"] == verifier.RECEIPT_REPLAY_SCHEMA_VERSION
    assert replay["receipt_schema_version"] == verifier.VERIFICATION_SCHEMA_VERSION
    assert replay["receipt_sha256"] == receipt_sha256
    assert replay["receipt_pin_verified"] is True
    assert replay["delivery_verification"] == verification


def test_verify_receipt_rejects_stale_delivery_and_tampered_receipt(
    tmp_path: Path,
) -> None:
    output, handoff = _delivery(tmp_path)
    verification = verifier.verify_delivery(output, handoff["manifest_sha256"])
    receipt = tmp_path / "verification-receipt.json"
    verifier.write_verification_receipt(verification, receipt, output)

    promotions = output / verifier.PROMOTIONS_FILENAME
    promotions.write_text(
        promotions.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="digest mismatch"):
        verifier.verify_verification_receipt(receipt, output)

    fresh_root = tmp_path / "fresh"
    fresh_root.mkdir()
    output, handoff = _delivery(fresh_root)
    verification = verifier.verify_delivery(output, handoff["manifest_sha256"])
    receipt = tmp_path / "fresh-receipt.json"
    verifier.write_verification_receipt(verification, receipt, output)
    parsed = json.loads(receipt.read_text(encoding="utf-8"))
    receipt.write_text(json.dumps(parsed), encoding="utf-8")
    with pytest.raises(ValueError, match="does not exactly match"):
        verifier.verify_verification_receipt(receipt, output)


def test_verify_receipt_rejects_wrong_pin_symlink_and_delivery_local_path(
    tmp_path: Path,
) -> None:
    output, _ = _delivery(tmp_path)
    verification = verifier.verify_delivery(output)
    receipt = tmp_path / "verification-receipt.json"
    verifier.write_verification_receipt(verification, receipt, output)

    with pytest.raises(ValueError, match="receipt digest mismatch"):
        verifier.verify_verification_receipt(
            receipt,
            output,
            expected_receipt_sha256="0" * 64,
        )

    linked_receipt = tmp_path / "linked-receipt.json"
    linked_receipt.symlink_to(receipt)
    with pytest.raises(FileNotFoundError, match="real file"):
        verifier.verify_verification_receipt(linked_receipt, output)

    with pytest.raises(ValueError, match="outside the verified delivery"):
        verifier.verify_verification_receipt(
            output / verifier.EVIDENCE_FILENAME,
            output,
        )
