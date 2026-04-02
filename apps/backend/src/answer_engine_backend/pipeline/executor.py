from collections.abc import Callable

from answer_engine_backend.model_runtime import ModelRuntimeError
from answer_engine_backend.pipeline.models import (
    AnswerResult,
    AnswerRun,
    RunEvent,
    RunError,
    StageTimer,
    VerificationResult,
    new_run_id,
    utc_now,
)
from answer_engine_backend.pipeline.stage_model_resolver import StageModelResolver
from answer_engine_backend.pipeline.stages import (
    AnswerGenerationStage,
    AnswerPolicyResolutionStage,
    AnswerVerificationStage,
    ContextAssemblyStage,
    FinalResponseMappingStage,
    QueryAnalysisStage,
    RetrievalExecutionStage,
    RetrievalPlanningStage,
    ScopeInferenceStage,
)


class RunExecutor:
    UPSTREAM_FAILURE_STATUSES = {"upstream_timeout", "upstream_unavailable", "upstream_failure"}

    def __init__(self) -> None:
        self.stage_model_resolver = StageModelResolver()
        self.query_analysis_stage = QueryAnalysisStage()
        self.answer_policy_resolution_stage = AnswerPolicyResolutionStage()
        self.scope_inference_stage = ScopeInferenceStage()
        self.retrieval_planning_stage = RetrievalPlanningStage()
        self.retrieval_execution_stage = RetrievalExecutionStage()
        self.context_assembly_stage = ContextAssemblyStage()
        self.answer_generation_stage = AnswerGenerationStage()
        self.answer_verification_stage = AnswerVerificationStage(
            answer_generation_stage=self.answer_generation_stage
        )
        self.final_response_mapping_stage = FinalResponseMappingStage()

    def execute(
        self,
        query: str,
        *,
        event_sink: Callable[[RunEvent], None] | None = None,
    ) -> AnswerRun:
        timer = StageTimer()
        run_id = new_run_id()
        errors: list[RunError] = []
        events: list[RunEvent] = []
        created_at = utc_now()

        def emit_event(
            event_type: str,
            *,
            stage_id: str | None = None,
            message: str | None = None,
            preview_text: str | None = None,
            summary: dict[str, str | int | float | bool | None] | None = None,
        ) -> None:
            event = RunEvent(
                run_id=run_id,
                event_type=event_type,
                stage_id=stage_id,
                timestamp=utc_now(),
                message=message,
                preview_text=preview_text,
                summary=summary or {},
            )
            events.append(event)
            if event_sink is not None:
                event_sink(event)

        emit_event(
            "run_started",
            message="Answer run started.",
            summary={"query_length": len(query)},
        )
        stage_model_routing = self.stage_model_resolver.resolve_many(
            [
                "query_analysis",
                "scope_inference_ranking",
                "answer_generation",
                "answer_verification",
            ]
        )
        answer_generation_model = next(
            (
                config
                for config in stage_model_routing
                if config.stage_id == "answer_generation"
            ),
            self.stage_model_resolver.resolve("answer_generation"),
        )
        answer_verification_model = next(
            (
                config
                for config in stage_model_routing
                if config.stage_id == "answer_verification"
            ),
            self.stage_model_resolver.resolve("answer_verification"),
        )

        timer.start_stage()
        emit_event("stage_started", stage_id="query_analysis", message="Query analysis started.")
        query_analysis = self.query_analysis_stage.execute(query)
        timer.end_stage("query_analysis")
        emit_event(
            "stage_completed",
            stage_id="query_analysis",
            message="Query analysis completed.",
            summary={
                "intent_type": query_analysis.intent_type,
                "requires_retrieval": query_analysis.requires_retrieval,
                "query_variants": len(query_analysis.query_variants),
            },
        )

        timer.start_stage()
        emit_event(
            "stage_started",
            stage_id="answer_policy_resolution",
            message="Answer policy resolution started.",
        )
        answer_policy = self.answer_policy_resolution_stage.execute(query_analysis)
        timer.end_stage("answer_policy_resolution")
        emit_event(
            "stage_completed",
            stage_id="answer_policy_resolution",
            message="Answer policy resolution completed.",
            summary={
                "retrieval_required": answer_policy.retrieval_required,
                "max_retrieval_rounds": answer_policy.max_retrieval_rounds,
                "allow_regeneration": answer_policy.allow_regeneration,
            },
        )

        timer.start_stage()
        emit_event("stage_started", stage_id="scope_inference", message="Scope inference started.")
        scope_inference = self.scope_inference_stage.execute(query_analysis)
        timer.end_stage("scope_inference")
        self._record_non_success_scope_inference(errors, scope_inference)
        emit_event(
            "stage_completed",
            stage_id="scope_inference",
            message="Scope inference completed.",
            summary={
                "status": scope_inference.status,
                "fallback_applied": scope_inference.fallback_applied,
                "candidate_count": len(scope_inference.candidate_scopes),
                "secondary_scope_count": len(scope_inference.secondary_scopes),
            },
        )

        timer.start_stage()
        emit_event(
            "stage_started",
            stage_id="retrieval_planning",
            message="Retrieval planning started.",
        )
        retrieval_plan = self.retrieval_planning_stage.execute(
            query_analysis,
            answer_policy,
            scope_inference,
        )
        timer.end_stage("retrieval_planning")
        emit_event(
            "stage_completed",
            stage_id="retrieval_planning",
            message="Retrieval planning completed.",
            summary={
                "planned_rounds": len(retrieval_plan.rounds),
                "scope_status": retrieval_plan.fallback_rules.get("scope_status", "n/a"),
            },
        )

        timer.start_stage()
        emit_event(
            "stage_started",
            stage_id="retrieval_execution",
            message="Retrieval execution started.",
        )
        retrieval_result = self.retrieval_execution_stage.execute(
            retrieval_plan,
            query_analysis.normalized_query,
        )
        timer.end_stage("retrieval_execution")
        self._record_non_success_retrieval(errors, retrieval_result)
        emit_event(
            "stage_completed",
            stage_id="retrieval_execution",
            message="Retrieval execution completed.",
            summary={
                "status": retrieval_result.status,
                "executed_rounds": len(retrieval_result.results_by_round),
                "aggregated_results": len(retrieval_result.aggregated_results),
            },
        )

        timer.start_stage()
        emit_event(
            "stage_started",
            stage_id="context_assembly",
            message="Context assembly started.",
        )
        context_pack = self.context_assembly_stage.execute(
            retrieval_result,
            answer_policy,
        )
        timer.end_stage("context_assembly")
        emit_event(
            "stage_completed",
            stage_id="context_assembly",
            message="Context assembly completed.",
            summary={
                "selected_chunks": len(context_pack.selected_chunks),
                "token_estimate": context_pack.token_estimate,
            },
        )

        timer.start_stage()
        emit_event(
            "stage_started",
            stage_id="answer_generation",
            message="Answer generation started.",
        )
        if self._should_skip_generation(scope_inference, retrieval_result):
            answer_result = self._build_failure_answer_result(
                category=self._derive_failure_category(scope_inference, retrieval_result),
                message=self._derive_failure_message(scope_inference, retrieval_result),
            )
        else:
            try:
                answer_result = self.answer_generation_stage.execute(
                    query_analysis.normalized_query,
                    context_pack,
                    answer_policy,
                    answer_generation_model,
                )
            except ModelRuntimeError as error:
                errors.append(
                    RunError(
                        stage="answer_generation",
                        category="generation_failure",
                        message=error.message,
                        endpoint=error.endpoint,
                    )
                )
                answer_result = self._build_failure_answer_result(
                    category="generation_failure",
                    message=error.message,
                )
        timer.end_stage("answer_generation")
        if answer_result.answer_text:
            emit_event(
                "stage_preview",
                stage_id="answer_generation",
                message="Bounded answer preview snapshot.",
                preview_text=answer_result.answer_text[:200],
                summary={"preview_chars": min(len(answer_result.answer_text), 200)},
            )
        emit_event(
            "stage_completed",
            stage_id="answer_generation",
            message="Answer generation completed.",
            summary={
                "answer_present": bool(answer_result.answer_text),
                "token_usage_present": bool(answer_result.token_usage),
                "failure_category": str(answer_result.model_metadata.get("failure_category", "none")),
            },
        )

        timer.start_stage()
        emit_event(
            "stage_started",
            stage_id="answer_verification",
            message="Answer verification started.",
        )
        if self._should_skip_verification(scope_inference, retrieval_result, errors):
            verification_result = self._build_failure_verification_result(
                category=self._derive_failure_category(scope_inference, retrieval_result, errors),
                message=self._derive_failure_message(scope_inference, retrieval_result, errors),
            )
        else:
            try:
                verification_outcome = self.answer_verification_stage.execute(
                    query_analysis.normalized_query,
                    answer_result,
                    context_pack,
                    scope_inference,
                    answer_policy,
                    answer_verification_model,
                    answer_generation_model,
                )
                answer_result = verification_outcome.answer_result
                verification_result = verification_outcome.verification_result
            except ModelRuntimeError as error:
                errors.append(
                    RunError(
                        stage="answer_verification",
                        category="verification_failure",
                        message=error.message,
                        endpoint=error.endpoint,
                    )
                )
                verification_result = self._build_failure_verification_result(
                    category="verification_failure",
                    message=error.message,
                )
        timer.end_stage("answer_verification")
        emit_event(
            "stage_completed",
            stage_id="answer_verification",
            message="Answer verification completed.",
            summary={
                "decision": verification_result.decision,
                "grounded": verification_result.grounded,
                "regeneration_attempted": verification_result.regeneration_attempted,
            },
        )

        timer.start_stage()
        emit_event(
            "stage_started",
            stage_id="final_response_mapping",
            message="Final response mapping started.",
        )
        final_response = self.final_response_mapping_stage.execute(
            run_id,
            answer_result,
            scope_inference,
            verification_result,
            context_pack.source_mapping,
        )
        timer.end_stage("final_response_mapping")
        emit_event(
            "stage_completed",
            stage_id="final_response_mapping",
            message="Final response mapping completed.",
            summary={
                "certainty": final_response.certainty,
                "source_count": len(final_response.sources),
                "limitation_count": len(final_response.limitations),
            },
        )

        run_failed = bool(errors) or verification_result.decision == "cannot_answer"
        emit_event(
            "run_failed" if run_failed else "run_completed",
            message=(
                self._derive_failure_message(scope_inference, retrieval_result, errors)
                if run_failed
                else "Answer run completed."
            ),
            summary={
                "decision": verification_result.decision,
                "error_count": len(errors),
                "certainty": final_response.certainty,
                "trace_id": final_response.trace_id,
                "final_answer_text": final_response.answer_text,
                "source_count": len(final_response.sources),
            },
        )

        return AnswerRun(
            id=run_id,
            query=query,
            created_at=created_at,
            answer_policy=answer_policy,
            stage_model_routing=stage_model_routing,
            query_analysis=query_analysis,
            scope_inference=scope_inference,
            retrieval_plan=retrieval_plan,
            retrieval_result=retrieval_result,
            context_pack=context_pack,
            answer_result=answer_result,
            verification_result=verification_result,
            final_response=final_response,
            timings=timer.build(),
            errors=errors,
            events=events,
        )

    def _build_failure_answer_result(
        self,
        *,
        category: str,
        message: str,
    ) -> AnswerResult:
        return AnswerResult(
            answer_text="",
            token_usage={},
            model_metadata={
                "failure_category": category,
                "failure_message": message,
            },
        )

    def _build_failure_verification_result(
        self,
        *,
        category: str,
        message: str,
    ) -> VerificationResult:
        return VerificationResult(
            grounded=False,
            scope_consistency_ok=False,
            coverage_ok=False,
            adequacy_ok=False,
            uncertainty_flags=[category],
            limitations=[message],
            decision="cannot_answer",
            requires_regeneration=False,
            regeneration_attempted=False,
            confidence_score=0.1,
        )

    def _record_non_success_scope_inference(self, errors, scope_inference) -> None:
        if scope_inference.status in {"ok", "fallback"}:
            return
        errors.append(
            RunError(
                stage="scope_inference",
                category=scope_inference.failure_reason or scope_inference.status,
                message=f"Scope inference ended with status '{scope_inference.status}'.",
            )
        )

    def _record_non_success_retrieval(self, errors, retrieval_result) -> None:
        if retrieval_result.status == "ok":
            return
        category = retrieval_result.failure_reason or retrieval_result.status
        errors.append(
            RunError(
                stage="retrieval_execution",
                category=category,
                message=self._message_for_category(
                    category,
                    default=f"Retrieval ended with status '{retrieval_result.status}'.",
                ),
            )
        )

    def _should_skip_generation(self, scope_inference, retrieval_result) -> bool:
        return (
            scope_inference.status in self.UPSTREAM_FAILURE_STATUSES
            or retrieval_result.status in self.UPSTREAM_FAILURE_STATUSES
        )

    def _should_skip_verification(self, scope_inference, retrieval_result, errors) -> bool:
        return self._should_skip_generation(scope_inference, retrieval_result) or any(
            error.category == "generation_failure" for error in errors
        )

    def _derive_failure_category(self, scope_inference, retrieval_result, errors=None) -> str:
        if errors:
            for error in reversed(errors):
                if error.category in {
                    "generation_failure",
                    "verification_failure",
                    "upstream_timeout",
                    "upstream_unavailable",
                    "upstream_failure",
                }:
                    return error.category
        if retrieval_result.status in self.UPSTREAM_FAILURE_STATUSES:
            return retrieval_result.failure_reason or retrieval_result.status
        if scope_inference.status in self.UPSTREAM_FAILURE_STATUSES:
            return scope_inference.failure_reason or scope_inference.status
        if scope_inference.status == "no_reliable_scope":
            return "no_reliable_scope"
        if retrieval_result.status == "no_evidence":
            return "no_evidence"
        return "cannot_answer"

    def _derive_failure_message(self, scope_inference, retrieval_result, errors=None) -> str:
        category = self._derive_failure_category(scope_inference, retrieval_result, errors)
        default_message = self._message_for_category(category)
        if category in self.UPSTREAM_FAILURE_STATUSES | {"no_reliable_scope", "no_evidence", "cannot_answer"}:
            return default_message
        if errors:
            for error in reversed(errors):
                if error.category == category:
                    return error.message
        return default_message

    def _message_for_category(self, category: str, default: str | None = None) -> str:
        messages = {
            "upstream_timeout": "Upstream retrieval timed out before the answer could be completed.",
            "upstream_unavailable": "Upstream retrieval is currently unavailable.",
            "upstream_failure": "Upstream retrieval failed before the answer could be completed.",
            "no_reliable_scope": "No reliable scope could be validated for this query.",
            "no_evidence": "No evidence was retrieved for this query.",
            "generation_failure": "Answer generation failed.",
            "verification_failure": "Answer verification failed.",
            "cannot_answer": "The system cannot answer this reliably from the available evidence.",
        }
        return messages.get(category, default or "The system cannot answer this reliably.")
