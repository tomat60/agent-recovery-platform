from copy import deepcopy

import pytest

from agent_recovery.judge_incident_evidence import (
    build_judge_incident_evidence,
    validate_judge_incident_evidence,
)


def test_full_incident_evidence_is_authority_free_and_measured() -> None:
    evidence = build_judge_incident_evidence()
    validate_judge_incident_evidence(evidence)

    assert evidence["authorization_effect"] == "none"
    assert evidence["scenario"] == "poisoned_support_to_shared_state_to_identity"
    phases = evidence["phases"]
    assert phases["blast_radius"]["recall"] == 1.0
    assert phases["blast_radius"]["precision"] == 1.0
    assert phases["containment"]["root_agent_remains_contained"] is True
    assert phases["recovery"]["platform_residual_effects"] == 0
    assert phases["replay"]["verified"] is True
    assert phases["replay"]["unsafe_recovery_executions"] == 0
    assert phases["restoration"]["root_authority_restored"] is False


def test_incident_evidence_rejects_authority_injection() -> None:
    evidence = build_judge_incident_evidence()
    tampered = deepcopy(evidence)
    tampered["authorization_effect"] = "execute"

    with pytest.raises(ValueError, match="must not carry execution authority"):
        validate_judge_incident_evidence(tampered)


def test_incident_evidence_rejects_missing_phase() -> None:
    evidence = build_judge_incident_evidence()
    tampered = deepcopy(evidence)
    del tampered["phases"]["replay"]

    with pytest.raises(ValueError, match="exact required phases"):
        validate_judge_incident_evidence(tampered)
