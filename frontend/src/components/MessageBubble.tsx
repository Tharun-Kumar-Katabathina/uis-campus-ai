import type { ChatMessage } from "../lib/types";

interface MessageBubbleProps {
  message: ChatMessage;
  onFeedback?: (id: string, helpful: boolean) => void;
}

export default function MessageBubble({
  message,
  onFeedback,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? "bg-black text-white dark:bg-zinc-50 dark:text-black"
            : "bg-zinc-100 text-black dark:bg-zinc-900 dark:text-zinc-50"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 border-t border-black/[.08] pt-2 dark:border-white/[.145]">
            <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
              Sources
            </p>
            <ul className="mt-1 flex flex-col gap-1">
              {message.sources.map((source) => (
                <li key={source.url}>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-700 underline underline-offset-2 dark:text-blue-400"
                  >
                    {source.title}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}

        {!isUser && onFeedback && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-xs text-zinc-500 dark:text-zinc-400">
              Was this helpful?
            </span>
            <button
              type="button"
              aria-label="Helpful"
              onClick={() => onFeedback(message.id, true)}
              disabled={message.feedback != null}
              className={`text-base leading-none disabled:opacity-40 ${
                message.feedback === "up"
                  ? "opacity-100"
                  : "opacity-60 hover:opacity-100"
              }`}
            >
              👍
            </button>
            <button
              type="button"
              aria-label="Not helpful"
              onClick={() => onFeedback(message.id, false)}
              disabled={message.feedback != null}
              className={`text-base leading-none disabled:opacity-40 ${
                message.feedback === "down"
                  ? "opacity-100"
                  : "opacity-60 hover:opacity-100"
              }`}
            >
              👎
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
