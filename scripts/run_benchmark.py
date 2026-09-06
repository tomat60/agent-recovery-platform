from __future__ import annotations

import json

from agent_recovery.benchmark import run_vertical_slice


def main() -> None:
    results = [score.to_dict() for score in run_vertical_slice()]
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
