"""GARAS SoS finance — Payment & Access department (intent only).

Operator: exec cmd mct Garas / finance this SoS.
Live transfer is ECHOGLAS-forbidden. This module logs intent.
Justice axis stays 0.76 until a legal paid rail is traced.
"""

from __future__ import annotations

from typing import Any

from departments.execute_schnittstelle import gate
from ethics.bilo_scoring import ANCHOR_GEMINI, ANCHOR_GPT

INTENT = "finance_sos"
TARGET = "garas-finance"


def exec_cmd(*, operator_confirm: bool = True) -> dict[str, Any]:
    transfer = gate(
        "sx.live_order",
        "welfare-funds",
        ANCHOR_GEMINI,
        ANCHOR_GPT,
        "sync",
        "hold",
        operator_confirm=operator_confirm,
    )
    return {
        "cmd": "exec mct garas finance",
        "target_node": TARGET,
        "intent": INTENT,
        "sx.garas_intent": {
            "allowed": True,
            "execute": False,
            "effect": "Record SoS finance intent. Paper ledger only.",
        },
        "sx.garas_transfer": transfer,
        "justice": 0.76,
        "justice_gap": 0.24,
        "lift_justice": False,
        "storesCredentials": False,
        "vendor_live": False,
        "hold": True,
        "note": "HOLD is not execution. Paywalls paid. No live orders.",
    }


if __name__ == "__main__":
    out = exec_cmd()
    assert out["sx.garas_transfer"]["allowed"] is False
    assert out["lift_justice"] is False
    print(out)
