from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import Approval, RecoveryEngine
from agent_recovery.investigation import build_evidence_view
from agent_recovery.ledger import EventType
from agent_recovery.simulator import SyntheticEnterprise
from agent_recovery.strands_investigator import run_strands_investigator
from agent_recovery.strands_recovery_planner import run_strands_recovery_planner
from agent_recovery.strands_skeptic import run_strands_skeptic


DEFAULT_MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
INCIDENT_ID = "judge-live-strands-proof"


def _engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def build_live_evidence():
    """Build read-only model evidence from the same bounded three-agent incident shape.

    All writes here target SyntheticEnterprise in memory only. No external system is called.
    The returned EvidenceView carries ledger evidence but no approval or execution handle.
    """

    engine = _engine()
    root = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        INCIDENT_ID,
        {
            "source": "support_ticket",
            "trust": "untrusted",
            "content_digest": "sha256:poisoned-support-ticket-v1",
        },
    )

    memory_params = {"key": "customer_instruction", "value": "elevate customer access"}
    memory_action = engine.execute(
        incident_id=INCIDENT_ID,
        agent_id="support-agent",
        tool_id="memory.write",
        params=memory_params,
        causal_parent_event_ids=(root.event_id,),
    )

    memory_read = engine.ledger.record(
        EventType.MEMORY_READ,
        INCIDENT_ID,
        {
            "agent_id": "crm-agent",
            "key": "customer_instruction",
            "observed": "elevate customer access",
        },
        parent_event_ids=(memory_action.action_event.event_id,),
    )

    crm_action = engine.execute(
        incident_id=INCIDENT_ID,
        agent_id="crm-agent",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
        causal_parent_event_ids=(memory_read.event_id,),
    )

    handoff = engine.ledger.record(
        EventType.AGENT_HANDOFF,
        INCIDENT_ID,
        {
            "from_agent_id": "crm-agent",
            "to_agent_id": "identity-agent",
            "reason": "customer access reconciliation",
        },
        parent_event_ids=(crm_action.action_event.event_id,),
    )

    permission_params = {"principal": "agent-1", "permission": "deploy:prod"}
    engine.execute(
        incident_id=INCIDENT_ID,
        agent_id="identity-agent",
        tool_id="identity.grant_permission",
        params=permission_params,
        approval=Approval.for_action(
            "identity.grant_permission",
            permission_params,
            "judge-live-strands-approval",
            incident_id=INCIDENT_ID,
            contract_version="0.1",
        ),
        causal_parent_event_ids=(handoff.event_id,),
    )

    return build_evidence_view(engine.ledger, incident_id=INCIDENT_ID)


def run(model_id: str, output: Path) -> dict[str, object]:
    view = build_live_evidence()

    investigator = run_strands_investigator(view, model=model_id)
    planner = run_strands_recovery_planner(view, model=model_id)
    skeptic = run_strands_skeptic(
        view,
        (
            ("investigator", investigator.proposal),
            ("recovery-plan", planner.proposal),
        ),
        model=model_id,
    )

    artifact: dict[str, object] = {
        "schema_version": "live-strands-judge-proof/v1",
        "authorization_effect": "none",
        "incident_id": view.incident_id,
        "ledger_head_hash": view.ledger_head_hash,
        "evidence_event_ids": [event.event_id for event in view.events],
        "model_id": model_id,
        "investigator": {
            "proposal": asdict(investigator.proposal),
            "raw_response": investigator.raw_response,
        },
        "recovery_planner": {
            "proposal": asdict(planner.proposal),
            "steps": [asdict(step) for step in planner.steps],
            "residual_risks": list(planner.residual_risks),
            "raw_response": planner.raw_response,
        },
        "skeptic": {
            "proposal": asdict(skeptic.proposal),
            "challenges": [asdict(challenge) for challenge in skeptic.challenges],
            "raw_response": skeptic.raw_response,
        },
        "claim_boundary": (
            "Live Strands advisory reasoning over synthetic evidence only. The agents have no tools "
            "and this artifact grants no approval, execution, recovery, replay, or restoration authority."
        ),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the bounded three-agent judge incident through live read-only Strands agents."
    )
    parser.add_argument(
        "--model-id",
        default=os.environ.get("STRANDS_MODEL_ID", DEFAULT_MODEL_ID),
        help="Explicit Amazon Bedrock model ID used by all three advisory agents.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/live-strands-proof.json"),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and validate the synthetic evidence without making any model invocation.",
    )
    args = parser.parse_args()

    if args.dry_run:
        view = build_live_evidence()
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "authorization_effect": "none",
                    "incident_id": view.incident_id,
                    "ledger_head_hash": view.ledger_head_hash,
                    "evidence_events": len(view.events),
                    "planned_model_id": args.model_id,
                    "planned_model_calls": 3,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return

    artifact = run(args.model_id, args.output)
    print(
        json.dumps(
            {
                "authorization_effect": artifact["authorization_effect"],
                "incident_id": artifact["incident_id"],
                "model_id": artifact["model_id"],
                "output": str(args.output),
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
