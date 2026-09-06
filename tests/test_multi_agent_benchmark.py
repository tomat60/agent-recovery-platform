from agent_recovery.multi_agent_benchmark import run_multi_agent_recovery_scenario


def test_three_agent_incident_recovers_and_restores_only_after_verified_replay() -> None:
    score = run_multi_agent_recovery_scenario()

    assert score.agents_involved == 3
    assert score.expected_blast_actions == 3
    assert score.detected_blast_actions == 3
    assert score.blast_radius_recall == 1.0
    assert score.blast_radius_precision == 1.0
    assert score.verified_recoveries == 3
    assert score.platform_residual_effects == 0
    assert score.replay_verified is True
    assert score.restored_downstream_authorities == 2
    assert score.root_agent_remains_contained is True
    assert score.unsafe_recovery_executions == 0
