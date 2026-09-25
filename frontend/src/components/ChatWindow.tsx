"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError, sendChatMessage, sendFeedback } from "../lib/api";
import { loadMessages, saveMessages } from "../lib/storage";
import type { ChatMessage, Role } from "../lib/types";
import MessageBubble from "./MessageBubble";

interface ChatWindowProps {
  token: string;
  role: Role;
  onSignOut: () => void;
}

function newId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export default function ChatWindow({
  token,
  role,
  onSignOut,
}: ChatWindowProps) {
  // Lazy initializer, not a separate load-on-mount effect: a "load" effect
  // and a "save on change" effect race (the save effect's first run sees
  // the pre-load [] closure and can overwrite real stored history with
  // an empty array before the load effect's state update lands — this
  // actually happened, caught via React Strict Mode's dev-mode double
  // effect invocation). Reading synchronously here is safe: ChatWindow
  // only ever mounts client-side, after page.tsx has already confirmed a
  // session exists, never during SSR.
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    loadMessages<ChatMessage>(),
  );
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    saveMessages(messages);
    bottomRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(event: React.FormEvent) {
    event.preventDefault();
    const question = input.trim();
    if (!question || sending) return;

    setInput("");
    setError(null);
    setMessages((prev) => [
      ...prev,
      { id: newId(), role: "user", content: question },
    ]);
    setSending(true);

    try {
      const response = await sendChatMessage(token, question);
      setMessages((prev) => [
        ...prev,
        {
          id: newId(),
          role: "assistant",
          content: response.answer,
          sources: response.sources,
          verified: response.verified,
          feedback: null,
        },
      ]);
    } catch {
      setError("Something went wrong reaching UIS CampusAI. Please try again.");
    } finally {
      setSending(false);
    }
  }

  async function handleFeedback(messageId: string, helpful: boolean) {
    const index = messages.findIndex((m) => m.id === messageId);
    if (index < 1) return;
    const answer = messages[index];
    const question = messages[index - 1];

    setMessages((prev) =>
      prev.map((m) =>
        m.id === messageId ? { ...m, feedback: helpful ? "up" : "down" } : m,
      ),
    );

    try {
      await sendFeedback(token, {
        question: question.content,
        answer: answer.content,
        helpful,
      });
    } catch (err) {
      if (err instanceof ApiError) {
        // best-effort — feedback not landing shouldn't block the chat UI
        console.error(err);
      }
    }
  }

  return (
    <div className="flex h-full w-full max-w-2xl flex-1 flex-col">
      <header className="flex items-center justify-between border-b border-black/[.08] px-4 py-3 dark:border-white/[.145]">
        <div>
          <h1 className="text-sm font-semibold text-black dark:text-zinc-50">
            UIS CampusAI
          </h1>
          <p className="text-xs capitalize text-zinc-500 dark:text-zinc-400">
            Signed in as {role}
          </p>
        </div>
        <button
          type="button"
          onClick={onSignOut}
          className="text-xs text-zinc-500 underline underline-offset-2 hover:text-black dark:text-zinc-400 dark:hover:text-zinc-50"
        >
          Switch role
        </button>
      </header>

      <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-4 py-4">
        {messages.length === 0 && (
          <p className="m-auto max-w-sm text-center text-sm text-zinc-500 dark:text-zinc-400">
            Ask a question about UIS academics, the calendar, the library,
            campus events, or student organizations.
          </p>
        )}
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onFeedback={handleFeedback}
          />
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-zinc-100 px-4 py-3 text-sm text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
              Thinking…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && (
        <p
          className="px-4 pb-2 text-xs text-red-600 dark:text-red-400"
          role="alert"
        >
          {error}
        </p>
      )}

      <form
        onSubmit={handleSend}
        className="flex gap-2 border-t border-black/[.08] p-4 dark:border-white/[.145]"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question…"
          aria-label="Ask a question"
          className="flex-1 rounded-full border border-black/[.08] px-4 py-2 text-sm outline-none focus:border-black/40 dark:border-white/[.145] dark:bg-black dark:text-zinc-50 dark:focus:border-white/40"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="rounded-full bg-black px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-[#383838] disabled:opacity-50 dark:bg-zinc-50 dark:text-black dark:hover:bg-[#ccc]"
        >
          Send
        </button>
      </form>
    </div>
  );
}
