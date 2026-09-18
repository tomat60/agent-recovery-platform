from __future__ import annotations

import pytest

from agent_recovery.contracts import RecoveryClass, RecoveryContract, RiskLevel
from agent_recovery.engine import digest_params
from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.restart import RestartRecoveryError, reconstruct_recovery_context


def _contract(version: str = "1") -> RecoveryContract:
    return RecoveryContract(
        tool_id="store.write",
        action_type="write",
        risk_level=RiskLevel.MEDIUM,
        recovery_class=RecoveryClass.REVERSIBLE,
        executor=lambda state, params: None,
        verifier=lambda state, params: None,
        recovery_executor=lambda state, params: None,
        recovery_params_builder=lambda result, observed, params: params,
        contract_version=version,
    )


def _executed(ledger: ActionLedger, *, version: str = "1"):
    params = {"key": "record:1", "value": "bad"}
    return ledger.record(
        EventType.ACTION_EXECUTED,
        "incident-1",
        {
            "agent_id": "agent-1",
            "tool_id": "store.write",
            "contract_version": version,
            "recovery_class": "reversible",
            "resource_keys": ("record:1",),
            "params": params,
            "params_digest": digest_params(params),
            "execution_result": {"previous": "good"},
            "observed_state": "bad",
            "outcome_uncertain": False,
        },
    )


def test_restart_reconstructs_only_from_integrity_checked_exact_runtime_binding():
    ledger = ActionLedger()
    action = _executed(ledger)
    contract = _contract()

    context = reconstruct_recovery_context(
        ledger,
        action_event_id=action.event_id,
        runtime_contracts={contract.tool_id: contract},
    )

    assert context.incident_id == "incident-1"
    assert context.params == {"key": "record:1", "value": "bad"}
    assert context.execution_result == {"previous": "good"}
    assert context.contract is contract


def test_restart_fails_closed_on_contract_version_mismatch():
    ledger = ActionLedger()
    action = _executed(ledger, version="1")

    with pytest.raises(RestartRecoveryError, match="version mismatch"):
        reconstruct_recovery_context(
            ledger,
            action_event_id=action.event_id,
            runtime_contracts={"store.write": _contract("2")},
        )


def test_restart_fails_closed_on_mismatched_parameter_evidence():
    ledger = ActionLedger()
    params = {"key": "record:1", "value": "bad"}
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "incident-1",
        {
            "agent_id": "agent-1",
            "tool_id": "store.write",
            "contract_version": "1",
            "recovery_class": "reversible",
            "resource_keys": ("record:1",),
            "params": params,
            "params_digest": "stale-digest",
            "execution_result": {"previous": "good"},
            "observed_state": "bad",
            "outcome_uncertain": False,
        },
    )

    with pytest.raises(RestartRecoveryError, match="stale or mismatched"):
        reconstruct_recovery_context(
            ledger,
            action_event_id=action.event_id,
            runtime_contracts={"store.write": _contract()},
        )


def test_restart_does_not_reconstruct_verified_recovery_for_second_compensation():
    ledger = ActionLedger()
    action = _executed(ledger)
    recovered = ledger.record(
        EventType.RECOVERY_EXECUTED,
        "incident-1",
        {"action_event_id": action.event_id, "tool_id": "store.write"},
        parent_event_ids=(action.event_id,),
    )
    ledger.record(
        EventType.VERIFICATION,
        "incident-1",
        {"action_event_id": action.event_id, "verified": True},
        parent_event_ids=(recovered.event_id,),
    )

    with pytest.raises(RestartRecoveryError, match="verified terminal recovery"):
        reconstruct_recovery_context(
            ledger,
            action_event_id=action.event_id,
            runtime_contracts={"store.write": _contract()},
        )


def test_restart_fails_closed_when_recovery_execution_has_no_terminal_verification():
    ledger = ActionLedger()
    action = _executed(ledger)
    ledger.record(
        EventType.RECOVERY_EXECUTED,
        "incident-1",
        {"action_event_id": action.event_id, "tool_id": "store.write"},
        parent_event_ids=(action.event_id,),
    )

    with pytest.raises(RestartRecoveryError, match="ambiguous"):
        reconstruct_recovery_context(
            ledger,
            action_event_id=action.event_id,
            runtime_contracts={"store.write": _contract()},
        )


def test_restart_fails_closed_on_later_writer_to_same_resource():
    ledger = ActionLedger()
    action = _executed(ledger)
    later_params = {"key": "record:1", "value": "newer"}
    ledger.record(
        EventType.ACTION_EXECUTED,
        "incident-1",
        {
            "agent_id": "agent-2",
            "tool_id": "store.write",
            "contract_version": "1",
            "recovery_class": "reversible",
            "resource_keys": ("record:1",),
            "params": later_params,
            "params_digest": digest_params(later_params),
            "execution_result": {"previous": "bad"},
            "observed_state": "newer",
            "outcome_uncertain": False,
        },
    )

    with pytest.raises(RestartRecoveryError, match="later resource writer"):
        reconstruct_recovery_context(
            ledger,
            action_event_id=action.event_id,
            runtime_contracts={"store.write": _contract()},
        )


def test_restart_never_turns_irreversible_evidence_into_undo_path():
    ledger = ActionLedger()
    params = {"key": "record:1"}
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "incident-1",
        {
            "tool_id": "store.write",
            "contract_version": "1",
            "recovery_class": "irreversible",
            "resource_keys": ("record:1",),
            "params": params,
            "params_digest": digest_params(params),
            "execution_result": None,
            "observed_state": None,
            "outcome_uncertain": False,
        },
    )
    irreversible = RecoveryContract(
        tool_id="store.write",
        action_type="write",
        risk_level=RiskLevel.MEDIUM,
        recovery_class=RecoveryClass.IRREVERSIBLE,
        executor=lambda state, params: None,
        verifier=lambda state, params: None,
        contract_version="1",
    )

    with pytest.raises(RestartRecoveryError, match="no restart undo path"):
        reconstruct_recovery_context(
            ledger,
            action_event_id=action.event_id,
            runtime_contracts={"store.write": irreversible},
        )
