import { Card } from "../components/ui";

// "How this works" -- προσβάσιμη εκδοχή του README's "Methodology" section
// (ίδιο περιεχόμενο, όχι "διάβασε το README"). Σκοπός: κάποιος να μπορεί να
// καταλάβει τι κάνει η πλατφόρμα ΠΡΙΝ δει τα charts στο Dashboard.
export function MethodologyPage() {
  return (
    <div>
      <h1 style={{ fontSize: "2rem" }}>How this works</h1>
      <p style={{ fontSize: "1.05rem", maxWidth: "640px" }}>
        Every number on this platform that isn't AI-generated interpretation goes through the
        same four-stage, fully deterministic calculation -- no LLM involved, same input always
        gives the same output.
      </p>

      <div
        style={{
          display: "grid",
          gap: "1rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          margin: "1.5rem 0",
        }}
      >
        <Card>
          <strong>The Power Index</strong>
          <p style={{ marginTop: "0.5rem" }}>
            A single 0-100 score, per country per year, combining economic, military, and social
            data into one measure of relative strength -- not a prediction of how a country will
            negotiate, just where it structurally stands.
          </p>
        </Card>
        <Card>
          <strong>The Window Score</strong>
          <p style={{ marginTop: "0.5rem" }}>
            A single 0-100 score, per year, estimating how favorable that specific year was for
            reaching a durable agreement -- combining how evenly matched the two sides were, the
            trend between them, and domestic stability.
          </p>
        </Card>
      </div>

      <h2 style={{ marginTop: "2rem" }}>How it's calculated -- four stages</h2>
      <div style={{ display: "grid", gap: "0.75rem", margin: "1rem 0" }}>
        <Card>
          <strong>1. Normalize</strong>
          <p style={{ marginTop: "0.5rem" }}>
            Every raw indicator (e.g. GDP growth of -10.33%) is rescaled to a common 0-100 range,
            with fixed bounds per indicator type. For unemployment, the direction is flipped -- a
            lower raw number produces a higher score, since lower unemployment is the stronger
            position. GDP and military spending use a logarithmic scale rather than a straight
            line: Serbia's economy and military budget are roughly ten times Kosovo's, and a
            plain linear scale would flatten Kosovo into an almost-constant low score regardless
            of real change.
          </p>
        </Card>
        <Card>
          <strong>2. Category score</strong>
          <p style={{ marginTop: "0.5rem" }}>
            For each country and year, the normalized indicators in the same category --
            Economic, Military, Social -- are averaged into one score per category.
          </p>
        </Card>
        <Card>
          <strong>3. Power Index</strong>
          <p style={{ marginTop: "0.5rem" }}>
            The three category scores are combined as Economic 40% + Military 40% + Social 20% --
            one 0-100 number per country per year.
          </p>
        </Card>
        <Card>
          <strong>4. Window Score</strong>
          <p style={{ marginTop: "0.5rem" }}>
            Power symmetry between Serbia and Kosovo (50% -- how close their Power Index scores
            are) + a mutual decline in power relative to the previous year with data (30% -- a
            Zartman "mutually hurting stalemate" signal) + domestic social stability (20% --
            higher stability contributes positively; internal instability raises the political
            cost of making concessions, which makes agreement harder, not easier).
          </p>
        </Card>
      </div>

      <h2 style={{ marginTop: "2rem" }}>What data is used</h2>
      <Card>
        <p>
          The 10 negotiation events and their qualitative fields (ZOPA, ripeness, BATNA, red
          lines) come from a postgraduate thesis on these negotiations, entered as structured
          data. The quantitative indicators are a mix -- some read directly from charts in that
          thesis, others pulled from the World Bank API (GDP, unemployment, military expenditure,
          FDI) and Freedom House (political stability). None of it is AI-generated: every number
          traces back to a specific, citable source.
        </p>
        <p style={{ marginTop: "0.75rem" }}>
          The 40/40/20 and 50/30/20 weightings are my own judgment about what matters most in
          this negotiation context, not an empirically derived or independently cited result --
          see the Sensitivity Explorer on the Dashboard to test how much the findings below
          actually depend on that specific choice of weights.
        </p>
      </Card>

      <h2 style={{ marginTop: "2rem" }}>The central finding</h2>
      <Card>
        <p>
          Conditions were structurally ripest in 2013 and 2023 -- both years score highest on the
          Window Score -- but the agreements reached in those years (the Brussels Agreement and
          the Ohrid Agreement) were only partially implemented. A high Window Score describes
          when a deal was structurally easiest to reach; it says nothing about whether the deal
          actually held. That gap between structural ripeness and real-world follow-through is
          the platform's central, testable finding -- see the Dashboard for the charts that show
          it directly.
        </p>
      </Card>
    </div>
  );
}
