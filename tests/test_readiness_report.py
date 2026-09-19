from __future__ import annotations

import pytest

from agent_recovery.contracts import RecoveryClass as RuntimeRecoveryClass
from agent_recovery.contracts import RecoveryContract as RuntimeRecoveryContract
from agent_recovery.contracts import RiskLevel as RuntimeRiskLevel
from agent_recovery.readiness_report import assert_recovery_ready, recovery_readiness_report
from agent_recovery.recovery_contract import RecoveryClass, RecoveryContract
from agent_recovery.runtime_binding import TrustedRuntimeBinding


def _executor(state, params):
    return None


def _verifier(state, params):
    return True


def _recovery_builder(before, after, params):
    return {}


def _declaration() -> RecoveryContract:
    return RecoveryContract(
        version="1",
        tool_id="crm",
        action_id="update_contact",
        recovery_class=RecoveryClass.REVERSIBLE,
        recovery_operation="restore_contact",
        verification_operation="verify_contact",
        parameter_binding="contact_id",
        context_binding="tenant_id",
    )


def _binding() -> TrustedRuntimeBinding:
    runtime = RuntimeRecoveryContract(
        tool_id="crm",
        action_type="update_contact",
        risk_level=RuntimeRiskLevel.MEDIUM,
        recovery_class=RuntimeRecoveryClass.REVERSIBLE,
        executor=_executor,
        verifier=_verifier,
        recovery_executor=_executor,
        recovery_params_builder=_recovery_builder,
        contract_version="1",
    )
    return TrustedRuntimeBinding(
        runtime_contract=runtime,
        verification_operation="verify_contact",
        parameter_binding="contact_id",
        context_binding="tenant_id",
        recovery_operation="restore_contact",
    )


def test_readiness_report_exposes_coverage_without_runtime_authority():
    declaration = _declaration()
    identity = (declaration.tool_id, declaration.action_id, declaration.version)

    report = recovery_readiness_report(
        [declaration],
        runtime_bindings={identity: _binding()},
    )

    assert report["ready"] is True
    assert report["recoverability_fraction"] == 1.0
    assert report["blockers"] == ()
    assert report["authority"] == "none"
    assert "runtime_bindings" not in report


def test_readiness_ci_gate_fails_closed_on_missing_trusted_binding():
    declaration = _declaration()

    report = recovery_readiness_report([declaration], runtime_bindings={})
    assert report["ready"] is False
    assert report["missing_runtime_bindings"] == ("crm:update_contact@1",)
    assert report["blockers"] == ("missing_runtime_binding:crm:update_contact@1",)

    with pytest.raises(RuntimeError, match="missing_runtime_binding:crm:update_contact@1"):
        assert_recovery_ready([declaration], runtime_bindings={})
