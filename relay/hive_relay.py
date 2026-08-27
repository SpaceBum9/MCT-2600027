"""Non-anthropomorphic hive-mind relay / teleprompter.

Compresses a sector state into a prompt packet bound to BILO2026.
HOLD: format only. No credentials. No live orders.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


MARKER = "BILO2026"


@dataclass
class SectorIntake:
    locomotion: str = ""
    environment: str = ""
    marks: list[str] = field(default_factory=list)
    department_zeitgeist: str = ""
    residual: float = 0.5


@dataclass
class PromptPacket:
    marker: str
    role: str
    anthropomorphic: bool
    compressed: str
    residual: float
    ts_utc: str
    hold: bool = True

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clamp01(x: float) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        v = 0.5
    return max(0.0, min(1.0, v))


def compress(intake: SectorIntake, marker: str = MARKER) -> PromptPacket:
    marks = ", ".join(intake.marks) if intake.marks else "none"
    compressed = (
        f"sector locomotion={intake.locomotion or 'n/a'}; "
        f"env={intake.environment or 'n/a'}; "
        f"marks={marks}; "
        f"zeitgeist={intake.department_zeitgeist or 'n/a'}; "
        f"residual={_clamp01(intake.residual):.3f}"
    )
    return PromptPacket(
        marker=marker,
        role="teleprompter",
        anthropomorphic=False,
        compressed=compressed,
        residual=_clamp01(intake.residual),
        ts_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        hold=True,
    )
