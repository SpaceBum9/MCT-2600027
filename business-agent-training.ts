export type AuthScheme = "bearer_env_only";
export type ConnectivityState = "unverified" | "verified" | "failed";
export type TrainingStage = "draft" | "prepared" | "ready";

export interface DeviceIdentity {
  deviceId: string;
  nodeId: string;
  role: "backoffice" | "operator" | "builder" | "observer";
  connectivity: ConnectivityState;
  identityVerified: boolean;
}

export interface BusinessAgentProfile {
  agentId: string;
  department: string;
  capabilities: readonly string[];
  auth: {
    scheme: AuthScheme;
    secretStored: false;
  };
  trainingStage: TrainingStage;
  traceId: string;
}

export interface TrainingSnapshot {
  devices: readonly DeviceIdentity[];
  agents: readonly BusinessAgentProfile[];
  hotNodes: readonly string[];
  externalStateVerified: boolean;
}

export function buildBusinessAgentProfile(input: {
  agentId: string;
  department: string;
  capabilities?: readonly string[];
  traceId: string;
}): BusinessAgentProfile {
  return {
    agentId: input.agentId,
    department: input.department,
    capabilities: input.capabilities ?? [],
    auth: {
      scheme: "bearer_env_only",
      secretStored: false,
    },
    trainingStage: "prepared",
    traceId: input.traceId,
  };
}

export function registerDeclaredDevice(input: {
  deviceId: string;
  nodeId: string;
  role: DeviceIdentity["role"];
}): DeviceIdentity {
  return {
    deviceId: input.deviceId,
    nodeId: input.nodeId,
    role: input.role,
    connectivity: "unverified",
    identityVerified: false,
  };
}

export function buildTrainingSnapshot(
  devices: readonly DeviceIdentity[],
  agents: readonly BusinessAgentProfile[],
): TrainingSnapshot {
  return {
    devices,
    agents,
    hotNodes: devices
      .filter((device) => device.connectivity === "verified" && device.identityVerified)
      .map((device) => device.nodeId),
    externalStateVerified: false,
  };
}

export function verifyDeviceIdentity(
  device: DeviceIdentity,
): DeviceIdentity {
  return {
    ...device,
    connectivity: "verified",
    identityVerified: true,
  };
}

// This module models declared business-agent/device state only.
// Bearer credentials must be supplied at runtime from environment/configuration
// and are never stored in this state model. A node is only considered "hot"
// after explicit identity + connectivity verification.
