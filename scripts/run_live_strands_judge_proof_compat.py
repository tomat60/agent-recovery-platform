from __future__ import annotations

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


class _SkepticChallengeOutput(_StrictModel):
    claim_id: str
    verdict: Literal["supported", "rejected", "uncertain"]
    reason: str
    evidence_event_ids: list[str]


class _SkepticOutput(_StrictModel):
    summary: str
    evidence_event_ids: list[str]
    challenges: list[_SkepticChallengeOutput]


def _structured_invoke(output_model: type[_StrictModel]):
    def invoke(prompt: str, *, model: Any = None) -> str:
        try:
            from strands import Agent
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Strands SDK is not installed; install the 'agent' optional dependency"
            ) from exc

        kwargs: dict[str, Any] = {
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


strands_investigator._default_invoke = _structured_invoke(_InvestigatorOutput)
strands_recovery_planner._default_invoke = _structured_invoke(_PlannerOutput)
strands_skeptic._default_invoke = _structured_invoke(_SkepticOutput)

runpy.run_path("scripts/run_live_strands_judge_proof.py", run_name="__main__")
