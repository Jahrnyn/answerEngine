# CURRENT_FOCUS - Answer Engine

---

## CURRENT FOCUS

Active stream / live run preview implementation path after backend SSE transport.

Status:
- the backend now exposes bounded live run events over SSE
- the next implementation step is to connect that transport to a frontend preview surface without weakening final verified answer semantics

---

## CURRENT GOAL

Build the first frontend-facing live preview path on top of the new SSE event transport while preserving the verified-final-answer model.

---

## SCOPE

Included:
- frontend consumption groundwork for SSE-backed run events
- staged live preview implementation
- preservation of preview versus final answer semantics
- minimal slices toward usable live run visibility

Excluded:
- persistence
- conversation history
- backend pipeline redesign

---

## DONE WHEN

- SSE-backed run events remain reliable and inspectable
- the next slice can consume transport without redefining event semantics
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
