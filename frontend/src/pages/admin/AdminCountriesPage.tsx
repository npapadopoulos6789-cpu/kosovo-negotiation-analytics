import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCountryLookup } from "../../hooks/useCountryLookup";
import { deleteCountry } from "../../api/countries";
import type { Country } from "../../api/types";
import { ApiError } from "../../api/client";
import { Card, Badge, LoadingState, ErrorState } from "../../components/ui";
import { AdminNav } from "../../components/admin/AdminNav";
import { CountryForm } from "../../components/admin/CountryForm";

type FormState = "closed" | "create" | Country;

export function AdminCountriesPage() {
  const { countryMap, isLoading, error } = useCountryLookup();
  const queryClient = useQueryClient();

  const [formState, setFormState] = useState<FormState>("closed");
  const [message, setMessage] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const deleteMutation = useMutation({
    mutationFn: deleteCountry,
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ["countries"] });
      setDeleteError(null);
      setMessage(`"${countryMap.get(id)?.name ?? `#${id}`}" deleted.`);
    },
    onError: (err) => {
      setDeleteError(err instanceof ApiError ? (typeof err.detail === "string" ? err.detail : err.message) : "Delete failed.");
    },
  });

  if (isLoading) return <LoadingState label="Loading countries…" />;
  if (error) return <ErrorState error={error} />;

  const countries = [...countryMap.values()].sort((a, b) => a.name.localeCompare(b.name));

  function handleFormSuccess(successMessage: string) {
    setFormState("closed");
    setMessage(successMessage);
  }

  function handleDelete(country: Country) {
    if (window.confirm(`Delete "${country.name}"? This cannot be undone.`)) {
      setMessage(null);
      deleteMutation.mutate(country.id);
    }
  }

  return (
    <div>
      <h1>Admin -- Countries</h1>
      <AdminNav />

      {message && <div className="state-block" style={{ textAlign: "left" }}>{message}</div>}
      {deleteError && <ErrorState error={new Error(deleteError)} />}

      {formState !== "closed" ? (
        <CountryForm
          editing={formState === "create" ? undefined : formState}
          onSuccess={handleFormSuccess}
          onCancel={() => setFormState("closed")}
        />
      ) : (
        <button type="button" onClick={() => setFormState("create")}>
          + New country
        </button>
      )}

      <div style={{ display: "grid", gap: "0.5rem", marginTop: "1.5rem" }}>
        {countries.map((country) => (
          <Card key={country.id}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem", flexWrap: "wrap" }}>
                <strong>{country.name}</strong>
                <Badge>{country.actor_type}</Badge>
                {country.geopolitical_bloc && <Badge tone="neutral">{country.geopolitical_bloc}</Badge>}
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button type="button" onClick={() => setFormState(country)}>
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(country)}
                  disabled={deleteMutation.isPending}
                >
                  Delete
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
