from agent_recovery.readiness import RecoveryReadiness
from agent_recovery.readiness_gate import evaluate_readiness_gate


def _readiness(**overrides: object) -> RecoveryReadiness:
    values = {
        "total_actions": 2,
        "structurally_recoverable": 2,
        "reversible": 1,
        "compensatable": 1,
        "irreversible": 0,
        "missing_runtime_bindings": (),
        "blockers": (),
    }
    values.update(overrides)
    return RecoveryReadiness(**values)


def test_gate_passes_full_recoverability_without_blockers() -> None:
    result = evaluate_readiness_gate(_readiness())

    assert result.passed is True
    assert result.reasons == ()


def test_gate_fails_closed_on_missing_trusted_runtime_binding() -> None:
    result = evaluate_readiness_gate(
        _readiness(
            missing_runtime_bindings=("mail:send@1",),
            blockers=("missing_runtime_binding:mail:send@1",),
        )
    )

    assert result.passed is False
    assert "missing_runtime_binding:mail:send@1" in result.reasons


def test_gate_fails_when_recoverability_is_below_policy_threshold() -> None:
    result = evaluate_readiness_gate(
        _readiness(total_actions=4, structurally_recoverable=3),
        minimum_recoverability_fraction=1.0,
        allow_irreversible=True,
    )

    assert result.passed is False
    assert "recoverability_below_threshold:0.750000<1.000000" in result.reasons


def test_irreversible_actions_require_explicit_policy_opt_in() -> None:
    readiness = _readiness(
        total_actions=2,
        structurally_recoverable=1,
        reversible=1,
        compensatable=0,
        irreversible=1,
    )

    denied = evaluate_readiness_gate(readiness, minimum_recoverability_fraction=0.5)
    allowed = evaluate_readiness_gate(
        readiness,
        minimum_recoverability_fraction=0.5,
        allow_irreversible=True,
    )

    assert denied.passed is False
    assert "irreversible_actions:1" in denied.reasons
    assert allowed.passed is True


def test_gate_rejects_invalid_threshold() -> None:
    try:
        evaluate_readiness_gate(_readiness(), minimum_recoverability_fraction=1.1)
    except ValueError as exc:
        assert str(exc) == "minimum_recoverability_fraction must be between 0 and 1"
    else:
        raise AssertionError("invalid threshold must fail closed")
