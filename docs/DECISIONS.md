# Architectural Decisions — Answer Engine

---

## ADR-001
The backend is Python + FastAPI.
Reason: consistency with CfHEE, strong ecosystem for AI orchestration, and rapid development of pipeline-based services.

---

## ADR-002
The frontend is Angular (standalone components).
Reason: existing familiarity and alignment with modern Angular best practices.

---

## ADR-003
The Answer Engine is defined as a pipeline-driven answering runtime, not an agent-based system.
Reason: deterministic execution, traceability, and debuggability are prioritized over emergent behavior.

---

## ADR-004
The system uses explicit pipeline stages instead of implicit orchestration.
Reason: each transformation step must be observable, testable, and controllable.

---

## ADR-005
Scope selection is fully automatic and must not be required from the user.
Reason: the system is designed as a general answering interface, not a scoped query tool.

---

## ADR-006
Scope inference must follow a hybrid approach:
- heuristic filtering
- LLM-assisted ranking
- retrieval-based validation
Reason: combining deterministic and probabilistic methods improves reliability and reduces hallucination risk.

---

## ADR-007
Retrieval is a multi-stage process, not a single operation.
Reason: better coverage, validation, and comparison across scopes.

---

## ADR-008
All answers must be grounded in retrieved context whenever retrieval is used.
Reason: correctness and trust are prioritized over fluent but unsupported responses.

---

## ADR-009
Answer verification is a mandatory pipeline stage.
Reason: local models (e.g. 7B class) require additional validation to reduce hallucination and ensure reliability.

---

## ADR-010
The system must expose full execution trace for every answer.
Reason: inspectability is a core feature, not an optional debugging tool.

---

## ADR-011
The model provider must remain abstracted and replaceable.
Reason: local-first execution now, flexible model integration later.

---

## ADR-012
CfHEE is used as the primary knowledge and long-term memory layer.
Reason: separation of concerns and reuse of existing scoped retrieval infrastructure.

---

## ADR-013
Short-term working memory must remain inside the Answer Engine.
Reason: intermediate pipeline state is transient and should not pollute long-term storage.

---

## ADR-014
Conversation memory may be partially persisted to CfHEE, but only in structured or summarized form.
Reason: prevent noise accumulation while enabling long-term knowledge reuse.

---

## ADR-015
No implicit fallback behavior is allowed in the pipeline.
Reason: all decisions must be explicit and visible in the trace.

---

## ADR-016
Failure states must be surfaced explicitly to the user.
Reason: silent failure or hidden fallback reduces trust and debuggability.

---

## ADR-017
The system must prefer incomplete but correct answers over complete but hallucinated ones.
Reason: correctness is prioritized over perceived completeness.

---

## ADR-018
The Answer Engine is not responsible for document ingestion or knowledge creation.
Reason: ingestion belongs to CfHEE, maintaining a clean module boundary.

---

## ADR-019
The Answer Engine must not perform external tool execution in V1.
Reason: keep the system focused on answering, not automation or orchestration.

---

## ADR-020
The system must be local-first in execution.
Reason: independence from external services and alignment with the CfHEE design philosophy.

---

## ADR-021
All pipeline data structures must conform to the DOMAIN_MODEL definitions.
Reason: consistency, stability, and prevention of schema drift.

---

## ADR-022
New functionality must map to an explicit pipeline stage or introduce a new stage.
Reason: prevent hidden logic and maintain architectural clarity.

---

## ADR-023
The system must not evolve into a general-purpose copilot without explicit redesign.
Reason: preserving focus on high-trust answering instead of uncontrolled feature expansion.

---

## ADR-024
Traceability is a first-class requirement, not a developer-only feature.
Reason: both developers and advanced users must understand how answers are produced.

---

## ADR-025
Scope inference must never silently expand into unrelated domains without validation.
Reason: prevents cross-domain contamination and incorrect answers.

---

## ADR-026
The pipeline must remain reproducible given the same inputs and configuration.
Reason: ensures testability and reliability of the system.

---

## ADR-027
The Answer Engine is an execution layer on top of CfHEE, not a replacement for it.
Reason: preserves modular architecture and reuse of the knowledge layer.

## ADR-028
Repository-level operational scripts must live under the root `scripts/` directory.
Reason: keep developer workflow entrypoints explicit, discoverable, and consistent across environments.

---

## ADR-029
Local development startup must use a root-level `scripts/dev-up.ps1` entrypoint.
Reason: environment preparation and process startup should be standardized instead of manually repeated.

---

## ADR-030
Answer Engine local development must avoid common default dev ports such as 4200 and 8000.
Reason: those ports are frequently occupied by unrelated local projects and increase collision risk.

---

## ADR-031
Default local development ports are:
- frontend: `8760`
- backend: `8761`
Reason: these ports are intentionally less common and should reduce local conflicts.

---

## ADR-032
The development startup script is responsible for checking local prerequisites and starting only the layers relevant to the current development model.
Reason: the workflow should remain practical during early local-first development and evolve later without changing the basic entrypoint pattern.

## ADR-033
The Answer Engine development startup must verify CfHEE availability before starting local services.
Reason: CfHEE is a required upstream dependency of the Answer Engine and the module should not appear healthy when its knowledge/memory backend is unavailable.

---

## ADR-034
CfHEE dependency verification must include both health and capability checks.
Reason: service reachability alone is insufficient; the Answer Engine depends on specific CfHEE capabilities and must fail early if they are missing.

---

## ADR-035
Default CfHEE base URL for local development is `http://127.0.0.1:8770`.
Reason: the Answer Engine should use a stable, non-casual local integration target and avoid common default ports.

---

## ADR-036
The Answer Engine `dev-up.ps1` script must fail fast if CfHEE is not reachable or does not expose the minimum required capabilities.
Reason: partial startup would create a misleading local development state and complicate debugging.