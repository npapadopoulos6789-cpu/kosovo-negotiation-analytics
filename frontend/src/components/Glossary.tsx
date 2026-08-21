import { useState } from "react";
import { Card } from "./ui";
import "./ui/ui.css";

interface GlossaryTerm {
  term: string;
  definition: string;
}

const TERMS: GlossaryTerm[] = [
  {
    term: "ZOPA",
    definition:
      "Zone of Possible Agreement: the range of outcomes where both sides' minimum acceptable " +
      "terms overlap. If the two sides' bottom lines don't overlap at all, no deal is " +
      "mathematically possible, regardless of goodwill.",
  },
  {
    term: "BATNA",
    definition:
      "Best Alternative to a Negotiated Agreement: what each side would realistically do if the " +
      "talks collapsed. A strong BATNA gives a side less incentive to compromise; a weak one " +
      "pushes them toward a deal.",
  },
  {
    term: "Ripeness",
    definition:
      "Whether the negotiating parties have reached a point where both sides see more to gain " +
      "from a deal than from continuing the deadlock -- typically because prolonging the " +
      "conflict has become too costly for at least one side (a \"mutually hurting stalemate,\" " +
      "per Zartman's ripeness theory). Ripeness is about timing, not just goodwill.",
  },
  {
    term: "Power Index",
    definition:
      "A composite 0-100 score combining a country's economic (40%), military (40%), and " +
      "social-stability (20%) indicators for a given year. This is exactly how the Power Index " +
      "shown throughout this platform is calculated -- it's a structural measure of relative " +
      "strength, not a prediction of negotiating behavior.",
  },
  {
    term: "Window Score",
    definition:
      "A composite score estimating how favorable a specific year was for reaching a durable " +
      "agreement, combining power symmetry between the two sides, the trend in that symmetry " +
      "over time, and domestic social stability (not instability -- per the thesis, internal " +
      "instability raises the political cost of concessions rather than easing them). A high " +
      "Window Score does not guarantee an agreement was reached or implemented -- see the " +
      "\"Window Score vs Implementation\" chart for that gap.",
  },
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
