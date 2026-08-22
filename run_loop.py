#!/usr/bin/env python3
"""
MCT-2600027 – Loop daemon.
Cycle → HEARTBEAT_PHASE (both poles) → GOLD ATM → optional Google worker POST.
"""

from __future__ import annotations

import os
import signal
import sys
import time
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import Orchestrator
from core.telemetry import envelope, node_name, post
from core.watermark import dispatch, load_manifest, stamp

_stop = False


def _handle_stop(signum: int, _frame: Optional[object]) -> None:
    global _stop
    _stop = True
    print(f"mct-loop: signal {signum}, draining", flush=True)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return int(raw)


def main() -> int:
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    manifest = load_manifest()
    interval = _env_int("MCT_INTERVAL", int(manifest.get("sync_interval_seconds") or 200))
    cycles_limit = _env_int("MCT_CYCLES", 0)
    node = node_name(manifest)

    orch = Orchestrator()
    cycle = 0
    print(
        f"mct-loop: daemon interval={interval}s cycles={cycles_limit or 'inf'} "
        f"flag={manifest.get('system_flag')} node={node}",
        flush=True,
    )

    while not _stop:
        cycle += 1
        orch.demo_cycle()
        mark = stamp(cycle, manifest)
        hb_hal = orch.hal.heartbeat({"atm": mark["watermark"], "utc": mark["utc"], "cycle": cycle})
        hb_zero = orch.zero.heartbeat({"atm": mark["watermark"], "utc": mark["utc"], "cycle": cycle})
        body = envelope(
            mark,
            node=node,
            phase_angle=float(orch.border.phase_vector),
            heartbeat={"hal": hb_hal.trace_id.value, "zero": hb_zero.trace_id.value},
        )
        dispatch(body)
        result = post(body)
        print(
            f"mct-loop: telemetry {result.get('status')} "
            f"delivered={result.get('claims_external_delivery')}",
            flush=True,
        )
        if cycles_limit and cycle >= cycles_limit:
            break
        deadline = time.monotonic() + interval
        while not _stop and time.monotonic() < deadline:
            time.sleep(min(0.25, deadline - time.monotonic()))

    print(f"mct-loop: halt after {cycle} cycle(s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
