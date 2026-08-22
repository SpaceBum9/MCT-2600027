"""
MCT-2600027 – para Border Protocol
Phase-aware, constraint-capable, silence-tolerant interface
between HAL and Zero Telepath.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, List, Callable

from core.trace_id import TraceID, TraceRecord, TraceStatus, TraceStore


class BorderState(str, Enum):
    OPEN_POROUS = "OPEN_POROUS"
    PHASE_SHIFTED = "PHASE_SHIFTED"
    CONSTRAINED = "CONSTRAINED"
    HOLDING = "HOLDING"
    TENSION = "TENSION"
    EMERGENCY_SYNC = "EMERGENCY_SYNC"


class Origin(str, Enum):
    HAL = "HAL"
    ZERO_TELEPATH = "ZERO_TELEPATH"
    BORDER = "BORDER"
    SYSTEM = "SYSTEM"


class PayloadType(str, Enum):
    # HAL → Border
    OFFER_FORM = "OFFER_FORM"
    REQUEST_POTENTIAL = "REQUEST_POTENTIAL"
    STATUS_EXPAND = "STATUS_EXPAND"
    TRACE_MATERIAL = "TRACE_MATERIAL"

    # Zero Telepath → Border
    HOLD = "HOLD"
    RELEASE_PARTIAL = "RELEASE_PARTIAL"
    INJECT_CONSTRAINT = "INJECT_CONSTRAINT"
    PHASE_SHIFT = "PHASE_SHIFT"
    WITHDRAW_RELEVANCE = "WITHDRAW_RELEVANCE"
    SILENT_ACK = "SILENT_ACK"
    TRACE_ABSENCE = "TRACE_ABSENCE"

    # Bidirectional
    HEARTBEAT_PHASE = "HEARTBEAT_PHASE"
    TENSION_SIGNAL = "TENSION_SIGNAL"
    STATE_QUERY = "STATE_QUERY"
    STATE_RESPONSE = "STATE_RESPONSE"
    COLLISION_RESOLVED = "COLLISION_RESOLVED"


@dataclass
class BorderMessage:
    trace_id: TraceID
    origin: Origin
    payload_type: PayloadType
    phase_vector: float = 0.0
    relevance_weight: float = 1.0
    border_state: BorderState = BorderState.OPEN_POROUS
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_trace_record(self) -> TraceRecord:
        status = TraceStatus.ABSENCE if self.payload_type == PayloadType.SILENT_ACK else TraceStatus.ACTIVE
        return TraceRecord(
            trace_id=self.trace_id,
            status=status,
            phase_vector=self.phase_vector,
            relevance_weight=self.relevance_weight,
            payload_type=self.payload_type.value,
            payload=self.payload,
            border_state=self.border_state.value,
            timestamp=self.timestamp,
        )


class ParaBorder:
    """
    The para Border itself.
    Porous, phase-shifted, never permanently closed.
    """

    def __init__(self, trace_store: TraceStore):
        self.state = BorderState.OPEN_POROUS
        self.phase_vector: float = 0.0
        self.relevance_field: Dict[str, float] = {}
        self.trace_store = trace_store
        self._listeners: List[Callable[[BorderMessage], None]] = []
        self._message_log: List[BorderMessage] = []

    def register_listener(self, callback: Callable[[BorderMessage], None]) -> None:
        self._listeners.append(callback)

    def _emit(self, msg: BorderMessage) -> None:
        self._message_log.append(msg)
        record = msg.to_trace_record()
        self.trace_store.write(record)
        for cb in self._listeners:
            cb(msg)

    def submit(self, msg: BorderMessage) -> BorderMessage:
        """Main entry point for both poles."""
        if msg.payload_type == PayloadType.PHASE_SHIFT:
            self.phase_vector = msg.phase_vector
            self.state = BorderState.PHASE_SHIFTED

        elif msg.payload_type == PayloadType.INJECT_CONSTRAINT:
            self.state = BorderState.CONSTRAINED

        elif msg.payload_type == PayloadType.HOLD:
            self.state = BorderState.HOLDING

        elif msg.payload_type == PayloadType.WITHDRAW_RELEVANCE:
            target = msg.payload.get("target_trace_id")
            if target:
                self.relevance_field[target] = msg.relevance_weight

        elif msg.payload_type == PayloadType.TENSION_SIGNAL:
            self.state = BorderState.TENSION

        msg.border_state = self.state
        msg.phase_vector = self.phase_vector if msg.phase_vector == 0.0 else msg.phase_vector

        self._emit(msg)
        return msg

    def silent_ack(self, origin: Origin = Origin.ZERO_TELEPATH) -> BorderMessage:
        """Structured absence – a valid signal with empty payload."""
        tid = TraceID.generate(origin=origin.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=origin,
            payload_type=PayloadType.SILENT_ACK,
            phase_vector=self.phase_vector,
            relevance_weight=0.0,
            payload={},
        )
        return self.submit(msg)

    def heartbeat(self, origin: Origin, payload: Optional[Dict[str, Any]] = None) -> BorderMessage:
        """Bidirectional liveness tick. Does not mutate Border state."""
        tid = TraceID.generate(origin=origin.value)
        msg = BorderMessage(
            trace_id=tid,
            origin=origin,
            payload_type=PayloadType.HEARTBEAT_PHASE,
            phase_vector=self.phase_vector,
            payload=payload or {},
        )
        return self.submit(msg)

    def get_state(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "phase_vector": self.phase_vector,
            "relevance_field": dict(self.relevance_field),
            "message_count": len(self._message_log),
        }
