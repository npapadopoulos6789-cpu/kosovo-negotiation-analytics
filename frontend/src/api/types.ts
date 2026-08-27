// Καθρεφτίζουν 1:1 τα Pydantic schemas του backend (app/schemas/*.py).
// Ενα resource τη φορά -- Country, Indicator, NegotiationEvent μπήκαν ήδη.
// NegotiationAnalysis εδώ ΜΟΝΟ το per-event Q&A σχήμα (POST
// /negotiation-analyses/) -- SynthesisCreate/CompareCreate ΔΕΝ έχουν μπει
// ακόμα, χτίζονται σε ξεχωριστό βήμα με ρητή επίβλεψη (πραγματικά paid
// LLM calls, βλ. PROJECT_STATUS.md).

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

// ---------- NegotiationAnalysis (per-event LLM Q&A μόνο, βλ. σχόλιο πάνω) ----------

// Αντιστοιχεί στο NegotiationAnalysisRead
export interface NegotiationAnalysis {
  id: number;
  negotiation_event_id: number | null;
  is_synthesis: boolean;
  user_question: string;
  llm_answer: string | null;
  model_used: string | null;
  created_at: string; // ISO datetime string
}

// Αντιστοιχεί στο NegotiationAnalysisCreate -- negotiation_event_id πάντα
// ορισμένο εδώ (per-event Q&A, όχι synthesis)
export interface NegotiationAnalysisCreate {
  negotiation_event_id: number;
  user_question: string;
}

// Αντιστοιχεί στο SynthesisCreate -- POST /synthesis, χωρίς negotiation_event_id
export interface SynthesisCreate {
  user_question: string;
}

// Αντιστοιχεί στο CompareCreate -- POST /compare, καμία free-text ερώτηση
export interface CompareCreate {
  event_a_id: number;
  event_b_id: number;
}

// ---------- Parsed σχήματα του analysis.llm_answer ----------
// ΠΡΟΣΟΧΗ: αυτά ΔΕΝ είναι Pydantic response schemas -- το backend αποθηκεύει
// το llm_answer ως raw JSON string (βλ. NegotiationAnalysis.llm_answer:
// string). Το σχήμα ΜΕΣΑ σε αυτό το string ορίζεται από τα task prompts στο
// backend/app/services/llm_prompts.py (QA_TASK/SYNTHESIS_TASK/COMPARE_TASK)
// -- τρία ΔΙΑΦΟΡΕΤΙΚΑ σχήματα, ένα ανά flow. Ο caller (σελίδα) ξέρει ποιο
// flow έκανε το call και περνάει το σωστό variant στο LLMAnswerCard.

export type AnswerCertainty = "HIGH" | "MEDIUM" | "LOW" | "INSUFFICIENT_DATA";

export interface QAAnswer {
  answer: string;
  answer_certainty: AnswerCertainty;
  data_gaps_noted: string[];
}

export interface SynthesisComparisonRow {
  event_id: number;
  title: string;
  year: number;
  window_score: number | null;
  ripeness_status: string | null;
  agrees: boolean;
  explanation: string;
}

export interface SynthesisAnswer {
  summary: string;
  quantitative_qualitative_comparison: SynthesisComparisonRow[];
  central_finding: string;
  answer_certainty: AnswerCertainty;
  data_gaps_noted: string[];
}

export interface CompareAnswer {
  zopa_difference: string;
  power_comparison: string;
  ripeness_difference: string;
  central_contrast: string;
  answer_certainty: AnswerCertainty;
  data_gaps_noted: string[];
}

// ---------- Analytics (ντετερμινιστικοί δείκτες ισχύος, βλ. CLAUDE.md) ----------
// ΠΡΟΣΟΧΗ: αυτά ΔΕΝ είναι Pydantic schemas -- τα /analytics endpoints
// επιστρέφουν plain dict (βλ. backend/app/api/analytics.py), όχι
// response_model. Τα τύποι εδώ αντιγράφουν το ακριβές shape του dict.

// Αντιστοιχεί στο response του GET /analytics/power-index-breakdown/{country_id}/{year}
export interface PowerIndexBreakdown {
  country_id: number;
  year: number;
  economic: number;
  military: number;
  social: number;
  power_index: number;
}

// Αντιστοιχεί στο response του GET /analytics/window-score/{year}
export interface WindowScoreResult {
  year: number;
  window_score: number;
}

// ---------- Auth ----------

export type UserRole = "ADMIN" | "VIEWER";

// Αντιστοιχεί στο UserRead (backend/app/schemas/user.py) -- ΔΕΝ έχει
// hashed_password, το backend δεν το επιστρέφει ποτέ
export interface User {
  id: number;
  email: string;
  role: UserRole;
}

// Αντιστοιχεί στο UserCreate -- role optional, το backend βάζει VIEWER
// default αν λείπει
export interface RegisterPayload {
  email: string;
  password: string;
  role?: UserRole;
}

// Αντιστοιχεί στο UserLogin
export interface LoginPayload {
  email: string;
  password: string;
}

// Αντιστοιχεί στο Token
export interface AuthToken {
  access_token: string;
  token_type: string;
}
