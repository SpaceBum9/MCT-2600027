import { clamp, hueNorm, type Hsl } from "./color";

export const SLOT_COUNT = 5;
export const SLOT_LABELS = ["I", "II", "III", "IV", "V"] as const;
export const SLOT_TOKENS = ["i", "ii", "iii", "iv", "v"] as const;

export type Harmony =
  | "analog"
  | "complement"
  | "split"
  | "triad"
  | "time"
  | "chaos";

export const HARMONY_LABELS: Record<Harmony, string> = {
  analog: "Analog",
  complement: "Komplementär",
  split: "Split",
  triad: "Triade",
  time: "Zeit",
  chaos: "Chaos",
};

export type Slot = Hsl & { locked: boolean };

export const DEFAULT_SLOTS: Slot[] = [
  { h: 28, s: 36, l: 18, locked: false },
  { h: 18, s: 54, l: 38, locked: false },
  { h: 32, s: 62, l: 52, locked: false },
  { h: 48, s: 34, l: 70, locked: false },
  { h: 210, s: 16, l: 86, locked: false },
];

const ROLE_SL = [
  { s: 40, l: 18 },
  { s: 54, l: 36 },
  { s: 64, l: 50 },
  { s: 38, l: 68 },
  { s: 22, l: 84 },
] as const;

function rand() {
  return Math.random();
}

export function timeHue(date = new Date()) {
  return hueNorm(
    (date.getHours() % 12) * 30 + date.getMinutes() * 0.5 + date.getSeconds() * 0.0083,
  );
}

function huesFor(harmony: Harmony, base: number): number[] {
  switch (harmony) {
    case "analog":
      return [-36, -16, 0, 18, 38].map((d) => hueNorm(base + d));
    case "complement":
      return [0, 14, 180, 194, 28].map((d) => hueNorm(base + d));
    case "split":
      return [0, 150, 210, -22, 32].map((d) => hueNorm(base + d));
    case "triad":
      return [0, 120, 240, 18, 132].map((d) => hueNorm(base + d));
    case "time":
      return [-48, -16, 0, 32, 196].map((d) => hueNorm(base + d));
    case "chaos":
      return Array.from({ length: SLOT_COUNT }, () => rand() * 360);
  }
}

function jitter(n: number, amount: number) {
  return n + (rand() * 2 - 1) * amount;
}

export function generateSlots(harmony: Harmony, previous: Slot[]): Slot[] {
  const lockedHue = previous.find((s) => s.locked);
  const base =
    harmony === "time"
      ? timeHue()
      : lockedHue
        ? lockedHue.h
        : rand() * 360;
  const hues = huesFor(harmony, base);

  return previous.map((slot, i) => {
    if (slot.locked) return slot;
    if (harmony === "chaos") {
      return {
        h: hues[i] ?? rand() * 360,
        s: 18 + rand() * 70,
        l: 14 + rand() * 72,
        locked: false,
      };
    }
    const role = ROLE_SL[i] ?? ROLE_SL[2];
    return {
      h: hues[i] ?? base,
      s: clamp(jitter(role.s, 6), 12, 78),
      l: clamp(jitter(role.l, 4), 10, 92),
      locked: false,
    };
  });
}

export function serializeSlots(slots: Slot[]) {
  return slots
    .map(
      (s) =>
        `${Math.round(s.h)},${Math.round(s.s)},${Math.round(s.l)},${s.locked ? 1 : 0}`,
    )
    .join("|");
}

export function parseSlots(raw: string | null | undefined): Slot[] | null {
  if (!raw) return null;
  const parts = raw.split("|");
  if (parts.length !== SLOT_COUNT) return null;
  const slots: Slot[] = [];
  for (const part of parts) {
    const [hs, ss, ls, lock] = part.split(",");
    const h = Number(hs);
    const s = Number(ss);
    const l = Number(ls);
    if (![h, s, l].every((n) => Number.isFinite(n))) return null;
    slots.push({
      h: hueNorm(h),
      s: clamp(s, 0, 100),
      l: clamp(l, 0, 100),
      locked: lock === "1",
    });
  }
  return slots;
}

export function hashFromSlots(slots: Slot[]) {
  return slots
    .map((s) => `${Math.round(s.h)}-${Math.round(s.s)}-${Math.round(s.l)}`)
    .join("_");
}

export function slotsFromHash(hash: string): Slot[] | null {
  const cleaned = hash.replace(/^#/, "");
  const parts = cleaned.split("_");
  if (parts.length !== SLOT_COUNT) return null;
  const slots: Slot[] = [];
  for (const part of parts) {
    const [hs, ss, ls] = part.split("-");
    const h = Number(hs);
    const s = Number(ss);
    const l = Number(ls);
    if (![h, s, l].every((n) => Number.isFinite(n))) return null;
    slots.push({
      h: hueNorm(h),
      s: clamp(s, 0, 100),
      l: clamp(l, 0, 100),
      locked: false,
    });
  }
  return slots;
}
