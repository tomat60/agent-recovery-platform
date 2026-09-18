from __future__ import annotations

from agent_recovery.contracts import RecoveryClass as RuntimeRecoveryClass
from agent_recovery.contracts import RecoveryContract as RuntimeRecoveryContract
from agent_recovery.contracts import RiskLevel
from agent_recovery.operator_api import recovery_readiness_response
from agent_recovery.recovery_contract import parse_recovery_contract


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
        contract_version="1",
    )


def test_operator_readiness_response_is_deterministic_and_non_authorizing():
    payload = recovery_readiness_response(
        (_declaration(),),
        runtime_bindings={("contacts", "contact.update", "1"): _runtime()},
    )

    assert payload == {
        "total_actions": 1,
        "structurally_recoverable": 1,
        "reversible": 1,
        "compensatable": 0,
        "irreversible": 0,
        "missing_runtime_bindings": (),
        "blockers": (),
        "recoverability_fraction": 1.0,
        "ready": True,
        "authority": "none",
    }
    assert all("executor" not in key and "binding" not in key for key in payload)


def test_operator_readiness_response_exposes_blocker_without_runtime_authority():
    payload = recovery_readiness_response((_declaration(),), runtime_bindings={})

    assert payload["ready"] is False
    assert payload["authority"] == "none"
    assert payload["missing_runtime_bindings"] == ("contacts:contact.update@1",)
    assert payload["blockers"] == ("missing_runtime_binding:contacts:contact.update@1",)
