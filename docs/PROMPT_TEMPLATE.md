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

Update if affected:

- `docs/CURRENT_FOCUS.md`
- `docs/ARCHITECTURE.md`
- `docs/ANSWER_PIPELINE.md`
- `docs/DOMAIN_MODEL.md`
- `docs/DECISIONS.md`
- `docs/API_V1.md` (when introduced or modified)
- `docs/FRONTEND_STYLE_GUIDE.md` (if UI is affected)
- `docs/RUNTIME_OPERATIONS.md` (if runtime behavior changes)
- `docs/PORTABLE_RUNTIME.md` (if runtime model changes)
- `docs/CFHEE_API.md` if the task involves CfHEE integration
- `docs/DOCS_INDEX.md`
- `README.md`

---

## Documentation rules

- reflect ONLY what is implemented or verified
- do NOT speculate
- keep updates concise and factual
- maintain terminology consistency
- do NOT introduce undocumented behavior

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