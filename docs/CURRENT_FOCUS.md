# CURRENT_FOCUS - Answer Engine

---

## CURRENT FOCUS

Active stream / live run preview implementation path after the first in-memory event foundation.

Status:
- the backend now emits bounded in-memory run events in dev run output
- the next implementation step is to add a transport-backed preview path without weakening final verified answer semantics

---

## CURRENT GOAL

Extend the new run-event foundation toward staged live preview transport while preserving the verified-final-answer model.

---

## SCOPE

Included:
- transport-ready active stream groundwork
- staged backend preview implementation
- preservation of preview versus final answer semantics
- minimal slices toward SSE or equivalent live run visibility

Excluded:
- persistence
- conversation history
- backend pipeline redesign

---

## DONE WHEN

- bounded run events remain reliable and inspectable
- the next slice can add transport without redefining event semantics
- preview output and final verified answer semantics remain clearly separated

---

## NOT IN SCOPE

- persistence
- chat-thread UX
- major backend changes
- full chat-style streaming redesign

---

## NOTES

The UI must stay run-centric in V1:
- main surface first
- inspectability second
- no thread-first product framing
- future live preview must remain non-final until verification completes
