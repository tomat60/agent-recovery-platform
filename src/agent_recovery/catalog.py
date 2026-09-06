from __future__ import annotations

from collections.abc import Mapping

from .contracts import RecoveryClass, RecoveryContract, RiskLevel
from .simulator import SyntheticEnterprise


def synthetic_contracts() -> tuple[RecoveryContract, ...]:
    return (
        RecoveryContract(
            tool_id="crm.update_contact",
            action_type="update",
            risk_level=RiskLevel.MEDIUM,
            recovery_class=RecoveryClass.REVERSIBLE,
            executor=lambda state, params: _enterprise(state).update_contact(params),
            verifier=lambda state, params: _enterprise(state).get_contact(params),
            recovery_executor=lambda state, params: _enterprise(state).restore_contact(params),
            recovery_params_builder=_restore_contact_params,
            recovery_window_seconds=86_400,
        ),
        RecoveryContract(
            tool_id="identity.grant_permission",
            action_type="permission_change",
            risk_level=RiskLevel.HIGH,
            recovery_class=RecoveryClass.COMPENSATABLE,
            executor=lambda state, params: _enterprise(state).grant_permission(params),
            verifier=lambda state, params: _enterprise(state).get_permissions(params),
            recovery_executor=lambda state, params: _enterprise(state).revoke_permission(params),
            recovery_params_builder=_revoke_permission_params,
            approval_before_action=True,
            approval_before_recovery=False,
            recovery_window_seconds=3_600,
            containment_scopes=("tool", "agent", "identity"),
        ),
        RecoveryContract(
            tool_id="memory.write",
            action_type="memory_write",
            risk_level=RiskLevel.MEDIUM,
            recovery_class=RecoveryClass.REVERSIBLE,
            executor=lambda state, params: _enterprise(state).write_memory(params),
            verifier=lambda state, params: _enterprise(state).get_memory(params),
            recovery_executor=lambda state, params: _enterprise(state).restore_memory(params),
            recovery_params_builder=_restore_memory_params,
            containment_scopes=("tool", "agent", "memory"),
        ),
        RecoveryContract(
            tool_id="comms.send_message",
            action_type="external_communication",
            risk_level=RiskLevel.HIGH,
            recovery_class=RecoveryClass.IRREVERSIBLE,
            executor=lambda state, params: _enterprise(state).send_message(params),
            verifier=lambda state, params: _verify_message(state, params),
            approval_before_action=True,
            containment_scopes=("tool", "agent", "identity"),
        ),
    )


def _enterprise(state: object) -> SyntheticEnterprise:
    if not isinstance(state, SyntheticEnterprise):
        raise TypeError("synthetic contract used with incompatible state")
    return state


def _restore_contact_params(
    execution_result: object,
    observed_after: object,
    original_params: Mapping[str, object],
) -> Mapping[str, object]:
    if not isinstance(execution_result, Mapping) or "before" not in execution_result:
        raise TypeError("contact update did not preserve before state")
    return {
        "contact_id": original_params["contact_id"],
        "previous": execution_result["before"],
    }


def _revoke_permission_params(
    execution_result: object,
    observed_after: object,
    original_params: Mapping[str, object],
) -> Mapping[str, object]:
    return {
        "principal": original_params["principal"],
        "permission": original_params["permission"],
    }


def _restore_memory_params(
    execution_result: object,
    observed_after: object,
    original_params: Mapping[str, object],
) -> Mapping[str, object]:
    if not isinstance(execution_result, Mapping):
        raise TypeError("memory write did not preserve before state")
    return {
        "key": original_params["key"],
        "previous": execution_result.get("before"),
    }


def _verify_message(state: object, params: Mapping[str, object]) -> object:
    enterprise = _enterprise(state)
    if "message_index" in params:
        return enterprise.get_message(params)
    if not enterprise.messages:
        return None
    return enterprise.messages[-1]
