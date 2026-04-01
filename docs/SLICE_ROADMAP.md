## Phase 1 — Backend execution foundation

Cél: a run-centric backend csontváza álljon.

Pipeline execution skeleton
RunExecutor
stage interface-ek / service boundary-k
stub pipeline flow: query → run → empty result
Core run data wiring
AnswerRun
QueryAnalysisResult
AnswerPolicy
VerificationResult
trace-alapú végigvezetés a pipeline-on
Stage model routing skeleton
központi stage model resolver
config-driven, de még stub működés
nincs valódi modellhívás

---

## Phase 2 — CfHEE integration foundation

Cél: a modul ténylegesen kapcsolódjon a külső dependencyhez.

CfHEE client skeleton
health
capabilities
base URL / config kezelés
Scope helper integration
scope tree lekérés
scope values lekérés
read-only wrapper
Retrieval integration skeleton
retrieval endpoint wrapper
context/build wrapper, ha kell
még nincs teljes pipeline logika, csak kliensszintű integráció

---

## Phase 3 — Minimal runnable answer path

Cél: az első valódi question → answer backend flow.

Query Analysis V1
kezdetben rule-based
intent detection
retrieval_required
optional query variants bounded módon
Answer Policy Resolution V1
default policy
bounded execution paraméterek
regeneration / multi-scope flag-ek
Scope Inference V1
heuristic filtering
LLM ranking hook
retrieval validation
explicit fallback
Retrieval Planning + Retrieval Execution V1
bounded scope setből retrieval plan
CfHEE hívások
explicit trace
Context Assembly V1
dedupe
rank
token budget
final context pack
Answer Generation V1
legerősebb elérhető modell
no user-visible answer streaming
trace + token metadata
Answer Verification V1
grounding
scope consistency
adequacy
keep / limit / regenerate / cannot_answer
Final Response mapping
answer
certainty
limitations
inferred scopes
trace reference

---

## Phase 4 — Minimal frontend

Cél: legyen egy használható, egyszerű V1 UI.

Angular app shell
alap projekt
dark theme foundation
Main question/answer surface
input
submit
answer display
loading / progress states
Inspect panel shell
sources
context
trace
verification summary
Backend ↔ frontend connection
question submit
run state polling / progress
final answer render

---

## Phase 5 — Persistence and hardening

Cél: a rendszer stabilizálása.

Optional AnswerRun persistence
local storage / db döntés szerint
trace visszanézhetőség
Optional raw interaction persistence
lightweight
nem core reasoning dependency
Error / uncertainty UX hardening
no-evidence
no-reliable-scope
cannot-answer
partial/limited answer states
Dev environment completion
dev-up.ps1
CfHEE dependency check
Ollama/model readiness check