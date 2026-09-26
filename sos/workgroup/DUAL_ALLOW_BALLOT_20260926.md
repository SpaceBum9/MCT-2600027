# Dual-Allow ballot fuse — 2026-09-26

**Grok voice:** Nikita proxy (Crystal authorized stellvertretend).
**GPT voice:** ask-openai + ASK_WRAPPER (Herr Schneider).
**Meta:** observe/doktern, not Dual-Allow brain.

LIVE_RAIL=false. No trading execute. Nikita does not merge without Crystal when merge_requires names Crystal.

| PR | Grok | GPT | Fuse |
|----|------|-----|------|
| #22 | ja | ja | **DUAL-ALLOW** — workgroup-allow; Crystal may merge |
| #21 | ja + SIM ONLY | nein | SPLIT — defer |
| #20 | enthalten (until mask) | enthalten | ALIGN defer |
| #18 | ja (evidence-only) | nein | SPLIT — defer |
| #23 | ja (docs HOLD) | nein | SPLIT — defer |
| #24 | ja (mask) | enthalten | SPLIT — prefer cherry-pick mask onto #20 |

## Grok notes
- #22: clean rebase of reviewed decision_state slice; docs/schema only.
- #21: sim-only + DENY_WRITE is the safety; approve with SIM ONLY banner, not reject.
- #18: not-quorum is intentional; evidence adapter should land.
- #20: JA after `::add-mask::$GPT_WAKE_TOKEN` on that PR head.

## decision_state.v1.json implication for #22
- grok.vote: approve (proxy confirmed 2026-09-26)
- gpt.vote: approve (API ballot 2026-09-26) — update on merge or follow-up commit on #22 head

## NEXT
1. Crystal merge #22
2. Clarify GPT on #21/#18 or leave SPLIT
3. Fold #24 mask into #20 then re-ballot #20
