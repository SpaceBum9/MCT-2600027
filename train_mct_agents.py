#!/usr/bin/env python3
"""Run or verify MCT-2600027 GARAS policy training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from training.engine import (
    CurriculumError,
    build_checkpoint,
    latest_parent_trace,
    load_curriculum,
    normalize_timestamp,
    train_agents,
    verify_checkpoint,
    write_checkpoint,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_CURRICULUM = ROOT / "training" / "curriculum.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train MCT GARAS role policies without vendor calls or weight claims."
    )
    parser.add_argument("--curriculum", type=Path, default=DEFAULT_CURRICULUM)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timestamp", help="ISO-8601 UTC timestamp ending in Z")
    parser.add_argument("--max-epochs", type=int, default=3)
    parser.add_argument("--parent-trace-id")
    parser.add_argument("--parent-human-id")
    parser.add_argument(
        "--verify",
        type=Path,
        metavar="CHECKPOINT",
        help="verify an existing checkpoint instead of training",
    )
    return parser


def _verify(path: Path, curriculum_path: Path = DEFAULT_CURRICULUM) -> int:
    try:
        checkpoint = json.loads(path.read_text(encoding="utf-8"))
        curriculum = load_curriculum(curriculum_path)
    except (OSError, json.JSONDecodeError, CurriculumError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 2
    valid, errors = verify_checkpoint(checkpoint, curriculum)
    checkpoint_object = checkpoint if isinstance(checkpoint, dict) else {}
    print(
        json.dumps(
            {
                "valid": valid,
                "human_id": checkpoint_object.get("human_id"),
                "trace_id": checkpoint_object.get("trace_id"),
                "errors": errors,
            },
            indent=2,
        )
    )
    return 0 if valid else 2


def main() -> int:
    args = _parser().parse_args()
    if args.verify:
        return _verify(args.verify, args.curriculum)

    try:
        curriculum = load_curriculum(args.curriculum)
        result = train_agents(curriculum, max_epochs=args.max_epochs)
        if args.parent_trace_id:
            parent_trace_id = args.parent_trace_id
            parent_human_id = args.parent_human_id
        else:
            parent_trace_id, parent_human_id = latest_parent_trace(ROOT / "traces")
        timestamp = normalize_timestamp(args.timestamp)
        checkpoint = build_checkpoint(
            curriculum,
            result,
            timestamp=timestamp,
            parent_trace_id=parent_trace_id,
            parent_human_id=parent_human_id,
        )
        output = args.output
        if output is None:
            output = ROOT / "traces" / "training" / f"{checkpoint['human_id']}.json"
        destination = write_checkpoint(output, checkpoint, curriculum)
    except CurriculumError as exc:
        print(json.dumps({"trained": False, "error": str(exc)}, indent=2))
        return 2

    agents = checkpoint["result"]["agents"]
    print(
        json.dumps(
            {
                "trained": checkpoint["result"]["promotion_gate"]["passed"],
                "training_mode": checkpoint["training_mode"],
                "model_weights_modified": checkpoint["model_weights_modified"],
                "epochs_completed": checkpoint["result"]["epochs_completed"],
                "stages": {agent["role"]: agent["stage"] for agent in agents},
                "learned_rules": {
                    agent["role"]: agent["learned_rules"] for agent in agents
                },
                "checkpoint": str(destination),
                "trace_id": checkpoint["trace_id"],
            },
            indent=2,
        )
    )
    return 0 if checkpoint["result"]["promotion_gate"]["passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
