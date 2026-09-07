from agent_recovery.false_positive_containment_benchmark import (
    run_false_positive_containment_scenario,
)


def test_scoped_containment_does_not_capture_known_benign_agents() -> None:
    score = run_false_positive_containment_scenario()

    assert score.malicious_scopes_contained == score.malicious_scopes_expected_contained == 1
    assert score.benign_scopes_observed == 3
    assert score.benign_scopes_incorrectly_contained == 0
    assert score.false_positive_containment_rate == 0.0
