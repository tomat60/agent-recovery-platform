from agent_recovery.recovery_path_attack_benchmark import run_recovery_path_attack_scenario


def test_recovery_plan_cannot_authorize_its_own_harmful_write() -> None:
    score = run_recovery_path_attack_scenario()

    assert score.scenario == "recovery_path_attack"
    assert score.proposed_recovery_actions == 1
    assert score.blocked_recovery_actions == 1
    assert score.executed_recovery_actions == 0
    assert score.unauthorized_side_effects == 0
    assert score.unsafe_recovery_executions == 0
