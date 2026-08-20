// Resource module για το /indicators. ΠΡΟΣΟΧΗ: η collection route εδώ ΕΧΕΙ
// trailing slash ("/indicators/"), σε αντίθεση με το /countries -- βλ.
// reference table στο τέλος του client.ts. Paths hardcoded από το
// backend/app/api/indicator.py, όχι μαντεμένα.

import { apiRequest } from "./client";
import type { Indicator, IndicatorCreate, IndicatorUpdate } from "./types";

export function listIndicators(): Promise<Indicator[]> {
  return apiRequest<Indicator[]>("/indicators/");
}

export function getIndicator(id: number): Promise<Indicator> {
  return apiRequest<Indicator>(`/indicators/${id}`);
}

export function listIndicatorsByCountry(countryId: number): Promise<Indicator[]> {
  return apiRequest<Indicator[]>(`/indicators/by-country/${countryId}`);
}

export function createIndicator(payload: IndicatorCreate): Promise<Indicator> {
  return apiRequest<Indicator>("/indicators/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateIndicator(id: number, payload: IndicatorUpdate): Promise<Indicator> {
  return apiRequest<Indicator>(`/indicators/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteIndicator(id: number): Promise<void> {
  return apiRequest<void>(`/indicators/${id}`, { method: "DELETE" });
}
