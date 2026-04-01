# DOMAIN_MODEL - Answer Engine

---

## 1. Purpose

This document defines the core data structures used across the Answer Engine.

It is the authoritative reference for:
- pipeline data flow
- backend internal models
- API response structures
- trace representation

All pipeline stages MUST use these structures or compatible extensions.

---

## 2. Design Principles

### 2.1 Explicit Structures
All data must be structured and typed.
No implicit or loosely shaped objects are allowed.

### 2.2 Trace Compatibility
Every structure must be traceable and serializable.

### 2.3 Pipeline Alignment
Each pipeline stage produces and consumes defined models.

### 2.4 Separation of Concerns
Different data types must not be merged:
- run data
- optional conversation data
- retrieval data
- context data
- model output

---

## 3. Core Entities

---

### 3.1 AnswerRun

Represents the primary runtime unit in V1.

AnswerRun:
- id: string
- query: string
- created_at: datetime
- answer_policy: AnswerPolicy

- query_analysis: QueryAnalysisResult
- scope_inference: ScopeInferenceResult
- retrieval_plan: RetrievalPlan
- retrieval_result: RetrievalResult
- context_pack: ContextPack
- answer_result: AnswerResult
- verification_result: VerificationResult

- conversation_ref: ConversationRef (optional)
- timings: TimingInfo
- errors: list (optional)

Notes:
- `AnswerRun` remains the primary V1 execution entity
- optional conversation support may link to a run but is not the primary reasoning substrate

---

### 3.2 ChatSession

Optional lightweight grouping for multiple runs or interactions.

ChatSession:
- id: string
- title: string
- created_at: datetime
- updated_at: datetime
- metadata: dict (optional)

---

### 3.3 ChatMessage

Optional raw interaction record stored by the Answer Engine.

ChatMessage:
- id: string
- session_id: string
- role: "user" | "assistant"
- content: string
- created_at: datetime
- metadata: dict (optional)

---

## 4. Pipeline Stage Models

---

### 4.1 QueryAnalysisResult

QueryAnalysisResult:
- normalized_query: string
- intent_type: string
- requires_retrieval: bool
- query_variants: list[string] (optional)

Notes:
- `conversation_context` is optional support to this stage
- V1 must not depend on ongoing conversation state as a primary reasoning dependency

---

### 4.2 ScopeInferenceResult

ScopeInferenceResult:
- primary_scope: ScopeReference
- secondary_scopes: list[ScopeReference] (optional)
- confidence_scores: dict[scope_id -> float]
- validation_scores: dict[scope_id -> float]
- fallback_applied: bool

---

### 4.3 ScopeReference

Represents a CfHEE scope.

ScopeReference:
- workspace: string
- domain: string
- project: string (optional)
- client: string (optional)
- module: string (optional)

---

### 4.4 AnswerPolicy

Internal backend/runtime control object resolved for a run.

AnswerPolicy:
- retrieval_required: bool
- max_retrieval_rounds: int
- default_top_k: int
- allow_multi_scope: bool
- allow_regeneration: bool
- verification_profile: string
- response_style: string

Notes:
- internal to the backend/runtime
- not a user-facing UI selection

---

### 4.5 ConversationRef

Links an `AnswerRun` to optional conversation persistence structures.

ConversationRef:
- session_id: string (optional)
- user_message_id: string (optional)
- assistant_message_id: string (optional)

---

### 4.6 RetrievalPlan

RetrievalPlan:
- rounds: list[RetrievalRound]
- fallback_rules: dict (optional)

---

### 4.7 RetrievalRound

RetrievalRound:
- scope: ScopeReference
- top_k: int
- strategy_type: string

---

### 4.8 RetrievalResult

RetrievalResult:
- results_by_round: list[RetrievalRoundResult]
- aggregated_results: list[RetrievedChunk]

---

### 4.9 RetrievalRoundResult

RetrievalRoundResult:
- scope: ScopeReference
- chunks: list[RetrievedChunk]

---

### 4.10 RetrievedChunk

Represents a unit returned from CfHEE.

RetrievedChunk:
- document_id: string
- chunk_id: string
- content: string
- score: float
- metadata: dict

---

### 4.11 ContextPack

ContextPack:
- selected_chunks: list[RetrievedChunk]
- source_mapping: list[SourceReference]
- structured_context: string
- token_estimate: int

---

### 4.12 SourceReference

SourceReference:
- document_id: string
- chunk_id: string
- position: int

---

### 4.13 AnswerResult

AnswerResult:
- answer_text: string
- token_usage: TokenUsage
- model_metadata: dict

---

### 4.14 TokenUsage

TokenUsage:
- prompt_tokens: int
- completion_tokens: int
- total_tokens: int

---

### 4.15 VerificationResult

Practical combined V1 verification result.

VerificationResult:
- grounded: bool
- scope_consistency_ok: bool
- coverage_ok: bool
- adequacy_ok: bool
- uncertainty_flags: list[string]
- limitations: list[string]
- decision: "keep" | "limit" | "regenerate" | "cannot_answer"
- requires_regeneration: bool

Notes:
- combines evidence and response checks into one V1 structure
- supports a bounded final decision for local execution

---

### 4.16 TimingInfo

TimingInfo:
- total_time_ms: int
- stage_times: dict[string -> int]

---

## 5. API Response Model

---

### 5.1 FinalResponse

FinalResponse:
- answer_text: string
- sources: list[SourceReference]
- inferred_scopes: list[ScopeReference]
- certainty: "high" | "medium" | "low" | "uncertain"
- limitations: list[string]
- verification_summary: dict
- trace_id: string

Notes:
- must be strong enough for a direct question/answer surface
- should surface answer limits explicitly rather than hide them

---

## 6. Trace Model

The trace is a serialized AnswerRun.

Requirements:
- complete pipeline visibility
- JSON serializable
- stable structure

---

## 7. Memory Model Alignment

### 7.1 CfHEE Integration

Stored in CfHEE:
- documents
- chunks
- promoted structured knowledge only

---

### 7.2 Answer Engine Storage

Stored locally:
- AnswerRun (optional persistence)
- ChatSession (optional)
- ChatMessage (optional)

Conversation persistence:
- raw interaction records owned by the Answer Engine
- useful for local history and trace linkage

Knowledge promotion:
- only structured, reusable long-term knowledge may be sent to CfHEE
- raw conversation dumps do not belong in CfHEE

---

### 7.3 Transient Data

NOT persisted:
- intermediate pipeline states
- temporary scoring
- candidate scopes

---

## 8. Extension Rules

New fields:
- must be backward compatible
- must not break existing models

New models:
- must be added explicitly here
- must map to a pipeline stage

---

## 9. Summary

The domain model defines:

- how data flows through the pipeline
- how results are structured
- how traceability is ensured

It enforces:
- consistency
- debuggability
- extensibility
