# CURRENT_FOCUS - Answer Engine

---

## CURRENT FOCUS

Frontend inspectability refinement on top of the run-centric V1 surface.

Status:
- the Angular app shell, main question/answer surface, and initial inspect panel shell now exist
- the next frontend step is to make inspectability more useful without turning the UI into a thread-first workbench

---

## CURRENT GOAL

Refine the inspect-oriented frontend surface so sources, context, and run details become easier to review during normal development use.

---

## SCOPE

Included:
- inspect panel refinement
- clearer sources and context visibility
- better trace-adjacent readability in the frontend

Excluded:
- persistence
- conversation history
- backend redesign

---

## DONE WHEN

- the main question/answer surface remains working
- inspect-oriented frontend visibility is useful for routine debugging and review
- failure and limitation states remain explicit and easy to understand

--- 

## NOT IN SCOPE

- persistence
- chat-thread UX
- major backend changes

--- 

## NOTES

The UI must stay run-centric in V1:
- main surface first
- inspectability second
- no thread-first product framing
