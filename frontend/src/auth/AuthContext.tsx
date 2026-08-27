import { createContext, useContext, useState, useMemo, useCallback } from "react";
import type { ReactNode } from "react";
import { loginUser, registerUser } from "../api/auth";
import type { LoginPayload, RegisterPayload, UserRole } from "../api/types";
import { getStoredToken, setStoredToken, clearStoredToken } from "./tokenStorage";
import { decodeTokenPayload, isTokenExpired } from "./decodeToken";

export interface AuthUser {
  email: string;
  role: UserRole;
}

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// Initial state από το localStorage -- ώστε ένα browser reload να ΜΗΝ
// αποσυνδέει τον χρήστη. Αν το token έχει λήξει, το καθαρίζουμε αμέσως
// αντί να δείχνουμε "συνδεδεμένο" χρήστη με άχρηστο token.
function readInitialUser(): AuthUser | null {
  const token = getStoredToken();
  if (!token) return null;

  const payload = decodeTokenPayload(token);
  if (!payload || isTokenExpired(payload)) {
    clearStoredToken();
    return null;
  }
  return { email: payload.sub, role: payload.role };
}

// Καμία σελίδα σήμερα δεν ΑΠΑΙΤΕΙ authentication -- Actors/Events/
// Dashboard/Synthesis/Compare παραμένουν πλήρως προσβάσιμα χωρίς login,
// γιατί κανένα από τα αντίστοιχα backend endpoints δεν το απαιτεί (βλ.
// core/dependencies.py: μόνο το verify indicators PUT περνάει από
// require_admin, και δεν έχει UI ακόμα). Το context εδώ κρατάει state
// για μελλοντική χρήση -- δεν φράζει τίποτα υπάρχον.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(readInitialUser);

  const login = useCallback(async (payload: LoginPayload) => {
    const token = await loginUser(payload);
    const decoded = decodeTokenPayload(token.access_token);
    if (!decoded) {
      throw new Error("Login succeeded but the returned token could not be read.");
    }
    setStoredToken(token.access_token);
    setUser({ email: decoded.sub, role: decoded.role });
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    // Το backend δεν κάνει auto-login μετά το register (response_model
    // είναι UserRead, όχι Token) -- ο χρήστης κάνει login ξεχωριστά μετά.
    await registerUser(payload);
  }, []);

  const logout = useCallback(() => {
    clearStoredToken();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isAuthenticated: user !== null, login, register, logout }),
    [user, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
