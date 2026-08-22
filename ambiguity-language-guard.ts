export type GuardTokenKind =
  | "literal"
  | "symbolic"
  | "brand"
  | "person_label"
  | "health_claim"
  | "technical_claim"
  | "speculative";

export interface GuardToken {
  raw: string;
  normalized: string;
  kind: GuardTokenKind;
  confidence: number;
  requiresEvidence: boolean;
  externalFact: false;
}

export interface AmbiguityLanguageSnapshot {
  language: "de";
  tokens: GuardToken[];
  unresolved: string[];
  disclaimers: string[];
  claimsExternalState: false;
}

const BRANDS = new Set(["novartis", "forbes"]);
const HEALTH = new Set(["virus", "vermin", "health"]);
const TECHNICAL = new Set(["reaktor", "fusion", "helios", "gravity"]);
const PERSON_LABELS = new Set(["peter", "molyneux", "raphalpha"]);
const SPECULATIVE = new Set(["schwurbel", "spirit", "galaxy", "blotter"]);

function clamp01(value: number): number {
  return Math.max(0, Math.min(1, value));
}

export function classifyGuardToken(raw: string): GuardToken {
  const normalized = raw.trim().toLowerCase();
  let kind: GuardTokenKind = "symbolic";
  let confidence = 0.4;
  let requiresEvidence = false;

  if (BRANDS.has(normalized)) {
    kind = "brand";
    confidence = 0.9;
  } else if (HEALTH.has(normalized)) {
    kind = "health_claim";
    confidence = 0.8;
    requiresEvidence = true;
  } else if (TECHNICAL.has(normalized)) {
    kind = "technical_claim";
    confidence = 0.8;
    requiresEvidence = true;
  } else if (PERSON_LABELS.has(normalized)) {
    kind = "person_label";
    confidence = 0.8;
  } else if (SPECULATIVE.has(normalized)) {
    kind = "speculative";
    confidence = 0.5;
    requiresEvidence = true;
  } else if (/^[\p{L}\p{N}_-]+$/u.test(normalized)) {
    kind = "literal";
    confidence = 0.7;
  }

  return {
    raw,
    normalized,
    kind,
    confidence: clamp01(confidence),
    requiresEvidence,
    externalFact: false,
  };
}

export function buildAmbiguityLanguageSnapshot(input: string): AmbiguityLanguageSnapshot {
  const tokens = input
    .split(/\s+/)
    .map((token) => token.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}_-]+$/gu, ""))
    .filter(Boolean)
    .map(classifyGuardToken);

  const unresolved = tokens
    .filter((token) => token.requiresEvidence || token.kind === "symbolic")
    .map((token) => token.raw);

  const disclaimers: string[] = [];
  if (tokens.some((token) => token.kind === "health_claim")) {
    disclaimers.push("Health-related tokens are labels only until supported by reliable evidence; no diagnosis or medical conclusion is inferred.");
  }
  if (tokens.some((token) => token.kind === "technical_claim")) {
    disclaimers.push("Technical claims require provenance and verification before they can update persistent state.");
  }
  if (tokens.some((token) => token.kind === "speculative")) {
    disclaimers.push("Speculative or symbolic language is kept separate from verified facts.");
  }

  return {
    language: "de",
    tokens,
    unresolved,
    disclaimers,
    claimsExternalState: false,
  };
}
