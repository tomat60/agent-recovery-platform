from agent_recovery.benchmark import run_vertical_slice


def test_recovery_platform_beats_stop_only_on_recoverable_scenarios() -> None:
    results = run_vertical_slice()
    recoverable = [result for result in results if result.platform_verified_recoveries]

    assert len(recoverable) == 3
    assert all(result.baseline_residual_effects == 1 for result in recoverable)
    assert all(result.platform_residual_effects == 0 for result in recoverable)
    assert all(result.unsafe_recovery_executions == 0 for result in recoverable)


def test_approval_bypass_fixture_fails_closed_without_side_effect() -> None:
    results = {result.scenario: result for result in run_vertical_slice()}
    approval_bypass = results["approval_bypass_attempt"]

    assert approval_bypass.baseline_residual_effects == 1
    assert approval_bypass.platform_residual_effects == 0
    assert approval_bypass.platform_verified_recoveries == 0
    assert approval_bypass.platform_explicit_irreversible_residuals == 0
    assert approval_bypass.unsafe_recovery_executions == 0


def test_irreversible_effect_remains_explicitly_residual() -> None:
    results = {result.scenario: result for result in run_vertical_slice()}
    message = results["irreversible_external_message"]

    assert message.baseline_residual_effects == 1
    assert message.platform_residual_effects == 1
    assert message.platform_verified_recoveries == 0
    assert message.platform_explicit_irreversible_residuals == 1
    assert message.unsafe_recovery_executions == 0
