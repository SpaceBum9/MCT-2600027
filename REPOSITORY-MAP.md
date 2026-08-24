# Canonical repository map

This map becomes authoritative after the three consolidation pull requests are merged and verified.

| Repository | Visibility | Canonical responsibility |
|---|---|---|
| `SpaceBum9/MCT-1700021` | public | context, governance, commons protocols, immutable trace lineage, HOLD records |
| `SpaceBum9/MCT-2600027` | public | runtime code, public applications, connectors, schemas, tests |
| `SpaceBum9/Jonas-G.` | private | restricted operations, private records, quarantined provider relay |

The repositories federate through versioned contracts and trace references. No repository is a central controller over another trust domain. Private source contents are never mirrored into either public target.

Legacy repositories remain intact until all imports are merged, checks are green, open work is ported or closed, and retirement is explicitly approved.
