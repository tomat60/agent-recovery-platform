import pytest

from agent_recovery.contracts import RecoveryClass as RuntimeRecoveryClass
from agent_recovery.contracts import RecoveryContract as RuntimeRecoveryContract
from agent_recovery.contracts import RiskLevel as RuntimeRiskLevel
from agent_recovery.recovery_contract import parse_recovery_contract
from agent_recovery.runtime_binding import (
    RuntimeBindingError,
    TrustedRuntimeBinding,
    bind_recovery_contract,
)


def _declaration():
    return parse_recovery_contract(
        {
            "version": "1",
            "tool_id": "contacts",
            "action_id": "contact.update",
            "risk_level": "high",
            "recovery_class": "reversible",
            "recovery_operation": "restore_contact",
            "verification_operation": "verify_contact",
            "parameter_binding": "sha256:parameters",
            "context_binding": "sha256:authority-scope",
            "action_approval_required": True,
            "recovery_approval_required": True,
            "parameter_bound_approval_required": True,
            "containment_scopes": ["tool", "session"],
            "recovery_window_seconds": 900,
            "reconciliation_operation": "reconcile_contact",
            "resource_key_operation": "contact_resource_key",
            "side_effects": ["crm_record_write"],
        }
    )


def _runtime(*, risk_level=RuntimeRiskLevel.HIGH):
    return RuntimeRecoveryContract(
        tool_id="contacts",
        action_type="contact.update",
        risk_level=risk_level,
        recovery_class=RuntimeRecoveryClass.REVERSIBLE,
        executor=lambda state, params: None,
        verifier=lambda state, params: None,
        recovery_executor=lambda state, params: None,
        recovery_params_builder=lambda result, observed, params: params,
        reconciliation_executor=lambda state, params: None,
        reconciliation_params_builder=lambda observed, params: params,
        resource_key_builder=lambda params: ("contact:42",),
        approval_before_action=True,
        approval_before_recovery=True,
        parameter_bound_approval=True,
        containment_scopes=("tool", "session"),
        recovery_window_seconds=900,
        contract_version="1",
    )


def _binding(runtime=None, **overrides):
    values = {
        "runtime_contract": runtime or _runtime(),
        "verification_operation": "verify_contact",
        "parameter_binding": "sha256:parameters",
        "context_binding": "sha256:authority-scope",
        "recovery_operation": "restore_contact",
        "reconciliation_operation": "reconcile_contact",
        "resource_key_operation": "contact_resource_key",
    }
    values.update(overrides)
    return TrustedRuntimeBinding(**values)


def test_trusted_binding_returns_only_the_supplied_runtime_contract():
    runtime = _runtime()
    bound = bind_recovery_contract(_declaration(), _binding(runtime))

    assert bound is runtime


def test_binding_fails_closed_on_policy_metadata_mismatch():
    with pytest.raises(RuntimeBindingError, match="metadata mismatch"):
        bind_recovery_contract(
            _declaration(),
            _binding(_runtime(risk_level=RuntimeRiskLevel.MEDIUM)),
        )


def test_binding_fails_closed_on_operation_identifier_mismatch():
    with pytest.raises(RuntimeBindingError, match="recovery operation mismatch"):
        bind_recovery_contract(
            _declaration(),
            _binding(recovery_operation="other_restore"),
        )


def test_binding_fails_closed_on_parameter_or_context_binding_mismatch():
    with pytest.raises(RuntimeBindingError, match="parameter binding mismatch"):
        bind_recovery_contract(
            _declaration(),
            _binding(parameter_binding="sha256:other-parameters"),
        )

    with pytest.raises(RuntimeBindingError, match="context binding mismatch"):
        bind_recovery_contract(
            _declaration(),
            _binding(context_binding="sha256:other-authority-scope"),
        )


def test_binding_requires_runtime_capability_for_declared_reconciliation():
    runtime = RuntimeRecoveryContract(
        tool_id="contacts",
        action_type="contact.update",
        risk_level=RuntimeRiskLevel.HIGH,
        recovery_class=RuntimeRecoveryClass.REVERSIBLE,
        executor=lambda state, params: None,
        verifier=lambda state, params: None,
        recovery_executor=lambda state, params: None,
        recovery_params_builder=lambda result, observed, params: params,
        resource_key_builder=lambda params: ("contact:42",),
        approval_before_action=True,
        approval_before_recovery=True,
        parameter_bound_approval=True,
        containment_scopes=("tool", "session"),
        recovery_window_seconds=900,
        contract_version="1",
    )

    with pytest.raises(RuntimeBindingError, match="reconciliation binding is incomplete"):
        bind_recovery_contract(_declaration(), _binding(runtime))
