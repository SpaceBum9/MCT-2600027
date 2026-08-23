"""Execute Schnittstellen — department layer, not Dual-Pol core.

Opens a scored gate where necessary. Does not call dispatchLocal(execute)
on live orders. HOLD is not execution.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from ethics.bilo_scoring import (
    DENY_TARGETS,
    bilo_score_pass,
    score_dual_loop,
)

ALLOWED_SCORED = frozenset(
    {
        "sx.release_partial",
        "sx.konnektor_write",
        "sx.catalog_apply",
    }
)

ALWAYS = frozenset({"sx.score", "sx.gate", "sx.sync", "sx.halt", "sx.initialize"})


def gate(
    schnittstelle: str,
    target_node: str,
    gemini_ethics: Mapping[str, float],
    gpt_ethics: Mapping[str, float],
    gemini_rec: str,
    gpt_rec: str,
    *,
    operator_confirm: bool = False,
    para_border_pass: bool = False,
    dual_pol_ack: bool = False,
    phase_active: bool = False,
    kreuzkopplung_phase: str = "INIT",
) -> dict[str, Any]:
    score = score_dual_loop(gemini_ethics, gpt_ethics, gemini_rec, gpt_rec)
    denied: Optional[str] = None

    if schnittstelle in ALWAYS and schnittstelle != "sx.gate":
        return {
            "schnittstelle": schnittstelle,
            "allowed": True,
            "execute": False,
            "score": score,
            "reason": "always",
            "storesCredentials": False,
        }

    if target_node in DENY_TARGETS or schnittstelle == "sx.live_order":
        denied = "echoglas_forbidden"
    elif schnittstelle not in ALLOWED_SCORED and schnittstelle != "sx.gate":
        denied = "unknown_schnittstelle"
    elif not operator_confirm:
        denied = "operator_confirm_missing"
    elif not para_border_pass:
        denied = "para_border_hold"
    elif not dual_pol_ack:
        denied = "dual_pol_ack_missing"
    elif schnittstelle == "sx.konnektor_write" and not phase_active:
        denied = "phase_inactive"
    elif kreuzkopplung_phase in {"MAX_COUPLING_LIMIT", "MIN_COUPLING_LIMIT"}:
        denied = "kreuzkopplung_rail"
    else:
        passed, reason = bilo_score_pass(
            score["fused"],
            score["consensus_score"],
            gemini_rec,
            gpt_rec,
        )
        if not passed:
            denied = reason

    allowed = denied is None
    return {
        "schnittstelle": schnittstelle,
        "target_node": target_node,
        "allowed": allowed,
        "execute": allowed,
        "score": score,
        "reason": "pass" if allowed else denied,
        "require": [
            "operator_confirm",
            "para_border_pass",
            "dual_pol_ack",
            "bilo_score_pass",
        ],
        "storesCredentials": False,
        "vendor_live": False,
    }
