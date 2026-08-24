export const PROJECT_ID = "MCT-2600027-CMD";
export const PROJECT_REV = 1;
export const GH_OWNER = "SpaceBum9";
export const GH_REPO = "MCT-2600027-CMD";
export const GH_URL = `https://github.com/${GH_OWNER}/${GH_REPO}`;
export const CODEX_ISSUE = `${GH_URL}/issues/1`;

export const PIPELINE = [
  { id: "analyze", label: "Analyze", verb: "Bestand lesen" },
  { id: "iterate", label: "Iterate", verb: "Kreuzkopplung" },
  { id: "consolidate", label: "Consolidate", verb: "Schema-Korridor" },
  { id: "ingest", label: "Ingest", verb: "Pulse aufnehmen" },
  { id: "update", label: "Update", verb: "Stand schreiben" },
] as const;

export type PipelineId = (typeof PIPELINE)[number]["id"];

export const DEPARTMENTS = [
  { id: "hal", title: "HAL", path: "/", summary: "Kommando. SAI-Trace. Live-Puls.", group: "kern" },
  { id: "tracer", title: "TracerHubs", path: "/tracer", summary: "Zero-Tier Quantum Architektur. ATM, Impuls = 0.", group: "netz" },
  { id: "tunnel", title: "Tunnel", path: "/tunnel", summary: "Cloudflare. colo, loc, warp.", group: "netz" },
  { id: "updater", title: "Updater", path: "/update", summary: "MCT-2600027 Systemzyklus.", group: "ops" },
  { id: "skills", title: "Skills", path: "/skills", summary: "LLM-Fusion: Grok, Codex, Siri, Knowledge.", group: "ops" },
  { id: "flow", title: "Flow", path: "/flow", summary: "BILO 2026 Flowchart. Control Plane.", group: "kern" },
  { id: "codex", title: "Codex", path: "/codex", summary: "GitHub → Issue → Agent → PR.", group: "ops" },
  { id: "agents", title: "Agents", path: "/agents", summary: "Orchestrator: Teacher, Learner, Challenger.", group: "kern" },
  { id: "lumen", title: "Lumen", path: "/write", summary: "iOS + Apple Intelligence.", group: "produkt" },
] as const;

export type DepartmentId = (typeof DEPARTMENTS)[number]["id"];

export const SAI_ROUTE = ["Quelle", "Crystal Mike", "HAL", "Zielknoten", "Reinforcement"] as const;

export const CONTROL_LAYERS = [
  { id: "control", title: "Control Plane", detail: "Lebenszyklus, Last, Failover. Orchestrator-Core." },
  { id: "transport", title: "Transport", detail: "Cloudflare Tunnels + ZeroTier Mesh, zero-trust." },
  { id: "ingest", title: "Ingestion", detail: "Live-Pulse, Streams, Geo-Routing an Edge-Knoten." },
  { id: "anchor", title: "Semantic Anchoring", detail: "Vektor-Fixpunkte + JSON-Schema. Drift → Feedback." },
] as const;

export function isKernelDay(d = new Date()) {
  return d.getMonth() === 7 && d.getDate() === 19;
}
