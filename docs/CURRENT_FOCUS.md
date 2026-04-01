# CURRENT_FOCUS — Answer Engine

---

## CURRENT FOCUS

CfHEE integration foundation for the Answer Engine backend.

Status:
- thin client foundation implemented
- dev-oriented CfHEE verification surface available

---

## CURRENT GOAL

Establish a thin, explicit client layer for CfHEE as an external dependency without integrating real pipeline behavior yet.

---

## SCOPE

Included:
- config-driven CfHEE base URL handling
- thin CfHEE client wrappers
- health/capabilities access
- scope helper access
- retrieval wrapper skeleton
- dev-oriented verification routes

Excluded:
- real pipeline integration
- real scope inference logic
- real retrieval orchestration logic
- real model provider integration
- persistence layer
- frontend

---

## DONE WHEN

- backend imports successfully
- `/health` remains working
- CfHEE routes are registered
- dependency failure is explicit when CfHEE is unavailable

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

This step establishes the external dependency foundation for CfHEE.

The run pipeline skeleton remains separate and intentionally stubbed.
