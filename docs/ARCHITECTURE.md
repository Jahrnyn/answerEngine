# ARCHITECTURE — Answer Engine

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

---

## 2. System Positioning

### 2.1 Relationship to CfHEE

CfHEE provides:
- knowledge storage (documents, chunks)
- scoped retrieval
- optional long-term memory persistence

Answer Engine provides:
- interaction layer
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

- Domain memory → CfHEE
- Conversation memory → hybrid (Answer Engine + CfHEE optional)
- Working memory → Answer Engine (non-persistent)

---

## 4. High-Level Execution Flow
User Query
↓
Query Analysis
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

#### Session Layer
- manages chat sessions
- stores messages
- tracks active context

#### Query Analysis Service
- intent detection
- query normalization
- retrieval requirement decision

#### Scope Inference Service
- candidate scope selection
- ranking and confidence scoring
- validation via retrieval

#### Retrieval Planner
- decides retrieval strategy
- controls number of rounds
- selects scopes and parameters

#### CfHEE Client
- communicates with CfHEE API
- performs scoped retrieval
- optionally writes memory

#### Context Builder
- selects relevant chunks
- deduplicates
- enforces token limits
- builds structured context pack

#### Model Provider Adapter
- abstracts LLM providers
- supports Ollama (default)
- allows future providers

#### Answer Generator
- executes model calls
- supports streaming
- attaches metadata

#### Answer Verifier
- checks grounding
- checks coverage
- detects uncertainty
- may trigger re-run or adjustment

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

Three-column layout:

LEFT:
- conversation list
- session control

CENTER:
- chat interface
- input
- streaming responses

RIGHT:
- sources panel
- context viewer
- trace/debug panel

---

### 6.3 Key UI Concepts

- chat is primary interaction
- trace is always accessible
- answers are inspectable
- developer mode exposes deeper details

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
- no relevant context → explicit response
- low confidence → uncertainty surfaced
- retrieval failure → visible error

---

## 10. Non-Goals (V1)

The system does NOT aim to:

- execute external actions
- call arbitrary tools
- orchestrate multi-agent workflows
- automate business processes
- replace human decision-making

---

## 11. Evolution Direction

Future extensions may include:

- advanced memory integration
- adaptive retrieval strategies
- tool integration
- partial automation layers

These are intentionally deferred.

---

## 12. Summary

The Answer Engine is:

- a pipeline-driven answering runtime
- grounded in CfHEE knowledge
- controlled by explicit architecture
- designed for transparency and reliability

It prioritizes:
- correctness over fluency
- traceability over abstraction
- control over autonomy