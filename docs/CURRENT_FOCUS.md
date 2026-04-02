# CURRENT_FOCUS - Answer Engine

---

## CURRENT FOCUS

Frontend run-detail polish on top of the run-centric V1 surface.

Status:
- the Angular app shell, main question/answer surface, and refined inspect side-panel now exist
- the next frontend step is to make source and context details easier to review without overbuilding a full trace explorer

---

## CURRENT GOAL

Refine the inspect-oriented frontend surface so source-backed context details and trace-adjacent review become easier to use during normal development.

---

## SCOPE

Included:
- source and context visibility refinement
- inspect-panel readability improvements
- clearer presentation of run diagnostics already present in backend output

Excluded:
- persistence
- conversation history
- backend redesign

---

## DONE WHEN

- the main question/answer surface remains working
- inspect-oriented frontend visibility is useful for routine debugging and review
- source and context details are easier to scan without weakening the run-centric main surface

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
