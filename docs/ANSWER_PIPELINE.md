# ANSWER_PIPELINE - Answer Engine

---

## 1. Purpose

This document defines the exact execution pipeline of the Answer Engine.

It is the authoritative source for:
- how queries are processed
- how scope is inferred
- how retrieval is executed
- how context is built
- how answers are generated and verified

Any change in runtime behavior MUST be reflected here.

---

## 2. Pipeline Overview
User Query
↓
Query Analysis
↓
Answer Policy Resolution
↓
Scope Inference (Hybrid, Bounded)
↓
Retrieval Planning
↓
Retrieval Execution (CfHEE)
↓
Context Assembly
↓
Answer Generation
↓
Answer Verification
↓
Final Response

Each stage:
- receives structured input
- produces structured output
- must be traceable

---

## 3. Stage Definitions

---

### 3.1 Query Analysis Stage

#### Purpose
Understand the user query and determine execution requirements.

#### Inputs
- user_query (string)
- conversation_context (optional)

#### Responsibilities
- normalize query
- detect query intent
- determine if retrieval is required
- optionally generate query variants

Model expectation:
- may be rule-based or use a smaller model

Current local development default:
- rule-based first
- optional small-model fallback intent: `qwen2.5:1.5b`

#### Outputs
QueryAnalysisResult:

- normalized_query
- intent_type
- requires_retrieval (bool)
- max query variants: 2–3

#### Notes
- `conversation_context` is optional support only
- V1 must not depend on long conversation state to answer correctly
- This stage MUST NOT perform retrieval
- This stage MUST NOT modify scope
- model choice is resolved via routing policy, not by the stage itself

---

### 3.2 Answer Policy Resolution Stage

#### Purpose
Resolve backend/runtime controls for the current run.

#### Inputs
- query_analysis_result
- system configuration
- route defaults (optional)

#### Responsibilities
- decide runtime answering constraints for the run
- set retrieval limits and defaults
- set verification strictness
- set regeneration allowance
- remain internal to the backend/runtime

#### Outputs
AnswerPolicy:

- retrieval_required: bool
- max_retrieval_rounds: int
- default_top_k: int
- allow_multi_scope: bool
- allow_regeneration: bool
- verification_profile: string
- response_style: string

#### Notes
- `AnswerPolicy` is NOT a user-facing UI selection
- `AnswerPolicy` must be explicit in trace
- `AnswerPolicy` does NOT replace pipeline stages

---

### 3.3 Scope Inference Stage (Hybrid, Bounded)

#### Purpose
Determine relevant CfHEE scope(s) without user input.

Scope inference remains a core capability in V1.
It must stay hybrid and strong, but it must also remain explicitly budgeted for local execution.

---

#### Step 1 - Heuristic Filtering

Inputs:
- normalized_query
- conversation_context (optional)
- available_scopes (from CfHEE)

Logic:
- keyword matching
- scope metadata hints
- lightweight continuity hints when conversation context exists

V1 execution limit:
- maximum candidate scopes after heuristic filtering: 12

Output:
- candidate_scopes (list)

---

#### Step 2 - LLM-assisted Ranking

Inputs:
- normalized_query
- candidate_scopes

Logic:
- evaluate semantic relevance
- rank scopes
- assign confidence

Model expectation:
- uses a medium-capability model when model assistance is applied

Current backend note:
- the current backend slice may use deterministic interim ranking preparation before model-assisted ranking is implemented

Current local development default when model routing is used:
- `qwen2.5:3b`

V1 execution limit:
- maximum scopes passed into LLM ranking: 6

Output:
RankedScopes:

- primary_scope
- secondary_scopes (optional)
- confidence_scores

---

#### Step 3 - Retrieval Validation

Inputs:
- top scopes

Logic:
- perform lightweight retrieval probe
- validate actual relevance

V1 execution limits:
- maximum scopes validated by retrieval probe: 3
- maximum scopes carried into main retrieval: 2

V1 limit:
- max retrieval rounds: 2

Output:
ValidatedScopes:

- confirmed_primary_scope
- confirmed_secondary_scopes
- validation_scores
- fallback_applied (bool)
- explicit no-reliable-scope outcome when validation remains insufficient

---

#### Scope Failure Fallback

If no reliable scope is produced:
- a narrow broader fallback may be attempted once
- the fallback must remain within the same visible scope hierarchy
- the fallback must be explicit in trace

If fallback still does not produce reliable scope evidence:
- do not continue with uncontrolled scope expansion
- return an explicit no-reliable-scope or no-evidence style response

fallback must stay within:
- same workspace
- same domain

---

#### Notes
- Scope inference MUST NOT rely on LLM alone
- Retrieval validation is mandatory for reliability
- Scope inference MUST remain bounded by explicit execution limits in V1
- model choice is resolved via routing policy, not by the stage itself
- candidate, rejected, validation, and fallback decisions should remain visible in trace

---

### 3.4 Retrieval Planning Stage

#### Purpose
Define how retrieval will be executed.

#### Inputs
- validated_scopes
- query_analysis_result
- answer_policy

#### Responsibilities
- decide number of retrieval rounds
- assign scopes per round
- define top_k values
- define fallback strategy

#### Output
RetrievalPlan:

- rounds:
- - scope
- - top_k
- - strategy_type
- fallback_rules

#### Notes
- V1 planning must respect the bounded scope set from scope inference
- V1 retrieval planning must not silently broaden scope beyond validated or explicit fallback scope
- the current backend slice plans one validated primary round and may add one validated secondary round when bounded policy allows it

---

### 3.5 Retrieval Execution Stage (CfHEE)

#### Purpose
Execute retrieval using CfHEE API.

#### Inputs
- retrieval_plan
- normalized_query

#### Execution
- perform retrieval per round
- collect results
- preserve metadata

#### Output
RetrievalResult:

- results_by_round:
- - scope
- - chunks
- - scores
- aggregated_results

#### Notes
- Retrieval MUST be deterministic per round
- No silent fallback allowed
- the current backend slice returns explicit `no_retrieval` or `no_evidence` style results when retrieval does not proceed or returns no chunks

---

### 3.6 Context Assembly Stage

#### Purpose
Construct the final context for the model.

#### Inputs
- retrieval_result
- token_budget
- answer_policy

#### Responsibilities
- deduplicate chunks
- rank by relevance
- filter low-value chunks
- enforce token limits
- structure context

#### Output
ContextPack:

- selected_chunks
- source_mapping
- structured_context
- token_estimate

#### Notes
- Context must remain interpretable
- Chunk selection must be traceable
- the current backend slice deduplicates by stable chunk identity, applies deterministic bounded truncation, and returns an explicit minimal context when retrieval is empty or skipped

---

### 3.7 Answer Generation Stage

#### Purpose
Generate response using model.

#### Inputs
- user_query
- context_pack
- answer_policy
- system_prompt

#### Execution
- build prompt
- call model provider
- may support runtime/provider streaming internally

Model expectation:
- uses the configured answer-generation model for the current runtime

Current local development default:
- `qwen2.5:7b`

#### Output
AnswerResult:

- answer_text
- token_usage
- model_metadata

#### Notes
- Model provider must be abstracted
- Prompt construction must be traceable
- verification requires a complete candidate answer
- V1 does NOT stream unverified final answer text directly to the user
- V1 may expose pipeline progress or status updates instead of answer-text streaming
- model choice is resolved via routing policy, not by the stage itself
- the current backend slice uses a simple grounded prompt built from the normalized query, structured context, and answer policy
- the current backend slice uses the central stage model resolver plus local Ollama runtime integration for candidate answer generation
- `token_usage` may use provider counts when exposed by the runtime and fall back to approximation only when exact counts are unavailable

---

### 3.8 Answer Verification Stage

#### Purpose
Determine whether the generated answer is reliable enough to keep for V1.

Verification runs only after a complete candidate answer exists.

#### Inputs
- user_query
- answer_result
- context_pack
- validated_scopes
- answer_policy

#### Checks

##### 1. Grounding Check
- verify claims exist in context

##### 2. Scope Consistency Check
- ensure no cross-scope contamination

##### 3. Coverage / Adequacy Check
- verify the answer addresses the user question sufficiently for V1

##### 4. Final Decision Check
- decide whether to keep the answer
- decide whether to keep it with explicit limitations
- decide whether one regeneration attempt is justified

Model expectation:
- uses a smaller or medium-capability model when model assistance is needed

Current local development default when model routing is used:
- `qwen2.5:3b`

#### Output
VerificationResult:

- grounded: bool
- scope_consistency_ok: bool
- coverage_ok: bool
- adequacy_ok: bool
- uncertainty_flags: list[string]
- limitations: list[string]
- decision: "keep" | "limit" | "regenerate" | "cannot_answer"
- requires_regeneration: bool

confidence_score: float (0.0–1.0)

#### Regeneration Rule (V1)

- maximum regeneration attempts: 1
- regeneration is optional and controlled by `AnswerPolicy.allow_regeneration`
- if the regenerated answer is still unacceptable, return an explicit limited, uncertain, or cannot-answer response

#### Notes
- model choice is resolved via routing policy, not by the stage itself
- the current backend slice uses combined practical V1 verification with conservative rule checks plus local model-assisted evaluation when available
- the current backend slice may fall back to explicit rule-based verification if model-assisted verification is unavailable or returns unusable output
- the current backend slice allows at most one explicit regeneration pass and records whether regeneration happened in trace data

---

### 3.9 Final Response Stage

#### Purpose
Prepare response for UI.

#### Output
FinalResponse:

- answer_text
- sources
- inferred_scopes
- certainty
- limitations
- verification_summary
- trace_reference

#### Notes
- the user-visible final answer is shown only after verification
- V1 may expose non-answer run states such as scope inference, retrieval, generation, and verification progress

---

## 4. Trace Model

Each pipeline execution produces a trace.
AnswerRun:

- id
- query
- query_analysis
- answer_policy
- scope_inference
- retrieval_plan
- retrieval_result
- context_pack
- answer_result
- verification_result
- final_response
- timings
- errors

Trace must be:
- complete
- structured
- accessible to UI

---

## 5. Execution Rules

### 5.1 Determinism
Each stage must produce reproducible outputs given same inputs.

---

### 5.2 No Hidden State
All important decisions must be explicit and logged.

---

### 5.3 No Silent Fallback
All fallback behavior must be visible in trace.

---

### 5.4 Fail Transparently
Failures must be surfaced, not hidden.

---

## 6. V1 Execution Budget

V1 is designed for practical local execution, including smaller local models.

Design target:
- one bounded run for one grounded answer
- bounded scope inference before main retrieval
- at most one regeneration attempt
- no unbounded retry loops

Latency target:
- optimize for a responsive local run rather than exhaustive search
- prefer explicit limitation responses over slow cascading retries

Target latency (V1):
- typical: 5–20 seconds
- soft upper bound: 20–25 seconds

The exact numeric latency target is implementation-dependent and not yet verified in code.
The architectural requirement is that V1 remain budgeted and bounded by design.

---

## 7. Failure Handling

Examples:

- no reliable scope after bounded fallback -> explicit no-reliable-scope response
- empty retrieval -> return "no evidence"
- low confidence -> mark answer as uncertain
- verification failure after one allowed regeneration -> return limited or cannot-answer response

---

## 8. Extensibility Rules

New features must:
- map to an existing stage OR
- introduce a new explicit stage

No implicit logic insertion allowed.

---

## 9. Summary

The Answer Engine pipeline is:

- explicit
- multi-stage
- traceable
- grounded
- bounded for local execution

It transforms user queries into validated answers through controlled execution, not emergent agent behavior.
