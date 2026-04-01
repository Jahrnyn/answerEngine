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
