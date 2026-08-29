// Resource module για /analytics -- οι ντετερμινιστικοί δείκτες ισχύος
// (Power Index/Gap/Window Score/Optimal Periods, βλ. CLAUDE.md). Κανένα
// από αυτά δεν είναι LLM-generated· είναι καθαρός υπολογισμός στο backend
// service layer. power-index-breakdown + window-score προς το παρόν --
// τα υπόλοιπα analytics endpoints (power-gap, optimal periods,
// best-moments) μπαίνουν σε επόμενα charts, ένα-ένα.
//
// Όλα τα paths εδώ είναι explicit endpoints (καμία trailing-slash
// ασάφεια, βλ. reference table στο τέλος του client.ts). 404 από το
// backend σημαίνει "ανεπαρκή δεδομένα για αυτό το country/year"
// (analytics.py: `detail: "Insufficient data for this country/year"`) --
// ΟΧΙ σφάλμα· ο caller πρέπει να το χειριστεί ως EmptyState, όχι ErrorState.

import { apiRequest } from "./client";
import type { PowerIndexBreakdown, WindowScoreResult, WindowScoreBreakdown } from "./types";

export function getPowerIndexBreakdown(
  countryId: number,
  year: number,
): Promise<PowerIndexBreakdown> {
  return apiRequest<PowerIndexBreakdown>(`/analytics/power-index-breakdown/${countryId}/${year}`);
}

// previousYear προαιρετικό -- αν παραλειφθεί ΚΑΙ το year είναι μέσα στο
// backend KEY_YEARS, το backend το υπολογίζει μόνο του (auto-lookup του
// πιο πρόσφατου προηγούμενου έτους με δεδομένα, βλ. app/api/analytics.py
// get_window_score). Αλλιώς trend_score=0.0 στο backend (όχι σφάλμα).
export function getWindowScore(
  year: number,
  serbiaId: number,
  kosovoId: number,
  previousYear?: number,
): Promise<WindowScoreResult> {
  const params = new URLSearchParams({
    serbia_id: String(serbiaId),
    kosovo_id: String(kosovoId),
  });
  if (previousYear !== undefined) {
    params.set("previous_year", String(previousYear));
  }
  return apiRequest<WindowScoreResult>(`/analytics/window-score/${year}?${params}`);
}

// Ίδιο previousYear-optional convention με το getWindowScore παραπάνω.
export function getWindowScoreBreakdown(
  year: number,
  serbiaId: number,
  kosovoId: number,
  previousYear?: number,
): Promise<WindowScoreBreakdown> {
  const params = new URLSearchParams({
    serbia_id: String(serbiaId),
    kosovo_id: String(kosovoId),
  });
  if (previousYear !== undefined) {
    params.set("previous_year", String(previousYear));
  }
  return apiRequest<WindowScoreBreakdown>(`/analytics/window-score-breakdown/${year}?${params}`);
}
