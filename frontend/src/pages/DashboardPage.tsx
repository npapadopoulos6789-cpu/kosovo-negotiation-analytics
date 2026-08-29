import { useQuery } from "@tanstack/react-query";
import { listNegotiationEvents } from "../api/negotiationEvents";
import { ZopaImplementationChart } from "../components/charts/ZopaImplementationChart";
import { PowerIndexBreakdownChart } from "../components/charts/PowerIndexBreakdownChart";
import { SerbiaPowerTransformationChart } from "../components/charts/SerbiaPowerTransformationChart";
import { PoliticalVsEconomicCostChart } from "../components/charts/PoliticalVsEconomicCostChart";
import { WindowScoreVsImplementationChart } from "../components/charts/WindowScoreVsImplementationChart";
import { WindowScoreSensitivityExplorer } from "../components/charts/WindowScoreSensitivityExplorer";
import { Glossary } from "../components/Glossary";
import { EconomySizeContext } from "../components/EconomySizeContext";
import { LoadingState, ErrorState, EmptyState } from "../components/ui";

// "What to expect" προτάσεις πριν από κάθε chart (βλ. παρακάτω) είναι
// ΠΡΟΒΛΕΨΕΙΣ ευρήματος, βασισμένες σε πραγματικά υπολογισμένα δεδομένα
// (επιβεβαιωμένα live μέσω του API πριν γραφτούν, όχι εικασία) -- ΟΧΙ
// περιγραφή του τι μετράει το chart (αυτό παραμένει στην ήδη υπάρχουσα,
// muted παράγραφο μεθοδολογίας κάτω από κάθε τίτλο).
//
// ΣΚΟΠΙΜΑ καμία εισαγωγική/thesis-statement πρόζα εδώ -- μετακόμισε στο
// LandingPage ("/"), που είναι πλέον η μοναδική σελίδα για το "τι/γιατί".
// Το Dashboard δείχνει μόνο δεδομένα/charts.
export function DashboardPage() {
  const { data: events, isLoading, error } = useQuery({
    queryKey: ["negotiation-events"],
    queryFn: listNegotiationEvents,
  });

  return (
    <div>
      <h1>Dashboard</h1>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Below are the key concepts used throughout this platform -- click each one to see how
        it's defined and calculated.
      </p>

      <Glossary />

      <h2 style={{ marginTop: "2.5rem", fontSize: "1.3rem" }}>Setting the stage</h2>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Four charts building up the structural picture -- power balance, its composition, and how
        it moved over time -- before the central finding below.
      </p>

      <h3 style={{ marginTop: "1.5rem" }}>ZOPA size vs. implementation success</h3>
      <p>
        <em>What to expect:</em> wider-ZOPA events show somewhat better average implementation,
        but the pattern is mixed -- a moderate-ZOPA event (UN 1244) actually outperforms both
        wide-ZOPA events individually.
      </p>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Does a wider Zone of Possible Agreement predict a better-implemented outcome? Only events
        that reached an agreement (implementation_success recorded) are shown.
      </p>
      {isLoading && <LoadingState label="Loading events…" />}
      {error && <ErrorState error={error} />}
      {events && events.every((e) => e.implementation_success === null) && (
        <EmptyState label="No events with recorded implementation_success yet." />
      )}
      {events && <ZopaImplementationChart events={events} />}

      <h3 style={{ marginTop: "2rem" }}>Power Index breakdown</h3>
      <p>
        <em>What to expect:</em> Serbia's edge over Kosovo is much larger in the military and
        social-stability components than in the economic one.
      </p>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Economic (40%) / Military (40%) / Social (20%) components of the Power Index, Serbia vs.
        Kosovo. Only years with indicator data for both countries are selectable.
      </p>
      <PowerIndexBreakdownChart />

      <h3 style={{ marginTop: "2rem" }}>Serbia's power transformation</h3>
      <p>
        <em>What to expect:</em> Serbia's economic strength dips around 2013 before recovering by
        2023, while its social-stability score falls sharply over that same stretch.
      </p>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Economic/Military/Social components of Serbia's own Power Index over time, one bar per
        year with data (bars, not a line -- these years are sparse, a continuous line would imply
        data in years that don't exist). Note: stacked as raw 0-100 category scores for
        readability -- the stack height is <em>not</em> the Power Index itself, which weights
        them 40% / 40% / 20% rather than summing them equally.
      </p>
      <SerbiaPowerTransformationChart />

      <h3 style={{ marginTop: "2rem" }}>Political vs. economic cost</h3>
      <p>
        <em>What to expect:</em> Serbia's political-stability score declines while Kosovo's
        steadily rises over the same period -- their trajectories move in opposite directions.
      </p>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Freedom House score (political stability, both countries) vs. Window Score (composite
        ripeness signal) -- same 0-100 scale, so a line is legitimate here. The Window Score line
        breaks where data is missing rather than interpolating across it.
      </p>
      <PoliticalVsEconomicCostChart />

      <div
        style={{
          background: "var(--color-surface, #ffffff)",
          border: "2px solid var(--color-accent, #22314f)",
          borderRadius: "8px",
          padding: "1.5rem",
          margin: "2.5rem 0 2rem",
        }}
      >
        <h2 style={{ marginTop: 0 }}>The central finding</h2>
        <p>
          <em>What to expect:</em> conditions were structurally ripest in 2013 and 2023 (high
          Window Score) -- but the resulting agreements were only partially implemented. Ripeness
          didn't guarantee follow-through.
        </p>
        <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
          The central finding: conditions were structurally ripe in 2013 and 2023 (high Window
          Score), but the resulting agreements were only partially implemented. Different scales
          -- implementation_success (0-1) is shown ×100 for a shared axis, labeled explicitly
          below.
        </p>
        <WindowScoreVsImplementationChart />
      </div>

      <h2 style={{ marginTop: "2.5rem" }}>Window Score Sensitivity Explorer</h2>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        The Window Score above uses fixed weights (50% power symmetry / 30% mutual declining
        trend / 20% social stability). How much does the 2013 finding actually depend on that one
        specific choice of weights?
      </p>
      <WindowScoreSensitivityExplorer />

      <div style={{ marginTop: "2.5rem" }}>
        <EconomySizeContext />
      </div>
    </div>
  );
}
