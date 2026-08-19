"""
MCT-2600027 – Trace-ID System
Immutable, collision-aware trace identifiers for the entire mesh.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any


class TraceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    COLLISION_LOCKED = "COLLISION_LOCKED"
    ARCHIVED_CONFLICT = "ARCHIVED_CONFLICT"
    RESOLVED = "RESOLVED"
    ABSENCE = "ABSENCE"          # Zero Telepath non-event
    META = "META"                # collision / system meta traces


@dataclass(frozen=True)
class TraceID:
    """Immutable Trace Identifier."""
    value: str
    created_at: float
    origin: str                  # HAL | ZERO_TELEPATH | BORDER | DEPARTMENT | SYSTEM
    parent_id: Optional[str] = None

    @staticmethod
    def generate(origin: str, parent_id: Optional[str] = None, seed: Optional[str] = None) -> "TraceID":
        raw = f"{origin}:{parent_id}:{seed}:{time.time_ns()}:{uuid.uuid4().hex}"
        digest = hashlib.sha256(raw.encode()).hexdigest()[:32]
        return TraceID(
            value=f"tr_{digest}",
            created_at=time.time(),
            origin=origin,
            parent_id=parent_id,
        )

    def __str__(self) -> str:
        return self.value


@dataclass
class TraceRecord:
    """Full trace record written into the mesh."""
    trace_id: TraceID
    status: TraceStatus = TraceStatus.ACTIVE
    phase_vector: float = 0.0
    relevance_weight: float = 1.0
    payload_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    border_state: str = "OPEN_POROUS"
    timestamp: float = field(default_factory=time.time)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id.value,
            "origin": self.trace_id.origin,
            "parent_id": self.trace_id.parent_id,
            "status": self.status.value,
            "phase_vector": self.phase_vector,
            "relevance_weight": self.relevance_weight,
            "payload_type": self.payload_type,
            "payload": self.payload,
            "border_state": self.border_state,
            "timestamp": self.timestamp,
            "meta": self.meta,
        }


class TraceStore:
    """In-memory trace store with basic collision detection."""

    def __init__(self):
        self._records: Dict[str, TraceRecord] = {}
        self._collisions: List[str] = []

    def write(self, record: TraceRecord) -> TraceRecord:
        tid = record.trace_id.value
        if tid in self._records:
            # Collision detected
            existing = self._records[tid]
            existing.status = TraceStatus.COLLISION_LOCKED
            record.status = TraceStatus.COLLISION_LOCKED
            self._collisions.append(tid)

            # Create meta-trace
            meta_id = TraceID.generate(origin="SYSTEM", parent_id=tid)
            meta_record = TraceRecord(
                trace_id=meta_id,
                status=TraceStatus.META,
                payload_type="COLLISION",
                payload={
                    "original_trace_ids": [tid],
                    "detection_point": "TraceStore.write",
                    "existing_origin": existing.trace_id.origin,
                    "new_origin": record.trace_id.origin,
                },
            )
            self._records[meta_id.value] = meta_record
            return meta_record

        self._records[tid] = record
        return record

    def get(self, trace_id: str) -> Optional[TraceRecord]:
        return self._records.get(trace_id)

    def list_collisions(self) -> List[str]:
        return list(self._collisions)

    def all_records(self) -> List[TraceRecord]:
        return list(self._records.values())
