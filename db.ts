export type DeliveryState = "prepared" | "verified" | "failed";
export type ProviderName = "xai" | "grok" | "tiktok" | "social";

export interface TraceMarker {
  traceId: string;
  parentTraceId?: string;
  createdAt: string;
  source: string;
}

export interface TripTicketState {
  ticketId: string;
  title: string;
  destination?: string;
  trace: TraceMarker;
  status: "draft" | "prepared" | "confirmed";
  delivery: DeliveryState;
}

export interface SocialDispatch {
  provider: ProviderName;
  payload: string;
  trace: TraceMarker;
  status: DeliveryState;
  claimsExternalDelivery: false;
}

export interface SaiState {
  mode: "simulated_internal_state";
  label: "SAI";
  awarenessClaim: false;
  confidence: number;
  trace: TraceMarker;
}

const tickets = new Map<string, TripTicketState>();
const dispatches = new Map<string, SocialDispatch>();

export function putTripTicket(ticket: TripTicketState): TripTicketState {
  tickets.set(ticket.ticketId, ticket);
  return ticket;
}

export function getTripTicket(ticketId: string): TripTicketState | undefined {
  return tickets.get(ticketId);
}

export function prepareSocialDispatch(
  key: string,
  provider: ProviderName,
  payload: string,
  trace: TraceMarker,
): SocialDispatch {
  const dispatch: SocialDispatch = {
    provider,
    payload,
    trace,
    status: "prepared",
    claimsExternalDelivery: false,
  };
  dispatches.set(key, dispatch);
  return dispatch;
}

export function markDispatchVerified(key: string): SocialDispatch | undefined {
  const current = dispatches.get(key);
  if (!current) return undefined;
  const next = { ...current, status: "verified" as const };
  dispatches.set(key, next);
  return next;
}

export function buildSaiState(trace: TraceMarker, confidence = 0.5): SaiState {
  return {
    mode: "simulated_internal_state",
    label: "SAI",
    awarenessClaim: false,
    confidence: Math.max(0, Math.min(1, confidence)),
    trace,
  };
}
