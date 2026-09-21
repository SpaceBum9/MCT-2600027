# GPT GitHub Delta Wake v1

Purpose: wake GPT directly from GitHub events without an iOS device.

Flow:

```
GitHub delta -> GitHub Actions -> authorized GPT wake endpoint -> GPT run
                                                    |
                                                    +-> independent GitHub reread
                                                        -> exact-SHA review/ballot
```

## Contract

- GitHub is the source of the wake event, not evidence of approval.
- The receiver accepts only authenticated POST requests.
- The packet carries repository references, event type, ref, exact SHA and delivery ID. It carries no repository credential.
- GPT independently fetches the current GitHub state before reviewing or voting.
- A changed SHA invalidates any SHA-bound ballot and requires a fresh review.
- Duplicate deliveries are deduplicated by `delivery_id`.
- Failure to wake, authenticate or verify means HOLD/no action.
- Wake grants no merge, execute, financial, ownership, quorum or vendor authority.

## Required repository secrets

- `GPT_WAKE_URL`: HTTPS endpoint of the authorized GPT/agent ingress.
- `GPT_WAKE_TOKEN`: random bearer secret shared only with that ingress.

Do not commit either value.

## Receiver behavior

The authorized GPT ingress must validate the bearer token and `schema == sos.gpt-wake.v1`, deduplicate `delivery_id`, then start a GPT review with the packet references. GPT must re-read GitHub rather than trusting event content.

This repository deliberately does not embed an OpenAI API key or attempt to call a consumer ChatGPT conversation. The external ingress is the authorization boundary and is configured separately.
