// Resource module για το /negotiation-events. ΠΡΟΣΟΧΗ: η collection route
// εδώ ΕΧΕΙ trailing slash ("/negotiation-events/") -- βλ. reference table
// στο τέλος του client.ts. Paths hardcoded από το
// backend/app/api/negotiation_event.py.

import { apiRequest } from "./client";
import type {
  NegotiationEvent,
  NegotiationEventCreate,
  NegotiationEventUpdate,
} from "./types";

export function listNegotiationEvents(): Promise<NegotiationEvent[]> {
  return apiRequest<NegotiationEvent[]>("/negotiation-events/");
}

export function getNegotiationEvent(id: number): Promise<NegotiationEvent> {
  return apiRequest<NegotiationEvent>(`/negotiation-events/${id}`);
}

export function createNegotiationEvent(
  payload: NegotiationEventCreate,
): Promise<NegotiationEvent> {
  return apiRequest<NegotiationEvent>("/negotiation-events/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateNegotiationEvent(
  id: number,
  payload: NegotiationEventUpdate,
): Promise<NegotiationEvent> {
  return apiRequest<NegotiationEvent>(`/negotiation-events/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteNegotiationEvent(id: number): Promise<void> {
  return apiRequest<void>(`/negotiation-events/${id}`, { method: "DELETE" });
}
