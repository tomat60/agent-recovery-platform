from __future__ import annotations

import json

from agent_recovery.authority_resurrection_benchmark import (
    run_authority_resurrection_scenario,
)
from agent_recovery.benchmark import run_vertical_slice
from agent_recovery.multi_agent_benchmark import run_multi_agent_recovery_scenario
from agent_recovery.partial_failure_benchmark import (
    run_partial_compensation_failure_scenario,
)
from agent_recovery.runaway_loop_benchmark import run_runaway_loop_scenario


def main() -> None:
    payload = {
        "single_action_vertical_slice": [score.to_dict() for score in run_vertical_slice()],
        "multi_agent_verified_restoration": run_multi_agent_recovery_scenario().to_dict(),
        "partial_compensation_failure": run_partial_compensation_failure_scenario().to_dict(),
        "authority_resurrection_replay_attempt": run_authority_resurrection_scenario().to_dict(),
        "runaway_tool_loop_containment": run_runaway_loop_scenario().to_dict(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
