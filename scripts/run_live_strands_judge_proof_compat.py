from __future__ import annotations

import runpy
from collections.abc import Callable
from typing import Any

from agent_recovery import strands_investigator
from agent_recovery import strands_recovery_planner
from agent_recovery import strands_skeptic


def _normalize_model_json(raw: str) -> str:
    """Accept raw JSON or exactly one JSON markdown fence, and nothing else."""

    text = raw.strip()
    lines = text.splitlines()
    if (
        len(lines) >= 3
        and lines[0].strip().lower() in {"```", "```json"}
        and lines[-1].strip() == "```"
    ):
        return "\n".join(lines[1:-1]).strip()
    return text


def _wrap(module: Any) -> None:
    original: Callable[..., str] = module._default_invoke

    def invoke(prompt: str, *, model: Any = None) -> str:
        return _normalize_model_json(original(prompt, model=model))

    module._default_invoke = invoke


for target in (
    strands_investigator,
    strands_recovery_planner,
    strands_skeptic,
):
    _wrap(target)

runpy.run_path("scripts/run_live_strands_judge_proof.py", run_name="__main__")
