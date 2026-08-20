// Resource module για /analytics -- οι ντετερμινιστικοί δείκτες ισχύος
// (Power Index/Gap/Window Score/Optimal Periods, βλ. CLAUDE.md). Κανένα
// από αυτά δεν είναι LLM-generated· είναι καθαρός υπολογισμός στο backend
// service layer. ΜΟΝΟ power-index-breakdown προς το παρόν -- τα υπόλοιπα
// analytics endpoints (power-gap, window-score, optimal periods,
// best-moments) μπαίνουν σε επόμενα charts, ένα-ένα.
//
// Όλα τα paths εδώ είναι explicit endpoints (καμία trailing-slash
// ασάφεια, βλ. reference table στο τέλος του client.ts). 404 από το
// backend σημαίνει "ανεπαρκή δεδομένα για αυτό το country/year"
// (analytics.py: `detail: "Insufficient data for this country/year"`) --
// ΟΧΙ σφάλμα· ο caller πρέπει να το χειριστεί ως EmptyState, όχι ErrorState.

import { apiRequest } from "./client";
import type { PowerIndexBreakdown } from "./types";

export function getPowerIndexBreakdown(
  countryId: number,
  year: number,
): Promise<PowerIndexBreakdown> {
  return apiRequest<PowerIndexBreakdown>(`/analytics/power-index-breakdown/${countryId}/${year}`);
}
