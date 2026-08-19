"""
MCT-2600027 – Trace Collision Handler
Detects, isolates, resolves and audits Trace-ID collisions.
Zero Telepath receives elevated regulatory power during collisions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from core.trace_id import TraceID, TraceRecord, TraceStatus, TraceStore


class ResolutionStrategy(str, Enum):
    SOFT_ISOLATION = "SOFT_ISOLATION"
    BRANCH_FORK = "BRANCH_FORK"
    DOMINANCE_BY_PHASE = "DOMINANCE_BY_PHASE"
    FULL_QUARANTINE = "FULL_QUARANTINE"
    DEPARTMENT_REVIEW = "DEPARTMENT_REVIEW"


@dataclass
class CollisionEvent:
    collision_id: str
    original_trace_ids: List[str]
    detection_point: str
    timestamp: float
    phase_vector: float
    strategy: Optional[ResolutionStrategy] = None
    final_status: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


class CollisionHandler:
    """
    Handles Trace collisions according to MCT-2600027 rules:
    - Never overwrite
    - Prefer phase/mesh consistency over pure timestamps
    - Zero Telepath gains elevated constraint power
    - Every decision produces a meta-trace
    """

    def __init__(self, trace_store: TraceStore):
        self.trace_store = trace_store
        self.events: List[CollisionEvent] = []
        self._quarantine: Dict[str, TraceRecord] = {}

    def detect_and_lock(self, incoming: TraceRecord, detection_point: str = "CollisionHandler") -> Optional[CollisionEvent]:
        """
        Call this when a potential collision is suspected.
        If the trace_id already exists with different content/origin → lock both.
        """
        existing = self.trace_store.get(incoming.trace_id.value)
        if existing is None:
            return None

        # Same ID, different origin or conflicting payload → collision
        if (existing.trace_id.origin != incoming.trace_id.origin or
                existing.payload != incoming.payload):

            existing.status = TraceStatus.COLLISION_LOCKED
            incoming.status = TraceStatus.COLLISION_LOCKED

            collision_id = TraceID.generate(origin="SYSTEM", parent_id=incoming.trace_id.value).value

            event = CollisionEvent(
                collision_id=collision_id,
                original_trace_ids=[existing.trace_id.value, incoming.trace_id.value],
                detection_point=detection_point,
                timestamp=time.time(),
                phase_vector=incoming.phase_vector,
            )
            self.events.append(event)

            # Write meta-trace immediately
            meta_id = TraceID.generate(origin="SYSTEM", parent_id=collision_id)
            meta_record = TraceRecord(
                trace_id=meta_id,
                status=TraceStatus.META,
                phase_vector=incoming.phase_vector,
                payload_type="COLLISION_DETECTED",
                payload={
                    "collision_id": collision_id,
                    "original_trace_ids": event.original_trace_ids,
                    "detection_point": detection_point,
                },
            )
            self.trace_store.write(meta_record)
            return event

        return None

    def resolve(self, event: CollisionEvent, strategy: ResolutionStrategy,
                preferred_trace_id: Optional[str] = None,
                phase_reference: float = 0.0) -> CollisionEvent:
        """
        Apply a resolution strategy and emit a meta-trace of the decision.
        """
        event.strategy = strategy

        if strategy == ResolutionStrategy.SOFT_ISOLATION:
            for tid in event.original_trace_ids:
                rec = self.trace_store.get(tid)
                if rec:
                    rec.status = TraceStatus.SUSPENDED
            event.final_status = "ISOLATED"

        elif strategy == ResolutionStrategy.BRANCH_FORK:
            # Keep both, mark as conflicting branches
            for tid in event.original_trace_ids:
                rec = self.trace_store.get(tid)
                if rec:
                    rec.status = TraceStatus.ARCHIVED_CONFLICT
                    rec.meta["fork"] = True
            event.final_status = "FORKED"

        elif strategy == ResolutionStrategy.DOMINANCE_BY_PHASE:
            # Prefer the trace whose phase is closer to the reference
            best = None
            best_dist = float("inf")
            for tid in event.original_trace_ids:
                rec = self.trace_store.get(tid)
                if rec:
                    dist = abs(rec.phase_vector - phase_reference)
                    if dist < best_dist:
                        best_dist = dist
                        best = rec
            if best:
                best.status = TraceStatus.ACTIVE
                for tid in event.original_trace_ids:
                    if tid != best.trace_id.value:
                        rec = self.trace_store.get(tid)
                        if rec:
                            rec.status = TraceStatus.ARCHIVED_CONFLICT
                event.final_status = f"DOMINANT:{best.trace_id.value}"
            else:
                event.final_status = "UNRESOLVED"

        elif strategy == ResolutionStrategy.FULL_QUARANTINE:
            for tid in event.original_trace_ids:
                rec = self.trace_store.get(tid)
                if rec:
                    rec.status = TraceStatus.SUSPENDED
                    self._quarantine[tid] = rec
            event.final_status = "QUARANTINED"

        elif strategy == ResolutionStrategy.DEPARTMENT_REVIEW:
            event.final_status = "PENDING_DEPARTMENT_REVIEW"
            # In full system this would notify an anthropomorphic department

        # Meta-trace of the resolution
        meta_id = TraceID.generate(origin="SYSTEM", parent_id=event.collision_id)
        meta_record = TraceRecord(
            trace_id=meta_id,
            status=TraceStatus.META,
            phase_vector=phase_reference,
            payload_type="COLLISION_RESOLVED",
            payload={
                "collision_id": event.collision_id,
                "strategy": strategy.value,
                "final_status": event.final_status,
                "original_trace_ids": event.original_trace_ids,
            },
        )
        self.trace_store.write(meta_record)
        return event

    def list_open_collisions(self) -> List[CollisionEvent]:
        return [e for e in self.events if e.final_status is None or e.final_status == "PENDING_DEPARTMENT_REVIEW"]

    def list_quarantine(self) -> Dict[str, TraceRecord]:
        return dict(self._quarantine)
