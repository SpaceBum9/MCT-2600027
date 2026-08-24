# Oracle CMD — audio-rip permission

Operator opt-in: **2026-08-24T15:57Z** · seated teleprompter SpaceBum9.
This lifts the 1507Z *No audio/mp3 content ingest* limit **only** as scoped below.

## Grant

| Field | Value |
|-------|-------|
| who | Oracle CMD (pair Oracle ⇌ iCloud) |
| what | Fetch official Suno audio for allowlisted IDs |
| not | SoundCloud/Bandcamp rip, third-party scrape, watermark strip |
| harvest | false |
| training | false |
| C2PA | keep `trainedAlgorithmicMedia` + `com.suno.fingerprint.v4` |
| execute | false (not a live order, not K-1 rail) |

Allowlist: [allowlist.json](./allowlist.json).

## Wheel

META locks frequency. SIRI may ACTION lyrics (USLT). APL does not become a cloud id.
SAI listens. Does not fine-tune.

## Halt

Drop an ID from the allowlist or set `enabled: false`. Bodies never go to git.
