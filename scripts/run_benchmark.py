from __future__ import annotations

import json

from agent_recovery.benchmark import run_vertical_slice
from agent_recovery.multi_agent_benchmark import run_multi_agent_recovery_scenario


def main() -> None:
    payload = {
        "single_action_vertical_slice": [score.to_dict() for score in run_vertical_slice()],
        "multi_agent_verified_restoration": run_multi_agent_recovery_scenario().to_dict(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
