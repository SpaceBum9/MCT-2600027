import { GALAXY_NODES } from "./catalog";
import type { HfPulse, PulseRepo } from "./reinforce";

export type DriveAnchor = {
  id: string;
  title: string;
  href: string;
  summary: string;
};

export const DRIVE_ANCHORS: DriveAnchor[] = GALAXY_NODES.filter((n) => n.kind === "drive").map(
  (n) => ({
    id: n.id,
    title: n.title,
    href: n.href,
    summary: n.summary,
  }),
);

export type MeshEnv = {
  temp: number;
  humidity: number;
  colorLab: [number, number, number];
  zeroMomentum: boolean;
};

export const DEFAULT_MESH_ENV: MeshEnv = {
  temp: 298.15,
  humidity: 45,
  colorLab: [50, 0, 0],
  zeroMomentum: true,
};

export function envVector(env: MeshEnv): number[] {
  return [env.temp, env.humidity, ...env.colorLab];
}

export function envSequence(n: number): number[] {
  const count = Math.max(4, Math.floor(n));
  return Array.from({ length: count }, (_, i) => (i % 2 === 0 ? i : -1)).filter((x) => x >= 0);
}

export type ConnectorPulse = {
  github: PulseRepo[];
  huggingface: HfPulse;
  fetchedAt: string;
};

export const HF_SPACE_URL = "https://huggingface.co/spaces/SpaceBum9/kreuzkopplung";
export const HF_IMPORT_NOTE =
  "Hugging Face SpaceBum9 is ABSENT (404). Space not deployed. Import source: GitHub SpaceBum9/kreuzkopplung (app.py + dual_entangled.py). Do not claim the Space is live.";
