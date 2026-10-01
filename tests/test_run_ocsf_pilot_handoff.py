from __future__ import annotations

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
package = _load("package_ocsf_pilot_handoff")


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


def _write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    events_path = tmp_path / "events.json"
    events_path.write_text(json.dumps([_event()]), encoding="utf-8")
    mappings_path = tmp_path / "mappings.json"
    mappings_path.write_text(
        json.dumps({"recovery_mappings": {"openshell-event-42": _mapping()}}),
        encoding="utf-8",
    )
    return events_path, mappings_path


def test_run_builds_and_self_verifies_complete_handoff(tmp_path: Path) -> None:
    events_path, mappings_path = _write_inputs(tmp_path)
    output = tmp_path / "handoff"

    result = runner.run_handoff(events_path, mappings_path, output)

    assert result["ok"] is True
    assert result["authorization_effect"] == "none"
    assert result["source_event_count"] == 1
    assert result["promotion_count"] == 1
    assert result["self_verification"]["manifest_pin_verified"] is True
    assert sorted(path.name for path in output.iterdir()) == sorted(
        [
            runner.EVIDENCE_FILENAME,
            runner.PROMOTIONS_FILENAME,
            runner.MANIFEST_FILENAME,
        ]
    )
    assert package.verify_handoff_package(
        output / runner.EVIDENCE_FILENAME,
        output / runner.PROMOTIONS_FILENAME,
        output / runner.MANIFEST_FILENAME,
        result["manifest_sha256"],
    )["ok"] is True


def test_run_fails_without_partial_output_when_mapping_is_missing(
    tmp_path: Path,
) -> None:
    events_path, mappings_path = _write_inputs(tmp_path)
    mappings_path.write_text(
        json.dumps({"recovery_mappings": {}}),
        encoding="utf-8",
    )
    output = tmp_path / "handoff"

    with pytest.raises(Exception, match="missing OCSF recovery mappings"):
        runner.run_handoff(events_path, mappings_path, output)

    assert not output.exists()


def test_run_refuses_to_overwrite_existing_delivery(tmp_path: Path) -> None:
    events_path, mappings_path = _write_inputs(tmp_path)
    output = tmp_path / "handoff"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("owner evidence", encoding="utf-8")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        runner.run_handoff(events_path, mappings_path, output)

    assert sentinel.read_text(encoding="utf-8") == "owner evidence"


def test_run_is_deterministic_across_clean_directories(tmp_path: Path) -> None:
    events_path, mappings_path = _write_inputs(tmp_path)

    first = runner.run_handoff(events_path, mappings_path, tmp_path / "first")
    second = runner.run_handoff(events_path, mappings_path, tmp_path / "second")

    assert first["evidence_artifact_sha256"] == second["evidence_artifact_sha256"]
    assert first["manifest_sha256"] == second["manifest_sha256"]
    for filename in first["artifacts"]:
        assert (tmp_path / "first" / filename).read_bytes() == (
            tmp_path / "second" / filename
        ).read_bytes()
