import { Link } from "react-router-dom";
import { Card } from "../components/ui";

// Νέα αρχική σελίδα ("/") -- πριν ήταν το Dashboard εδώ, μετακόμισε σε
// "/dashboard" (βλ. App.tsx/Layout.tsx). Σκοπός: εξηγεί ΤΙ είναι η
// πλατφόρμα πριν δείξει δεδομένα -- condensed version του "About this
// project"/"What it does" του README.md, όχι αντιγραφή 1:1.
export function LandingPage() {
  return (
    <div>
      <h1 style={{ fontSize: "2rem" }}>Kosovo Negotiation Analytics</h1>
      <p style={{ fontSize: "1.05rem", maxWidth: "640px" }}>
        A research platform on the Serbia-Kosovo negotiations (1989-2023) -- real historical,
        economic, military, and social data, paired with a deterministic Power Index/Window Score
        and LLM-assisted interpretation grounded in negotiation theory (Zartman ripeness,
        BATNA/ZOPA, red lines).
      </p>

      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", margin: "1.25rem 0 2rem" }}>
        <Link
          to="/dashboard"
          style={{
            padding: "0.65rem 1.1rem",
            borderRadius: "6px",
            background: "var(--color-accent, #22314f)",
            color: "#fff",
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          Explore the data
        </Link>
        <Link
          to="/register"
          style={{
            padding: "0.65rem 1.1rem",
            borderRadius: "6px",
            border: "1px solid var(--color-border, #d7dbe0)",
            color: "var(--color-text, #1a2130)",
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          Create free account
        </Link>
      </div>

      <h2>The research question</h2>
      <p style={{ maxWidth: "640px" }}>
        A postgraduate thesis analyzed these negotiations qualitatively, in depth -- ZOPA, BATNA,
        Zartman ripeness, red lines. This platform asks whether those qualitative findings actually
        agree with real, measurable data. Quantitative indicators (economic, military, social) from
        public sources -- World Bank, Freedom House, and others -- feed a composite Power Index (40%
        economy / 40% military / 20% social stability), computed with deterministic code, never
        AI-generated numbers. An LLM (Claude) is used only afterwards, to connect those numbers to
        negotiation theory -- it never invents data, only interprets what already exists here.
      </p>

      <h2 style={{ marginTop: "2rem" }}>What you can do</h2>
      <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))" }}>
        <Card>
          <strong>Free, no account needed</strong>
          <p style={{ marginTop: "0.5rem" }}>
            Explore the underlying data yourself: <strong>Actors</strong> (states and international
            actors), <strong>Events</strong> (10 milestones, 1989-2023, with ZOPA/BATNA/ripeness),
            and the <strong>Dashboard</strong> (5 interactive charts built on the deterministic
            scores).
          </p>
        </Card>
        <Card>
          <strong>Needs a free account</strong>
          <p style={{ marginTop: "0.5rem" }}>
            <strong>Synthesis</strong> and <strong>Compare</strong> run a real LLM analysis call per
            question -- an AI-generated interpretation of the data, with an explicit disclaimer on
            every answer. Asking a question about a single event (on its Event page) stays free,
            no account needed.
          </p>
        </Card>
      </div>
    </div>
  );
}
