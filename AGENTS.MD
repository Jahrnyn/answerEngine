# AGENTS.md

## Project
Answer Engine

A local-first, pipeline-driven answering module built on top of CfHEE.

---

## Mission

Build a reusable answering layer that:

- consumes scoped knowledge from CfHEE
- performs controlled scope inference
- constructs grounded context
- generates and verifies answers
- exposes full execution trace

The system is designed to act as a:

> **High-trust answering execution layer**

---

## Core principles

- Local-first by default
- Pipeline-first, not agent-first
- Retrieval-grounded answers only
- Explicit scope handling
- Full traceability of execution
- Deterministic and inspectable behavior
- Separation of knowledge (CfHEE) and execution (Answer Engine)
- Favor thin vertical slices over broad unfinished scaffolding

---

## What this system is

Answer Engine is a:

> **Pipeline-based Answering Module**

It provides:

- query analysis
- scope inference (hybrid)
- retrieval orchestration
- context construction
- answer generation
- answer verification
- execution trace visibility

---

## What this system is NOT

Do not treat Answer Engine as:

- a generic AI assistant
- an agent framework
- an autonomous system
- a workflow automation engine
- a business logic container

---

## Critical architectural boundary

> CfHEE = knowledge + retrieval  
> Answer Engine = orchestration + reasoning

Rules:

- CfHEE must NOT perform scope inference
- CfHEE must NOT perform orchestration
- Answer Engine must NOT modify CfHEE behavior
- Answer Engine must treat CfHEE as an external system

---

## Pipeline rule (MANDATORY)

All logic must follow the defined pipeline:

1. Query analysis
2. Scope inference
3. Retrieval planning
4. Retrieval execution
5. Context assembly
6. Answer generation
7. Answer verification

Do NOT:

- skip stages
- merge stages implicitly
- introduce hidden logic outside pipeline stages

---

## Traceability rule

Every answer must be explainable.

The system must expose:

- inferred scopes
- retrieval inputs and outputs
- selected context
- model inputs
- verification result

If something is not traceable, it is considered incorrect.

---

## Scope handling

- scope is never implicit
- scope inference is explicit and controlled
- multiple candidate scopes are allowed
- validation must be applied before final selection

Do NOT:

- rely on CfHEE for scope inference
- perform uncontrolled scope expansion

---

## Answering rules

- answers must be grounded in retrieved context
- if evidence is weak → reflect uncertainty
- do NOT hallucinate missing information
- prefer incomplete but correct answers over confident false ones

---

## Verification rule

Answer verification is mandatory.

The system must:

- check grounding
- check scope consistency
- detect missing evidence
- allow regeneration when needed

---

## Tech stack

- Frontend: Angular (standalone components)
- Backend: Python + FastAPI
- LLM runtime: Ollama (local)
- Knowledge layer: CfHEE (external dependency)

---

## Backend structure (target)

Expected modules:

- api
- pipeline
- query_analysis
- scope_inference
- retrieval_orchestrator
- context_builder
- answer_generator
- answer_verifier
- model_provider
- cfhee_client
- trace

---

## Frontend structure

The frontend acts as a:

> **Answer Workbench**

Expected areas:

- Chat interface (main)
- Conversation list
- Sources panel
- Context viewer
- Trace / debug panel

---

## Working style for Codex

When implementing:

1. Read `docs/ARCHITECTURE.md`
2. Read `docs/CURRENT_FOCUS.md`
3. Align with pipeline design
4. Implement the smallest viable change
5. Keep diffs minimal
6. Do not expand scope
7. Update documentation immediately

---

## Documentation-driven development (MANDATORY)

The system is documentation-first.

Workflow:

1. Read docs
2. Implement
3. Update docs

If documentation is outdated:
→ the system is considered broken

---

## Do not do

- Do not introduce agent loops
- Do not introduce hidden orchestration
- Do not bypass pipeline stages
- Do not merge responsibilities across layers
- Do not implement business-specific logic
- Do not assume CfHEE behavior beyond its API contract
- Do not introduce implicit fallback behavior

---

## Final rule

Keep the system:

- explicit
- controlled
- traceable
- grounded