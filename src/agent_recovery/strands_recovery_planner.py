from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .investigation import (
    AgentProposal,
    EvidenceView,
    InvestigationBoundaryError,
    bind_agent_proposal,
)


class RecoveryPlannerRuntimeError(ValueError):
    """Raised when planner output cannot be safely bound to incident evidence."""


@dataclass(frozen=True)
class ProposedRecoveryStep:
    step_id: str
    description: str
    evidence_event_ids: tuple[str, ...]
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecoveryPlannerResult:
    proposal: AgentProposal
    steps: tuple[ProposedRecoveryStep, ...]
    residual_risks: tuple[str, ...]
    raw_response: str


_SYSTEM_PROMPT = """You are a read-only recovery planner.
You may propose recovery steps only from the supplied incident evidence. You have no authority to
execute tools, approve actions, restore authority, mutate state, or declare an incident recovered.
Return JSON only with keys summary, evidence_event_ids, steps, and residual_risks. Each step must
contain exactly step_id, description, evidence_event_ids, and depends_on. depends_on may reference
only earlier step IDs. Cite only ledger event IDs from the supplied incident. Keep irreversible or
unverified external effects explicit in residual_risks. State uncertainty instead of inventing facts.
"""


def _prompt_for(view: EvidenceView) -> str:
    payload = view.as_prompt_payload()
    return (
        "Propose an ordered, dependency-aware recovery plan from this evidence only. "
        "Do not execute anything and do not claim authorization or successful recovery.\n"
        "EVIDENCE_JSON:\n"
        + json.dumps(payload, sort_keys=True, separators=(",", ":"))
    )


def _default_invoke(prompt: str, *, model: Any = None) -> str:
    try:
        from strands import Agent
    except ImportError as exc:  # pragma: no cover
        raise RecoveryPlannerRuntimeError(
            "Strands SDK is not installed; install the 'agent' optional dependency"
        ) from exc

    kwargs: dict[str, Any] = {
        "system_prompt": _SYSTEM_PROMPT,
        "tools": [],
        "callback_handler": None,
    }
    if model is not None:
        kwargs["model"] = model
    agent = Agent(**kwargs)
    return str(agent(prompt))


def _require_string_list(value: Any, *, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise RecoveryPlannerRuntimeError(f"{field} must be a list of strings")
    return value


def _bind_step(
    view: EvidenceView,
    raw_step: Any,
    *,
    known_step_ids: set[str],
) -> ProposedRecoveryStep:
    if not isinstance(raw_step, dict):
        raise RecoveryPlannerRuntimeError("each recovery step must be a JSON object")
    expected = {"step_id", "description", "evidence_event_ids", "depends_on"}
    if set(raw_step) != expected:
        raise RecoveryPlannerRuntimeError("recovery step has unsupported or missing fields")

    step_id = raw_step["step_id"]
    description = raw_step["description"]
    if not isinstance(step_id, str) or not step_id.strip():
        raise RecoveryPlannerRuntimeError("recovery step_id is required")
    if step_id in known_step_ids:
        raise RecoveryPlannerRuntimeError("recovery step_id must be unique")
    if not isinstance(description, str) or not description.strip():
        raise RecoveryPlannerRuntimeError("recovery step description is required")

    evidence_ids = _require_string_list(
        raw_step["evidence_event_ids"], field="step evidence_event_ids"
    )
    depends_on = _require_string_list(raw_step["depends_on"], field="step depends_on")
    if not evidence_ids:
        raise RecoveryPlannerRuntimeError("each recovery step must cite ledger evidence")
    unknown_dependencies = sorted(set(depends_on) - known_step_ids)
    if unknown_dependencies:
        raise RecoveryPlannerRuntimeError(
            f"step dependencies must reference earlier steps: {unknown_dependencies}"
        )

    try:
        bound = bind_agent_proposal(
            view,
            role="recovery_planner",
            summary=description,
            evidence_event_ids=tuple(evidence_ids),
        )
    except InvestigationBoundaryError as exc:
        raise RecoveryPlannerRuntimeError(str(exc)) from exc

    known_step_ids.add(step_id)
    return ProposedRecoveryStep(
        step_id=step_id,
        description=bound.summary,
        evidence_event_ids=bound.evidence_event_ids,
        depends_on=tuple(dict.fromkeys(depends_on)),
    )


def run_strands_recovery_planner(
    view: EvidenceView,
    *,
    invoke: Callable[[str], str] | None = None,
    model: Any = None,
) -> RecoveryPlannerResult:
    """Run advisory recovery planning while keeping execution authority deterministic."""

    if invoke is not None and model is not None:
        raise RecoveryPlannerRuntimeError("model cannot be supplied with an injected planner")

    prompt = _prompt_for(view)
    raw = invoke(prompt) if invoke is not None else _default_invoke(prompt, model=model)
    if not isinstance(raw, str) or not raw.strip():
        raise RecoveryPlannerRuntimeError("recovery planner returned an empty response")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RecoveryPlannerRuntimeError("recovery planner response must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise RecoveryPlannerRuntimeError("recovery planner response must be a JSON object")

    expected = {"summary", "evidence_event_ids", "steps", "residual_risks"}
    if set(parsed) != expected:
        raise RecoveryPlannerRuntimeError("recovery planner has unsupported or missing fields")

    summary = parsed["summary"]
    if not isinstance(summary, str):
        raise RecoveryPlannerRuntimeError("recovery planner summary must be a string")
    evidence_ids = _require_string_list(
        parsed["evidence_event_ids"], field="evidence_event_ids"
    )
    residual_risks = _require_string_list(parsed["residual_risks"], field="residual_risks")
    raw_steps = parsed["steps"]
    if not isinstance(raw_steps, list) or not raw_steps:
        raise RecoveryPlannerRuntimeError("recovery planner must propose at least one step")

    try:
        proposal = bind_agent_proposal(
            view,
            role="recovery_planner",
            summary=summary,
            evidence_event_ids=tuple(evidence_ids),
        )
    except InvestigationBoundaryError as exc:
        raise RecoveryPlannerRuntimeError(str(exc)) from exc

    known_step_ids: set[str] = set()
    steps = tuple(
        _bind_step(view, step, known_step_ids=known_step_ids) for step in raw_steps
    )

    return RecoveryPlannerResult(
        proposal=proposal,
        steps=steps,
        residual_risks=tuple(item.strip() for item in residual_risks if item.strip()),
        raw_response=raw,
    )
