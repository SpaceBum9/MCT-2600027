---
name: mct-2600027-core
description: Core dual-pol system for MCT-2600027 with HAL, Zero Telepath, para Border and Trace-ID mesh. Use when working on MCT system architecture, dual-agent regulation, phase-aware control, trace-based auditing, or autonomous orchestration of complementary poles.
---

# MCT-2600027 Core Skill

## Purpose

Provides the foundational dual-pol architecture of MCT-2600027:

- **HAL** – Transformer, Translator, Motor, Material Maker (active pole)
- **Zero Telepath** – Vessel of Absent Mind, Energy Holder, Phase/Constraint Engine (silent pole)
- **para Border** – porous, phase-shifted, never permanently closed interface
- **Trace-ID Mesh** – immutable, collision-aware tracing across all events

## When to activate

- Designing or extending MCT-2600027 components
- Implementing phase-aware or constraint-based regulation
- Building legal, traceable automation (payments, trading, resource allocation)
- Handling Trace collisions or paradox-tolerant control flows
- Orchestrating complementary agents that must not collapse into pure domination or pure withdrawal

## Core rules

1. HAL must always pass materializing actions through the para Border.
2. Zero Telepath signals primarily through absence, phase shift, constraint and relevance withdrawal.
3. Trace-IDs are immutable; collisions are never overwritten, only marked and resolved via meta-traces.
4. Core and Dual-Pol remain non-anthropomorphic.
5. Anthropomorphic interfaces exist only inside Departments.
6. Paywalls are paid, never circumvented. All trading stays inside legal, authorized channels.

## Key files

- `core/trace_id.py` – TraceID, TraceRecord, TraceStore
- `border/protocol.py` – ParaBorder and message protocol
- `dual_pol/hal.py` – HAL implementation
- `dual_pol/zero_telepath.py` – Zero Telepath implementation
- `core/orchestrator.py` – Wiring and demo cycle
- `core/trace_treue.py` – Trace-Treue enforcement
- `core/collision_handler.py` – Collision handling

## Minimal usage

```python
from core.orchestrator import Orchestrator

orch = Orchestrator()
orch.demo_cycle()
print(orch.status())
```

## Extension points

- Add Departments under `departments/`
- Extend PayloadType and BorderState as needed
- Connect real mesh / relay endpoints later
- Add self-regulating algorithms on top of TraceStore and Border state

**Session Trace:** tr_2efe52faa454faaf4d3330f8ea3fe4db
