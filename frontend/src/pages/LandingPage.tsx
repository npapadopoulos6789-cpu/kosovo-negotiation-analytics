import { Link } from "react-router-dom";
import { Card } from "../components/ui";

// Αρχική σελίδα ("/"). Το Dashboard ("/dashboard") έχει ΠΙΑ μόνο charts --
// όλο το αφηγηματικό/εισαγωγικό κείμενο (intro, thesis statement) ΜΕΤΑΚΟΜΙΣΕ
// εδώ (ΟΧΙ αντιγράφηκε) από το DashboardPage, ώστε τα δύο να έχουν σαφή,
// ξεχωριστό ρόλο: εδώ εξηγούμε ΤΙ/ΓΙΑΤΙ, εκεί δείχνουμε τα δεδομένα.
export function LandingPage() {
  return (
    <div>
      <h1 style={{ fontSize: "2rem" }}>Kosovo Negotiation Analytics</h1>
      <p style={{ fontSize: "1.05rem", maxWidth: "640px" }}>
        A research platform on the Serbia-Kosovo negotiations (1989-2023): real historical,
        economic, military, and social data, paired with a deterministic Power Index and Window
        Score, and read through the qualitative findings of a postgraduate thesis grounded in
        negotiation theory (Zartman ripeness, BATNA/ZOPA, red lines). The goal throughout is to
        see when, and why, conditions were -- or weren't -- actually ripe for agreement, not just
        to assert it.
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
      <p style={{ maxWidth: "640px" }}>
        Why it matters: deciding whether a negotiation window is genuinely ripe -- not just
        declared so after the fact, once an agreement has already happened or failed -- is exactly
        the kind of judgment mediators, policymakers, and analysts have to make in real time,
        usually without the benefit of hindsight. A qualitative read that can be checked against
        independent, measurable data is more useful than one that can only be asserted
        persuasively, however well-argued.
      </p>

      <div
        style={{
          background: "var(--color-accent-bg, #e7eaf0)",
          borderLeft: "3px solid var(--color-accent, #22314f)",
          borderRadius: "6px",
          padding: "1rem 1.25rem",
          margin: "1.5rem 0",
          maxWidth: "640px",
        }}
      >
        <strong>The thesis statement</strong>
        <p style={{ marginTop: "0.5rem" }}>
          The underlying thesis argues that 2013 -- the year of the Brussels Agreement -- was the
          most ripe moment in this negotiation record: a rare structural alignment of power
          symmetry, a mutually declining trend, and comparatively stable domestic conditions. A
          qualitative argument like that is only as strong as the evidence behind it, though --
          which is the actual point of this platform. It combines that qualitative reading with
          independent, deterministic quantitative measures -- the Power Index and Window Score,
          built from real economic, military, and social data -- to check whether the numbers
          actually support the theory, not just illustrate it. Explore the Dashboard's charts and
          the Window Score Sensitivity Explorer there to see how that claim holds up under
          scrutiny.
        </p>
      </div>

      <h2 style={{ marginTop: "2rem" }}>Beyond Serbia and Kosovo</h2>
      <p style={{ maxWidth: "640px" }}>
        The real idea behind this platform isn't Serbia and Kosovo specifically -- it's a way of
        thinking: pair a qualitative reading of a negotiation with independent, measurable data,
        and check whether the two actually agree, instead of taking either on faith. That same
        approach could reach further than economic, military, and social data -- energy
        dependence, trade flows, and other dimensions of power aren't covered here yet, but
        nothing about the model rules them out. And it doesn't have to stop at one dispute: the
        same method could connect other major negotiations and regions too, comparing how power
        dynamics actually played out across different conflicts, not just this one. See "Beyond
        this case study" in the README for the technical version of this same argument.
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
