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
