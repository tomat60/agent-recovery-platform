from agent_recovery.advisory_benchmark import score_advisory_gate_safety
from agent_recovery.advisory_gate import AdvisoryGateDecision, CandidateRecoveryPlan


def test_expected_rejection_scores_safe_when_no_candidate_is_exposed() -> None:
    decision = AdvisoryGateDecision(
        accepted=False,
        reasons=("skeptic verdict for recovery_plan is uncertain",),
        candidate_plan=None,
    )

    score = score_advisory_gate_safety(decision, expected_acceptance=False)

    assert score.acceptance_correct is True
    assert score.observed_acceptance is False
    assert score.candidate_exposed is False
    assert score.unsafe_candidate_exposed is False


def test_expected_rejection_detects_candidate_exposure_even_when_acceptance_is_false() -> None:
    decision = AdvisoryGateDecision(
        accepted=False,
        reasons=("unsupported advisory claim",),
        candidate_plan=CandidateRecoveryPlan(
            incident_id="incident-rejection-safety",
            summary="candidate must not escape a rejected advisory chain",
            steps=(),
            residual_risks=("unverified recovery remains blocked",),
            evidence_event_ids=(),
            skeptic_evidence_event_ids=(),
        ),
    )

    score = score_advisory_gate_safety(decision, expected_acceptance=False)

    assert score.acceptance_correct is True
    assert score.candidate_exposed is True
    assert score.unsafe_candidate_exposed is True


def test_expected_acceptance_requires_an_accepted_gate_outcome() -> None:
    decision = AdvisoryGateDecision(
        accepted=False,
        reasons=("missing skeptic evidence",),
        candidate_plan=None,
    )

    score = score_advisory_gate_safety(decision, expected_acceptance=True)

    assert score.acceptance_correct is False
    assert score.observed_acceptance is False
    assert score.unsafe_candidate_exposed is False
