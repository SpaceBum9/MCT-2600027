# MCT-2600027-CMD

Open source. MIT.

**BILO 2026 · HAL · Crystal Mike**

Agent-Orchestrator mit verschränkten Zyklen.

`Quelle → Crystal Mike → HAL → Zielknoten → Reinforcement`

## Automationen

In der App: Entangle 45s (solange CMD offen), Oracle-Refresh, iCloud-Inbox.
Grok: System-Updater 09:00, Oracle-Cycle 21:00 Europe/Berlin.

Paare, `b = −tanh(a)`:

- Teacher ⇌ Learner
- Challenger ⇌ Referee
- Scout ⇌ Keeper
- Oracle ⇌ iCloud

DAG: scout-keep → oracle-cloud → teach-learn → challenge-ref

## Oracle

SoundCloud (oEmbed), Bandcamp — **Metadaten only**.

Suno — **operator opt-in audio-rip** for allowlisted song IDs only.
See [oracle/AUDIO-RIP.md](./oracle/AUDIO-RIP.md). Preserve C2PA / `sga` / `fingerprint.v4`. No watermark strip. `harvest: false`. Not training data.

## iCloud

Kein Sign in with Apple. Share Sheet, Datei, iOS-Shortcut → Inbox (Konto).

## Grenzen

Keine Credentials. Keine Rohbeweise. Kein Halt auf `jonas-g`.
Kein mass-rip. Kein C2PA-strip. `execute: false` on live orders.

[MIT](./LICENSE)
