# PROJECT_STATE — Answer Engine

---

## 1. Current Status

The Answer Engine project is in **V0 early implementation state**.

A minimal backend runtime foundation and initial frontend shell now exist.

The system currently consists of:
- architectural design
- pipeline specification
- domain model definition
- decision records
- documentation framework
- minimal backend application scaffold

The documented V1 direction is now:
- run-centric, not chat-centric
- centered on `AnswerRun` as the primary runtime unit
- focused on one question -> one grounded answer
- keeps strong hybrid scope inference as a core capability
- keeps execution bounded for practical local runs
- not focused on long continuous conversation handling

---

## 2. Implemented Components

### 2.1 Backend
Status: PARTIALLY IMPLEMENTED

- FastAPI application scaffold exists under `apps/backend`
- Unversioned `GET /health` endpoint exists
- Dev-oriented `POST /runs/execute` route exists for exercising the pipeline skeleton
- Dev-oriented CfHEE verification routes exist under `/cfhee/*`
- Local editable install is defined for the backend package
- Run-centric pipeline execution skeleton exists
- Practical deterministic V1 logic exists for Query Analysis and Answer Policy Resolution
- Practical bounded V1 scope inference exists with deterministic filtering and CfHEE-backed validation
- Practical bounded V1 retrieval planning and CfHEE-backed retrieval execution exist
- Practical bounded V1 context assembly exists with deterministic chunk selection and explicit minimal empty-context handling
- Practical V1 answer generation exists with a simple grounded prompt path and local Ollama runtime integration
- Practical V1 answer verification exists with combined bounded evaluation and at-most-one regeneration handling
- Practical V1 failure hardening exists for scope inference, retrieval execution, and final cannot-answer behavior under upstream timeout/failure conditions
- Explicit stub stage boundaries remain in the final response mapping layer only
- Thin CfHEE client foundation exists
- Central stage model resolver skeleton exists

---

### 2.2 Frontend
Status: PARTIALLY IMPLEMENTED

- Angular project exists under `apps/frontend`
- Dark-theme baseline exists for V1
- Main question/answer surface exists
- Minimal frontend-to-backend call path exists for `/runs/execute`
- Refined main result surface exists with clearer keep / limit / cannot-answer / uncertainty-oriented rendering
- Main result summary visibility now includes certainty, verification decision, primary scope, run time, trace id, and top limitations when present
- Optional inspect side-panel exists as a real secondary drawer-style surface
- Inspect drawer now uses a compact right-edge handle instead of a floating CTA-style trigger
- Richer trace-oriented rendering exists for scope, retrieval, verification, context preview, stage routing, timings, token visibility, and errors
- No advanced trace/debug explorer exists yet

---

### 2.3 Model Integration
Status: PARTIALLY IMPLEMENTED

- Local Ollama-backed answer generation exists
- Local Ollama-backed verification assistance exists
- No broad model provider abstraction
- Stage-specific model routing skeleton exists with config-driven defaults and inspectable run output
- Central stage routing is consumed for answer generation
- Central stage routing is consumed for answer verification
- Current local development defaults are explicitly aligned to:
- `query_analysis` -> rule-based first with optional `qwen2.5:1.5b` fallback intent
- `scope_inference_ranking` -> `qwen2.5:3b`
- `answer_generation` -> `qwen2.5:7b`
- `answer_verification` -> `qwen2.5:3b`
- No user-visible streaming logic

---

### 2.4 Storage
Status: NOT IMPLEMENTED

- No AnswerRun persistence
- No raw interaction persistence
- No optional conversation/session persistence

---

### 2.5 CfHEE Integration
Status: PARTIALLY IMPLEMENTED

- Thin API client exists
- Config-driven CfHEE base URL handling exists
- Health and capabilities access exists
- Scope helper access exists
- Retrieval wrapper skeleton exists
- Dev-oriented backend verification routes exist
- Pipeline integration exists for scope inference, retrieval planning, and retrieval execution
- Current local CfHEE verification has been re-checked against `http://127.0.0.1:4210`
- Current CfHEE timeout default is `10.0` seconds for backend requests
- No knowledge promotion behavior

---

## 3. Defined but Not Implemented

The following are fully specified in documentation but not yet implemented:

### 3.1 Pipeline
Defined in:
- docs/ANSWER_PIPELINE.md

Includes:
- Query Analysis
- Answer Policy Resolution
- Scope Inference (Hybrid)
- Retrieval Planning
- Multi-stage Retrieval
- Context Assembly
- Answer Generation
- Answer Verification

Current code state:
- Query Analysis and Answer Policy Resolution use deterministic V1 rule-based behavior
- Scope Inference uses bounded deterministic candidate filtering and CfHEE-backed retrieval validation
- Retrieval Planning uses bounded validated-scope planning
- Retrieval Execution uses CfHEE-backed execution with explicit per-round and aggregated results
- Context Assembly uses deterministic dedupe, bounded selection, inspectable structured context formatting, and approximate token estimation
- CfHEE client can resolve the effective API base URL from the configured local CfHEE host when that host serves the workbench UI
- Answer Generation uses a simple grounded prompt path with the local model runtime and explicit failure surfacing
- Answer Verification uses combined bounded rule checks, model-assisted evaluation when available, and at-most-one explicit regeneration
- retrieval and final run output now preserve explicit upstream timeout/unavailable/failure distinctions instead of collapsing them into no-evidence behavior
- final response mapping remains structurally simple

---

### 3.2 Domain Model
Defined in:
- docs/DOMAIN_MODEL.md

Includes:
- AnswerRun
- AnswerPolicy
- StageModelConfig (conceptual)
- VerificationResult
- ChatSession (optional)
- ChatMessage (optional)
- Retrieval structures
- ContextPack

Current code state:
- `AnswerRun`-like execution payload assembled by the backend skeleton
- stage model routing metadata may be attached to run output for inspectability
- no persistence

---

### 3.3 Architecture
Defined in:
- docs/ARCHITECTURE.md

Includes:
- system layers
- backend services
- frontend structure
- execution model

Current code state:
- explicit pipeline skeleton
- explicit external CfHEE client layer

---

### 3.4 Decisions
Defined in:
- docs/DECISIONS.md

Includes:
- pipeline-first architecture
- hybrid scope inference
- grounded answering
- traceability requirements

---

## 4. Known Constraints

### 4.1 Local-first requirement
The system must be able to run locally.

---

### 4.2 CfHEE dependency
The Answer Engine depends on:
- CfHEE API
- scoped retrieval
- scope hierarchy

---

### 4.3 No agent-based orchestration
The system must follow a structured pipeline.

---

### 4.4 Full traceability required
All pipeline steps must be inspectable.

---

## 5. Known Unknowns

The following are not yet resolved:

- exact prompt structure
- token budgeting strategy
- optimal chunk selection strategy
- bounded scope inference thresholds
- regeneration conditions in verification stage
- practical latency budget targets
- retrieval orchestration implementation
- persistence strategy for AnswerRun
- rules for structured knowledge promotion into CfHEE

---

## 6. Initial Development State

The project is ready for:

- backend scaffold extension
- pipeline skeleton implementation
- first integration with CfHEE (read-only)

No production-ready behavior exists yet.

---

## 7. What DOES NOT exist yet (Important)

- no answering API endpoints
- no production-ready answering API endpoints
- no fully verified live end-to-end answer pipeline yet
- implemented chat/session capability

The following DO exist in minimal structural form:
- `/health`
- dev-only pipeline execution route
- dev-only CfHEE verification routes
- stub `AnswerRun` execution flow
- practical deterministic query analysis
- practical deterministic answer policy resolution
- thin CfHEE client foundation
- stage model resolver skeleton with deterministic routing defaults
- bounded scope inference using CfHEE scope visibility and validation probes
- bounded retrieval planning and CfHEE-backed retrieval execution
- bounded context assembly with inspectable structured context output
- practical V1 answer generation with central stage routing and local Ollama runtime integration
- practical V1 answer verification with bounded combined evaluation and explicit regeneration trace visibility
- practical V1 stage-attributed failure surfacing through `AnswerRun.errors`
- Angular app shell with a dark main question/answer surface and thin `/runs/execute` integration
- optional inspect drawer with richer run-detail rendering

The following have been verified against the current live local CfHEE setup:
- backend settings use `http://127.0.0.1:4210` as the configured CfHEE base URL
- the live `4210` host currently serves the CfHEE workbench UI and exposes `runtime-config.js`
- the backend now resolves the effective live API base URL from that runtime config for CfHEE-dependent requests
- live health, capabilities, scope values, scope tree, developer verification routes, and scoped retrieval calls have been re-checked
- live pipeline execution has been re-checked successfully for at least one real query path (`bechtle crm`)
- live context assembly has been re-checked successfully for at least one real query path (`bechtle crm`)
- live answer generation has been re-checked successfully for at least one real query path (`bechtle crm`)
- the local Ollama runtime has been re-checked and currently includes `qwen2.5:1.5b`, `qwen2.5:3b`, and `qwen2.5:7b`
- centralized stage routing has been re-checked and currently resolves `answer_generation` to `qwen2.5:7b`
- live end-to-end `/runs/execute` remained intermittently blocked in this round by upstream CfHEE retrieval timeouts before verification could complete
- controlled local verification runs now produce real non-placeholder `verification_result` output, including explicit keep, regenerate, and cannot-answer style outcomes
- live end-to-end `/runs/execute` has now been re-checked successfully again for at least one real query path (`bechtle crm`) after the CfHEE timeout hardening round
- controlled timeout-path runs now return explicit `upstream_timeout` status and truthful cannot-answer output instead of surfacing as empty-evidence success
- the frontend now builds successfully under `apps/frontend`
- the frontend dev server has been re-checked on `http://127.0.0.1:8760`
- the frontend dev proxy now reaches the backend `/runs/execute` route on `http://127.0.0.1:8761`
- the frontend inspect panel shell has been re-checked against a live timeout-path run payload and now renders practical trace-adjacent data sections from the backend run output
- the refined inspect side-panel has been re-checked against a live timeout-path run payload and now surfaces run time, scope status, retrieval status, verification decision, token visibility, timings, routing, and errors more prominently
- the refined main result surface has been re-checked against a live timeout-path run payload and now surfaces cannot-answer state, certainty, verification decision, trace id, run time, primary scope, and limitations more clearly without requiring the inspect drawer
- the inspect drawer trigger has been cleaned up to a compact right-edge handle and the floating inspect CTA is no longer part of the current frontend shell

Any assumption that these exist is incorrect.

---

## 8. Development Readiness

The project is considered:

- Architecturally defined: YES
- Ready for implementation: YES
- Ready for backend foundation testing: YES
- Ready for production: NO

---

## 9. Next Step Reference

See:
- docs/CURRENT_FOCUS.md

This document defines the active implementation target.

---

## 10. Summary

The Answer Engine is currently:

- fully designed
- specified
- minimally implemented at the backend foundation level

All future work must:
- follow the defined architecture
- adhere to the pipeline specification
- respect the decision records
- update this document after every iteration
