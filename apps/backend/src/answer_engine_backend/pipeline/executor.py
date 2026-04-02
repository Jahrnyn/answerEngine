from answer_engine_backend.model_runtime import ModelRuntimeError
from answer_engine_backend.pipeline.models import (
    AnswerResult,
    AnswerRun,
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

    def execute(self, query: str) -> AnswerRun:
        timer = StageTimer()
        run_id = new_run_id()
        errors: list[RunError] = []
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
        query_analysis = self.query_analysis_stage.execute(query)
        timer.end_stage("query_analysis")

        timer.start_stage()
        answer_policy = self.answer_policy_resolution_stage.execute(query_analysis)
        timer.end_stage("answer_policy_resolution")

        timer.start_stage()
        scope_inference = self.scope_inference_stage.execute(query_analysis)
        timer.end_stage("scope_inference")
        self._record_non_success_scope_inference(errors, scope_inference)

        timer.start_stage()
        retrieval_plan = self.retrieval_planning_stage.execute(
            query_analysis,
            answer_policy,
            scope_inference,
        )
        timer.end_stage("retrieval_planning")

        timer.start_stage()
        retrieval_result = self.retrieval_execution_stage.execute(
            retrieval_plan,
            query_analysis.normalized_query,
        )
        timer.end_stage("retrieval_execution")
        self._record_non_success_retrieval(errors, retrieval_result)

        timer.start_stage()
        context_pack = self.context_assembly_stage.execute(
            retrieval_result,
            answer_policy,
        )
        timer.end_stage("context_assembly")

        timer.start_stage()
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

        timer.start_stage()
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

        timer.start_stage()
        final_response = self.final_response_mapping_stage.execute(
            run_id,
            answer_result,
            scope_inference,
            verification_result,
            context_pack.source_mapping,
        )
        timer.end_stage("final_response_mapping")

        return AnswerRun(
            id=run_id,
            query=query,
            created_at=utc_now(),
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
