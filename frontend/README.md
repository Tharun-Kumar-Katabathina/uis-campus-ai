# Frontend

The chat UI (Module 7) — Next.js, TypeScript, Tailwind CSS. See
`docs/PROJECT_CONTRACT.md` for the full module contract.

## What it looks like

```text
+-------------------------------------------------+
| UIS CampusAI                          Switch role|
| Signed in as student                             |
|---------------------------------------------------|
|                                                   |
|                     When does fall registration   |
|                     open?                    [you]|
|                                                   |
| [assistant] According to the available evidence,  |
| fall registration opens on July 6, 2026, for       |
| continuing students and July 20, 2026, for new     |
| and transfer students [2].                         |
|                                                     |
| Sources                                            |
| 2026-2027 Academic Calendar (link)                 |
|                                                     |
| Was this helpful? 👍 👎                             |
|                                                     |
|---------------------------------------------------|
| Ask a question...                          [Send] |
+-------------------------------------------------+
```

No login form: click a role (Student/Faculty/Staff/Admin) to get a demo
token from the backend (`POST /auth/demo-login` — see its docstring;
there's no real user-account system in this project). Then it's a plain
chat: type a question, get an answer with clickable sources and a
verified/unverified state baked into whether an answer or the roadmap
§28 refusal comes back, and thumbs up/down feedback under each answer.

## Architecture

- `src/app/page.tsx` — top-level: restores a session from
  `sessionStorage` if one exists, otherwise shows `RoleSelector`; once
  signed in, renders `ChatWindow`.
- `src/components/RoleSelector.tsx` — the 4 role buttons; calls
  `demoLogin()`.
- `src/components/ChatWindow.tsx` — message list + input; calls
  `sendChatMessage()` per question and `sendFeedback()` per thumbs
  click; persists messages to `sessionStorage` on every change.
- `src/components/MessageBubble.tsx` — renders one message: content,
  sources as links (assistant only), feedback buttons (assistant only,
  disabled once clicked).
- `src/lib/api.ts` — typed fetch wrappers for `/auth/demo-login`,
  `/chat`, `/feedback` (`NEXT_PUBLIC_API_URL`, defaults to
  `http://localhost:8000`).
- `src/lib/storage.ts` — `sessionStorage` helpers, wrapped in try/catch.

## Manual end-to-end verification

This was actually driven in a browser against the real stack, not just
component tests against mocks: Qdrant populated via `ingestion/`'s
pipeline, the real backend (`uvicorn`), and a real local LLM (Ollama +
`llama3.2`, installed just for this check — see
`docs/PROJECT_CONTRACT.md` Module 7's interface decisions for what that
surfaced, including a real conversation-history race condition it caught
and the fix). Ollama isn't a project dependency and isn't installed by
default — `backend/README.md`'s Module 5 section has the manual setup if
you want to reproduce this.

## Development

```bash
npm install
npm run dev            # http://localhost:3000 (needs the backend running too)
npm run test           # Vitest + React Testing Library, mocks lib/api — no backend needed
npm run lint            # eslint
npm run format:check    # prettier check
npm run build            # production build
```
