# Runtime consolidation

`MCT-2600027` is the canonical public runtime monorepo. Existing root runtime code remains in place.

## Imported, disabled-by-default domains

| Source | Source commit | Destination |
|---|---|---|
| `MCT-2600027-CMD` | `c6d5c3960cf49c3182ffba0242e8ebecbb14073e` | `apps/cmd/` |
| `kreuzkopplung` | `c82cdc3ee13637a6f85224aed468d08ae86fcd4f` | `apps/kreuzkopplung/` |
| `crystal-galaxy` | `5242d637b05fb20631d4ad1cecb7b9e05cba3712` | `packages/crystal-galaxy/` |
| `mct-170021-zero-tier-quantum-skills-tools-mcp-connectors` | `1ed8b52490b138680a0df0f162fb0b47102ae3be` | `packages/zero-tier-connectors/` |
| `plasma-toxogon` | `46dc31d888409835723e9a1de84e96d00a60e8a7` | `services/plasma-toxogon/` |

Imports are source snapshots. They are not automatically registered, started, scheduled, granted credentials, or treated as evidence of network reachability. The Oracle files under `apps/cmd/oracle/` remain an isolated opt-in module: allowlist required, C2PA preserved, no mass-rip, `harvest=false`, `execute=false`.

Root safety remains binding: `LIVE_RAIL=false`, deny-before-execute, least privilege, and independent human approval for irreversible operations.
