# CURRENT_FOCUS - Answer Engine

---

## CURRENT FOCUS

Active stream / live run preview groundwork on top of the run-centric V1 surface.

Status:
- the Angular app shell, refined main result surface, and inspect drawer now exist
- the next implementation step is to define the backend run-event contract and staged preview semantics before SSE or frontend live preview work begins

---

## CURRENT GOAL

Prepare the repository for staged live run preview work without weakening the current verified-final-answer model.

---

## SCOPE

Included:
- active stream document integration
- backend run-event contract definition
- clarification of preview versus final answer semantics
- staged implementation groundwork for later SSE/live preview slices

Excluded:
- SSE endpoint implementation
- live frontend preview implementation
- backend pipeline redesign
- persistence
- conversation history

---

## DONE WHEN

- the active stream design is integrated into the documentation system
- the backend run-event contract is defined minimally and explicitly
- preview output and final verified answer semantics are clearly separated in the docs

---

## NOT IN SCOPE

- persistence
- chat-thread UX
- major backend changes
- full streaming transport or frontend preview implementation

---

## NOTES

The UI must stay run-centric in V1:
- main surface first
- inspectability second
- no thread-first product framing
- future live preview must remain non-final until verification completes
