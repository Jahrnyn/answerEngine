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
Scope Inference (Hybrid)
↓
Retrieval Planning
↓
Retrieval Execution (CfHEE)
↓
Context Assembly
↓
Answer Generation
↓
Evidence Verification
↓
Response Evaluation
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

#### Outputs
QueryAnalysisResult:

- normalized_query
- intent_type
- requires_retrieval (bool)
- query_variants (optional list)

#### Notes
- This stage MUST NOT perform retrieval
- This stage MUST NOT modify scope

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
- remain internal to the backend/runtime

#### Outputs
AnswerPolicy:

- retrieval_required: bool
- max_retrieval_rounds: int
- default_top_k: int
- verification_profile: string
- response_style: string

#### Notes
- `AnswerPolicy` is NOT a user-facing UI selection
- `AnswerPolicy` must be explicit in trace
- `AnswerPolicy` does NOT replace pipeline stages

---

### 3.3 Scope Inference Stage (Hybrid)

#### Purpose
Determine relevant CfHEE scope(s) without user input.

---

#### Step 1 - Heuristic Filtering

Inputs:
- normalized_query
- conversation_context
- available_scopes (from CfHEE)

Logic:
- keyword matching
- scope metadata hints
- lightweight continuity hints when conversation context exists

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

Output:
ValidatedScopes:

- confirmed_primary_scope
- confirmed_secondary_scopes
- validation_scores

---

#### Notes
- Scope inference MUST NOT rely on LLM alone
- Retrieval validation is mandatory for reliability

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
- support streaming

#### Output
AnswerResult:

- answer_text
- token_usage
- model_metadata

#### Notes
- Model provider must be abstracted
- Prompt construction must be traceable

---

### 3.8 Evidence Verification Stage

#### Purpose
Ensure the generated answer is supported by retrieved evidence.

#### Inputs
- answer_result
- context_pack
- validated_scopes

#### Checks

##### 1. Grounding Check
- verify claims exist in context

##### 2. Uncertainty Check
- detect unsupported claims

##### 3. Scope Consistency Check
- ensure no cross-scope contamination

#### Output
EvidenceVerificationResult:

- grounded (bool)
- uncertainty_flags
- scope_consistency_ok (bool)
- requires_regeneration (bool)

---

### 3.9 Response Evaluation Stage

#### Purpose
Evaluate whether the evidence-grounded answer actually satisfies the question.

#### Inputs
- user_query
- answer_result
- evidence_verification_result
- answer_policy

#### Checks

##### 1. Coverage Check
- verify question coverage

##### 2. Response Quality Check
- verify the response follows the intended answer shape for the run

##### 3. Final Handling Decision
- decide whether to keep the answer, mark limitations, or regenerate

#### Output
ResponseEvaluationResult:

- coverage_ok (bool)
- response_quality_ok (bool)
- limitations: list[string]
- requires_regeneration (bool)

#### Optional Actions
- regenerate answer
- downgrade confidence
- inject uncertainty message

---

### 3.10 Final Response Stage

#### Purpose
Prepare response for UI.

#### Output
FinalResponse:

- answer_text
- sources
- inferred_scopes
- verification_summary
- trace_reference

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
- evidence_verification_result
- response_evaluation_result
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

## 6. Failure Handling

Examples:

- no relevant scope -> explicit response
- empty retrieval -> return "no evidence"
- low confidence -> mark answer as uncertain

---

## 7. Extensibility Rules

New features must:
- map to an existing stage OR
- introduce a new explicit stage

No implicit logic insertion allowed.

---

## 8. Summary

The Answer Engine pipeline is:

- explicit
- multi-stage
- traceable
- grounded

It transforms user queries into validated answers through controlled execution, not emergent agent behavior.
