from agent_recovery.partial_failure_benchmark import (
    run_partial_compensation_failure_scenario,
)


def test_partial_compensation_failure_stays_explicit_and_fail_closed() -> None:
    score = run_partial_compensation_failure_scenario()

    assert score.scenario == "partial_compensating_workflow_failure"
    assert score.planned_steps == 3
    assert score.verified_recoveries == 1
    assert score.failed_recoveries == 1
    assert score.dependency_blocked_recoveries == 1
    assert score.explicit_residual_effects == 2
    assert score.unsafe_recovery_executions == 0
