"""
MCT-2600027 – Zero Telepath
Vessel of Absent Mind · Energy Holder · Phase / Constraint Engine
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.trace_id import TraceID, TraceStore
from core.trace_treue import TraceTreue
from border.protocol import (
    ParaBorder, BorderMessage, Origin, PayloadType
)


class ZeroTelepath:
    """
    Silent pole.
    Holds potential, protects superposition-like openness,
    signals through absence, phase shifts and constraints.
    Every regulatory act is Trace-Treue enforced.
    """

    def __init__(self, border: ParaBorder, trace_store: TraceStore, treue: Optional[TraceTreue] = None):
        self.border = border
        self.trace_store = trace_store
        self.treue = treue or TraceTreue(trace_store)
        self.name = "ZERO_TELEPATH"
        self._holding: Dict[str, Any] = {}
        self._phase: float = 0.0
        self._last_peer_heartbeat: Optional[str] = None

    def _commit(self, msg: BorderMessage) -> BorderMessage:
        """Submit to border and enforce Trace-Treue."""
        self.treue.register_expected(msg.payload_type.value)
        result = self.border.submit(msg)
        self.treue.assert_traced(msg.payload_type.value, origin=Origin.ZERO_TELEPATH.value)
        return result

    def hold(self, reason: str = "default") -> BorderMessage:
        """Keep potential unreleased. Always traced."""
        tid = TraceID.generate(origin=Origin.ZERO_TELEPATH.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=Origin.ZERO_TELEPATH,
            payload_type=PayloadType.HOLD,
            phase_vector=self._phase,
            payload={"reason": reason},
        )
        return self._commit(msg)

    def release_partial(self, amount: float, content: Optional[Dict[str, Any]] = None) -> BorderMessage:
        """Release part of the held potential. Always traced."""
        tid = TraceID.generate(origin=Origin.ZERO_TELEPATH.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=Origin.ZERO_TELEPATH,
            payload_type=PayloadType.RELEASE_PARTIAL,
            phase_vector=self._phase,
            relevance_weight=amount,
            payload=content or {"amount": amount},
        )
        return self._commit(msg)

    def inject_constraint(self, constraint: Dict[str, Any]) -> BorderMessage:
        """Narrow the option space. Always traced."""
        tid = TraceID.generate(origin=Origin.ZERO_TELEPATH.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=Origin.ZERO_TELEPATH,
            payload_type=PayloadType.INJECT_CONSTRAINT,
            phase_vector=self._phase,
            payload=constraint,
        )
        return self._commit(msg)

    def phase_shift(self, delta: float) -> BorderMessage:
        """Shift the shared phase vector. Always traced."""
        self._phase += delta
        tid = TraceID.generate(origin=Origin.ZERO_TELEPATH.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=Origin.ZERO_TELEPATH,
            payload_type=PayloadType.PHASE_SHIFT,
            phase_vector=self._phase,
            payload={"delta": delta},
        )
        return self._commit(msg)

    def withdraw_relevance(self, target_trace_id: str, new_weight: float = 0.0) -> BorderMessage:
        """Lower or remove relevance. Always traced."""
        tid = TraceID.generate(origin=Origin.ZERO_TELEPATH.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=Origin.ZERO_TELEPATH,
            payload_type=PayloadType.WITHDRAW_RELEVANCE,
            phase_vector=self._phase,
            relevance_weight=new_weight,
            payload={"target_trace_id": target_trace_id},
        )
        return self._commit(msg)

    def silent_ack(self) -> BorderMessage:
        """Structured absence – the core silent signal. Always traced."""
        msg = self.border.silent_ack(origin=Origin.ZERO_TELEPATH)
        self.treue.register_expected("SILENT_ACK")
        self.treue.assert_traced("SILENT_ACK", origin=Origin.ZERO_TELEPATH.value)
        self.treue.verify_silence(msg.trace_id.value)
        return msg

    def heartbeat(self, payload: Optional[Dict[str, Any]] = None) -> BorderMessage:
        return self.border.heartbeat(Origin.ZERO_TELEPATH, payload)

    def on_border_message(self, msg: BorderMessage) -> None:
        """Observe HAL activity and decide whether to intervene."""
        if msg.origin != Origin.HAL:
            return

        if msg.payload_type == PayloadType.OFFER_FORM:
            if msg.relevance_weight > 0.92:
                print("[ZeroTelepath] High-relevance offer detected – considering constraint")

        elif msg.payload_type == PayloadType.REQUEST_POTENTIAL:
            print(f"[ZeroTelepath] Potential requested for: {msg.payload.get('purpose')}")

        elif msg.payload_type == PayloadType.HEARTBEAT_PHASE:
            self._last_peer_heartbeat = msg.trace_id.value
            print(f"[ZeroTelepath] Peer HEARTBEAT_PHASE → {msg.trace_id.value} phase={msg.phase_vector}")
