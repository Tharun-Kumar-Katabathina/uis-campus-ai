import type { ChatResponse, Role } from "./types";

// No login/user-account module exists yet (see backend/app/api/auth.py's
// docstring) — NEXT_PUBLIC_API_URL points at the backend for this
// demo-only auth flow.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {}

async function requestJson<T>(path: string, options: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!response.ok) {
    throw new ApiError(
      `${options.method ?? "GET"} ${path} failed: ${response.status}`,
    );
  }
  return response.json() as Promise<T>;
}

export function demoLogin(
  role: Role,
): Promise<{ access_token: string; role: Role }> {
  return requestJson("/auth/demo-login", {
    method: "POST",
    body: JSON.stringify({ role }),
  });
}

export function sendChatMessage(
  token: string,
  message: string,
): Promise<ChatResponse> {
  return requestJson("/chat", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ message }),
  });
}

export function sendFeedback(
  token: string,
  payload: { question: string; answer: string; helpful: boolean },
): Promise<void> {
  return requestJson("/feedback", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}
