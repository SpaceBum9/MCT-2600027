# DT2 Live Set Synthesis — GPT Remote Handoff

TRACE_ID: DT2-LIVE-GPT-REMOTE-20260915-2317-CET
STATUS: HANDOFF / UNMERGED
LIVE_RAIL: false

## Objective
Unify the useful knowledge/assets of the Custom GPTs **Live Assistant** and **Music Gear Buddy** with the DT2 Live Set Synthesis project, Nikita, Ableton Live 12 and the existing ZeroTier transport.

## Target topology

DT2 / hardware <-> Ableton Live 12 <-> Max for Live / Producer Pal
                                      |
                                      | MCP / API
                                      v
                              DT2 synthesis gateway
                              /        |          \
                    Live Assistant  Gear Buddy   Nikita
                              \        |          /
                                      v
                                    GPT

## Required interfaces

### live.*
- live.get_set
- live.get_tracks
- live.get_devices
- live.get_clips
- live.get_transport
- live.get_parameters
- live.set_parameter
- live.mute_track
- live.launch_clip
- live.create_clip
- live.write_notes

### gear.*
- gear.lookup
- gear.manual_search
- gear.midi_map
- gear.sysex_capabilities
- gear.routing

### nikita.*
- nikita.get_state
- nikita.search_dt2_knowledge
- nikita.propose_pattern
- nikita.propose_transition
- nikita.validate_mutation
- nikita.submit_observation

## Knowledge migration
Treat Live Assistant and Music Gear Buddy as source/asset providers. Do not assume one Custom GPT can directly read another GPT's private knowledge. Export or mirror their useful source assets into a shared knowledge layer that the gateway can query with provenance.

## Transport
Existing ZeroTier One mesh is the preferred private transport between the Ableton/Max host and Nikita-side services. Do not expose Producer Pal / MCP ports directly to the public Internet. Runtime discovery still needs to establish the actual ZeroTier host/IP, listening port, MESH_CONTROLLER_URL and service identity. Never log or commit auth tokens.

## Closed-loop synthesis target
1. Read current Live 12 state.
2. Retrieve verified gear/manual constraints.
3. Retrieve Nikita DT2 synthesis state.
4. Generate the smallest progressive-overdub mutation.
5. Validate mutation before execution.
6. Apply only through an explicitly enabled Live rail.
7. Observe resulting state/audio metrics.
8. Persist observation with provenance and TRACE_ID.

## DT2 musical invariant
Arrangement is progressive overdub rather than intro/break/drop/bridge templating. Prefer continuity, track mutes, fills, BILO breaks, density changes and controlled pattern mutations. Preserve stable groove anchors unless a transition explicitly calls for changing them.

## Safety / execution boundary
LIVE_RAIL=false by default. Discovery and read-only validation are allowed. Do not execute destructive project changes, expose secrets, or merge this branch merely because the handoff exists. Writes to Ableton require an explicit enabled execution rail and a validated target.

## GPT Remote resume token
Use this exact trace to resume cross-surface work:

`TRACE_ID=DT2-LIVE-GPT-REMOTE-20260915-2317-CET`

On resume: locate this file, verify current branch/head, inspect any newer trace-bearing commits/comments, then continue from the newest proven state rather than reconstructing state from chat memory.
