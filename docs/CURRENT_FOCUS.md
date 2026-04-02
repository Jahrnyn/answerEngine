# CURRENT_FOCUS - Answer Engine

---

## CURRENT FOCUS

Active stream / live run preview refinement after initial frontend SSE consumption.

Status:
- the backend now exposes bounded live run events over SSE
- the frontend now consumes that transport for non-final stage/activity preview on the main surface
- richer stage-summary preview now exists for scope, retrieval, context, and verification
- generation preview text now exists as non-final `answer_generation` output during active runs
- preview transitions now clear or restart generation preview text correctly across verification, regeneration, and terminal outcomes
- the next implementation step is to extend inspectability and preview polish further without weakening final verified answer semantics

---

## CURRENT GOAL

Refine live run preview beyond initial generation preview and transition correctness while preserving the verified-final-answer model.

---

## SCOPE

Included:
- frontend consumption groundwork for SSE-backed run events
- staged live preview refinement
- preservation of preview versus final answer semantics
- minimal slices toward usable live run visibility
- inspectability refinement after preview transition correctness

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
