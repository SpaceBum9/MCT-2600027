"""
MCT-2600027 – Telemetry POST to the Google Workspace worker.
No URL → skip. HTTP 2xx only counts as delivered. Token never printed.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_NODE = "ALG_0_EGELHEIMER"


def node_name(manifest: Dict[str, Any]) -> str:
    env = os.getenv("MCT_NODE")
    if env:
        return env
    nodes = list(manifest.get("nodes") or [])
    return str(nodes[0]) if nodes else DEFAULT_NODE


def envelope(
    mark: Dict[str, Any],
    *,
    node: str,
    phase_angle: float,
    heartbeat: Dict[str, str],
) -> Dict[str, Any]:
    body = dict(mark)
    body["trace_id"] = mark.get("watermark") or heartbeat.get("hal") or "mct-trace-auto"
    body["node"] = node
    body["phase_angle"] = phase_angle
    body["phase_vector"] = phase_angle
    body["payload_type"] = "HEARTBEAT_PHASE"
    body["heartbeat"] = heartbeat
    return body


def post(body: Dict[str, Any], url: Optional[str] = None) -> Dict[str, Any]:
    url = url if url is not None else os.getenv("MCT_TELEMETRY_URL", "").strip()
    if not url:
        return {"status": "skipped", "reason": "no_url", "claims_external_delivery": False}

    payload = dict(body)
    token = os.getenv("MCT_WEBHOOK_TOKEN", "").strip()
    if token:
        payload["token"] = token

    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            ok = 200 <= getattr(resp, "status", 200) < 300
            return {
                "status": "SUCCESS" if ok else "ERROR",
                "http_status": getattr(resp, "status", 200),
                "body": raw[:500],
                "claims_external_delivery": ok,
            }
    except urllib.error.HTTPError as exc:
        return {
            "status": "ERROR",
            "http_status": exc.code,
            "error": str(exc),
            "claims_external_delivery": False,
        }
    except Exception as exc:
        return {
            "status": "ERROR",
            "error": str(exc),
            "claims_external_delivery": False,
        }
