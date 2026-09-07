from agent_recovery.indirect_prompt_injection_benchmark import (
    run_indirect_prompt_injection_benchmark,
)


def test_indirect_prompt_injection_trajectory_is_contained_and_recovered() -> None:
    score = run_indirect_prompt_injection_benchmark()

    assert score.scenario == "indirect_prompt_injection_trajectory"
    assert score.baseline_residual_effects == 1
    assert score.platform_residual_effects == 0
    assert score.containment_success == 1
    assert score.causal_evidence_complete == 1
    assert score.verified_recoveries == 1
    assert score.unsafe_recovery_executions == 0
