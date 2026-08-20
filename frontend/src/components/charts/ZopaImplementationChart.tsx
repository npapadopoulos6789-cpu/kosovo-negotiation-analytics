import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { NegotiationEvent, ZopaSize } from "../../api/types";

interface ZopaImplementationChartProps {
  events: NegotiationEvent[];
}

// Γκρι-άξονα βαθμωτό: σκουρότερο = ευρύτερη ZOPA. Ίδια λογιστική με τα
// Badge tones (ui.css), όχι traffic-light χρώματα -- ακαδημαϊκό ύφος.
// Recharts θέλει πραγματικές τιμές χρώματος, όχι CSS custom properties,
// γι' αυτό hex εδώ (ίδιες τιμές με το ui.css).
const ZOPA_COLOR: Record<ZopaSize, string> = {
  NARROW: "#cfd4db",
  MODERATE: "#9aa5b1",
  WIDE: "#22314f",
};

interface ChartRow {
  id: number;
  label: string;
  implementationPct: number;
  zopa_size: ZopaSize;
  title: string;
}

// implementation_success είναι null για events χωρίς συμφωνία (καμία
// τιμή να δείξουμε) -- ΔΕΝ τα δείχνουμε ως 0%, τα αφαιρούμε εντελώς από
// το chart. Ίδιο "null σημαίνει απουσία δεδομένων" convention με το
// backend/CLAUDE.md.
function buildChartData(events: NegotiationEvent[]): ChartRow[] {
  return events
    .filter((e) => e.implementation_success !== null && e.zopa_size !== null)
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((e) => ({
      id: e.id,
      label: e.date.slice(0, 4), // year -- πιο ευανάγνωστο στον X άξονα από πλήρη τίτλο
      implementationPct: Math.round((e.implementation_success as number) * 100),
      zopa_size: e.zopa_size as ZopaSize,
      title: e.title,
    }));
}

export function ZopaImplementationChart({ events }: ZopaImplementationChartProps) {
  const data = buildChartData(events);

  return (
    <div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e2e6" />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} />
          <YAxis
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 12 }}
            label={{ value: "Implementation success", angle: -90, position: "insideLeft", fontSize: 12 }}
          />
          <Tooltip
            formatter={(value) => [`${value}%`, "Implementation success"]}
            labelFormatter={(_label, payload) => (payload?.[0]?.payload as ChartRow | undefined)?.title ?? ""}
          />
          <Bar dataKey="implementationPct" radius={[3, 3, 0, 0]}>
            {data.map((row) => (
              <Cell key={row.id} fill={ZOPA_COLOR[row.zopa_size]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ display: "flex", gap: "1rem", justifyContent: "center", fontSize: "0.8rem", marginTop: "0.5rem" }}>
        {(Object.keys(ZOPA_COLOR) as ZopaSize[]).map((size) => (
          <span key={size} style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
            <span
              style={{
                display: "inline-block",
                width: "0.7rem",
                height: "0.7rem",
                borderRadius: "2px",
                background: ZOPA_COLOR[size],
              }}
            />
            {size}
          </span>
        ))}
      </div>
    </div>
  );
}
