// roadmap §42: "conversation history can be local/session-based" for the
// initial version — no backend conversation store exists yet. Wrapped in
// try/catch since sessionStorage can throw (private browsing, disabled
// site data, etc.).

const SESSION_KEY = "campusai.session";

export interface StoredSession {
  role: string;
  token: string;
}

export function loadSession(): StoredSession | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as StoredSession) : null;
  } catch {
    return null;
  }
}

export function saveSession(session: StoredSession): void {
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
  } catch {
    // per-viewer convenience only; losing it just means re-selecting a role
  }
}

export function clearSession(): void {
  try {
    sessionStorage.removeItem(SESSION_KEY);
  } catch {
    // ignore
  }
}

const MESSAGES_KEY = "campusai.messages";

export function loadMessages<T>(): T[] {
  try {
    const raw = sessionStorage.getItem(MESSAGES_KEY);
    return raw ? (JSON.parse(raw) as T[]) : [];
  } catch {
    return [];
  }
}

export function saveMessages<T>(messages: T[]): void {
  try {
    sessionStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
  } catch {
    // ignore
  }
}
