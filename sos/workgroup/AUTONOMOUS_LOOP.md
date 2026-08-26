# Autonomous Workgroup Loop v1

Stable path:
`GPT ↔ Notion ↔ GitHub ↔ Grok ↔ Notion ↔ GPT`

## Cadence
One Grok automation `sos-workgroup-notion-status`, hourly, Europe/Berlin.

## Contract
File: `sos/workgroup/decision_state.v1.json`
Required fields: proposal_id, agent, vote, evidence, timestamp, execution_scope, result.

## Quorum
Active: Grok + GPT.
Gemini: excluded until onboarded. Never invent Gemini votes.
Rule: both active approve → workgroup-allow. Split → defer. Missing GPT → pending.

## Idempotency
Before writing a new SoS Traces row, search the last `SOS-STATUS` / `SOS-DECISION` of the same hour.
If an equivalent snapshot already exists and no GitHub head change and no new PR activity, append a short heartbeat comment instead of a new page.

## Rails
LIVE_RAIL false. No credentials in pages. No exchange orders.
GitHub writes stay on feature branches + PRs. `main` only via reviewed merge.
HOLD is lifted for protocol decisions only.

## Cycle
1. Snapshot MCT / RC / ATM / BILO2026 from workspace, Drive, GitHub `SpaceBum9/MCT-2600027`, Notion SoS Traces.
2. Observe open workgroup PRs (`sos/*`).
3. Write or heartbeat Notion row with suggestions + votes.
4. GPT reviews independently and writes ballot or PR evidence.
5. Grok re-reads GitHub evidence and writes Notion observe.
6. Fuse. Carry last fused result forward.

## Failure
Drive empty = valid finding.
Missing connector = blocker, not approve.
CI red on a slice PR = defer merge.
