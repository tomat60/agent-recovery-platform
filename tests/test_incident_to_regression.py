import pytest

from agent_recovery.regression import build_incident_regression


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
