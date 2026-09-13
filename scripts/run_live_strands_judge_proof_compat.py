from __future__ import annotations

import json
import runpy
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from agent_recovery import strands_investigator
from agent_recovery import strands_recovery_planner
from agent_recovery import strands_skeptic


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _InvestigatorOutput(_StrictModel):
    summary: str
    evidence_event_ids: list[str]


class _RecoveryStepOutput(_StrictModel):
    step_id: str
    description: str
    evidence_event_ids: list[str]
    depends_on: list[str]


class _PlannerOutput(_StrictModel):
    summary: str
    evidence_event_ids: list[str]
    steps: list[_RecoveryStepOutput] = Field(min_length=1)
    residual_risks: list[str]


class _ChallengeBody(_StrictModel):
    verdict: Literal["supported", "rejected", "uncertain"]
    reason: str
    evidence_event_ids: list[str]


class _SkepticStructuredOutput(_StrictModel):
    summary: str
    evidence_event_ids: list[str]
    investigator_challenge: _ChallengeBody
    recovery_plan_challenge: _ChallengeBody


def _structured_invoke(output_model: type[_StrictModel], *, system_prompt: str):
    def invoke(prompt: str, *, model: Any = None) -> str:
        try:
            from strands import Agent
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Strands SDK is not installed; install the 'agent' optional dependency"
            ) from exc

        kwargs: dict[str, Any] = {
            "system_prompt": system_prompt,
            "tools": [],
            "callback_handler": None,
        }
        if model is not None:
            kwargs["model"] = model

        agent = Agent(**kwargs)
        result = agent(prompt, structured_output_model=output_model)
        structured = result.structured_output
        if structured is None:
            raise RuntimeError("Strands returned no structured output")
        return structured.model_dump_json()

    return invoke


def _skeptic_structured_invoke(prompt: str, *, model: Any = None) -> str:
    try:
        from strands import Agent
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Strands SDK is not installed; install the 'agent' optional dependency"
        ) from exc

    structured_prompt = (
        strands_skeptic._SYSTEM_PROMPT
        + "\nFor this live structured-output adapter, return two dedicated challenge objects: "
        "investigator_challenge for claim_id 'investigator' and recovery_plan_challenge for "
        "claim_id 'recovery-plan'. Do not merge, omit, or duplicate them."
    )
    kwargs: dict[str, Any] = {
        "system_prompt": structured_prompt,
        "tools": [],
        "callback_handler": None,
    }
    if model is not None:
        kwargs["model"] = model

    agent = Agent(**kwargs)
    result = agent(prompt, structured_output_model=_SkepticStructuredOutput)
    structured = result.structured_output
    if structured is None:
        raise RuntimeError("Strands returned no structured skeptic output")

    payload = {
        "summary": structured.summary,
        "evidence_event_ids": structured.evidence_event_ids,
        "challenges": [
            {
                "claim_id": "investigator",
                **structured.investigator_challenge.model_dump(),
            },
            {
                "claim_id": "recovery-plan",
                **structured.recovery_plan_challenge.model_dump(),
            },
        ],
    }
    return json.dumps(payload, separators=(",", ":"))


strands_investigator._default_invoke = _structured_invoke(
    _InvestigatorOutput,
    system_prompt=strands_investigator._SYSTEM_PROMPT,
)
strands_recovery_planner._default_invoke = _structured_invoke(
    _PlannerOutput,
    system_prompt=strands_recovery_planner._SYSTEM_PROMPT,
)
strands_skeptic._default_invoke = _skeptic_structured_invoke

runpy.run_path("scripts/run_live_strands_judge_proof.py", run_name="__main__")
