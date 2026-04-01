# Answer Engine

## Overview

Answer Engine is a local-first, modular answering system built on top of a scoped knowledge infrastructure (CfHEE).

The system is designed to take a single user question and produce a **grounded, high-trust answer** by:

- selecting relevant knowledge scope(s)
- retrieving context from CfHEE
- generating an answer using local models
- verifying that the answer is supported by evidence

It is not a chatbot.
It is a **run-based answering engine**.

---

## Core Idea

> One question → one controlled execution → one grounded answer

Each request is executed as an independent **AnswerRun**, which goes through a structured pipeline:

1. Query Analysis  
2. Answer Policy Resolution  
3. Scope Inference  
4. Retrieval  
5. Context Assembly  
6. Answer Generation  
7. Verification  
8. Final Response

The system prioritizes:
- determinism
- traceability
- explicit decisions
- bounded execution

---

## Relationship with CfHEE

Answer Engine depends on **CfHEE (Context-first Hierarchical Enterprise Engine)** as its knowledge backend.

CfHEE is responsible for:
- document ingestion
- storage
- scoped retrieval
- context building

Answer Engine is responsible for:
- orchestration
- scope selection
- answer generation
- verification

Important boundary:

> CfHEE = knowledge system  
> Answer Engine = answering system

---

## Key Design Principles

- **Local-first**
  - Designed to run entirely on a developer machine
  - Uses local models (via Ollama or similar)

- **Run-centric**
  - No chat-first design
  - Each execution is independent and inspectable

- **Scoped reasoning**
  - Retrieval always happens within explicit scope
  - No hidden global search

- **High-trust answers**
  - Answers must be grounded in retrieved evidence
  - Verification is part of the pipeline

- **Explicit over implicit**
  - No hidden heuristics
  - All major decisions are visible in the run output

- **Modular architecture**
  - Each stage is isolated and replaceable
  - Model usage is configurable per stage

---

## Architecture (High-level)

Frontend (Angular) → Answer Engine (FastAPI backend) →CfHEE (knowledge infrastructure)

Backend pipeline:
RunExecutor
- Query Analysis
- Answer Policy
- Scope Inference
- Retrieval
- Context Assembly
- Answer Generation
- Verification
- Final Response

---

## Model Usage

The system supports **stage-specific model routing**:

- lightweight stages may use:
  - rule-based logic
  - small models

- complex stages may use:
  - medium models (e.g. scope ranking)

- answer generation uses:
  - the strongest available model

Model selection is:
- centralized
- configurable
- not hardcoded

---

## Current State (V0.1)

The project is in early backend development.

Currently implemented:

- backend scaffold (FastAPI)
- pipeline execution skeleton (`RunExecutor`)
- deterministic Query Analysis
- deterministic Answer Policy Resolution
- CfHEE client foundation
- stage model resolver skeleton
- developer execution route (`/runs/execute`)

Not yet implemented:

- real scope inference logic
- retrieval orchestration
- context assembly
- answer generation
- verification
- frontend
- persistence

---

## Development Approach

The project is **documentation-driven** and built in small, controlled slices.

Workflow:

1. define behavior in docs
2. implement minimal vertical slice
3. update docs immediately

Key rules:

- small changes only
- no speculative abstractions
- no hidden behavior
- no overengineering

---

## Intended Use (V1)

V1 is a **developer-oriented answering system**:

- local execution
- inspectable pipeline
- traceable decisions
- controlled reasoning

It is not yet a production chatbot.

---

## Future Direction

Planned evolutions include:

- improved scope inference (hybrid + model-assisted)
- real model integration
- verification improvements
- UI for inspection and control
- optional persistence
- runtime packaging

---

## Status

Experimental / in active development.
