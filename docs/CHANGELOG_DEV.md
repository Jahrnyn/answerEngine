# Dev Changelog

## 2026-03-31

- Created the initial backend scaffold under `apps/backend`.
- Added an installable Python package at `apps/backend/src/answer_engine_backend`.
- Added a minimal FastAPI bootstrap in `answer_engine_backend.main`.
- Added an unversioned `GET /health` endpoint returning simple JSON health data.
- Added backend packaging and runtime dependencies for local editable installation.
- Added `docs/PROMPTING_GUIDE.md` because it was referenced by the documentation workflow but missing from the repository.
- Updated project state, current focus, and documentation index references to match the current repository state.

## 2026-04-01

- Refined the documentation set to clarify the V1 direction as run-centric rather than chat-centric.
- Updated `ARCHITECTURE`, `ANSWER_PIPELINE`, and `DOMAIN_MODEL` to make `AnswerRun` the primary runtime unit and to keep conversation support lightweight and optional in V1.
- Split verification in the documentation into evidence verification and response evaluation, and added the internal `AnswerPolicy` runtime concept.
- Updated decision records, project state, and docs index to remove stale references and keep the Answer Engine / CfHEE boundary explicit.
- Refined the V1 runtime profile again to keep hybrid scope inference strong but explicitly bounded, merge verification back into one V1 stage, and make regeneration and scope-failure fallback rules explicit.
- Updated the frontend documentation to keep V1 focused on a main question/answer surface with an optional inspect panel rather than a thread-first layout.
- Clarified that V1 may expose run progress states but does not stream unverified final answer text to the user before post-generation verification completes.
- Introduced stage-specific model routing as a documentation concept and aligned architecture, pipeline, domain model, decisions, and project state around centralized, configuration-driven model selection.
- Implemented Slice 1 backend pipeline skeleton with a `RunExecutor`, explicit stub stage boundaries, a dev-oriented `POST /runs/execute` route, and deterministic `AnswerRun`-like output assembly.
- Implemented Slice 2 CfHEE integration foundation with config-driven base URL settings, a thin external client, and developer-oriented `/cfhee/*` verification routes for health, capabilities, scope helpers, and retrieval wrapper testing.
- Implemented Slice 3 with deterministic V1 Query Analysis and Answer Policy Resolution logic, replacing early placeholders in the pipeline skeleton while keeping later stages stubbed.
- Implemented Slice 3.5 with a central Stage Model Resolver skeleton, config-driven default stage routing, and inspectable stage model routing metadata in the dev run output without adding real model execution.
- Implemented Slice 4 with bounded V1 Scope Inference using deterministic candidate filtering, bounded CfHEE-backed retrieval validation, explicit narrow fallback behavior, and richer `ScopeInferenceResult` trace data.
- Implemented Slice 5 with bounded V1 Retrieval Planning and CfHEE-backed Retrieval Execution, including explicit per-round retrieval results, deterministic aggregation, and explicit `no_retrieval` or `no_evidence` outcomes.
- Re-verified CfHEE-dependent backend behavior against the correct local CfHEE base URL `http://127.0.0.1:4210`, corrected the client to resolve the live API base from `runtime-config.js` when the configured host serves the CfHEE workbench UI, fixed live scope-tree flattening for the current nested `name` shape, and updated runtime docs and startup defaults away from stale `8770` assumptions.
- Implemented Slice 6 with bounded V1 Context Assembly, replacing the placeholder stage with deterministic chunk dedupe, bounded selection, inspectable structured context formatting, approximate token estimation, and explicit minimal empty-context behavior.
- Implemented Slice 7 with practical V1 Answer Generation, replacing the placeholder stage with a simple grounded prompt path, central stage-model routing consumption, local Ollama runtime integration, explicit generation failure surfacing, and real `answer_result` output.
- Implemented Slice 7.5 to lock in the current local development model profile centrally through settings and stage routing defaults: `query_analysis` remains rule-based first with optional `qwen2.5:1.5b` fallback intent, `scope_inference_ranking` and `answer_verification` now default to `qwen2.5:3b`, and `answer_generation` now defaults explicitly to `qwen2.5:7b`.
- Verified local Ollama availability for `qwen2.5:1.5b`, `qwen2.5:3b`, and `qwen2.5:7b`, and pulled the missing `1.5b` and `3b` models into the development environment.
- Implemented Slice 8 with practical V1 Answer Verification, replacing the placeholder stage with bounded combined verification, central verification-model routing consumption, explicit keep/limit/regenerate/cannot-answer decisions, and at-most-one regeneration handling that can replace the candidate answer in the run trace.
- Re-checked verification behavior locally with controlled runs, including explicit regeneration and cannot-answer paths; live end-to-end `/runs/execute` remained intermittently blocked in this round by upstream CfHEE retrieval timeouts before verification could complete.
- Implemented Slice 9 with end-to-end backend stabilization focused on timeout and failure hardening: scope inference and retrieval execution now preserve explicit upstream timeout/unavailable/failure states, the backend returns truthful cannot-answer run output instead of collapsing those paths into no-evidence semantics, and stage-attributed `AnswerRun.errors` now surface important failures explicitly.
- Increased the backend CfHEE timeout default to `10.0` seconds, re-checked the live `bechtle crm` path successfully, and verified controlled upstream-timeout behavior now returns explicit `upstream_timeout` run output and cannot-answer final responses.

## 2026-04-02

- Implemented Slice 10 with the first Angular frontend shell under `apps/frontend`.
- Replaced the Angular starter template with a dark, run-centric main question/answer surface using standalone components.
- Added a thin frontend API service for `POST /runs/execute` and wired the page to render running, answer, certainty, limitations, and request-failure states.
- Added frontend dev-server proxying for `/runs` and `/health` to the backend on `http://127.0.0.1:8761`.
- Verified the frontend build locally, verified the dev server on `http://127.0.0.1:8760`, and re-checked proxied `/runs/execute` calls through the frontend dev server against the live local backend.
- Implemented Slice 11 with an optional inspect panel shell for the Angular frontend.
- Added basic inspect-oriented rendering for run summary, scope, retrieval, verification, context preview, stage routing, timings, and stage-attributed errors.
- Preserved the main question/answer surface as primary while making inspectability a secondary toggleable surface.
- Re-checked the frontend build and verified the inspect-oriented payload path through the frontend dev proxy with a live timeout-path run response.
- Implemented Slice 12 with a refined inspect side-panel experience that now behaves as a clearer secondary drawer rather than just extra detail blocks beside the main surface.
- Added richer run visibility for total run time, primary scope, retrieval scopes, verification outcome, certainty, token visibility, context token estimate, routing, timings, trace id, and stage-attributed errors when those values are present in backend output.
- Kept the main answer surface primary while promoting the inspect view into a more structured secondary diagnostics surface.
- Re-checked the refined frontend build and verified the richer inspect path again through the frontend dev proxy with a live timeout-path run response.
- Implemented Slice 13 with a more intentional main result surface for success, limited, cannot-answer, and uncertainty-heavy outcomes.
- Refined the primary answer card to keep answer text visually dominant while surfacing certainty, verification decision, primary scope, total run time, trace id, and top limitations more clearly.
- Re-checked the frontend build and verified the refined main-result path again through the frontend dev proxy with a live timeout-path run response.
- Implemented Slice 12.5 with a compact right-edge inspect drawer handle, replacing the floating inspect CTA-style trigger and the extra top-level inspect action button.
- Re-checked the frontend build after the drawer-trigger cleanup and kept the existing drawer open/close behavior intact.
- Integrated `docs/ACTIVE_STREAM.md` into the documentation system and aligned architecture, pipeline, and project-state docs around future live run preview as a non-final execution-visibility layer.
- Added a minimal conceptual backend run-event contract in `DOMAIN_MODEL` for future run activity transport, including `RunEvent` and `RunEventType`.
- Updated current focus toward active stream / live run preview groundwork without claiming any SSE, event emission, or frontend live preview implementation.
- Implemented Slice 14 with bounded in-memory backend run event emission, collecting run and stage lifecycle events during execution and attaching them to the final dev run output.
- Added one bounded generation preview snapshot event to the answer-generation path without introducing SSE, transport, or user-visible streaming behavior.
- Re-checked backend execution locally so `/runs/execute` still returns normal final answer output while now also returning `events[]` for dev/debug inspection.
- Implemented Slice 15 with a dedicated SSE transport route for bounded run events while preserving the existing synchronous `/runs/execute` behavior.
- Added backend streaming of `run_started`, stage lifecycle events, bounded generation preview snapshots, and terminal `run_completed` or `run_failed` events over `POST /runs/stream`.
- Re-checked the backend locally so `/health` and `/runs/execute` remain intact and the new SSE route emits ordered live event payloads with terminal completion or failure behavior.
