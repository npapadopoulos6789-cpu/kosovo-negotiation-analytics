import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useCountryLookup } from "../../hooks/useCountryLookup";
import { listNegotiationEvents } from "../../api/negotiationEvents";
import { getWindowScore } from "../../api/analytics";
import { ApiError } from "../../api/client";
import { LoadingState, ErrorState } from "../ui";

// Ίδιος περιορισμός με τα charts 2 και 4 -- Window Score χρειάζεται πλήρες
// Power Index και για τις δύο χώρες, μόνο αυτά τα 4 KEY_YEARS το έχουν
// (επιβεβαιωμένο εμπειρικά, βλ. PROJECT_STATUS.md).
const WINDOW_SCORE_YEARS = [2005, 2007, 2013, 2023] as const;

async function windowScoreOrNull(year: number, serbiaId: number, kosovoId: number) {
  try {
    const result = await getWindowScore(year, serbiaId, kosovoId);
    return result.window_score;
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

interface ChartRow {
  year: number;
  windowScore: number | null;
  implementationPct: number | null;
  eventTitle: string | null;
}

export function WindowScoreVsImplementationChart() {
  const { countryMap, isLoading: countriesLoading } = useCountryLookup();
  const serbia = [...countryMap.values()].find((c) => c.name === "Serbia");
  const kosovo = [...countryMap.values()].find((c) => c.name === "Kosovo");

  const query = useQuery({
    queryKey: ["window-score-vs-implementation", serbia?.id, kosovo?.id],
    queryFn: async (): Promise<ChartRow[]> => {
      const [events, ...windowScores] = await Promise.all([
        listNegotiationEvents(),
        ...WINDOW_SCORE_YEARS.map((year) => windowScoreOrNull(year, serbia!.id, kosovo!.id)),
      ]);

      // implementation_success ζει στο NegotiationEvent, ΟΧΙ σε analytics
      // endpoint -- ταιριάζουμε ανά έτος (date.getFullYear()). Αν δεν
      // υπάρχει KANENA event εκείνο το έτος (π.χ. 2005), ή το event
      // υπάρχει αλλά implementation_success είναι null (καμία συμφωνία),
      // και τα δύο είναι φυσιολογικά -- όχι σφάλμα.
      return WINDOW_SCORE_YEARS.map((year, i) => {
        const event = events.find((e) => Number(e.date.slice(0, 4)) === year);
        return {
          year,
          windowScore: windowScores[i],
          implementationPct: event?.implementation_success != null ? event.implementation_success * 100 : null,
          eventTitle: event?.title ?? null,
        };
      });
    },
    enabled: !!serbia && !!kosovo,
  });

  if (countriesLoading || query.isLoading) return <LoadingState label="Loading Window Score vs. implementation data…" />;
  if (!serbia || !kosovo) {
    return <ErrorState error={new Error("Serbia/Kosovo not found among seeded actors.")} />;
  }
  if (query.error) return <ErrorState error={query.error} />;

  const data = query.data ?? [];

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e2e6" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value, name) => [value, name]}
            labelFormatter={(year) => {
              const row = data.find((r) => r.year === year);
              return row?.eventTitle ? `${year} -- ${row.eventTitle}` : String(year);
            }}
          />
          <Legend wrapperStyle={{ fontSize: "0.85rem" }} />
          <Bar dataKey="windowScore" name="Window Score" fill="#22314f" radius={[3, 3, 0, 0]} />
          <Bar
            dataKey="implementationPct"
            name="Implementation success (×100 for display)"
            fill="#9aa5b1"
            radius={[3, 3, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
      <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", textAlign: "center", marginTop: "0.25rem" }}>
        Window Score (0-100) and implementation_success (0-1, scaled ×100 here for a shared axis
        -- these are different measures, not directly comparable units) are shown side by side.
        2005 has no negotiation event; missing bars are absent data, not zero.
      </p>
    </div>
  );
}
