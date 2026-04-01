# ARCHITECTURE - Answer Engine

---

## 1. Overview

The Answer Engine is a locally runnable, developer-controlled answering runtime built on top of CfHEE.

It is NOT:
- a generic chatbot
- a copilot system
- an autonomous agent framework

It IS:
- a structured answering system
- a pipeline-driven execution engine
- a high-trust, inspectable answer generator

The system transforms user queries into grounded answers through a multi-stage pipeline involving:
- query analysis
- scope inference
- retrieval
- context construction
- reasoning
- verification

V1 is run-centric, not chat-centric:
- the primary runtime unit is `AnswerRun`
- the primary V1 flow is one question -> one grounded answer
- long continuous conversation handling is not a primary V1 capability

---

## 2. System Positioning

### 2.1 Relationship to CfHEE

CfHEE provides:
- knowledge storage (documents, chunks)
- scoped retrieval
- long-term structured knowledge persistence

Answer Engine provides:
- run execution and interaction persistence
- execution pipeline
- reasoning and answer generation
- traceability and inspection

---

### 2.2 Layered Model
[ User Interface (Angular) ]
↓
[ Answer Engine (FastAPI) ]
↓
[ CfHEE (Knowledge + Memory Layer) ]
↓
[ Storage + Vector DB ]

---

## 3. Core Architectural Principles

### 3.1 Pipeline over Agents

The system is explicitly structured as a deterministic pipeline.

LLMs may be used within stages, but:
- orchestration is NOT delegated to agents
- each stage has a defined responsibility
- behavior must remain traceable and debuggable

---

### 3.2 Hybrid Scope Inference

The system automatically determines relevant scope(s).

This is implemented as a hybrid approach:
- heuristic filtering
- LLM-assisted ranking
- retrieval-based validation

In V1 this remains a strong core capability, not a trivial heuristic shortcut.
It must also remain bounded by explicit execution limits so local runs stay practical.

The user does NOT select scope manually.

---

### 3.3 Multi-Stage Retrieval

Retrieval is not a single step.

The system may:
- query multiple scopes
- perform multiple rounds
- compare results

Retrieval is treated as an iterative process, not a one-shot call.

---

### 3.4 Grounded Answering

Answers must be:
- based on retrieved context
- traceable to sources
- constrained when confidence is low

The system must prefer:
- partial but correct answers
over:
- complete but hallucinated answers

---

### 3.5 Inspectability as a First-Class Feature

Every answer must be inspectable.

The system exposes:
- inferred scopes
- retrieval results
- selected chunks
- context pack
- model inputs (optional)
- verification outcomes

---

### 3.6 Memory Separation

The system distinguishes:

- Domain memory -> CfHEE
- Raw interaction persistence -> Answer Engine
- Long-term structured knowledge promotion -> CfHEE
- Working memory -> Answer Engine (non-persistent)

Raw question/answer interactions remain the responsibility of the Answer Engine.
Only long-term valuable structured knowledge may be promoted into CfHEE.

---

## 4. High-Level Execution Flow
User Query
↓
Query Analysis
↓
Answer Policy Resolution
↓
Scope Inference
↓
Retrieval Planning
↓
CfHEE Retrieval (multi-round)
↓
Context Assembly
↓
Answer Generation
↓
Answer Verification
↓
Final Response

Each stage produces structured outputs that can be inspected.

---

## 5. Backend Architecture

### 5.1 Technology

- Python
- FastAPI
- modular service structure
- local-first execution

---

### 5.2 Core Components

#### Run Layer
- manages `AnswerRun` execution records
- stores raw interaction history when persistence is enabled
- keeps optional lightweight links to conversation structures

#### Query Analysis Service
- intent detection
- query normalization
- retrieval requirement decision

#### Answer Policy Resolver
- resolves backend/runtime answering controls
- sets retrieval and verification defaults
- sets bounded execution constraints for the run
- resolves stage-specific model routing centrally
- is internal, not user-facing

#### Scope Inference Service
- candidate scope selection
- ranking and confidence scoring
- validation via retrieval
- bounded fallback handling when no reliable scope is found

#### Retrieval Planner
- decides retrieval strategy
- controls number of rounds
- selects scopes and parameters

#### CfHEE Client
- communicates with CfHEE API
- performs scoped retrieval
- does not own raw interaction persistence

#### Context Builder
- selects relevant chunks
- deduplicates
- enforces token limits
- builds structured context pack

#### Model Provider Adapter
- abstracts LLM providers
- supports Ollama (default)
- allows future providers

#### Stage Model Resolver
- resolves model choice centrally per pipeline stage
- keeps model selection configuration-driven, not hardcoded
- may route stages to rule-based execution, smaller models, or stronger models
- keeps stage code free from direct model selection

#### Answer Generator
- executes model calls
- may support provider/runtime streaming internally
- attaches metadata

#### Answer Verifier
- performs combined V1 verification
- determines keep, limitation, or single regeneration decision
- may trigger at most one re-run

#### Trace Service
- records full execution trace
- exposes pipeline visibility

---

## 6. Frontend Architecture

### 6.1 Technology

- Angular
- standalone components
- modular UI structure

---

### 6.2 Layout Model

V1 layout:

MAIN SURFACE:
- question input
- grounded answer output

OPTIONAL INSPECT / SIDE PANEL:
- sources panel
- context viewer
- trace/debug panel
- verification details

---

### 6.3 Key UI Concepts

- the main question/answer surface is primary in V1
- the final answer text is shown only after verification
- pipeline progress or status updates may be shown during execution
- trace is always accessible when inspection is needed
- answers are inspectable
- developer mode exposes deeper details
- conversation/session UI is optional support, not the primary V1 interaction model

---

## 7. Model Integration

### 7.1 Default

- Ollama
- local models (e.g. 7B class)

---

### 7.2 Abstraction

Model providers must be replaceable.

The system must support:
- synchronous generation
- streaming generation
- model metadata access

In V1, provider/runtime streaming support does not imply streaming unverified final answer text to the user.

---

### 7.3 Stage-Specific Model Routing

Model usage is stage-specific in V1.

This means:
- each pipeline stage may use a different model
- some stages may be rule-based instead of model-driven
- model selection is resolved centrally, not scattered across stages
- routing must be configuration-driven, not hardcoded

Typical routing intent:
- lightweight stages may use rules or smaller models
- ranking and verification stages may use smaller or medium-capability models
- answer generation uses the strongest available model in the current runtime

This is a routing concept, not a claim of implemented runtime behavior.

---

## 8. Data Flow Philosophy

The system operates on structured intermediate data.

Each stage produces:
- explicit outputs
- typed structures
- traceable transformations

No stage should:
- hide critical decisions
- mutate state implicitly

---

## 9. Error Handling Strategy

The system must:

- degrade gracefully
- expose failures in trace
- avoid silent fallback behavior

Examples:
- no relevant context -> explicit response
- low confidence -> uncertainty surfaced
- retrieval failure -> visible error
- no reliable scope after bounded fallback -> explicit limitation response

---

## 10. V1 Execution Budget

V1 is designed for bounded local execution.

This means:
- bounded scope inference before main retrieval
- bounded retrieval planning
- a single combined verification stage
- at most one regeneration attempt
- explicit limitation responses instead of unbounded retries

The exact runtime numbers are implementation concerns.
The architectural requirement is that V1 remains budgeted by design for local models.

---

## 11. Non-Goals (V1)

The system does NOT aim to:

- execute external actions
- call arbitrary tools
- orchestrate multi-agent workflows
- automate business processes
- replace human decision-making
- prioritize long continuous conversation management

---

## 12. Evolution Direction

Future extensions may include:

- advanced knowledge promotion rules
- adaptive retrieval strategies
- tool integration
- partial automation layers

These are intentionally deferred.

---

## 13. Summary

The Answer Engine is:

- a pipeline-driven answering runtime
- grounded in CfHEE knowledge
- controlled by explicit architecture
- designed for transparency and reliability

It prioritizes:
- correctness over fluency
- traceability over abstraction
- control over autonomy
