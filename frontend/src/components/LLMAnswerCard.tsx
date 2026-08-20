import type { NegotiationAnalysis } from "../api/types";
import { Card } from "./ui";

interface LLMAnswerCardProps {
  analysis: NegotiationAnalysis;
}

// Κάθε LLM απάντηση εμφανίζεται ΠΑΝΤΑ με disclaimer -- βλ. CLAUDE.md "LLM
// integration": "Κάθε απάντηση αποθηκεύεται ως NegotiationAnalysis και
// εμφανίζεται με disclaimer." Δεν είναι πηγή δεδομένων, είναι ερμηνεία
// πάνω σε δοθέντα.
export function LLMAnswerCard({ analysis }: LLMAnswerCardProps) {
  return (
    <Card>
      <p style={{ fontWeight: 600 }}>{analysis.user_question}</p>
      <p style={{ whiteSpace: "pre-wrap", marginTop: "0.5rem" }}>{analysis.llm_answer}</p>
      <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginTop: "0.75rem" }}>
        AI-generated interpretation of the data already in this platform -- not a primary
        source, verify against the underlying events/indicators. Model: {analysis.model_used ?? "unknown"}
        {" · "}
        {new Date(analysis.created_at).toLocaleString()}
      </p>
    </Card>
  );
}
