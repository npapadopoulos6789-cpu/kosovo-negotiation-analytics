import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ApiError } from "../api/client";
import { Card } from "../components/ui";

// Δεν είναι protected route -- κανένα υπάρχον endpoint δεν απαιτεί login
// (βλ. σχόλιο στο AuthProvider). Απλή φόρμα, redirect στο dashboard μετά
// από επιτυχές login.
export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login({ email, password });
      navigate("/");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(typeof err.detail === "string" ? err.detail : err.message);
      } else {
        setError("Login failed. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: "360px", margin: "0 auto" }}>
      <h1>Log in</h1>
      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              style={{ padding: "0.5rem", fontFamily: "inherit" }}
            />
          </label>
          <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              style={{ padding: "0.5rem", fontFamily: "inherit" }}
            />
          </label>
          {error && <div className="state-block state-block--error">{error}</div>}
          <button type="submit" disabled={isSubmitting} style={{ alignSelf: "flex-start" }}>
            {isSubmitting ? "Logging in…" : "Log in"}
          </button>
        </form>
      </Card>
      <p style={{ fontSize: "0.9rem", color: "var(--color-text-muted, #5b6472)" }}>
        No account yet? <Link to="/register">Register</Link>
      </p>
    </div>
  );
}
