import {
  clamp,
  contrastRatio,
  gradeContrast,
  hslToRgb,
  relativeLuminance,
  rgbToHex,
  type ContrastGrade,
} from "./color";
import { SLOT_LABELS, type Slot } from "./palette";

export type CvdMode = "none" | "protan" | "deutan" | "tritan" | "achroma";

export const CVD_MODES: CvdMode[] = [
  "none",
  "protan",
  "deutan",
  "tritan",
  "achroma",
];

export const CVD_LABELS: Record<CvdMode, string> = {
  none: "Normal",
  protan: "Protanopie",
  deutan: "Deuteranopie",
  tritan: "Tritanopie",
  achroma: "Achromatopsie",
};

export const CVD_HINTS: Record<CvdMode, string> = {
  none: "Ungefilterte Palette.",
  protan: "Rotblindheit — Rot wirkt dunkler, Rot und Grün fallen zusammen.",
  deutan: "Grünblindheit — häufigste Form, Rot und Grün kaum unterscheidbar.",
  tritan: "Blaublindheit — Blau und Gelb fallen zusammen.",
  achroma: "Keine Farbe, nur Helligkeit.",
};

type Mat3 = readonly [
  number,
  number,
  number,
  number,
  number,
  number,
  number,
  number,
  number,
];

const MACHADO: Record<Exclude<CvdMode, "none" | "achroma">, Mat3> = {
  protan: [
    0.152286, 1.052583, -0.204868, 0.114503, 0.786281, 0.099216, -0.003882,
    -0.048116, 1.051998,
  ],
  deutan: [
    0.367322, 0.860646, -0.227968, 0.280085, 0.672501, 0.047413, -0.01182,
    0.04294, 0.968881,
  ],
  tritan: [
    1.255528, -0.076749, -0.178779, -0.078411, 0.930809, 0.147602, 0.004733,
    0.691367, 0.3039,
  ],
};

function srgbToLin(c: number) {
  const x = c / 255;
  return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
}

function linToSrgb(x: number) {
  const y = x <= 0.0031308 ? 12.92 * x : 1.055 * Math.pow(Math.max(x, 0), 1 / 2.4) - 0.055;
  return clamp(Math.round(y * 255), 0, 255);
}

export function simulateCvd(
  r: number,
  g: number,
  b: number,
  mode: CvdMode,
): [number, number, number] {
  if (mode === "none") return [r, g, b];
  if (mode === "achroma") {
    const y = relativeLuminance(r, g, b);
    const v = linToSrgb(y);
    return [v, v, v];
  }
  const m = MACHADO[mode];
  const rl = srgbToLin(r);
  const gl = srgbToLin(g);
  const bl = srgbToLin(b);
  return [
    linToSrgb(m[0] * rl + m[1] * gl + m[2] * bl),
    linToSrgb(m[3] * rl + m[4] * gl + m[5] * bl),
    linToSrgb(m[6] * rl + m[7] * gl + m[8] * bl),
  ];
}

export function contrastRgb(
  a: [number, number, number],
  b: [number, number, number],
) {
  return contrastRatio(relativeLuminance(...a), relativeLuminance(...b));
}

export function bestOnRgb(r: number, g: number, b: number): "light" | "ink" {
  const lum = relativeLuminance(r, g, b);
  return contrastRatio(lum, 1) >= contrastRatio(lum, 0) ? "light" : "ink";
}

export function apcaLc(
  text: [number, number, number],
  bg: [number, number, number],
) {
  const trc = (c: number) => (c / 255) ** 2.4;
  const yOf = ([r, g, b]: [number, number, number]) =>
    trc(r) * 0.2126729 + trc(g) * 0.7151522 + trc(b) * 0.072175;
  const blkThrs = 0.022;
  const blkClmp = 1.414;
  const clampY = (y: number) =>
    y >= blkThrs ? y : y + (blkThrs - y) ** blkClmp;
  let txtY = clampY(yOf(text));
  let bgY = clampY(yOf(bg));
  if (Math.abs(bgY - txtY) < 0.0005) return 0;
  const scale = 1.14;
  const loClip = 0.1;
  const loOff = 0.027;
  let sapc: number;
  if (bgY > txtY) {
    sapc = (bgY ** 0.56 - txtY ** 0.57) * scale;
    return (sapc < loClip ? 0 : sapc - loOff) * 100;
  }
  sapc = (bgY ** 0.65 - txtY ** 0.62) * scale;
  return (sapc > -loClip ? 0 : sapc + loOff) * 100;
}

export type ApcaGrade = "Lc75" | "Lc60" | "Lc45" | "Lc30" | "Fail";

export function gradeApca(lc: number): ApcaGrade {
  const a = Math.abs(lc);
  if (a >= 75) return "Lc75";
  if (a >= 60) return "Lc60";
  if (a >= 45) return "Lc45";
  if (a >= 30) return "Lc30";
  return "Fail";
}

export const APCA_LABELS: Record<ApcaGrade, string> = {
  Lc75: "Fließtext+",
  Lc60: "Fließtext",
  Lc45: "Große Schrift",
  Lc30: "Platzhalter",
  Fail: "Zu schwach",
};

export type PairReport = {
  fg: number;
  bg: number;
  fgHex: string;
  bgHex: string;
  fgRgb: [number, number, number];
  bgRgb: [number, number, number];
  ratio: number;
  grade: ContrastGrade;
  uiPass: boolean;
  largeAA: boolean;
  largeAAA: boolean;
  bodyAA: boolean;
  bodyAAA: boolean;
  lc: number;
  apca: ApcaGrade;
};

export function pairReport(slots: Slot[], fg: number, bg: number): PairReport {
  const f = slots[fg] ?? slots[0];
  const b = slots[bg] ?? slots[4];
  const fgRgb = hslToRgb(f.h, f.s, f.l);
  const bgRgb = hslToRgb(b.h, b.s, b.l);
  const ratio = contrastRgb(fgRgb, bgRgb);
  const grade = gradeContrast(ratio);
  const lc = apcaLc(fgRgb, bgRgb);
  return {
    fg,
    bg,
    fgHex: rgbToHex(...fgRgb),
    bgHex: rgbToHex(...bgRgb),
    fgRgb,
    bgRgb,
    ratio,
    grade,
    uiPass: ratio >= 3,
    largeAA: ratio >= 3,
    largeAAA: ratio >= 4.5,
    bodyAA: ratio >= 4.5,
    bodyAAA: ratio >= 7,
    lc,
    apca: gradeApca(lc),
  };
}

export function directedPairCount(slots: Slot[]) {
  let aa = 0;
  let total = 0;
  for (let fg = 0; fg < slots.length; fg++) {
    for (let bg = 0; bg < slots.length; bg++) {
      if (fg === bg) continue;
      total += 1;
      if (pairReport(slots, fg, bg).bodyAA) aa += 1;
    }
  }
  return { aa, total };
}

export function pairName(fg: number, bg: number) {
  return `${SLOT_LABELS[fg]} auf ${SLOT_LABELS[bg]}`;
}
