export type Hsl = { h: number; s: number; l: number };

export function clamp(n: number, min: number, max: number) {
  return Math.min(max, Math.max(min, n));
}

export function hueNorm(h: number) {
  return ((h % 360) + 360) % 360;
}

export function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  const hh = hueNorm(h);
  const ss = clamp(s, 0, 100) / 100;
  const ll = clamp(l, 0, 100) / 100;
  const c = (1 - Math.abs(2 * ll - 1)) * ss;
  const hp = hh / 60;
  const x = c * (1 - Math.abs((hp % 2) - 1));
  let r = 0;
  let g = 0;
  let b = 0;
  if (hp < 1) [r, g, b] = [c, x, 0];
  else if (hp < 2) [r, g, b] = [x, c, 0];
  else if (hp < 3) [r, g, b] = [0, c, x];
  else if (hp < 4) [r, g, b] = [0, x, c];
  else if (hp < 5) [r, g, b] = [x, 0, c];
  else [r, g, b] = [c, 0, x];
  const m = ll - c / 2;
  return [
    Math.round((r + m) * 255),
    Math.round((g + m) * 255),
    Math.round((b + m) * 255),
  ];
}

export function rgbToHex(r: number, g: number, b: number) {
  return (
    "#" +
    [r, g, b]
      .map((v) => clamp(Math.round(v), 0, 255).toString(16).padStart(2, "0"))
      .join("")
      .toUpperCase()
  );
}

export function formatHsl(h: number, s: number, l: number) {
  return `hsl(${Math.round(hueNorm(h))} ${Math.round(s)}% ${Math.round(l)}%)`;
}

export function formatHslChannels(h: number, s: number, l: number) {
  return `${Math.round(hueNorm(h))} ${Math.round(s)}% ${Math.round(l)}%`;
}

export function formatRgb(r: number, g: number, b: number) {
  return `rgb(${r}, ${g}, ${b})`;
}

export function formatRgbChannels(r: number, g: number, b: number) {
  return `${r} ${g} ${b}`;
}

export function relativeLuminance(r: number, g: number, b: number) {
  const lin = (c: number) => {
    const x = c / 255;
    return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

export function contrastRatio(lumA: number, lumB: number) {
  const a = Math.max(lumA, lumB);
  const b = Math.min(lumA, lumB);
  return (a + 0.05) / (b + 0.05);
}

export type ContrastGrade = "AAA" | "AA" | "AA large" | "Fail";

export function gradeContrast(ratio: number): ContrastGrade {
  if (ratio >= 7) return "AAA";
  if (ratio >= 4.5) return "AA";
  if (ratio >= 3) return "AA large";
  return "Fail";
}

export function contrastAgainstWhite(h: number, s: number, l: number) {
  const [r, g, b] = hslToRgb(h, s, l);
  return contrastRatio(relativeLuminance(r, g, b), 1);
}

export function contrastAgainstBlack(h: number, s: number, l: number) {
  const [r, g, b] = hslToRgb(h, s, l);
  return contrastRatio(relativeLuminance(r, g, b), 0);
}

export function bestOnColor(h: number, s: number, l: number): "light" | "ink" {
  return contrastAgainstWhite(h, s, l) >= contrastAgainstBlack(h, s, l)
    ? "light"
    : "ink";
}

export function onHex(on: "light" | "ink") {
  return on === "light" ? "#F4F1EA" : "#141310";
}

export function slotFormats(hsl: Hsl) {
  const [r, g, b] = hslToRgb(hsl.h, hsl.s, hsl.l);
  return {
    hex: rgbToHex(r, g, b),
    rgb: formatRgb(r, g, b),
    rgbChannels: formatRgbChannels(r, g, b),
    hsl: formatHsl(hsl.h, hsl.s, hsl.l),
    hslChannels: formatHslChannels(hsl.h, hsl.s, hsl.l),
    r,
    g,
    b,
  };
}
