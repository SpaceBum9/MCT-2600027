from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path("mct_state_manifest.json")


@dataclass(frozen=True)
class NodeState:
    node_id: str
    declared: bool
    connectivity: str = "unverified"


@dataclass(frozen=True)
class OrchestratorSnapshot:
    project_identifier: str
    system_flag: str
    sync_interval_seconds: int
    nodes: tuple[NodeState, ...]
    greeting: str
    external_delivery_verified: bool = False


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_snapshot(manifest: dict[str, Any]) -> OrchestratorSnapshot:
    interval = int(manifest.get("sync_interval_seconds", 200))
    interval = max(1, interval)

    nodes = tuple(
        NodeState(node_id=str(node), declared=True)
        for node in manifest.get("nodes", [])
    )

    return OrchestratorSnapshot(
        project_identifier=str(manifest.get("project_identifier", "MCT-2600027")),
        system_flag=str(manifest.get("system_flag", "UNSET")),
        sync_interval_seconds=interval,
        nodes=nodes,
        greeting=".hallo",
    )


def build_sync_plan(snapshot: OrchestratorSnapshot) -> dict[str, Any]:
    return {
        "project_identifier": snapshot.project_identifier,
        "system_flag": snapshot.system_flag,
        "command": snapshot.greeting,
        "sync_interval_seconds": snapshot.sync_interval_seconds,
        "nodes": [
            {
                "node_id": node.node_id,
                "declared": node.declared,
                "connectivity": node.connectivity,
                "action": "heartbeat_prepared",
            }
            for node in snapshot.nodes
        ],
        "external_delivery_verified": snapshot.external_delivery_verified,
    }


def main() -> None:
    snapshot = build_snapshot(load_manifest())
    print(json.dumps(build_sync_plan(snapshot), indent=2))


if __name__ == "__main__":
    main()
