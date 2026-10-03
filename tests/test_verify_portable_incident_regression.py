from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from agent_recovery.regression import build_portable_incident_regression

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "verify_portable_incident_regression.py"
)
spec = importlib.util.spec_from_file_location(
    "verify_portable_incident_regression",
    SCRIPT,
)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _package() -> dict[str, object]:
    return build_portable_incident_regression(
        source_incident_id="incident-42",
        scenario="owned multi-surface recovery",
        evidence_refs=("evidence:sha256:abc",),
        causal_dependencies=("surface:shared-state",),
        recovery_obligations=("verify:shared-state",),
        residual_expectations=("root-contained:true",),
        replay_inputs=("fixture:incident-42",),
        restoration_scopes=("surface:downstream",),
        expected_invariants=("root-remains-contained",),
    ).to_dict()


def _write_package(tmp_path: Path, payload: dict[str, object]) -> tuple[Path, bytes]:
    raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    path = tmp_path / "incident-regression.json"
    path.write_bytes(raw)
    return path, raw


def test_verifies_exact_portable_package_and_optional_pin(tmp_path: Path) -> None:
    package_path, raw = _write_package(tmp_path, _package())
    digest = hashlib.sha256(raw).hexdigest()

    result = module.verify_regression_package(package_path, digest.upper())

    assert result["ok"] is True
    assert result["authorization_effect"] == "none"
    assert result["artifact_sha256"] == digest
    assert result["artifact_pin_verified"] is True
    assert result["regression_id"] == _package()["regression_id"]
    assert result["restoration_scopes"] == ["surface:downstream"]


def test_rejects_tampered_package(tmp_path: Path) -> None:
    payload = copy.deepcopy(_package())
    payload["restoration_scopes"] = ["surface:root"]
    package_path, _ = _write_package(tmp_path, payload)

    with pytest.raises(ValueError, match="package mismatch"):
        module.verify_regression_package(package_path)


def test_rejects_wrong_out_of_band_pin_before_payload_validation(
    tmp_path: Path,
) -> None:
    package_path, _ = _write_package(tmp_path, {"malformed": True})

    with pytest.raises(ValueError, match="digest mismatch"):
        module.verify_regression_package(package_path, "0" * 64)


def test_rejects_invalid_pin_shape(tmp_path: Path) -> None:
    package_path, _ = _write_package(tmp_path, _package())

    with pytest.raises(ValueError, match="64 hexadecimal"):
        module.verify_regression_package(package_path, "not-a-digest")


def test_persists_and_replays_exact_verification_receipt(tmp_path: Path) -> None:
    package_path, raw = _write_package(tmp_path, _package())
    package_sha256 = hashlib.sha256(raw).hexdigest()
    result = module.verify_regression_package(package_path, package_sha256)
    receipt_path = tmp_path / "verification-receipt.json"

    module.write_verification_receipt(result, receipt_path, package_path)
    receipt_sha256 = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    replay = module.verify_verification_receipt(
        receipt_path,
        package_path,
        package_sha256,
        receipt_sha256.upper(),
    )

    assert replay["ok"] is True
    assert replay["authorization_effect"] == "none"
    assert replay["receipt_pin_verified"] is True
    assert replay["package_verification"] == result


def test_refuses_to_overwrite_verification_receipt(tmp_path: Path) -> None:
    package_path, _ = _write_package(tmp_path, _package())
    result = module.verify_regression_package(package_path)
    receipt_path = tmp_path / "verification-receipt.json"
    receipt_path.write_text("retained receipt\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        module.write_verification_receipt(result, receipt_path, package_path)
    assert receipt_path.read_text(encoding="utf-8") == "retained receipt\n"


def test_replay_rejects_changed_package(tmp_path: Path) -> None:
    package_path, _ = _write_package(tmp_path, _package())
    result = module.verify_regression_package(package_path)
    receipt_path = tmp_path / "verification-receipt.json"
    module.write_verification_receipt(result, receipt_path, package_path)

    changed = _package()
    changed["source_incident_id"] = "incident-43"
    changed_package_path, _ = _write_package(tmp_path, changed)
    assert changed_package_path == package_path

    with pytest.raises(ValueError):
        module.verify_verification_receipt(receipt_path, package_path)


def test_replay_rejects_changed_receipt(tmp_path: Path) -> None:
    package_path, _ = _write_package(tmp_path, _package())
    result = module.verify_regression_package(package_path)
    receipt_path = tmp_path / "verification-receipt.json"
    module.write_verification_receipt(result, receipt_path, package_path)
    receipt_path.write_text(
        receipt_path.read_text(encoding="utf-8") + "tampered",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="does not exactly match"):
        module.verify_verification_receipt(receipt_path, package_path)
