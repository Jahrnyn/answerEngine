# CURRENT_FOCUS — Answer Engine

---

## CURRENT FOCUS

Stage Model Resolver skeleton for the Answer Engine backend.

Status:
- stage-specific routing defaults are the active backend infrastructure target
- no real model execution is in scope for this step

---

## CURRENT GOAL

Add a small central resolver for stage-specific model routing so model intent is configuration-driven and inspectable before real provider execution exists.

---

## SCOPE

Included:
- central stage model resolver
- config-driven routing defaults for key V1 stages
- inspectable routing output in the run payload
- keeping stage modules free from direct model choice

Excluded:
- real model/provider execution
- real scope inference logic
- real retrieval orchestration logic
- persistence layer
- frontend

---

## DONE WHEN

- backend imports successfully
- `/health` remains working
- `/runs/execute` remains working
- routing output is visible and deterministic in run execution results

---

## NOT IN SCOPE

- real scope inference
- real retrieval orchestration
- real context building logic
- real model calls
- UI development

---

## NOTES

This step establishes the central runtime hook for stage-specific model routing without changing later stub stage behavior into real model execution.
