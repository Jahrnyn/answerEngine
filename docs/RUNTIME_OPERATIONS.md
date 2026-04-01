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

---

## 3. Local development ports

Default local development ports are:

- Answer Engine frontend: `8760`
- Answer Engine backend: `8761`
- CfHEE runtime: `8770` (expected upstream dependency)

These ports are intentionally non-default to reduce conflicts with other local projects.

---

## 4. CfHEE dependency rule

The Answer Engine depends on a running CfHEE instance.

The startup script must verify:

- `GET /api/v1/health`
- `GET /api/v1/capabilities`

Default expected base URL:

- `http://127.0.0.1:8770`

If CfHEE is unavailable or does not expose the required capabilities, the Answer Engine development startup must fail.

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

## 7. Developer verification routes

The backend may expose narrow developer-oriented routes for checking local integration surfaces.

Current examples:
- `GET /cfhee/health`
- `GET /cfhee/capabilities`
- `GET /cfhee/scopes/values`
- `GET /cfhee/scopes/tree`
- `POST /cfhee/retrieval/query`

These routes are intended for local verification only.
They do not imply that the full answer pipeline is already integrated with CfHEE.
