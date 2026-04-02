# Docs Index - Answer Engine

This file explains the role of each documentation file in the Answer Engine repository.

The Answer Engine is a structured answering runtime built on top of CfHEE.
This documentation set acts as the **external project memory** and must always reflect the current state of the system.

---

## Core architecture docs

### `docs/ARCHITECTURE.md`
High-level architecture of the Answer Engine.

Describes:
- system boundaries (Answer Engine vs CfHEE)
- runtime pipeline structure
- backend and frontend architecture
- V1 runtime direction

This is the primary reference for how the system is supposed to work.

---

### `docs/DECISIONS.md`
List of architectural and design decisions that must not be casually reinterpreted.

Use this to:
- prevent drift in system behavior
- enforce agreed patterns (e.g. pipeline over agents, hybrid scope inference)
- keep Codex aligned with established constraints

---

### `docs/ANSWER_PIPELINE.md`
Defines the full answering pipeline.

Includes:
- query analysis
- answer policy resolution
- scope inference (hybrid)
- retrieval planning
- multi-stage retrieval
- context assembly
- answer generation
- answer verification

This is the most critical execution document.
Any change to runtime behavior must be reflected here.

---

### `docs/DOMAIN_MODEL.md`
Defines all core data structures used by the Answer Engine.

Includes:
- answer run
- answer policy
- optional chat session / message support
- verification result
- context pack
- scope references
- retrieval results

Use this when:
- modifying persistence
- working with pipeline data
- designing API responses

---

## Live project state docs

### `docs/PROJECT_STATE.md`
Current verified implementation state.

Use this first to understand:
- what already exists
- what is implemented vs planned

This is the most important "truth" document.

---

### `docs/CURRENT_FOCUS.md`
Current execution anchor

- Not a list.
- Not a roadmap.
- Not a backlog.

But rather:
"What is the ONE thing we're working on right now?"

---

### `docs/CHANGELOG_DEV.md`
Chronological development log.

Tracks:
- what was implemented
- what changed
- observed issues
- important insights

---

## Runtime docs

### `docs/PORTABLE_RUNTIME.md`
Defines how the Answer Engine runs locally.

Includes:
- runtime composition
- dependency on CfHEE
- model provider setup (Ollama, etc.)
- minimal runnable environment

---

### `docs/RUNTIME_OPERATIONS.md`
Operational guide.

Includes:
- start/stop
- logs
- debugging
- development workflow

---

### `docs/OPERATIONS_SURFACE.md`
Defines the intended operational/debug surface.

Includes:
- trace inspection
- pipeline visibility
- developer/debug UI concepts

---

### `docs/CFHEE_API.md`
External dependency contract for CfHEE.

Use this when:
- implementing CfHEE integration
- working on retrieval logic
- handling scope and capabilities

---

## Prompting docs

### `docs/PROMPTING_GUIDE.md`
Rules for working with Codex in this repository.

Use this before writing prompts.

---

### `docs/PROMPT_TEMPLATE.md`
Reusable prompt template for Codex.

Ensures:
- consistency
- correct context loading
- structured outputs

---

## Frontend docs

### `docs/FRONTEND_STYLE_GUIDE.md`
Frontend UI consistency rules.

Includes:
- layout structure
- main question/answer surface
- optional inspect panel
- styling constraints

---

### `docs/ACTIVE_STREAM.md`

Defines the live run preview / active stream model for the Answer Engine.

Use this when working on:
- backend-to-frontend run event streaming
- live pipeline activity visibility
- preview output vs final verified answer semantics
- generation preview text streaming
- SSE or equivalent real-time transport design

This document defines how transient preview output is exposed during execution without breaking the verified-final-answer contract.

---

## Meta docs

### `docs/DOCS_INDEX.md`
Index of the documentation system.

Use this to locate the correct source of truth before making changes.

---

## Suggested reading order for AI assistants

For most implementation tasks:

1. `AGENTS.md`
2. `docs/DOCS_INDEX.md`
3. `docs/ARCHITECTURE.md`
4. `docs/ANSWER_PIPELINE.md`
5. `docs/DOMAIN_MODEL.md`
6. `docs/DECISIONS.md`
7. `docs/PROJECT_STATE.md`
8. `docs/CURRENT_FOCUS.md`
9. `docs/PORTABLE_RUNTIME.md`
10. `docs/RUNTIME_OPERATIONS.md`
11. `docs/OPERATIONS_SURFACE.md`
12. `docs/PROMPTING_GUIDE.md`
13. `docs/CHANGELOG_DEV.md`
14. `docs/ACTIVE_STREAM.md` when working on live run preview, run events, or real-time transport

---

## Human usage note

If resuming work:

Start with:
- `docs/PROJECT_STATE.md`
- `docs/CURRENT_FOCUS.md`
- `docs/CHANGELOG_DEV.md`

Then:
- `docs/ARCHITECTURE.md`
- `docs/ANSWER_PIPELINE.md`

---

## Authority rules

When documents disagree:

1. `docs/PROJECT_STATE.md` -> current reality
2. `docs/CURRENT_FOCUS.md` -> current execution target
3. `docs/DECISIONS.md` -> fixed decisions
4. `docs/ANSWER_PIPELINE.md` -> runtime behavior
5. `docs/ARCHITECTURE.md` -> long-term structure
6. `docs/CHANGELOG_DEV.md` -> historical context

---

## Important rule

This documentation system is the **external project memory**.

Every iteration MUST:
- read relevant docs before implementation
- update docs immediately after implementation

If documentation is outdated, the system is considered broken.
