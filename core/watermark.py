"""
MCT-2600027 – Semantic watermark / Automated Timestamp Mark (ATM).
Binds a cycle to fluid-state hash, registered identity, UTC, and tick frequency.
No secrets: credentials are semantic (manifest identity), never tokens.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "mct_state_manifest.json"
FLUID_PATH = ROOT / "FLUID_MEMORY_SNAPSHOT.md"
SESSION_TRACE = "tr_2efe52faa454faaf4d3330f8ea3fe4db"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_manifest() -> Dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def fluid_digest() -> str:
    if not FLUID_PATH.exists():
        return ""
    return _sha256_text(FLUID_PATH.read_text(encoding="utf-8"))


def semantic_credential(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Registered identity only — project, alignment, nodes. No PAT, no passwords."""
    registered = {
        "project_identifier": manifest.get("project_identifier"),
        "system_flag": manifest.get("system_flag"),
        "alignment": manifest.get("alignment"),
        "nodes": list(manifest.get("nodes") or []),
        "spin_flip": manifest.get("spin_flip"),
    }
    canonical = json.dumps(registered, sort_keys=True, separators=(",", ":"))
    return {
        "kind": "semantic_registered",
        "credential_id": "sem_" + _sha256_text(canonical)[:32],
        "registered": registered,
    }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def stamp(cycle: int, manifest: Dict[str, Any] | None = None) -> Dict[str, Any]:
    manifest = manifest or load_manifest()
    interval = int(manifest.get("sync_interval_seconds") or 200)
    now = utc_now()
    iso = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    cred = semantic_credential(manifest)
    payload = {
        "atm": "MCT_ATM",
        "grade": "GOLD",
        "cycle": cycle,
        "utc": iso,
        "unix_ms": int(now.timestamp() * 1000),
        "frequency": {
            "interval_seconds": interval,
            "hz": round(1.0 / interval, 8),
        },
        "fluid_state": {
            "path": "FLUID_MEMORY_SNAPSHOT.md",
            "sha256": fluid_digest(),
            "session_trace": SESSION_TRACE,
        },
        "credential": cred,
        "channel": "stdout_jsonl",
    }
    payload["watermark"] = "wm_" + _sha256_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"))
    )[:32]
    return payload


def dispatch(mark: Dict[str, Any]) -> None:
    """Send ATM over stdout — the loop's registered dispatch path."""
    print(json.dumps(mark, separators=(",", ":"), ensure_ascii=True), flush=True)
