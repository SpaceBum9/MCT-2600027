/** Port of MCT-170021: Euclidean sequencer, Zero-Tier ATM, state vector. */

export type Complex = { re: number; im: number };

export function euclideanSequence(start: number, end: number, step = 1): number[] {
  const seq: number[] = [];
  const safe = step === 0 ? 1 : step;
  for (let x = start; x <= end + 1e-9; x += safe) {
    seq.push(Number(x.toFixed(4)));
  }
  return seq;
}

export function gcd(a: number, b: number): number {
  let x = Math.abs(Math.round(a));
  let y = Math.abs(Math.round(b));
  while (y) {
    const t = y;
    y = x % y;
    x = t;
  }
  return x || 1;
}

export function spacedSequence(n: number, pulses: number): number[] {
  const count = Math.max(1, Math.floor(n));
  const hits = Math.min(count, Math.max(1, Math.floor(pulses)));
  const out: number[] = [];
  for (let i = 0; i < hits; i++) {
    out.push(Math.floor((i * count) / hits));
  }
  return out;
}

export function normalizeState(amps: Complex[]): Complex[] {
  const norm = Math.sqrt(amps.reduce((s, a) => s + a.re * a.re + a.im * a.im, 0)) || 1;
  return amps.map((a) => ({ re: a.re / norm, im: a.im / norm }));
}

export function seedState(nQubits: number, seed: number): Complex[] {
  const dim = 2 ** Math.max(1, Math.min(4, nQubits));
  const amps: Complex[] = [];
  let s = seed || 1;
  for (let i = 0; i < dim; i++) {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    const re = (s / 0x7fffffff) * 2 - 1;
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    const im = (s / 0x7fffffff) * 2 - 1;
    amps.push({ re, im });
  }
  return normalizeState(amps);
}

export function applyPhase(state: Complex[], sequence: number[]): Complex[] {
  const n = Math.max(sequence.length, 1);
  return state.map((amp, i) => {
    const theta = (Math.PI * (sequence[i % sequence.length] ?? 0)) / n;
    const c = Math.cos(theta);
    const s = Math.sin(theta);
    return { re: amp.re * c - amp.im * s, im: amp.re * s + amp.im * c };
  });
}

export function vonNeumannEntropy(state: Complex[]): number {
  const probs = state.map((a) => a.re * a.re + a.im * a.im);
  return -probs.reduce((s, p) => s + (p > 1e-12 ? p * Math.log2(p) : 0), 0);
}

export function iterateRegler(a: number) {
  const b = -Math.tanh(a);
  return { a, b, divergence: Math.abs(a - b) };
}

export type TracerHub = {
  id: string;
  title: string;
  network: string;
  channel: string;
  hops: number[];
  momentum: [number, number, number];
  entropy: number;
  status: "locked" | "drift" | "dark";
  note: string;
};

const HUB_DEFS = [
  { id: "crystal-mike", title: "Crystal Mike", network: "bilo-origin", note: "Semantic Anchor" },
  { id: "hal", title: "HAL", network: "galaxy-core", note: "Control Plane" },
  { id: "mct-170021", title: "MCT-170021", network: "mct170021-zero-tier", note: "Mesh / MCP" },
  { id: "mct-2600027-cmd", title: "MCT-2600027", network: "mct2600027-cmd", note: "Dieses CMD" },
  { id: "kreuzkopplung", title: "Kreuzkopplung", network: "dual-entangled", note: "Zwei-Kanal-Regler" },
  { id: "lumen", title: "Lumen", network: "ios-edge", note: "Apple Intelligence" },
] as const;

export function buildTracerHubs(seed = Date.now() % 997): TracerHub[] {
  return HUB_DEFS.map((hub, i) => {
    const hops = spacedSequence(16, 5 + (i % 3));
    const state = applyPhase(seedState(2, seed + i * 17), hops);
    const entropy = vonNeumannEntropy(state);
    const momentum: [number, number, number] = [0, 0, 0];
    return {
      id: hub.id,
      title: hub.title,
      network: hub.network,
      channel: `atm-${hub.id}`,
      hops,
      momentum,
      entropy: Number(entropy.toFixed(3)),
      status: entropy > 1.85 ? "drift" : "locked",
      note: hub.note,
    };
  });
}

export function transferState(hub: TracerHub) {
  const zero = hub.momentum.every((m) => m === 0);
  return {
    status: zero ? "zero_momentum_ok" : "momentum_error",
    target: hub.id,
    channel: hub.channel,
    qos: "guaranteed" as const,
    cell: 53,
  };
}
