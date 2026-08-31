import { useState } from "react";
import type { CSSProperties } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listIndicators, deleteIndicator } from "../../api/indicators";
import { useCountryLookup } from "../../hooks/useCountryLookup";
import type { Indicator } from "../../api/types";
import { ApiError } from "../../api/client";
import { LoadingState, ErrorState, EmptyState } from "../../components/ui";
import { AdminNav } from "../../components/admin/AdminNav";
import { IndicatorForm } from "../../components/admin/IndicatorForm";

type FormState = "closed" | "create" | Indicator;

// 100+ indicators σύνολο -- χωρίς φίλτρο ανά χώρα θα ήταν μη πρακτικό
// λιστάρισμα.
export function AdminIndicatorsPage() {
  const { countryMap, isLoading: countriesLoading, error: countriesError } = useCountryLookup();
  const indicators = useQuery({ queryKey: ["indicators"], queryFn: listIndicators });
  const queryClient = useQueryClient();

  const [countryFilter, setCountryFilter] = useState<string>("all");
  const [formState, setFormState] = useState<FormState>("closed");
  const [message, setMessage] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const deleteMutation = useMutation({
    mutationFn: deleteIndicator,
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ["indicators"] });
      setDeleteError(null);
      setMessage(`Indicator #${id} deleted.`);
    },
    onError: (err) => {
      setDeleteError(err instanceof ApiError ? (typeof err.detail === "string" ? err.detail : err.message) : "Delete failed.");
    },
  });

  if (countriesLoading || indicators.isLoading) return <LoadingState label="Loading indicators…" />;
  if (countriesError) return <ErrorState error={countriesError} />;
  if (indicators.error) return <ErrorState error={indicators.error} />;

  const countries = [...countryMap.values()].sort((a, b) => a.name.localeCompare(b.name));

  const rows = (indicators.data ?? [])
    .filter((ind) => countryFilter === "all" || ind.country_id === Number(countryFilter))
    .sort((a, b) => {
      const countryCompare = (countryMap.get(a.country_id)?.name ?? "").localeCompare(
        countryMap.get(b.country_id)?.name ?? "",
      );
      return countryCompare !== 0 ? countryCompare : a.year - b.year;
    });

  function handleFormSuccess(successMessage: string) {
    setFormState("closed");
    setMessage(successMessage);
  }

  function handleDelete(indicator: Indicator) {
    if (window.confirm(`Delete indicator "${indicator.indicator_type}" (${indicator.year})? This cannot be undone.`)) {
      setMessage(null);
      deleteMutation.mutate(indicator.id);
    }
  }

  return (
    <div>
      <h1>Admin -- Indicators</h1>
      <AdminNav />

      {message && <div className="state-block" style={{ textAlign: "left" }}>{message}</div>}
      {deleteError && <ErrorState error={new Error(deleteError)} />}

      {formState !== "closed" ? (
        <IndicatorForm
          editing={formState === "create" ? undefined : formState}
          onSuccess={handleFormSuccess}
          onCancel={() => setFormState("closed")}
        />
      ) : (
        <button type="button" onClick={() => setFormState("create")}>
          + New indicator
        </button>
      )}

      <label style={{ display: "block", margin: "1.5rem 0 0.75rem", fontSize: "0.9rem" }}>
        Filter by country:{" "}
        <select value={countryFilter} onChange={(e) => setCountryFilter(e.target.value)}>
          <option value="all">All ({indicators.data?.length ?? 0})</option>
          {countries.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </label>

      {rows.length === 0 ? (
        <EmptyState label="No indicators match this filter." />
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                <th style={cellStyle}>Country</th>
                <th style={cellStyle}>Category</th>
                <th style={cellStyle}>Type</th>
                <th style={cellStyle}>Year</th>
                <th style={cellStyle}>Value</th>
                <th style={cellStyle}>Source</th>
                <th style={cellStyle}>Verified</th>
                <th style={cellStyle}></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((ind) => (
                <tr key={ind.id}>
                  <td style={cellStyle}>{countryMap.get(ind.country_id)?.name ?? ind.country_id}</td>
                  <td style={cellStyle}>{ind.category}</td>
                  <td style={cellStyle}>{ind.indicator_type}</td>
                  <td style={cellStyle}>{ind.year}</td>
                  <td style={cellStyle}>
                    {ind.value}
                    {ind.unit ? ` ${ind.unit}` : ""}
                  </td>
                  <td style={cellStyle}>{ind.source ?? "—"}</td>
                  <td style={cellStyle}>{ind.is_verified ? "✓" : "—"}</td>
                  <td style={{ ...cellStyle, whiteSpace: "nowrap" }}>
                    <button type="button" onClick={() => setFormState(ind)} style={{ marginRight: "0.4rem" }}>
                      Edit
                    </button>
                    <button type="button" onClick={() => handleDelete(ind)} disabled={deleteMutation.isPending}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const cellStyle: CSSProperties = {
  border: "1px solid var(--color-border)",
  padding: "0.4rem 0.6rem",
  textAlign: "left",
  fontSize: "0.85rem",
};
