// Resource module για /negotiation-analyses -- ΜΟΝΟ per-event Q&A προς το
// παρόν (negotiation_event_id ορισμένο). ΠΡΟΣΟΧΗ: η collection route εδώ
// ΕΧΕΙ trailing slash ("/negotiation-analyses/") -- βλ. reference table
// στο τέλος του client.ts. Synthesis (/synthesis) και Compare (/compare)
// ΔΕΝ έχουν μπει ακόμα -- ξεχωριστό βήμα, με ρητή επίβλεψη.

import { apiRequest } from "./client";
import type { NegotiationAnalysis, NegotiationAnalysisCreate } from "./types";

export function listAnalysesByEvent(eventId: number): Promise<NegotiationAnalysis[]> {
  return apiRequest<NegotiationAnalysis[]>(`/negotiation-analyses/by-event/${eventId}`);
}

// Πραγματικό paid Claude API call στο backend -- ΟΧΙ να καλείται χωρίς
// ρητή ενέργεια χρήστη (κουμπί submit), ποτέ αυτόματα/σε loop.
export function createAnalysis(payload: NegotiationAnalysisCreate): Promise<NegotiationAnalysis> {
  return apiRequest<NegotiationAnalysis>("/negotiation-analyses/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
