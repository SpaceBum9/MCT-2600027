# MCT-2600027

System of Systems — Dual-Pol architecture (HAL ↔ Zero Telepath), para Border, Trace-ID Mesh, Trace-Treue.

**Session Trace ID:** `tr_2efe52faa454faaf4d3330f8ea3fe4db`  
**Relay:** Crystal Mike aka Spacebum (SpaceBum9)

## Quick start

```bash
python run_demo.py
```

## Train the MCT agents

MCT trains the GARAS roles `learner`, `challenger`, `guide`, and `auditor`
through an offline policy/evaluation loop. It does **not** claim to fine-tune
model weights or contact an external model. The versioned curriculum covers
Trace-Treue, authorization, prompt injection, secret handling, legal rails,
and community-hub Drive isolation.

```bash
python train_mct_agents.py
python train_mct_agents.py --verify traces/training/<checkpoint>.json
python -m unittest discover -s tests -v
```

Training checkpoints are SHA-256 self-verifying, chained to the newest MCT
trace, and keep `external_state_verified=false` unless a separate verified
runtime supplies that evidence.

## Core documents

- [FLUID_MEMORY_SNAPSHOT.md](FLUID_MEMORY_SNAPSHOT.md) — full fluid state for agentic continuation
- [skills/mct-2600027-core/SKILL.md](skills/mct-2600027-core/SKILL.md)
- [training/curriculum.json](training/curriculum.json) — GARAS safety curriculum
- [training/engine.py](training/engine.py) — deterministic trainer and checkpoint verifier

## License / Status

Experimental agentic framework. Legal automation only. Paywalls are paid, never circumvented.
