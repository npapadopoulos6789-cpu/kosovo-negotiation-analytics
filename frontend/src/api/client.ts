// Γενικός fetch wrapper. ΔΕΝ κατασκευάζει/κανονικοποιεί paths (καμία λογική
// "πάντα με slash" ή "πάντα χωρίς") -- το backend δεν έχει ενιαία σύμβαση
// trailing slash ανά resource (βλ. σημείωση στο τέλος του αρχείου). Λάθος
// convention εδώ θα έστελνε π.χ. GET /indicators αντί για το πραγματικό
// /indicators/, το FastAPI θα απαντούσε με 307 redirect, και σε cross-origin
// request αυτό σπάει το CORS preflight (confusing error στο browser console,
// όχι καθαρό 404). Άρα κάθε resource module (countries.ts κ.λπ.) περνάει το
// ΑΚΡΙΒΕΣ path string όπως ορίζεται στο αντίστοιχο backend router -- κανένα
// hardcode-άρισμα εδώ.

import { getStoredToken } from "../auth/tokenStorage";

// VITE_API_URL: production backend origin (Railway κ.λπ.), set στο build
// environment. Fallback σε localhost:8000 όταν λείπει, ώστε το τοπικό dev
// να συνεχίσει να δουλεύει χωρίς καμία αλλαγή.
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : `API error ${status}`);
    this.status = status;
    this.detail = detail;
  }
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  // Επισυνάπτουμε το token (αν υπάρχει συνδεδεμένος χρήστης) σε ΚΑΘΕ
  // request -- σήμερα κανένα από τα υπάρχοντα endpoints δεν το απαιτεί
  // (βλ. σχόλιο στο AuthProvider), αλλά τα λίγα που ΘΑ το χρειαστούν
  // (π.χ. verify indicator μέσω PUT /indicators/{id}) δουλεύουν ήδη χωρίς
  // αλλαγή σε κάθε resource module.
  const token = getStoredToken();

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    let detail: unknown = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? body;
    } catch {
      // το error body δεν ήταν JSON -- κρατάμε το statusText
    }
    throw new ApiError(response.status, detail);
  }

  // 204 No Content (π.χ. DELETE) δεν έχει body -- response.json() θα έσκαγε
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

/*
Ακριβή paths ανά resource, ελεγμένα στον πραγματικό κώδικα
(backend/main.py + backend/app/api/*.py, 2026-08-20):

  /countries                          GET (list) / POST   -- ΧΩΡΙΣ trailing slash
  /countries/{id}                     GET / PUT / DELETE
  /indicators/                        GET (list) / POST   -- ΜΕ trailing slash
  /indicators/{id}                    GET / PUT / DELETE
  /indicators/by-country/{country_id} GET
  /negotiation-events/                GET (list) / POST   -- ΜΕ trailing slash
  /negotiation-events/{id}            GET / PUT / DELETE
  /negotiation-analyses/              GET (list) / POST   -- ΜΕ trailing slash
  /negotiation-analyses/{id}          GET
  /negotiation-analyses/by-event/{event_id} GET
  /auth/register, /auth/login         POST
  /compare                            POST
  /synthesis                          POST
  /analytics/...                      GET, όλα explicit paths

Κάθε νέο resource module: κοίτα το αντίστοιχο app/api/*.py, μη μαντέψεις.
*/
