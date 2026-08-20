// Καθρεφτίζουν 1:1 τα Pydantic schemas του backend (app/schemas/*.py).
// Ενα resource τη φορά -- Country, Indicator, NegotiationEvent μπήκαν ήδη.
// Analytics/NegotiationAnalysis (synthesis/compare) ΔΕΝ έχουν μπει ακόμα --
// σκόπιμα, αφού κάνουν πραγματικά paid LLM calls και χτίζονται ξεχωριστά,
// με ρητή επίβλεψη.

// ---------- Country ----------

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

// ---------- Indicator ----------

export type IndicatorCategory = "ECONOMIC" | "MILITARY" | "SOCIAL_UNREST";
export type IndicatorConfidence = "EXACT" | "CHART_READ" | "RANGE";

// Αντιστοιχεί στο IndicatorRead (backend/app/schemas/indicator.py)
export interface Indicator {
  id: number;
  country_id: number;
  category: IndicatorCategory;
  indicator_type: string;
  year: number;
  value: number;
  unit: string | null;
  source: string | null;
  is_verified: boolean;
  confidence: IndicatorConfidence | null;
}

export type IndicatorCreate = Omit<Indicator, "id" | "is_verified"> & { is_verified?: boolean };
export type IndicatorUpdate = Partial<IndicatorCreate>;

// ---------- NegotiationEvent ----------

export type ZopaSize = "NARROW" | "MODERATE" | "WIDE";
export type RipenessStatus = "NOT_RIPE" | "EMERGING" | "RIPE";
export type NegotiationType = "DISTRIBUTIVE" | "INTEGRATIVE_WIN_WIN";
export type ParticipantRole = "PARTY" | "MEDIATOR" | "GUARANTOR" | "SUPPORTER";

// Αντιστοιχεί στο ParticipantRead -- εμπλουτισμένο με country_name από το service
export interface Participant {
  id: number;
  country_id: number;
  country_name: string;
  role: ParticipantRole;
  supports_country_id: number | null;
}

export interface ParticipantCreate {
  country_id: number;
  role: ParticipantRole;
  supports_country_id?: number | null;
}

// Αντιστοιχεί στο NegotiationEventRead
export interface NegotiationEvent {
  id: number;
  title: string;
  date: string; // ISO date string (YYYY-MM-DD)
  description: string | null;
  zopa_size: ZopaSize | null;
  zopa_reasoning: string | null;
  ripeness_status: RipenessStatus | null;
  ripeness_reasoning: string | null;
  batna_side_a: string | null;
  batna_side_b: string | null;
  red_lines_side_a: string | null;
  red_lines_side_b: string | null;
  negotiation_type: NegotiationType | null;
  economic_weight: number;
  military_weight: number;
  social_weight: number;
  implementation_success: number | null;
  participants: Participant[];
}

export type NegotiationEventCreate = Omit<NegotiationEvent, "id" | "participants"> & {
  participants?: ParticipantCreate[];
};
export type NegotiationEventUpdate = Partial<NegotiationEventCreate>;
