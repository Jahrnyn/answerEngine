# RUNTIME_OPERATIONS — Answer Engine

---

## 1. Purpose

This document defines how the Answer Engine local development environment is started, verified, and operated.

---

## 2. Development entrypoint

The canonical local development entrypoint is:

- `.\scripts\dev-up.ps1`

This script is responsible for:
- checking required local tools
- preparing backend and frontend dependencies
- checking Ollama availability
- verifying CfHEE availability
- starting backend and frontend processes

Manual frontend entrypoint during development:

- `cd apps/frontend`
- `npm install`
- `npm start`

---

## 3. Local development ports

Default local development ports are:

- Answer Engine frontend: `8760`
- Answer Engine backend: `8761`
- CfHEE runtime: `4210` (expected upstream dependency)

These ports are intentionally non-default to reduce conflicts with other local projects.

---

## 4. CfHEE dependency rule

The Answer Engine depends on a running CfHEE instance.

The startup script must verify:

- `GET /api/v1/health`
- `GET /api/v1/capabilities`

Default expected base URL:

- `http://127.0.0.1:4210`

Current backend timeout default for CfHEE requests:

- `10.0` seconds

Current local note:
- the configured CfHEE base URL may be a workbench/UI host
- the backend and local startup script may resolve the effective CfHEE API base URL from `runtime-config.js` when that host exposes the API separately

If CfHEE is unavailable or does not expose the required capabilities, the Answer Engine development startup must fail.
During normal backend runs, upstream timeout and availability failures should remain explicit in run output rather than being collapsed into empty-evidence behavior.

---

## 5. Minimum required CfHEE capabilities

At minimum, the startup check should require:

- `scoped_retrieval = true`
- `scope_values = true`

Later versions may add stricter requirements depending on integration depth.

---

## 6. Startup behavior

The intended startup order is:

1. check local tools
2. verify CfHEE availability
3. prepare backend environment
4. prepare frontend environment
5. verify Ollama availability
6. start backend
7. start frontend

If step 2 fails, the startup must stop.

---

## 7. Current local development model profile

Current centralized local development defaults:

- `query_analysis` -> rule-based first with optional `qwen2.5:1.5b` fallback intent
- `scope_inference_ranking` -> `qwen2.5:3b`
- `answer_generation` -> `qwen2.5:7b`
- `answer_verification` -> `qwen2.5:3b`

Notes:
- these are development defaults, not permanent product-level model commitments
- routing remains centralized and configuration-driven
- the current local environment has been checked for `qwen2.5:1.5b`, `qwen2.5:3b`, and `qwen2.5:7b`

---

## 8. Frontend development surface

Current frontend slice:

- Angular standalone app under `apps/frontend`
- dark main question/answer surface
- refined main result surface with clearer success, limitation, cannot-answer, and uncertainty-oriented rendering
- optional inspect side-panel with richer run-detail rendering

Current frontend dev behavior:

- the Angular dev server runs on `http://127.0.0.1:8760`
- the frontend proxies `/runs` and `/health` to the backend on `http://127.0.0.1:8761`
- the main surface can submit a question to `POST /runs/execute`
- returned final answer, certainty, verification decision, limitations, request failure state, and top run summary details are rendered on the page
- the inspect side-panel can be opened or closed explicitly
- the inspect panel can render run summary, scope, retrieval, verification, context preview, routing, timings, token visibility, and error details when a run payload is present

Current backend active-stream note:

- `POST /runs/stream` may now emit bounded run events over SSE
- this is a backend transport surface only at present
- it does not imply frontend live preview rendering or unverified final-answer streaming

---

## 9. Developer verification routes

The backend may expose narrow developer-oriented routes for checking local integration surfaces.

Current examples:
- `GET /cfhee/health`
- `GET /cfhee/capabilities`
- `GET /cfhee/scopes/values`
- `GET /cfhee/scopes/tree`
- `POST /cfhee/retrieval/query`

These routes are intended for local verification only.
They do not imply that the full answer pipeline is already integrated with CfHEE.
