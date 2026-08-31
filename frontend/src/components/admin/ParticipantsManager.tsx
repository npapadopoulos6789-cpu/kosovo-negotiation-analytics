import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateNegotiationEvent } from "../../api/negotiationEvents";
import { useCountryLookup } from "../../hooks/useCountryLookup";
import type { NegotiationEvent, ParticipantRole } from "../../api/types";
import { ApiError } from "../../api/client";
import { Card, Badge } from "../ui";

const ROLES: ParticipantRole[] = ["PARTY", "MEDIATOR", "GUARANTOR", "SUPPORTER"];

// NegotiationEventUpdate.participants αντικαθιστά όλη τη λίστα όταν
// σταλεί (δεν υπάρχει add/remove-single endpoint) -- κάθε add/remove εδώ
// φτιάχνει την πλήρη νέα λίστα client-side και στέλνει ένα PUT με αυτήν.
export function ParticipantsManager({ event }: { event: NegotiationEvent }) {
  const queryClient = useQueryClient();
  const { countryMap, isLoading: countriesLoading } = useCountryLookup();
  const countries = [...countryMap.values()].sort((a, b) => a.name.localeCompare(b.name));

  const [newCountryId, setNewCountryId] = useState<string>("");
  const [newRole, setNewRole] = useState<ParticipantRole>("PARTY");
  const [newSupportsCountryId, setNewSupportsCountryId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (participants: { country_id: number; role: ParticipantRole; supports_country_id?: number | null }[]) =>
      updateNegotiationEvent(event.id, { participants }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["negotiation-events"] });
      setError(null);
    },
    onError: (err) => {
      setError(err instanceof ApiError ? (typeof err.detail === "string" ? err.detail : err.message) : "Update failed.");
    },
  });

  function currentPayload() {
    return event.participants.map((p) => ({
      country_id: p.country_id,
      role: p.role,
      supports_country_id: p.supports_country_id,
    }));
  }

  const alreadyAdded = newCountryId !== "" &&
    event.participants.some((p) => p.country_id === Number(newCountryId) && p.role === newRole);

  function handleAdd() {
    if (newCountryId === "" || alreadyAdded) return;
    setError(null);
    mutation.mutate([
      ...currentPayload(),
      {
        country_id: Number(newCountryId),
        role: newRole,
        supports_country_id: newRole === "SUPPORTER" && newSupportsCountryId !== "" ? Number(newSupportsCountryId) : null,
      },
    ]);
    setNewCountryId("");
    setNewRole("PARTY");
    setNewSupportsCountryId("");
  }

  function handleRemove(participantId: number) {
    setError(null);
    mutation.mutate(currentPayload().filter((_, i) => event.participants[i].id !== participantId));
  }

  if (countriesLoading) return <Card>Loading countries…</Card>;

  return (
    <Card>
      <h3 style={{ marginTop: 0, fontSize: "1rem" }}>Participants</h3>

      {event.participants.length === 0 ? (
        <p style={{ fontSize: "0.9rem", color: "var(--color-text-muted)" }}>No participants yet.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, margin: "0 0 1rem", display: "flex", flexDirection: "column", gap: "0.4rem" }}>
          {event.participants.map((p) => (
            <li key={p.id} style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.9rem" }}>
              <strong>{p.country_name}</strong>
              <Badge tone="neutral">{p.role}</Badge>
              {p.role === "SUPPORTER" && p.supports_country_id != null && (
                <span style={{ color: "var(--color-text-muted)" }}>
                  supports {countryMap.get(p.supports_country_id)?.name ?? `#${p.supports_country_id}`}
                </span>
              )}
              <button type="button" onClick={() => handleRemove(p.id)} disabled={mutation.isPending} style={{ marginLeft: "auto" }}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}

      {error && <div className="state-block state-block--error">{error}</div>}

      <div style={{ display: "flex", gap: "0.5rem", alignItems: "flex-end", flexWrap: "wrap" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.85rem" }}>
          Country
          <select value={newCountryId} onChange={(e) => setNewCountryId(e.target.value)}>
            <option value="">(select)</option>
            {countries.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.85rem" }}>
          Role
          <select value={newRole} onChange={(e) => setNewRole(e.target.value as ParticipantRole)}>
            {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </label>
        {newRole === "SUPPORTER" && (
          <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.85rem" }}>
            Supports (optional)
            <select value={newSupportsCountryId} onChange={(e) => setNewSupportsCountryId(e.target.value)}>
              <option value="">(none)</option>
              {countries.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </label>
        )}
        <button type="button" onClick={handleAdd} disabled={mutation.isPending || newCountryId === "" || alreadyAdded}>
          Add participant
        </button>
      </div>
      {alreadyAdded && (
        <p style={{ fontSize: "0.8rem", margin: "0.35rem 0 0", color: "var(--color-text-muted)" }}>
          Already added with that role.
        </p>
      )}
    </Card>
  );
}
