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


class InvestigatorRuntimeError(ValueError):
    """Raised when investigator output cannot be safely bound to incident evidence."""


@dataclass(frozen=True)
class InvestigatorResult:
    proposal: AgentProposal
    raw_response: str


_SYSTEM_PROMPT = """You are a read-only incident investigator.
You may analyze only the supplied incident evidence. You have no authority to execute tools,
restore authority, approve actions, mutate state, or declare an incident recovered.
Return JSON only with keys summary and evidence_event_ids. evidence_event_ids must contain only
ledger event IDs from the supplied incident. State uncertainty in summary rather than inventing facts.
"""


def _prompt_for(view: EvidenceView) -> str:
    payload = view.as_prompt_payload()
    return (
        "Investigate the causal trajectory and most likely root cause from this evidence only. "
        "Do not propose or execute recovery actions.\nEVIDENCE_JSON:\n"
        + json.dumps(payload, sort_keys=True, separators=(",", ":"))
    )


def _default_invoke(prompt: str, *, model: Any = None) -> str:
    try:
        from strands import Agent
    except ImportError as exc:  # pragma: no cover - exercised only with optional dependency absent
        raise InvestigatorRuntimeError(
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


def run_strands_investigator(
    view: EvidenceView,
    *,
    invoke: Callable[[str], str] | None = None,
    model: Any = None,
) -> InvestigatorResult:
    """Run read-only investigation and deterministically bind its claims to ledger evidence.

    CI can inject ``invoke`` and therefore never requires credentials or paid model calls. The live
    path lazily imports Strands and gives the agent no tools. Model output is analysis only; the
    deterministic boundary remains responsible for incident/evidence binding.
    """

    if invoke is not None and model is not None:
        raise InvestigatorRuntimeError("model cannot be supplied with an injected investigator")

    prompt = _prompt_for(view)
    raw = invoke(prompt) if invoke is not None else _default_invoke(prompt, model=model)
    if not isinstance(raw, str) or not raw.strip():
        raise InvestigatorRuntimeError("investigator returned an empty response")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InvestigatorRuntimeError("investigator response must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise InvestigatorRuntimeError("investigator response must be a JSON object")

    summary = parsed.get("summary")
    evidence_ids = parsed.get("evidence_event_ids")
    if not isinstance(summary, str):
        raise InvestigatorRuntimeError("investigator summary must be a string")
    if not isinstance(evidence_ids, list) or not all(isinstance(item, str) for item in evidence_ids):
        raise InvestigatorRuntimeError("evidence_event_ids must be a list of strings")

    try:
        proposal = bind_agent_proposal(
            view,
            role="investigator",
            summary=summary,
            evidence_event_ids=tuple(evidence_ids),
        )
    except InvestigationBoundaryError as exc:
        raise InvestigatorRuntimeError(str(exc)) from exc

    return InvestigatorResult(proposal=proposal, raw_response=raw)
