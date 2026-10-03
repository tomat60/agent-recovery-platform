from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = _load("run_recoverability_assessment_handoff")
assessment = _load("build_recoverability_assessment")
pilot = _load("run_owned_multisurface_pilot")


def _write_evidence(tmp_path: Path) -> tuple[Path, str]:
    evidence = pilot.build_pilot_evidence()
    path = tmp_path / "owned-pilot-evidence.json"
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path, assessment.evidence_identity(evidence)


def test_run_builds_and_self_verifies_complete_handoff(tmp_path: Path) -> None:
    evidence_path, evidence_sha256 = _write_evidence(tmp_path)
    output = tmp_path / "handoff"

    result = runner.run_handoff(evidence_path, output, evidence_sha256.upper())

    assert result["ok"] is True
    assert result["authorization_effect"] == "none"
    assert result["source_evidence_identity"]["sha256"] == evidence_sha256
    assert result["self_verification"]["assessment"]["manifest_pin_verified"] is True
    assert (
        result["self_verification"]["portable_regression"][
            "artifact_pin_verified"
        ]
        is True
    )
    assert sorted(path.name for path in output.iterdir()) == sorted(result["artifacts"])


def test_run_rejects_wrong_evidence_pin_without_output(tmp_path: Path) -> None:
    evidence_path, _ = _write_evidence(tmp_path)
    output = tmp_path / "handoff"

    with pytest.raises(ValueError, match="evidence identity mismatch"):
        runner.run_handoff(evidence_path, output, "0" * 64)

    assert not output.exists()


def test_run_removes_partial_delivery_when_publication_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_path, _ = _write_evidence(tmp_path)
    output = tmp_path / "handoff"
    move = runner.shutil.move
    calls = 0

    def fail_second_move(source: str, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic publication failure")
        move(source, destination)

    monkeypatch.setattr(runner.shutil, "move", fail_second_move)

    with pytest.raises(OSError, match="synthetic publication failure"):
        runner.run_handoff(evidence_path, output)

    assert not output.exists()


def test_run_refuses_to_overwrite_existing_delivery(tmp_path: Path) -> None:
    evidence_path, _ = _write_evidence(tmp_path)
    output = tmp_path / "handoff"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("retained evidence", encoding="utf-8")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        runner.run_handoff(evidence_path, output)

    assert sentinel.read_text(encoding="utf-8") == "retained evidence"


def test_run_is_deterministic_across_clean_directories(tmp_path: Path) -> None:
    evidence_path, _ = _write_evidence(tmp_path)

    first = runner.run_handoff(evidence_path, tmp_path / "first")
    second = runner.run_handoff(evidence_path, tmp_path / "second")

    for key in (
        "assessment_sha256",
        "assessment_manifest_sha256",
        "portable_regression_sha256",
    ):
        assert first[key] == second[key]
    for filename in first["artifacts"]:
        assert (tmp_path / "first" / filename).read_bytes() == (
            tmp_path / "second" / filename
        ).read_bytes()
