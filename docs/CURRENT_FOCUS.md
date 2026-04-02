# CURRENT_FOCUS - Answer Engine

---

## CURRENT FOCUS

Active stream / live run preview refinement after initial frontend SSE consumption.

Status:
- the backend now exposes bounded live run events over SSE
- the frontend now consumes that transport for non-final stage/activity preview on the main surface
- richer stage-summary preview now exists for scope, retrieval, context, and verification
- the next implementation step is to extend preview richness further without weakening final verified answer semantics

---

## CURRENT GOAL

Refine live run preview on top of the existing SSE path while preserving the verified-final-answer model.

---

## SCOPE

Included:
- frontend consumption groundwork for SSE-backed run events
- staged live preview refinement
- preservation of preview versus final answer semantics
- minimal slices toward usable live run visibility
- preview-only generation-text work as the next higher-value incremental step

Excluded:
- persistence
- conversation history
- backend pipeline redesign

---

## DONE WHEN

- SSE-backed run events remain reliable and inspectable
- frontend preview remains visibly non-final during execution
- the next slice can enrich preview detail without redefining event semantics
- preview output and final verified answer semantics remain clearly separated

---

## NOT IN SCOPE

- persistence
- chat-thread UX
- major backend changes
- full chat-style streaming redesign
- backend transport redesign

---

## NOTES

The UI must stay run-centric in V1:
- main surface first
- inspectability second
- no thread-first product framing
- future live preview must remain non-final until verification completes
