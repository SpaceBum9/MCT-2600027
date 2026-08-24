export type SystemConfig = {
  epsilon: number;
  weightUpdateRate: number;
  initialCoupling: number;
  minCoupling: number;
  maxCoupling: number;
  targetRelativeDivergence: number;
  couplingAdaptationRate: number;
  maxCouplingStep: number;
  divergenceDeadband: number;
};

export const DEFAULT_CONFIG: SystemConfig = {
  epsilon: 1e-6,
  weightUpdateRate: 0.15,
  initialCoupling: 0.3,
  minCoupling: 0.05,
  maxCoupling: 0.95,
  targetRelativeDivergence: 0.25,
  couplingAdaptationRate: 0.05,
  maxCouplingStep: 0.02,
  divergenceDeadband: 1e-3,
};

export type Telemetry = {
  absoluteDivergence: number;
  relativeDivergence: number;
  targetRelativeDivergence: number;
  couplingUsed: number;
  couplingFactor: number;
  couplingDelta: number;
  error: number;
  weights: [number, number];
  systemPhase: string;
};

export function validateConfig(c: SystemConfig) {
  if (!Number.isFinite(c.epsilon) || c.epsilon <= 0) {
    throw new Error("epsilon must be finite and > 0");
  }
  if (!(c.weightUpdateRate > 0 && c.weightUpdateRate <= 1)) {
    throw new Error("weightUpdateRate must be in (0, 1]");
  }
  if (!(c.minCoupling >= 0 && c.minCoupling < c.maxCoupling && c.maxCoupling <= 1)) {
    throw new Error("must satisfy: 0 <= minCoupling < maxCoupling <= 1");
  }
  if (c.initialCoupling < c.minCoupling || c.initialCoupling > c.maxCoupling) {
    throw new Error("initialCoupling must lie within coupling limits");
  }
}

export class DualEntangledSystem {
  config: SystemConfig;
  prevWeights: [number, number];
  rules: Telemetry;

  constructor(config: Partial<SystemConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    validateConfig(this.config);
    this.prevWeights = [0.5, 0.5];
    this.rules = this.initialRules();
  }

  get coupling() {
    return this.rules.couplingFactor;
  }

  reset() {
    this.prevWeights = [0.5, 0.5];
    this.rules = this.initialRules();
  }

  private initialRules(): Telemetry {
    const c = this.config.initialCoupling;
    return {
      absoluteDivergence: 0,
      relativeDivergence: 0,
      targetRelativeDivergence: this.config.targetRelativeDivergence,
      couplingUsed: c,
      couplingFactor: c,
      couplingDelta: 0,
      error: 0,
      weights: [0.5, 0.5],
      systemPhase: "INIT",
    };
  }

  static mirrorInvert(stateA: number) {
    return -Math.tanh(stateA);
  }

  private calculateWeights(a: number, b: number): [number, number] {
    const eps = this.config.epsilon;
    const denom = Math.abs(a) + Math.abs(b) + 2 * eps;
    const target: [number, number] = [
      (Math.abs(a) + eps) / denom,
      (Math.abs(b) + eps) / denom,
    ];
    const rate = this.config.weightUpdateRate;
    let w0 = (1 - rate) * this.prevWeights[0] + rate * target[0];
    let w1 = (1 - rate) * this.prevWeights[1] + rate * target[1];
    const sum = w0 + w1;
    w0 /= sum;
    w1 /= sum;
    this.prevWeights = [w0, w1];
    return [w0, w1];
  }

  step(stateA: number): { out: [number, number]; rules: Telemetry } {
    if (!Number.isFinite(stateA)) throw new Error("input must be finite");
    const stateB = DualEntangledSystem.mirrorInvert(stateA);
    const weights = this.calculateWeights(stateA, stateB);
    const couplingUsed = this.coupling;
    const out0 = weights[0] * stateA + couplingUsed * weights[1] * stateB;
    const out1 = couplingUsed * weights[0] * stateA + weights[1] * stateB;
    const out: [number, number] = [out0, out1];

    const absDiv = Math.abs(out0 - out1);
    const scale = Math.max(Math.abs(stateA), Math.abs(stateB), this.config.epsilon);
    const rel = absDiv / scale;
    const error = rel - this.config.targetRelativeDivergence;
    const raw = this.config.couplingAdaptationRate * error;
    const delta = Math.min(
      this.config.maxCouplingStep,
      Math.max(-this.config.maxCouplingStep, raw),
    );
    const next = Math.min(
      this.config.maxCoupling,
      Math.max(this.config.minCoupling, couplingUsed + delta),
    );

    let phase = "STABLE";
    if (Math.abs(error) <= this.config.divergenceDeadband) phase = "STABLE";
    else if (next > couplingUsed) phase = "COUPLING_UP";
    else if (next < couplingUsed) phase = "COUPLING_DOWN";
    else if (error > 0) phase = "MAX_COUPLING_LIMIT";
    else phase = "MIN_COUPLING_LIMIT";

    this.rules = {
      absoluteDivergence: absDiv,
      relativeDivergence: rel,
      targetRelativeDivergence: this.config.targetRelativeDivergence,
      couplingUsed,
      couplingFactor: next,
      couplingDelta: next - couplingUsed,
      error,
      weights,
      systemPhase: phase,
    };
    return { out, rules: { ...this.rules } };
  }

  run(inputs: number[], reset = true) {
    if (reset) this.reset();
    const outputs: [number, number][] = [];
    const telemetry: Telemetry[] = [];
    for (const value of inputs) {
      const { out, rules } = this.step(value);
      outputs.push(out);
      telemetry.push(rules);
    }
    return { outputs, telemetry };
  }
}

export function makeSignal(
  kind: "sine" | "square" | "step" | "ramp" | "chirp" | "noise",
  n: number,
  amplitude: number,
  cycles: number,
) {
  const count = Math.max(8, Math.floor(n));
  const values: number[] = [];
  for (let i = 0; i < count; i++) {
    const t = i / Math.max(1, count - 1);
    if (kind === "sine") values.push(amplitude * Math.sin(2 * Math.PI * cycles * t));
    else if (kind === "square") {
      values.push(amplitude * Math.sign(Math.sin(2 * Math.PI * cycles * t) + 1e-12));
    } else if (kind === "step") values.push(t < 0.35 ? 0 : amplitude);
    else if (kind === "ramp") values.push(amplitude * (2 * t - 1));
    else if (kind === "chirp") {
      const phase = 2 * Math.PI * (0.4 * cycles * t + 3.2 * cycles * t * t);
      values.push(amplitude * Math.sin(phase));
    } else {
      values.push(amplitude * (2 * seeded(i) - 1));
    }
  }
  return values;
}

function seeded(i: number) {
  const x = Math.sin(i * 12.9898 + 1) * 43758.5453;
  return x - Math.floor(x);
}
