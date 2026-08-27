import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ApiError } from "../api/client";
import { Card } from "../components/ui";
import type { UserRole } from "../api/types";

// Δεν είναι protected route. Το backend δεν κάνει auto-login μετά το
// register (POST /auth/register επιστρέφει UserRead, όχι Token) -- μετά
// από επιτυχία δείχνουμε μήνυμα και link προς /login, όχι redirect.
export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("VIEWER");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRegistered, setIsRegistered] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await register({ email, password, role });
      setIsRegistered(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(typeof err.detail === "string" ? err.detail : err.message);
      } else {
        setError("Registration failed. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isRegistered) {
    return (
      <div style={{ maxWidth: "360px", margin: "0 auto" }}>
        <h1>Registered</h1>
        <Card>
          <p>Account created for {email}. You can now log in.</p>
          <button onClick={() => navigate("/login")}>Go to login</button>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "360px", margin: "0 auto" }}>
      <h1>Register</h1>
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
              minLength={6}
              autoComplete="new-password"
              style={{ padding: "0.5rem", fontFamily: "inherit" }}
            />
          </label>
          <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
            Role
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              style={{ padding: "0.5rem", fontFamily: "inherit" }}
            >
              <option value="VIEWER">Viewer</option>
              <option value="ADMIN">Admin</option>
            </select>
          </label>
          {error && <div className="state-block state-block--error">{error}</div>}
          <button type="submit" disabled={isSubmitting} style={{ alignSelf: "flex-start" }}>
            {isSubmitting ? "Registering…" : "Register"}
          </button>
        </form>
      </Card>
      <p style={{ fontSize: "0.9rem", color: "var(--color-text-muted, #5b6472)" }}>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
