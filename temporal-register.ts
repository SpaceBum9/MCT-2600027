export type RegisterStatus = "active" | "expired" | "detached";
export type AccessRole = "observer" | "operator" | "builder" | "admin";
export type SystemLabel = "halo" | "galaxy" | "hal";

export interface TemporalRegisterEntry {
  registerId: string;
  subjectLabel: string;
  role: AccessRole;
  systemLabels: readonly SystemLabel[];
  validFrom: string;
  validUntil?: string;
  inclusiveAccess: true;
  storesCredentials: false;
  credentialState: "not_stored";
  status: RegisterStatus;
}

export interface AccessCheck {
  registerId: string;
  at: string;
  allowed: boolean;
  reason: "active" | "expired" | "detached" | "not_found";
}

const registry = new Map<string, TemporalRegisterEntry>();

function isExpired(entry: TemporalRegisterEntry, at: Date): boolean {
  if (!entry.validUntil) return false;
  const until = Date.parse(entry.validUntil);
  return Number.isFinite(until) && at.getTime() > until;
}

export function registerTemporalEntry(
  input: Omit<TemporalRegisterEntry, "inclusiveAccess" | "storesCredentials" | "credentialState" | "status">,
): TemporalRegisterEntry {
  const entry: TemporalRegisterEntry = {
    ...input,
    inclusiveAccess: true,
    storesCredentials: false,
    credentialState: "not_stored",
    status: "active",
  };
  registry.set(entry.registerId, entry);
  return entry;
}

export function validateTemporalAccess(registerId: string, atIso = new Date().toISOString()): AccessCheck {
  const entry = registry.get(registerId);
  if (!entry) return { registerId, at: atIso, allowed: false, reason: "not_found" };

  if (entry.status === "detached") {
    return { registerId, at: atIso, allowed: false, reason: "detached" };
  }

  const at = new Date(atIso);
  if (isExpired(entry, at)) {
    const expired = { ...entry, status: "expired" as const };
    registry.set(registerId, expired);
    return { registerId, at: atIso, allowed: false, reason: "expired" };
  }

  return { registerId, at: atIso, allowed: true, reason: "active" };
}

export function detachTemporalAccess(registerId: string): TemporalRegisterEntry | undefined {
  const entry = registry.get(registerId);
  if (!entry) return undefined;
  const detached = { ...entry, status: "detached" as const };
  registry.set(registerId, detached);
  return detached;
}

export function getTemporalEntry(registerId: string): TemporalRegisterEntry | undefined {
  return registry.get(registerId);
}

// Internal access-state model only. HAL/halo/galaxy are labels, not claims of
// external connectivity. Credentials are intentionally never accepted or stored.
