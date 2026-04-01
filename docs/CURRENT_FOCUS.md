# CURRENT_FOCUS — Answer Engine

---

## CURRENT FOCUS

Query Analysis and Answer Policy Resolution V1 for the Answer Engine backend.

Status:
- deterministic V1 stage logic implemented
- existing pipeline execution route now exposes more meaningful early-stage outputs

---

## CURRENT GOAL

Replace early placeholder pipeline behavior with practical deterministic V1 logic before real scope inference and retrieval are implemented.

---

## SCOPE

Included:
- query normalization
- simple intent classification
- explicit retrieval-required decision
- bounded query variants
- deterministic answer policy defaults
- route-visible run output for these stages

Excluded:
- real scope inference logic
- real retrieval orchestration logic
- real model/provider integration
- persistence layer
- frontend

---

## DONE WHEN

- backend imports successfully
- `/health` remains working
- `/runs/execute` remains working
- `query_analysis` output is meaningful and deterministic
- `answer_policy` output is meaningful and deterministic

---

## NOT IN SCOPE

- real business logic
- real scope inference
- real retrieval orchestration
- real context building logic
- real model calls
- UI development

---

## NOTES

This step establishes practical V1 behavior for the first two pipeline stages.

Later pipeline stages remain intentionally stubbed.
