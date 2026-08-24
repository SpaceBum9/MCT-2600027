# Open work requiring a merge decision

These branches were deliberately not folded into the snapshot import.

| Source work | State | Decision required before porting |
|---|---|---|
| `MCT-2600027#1` GARAS training | open PR in target | Review checkpoint semantics, generated trace policy, and whether the training package belongs at root or under `packages/garas-training/`. |
| `MCT-2600027-CMD#2` registry/probes/connectors/interoception/scheduler/limiter | open PR in legacy source | Split deterministic registry/limiter/model code from network and scheduler adapters. Resolve compile coverage gaps, arbitrary xAI base-URL credential forwarding, mesh activation/authentication, delivery verification/timestamp ordering, Urlaubsgeld schema mismatch, and drift-baseline behavior before porting. |
| `mct-170021-zero-tier-quantum-skills-tools-mcp-connectors#1` orchestrator/router/gateway | open PR in legacy source | Run with dependencies, then decide durable replay storage, key rotation, immutable audit, rate limits, controller-side authorization, and human approval for admin/execute/halt. |
| `MCT-2600027#2` trace interoperability | open issue | Keep deferred until trace ID versus checkpoint digest semantics and privacy-redacted export fixtures are accepted. |

Safest sequence: review and port pure deterministic modules first; add provider/network adapters only as separately gated packages with fixed endpoints and explicit operator enablement.
