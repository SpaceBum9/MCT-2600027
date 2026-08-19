"""
MCT-2600027 – Orchestrator
Wires HAL, Zero Telepath and the para Border into a running system.
"""

from __future__ import annotations

from core.trace_id import TraceStore
from core.collision_handler import CollisionHandler
from core.trace_treue import TraceTreue
from border.protocol import ParaBorder
from dual_pol.hal import HAL
from dual_pol.zero_telepath import ZeroTelepath


class Orchestrator:
    """
    Minimal autonomous wiring of the Dual-Pol system.
    Trace-Treue is enforced on every Zero Telepath regulatory act.
    """

    def __init__(self):
        self.trace_store = TraceStore()
        self.collision_handler = CollisionHandler(self.trace_store)
        self.treue = TraceTreue(self.trace_store)
        self.border = ParaBorder(self.trace_store)
        self.hal = HAL(self.border, self.trace_store)
        self.zero = ZeroTelepath(self.border, self.trace_store, treue=self.treue)

        # Cross-register listeners so both poles see Border traffic
        self.border.register_listener(self.hal.on_border_message)
        self.border.register_listener(self.zero.on_border_message)

    def status(self) -> dict:
        return {
            "border": self.border.get_state(),
            "trace_count": len(self.trace_store.all_records()),
            "collisions": self.trace_store.list_collisions(),
            "open_collision_events": len(self.collision_handler.list_open_collisions()),
            "quarantine_count": len(self.collision_handler.list_quarantine()),
            "trace_treue": self.treue.summary(),
        }

    def demo_cycle(self) -> None:
        """One short autonomous demonstration cycle."""
        print("=== MCT-2600027 Demo Cycle ===")

        # HAL offers a form
        offer = self.hal.offer_form(
            content={"action": "allocate_resource", "target": "payment_department", "amount": 42},
            relevance=0.95,
        )
        print(f"HAL offer_form → {offer.trace_id.value}")

        # Zero Telepath responds with a phase shift + soft constraint
        shift = self.zero.phase_shift(delta=0.15)
        print(f"ZeroTelepath phase_shift → {shift.phase_vector}")

        constraint = self.zero.inject_constraint({"max_parallel_allocations": 1})
        print(f"ZeroTelepath constraint → {constraint.payload}")

        # HAL requests potential
        req = self.hal.request_potential(purpose="legal_payment_execution")
        print(f"HAL request_potential → {req.trace_id.value}")

        # Zero Telepath holds, then partially releases
        hold = self.zero.hold(reason="integrity_check")
        print(f"ZeroTelepath HOLD → {hold.payload}")

        release = self.zero.release_partial(amount=0.4, content={"scope": "limited_trial"})
        print(f"ZeroTelepath RELEASE_PARTIAL → {release.payload}")

        # Structured silence
        silence = self.zero.silent_ack()
        print(f"ZeroTelepath SILENT_ACK → {silence.trace_id.value}")

        print("\n--- System Status ---")
        print(self.status())
        print("=== Cycle complete ===")
