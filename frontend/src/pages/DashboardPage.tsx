import { useQuery } from "@tanstack/react-query";
import { listNegotiationEvents } from "../api/negotiationEvents";
import { ZopaImplementationChart } from "../components/charts/ZopaImplementationChart";
import { PowerIndexBreakdownChart } from "../components/charts/PowerIndexBreakdownChart";
import { SerbiaPowerTransformationChart } from "../components/charts/SerbiaPowerTransformationChart";
import { PoliticalVsEconomicCostChart } from "../components/charts/PoliticalVsEconomicCostChart";
import { WindowScoreVsImplementationChart } from "../components/charts/WindowScoreVsImplementationChart";
import { Glossary } from "../components/Glossary";
import { EconomySizeContext } from "../components/EconomySizeContext";
import { LoadingState, ErrorState, EmptyState } from "../components/ui";

export function DashboardPage() {
  const { data: events, isLoading, error } = useQuery({
    queryKey: ["negotiation-events"],
    queryFn: listNegotiationEvents,
  });

  return (
    <div>
      <h1>Dashboard</h1>
      <p>
        This platform pairs quantitative power indicators -- Power Index and Window Score,
        computed from real economic, military, and social data -- with the qualitative findings
        of a thesis on the Serbia-Kosovo negotiations. Use the charts below to explore
        interactively when, and why, conditions were (or weren't) ripe for agreement.
      </p>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Below are the key concepts used throughout this platform -- click each one to see how
        it's defined and calculated.
      </p>

      <Glossary />

      <div style={{ marginTop: "1.5rem" }}>
        <EconomySizeContext />
      </div>

      <h2 style={{ marginTop: "2rem" }}>ZOPA size vs. implementation success</h2>
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

      <h2 style={{ marginTop: "2rem" }}>Power Index breakdown</h2>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Economic (40%) / Military (40%) / Social (20%) components of the Power Index, Serbia vs.
        Kosovo. Only years with indicator data for both countries are selectable.
      </p>
      <PowerIndexBreakdownChart />

      <h2 style={{ marginTop: "2rem" }}>Serbia's power transformation</h2>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Economic/Military/Social components of Serbia's own Power Index over time, one bar per
        year with data (bars, not a line -- these years are sparse, a continuous line would imply
        data in years that don't exist). Note: stacked as raw 0-100 category scores for
        readability -- the stack height is <em>not</em> the Power Index itself, which weights
        them 40% / 40% / 20% rather than summing them equally (see CLAUDE.md).
      </p>
      <SerbiaPowerTransformationChart />

      <h2 style={{ marginTop: "2rem" }}>Political vs. economic cost</h2>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Freedom House score (political stability, both countries) vs. Window Score (composite
        ripeness signal) -- same 0-100 scale, so a line is legitimate here. The Window Score line
        breaks where data is missing rather than interpolating across it.
      </p>
      <PoliticalVsEconomicCostChart />

      <h2 style={{ marginTop: "2rem" }}>Window Score vs. implementation success</h2>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        The central finding: conditions were structurally ripe in 2013 and 2023 (high Window
        Score), but the resulting agreements were only partially implemented. Different scales --
        implementation_success (0-1) is shown ×100 for a shared axis, labeled explicitly below.
      </p>
      <WindowScoreVsImplementationChart />
    </div>
  );
}
