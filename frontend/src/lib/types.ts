export type Role = "student" | "faculty" | "staff" | "admin";

export interface Source {
  title: string;
  url: string;
  relevance: number;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  verified: boolean;
  intent: string;
}

export type Feedback = "up" | "down" | null;

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  verified?: boolean;
  feedback?: Feedback;
}
