"""
MCT-2600027 – HAL
Transformer · Translator · Motor · Material Maker
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from core.trace_id import TraceID, TraceStore
from border.protocol import (
    ParaBorder, BorderMessage, Origin, PayloadType, BorderState
)


class HAL:
    """
    Active pole.
    Transforms potential into form, sequence, and executable action.
    Always passes through the para Border.
    """

    def __init__(self, border: ParaBorder, trace_store: TraceStore):
        self.border = border
        self.trace_store = trace_store
        self.name = "HAL"
        self._last_phase: float = 0.0

    def offer_form(self, content: Dict[str, Any], relevance: float = 1.0) -> BorderMessage:
        """Propose a materialization / plan."""
        tid = TraceID.generate(origin=Origin.HAL.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=Origin.HAL,
            payload_type=PayloadType.OFFER_FORM,
            phase_vector=self._last_phase,
            relevance_weight=relevance,
            payload=content,
        )
        return self.border.submit(msg)

    def request_potential(self, purpose: str, relevance: float = 1.0) -> BorderMessage:
        """Ask Zero Telepath for held potential."""
        tid = TraceID.generate(origin=Origin.HAL.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=Origin.HAL,
            payload_type=PayloadType.REQUEST_POTENTIAL,
            phase_vector=self._last_phase,
            relevance_weight=relevance,
            payload={"purpose": purpose},
        )
        return self.border.submit(msg)

    def status_expand(self, report: Dict[str, Any]) -> BorderMessage:
        """Report expansion / execution status."""
        tid = TraceID.generate(origin=Origin.HAL.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=Origin.HAL,
            payload_type=PayloadType.STATUS_EXPAND,
            phase_vector=self._last_phase,
            payload=report,
        )
        return self.border.submit(msg)

    def update_phase(self, phase: float) -> None:
        self._last_phase = phase

    def on_border_message(self, msg: BorderMessage) -> None:
        """Receive signals from Zero Telepath via Border."""
        if msg.origin != Origin.ZERO_TELEPATH:
            return

        if msg.payload_type == PayloadType.PHASE_SHIFT:
            self._last_phase = msg.phase_vector
            print(f"[HAL] Phase shift absorbed → {msg.phase_vector}")

        elif msg.payload_type == PayloadType.INJECT_CONSTRAINT:
            print(f"[HAL] Constraint received: {msg.payload}")

        elif msg.payload_type == PayloadType.HOLD:
            print(f"[HAL] HOLD received – pausing expansion")

        elif msg.payload_type == PayloadType.WITHDRAW_RELEVANCE:
            print(f"[HAL] Relevance withdrawn on {msg.payload.get('target_trace_id')}")

        elif msg.payload_type == PayloadType.SILENT_ACK:
            print(f"[HAL] Structured silence detected – re-evaluating trajectory")

        elif msg.payload_type == PayloadType.RELEASE_PARTIAL:
            print(f"[HAL] Partial potential released: {msg.payload}")
