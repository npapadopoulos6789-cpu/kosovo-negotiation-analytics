import { useState } from "react";
import { Card } from "./ui";
import "./ui/ui.css";

interface GlossaryTerm {
  term: string;
  definition: string;
}

const TERMS: GlossaryTerm[] = [
  { term: "ZOPA", definition: "The range where both sides could realistically agree." },
  { term: "BATNA", definition: "What each side would do if talks failed." },
  { term: "Ripeness", definition: "Whether conditions are favorable for a deal right now." },
  { term: "Power Index", definition: "A composite score of a country's economic/military/social strength." },
  { term: "Window Score", definition: "How favorable a specific year was for reaching agreement." },
];

// Κλικαρίσιμα chips, ξαναχρησιμοποιούν την ίδια .badge κλάση από το
// ui.css (ίδιο navy/γκρι στυλ με το Badge component) -- <button> αντί
// για <span> για σωστή προσβασιμότητα (focus/keyboard/aria-expanded).
// Default: όλα κλειστά, ο χρήστης ανοίγει μόνο ό,τι θέλει (ρητό
// ζητούμενο -- να μην πλημμυρίζει τη σελίδα).
export function Glossary() {
  const [openTerms, setOpenTerms] = useState<Set<string>>(new Set());

  function toggle(term: string) {
    setOpenTerms((prev) => {
      const next = new Set(prev);
      if (next.has(term)) {
        next.delete(term);
      } else {
        next.add(term);
      }
      return next;
    });
  }

  const openList = TERMS.filter((t) => openTerms.has(t.term));

  return (
    <div>
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        {TERMS.map(({ term }) => {
          const isOpen = openTerms.has(term);
          return (
            <button
              key={term}
              type="button"
              onClick={() => toggle(term)}
              aria-expanded={isOpen}
              className={isOpen ? "badge badge--positive" : "badge"}
              style={{ border: "none", font: "inherit", cursor: "pointer" }}
            >
              {term} {isOpen ? "−" : "+"}
            </button>
          );
        })}
      </div>
      {openList.length > 0 && (
        <div style={{ display: "grid", gap: "0.5rem", marginTop: "0.75rem" }}>
          {openList.map(({ term, definition }) => (
            <Card key={term}>
              <strong>{term}</strong>
              <p style={{ marginTop: "0.25rem" }}>{definition}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
