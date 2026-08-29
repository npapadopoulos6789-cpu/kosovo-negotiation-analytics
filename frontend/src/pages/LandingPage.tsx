import { Link } from "react-router-dom";
import { Card } from "../components/ui";

// Αρχική σελίδα ("/"). Το Dashboard ("/dashboard") έχει μόνο charts -- όλο
// το αφηγηματικό/εισαγωγικό κείμενο ζει εδώ. Card-based sections (ΟΧΙ ένας
// συνεχής τοίχος κειμένου) -- κάθε ενότητα δικό της heading + Card, ίδια
// navy/γκρι παλέτα με το υπόλοιπο site, κανένα νέο χρώμα/στυλ.
export function LandingPage() {
  return (
    <div>
      {/* ---------- Hero: τίτλος + ΜΙΑ δυνατή πρόταση + CTAs ---------- */}
      <h1 style={{ fontSize: "2.25rem", marginBottom: "0.75rem" }}>Kosovo Negotiation Analytics</h1>
      <p style={{ fontSize: "1.15rem", maxWidth: "620px", lineHeight: 1.5 }}>
        A research platform that checks a postgraduate thesis's qualitative reading of the
        Serbia-Kosovo negotiations (1989-2023) against real, independently measured data -- to
        see when, and why, conditions were actually ripe for agreement.
      </p>

      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", margin: "1.5rem 0 2.5rem" }}>
        <Link
          to="/dashboard"
          style={{
            padding: "0.75rem 1.4rem",
            borderRadius: "6px",
            background: "var(--color-accent, #22314f)",
            color: "#fff",
            textDecoration: "none",
            fontWeight: 600,
            fontSize: "1rem",
          }}
        >
          Explore the data
        </Link>
        <Link
          to="/register"
          style={{
            padding: "0.75rem 1.4rem",
            borderRadius: "6px",
            border: "1px solid var(--color-border, #d7dbe0)",
            color: "var(--color-text, #1a2130)",
            textDecoration: "none",
            fontWeight: 600,
            fontSize: "1rem",
          }}
        >
          Create free account
        </Link>
      </div>

      {/* ---------- Καθαρές, ξεχωριστές ενότητες (κάρτες) ---------- */}
      <div style={{ display: "grid", gap: "1.25rem", maxWidth: "680px" }}>
        <Card>
          <h2 style={{ marginTop: 0 }}>The research question</h2>
          <p>
            A postgraduate thesis analyzed these negotiations qualitatively, in depth -- ZOPA,
            BATNA, Zartman ripeness, red lines. This platform asks whether those qualitative
            findings actually agree with real, measurable data. Quantitative indicators
            (economic, military, social) from public sources -- World Bank, Freedom House, and
            others -- feed a composite Power Index, computed with deterministic code, never
            AI-generated numbers. An LLM (Claude) is used only afterwards, to connect those
            numbers to negotiation theory -- it never invents data, only interprets what already
            exists here. The full four-stage calculation is on the{" "}
            <Link to="/methodology">How it works</Link> page.
          </p>
          <p style={{ marginTop: "0.75rem" }}>
            Why it matters: deciding whether a negotiation window is genuinely ripe -- not just
            declared so after the fact, once an agreement has already happened or failed -- is
            exactly the kind of judgment mediators, policymakers, and analysts have to make in
            real time, usually without the benefit of hindsight. A qualitative read that can be
            checked against independent, measurable data is more useful than one that can only be
            asserted persuasively, however well-argued.
          </p>
        </Card>

        <div
          style={{
            background: "var(--color-accent-bg, #e7eaf0)",
            borderLeft: "3px solid var(--color-accent, #22314f)",
            borderRadius: "6px",
            padding: "1rem 1.25rem",
          }}
        >
          <strong>The thesis statement</strong>
          <p style={{ marginTop: "0.5rem" }}>
            The underlying thesis argues that 2013 -- the year of the Brussels Agreement -- was
            the most ripe moment in this negotiation record: a rare structural alignment of power
            symmetry, a mutually declining trend, and comparatively stable domestic conditions. A
            qualitative argument like that is only as strong as the evidence behind it, though --
            which is the actual point of this platform. It combines that qualitative reading with
            independent, deterministic quantitative measures -- the Power Index and Window Score,
            built from real economic, military, and social data -- to check whether the numbers
            actually support the theory, not just illustrate it. Explore the Dashboard's charts
            and the Window Score Sensitivity Explorer there to see how that claim holds up under
            scrutiny.
          </p>
        </div>

        <Card>
          <h2 style={{ marginTop: 0 }}>Beyond Serbia and Kosovo</h2>
          <p>
            The real idea behind this platform isn't Serbia and Kosovo specifically -- it's a way
            of thinking: pair a qualitative reading of a negotiation with independent, measurable
            data, and check whether the two actually agree, instead of taking either on faith.
            That same approach could reach further than economic, military, and social data --
            energy dependence, trade flows, and other dimensions of power aren't covered here yet,
            but nothing about the model rules them out. And it doesn't have to stop at one
            dispute: the same method could connect other major negotiations and regions too,
            comparing how power dynamics actually played out across different conflicts, not just
            this one. See "Beyond this case study" in the README for the technical version of
            this same argument.
          </p>
        </Card>
      </div>

      <h2 style={{ marginTop: "2.5rem" }}>What you can do</h2>
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
