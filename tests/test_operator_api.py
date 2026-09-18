from __future__ import annotations

from agent_recovery.contracts import RecoveryClass as RuntimeRecoveryClass
from agent_recovery.contracts import RecoveryContract as RuntimeRecoveryContract
from agent_recovery.contracts import RiskLevel
from agent_recovery.operator_api import recovery_readiness_response
from agent_recovery.recovery_contract import parse_recovery_contract
from agent_recovery.runtime_binding import TrustedRuntimeBinding


def _declaration():
    return parse_recovery_contract(
        {
            "version": "1",
            "tool_id": "contacts",
            "action_id": "contact.update",
            "recovery_class": "reversible",
            "recovery_operation": "restore_contact",
            "verification_operation": "verify_contact",
            "parameter_binding": "sha256:parameters",
            "context_binding": "sha256:authority-scope",
            "containment_scopes": ["tool", "session"],
        }
    )


def _runtime():
    return RuntimeRecoveryContract(
        tool_id="contacts",
        action_type="contact.update",
        risk_level=RiskLevel.MEDIUM,
        recovery_class=RuntimeRecoveryClass.REVERSIBLE,
        executor=lambda state, params: None,
        verifier=lambda state, params: None,
        recovery_executor=lambda state, params: None,
        recovery_params_builder=lambda result, observed, params: params,
        containment_scopes=("tool", "session"),
        contract_version="1",
    )


def _binding():
    return TrustedRuntimeBinding(
        runtime_contract=_runtime(),
        verification_operation="verify_contact",
        parameter_binding="sha256:parameters",
        context_binding="sha256:authority-scope",
        recovery_operation="restore_contact",
    )


def test_operator_readiness_response_is_deterministic_and_non_authorizing():
    payload = recovery_readiness_response(
        (_declaration(),),
        runtime_bindings={("contacts", "contact.update", "1"): _binding()},
    )

    assert payload == {
        "total_actions": 1,
        "structurally_recoverable": 1,
        "reversible": 1,
        "compensatable": 0,
        "irreversible": 0,
        "human_approval_required": 0,
        "missing_runtime_bindings": (),
        "blockers": (),
        "recoverability_fraction": 1.0,
        "ready": True,
        "authority": "none",
    }
    forbidden_runtime_keys = {
        "executor",
        "verifier",
        "recovery_executor",
        "recovery_params_builder",
        "runtime_bindings",
    }
    assert forbidden_runtime_keys.isdisjoint(payload)
    assert all(not callable(value) for value in payload.values())


def test_operator_readiness_response_exposes_blocker_without_runtime_authority():
    payload = recovery_readiness_response((_declaration(),), runtime_bindings={})

    assert payload["ready"] is False
    assert payload["authority"] == "none"
    assert payload["missing_runtime_bindings"] == ("contacts:contact.update@1",)
    assert payload["blockers"] == ("missing_runtime_binding:contacts:contact.update@1",)
