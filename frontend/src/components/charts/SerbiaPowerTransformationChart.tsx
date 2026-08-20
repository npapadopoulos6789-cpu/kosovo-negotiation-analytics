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
import { getPowerIndexBreakdown } from "../../api/analytics";
import { ApiError } from "../../api/client";
import { LoadingState, ErrorState } from "../ui";

// Δέκα έτη -- η ΕΝΩΣΗ όλων των ετών όπου η Σερβία έχει ΤΟΥΛΑΧΙΣΤΟΝ κάποιο
// indicator seeded (βλ. seed.py), ΟΧΙ το backend KEY_YEARS (6 έτη, το
// σύνολο που χρησιμοποιεί το optimal-period search, βλ.
// services/analytics.py) και ΟΧΙ το AVAILABLE_YEARS του Power Index
// Breakdown chart (4 έτη, περιορισμένο σε "και οι δύο χώρες"). Εδώ θέλουμε
// ΟΛΑ τα υποψήφια έτη -- ρητό ζητούμενο: bar ανά έτος, stacked, ΧΩΡΙΣ
// γραμμή/area που θα υπονοούσε συνέχεια ανάμεσα σε αραιά σημεία.
const CANDIDATE_YEARS = [1998, 1999, 2000, 2005, 2007, 2008, 2013, 2018, 2020, 2023] as const;

// 404 = "δεν υπάρχει πλήρες σύνολο indicators (economic+military+social)
// για αυτό το έτος" (π.χ. Freedom House gate -- η social κατηγορία
// ξεκινά μόλις το 2005, βλ. CLAUDE.md). ΟΧΙ σφάλμα, ΟΧΙ 0.
async function breakdownOrNull(countryId: number, year: number) {
  try {
    return await getPowerIndexBreakdown(countryId, year);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

interface ChartRow {
  year: number;
  economic: number | null;
  military: number | null;
  social: number | null;
}

export function SerbiaPowerTransformationChart() {
  const { countryMap, isLoading: countryLoading } = useCountryLookup();
  const serbia = [...countryMap.values()].find((c) => c.name === "Serbia");

  const query = useQuery({
    queryKey: ["power-index-breakdown", "serbia-transformation", serbia?.id],
    queryFn: async (): Promise<ChartRow[]> => {
      const results = await Promise.all(
        CANDIDATE_YEARS.map((year) => breakdownOrNull(serbia!.id, year)),
      );
      return CANDIDATE_YEARS.map((year, i) => {
        const r = results[i];
        return {
          year,
          economic: r?.economic ?? null,
          military: r?.military ?? null,
          social: r?.social ?? null,
        };
      });
    },
    enabled: !!serbia,
  });

  if (countryLoading || query.isLoading) return <LoadingState label="Loading Serbia's power index history…" />;
  if (!serbia) return <ErrorState error={new Error("Serbia not found among seeded actors.")} />;
  if (query.error) return <ErrorState error={query.error} />;

  const data = query.data ?? [];
  const missingYears = data.filter((row) => row.economic === null).map((row) => row.year);

  return (
    <div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e2e6" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend wrapperStyle={{ fontSize: "0.85rem" }} />
          {/* stackId="power" -- τα 3 segments στοιβάζονται στο ίδιο bar ανά
              έτος. null τιμές (έτη χωρίς δεδομένα) δεν παράγουν segment,
              ΔΕΝ εμφανίζονται σαν 0. */}
          <Bar dataKey="economic" name="Economic" stackId="power" fill="#22314f" />
          <Bar dataKey="military" name="Military" stackId="power" fill="#5b6472" />
          <Bar dataKey="social" name="Social" stackId="power" fill="#9aa5b1" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      {missingYears.length > 0 && (
        <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", textAlign: "center", marginTop: "0.25rem" }}>
          No data available for: {missingYears.join(", ")} (empty columns above -- not zero values).
        </p>
      )}
    </div>
  );
}
