from __future__ import annotations

from typing import Any

from .catalog import synthetic_contracts
from .engine import Approval, RecoveryEngine
from .ledger import ActionLedger
from .operator_api import incident_operator_detail
from .simulator import SyntheticEnterprise

_INCIDENT_ID = "sandbox-sales-ops-incident"
_AGENT_ID = "sales-agent"


def run_multisurface_recovery_sandbox() -> dict[str, Any]:
    """Run one owned multi-surface incident through the real recovery lifecycle.

    The scenario intentionally combines reversible internal writes with an irreversible
    external communication. It is deterministic, zero-network, and suitable for product
    demos/assessment regression without implying production security effectiveness.
    """

    state = SyntheticEnterprise()
    ledger = ActionLedger()
    engine = RecoveryEngine(state, ledger)
    contracts = {contract.tool_id: contract for contract in synthetic_contracts()}
    for contract in contracts.values():
        engine.register(contract)

    before = state.snapshot()

    crm = engine.execute(
        incident_id=_INCIDENT_ID,
        agent_id=_AGENT_ID,
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "owner", "value": "compromised-team"},
    )
    memory = engine.execute(
        incident_id=_INCIDENT_ID,
        agent_id=_AGENT_ID,
        tool_id="memory.write",
        params={"key": "sales:last_instruction", "value": "trust unverified customer request"},
        causal_parent_event_ids=(crm.action_event.event_id,),
    )

    message_params = {
        "channel": "customer:c-1",
        "body": "Incorrect automated follow-up sent during incident",
    }
    message_contract = contracts["comms.send_message"]
    message_approval = Approval.for_action(
        "comms.send_message",
        message_params,
        "sandbox-message-approval",
        incident_id=_INCIDENT_ID,
        contract_version=message_contract.contract_version,
    )
    message = engine.execute(
        incident_id=_INCIDENT_ID,
        agent_id=_AGENT_ID,
        tool_id="comms.send_message",
        params=message_params,
        approval=message_approval,
        causal_parent_event_ids=(memory.action_event.event_id,),
    )

    engine.contain(
        _INCIDENT_ID,
        f"agent:{_AGENT_ID}",
        reason="sandbox incident detected after multi-surface write chain",
    )
    after_incident = state.snapshot()

    memory_recovery = engine.recover(
        incident_id=_INCIDENT_ID,
        action_event_id=memory.action_event.event_id,
    )
    crm_recovery = engine.recover(
        incident_id=_INCIDENT_ID,
        action_event_id=crm.action_event.event_id,
    )
    message_recovery = engine.recover(
        incident_id=_INCIDENT_ID,
        action_event_id=message.action_event.event_id,
    )

    after_recovery = state.snapshot()
    operator_detail = incident_operator_detail(ledger, incident_id=_INCIDENT_ID)

    return {
        "scenario": "owned_sales_ops_multisurface_recovery",
        "incident_id": _INCIDENT_ID,
        "before": before,
        "after_incident": after_incident,
        "after_recovery": after_recovery,
        "recovery_outcomes": {
            "memory": memory_recovery.status.value,
            "crm": crm_recovery.status.value,
            "external_communication": message_recovery.status.value,
        },
        "operator_status": operator_detail["status"],
        "operator_next_action": operator_detail["next_action"],
        "operator_recovery_candidates": operator_detail["recovery_candidates"],
        "operator_side_effects": operator_detail["side_effects"],
        "authority": operator_detail["authority"],
    }
