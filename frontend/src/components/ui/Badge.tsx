import type { ReactNode } from "react";
import "./ui.css";

export type BadgeTone = "neutral" | "positive" | "warning" | "negative";

interface BadgeProps {
  children: ReactNode;
  tone?: BadgeTone;
}

// Μικρή ετικέτα για enum τιμές (actor_type, zopa_size, ripeness_status, ...).
// Το "tone" είναι σκόπιμα ξεχωριστό από το ίδιο το enum -- η κάθε σελίδα
// αποφασίζει τι σημαίνει "positive" για το δικό της enum (π.χ. RIPE θετικό
// για ripeness, αλλά ΔΕΝ βγάζει νόημα να προσπαθήσουμε να το μαντέψουμε εδώ).
// Tones εκφράζονται με βάρος/σκίαση γκρι-άξονα, όχι traffic-light χρώματα
// (βλ. ui.css) -- ακαδημαϊκό, όχι δραματικό ύφος.
export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}
