# iOS Wake Relay

This relay closes the server-side half of:

`GitHub Delta -> HTTPS relay -> iOS push/automation endpoint -> SoS GPT Delta Wake shortcut -> GPT review`

## Configuration

Relay secrets:
- `INBOUND_TOKEN`: must equal GitHub repository secret `GPT_WAKE_TOKEN`.
- `PUSH_URL`: HTTPS endpoint supplied by the chosen iOS push/automation provider.
- `PUSH_TOKEN`: downstream token when the provider requires bearer auth.

GitHub repository secret:
- `GPT_WAKE_URL`: deployed relay URL.
- `GPT_WAKE_TOKEN`: same random secret as relay `INBOUND_TOKEN`.

Never commit any of those values.

## Shortcut

Create an iOS Shortcut named **SoS GPT Delta Wake**. Its input contract is the `payload` object. It must reject input unless:
- `schema == sos.gpt-wake.v1`
- `to == GPT`

It then constructs this instruction:

`GitHub delta wake. Repo: <repo>. Event: <event>. Ref: <ref>. Expected SHA: <sha>. Delivery: <delivery_id>. Independently fetch current state, verify the exact SHA, then observe/review under existing SoS quorum/HOLD rules. Do not infer approval from this wake.`

The final device-specific action may open/share that instruction into ChatGPT. iOS decides which third-party push services can automatically invoke a shortcut; the relay therefore keeps the downstream provider replaceable.

## Authority

Wake is transport only. No merge, execute, financial, ownership, quorum, or vendor authority is conveyed.
