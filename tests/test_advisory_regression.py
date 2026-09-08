import pytest

from agent_recovery.advisory_gate import AdvisoryGateDecision, CandidateRecoveryPlan
from agent_recovery.advisory_regression import build_rejected_advisory_regression


def test_builds_rejected_advisory_regression_from_evidence() -> None:
    regression = build_rejected_advisory_regression(
        source_incident_id="inc-42",
        scenario="recovery_path_attack",
        decision=AdvisoryGateDecision(
            accepted=False,
            reasons=("skeptic verdict is unsupported",),
            candidate_plan=None,
        ),
        evidence_refs=("ledger:evt-9", "skeptic:challenge-2"),
    )

    assert regression.source_incident_id == "inc-42"
    assert regression.scenario == "recovery_path_attack"
    assert "model output is never authorization" in regression.expected_invariants
    assert "rejected advisory exposes no candidate recovery plan" in regression.expected_invariants
    assert "unsupported or uncertain advisory claims remain rejected" in regression.expected_invariants


def test_rejects_accepted_advisory_decision() -> None:
    with pytest.raises(ValueError, match="accepted advisory"):
        build_rejected_advisory_regression(
            source_incident_id="inc-42",
            scenario="memory_poisoning",
            decision=AdvisoryGateDecision(accepted=True, reasons=(), candidate_plan=None),
            evidence_refs=("ledger:evt-1",),
        )


def test_rejects_candidate_exposure_on_rejected_decision() -> None:
    candidate = CandidateRecoveryPlan(
        incident_id="inc-42",
        summary="plausible but unauthorized",
        steps=(),
        residual_risks=(),
        evidence_event_ids=("evt-1",),
        skeptic_evidence_event_ids=("evt-1",),
    )
    with pytest.raises(ValueError, match="must not expose"):
        build_rejected_advisory_regression(
            source_incident_id="inc-42",
            scenario="approval_bypass",
            decision=AdvisoryGateDecision(
                accepted=False,
                reasons=("unsupported",),
                candidate_plan=candidate,
            ),
            evidence_refs=("ledger:evt-1",),
        )


def test_rejected_advisory_requires_reasons() -> None:
    with pytest.raises(ValueError, match="rejection reasons"):
        build_rejected_advisory_regression(
            source_incident_id="inc-42",
            scenario="tool_output_poisoning",
            decision=AdvisoryGateDecision(accepted=False, reasons=(), candidate_plan=None),
            evidence_refs=("ledger:evt-1",),
        )
