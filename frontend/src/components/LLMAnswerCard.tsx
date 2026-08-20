import type {
  AnswerCertainty,
  CompareAnswer,
  NegotiationAnalysis,
  QAAnswer,
  SynthesisAnswer,
} from "../api/types";
import { Card, Badge } from "./ui";
import type { BadgeTone } from "./ui";

// Ο caller ΞΕΡΕΙ ποιο flow έκανε το call (Q&A/synthesis/compare) -- δεν
// προσπαθούμε να το μαντέψουμε από το ίδιο το NegotiationAnalysis object.
// Compare, συγκεκριμένα, είναι ΑΔΥΝΑΤΟ να ξεχωριστεί αξιόπιστα από Q&A στο
// backend response: και τα δύο έχουν is_synthesis=false και μη-null
// negotiation_event_id -- η μόνη διαφορά είναι ένα "[COMPARE]" πρόθεμα στο
// user_question, σύμβαση όχι σχήμα (βλ. negotiation_analysis.py
// create_comparison). Άρα explicit prop, όχι sniffing.
export type LLMAnswerVariant = "qa" | "synthesis" | "compare";

interface LLMAnswerCardProps {
  analysis: NegotiationAnalysis;
  variant: LLMAnswerVariant;
}

const CERTAINTY_TONE: Record<AnswerCertainty, BadgeTone> = {
  HIGH: "positive",
  MEDIUM: "warning",
  LOW: "negative",
  INSUFFICIENT_DATA: "negative",
};

function Disclaimer({ analysis }: { analysis: NegotiationAnalysis }) {
  return (
    <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginTop: "0.75rem" }}>
      AI-generated interpretation of the data already in this platform -- not a primary source,
      verify against the underlying events/indicators. Model: {analysis.model_used ?? "unknown"}
      {" · "}
      {new Date(analysis.created_at).toLocaleString()}
    </p>
  );
}

function DataGaps({ gaps }: { gaps: string[] }) {
  if (gaps.length === 0) return null;
  return (
    <div style={{ marginTop: "0.75rem" }}>
      <strong style={{ fontSize: "0.85rem" }}>Data gaps noted</strong>
      <ul style={{ margin: "0.25rem 0 0", paddingLeft: "1.25rem", fontSize: "0.85rem" }}>
        {gaps.map((gap, i) => (
          <li key={i}>{gap}</li>
        ))}
      </ul>
    </div>
  );
}

// Κάθε LLM απάντηση εμφανίζεται ΠΑΝΤΑ με disclaimer -- βλ. CLAUDE.md "LLM
// integration": "Κάθε απάντηση αποθηκεύεται ως NegotiationAnalysis και
// εμφανίζεται με disclaimer." Δεν είναι πηγή δεδομένων, είναι ερμηνεία
// πάνω σε δοθέντα.
export function LLMAnswerCard({ analysis, variant }: LLMAnswerCardProps) {
  if (!analysis.llm_answer) {
    return (
      <Card>
        <p style={{ color: "var(--color-text-muted)" }}>No answer text stored for this analysis.</p>
      </Card>
    );
  }

  let parsed: QAAnswer | SynthesisAnswer | CompareAnswer;
  try {
    parsed = JSON.parse(analysis.llm_answer);
  } catch {
    // Το backend αποθηκεύει πάντα το raw_text του LLM call χωρίς δικό
    // του JSON validation (βλ. negotiation_analysis.py) -- ένα
    // malformed response είναι θεωρητικά δυνατό. Fallback: δείξε το raw
    // κείμενο αντί να σκάσει η σελίδα.
    return (
      <Card>
        {variant === "qa" && <p style={{ fontWeight: 600 }}>{analysis.user_question}</p>}
        <p style={{ whiteSpace: "pre-wrap", marginTop: "0.5rem" }}>{analysis.llm_answer}</p>
        <p style={{ fontSize: "0.75rem", color: "var(--color-negative)", marginTop: "0.5rem" }}>
          (Raw response -- expected JSON shape was not parseable.)
        </p>
        <Disclaimer analysis={analysis} />
      </Card>
    );
  }

  return (
    <Card>
      {variant === "qa" && (
        <>
          <p style={{ fontWeight: 600 }}>{analysis.user_question}</p>
          <p style={{ whiteSpace: "pre-wrap", marginTop: "0.5rem" }}>{(parsed as QAAnswer).answer}</p>
        </>
      )}

      {variant === "synthesis" && (
        <>
          <p style={{ whiteSpace: "pre-wrap" }}>{(parsed as SynthesisAnswer).summary}</p>
          <div style={{ marginTop: "0.75rem" }}>
            <strong>Central finding</strong>
            <p style={{ whiteSpace: "pre-wrap", marginTop: "0.25rem" }}>
              {(parsed as SynthesisAnswer).central_finding}
            </p>
          </div>
          {(parsed as SynthesisAnswer).quantitative_qualitative_comparison.length > 0 && (
            <div style={{ marginTop: "0.75rem" }}>
              <strong>Quantitative vs qualitative, per event</strong>
              <div style={{ display: "grid", gap: "0.5rem", marginTop: "0.5rem" }}>
                {(parsed as SynthesisAnswer).quantitative_qualitative_comparison.map((row) => (
                  <div key={row.event_id} style={{ borderLeft: "3px solid var(--color-border)", paddingLeft: "0.6rem" }}>
                    <div style={{ display: "flex", gap: "0.4rem", alignItems: "baseline", flexWrap: "wrap" }}>
                      <strong>
                        {row.title} ({row.year})
                      </strong>
                      <Badge tone={row.agrees ? "positive" : "negative"}>
                        {row.agrees ? "agrees" : "disagrees"}
                      </Badge>
                      {row.ripeness_status && <Badge tone="neutral">{row.ripeness_status}</Badge>}
                      {row.window_score !== null && <Badge tone="neutral">Window Score: {row.window_score}</Badge>}
                    </div>
                    <p style={{ fontSize: "0.9rem", marginTop: "0.25rem" }}>{row.explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {variant === "compare" && (
        <>
          <div>
            <strong>ZOPA difference</strong>
            <p style={{ marginTop: "0.25rem" }}>{(parsed as CompareAnswer).zopa_difference}</p>
          </div>
          <div style={{ marginTop: "0.75rem" }}>
            <strong>Power comparison</strong>
            <p style={{ marginTop: "0.25rem" }}>{(parsed as CompareAnswer).power_comparison}</p>
          </div>
          <div style={{ marginTop: "0.75rem" }}>
            <strong>Ripeness difference</strong>
            <p style={{ marginTop: "0.25rem" }}>{(parsed as CompareAnswer).ripeness_difference}</p>
          </div>
          <div style={{ marginTop: "0.75rem" }}>
            <strong>Central contrast</strong>
            <p style={{ marginTop: "0.25rem" }}>{(parsed as CompareAnswer).central_contrast}</p>
          </div>
        </>
      )}

      <div style={{ marginTop: "0.75rem" }}>
        <Badge tone={CERTAINTY_TONE[parsed.answer_certainty]}>{parsed.answer_certainty}</Badge>
      </div>
      <DataGaps gaps={parsed.data_gaps_noted} />
      <Disclaimer analysis={analysis} />
    </Card>
  );
}
