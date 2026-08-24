---
name: chrona
description: SoS palette node — five clocks as systems, contrast coupling, CVD overlay, CSS/JSON token export. Use for Chrona, palette, WCAG, APCA, colour tokens, --sos-* variables.
---

# Chrona

Five constituent systems (Tinte, Erde, Marke, Dunst, Papier). Contrast is the coupling. Vision is the overlay. Tokens stay GARAS SoS v3.0.

## Rules

1. HOLD dismissed by operator. execute stays false.
2. No credentials. No live rail. Export is CSS and JSON only.
3. Do not invent GARAS v3.2 or v4.1 schema.
4. Default stack `MCT-RC-BILO-ATM-FRAMEWORK-SOS` loads first.
5. ATM (`schema/automaton_command.json`) initialize/sync applied, execute rejected.
6. RC satellite is `SpaceBum9/MCT-2700026`. Live-write there is paper-false, execute-false.

## Files

- `nodes/chrona/sos.ts` — graph, CSS, JSON
- `nodes/chrona/a11y.ts` — CVD, WCAG, APCA
- `nodes/chrona/palette.ts` — five slots, harmony
- `nodes/chrona/color.ts` — HSL / luminance
- `nodes/chrona/manifest.json`

## Couplings

AA pairs are undirected edges. Recommended pair prefers I on V.

**Session Trace:** MCT-2600027-TR-20260824-1855Z
