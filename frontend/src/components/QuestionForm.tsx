import { useState } from "react";
import type { FormEvent } from "react";

interface QuestionFormProps {
  onSubmit: (question: string) => void;
  isSubmitting: boolean;
  placeholder?: string;
}

// Γενική φόρμα ερώτησης -- δεν ξέρει τίποτα για event/synthesis/compare,
// απλά παίρνει το κείμενο και το περνάει στον caller. Ο caller αποφασίζει
// ΤΙ σημαίνει η ερώτηση (per-event Q&A εδώ· synthesis/compare αργότερα,
// ίδιο component, επαναχρησιμοποιήσιμο).
export function QuestionForm({ onSubmit, isSubmitting, placeholder }: QuestionFormProps) {
  const [question, setQuestion] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = question.trim();
    if (trimmed) {
      onSubmit(trimmed);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder={placeholder ?? "Ask a question about this data…"}
        rows={3}
        style={{ padding: "0.5rem", fontFamily: "inherit" }}
      />
      <button type="submit" disabled={isSubmitting || !question.trim()} style={{ alignSelf: "flex-start" }}>
        {isSubmitting ? "Asking…" : "Ask"}
      </button>
    </form>
  );
}
