import {
  directedPairCount,
  pairReport,
  type CvdMode,
  type PairReport,
} from "./a11y";
import { bestOnColor, onHex, slotFormats } from "./color";
import {
  SLOT_LABELS,
  SLOT_TOKENS,
  type Harmony,
  type Slot,
} from "./palette";

export const SOS_VERSION = "3.0";

export const SLOT_ROLES = [
  { id: "tinte", label: "Tinte" },
  { id: "erde", label: "Erde" },
  { id: "marke", label: "Marke" },
  { id: "dunst", label: "Dunst" },
  { id: "papier", label: "Papier" },
] as const;

export type SosNode = {
  index: number;
  token: string;
  label: string;
  role: string;
  roleId: string;
  hex: string;
  hsl: string;
  hslChannels: string;
  rgb: string;
  rgbChannels: string;
  on: string;
};

export type SosCoupling = {
  from: string;
  to: string;
  fromIndex: number;
  toIndex: number;
  ratio: number;
  wcag: PairReport["grade"];
  lc: number;
  aa: boolean;
};

export type SosManifest = {
  sos: typeof SOS_VERSION;
  name: "Chrona";
  harmony: Harmony;
  vision: CvdMode;
  systems: SosNode[];
  overlays: { id: string; label: string }[];
  couplings: SosCoupling[];
  recommended: {
    fg: string;
    bg: string;
    ratio: number;
    wcag: PairReport["grade"];
  };
  aa: { pass: number; total: number };
};

export function sosNodes(slots: Slot[]): SosNode[] {
  return slots.map((slot, i) => {
    const fmt = slotFormats(slot);
    const role = SLOT_ROLES[i] ?? SLOT_ROLES[2];
    return {
      index: i,
      token: SLOT_TOKENS[i] ?? `n${i}`,
      label: SLOT_LABELS[i] ?? String(i + 1),
      role: role.label,
      roleId: role.id,
      hex: fmt.hex,
      hsl: fmt.hsl,
      hslChannels: fmt.hslChannels,
      rgb: fmt.rgb,
      rgbChannels: fmt.rgbChannels,
      on: onHex(bestOnColor(slot.h, slot.s, slot.l)),
    };
  });
}

export function sosCouplings(slots: Slot[]): SosCoupling[] {
  const edges: SosCoupling[] = [];
  for (let fg = 0; fg < slots.length; fg++) {
    for (let bg = 0; bg < slots.length; bg++) {
      if (fg === bg) continue;
      const report = pairReport(slots, fg, bg);
      edges.push({
        from: SLOT_TOKENS[fg] ?? "i",
        to: SLOT_TOKENS[bg] ?? "v",
        fromIndex: fg,
        toIndex: bg,
        ratio: Number(report.ratio.toFixed(2)),
        wcag: report.grade,
        lc: Number(report.lc.toFixed(1)),
        aa: report.bodyAA,
      });
    }
  }
  return edges;
}

export function recommendedPair(slots: Slot[]): PairReport {
  const preferred = pairReport(slots, 0, Math.max(slots.length - 1, 0));
  if (preferred.bodyAA) return preferred;
  let best = preferred;
  for (let fg = 0; fg < slots.length; fg++) {
    for (let bg = 0; bg < slots.length; bg++) {
      if (fg === bg) continue;
      const next = pairReport(slots, fg, bg);
      if (next.ratio > best.ratio) best = next;
    }
  }
  return best;
}

export function undirectedAaPairs(slots: Slot[]) {
  const seen = new Set<string>();
  const pairs: { a: number; b: number; ratio: number }[] = [];
  for (const edge of sosCouplings(slots)) {
    if (!edge.aa) continue;
    const key = [edge.fromIndex, edge.toIndex].sort((x, y) => x - y).join("-");
    if (seen.has(key)) continue;
    seen.add(key);
    pairs.push({ a: edge.fromIndex, b: edge.toIndex, ratio: edge.ratio });
  }
  return pairs;
}

export function buildSosManifest(
  slots: Slot[],
  harmony: Harmony,
  vision: CvdMode,
): SosManifest {
  const rec = recommendedPair(slots);
  const counts = directedPairCount(slots);
  return {
    sos: SOS_VERSION,
    name: "Chrona",
    harmony,
    vision,
    systems: sosNodes(slots),
    overlays: [
      { id: "contrast", label: "Kontrast · WCAG 2 / APCA" },
      { id: "vision", label: "Sehen · Farbfehlsicht" },
    ],
    couplings: sosCouplings(slots),
    recommended: {
      fg: SLOT_TOKENS[rec.fg] ?? "i",
      bg: SLOT_TOKENS[rec.bg] ?? "v",
      ratio: Number(rec.ratio.toFixed(2)),
      wcag: rec.grade,
    },
    aa: { pass: counts.aa, total: counts.total },
  };
}

export function buildCssVariables(slots: Slot[]) {
  const nodes = sosNodes(slots);
  const rec = recommendedPair(slots);
  const counts = directedPairCount(slots);
  const lines: string[] = [
    `/* Chrona · SoS ${SOS_VERSION} */`,
    ":root {",
  ];
  for (const node of nodes) {
    lines.push(`  /* ${node.label} · ${node.role} */`);
    lines.push(`  --sos-${node.token}: ${node.hex};`);
    lines.push(`  --sos-${node.token}-hsl: ${node.hslChannels};`);
    lines.push(`  --sos-${node.token}-rgb: ${node.rgbChannels};`);
    lines.push(`  --sos-${node.token}-on: ${node.on};`);
    lines.push(`  --sos-${node.roleId}: var(--sos-${node.token});`);
    lines.push(`  --sos-color-${node.index + 1}: var(--sos-${node.token});`);
  }
  const fg = nodes[rec.fg];
  const bg = nodes[rec.bg];
  lines.push("  /* Semantik · empfohlene Kopplung */");
  lines.push(`  --sos-fg: ${fg?.hex ?? "#141310"};`);
  lines.push(`  --sos-bg: ${bg?.hex ?? "#F4F1EA"};`);
  lines.push(`  --sos-fg-on-bg: ${rec.ratio.toFixed(2)};`);
  lines.push(`  --sos-aa-pairs: ${counts.aa};`);
  lines.push(`  --sos-brand: var(--sos-iii);`);
  lines.push(`  --sos-ink: var(--sos-i);`);
  lines.push(`  --sos-paper: var(--sos-v);`);
  lines.push("}");
  return lines.join("\n");
}

export function buildSosJson(
  slots: Slot[],
  harmony: Harmony,
  vision: CvdMode,
) {
  return `${JSON.stringify(buildSosManifest(slots, harmony, vision), null, 2)}\n`;
}
