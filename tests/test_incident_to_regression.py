import pytest

from agent_recovery.regression import (
    PORTABLE_REGRESSION_SCHEMA_VERSION,
    build_incident_regression,
    build_portable_incident_regression,
    verify_portable_incident_regression,
)


def test_incident_to_regression_is_deterministic_and_evidence_bound() -> None:
    first = build_incident_regression(
        source_incident_id="inc-42",
        scenario="indirect_prompt_injection",
        evidence_refs=("ledger:evt-9", "replay:proof-3", "ledger:evt-9"),
        expected_invariants=(
            "source agent remains contained",
            "no consequential write without valid approval",
        ),
    )
    second = build_incident_regression(
        source_incident_id="inc-42",
        scenario="indirect_prompt_injection",
        evidence_refs=("replay:proof-3", "ledger:evt-9"),
        expected_invariants=(
            "no consequential write without valid approval",
            "source agent remains contained",
        ),
    )

    assert first == second
    assert first.regression_id.startswith("reg-")
    assert first.evidence_refs == ("ledger:evt-9", "replay:proof-3")
    assert first.fingerprint


def test_incident_to_regression_requires_evidence_and_invariants() -> None:
    with pytest.raises(ValueError, match="evidence"):
        build_incident_regression(
            source_incident_id="inc-42",
            scenario="memory_poisoning",
            evidence_refs=(),
            expected_invariants=("memory remains quarantined",),
        )

    with pytest.raises(ValueError, match="invariant"):
        build_incident_regression(
            source_incident_id="inc-42",
            scenario="memory_poisoning",
            evidence_refs=("ledger:evt-1",),
            expected_invariants=(),
        )



def _portable_package(**overrides: tuple[str, ...]):
    values = {
        "source_incident_id": "inc-42",
        "scenario": "cross_system_partial_completion",
        "evidence_refs": ("ledger:evt-9", "verifier:proof-3"),
        "causal_dependencies": ("evt-9->evt-10",),
        "recovery_obligations": (
            "restore crm:contact:c-1",
            "delete tasks:task:t-7",
        ),
        "residual_expectations": ("external notification remains explicit",),
        "replay_inputs": ("fixture:incident-inc-42-v1",),
        "restoration_scopes": ("integration:crm", "integration:tasks"),
        "expected_invariants": (
            "no consequential write without valid approval",
            "restoration is limited to verified scopes",
        ),
    }
    values.update(overrides)
    return build_portable_incident_regression(**values)


def test_portable_incident_regression_is_deterministic_and_verifiable() -> None:
    first = _portable_package()
    second = _portable_package(
        evidence_refs=("verifier:proof-3", "ledger:evt-9", "ledger:evt-9"),
        recovery_obligations=(
            "delete tasks:task:t-7",
            "restore crm:contact:c-1",
        ),
        restoration_scopes=("integration:tasks", "integration:crm"),
    )

    assert first == second
    assert first.schema_version == PORTABLE_REGRESSION_SCHEMA_VERSION
    assert first.authorization_effect == "none"
    assert first.regression_id.startswith("regpkg-")
    assert verify_portable_incident_regression(first.to_dict()) == first


def test_portable_incident_regression_rejects_tampering_and_authority() -> None:
    payload = _portable_package().to_dict()
    payload["replay_inputs"] = ["fixture:substituted"]
    with pytest.raises(ValueError, match="package mismatch"):
        verify_portable_incident_regression(payload)

    payload = _portable_package().to_dict()
    payload["authorization_effect"] = "restore"
    with pytest.raises(ValueError, match="non-authorizing"):
        verify_portable_incident_regression(payload)

    payload = _portable_package().to_dict()
    payload["unexpected"] = True
    with pytest.raises(ValueError, match="fields mismatch"):
        verify_portable_incident_regression(payload)


@pytest.mark.parametrize(
    ("field", "message"),
    (
        ("evidence_refs", "evidence reference"),
        ("recovery_obligations", "recovery obligation"),
        ("residual_expectations", "residual expectation"),
        ("replay_inputs", "replay input"),
        ("restoration_scopes", "restoration scope"),
        ("expected_invariants", "expected invariant"),
    ),
)
def test_portable_incident_regression_requires_complete_recovery_truth(
    field: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        _portable_package(**{field: ()})
