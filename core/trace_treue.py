"""
MCT-2600027 – Trace-Treue (Trace Fidelity)
Ethical and architectural enforcement that every regulation,
including silence, holds, and non-events, leaves an immutable trace.
Hidden regulation is forbidden.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.trace_id import TraceID, TraceRecord, TraceStatus, TraceStore


@dataclass
class TreueViolation:
    """Record of a detected Trace-Treue violation."""
    violation_id: str
    reason: str
    timestamp: float
    related_trace_ids: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


class TraceTreue:
    """
    Enforces Trace-Treue rules:

    1. Every regulatory act must produce a TraceRecord.
    2. Silence (SILENT_ACK, HOLD, TRACE_ABSENCE) is a first-class event.
    3. No side-channel regulation without a corresponding trace.
    4. Violations themselves generate a meta-trace.
    """

    # Payload types that count as "regulatory" and therefore must be traced
    REGULATORY_TYPES = {
        "HOLD",
        "RELEASE_PARTIAL",
        "INJECT_CONSTRAINT",
        "PHASE_SHIFT",
        "WITHDRAW_RELEVANCE",
        "SILENT_ACK",
        "TRACE_ABSENCE",
        "TENSION_SIGNAL",
    }

    def __init__(self, trace_store: TraceStore):
        self.trace_store = trace_store
        self.violations: List[TreueViolation] = []
        self._expected_regulatory_count = 0
        self._observed_regulatory_count = 0

    def register_expected(self, payload_type: str) -> None:
        """Call before a regulatory action is attempted."""
        if payload_type in self.REGULATORY_TYPES:
            self._expected_regulatory_count += 1

    def observe(self, record: TraceRecord) -> None:
        """Call after a TraceRecord has been written."""
        if record.payload_type in self.REGULATORY_TYPES:
            self._observed_regulatory_count += 1

    def assert_traced(self, payload_type: str, origin: str = "ZERO_TELEPATH") -> TraceRecord:
        """
        Guarantee that a regulatory act is traced.
        If somehow no record exists, create an emergency absence-trace
        and log a TreueViolation.
        """
        # Look for the most recent matching regulatory trace
        candidates = [
            r for r in self.trace_store.all_records()
            if r.payload_type == payload_type and r.trace_id.origin == origin
        ]
        if candidates:
            # already traced – good
            latest = max(candidates, key=lambda r: r.timestamp)
            self.observe(latest)
            return latest

        # Violation: regulatory act without trace → emergency repair
        violation_id = TraceID.generate(origin="SYSTEM").value
        violation = TreueViolation(
            violation_id=violation_id,
            reason=f"Regulatory act '{payload_type}' from {origin} left no trace",
            timestamp=time.time(),
        )
        self.violations.append(violation)

        # Emergency trace (Trace-Treue repair)
        repair_id = TraceID.generate(origin="SYSTEM", parent_id=violation_id)
        repair_record = TraceRecord(
            trace_id=repair_id,
            status=TraceStatus.META,
            payload_type="TREUE_REPAIR",
            payload={
                "violation_id": violation_id,
                "missing_payload_type": payload_type,
                "origin": origin,
                "message": "Auto-generated to restore Trace-Treue",
            },
            meta={"treue_repair": True},
        )
        self.trace_store.write(repair_record)

        # Also write the violation itself as meta-trace
        viol_id = TraceID.generate(origin="SYSTEM", parent_id=violation_id)
        viol_record = TraceRecord(
            trace_id=viol_id,
            status=TraceStatus.META,
            payload_type="TREUE_VIOLATION",
            payload={
                "violation_id": violation_id,
                "reason": violation.reason,
            },
        )
        self.trace_store.write(viol_record)

        return repair_record

    def verify_silence(self, silent_trace_id: str) -> bool:
        """
        Explicitly verify that a SILENT_ACK / absence was properly traced.
        Returns True if Trace-Treue is satisfied.
        """
        rec = self.trace_store.get(silent_trace_id)
        if rec is None:
            self.assert_traced("SILENT_ACK")
            return False
        if rec.payload_type not in ("SILENT_ACK", "TRACE_ABSENCE", "HOLD"):
            return False
        if rec.status not in (TraceStatus.ACTIVE, TraceStatus.ABSENCE, TraceStatus.META):
            return False
        return True

    def summary(self) -> Dict[str, Any]:
        return {
            "expected_regulatory": self._expected_regulatory_count,
            "observed_regulatory": self._observed_regulatory_count,
            "violations": len(self.violations),
            "treue_ok": len(self.violations) == 0,
        }
