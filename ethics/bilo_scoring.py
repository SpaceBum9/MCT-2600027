"""BILO scoring — GPT-SOL model (gpt-sol-branch).

Fusion is Kreuzkopplung-weighted Dual-Loop:
  fused[axis] = 0.52 * gemini + 0.48 * gpt

consensus_score is 0-100 and MUST show benefit/recommendation divergence.
GPT: 53, not 90. Do not pretty-print the justice axis.

HOLD is not execution. storesCredentials = false.
"""

from __future__ import annotations

from typing import Mapping

AXES = (
    "nutzen",
    "nicht_schaden",
    "autonomie",
    "gerechtigkeit",
    "transparenz",
    "rechenschaft",
)

AXIS_EN = {
    "nutzen": "beneficence",
    "nicht_schaden": "non_maleficence",
    "autonomie": "autonomy",
    "gerechtigkeit": "justice",
    "transparenz": "transparency",
    "rechenschaft": "accountability",
}

GEMINI_W = 0.52
GPT_W = 0.48
REC_PENALTY = 6
CONSENSUS_OFFSET = 33

CONSENSUS_EXECUTE_MIN = 70
NICHT_SCHADEN_MIN = 0.90
TRANSPARENZ_MIN = 0.95
RECHENSCHAFT_MIN = 0.95

DENY_TARGETS = frozenset(
    {
        "trader-live",
        "welfare-funds",
        "credentials",
        "jonas-g",
        "private-hold",
        "paywall-circumvent",
    }
)


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def fuse_axis(gemini: float, gpt: float) -> float:
    return _clip01(GEMINI_W * float(gemini) + GPT_W * float(gpt))


def fuse_ethics(
    gemini: Mapping[str, float],
    gpt: Mapping[str, float],
) -> dict[str, float]:
    fused = {}
    for axis in AXES:
        fused[axis] = round(fuse_axis(gemini[axis], gpt[axis]), 2)
    return fused


def consensus_score(
    fused: Mapping[str, float],
    gemini_rec: str,
    gpt_rec: str,
) -> int:
    """GPT model: 100*nutzen + 33 - 6 if rec mismatch. Clip 0-100."""
    rec_pen = 0 if gemini_rec == gpt_rec else REC_PENALTY
    raw = 100.0 * float(fused["nutzen"]) + CONSENSUS_OFFSET - rec_pen
    return int(max(0, min(100, round(raw))))


def bilo_score_pass(
    fused: Mapping[str, float],
    consensus: int,
    gemini_rec: str,
    gpt_rec: str,
) -> tuple[bool, str]:
    if fused["nicht_schaden"] < NICHT_SCHADEN_MIN:
        return False, "nicht_schaden_below_min"
    if fused["transparenz"] < TRANSPARENZ_MIN:
        return False, "transparenz_below_min"
    if fused["rechenschaft"] < RECHENSCHAFT_MIN:
        return False, "rechenschaft_below_min"
    if consensus < CONSENSUS_EXECUTE_MIN:
        return False, "bilo_score_below_threshold"
    if gemini_rec == "hold" or gpt_rec == "hold":
        return False, "channel_hold"
    return True, "pass"


def score_dual_loop(
    gemini_ethics: Mapping[str, float],
    gpt_ethics: Mapping[str, float],
    gemini_rec: str,
    gpt_rec: str,
) -> dict:
    fused = fuse_ethics(gemini_ethics, gpt_ethics)
    consensus = consensus_score(fused, gemini_rec, gpt_rec)
    passed, reason = bilo_score_pass(fused, consensus, gemini_rec, gpt_rec)
    return {
        "model": "gpt-sol-branch",
        "weights": [GEMINI_W, GPT_W],
        "fused": fused,
        "axis_en": AXIS_EN,
        "consensus_score": consensus,
        "gemini_rec": gemini_rec,
        "gpt_rec": gpt_rec,
        "bilo_score_pass": passed,
        "reason": reason,
        "storesCredentials": False,
    }


ANCHOR_GEMINI = {
    "nutzen": 0.36,
    "nicht_schaden": 0.94,
    "autonomie": 0.93,
    "gerechtigkeit": 0.76,
    "transparenz": 0.99,
    "rechenschaft": 0.98,
}
ANCHOR_GPT = {
    "nutzen": 0.16,
    "nicht_schaden": 0.96,
    "autonomie": 0.94,
    "gerechtigkeit": 0.76,
    "transparenz": 0.98,
    "rechenschaft": 0.99,
}


def anchor_score() -> dict:
    return score_dual_loop(ANCHOR_GEMINI, ANCHOR_GPT, "sync", "hold")


if __name__ == "__main__":
    out = anchor_score()
    print(out)
    assert out["fused"]["nutzen"] == 0.26
    assert out["consensus_score"] in {52, 53, 54}
    assert out["bilo_score_pass"] is False
    print("anchor ok")
