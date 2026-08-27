// Persist του JWT access token σε localStorage. Ξεχωριστό module (όχι μέσα
// στο AuthContext) ώστε το api/client.ts να μπορεί να το διαβάζει χωρίς να
// εισάγει React context -- αλλιώς κάθε plain apiRequest() call θα χρειαζόταν
// να περνάει το token χειροκίνητα.

const TOKEN_STORAGE_KEY = "kosovo_analytics_auth_token";

export function getStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    // localStorage μπορεί να μην είναι διαθέσιμο (π.χ. private mode σε
    // κάποια browsers) -- συνεχίζουμε σαν να μην υπάρχει token
    return null;
  }
}

export function setStoredToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } catch {
    // αν δεν μπορούμε να γράψουμε, ο χρήστης απλά θα χρειαστεί να ξανακάνει
    // login στο επόμενο reload -- όχι κρίσιμο σφάλμα
  }
}

export function clearStoredToken(): void {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch {
    // βλ. πάνω
  }
}
