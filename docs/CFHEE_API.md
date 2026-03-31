# CFHEE_API — External Dependency Contract

---

## 1. Purpose

This document describes the CfHEE API as an **external dependency contract** for the Answer Engine.

It exists to:

- define how Answer Engine interacts with CfHEE
- provide a stable reference for Codex
- prevent API misuse or hallucinated integrations

This document is a **snapshot of the CfHEE API**, not its source of truth.

---

## 2. Ownership & Boundary

- CfHEE owns this API
- Answer Engine consumes it
- this document must NOT redefine CfHEE behavior

Key boundary:

> CfHEE = scoped execution engine  
> Answer Engine = orchestration + reasoning layer

CfHEE:
- does NOT infer scope
- does NOT orchestrate workflows

Answer Engine:
- MUST provide scope
- MUST handle orchestration

---

## 3. Integration Role

Answer Engine uses CfHEE for:

- scoped retrieval
- scope hierarchy inspection
- context building
- capability validation

Answer Engine does NOT use CfHEE for:

- orchestration
- reasoning
- answer generation (core flow)

---

## 4. Core API Principles (Critical)

### 4.1 Scope is mandatory

All retrieval operations require explicit scope.

CfHEE:
- does NOT perform scope inference
- does NOT widen scope implicitly

This is a strict rule.

---

### 4.2 Hard scope model

Scope fields:

- workspace
- domain
- project (optional)
- client (optional)
- module (optional)

Hierarchy rules:

- client requires project
- module requires client

---

### 4.3 No implicit cross-scope behavior

- no fallback to broader scope
- no cross-domain blending
- no automatic scope expansion

---

### 4.4 API is deterministic

Given:
- same query
- same scope

Result must be stable.

---

## 5. System Endpoints

### GET /api/v1/health

Used to verify:

- service availability
- API version
- capabilities

Example response:

{
  "status": "ok",
  "service": "cfhee",
  "api_version": "v1",
  "capabilities": {
    "scoped_retrieval": true,
    "scope_values": true,
    "grounded_answer": true
  }
}

---

### GET /api/v1/capabilities

Used to:

- validate feature support
- confirm integration compatibility

---

## 6. Required Capabilities (Answer Engine V1)

The Answer Engine requires:

- scoped_retrieval = true
- scope_values = true

If missing:
→ Answer Engine must NOT start

---

## 7. Scope Helpers

### GET /api/v1/scopes/values

Returns stored scope values.

Used for:
- autocomplete
- reuse
- conservative scope construction

---

### GET /api/v1/scopes/tree

Returns full scope hierarchy.

Used for:
- scope inference
- candidate scope generation

Important:

- this is a visibility tool
- NOT a scope inference engine

---

## 8. Retrieval

### POST /api/v1/retrieval/query

Primary retrieval endpoint.

---

### Request

{
  "query": "string",
  "scope": { ScopeRef },
  "top_k": 5,
  "include_chunks": true
}

---

### Response

{
  "status": "ok",
  "active_scope": { ScopeRef },
  "results": [
    {
      "document_id": number,
      "chunk_id": number,
      "similarity_score": float,
      "text": "string"
    }
  ],
  "result_count": number
}

---

### Retrieval rules

- always scoped
- no implicit widening
- no scope inference
- no cross-scope blending

---

## 9. Context Build

### POST /api/v1/context/build

Used to:

- construct structured context
- prepare LLM-ready input

Does NOT:

- generate answers
- infer scope

---

## 10. Shared Model

### ScopeRef

{
  "workspace": "string",
  "domain": "string",
  "project": "string|null",
  "client": "string|null",
  "module": "string|null"
}

---

## 11. Integration Rules

Answer Engine must:

- always provide explicit scope
- never rely on CfHEE for orchestration
- never assume undocumented endpoints
- never extend CfHEE behavior implicitly

---

## 12. Important Notes

- CfHEE is strict by design
- CfHEE is NOT a discovery system
- CfHEE is NOT an agent system

This separation is a core architectural rule.

---

## 13. Summary

CfHEE provides:

- scoped retrieval
- scope structure
- context preparation

Answer Engine provides:

- scope inference
- orchestration
- reasoning
- answer validation

This boundary must remain intact.