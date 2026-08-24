import { GALAXY, SAI_STEPS, nodeById, resolveTarget, type GalaxyNode } from "./catalog";

export type SaiTrace = {
  source: string;
  origin: "Crystal Mike";
  core: "HAL";
  targetId: string;
  targetName: string;
  path: string[];
};

export function buildTrace(source: string, text: string, targetId?: string): SaiTrace {
  const target: GalaxyNode =
    (targetId ? nodeById(targetId) : undefined) ?? resolveTarget(text);
  return {
    source: source.trim() || "operator",
    origin: "Crystal Mike",
    core: "HAL",
    targetId: target.id,
    targetName: target.title,
    path: [source.trim() || "operator", SAI_STEPS[1], SAI_STEPS[2], target.title, SAI_STEPS[4]],
  };
}

export function traceLine(t: SaiTrace) {
  return t.path.join(" → ");
}

export function defaultTrace(): SaiTrace {
  return buildTrace("operator", "HAL");
}

export { GALAXY, SAI_STEPS };
