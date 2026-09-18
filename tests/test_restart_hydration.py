from __future__ import annotations

from agent_recovery.contracts import RecoveryClass, RecoveryContract, RiskLevel
from agent_recovery.engine import RecoveryEngine, RecoveryStatus, digest_params
from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.restart import hydrate_recovery_action


def test_hydrated_action_can_recover_after_controller_restart():
    state = {"value": "bad"}
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
            "params_digest": digest_params(params),
            "execution_result": {"before": "good"},
            "observed_state": "bad",
            "outcome_uncertain": False,
        },
    )

    def recover(current_state, recovery_params):
        current_state["value"] = recovery_params["value"]
        return current_state["value"]

    contract = RecoveryContract(
        tool_id="store.write",
        action_type="write",
        risk_level=RiskLevel.MEDIUM,
        recovery_class=RecoveryClass.REVERSIBLE,
        executor=lambda current_state, action_params: None,
        verifier=lambda current_state, verify_params: current_state["value"],
        recovery_executor=recover,
        recovery_params_builder=lambda result, observed, original: {"value": result["before"]},
        contract_version="1",
    )

    restarted = RecoveryEngine(state, ledger)
    hydrate_recovery_action(
        restarted,
        action_event_id=action.event_id,
        runtime_contracts={contract.tool_id: contract},
    )
    result = restarted.recover(incident_id="incident-1", action_event_id=action.event_id)

    assert result.status is RecoveryStatus.VERIFIED
    assert state["value"] == "good"
    assert result.verification_event is not None
    assert result.verification_event.payload["verified"] is True


def test_containment_remains_effective_on_restarted_engine():
    ledger = ActionLedger()
    ledger.record(
        EventType.CONTAINMENT,
        "incident-1",
        {"scope": "tool:store.write", "reason": "incident", "active": True},
    )

    restarted = RecoveryEngine({}, ledger)

    assert restarted.is_contained("tool:store.write") is True
