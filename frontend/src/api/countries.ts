// Resource module για το /countries. Paths hardcoded ΑΚΡΙΒΩΣ όπως στο
// backend/app/api/country.py -- η collection route είναι "/countries"
// ΧΩΡΙΣ trailing slash (βλ. σημείωση στο client.ts).

import { apiRequest } from "./client";
import type { Country, CountryCreate, CountryUpdate } from "./types";

export function listCountries(): Promise<Country[]> {
  return apiRequest<Country[]>("/countries");
}

export function getCountry(id: number): Promise<Country> {
  return apiRequest<Country>(`/countries/${id}`);
}

export function createCountry(payload: CountryCreate): Promise<Country> {
  return apiRequest<Country>("/countries", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateCountry(id: number, payload: CountryUpdate): Promise<Country> {
  return apiRequest<Country>(`/countries/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteCountry(id: number): Promise<void> {
  return apiRequest<void>(`/countries/${id}`, {
    method: "DELETE",
  });
}
