# CURRENT_FOCUS - Answer Engine

---

## CURRENT FOCUS

Frontend inspectability and run-surface refinement for the Answer Engine UI.

Status:
- the Angular app shell and main question/answer surface now exist
- the next frontend step is to expose inspectable run details without shifting the UI into a thread-first layout

---

## CURRENT GOAL

Build the first inspect-oriented frontend extension on top of the working main question/answer surface.

---

## SCOPE

Included:
- inspect panel or side-surface work
- sources, context, and trace visibility
- clearer frontend surfacing of run outcomes and limitations

Excluded:
- persistence
- conversation history
- backend redesign

---

## DONE WHEN

- the main question/answer surface remains working
- inspect-oriented frontend visibility exists for at least the core run details
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
