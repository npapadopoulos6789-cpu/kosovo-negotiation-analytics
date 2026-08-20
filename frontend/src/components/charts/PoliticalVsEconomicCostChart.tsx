import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useCountryLookup } from "../../hooks/useCountryLookup";
import { listIndicatorsByCountry } from "../../api/indicators";
import { getWindowScore } from "../../api/analytics";
import { ApiError } from "../../api/client";
import { LoadingState, ErrorState, EmptyState } from "../ui";

const FREEDOM_HOUSE_TYPE = "freedom_house_score";

// 404 = "ανεπαρκή δεδομένα" (π.χ. λείπει πλήρες Power Index και για τις
// δύο χώρες εκείνο το έτος) -- ΟΧΙ σφάλμα, ΟΧΙ 0. Ίδιο convention με τα
// υπόλοιπα charts.
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
  serbiaFH: number | null;
  kosovoFH: number | null;
  windowScore: number | null;
}

export function PoliticalVsEconomicCostChart() {
  const { countryMap, isLoading: countriesLoading } = useCountryLookup();
  const serbia = [...countryMap.values()].find((c) => c.name === "Serbia");
  const kosovo = [...countryMap.values()].find((c) => c.name === "Kosovo");

  const query = useQuery({
    queryKey: ["political-vs-economic-cost", serbia?.id, kosovo?.id],
    queryFn: async (): Promise<ChartRow[]> => {
      const [serbiaIndicators, kosovoIndicators] = await Promise.all([
        listIndicatorsByCountry(serbia!.id),
        listIndicatorsByCountry(kosovo!.id),
      ]);

      const serbiaFH = new Map(
        serbiaIndicators.filter((i) => i.indicator_type === FREEDOM_HOUSE_TYPE).map((i) => [i.year, i.value]),
      );
      const kosovoFH = new Map(
        kosovoIndicators.filter((i) => i.indicator_type === FREEDOM_HOUSE_TYPE).map((i) => [i.year, i.value]),
      );

      // Ένωση όλων των ετών όπου ΤΟΥΛΑΧΙΣΤΟΝ μία χώρα έχει Freedom House
      // τιμή -- παράγεται από τα ίδια τα δεδομένα, όχι hardcoded λίστα.
      const years = [...new Set([...serbiaFH.keys(), ...kosovoFH.keys()])].sort((a, b) => a - b);

      const windowScores = await Promise.all(
        years.map((year) => windowScoreOrNull(year, serbia!.id, kosovo!.id)),
      );

      return years.map((year, i) => ({
        year,
        serbiaFH: serbiaFH.get(year) ?? null,
        kosovoFH: kosovoFH.get(year) ?? null,
        windowScore: windowScores[i],
      }));
    },
    enabled: !!serbia && !!kosovo,
  });

  if (countriesLoading || query.isLoading) return <LoadingState label="Loading political/economic cost data…" />;
  if (!serbia || !kosovo) {
    return <ErrorState error={new Error("Serbia/Kosovo not found among seeded actors.")} />;
  }
  if (query.error) return <ErrorState error={query.error} />;

  const data = query.data ?? [];
  if (data.length === 0) return <EmptyState label="No Freedom House data available." />;

  const missingWindowYears = data.filter((row) => row.windowScore === null).map((row) => row.year);

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e2e6" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend wrapperStyle={{ fontSize: "0.85rem" }} />
          {/* connectNulls={false} (το recharts default, ρητό εδώ επίτηδες):
              η Window Score γραμμή σπάει στα έτη χωρίς δεδομένα αντί να
              υπονοεί ενδιάμεσες τιμές που δεν υπάρχουν. */}
          <Line type="monotone" dataKey="serbiaFH" name="Serbia (Freedom House)" stroke="#22314f" connectNulls={false} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="kosovoFH" name="Kosovo (Freedom House)" stroke="#9aa5b1" connectNulls={false} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="windowScore" name="Window Score" stroke="#5b6472" strokeDasharray="4 3" connectNulls={false} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
      {missingWindowYears.length > 0 && (
        <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", textAlign: "center", marginTop: "0.25rem" }}>
          Window Score unavailable for: {missingWindowYears.join(", ")} (requires full Power Index
          for both countries that year -- gap in the dashed line above, not zero).
        </p>
      )}
    </div>
  );
}
