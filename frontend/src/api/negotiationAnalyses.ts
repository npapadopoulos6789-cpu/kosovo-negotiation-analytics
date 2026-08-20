// Resource module για NegotiationAnalysis: per-event Q&A (/negotiation-
// analyses/, ΕΧΕΙ trailing slash), + /synthesis και /compare (χωρίς
// prefix, δικά τους top-level POST routes -- βλ. backend/app/api/
// synthesis.py + compare.py, ΧΩΡΙΣ trailing slash). Κάθε path hardcoded
// ξεχωριστά, όπως στα υπόλοιπα resource modules (βλ. reference table στο
// τέλος του client.ts).

import { apiRequest } from "./client";
import type {
  NegotiationAnalysis,
  NegotiationAnalysisCreate,
  SynthesisCreate,
  CompareCreate,
} from "./types";

export function listAnalysesByEvent(eventId: number): Promise<NegotiationAnalysis[]> {
  return apiRequest<NegotiationAnalysis[]>(`/negotiation-analyses/by-event/${eventId}`);
}

// Πραγματικά paid Claude API calls στο backend, και τα 3 function
// παρακάτω -- ΟΧΙ να καλούνται χωρίς ρητή ενέργεια χρήστη (κουμπί
// submit), ποτέ αυτόματα/σε loop.

export function createAnalysis(payload: NegotiationAnalysisCreate): Promise<NegotiationAnalysis> {
  return apiRequest<NegotiationAnalysis>("/negotiation-analyses/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// Γενική σύνθεση πάνω σε όλα τα events μαζί (is_synthesis=true, negotiation_event_id=NULL)
export function createSynthesis(payload: SynthesisCreate): Promise<NegotiationAnalysis> {
  return apiRequest<NegotiationAnalysis>("/synthesis", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// Σύγκριση ακριβώς δύο events -- backend αρνείται event_a_id == event_b_id
// με 422 (IdenticalComparisonEventsError). Κάνουμε το ίδιο check
// client-side στο ComparePage ώστε να μη χρειάζεται καν το round-trip.
export function createComparison(payload: CompareCreate): Promise<NegotiationAnalysis> {
  return apiRequest<NegotiationAnalysis>("/compare", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
