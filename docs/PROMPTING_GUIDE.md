# PROMPTING_GUIDE - Answer Engine

---

## Purpose

This document defines the minimum prompting rules for working in the Answer Engine repository.

It exists to keep implementation aligned with:
- the documented architecture
- the explicit pipeline
- the current verified project state

---

## Required context before implementation

Read:
- `AGENTS.md`
- `docs/DOCS_INDEX.md`
- `docs/ARCHITECTURE.md`
- `docs/ANSWER_PIPELINE.md`
- `docs/DOMAIN_MODEL.md`
- `docs/DECISIONS.md`
- `docs/PROJECT_STATE.md`
- `docs/CURRENT_FOCUS.md`

If the task touches recent work, also read:
- `docs/CHANGELOG_DEV.md`

---

## Prompting rules

- Keep the system pipeline-first, not agent-first.
- Do not introduce hidden orchestration outside explicit pipeline stages.
- Keep scope inference explicit and hybrid when that work is implemented.
- Keep retrieval grounded in CfHEE and do not move CfHEE responsibilities into the Answer Engine.
- Prefer small, vertical, verifiable changes over broad scaffolding.
- Update documentation immediately after implementation.

---

## Documentation rule

Documentation must reflect current reality.

If code changes but documentation does not, the repository state is considered incorrect.
