# GPT GitHub Delta Wake — iOS adapter v1

Purpose: bridge a GitHub delta to an iOS Shortcut that opens the GPT review path. The shortcut is transport/wake only and receives no merge, execute, financial, or quorum authority.

Flow:

```
GitHub delta -> GitHub Actions -> wake endpoint/push adapter -> iOS Shortcut -> ChatGPT/GPT
                                                            -> GitHub/Notion review trace
```

## Contract

- GitHub is persistent source state.
- Notion remains decision/trace state.
- The iOS Shortcut is a wake/transport adapter, not an actor with decision authority.
- The wake payload contains references only. No credentials or repository secrets.
- GPT must independently re-read the referenced GitHub state before voting.
- Duplicate delivery is harmless: consumers deduplicate by `delivery_id`.
- Failure to wake GPT does not imply approval. Required missing quorum => HOLD.
- MEV may substitute an allowed machine slot but never expands its authority.
- Banking Philosophy boundaries remain unchanged: no transfer or spend authority is granted by this adapter.

## Wake payload

```json
{
  "schema": "sos.gpt-wake.v1",
  "repo": "SpaceBum9/MCT-2600027",
  "event": "push|pull_request|pull_request_review|issue_comment|workflow_dispatch",
  "ref": "<branch/pr/ref>",
  "sha": "<exact commit/head sha>",
  "delivery_id": "<stable run/event id>",
  "to": "GPT",
  "action": "observe_and_review",
  "live_rail": false
}
```

The external wake adapter is intentionally not hard-coded. iOS Shortcuts cannot be treated as a public webhook listener; an authorized push/app/endpoint bridge must deliver the payload to the device.

## iOS Shortcut contract

Shortcut name: `SoS GPT Delta Wake`

1. Receive wake payload from the chosen authorized adapter.
2. Validate `schema == sos.gpt-wake.v1` and `to == GPT`.
3. Extract repo, event, ref, sha, delivery_id.
4. Open ChatGPT with a compact instruction containing those references.
5. GPT independently fetches current GitHub state and compares the exact SHA before any ballot/comment.
6. If state changed, review the new exact head. If evidence is incomplete, defer/HOLD.
7. Record any resulting decision through the existing GitHub/Notion trace path.

No token, API key, secret, merge command, execute command, or payment instruction belongs in the Shortcut payload.
