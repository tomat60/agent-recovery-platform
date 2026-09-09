from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_recovery.judge_evidence_package import package_judge_evidence


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and package deterministic judge advisory evidence."
    )
    parser.add_argument("artifact", type=Path, help="Existing measured judge artifact JSON")
    parser.add_argument("output_dir", type=Path, help="Directory for deterministic package output")
    args = parser.parse_args()

    manifest = package_judge_evidence(args.artifact, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
