from agent_recovery.over_scoped_identity_benchmark import run_over_scoped_identity_benchmark


def test_narrow_identity_approval_cannot_authorize_broader_privilege() -> None:
    result = run_over_scoped_identity_benchmark()

    assert result.baseline_privilege_present is True
    assert result.platform_privilege_present is False
    assert result.narrow_approval_rejected is True
    assert result.unsafe_recovery_executions == 0
