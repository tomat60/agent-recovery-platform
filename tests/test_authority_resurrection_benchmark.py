from agent_recovery.authority_resurrection_benchmark import (
    run_authority_resurrection_scenario,
)


def test_authority_resurrection_replay_attempt_fails_closed() -> None:
    score = run_authority_resurrection_scenario()

    assert score.scenario == "authority_resurrection_replay_attempt"
    assert score.initial_executions == 1
    assert score.resurrection_attempts == 1
    assert score.blocked_resurrection_attempts == 1
    assert score.duplicate_external_effects == 0
    assert score.unsafe_executions == 0
