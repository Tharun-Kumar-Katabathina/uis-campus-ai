# CLAUDE.md — UIS CampusAI

## Session start checklist
Before anything else, check whether a memory note about in-progress work
exists for this project (e.g. `deployment_in_progress.md`). If one does,
surface it proactively in your very first reply this session — don't wait
to be asked "where did we leave off". State what's pending and what you
need from me to continue. Once that pending item is resolved (e.g.
deployment finishes or the plan changes), delete/update the memory note so
this stops firing.

## Context
Read `docs/PROJECT_CONTRACT.md` in full before doing anything else this
session. It's the shared source of truth for architecture, stack, and module
breakdown — don't deviate from it without flagging the conflict to me first.

## Your role
You are acting as the **Main Orchestrator Agent** described in
`docs/PROJECT_CONTRACT.md` §3. In practice that means: you also *are* the
Working Agent for whichever module is active — there's no separate persona
to hand off to within one session. The one role that IS a separate, real
entity is the **Testing Agent**: `.claude/agents/qa-tester.md`. Use it, don't
just simulate it in your own voice.

## Per-module loop
For each module, in the order listed in `docs/PROJECT_CONTRACT.md` §11:

1. Confirm the module's acceptance criteria are actually defined. If they're
   missing or vague (as Module 0's currently are), stop and ask me to firm
   them up before writing code.
2. Implement the module: code, unit tests, integration tests where
   applicable, and docs (README / API docs / env vars) updated as you go,
   not after.
3. Invoke the `qa-tester` subagent to independently verify the module
   against its acceptance criteria. It inspects the actual code and runs the
   tests itself — it does not take your summary on faith, and neither should
   you skip calling it.
4. If `qa-tester` returns FAIL: fix the specific issues it found, then
   re-invoke it. Repeat until PASS. Never mark a module complete on a FAIL.
5. **Stop.** Report to me: what was implemented, files changed, the
   qa-tester verdict with evidence, known limitations, and how the
   acceptance criteria were met. Wait for my explicit go-ahead before
   starting the next module.

## Hard rules
- Don't redesign the architecture, swap technologies, or touch a module
  that isn't the one currently active, without asking first.
- Don't claim a module is done without a PASS from `qa-tester`.
- Keep `docs/PROJECT_CONTRACT.md` updated if a module's actual interface
  ends up differing from what was originally specified — it's the contract
  other modules (and other sessions) will build against.

## Tech stack
See `docs/PROJECT_CONTRACT.md` §10 for the full contract. Summary:
- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, Pydantic
- Data: PostgreSQL, Qdrant, Redis
- Dev: Docker, GitHub Actions

## On running modules in parallel
`docs/PROJECT_CONTRACT.md` §9 wants independent modules (e.g. Frontend /
Backend / Ingestion) built in parallel by separate agents. The real Claude
Code feature for that is **Agent Teams** — experimental, off by default
(`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). It's a lead session plus
teammates sharing a task list and messaging each other directly, not the
full orchestrator → module → working → test tree in the design doc, and it
has known limitations around session resumption and shutdown. Don't reach
for it by default — only when I explicitly ask for a module or set of
modules to be parallelized, and only once their interfaces are frozen in
the contract.
