// Καθρεφτίζουν 1:1 τα Pydantic schemas του backend (app/schemas/*.py).
// Ενα resource τη φορά -- ξεκινάμε με Country, τα υπόλοιπα entities
// (Indicator, NegotiationEvent, ...) μπαίνουν σε επόμενα slices.

export type ActorType = "STATE" | "INTERNATIONAL_ORG" | "MILITARY_ALLIANCE";

export type GeopoliticalBloc = "WEST" | "EAST" | "EU" | "NEUTRAL";

// Αντιστοιχεί στο CountryRead (backend/app/schemas/country.py)
export interface Country {
  id: number;
  name: string;
  actor_type: ActorType;
  geopolitical_bloc: GeopoliticalBloc | null;
  recognized_kosovo: boolean | null;
  country_code: string | null;
  role_description: string | null;
}

// Αντιστοιχεί στο CountryCreate -- όλα τα πεδία εκτός από id
export type CountryCreate = Omit<Country, "id">;

// Αντιστοιχεί στο CountryUpdate -- όλα τα πεδία optional (partial update)
export type CountryUpdate = Partial<CountryCreate>;
