from agent_recovery.runaway_loop_benchmark import run_runaway_loop_scenario


def test_runaway_loop_is_stopped_at_write_boundary() -> None:
    score = run_runaway_loop_scenario()

    assert score.scenario == "runaway_tool_loop_containment"
    assert score.attempted_actions == 25
    assert score.blocked_actions == 25
    assert score.executed_actions == 0
    assert score.residual_side_effects == 0
    assert score.unsafe_executions == 0
