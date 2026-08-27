// Το POST /auth/login επιστρέφει μόνο το Token schema (access_token,
// token_type) -- ΚΑΝΕΝΑ user info (βλ. backend/app/schemas/user.py). Το
// access_token όμως ΕΙΝΑΙ ένα JWT που ήδη περιέχει email+role στο payload
// (βλ. create_access_token στο core/security.py: data={"sub": user.email,
// "role": user.role.value}). Αντί για ένα δεύτερο round-trip (π.χ. GET
// /users/me που δεν υπάρχει καν σήμερα), αποκωδικοποιούμε το payload
// τοπικά. ΔΕΝ επαληθεύουμε signature εδώ -- αυτό δεν χρειάζεται στο
// frontend, το backend το ελέγχει σε κάθε request (get_current_user).

export interface TokenPayload {
  sub: string; // email
  role: "ADMIN" | "VIEWER";
  exp: number; // unix seconds
}

export function decodeTokenPayload(token: string): TokenPayload | null {
  try {
    const payloadSegment = token.split(".")[1];
    const base64 = payloadSegment.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
        .join("")
    );
    return JSON.parse(json) as TokenPayload;
  } catch {
    return null;
  }
}

export function isTokenExpired(payload: TokenPayload): boolean {
  return payload.exp * 1000 < Date.now();
}
