# ACTIVE STREAM / LIVE RUN PREVIEW — Architecture Draft

## 1. Purpose

This design defines a future frontend/backend capability for the Answer Engine:

> live run preview

The feature is NOT classic chatbot token streaming.
It is a controlled, stage-aware execution preview surface for a run-centric verified answering system.

Its purpose is to let the user see that the pipeline is actively working, and optionally see bounded intermediate preview outputs, without breaking the existing verified-final-answer contract.

The final answer remains authoritative only after the pipeline completes verification.

---

## 2. Core Product Rule

The Answer Engine must preserve this distinction:

- preview output = transient, non-authoritative, currently-running stage output
- final output = verified answer shown after the pipeline completes

This distinction is the core UX contract.

The system must NEVER visually blur preview output and final verified answer into the same semantic state.

---

## 3. What this feature IS

Active Stream / Live Run Preview is:

- a real-time execution visibility layer
- a stage-oriented event stream from backend to frontend
- a controlled preview surface for currently running pipeline activity
- optionally capable of showing generation preview text
- always subordinate to the final verified answer

---

## 4. What this feature is NOT

It is NOT:

- direct final-answer token streaming
- a bypass around verification
- a raw debug log dump
- a chat-style emergent stream with no pipeline awareness
- a guarantee that preview text will survive unchanged into the final answer

---

## 5. UX Model

### 5.1 Primary User Experience

User submits one question.

The UI enters a distinct "run active" state.

During this active state, the main answer area changes visually:
- slightly dimmed or visually marked as preview mode
- clearly separated from the final answer state
- may display stage activity and preview output

At completion:
- preview state ends
- final verified answer replaces the preview state
- normal answer view becomes primary again

### 5.2 User Promise

The UI must communicate this clearly:

- while running: "this is what the system is doing now"
- after completion: "this is the final verified answer"

The user must never be misled into thinking the preview text is already the verified answer.

### 5.3 Visual State Separation

At minimum, the UI should have two clearly distinct visual modes:

RUNNING / PREVIEW MODE
- dimmed or altered answer surface
- animated activity indicator
- stage label visible
- preview text may appear
- may be overwritten by subsequent preview content

FINAL / VERIFIED MODE
- normal answer surface
- stable final answer text
- certainty / limitations / decision shown
- no preview semantics visible

---

## 6. Information Hierarchy

The live preview should expose only bounded, high-value information.

Priority order:

1. Current stage
2. Short stage status
3. Important stage outcome preview
4. Generation preview text when generation is active
5. Final verified answer only after completion

The preview must not flood the user with internal technical noise.

---

## 7. Stage Visibility Rules

### 7.1 Always allowed to preview
These stages may emit lightweight preview/status events:

- query_analysis
- answer_policy_resolution
- scope_inference
- retrieval_planning
- retrieval_execution
- context_assembly
- answer_generation
- answer_verification

### 7.2 Recommended preview content by stage

#### Query Analysis
May show:
- normalized question ready
- intent classification
- retrieval required / not required

Do not show:
- low-level internal objects

#### Answer Policy Resolution
May show:
- bounded answering policy selected
- multi-scope enabled/disabled
- regeneration enabled/disabled

Do not show:
- noisy config dumps

#### Scope Inference
May show:
- candidate scope selected
- primary scope candidate
- fallback triggered
- no reliable scope found

This is a high-value preview stage.

#### Retrieval Planning
May show:
- number of planned rounds
- selected retrieval scope(s)
- top_k

#### Retrieval Execution
May show:
- retrieval running
- chunks found count
- no evidence found
- timeout/failure if it happens

#### Context Assembly
May show:
- selected chunk count
- token estimate
- context pack ready

#### Answer Generation
This is the only stage where text streaming is desirable.

May show:
- preview text streamed incrementally
- generation started / running / complete

Important:
this text is preview text only, not final answer text.

#### Answer Verification
May show:
- verification running
- regeneration triggered
- answer limited
- cannot_answer
- verification accepted

Do not show:
- raw judge prompt or full internal scoring dump by default

---

## 8. Preview Text Rules

### 8.1 Generation Preview
Generation preview text may be streamed in real time.

This preview text:
- belongs only to the generation stage
- is ephemeral
- may be replaced or superseded by later verification outcomes
- must be visually marked as preview / draft / in-progress content

### 8.2 Verification Supersession
If verification decides:
- keep -> final answer becomes visible
- limit -> final answer may differ in phrasing or state labeling
- regenerate -> generation preview may be replaced by regenerated preview or withheld until final answer
- cannot_answer -> preview disappears and final cannot-answer result is shown

### 8.3 Finality Rule
Preview text must never silently become the final answer without the UI indicating that the run has completed and verification has passed.

---

## 9. Recommended UX Behavior

### 9.1 Minimal V1.1 path
Smallest useful version:
- spinner/activity indicator
- current stage label
- short stage status text

No text streaming yet.

### 9.2 V1.2 path
Adds:
- stage summary preview
- scope choice preview
- retrieval summary preview
- verification status preview

### 9.3 V1.3 path
Adds:
- generation preview text streaming
- still marked as transient preview
- replaced by final verified result at end

This is the recommended phased implementation path.

---

## 10. Backend Architecture Requirements

This feature requires a real-time run event stream.

The existing request/response model is not enough by itself.

The backend must emit structured run events while a run is executing.

### 10.1 Recommended transport
Use Server-Sent Events (SSE) first.

Reason:
- one-way backend -> frontend fits this use case
- simpler than WebSocket
- enough for pipeline preview streaming
- lower implementation complexity

WebSocket is not required for the first version.

### 10.2 Event stream shape
The backend should emit typed events such as:

- run_started
- stage_started
- stage_progress
- stage_preview
- stage_completed
- run_completed
- run_failed

### 10.3 Event payload design
Each event should carry only bounded, stage-relevant data.

Recommended common fields:
- run_id
- event_type
- stage_id
- timestamp
- message
- preview_text (optional)
- summary (optional structured lightweight object)

Do not stream giant internal objects by default.

---

## 11. Frontend State Model

The frontend must treat preview state and final state as separate.

Recommended top-level state groups:

- idle
- running_preview
- completed
- failed

### 11.1 running_preview state
Contains:
- current stage
- latest preview message
- latest preview text
- latest stage summary
- whether generation preview is active

### 11.2 completed state
Contains:
- final verified answer response
- certainty
- limitations
- inspect drawer data

### 11.3 failed state
Contains:
- explicit failure/cannot-answer outcome
- any useful run-level diagnostics

---

## 12. Main Answer Surface Behavior

### 12.1 While running
The main answer card should:
- enter preview mode
- show activity
- optionally show streamed preview text
- not present itself as final

### 12.2 After completion
The main answer card should:
- leave preview mode
- render final verified answer normally
- remove transient preview styling
- preserve final certainty/limitations/decision

---

## 13. Inspect Panel Behavior

The inspect panel should remain secondary.

During active run:
- it may show current stage
- stage summaries
- event timeline snippets

After completion:
- it shows the final trace-oriented data as it does now

The inspect drawer should not become the only place where run activity is visible.
The main surface should still communicate that the pipeline is active.

---

## 14. Performance / Cost Considerations

### 14.1 Compute cost
The event stream itself is cheap.
The main cost does NOT come from SSE or frontend rendering.

The real costs are:
- additional backend event emission logic
- optional generation preview handling
- optional token-by-token generation stream forwarding

### 14.2 Complexity cost
The biggest cost is architectural complexity, not raw performance.

The system now needs:
- preview event model
- running-state frontend rendering
- transition rules between preview and final answer
- explicit handling of overwritten preview outputs

### 14.3 Safe first implementation
To keep complexity bounded:
- start with stage events and short summaries only
- add generation preview text later
- keep final answer rendering unchanged

---

## 15. Failure Semantics

If a run fails mid-stream:
- the preview must stop
- the UI must transition into a truthful failure/cannot-answer state
- the final answer surface must not imply success

Examples:
- no_reliable_scope
- upstream_timeout
- no_evidence
- generation_failure
- verification_failure

These should appear as explicit final states, not just as disappearing previews.

---

## 16. Token Streaming Clarification

If generation preview text is streamed, it is acceptable for that preview to reflect real token streaming from the generation model.

But:
- that preview is not the final answer
- verification may still reject or limit it
- the UI must visibly distinguish preview from final

This resolves the original conflict:
the system is not streaming the final verified answer early;
it is streaming generation-stage preview output only.

---

## 17. Recommended Terminology

Use stable terms in UI and docs:

- Live Run Preview
- Run Activity
- Preview Output
- Final Verified Answer

Avoid ambiguous labels like:
- "answer streaming"
- "live answer"
if they could imply finality.

---

## 18. Recommended Slice Plan

### Slice A
Backend event model + frontend running-state shell
- no generation preview text yet

### Slice B
Stage summary events for:
- scope inference
- retrieval
- verification

### Slice C
Generation preview text streaming
- preview-only
- visually distinct
- replaced by final answer on completion

### Slice D
Polish / refine transitions and drawer timeline

---

## 19. Architecture Rule to Add

A future architecture/doc rule should be:

V1 final answer semantics remain unchanged:
- the user-visible final answer is still shown only after verification

Live preview, if implemented, is:
- non-final
- transient
- stage-scoped
- explicitly distinguished from the final answer

---

## 20. Summary

This feature is feasible and valuable.

It should be treated as:
- a live execution preview system
- not a classic chatbot streaming system

The right model is:
- pipeline activity is visible
- generation preview may be visible
- verification remains authoritative
- final answer remains post-verification only

This preserves the high-trust Answer Engine architecture while still making the runtime feel alive and inspectable.