# Prompt Template for Codex — Answer Engine

Use this template when asking Codex to implement or modify anything in this repository.

---

## Standard opening (MANDATORY)

Read `AGENTS.md` and review the documentation index first:
- `docs/DOCS_INDEX.md`

Then read all relevant documents under `docs/` based on that index.

Before making changes, ALWAYS align with:

- `docs/ARCHITECTURE.md`
- `docs/ANSWER_PIPELINE.md`
- `docs/DOMAIN_MODEL.md`
- `docs/DECISIONS.md`
- `docs/PROJECT_STATE.md`
- `docs/CURRENT_FOCUS.md`
- `docs/PROMPTING_GUIDE.md`

If the task touches CfHEE integration boundaries, also read:
- `docs/CFHEE_API.md`

If the task relates to recent work, also read:
- `docs/CHANGELOG_DEV.md`

---

## Task statement

Implement the following narrow vertical slice:

[DESCRIBE THE TASK HERE]

---

## Requirements

- keep the implementation small and practical
- do not refactor unrelated parts
- avoid speculative abstractions
- prefer explicit logic over implicit behavior
- keep business logic readable and debuggable
- preserve existing working behavior unless change is required

---

## Architectural constraints (MANDATORY)

- follow the pipeline defined in `docs/ANSWER_PIPELINE.md`
- do NOT introduce hidden logic outside pipeline stages
- do NOT convert the system into an agent-based architecture
- scope inference must remain explicit and hybrid
- retrieval must not become implicit or uncontrolled
- all major decisions must be traceable
- do NOT bypass domain model definitions

---

## Explicit in-scope

- [LIST WHAT IS IN SCOPE]

---

## Explicit out-of-scope

- [LIST WHAT MUST NOT BE DONE]

---

## Implementation guidance

- prefer minimal diffs
- implement thin vertical slices
- keep logic local and understandable
- do not expand system responsibility
- do not implement future features prematurely
- prefer structured data over ad-hoc objects
- ensure compatibility with DOMAIN_MODEL

---

## Deliverables

1. [DELIVERABLE 1]
2. [DELIVERABLE 2]
3. [DELIVERABLE 3]

---

## Verification

Clearly distinguish between:

- implemented in code
- verified by running locally
- not verified due to environment limits

Do NOT:
- overclaim verification
- assume behavior without testing

---

## Documentation update rules (MANDATORY)

After implementation, ALWAYS update:

- `docs/PROJECT_STATE.md`
- `docs/CHANGELOG_DEV.md`

Update other docs ONLY IF STRICTLY REQUIRED by the implemented change.

Default rule:
- do NOT edit documentation files unless the change directly affects their contract or truth content

Update conditionally only when actually affected:

- `docs/CURRENT_FOCUS.md` → only when the current execution target has been completed or intentionally changed
- `docs/ARCHITECTURE.md` → only if architectural intent or system boundaries changed
- `docs/ANSWER_PIPELINE.md` → only if pipeline behavior or stage responsibilities changed
- `docs/DOMAIN_MODEL.md` → only if data structures or contracts changed
- `docs/DECISIONS.md` → only if a new architectural decision was explicitly made
- `docs/API_V1.md` → only if Answer Engine public API contract was introduced or changed
- `docs/CFHEE_API.md` → only if the external dependency contract snapshot must be refreshed
- `docs/FRONTEND_STYLE_GUIDE.md` → only if frontend styling rules changed
- `docs/RUNTIME_OPERATIONS.md` → only if runtime usage or startup/operation behavior changed
- `docs/PORTABLE_RUNTIME.md` → only if runtime packaging or deployment model changed
- `docs/DOCS_INDEX.md` → only if a documentation file was added, removed, renamed, or its role materially changed
- `README.md` → only if setup, usage, or project positioning changed

Special rule for `docs/DOCS_INDEX.md`:
- do NOT rewrite, simplify, or reorganize it opportunistically
- edit it only for exact index maintenance
- preserve existing structure and entries unless a specific documentation change requires an index update

---

## Documentation rules

- reflect ONLY what is implemented or verified
- do NOT speculate
- keep updates concise and factual
- maintain terminology consistency
- do NOT introduce undocumented behavior

## Documentation guardrail

Do NOT rewrite documentation for style, brevity, cleanup, or reorganization unless explicitly asked.

When updating docs:
- make the smallest factual change possible
- preserve structure, headings, and existing intent
- do not delete content unless it is demonstrably obsolete and directly replaced by the implemented change
- do not "simplify" governance documents

---

## Critical workflow rule

This repository is documentation-driven.

The correct workflow is:

1. Read docs
2. Implement small, focused change
3. Update docs immediately

If documentation is outdated, the system is considered broken.

---

## Final note

Do NOT:

- expand scope beyond CURRENT_FOCUS
- introduce hidden orchestration
- bypass the defined pipeline

Keep the system:
- explicit
- traceable
- controlled