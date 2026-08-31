import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createCountry, updateCountry } from "../../api/countries";
import type { ActorType, Country, GeopoliticalBloc } from "../../api/types";
import { ApiError } from "../../api/client";
import { Card } from "../ui";

const ACTOR_TYPES: ActorType[] = ["STATE", "INTERNATIONAL_ORG", "MILITARY_ALLIANCE"];
const BLOCS: GeopoliticalBloc[] = ["WEST", "EAST", "EU", "NEUTRAL"];

interface CountryFormProps {
  editing?: Country;
  onSuccess: (message: string) => void;
  onCancel: () => void;
}

export function CountryForm({ editing, onSuccess, onCancel }: CountryFormProps) {
  const queryClient = useQueryClient();

  const [name, setName] = useState(editing?.name ?? "");
  const [actorType, setActorType] = useState<ActorType>(editing?.actor_type ?? "STATE");
  const [bloc, setBloc] = useState<GeopoliticalBloc | "">(editing?.geopolitical_bloc ?? "");
  const [recognizedKosovo, setRecognizedKosovo] = useState<"unknown" | "true" | "false">(
    editing?.recognized_kosovo === true ? "true" : editing?.recognized_kosovo === false ? "false" : "unknown",
  );
  const [countryCode, setCountryCode] = useState(editing?.country_code ?? "");
  const [roleDescription, setRoleDescription] = useState(editing?.role_description ?? "");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => {
      const payload = {
        name,
        actor_type: actorType,
        geopolitical_bloc: bloc === "" ? null : bloc,
        recognized_kosovo: recognizedKosovo === "unknown" ? null : recognizedKosovo === "true",
        country_code: countryCode.trim() === "" ? null : countryCode.trim(),
        role_description: roleDescription.trim() === "" ? null : roleDescription,
      };
      return editing ? updateCountry(editing.id, payload) : createCountry(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["countries"] });
      onSuccess(editing ? `"${name}" updated successfully.` : `"${name}" created successfully.`);
    },
    onError: (err) => {
      setError(err instanceof ApiError ? (typeof err.detail === "string" ? err.detail : err.message) : "Save failed.");
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <Card>
      <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>{editing ? `Edit ${editing.name}` : "New country"}</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxWidth: "420px" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Name
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Actor type
          <select value={actorType} onChange={(e) => setActorType(e.target.value as ActorType)}>
            {ACTOR_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Geopolitical bloc
          <select value={bloc} onChange={(e) => setBloc(e.target.value as GeopoliticalBloc | "")}>
            <option value="">(none)</option>
            {BLOCS.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Recognizes Kosovo?
          <select
            value={recognizedKosovo}
            onChange={(e) => setRecognizedKosovo(e.target.value as "unknown" | "true" | "false")}
          >
            <option value="unknown">Unknown / not applicable</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Country code (ISO, optional)
          <input type="text" value={countryCode} onChange={(e) => setCountryCode(e.target.value)} maxLength={3} />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Role description (optional)
          <textarea
            value={roleDescription}
            onChange={(e) => setRoleDescription(e.target.value)}
            rows={3}
            style={{ fontFamily: "inherit" }}
          />
        </label>

        {error && <div className="state-block state-block--error">{error}</div>}

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button type="submit" disabled={mutation.isPending || !name.trim()}>
            {mutation.isPending ? "Saving…" : editing ? "Save changes" : "Create country"}
          </button>
          <button type="button" onClick={onCancel} disabled={mutation.isPending}>
            Cancel
          </button>
        </div>
      </form>
    </Card>
  );
}
