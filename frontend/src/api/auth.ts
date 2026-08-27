// Resource module για το /auth. Paths hardcoded ΑΚΡΙΒΩΣ όπως στο
// backend/app/api/auth.py -- ΧΩΡΙΣ trailing slash και στα δύο.

import { apiRequest } from "./client";
import type { AuthToken, LoginPayload, RegisterPayload, User } from "./types";

export function registerUser(payload: RegisterPayload): Promise<User> {
  return apiRequest<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload: LoginPayload): Promise<AuthToken> {
  return apiRequest<AuthToken>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
