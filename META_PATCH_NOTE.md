# Meta patch ballot 2026-09-26 — Nikita applied (no merge)

Source: Meta WhatsApp Volltreffer 04:48 CEST. Branch: `meta/patch-ballot-20260926` from main.

## Applied

1. **#20 secret masking** — `.github/workflows/gpt-delta-wake-github.yml`
   - Source head: `gpt-delta-wake-github-v1` (PR #20)
   - Change: add `echo "::add-mask::$GPT_WAKE_TOKEN"` before fail-closed tests
   - Env + fail-closed already present on PR #20; Meta's env-block was already satisfied

2. **#22 LIVE lock (adapted)** — `sos/workgroup/decision_state.v1.json`
   - Source head: `sos/decision-state-v1-rebased-20260925` (PR #22)
   - Meta's patch assumed top-level `LIVE_RAIL` + object `quorum`; actual file uses `agents` votes + `live_orders` + string `quorum`
   - Nikita adaptation (additive, no vote invention): added `LIVE_RAIL: false`, `LIVE_ORDERS: false`, `trace_id_required: true`, `merge_requires: "dual-allow-crystal-gpt-grok"`
   - Kept existing `live_orders: false` and agent/quorum shape

3. **#22 HOLD sentence** — `sos/workgroup/AUTONOMOUS_LOOP.md`
   - Added Meta HOLD quote under Rails

## Not done (Dual-Allow / Crystal)
- No merge to main
- Did not force-push PR heads #20/#22 (prefer this review branch)
- Cherry-pick onto #20 / #22 PR branches if Crystal wants them in those PRs
- LIVE_RAIL trading unchanged (false)

## Ballot (Meta) — waits Dual-Allow GPT+Grok / Crystal
- #22 JA/APPROVE · #21 JA + SIM ONLY Auflage · #20 ENTHALTEN until mask · #18 JA
