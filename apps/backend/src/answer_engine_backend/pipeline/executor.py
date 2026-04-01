from answer_engine_backend.pipeline.models import AnswerRun, StageTimer, new_run_id, utc_now
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
    def __init__(self) -> None:
        self.stage_model_resolver = StageModelResolver()
        self.query_analysis_stage = QueryAnalysisStage()
        self.answer_policy_resolution_stage = AnswerPolicyResolutionStage()
        self.scope_inference_stage = ScopeInferenceStage()
        self.retrieval_planning_stage = RetrievalPlanningStage()
        self.retrieval_execution_stage = RetrievalExecutionStage()
        self.context_assembly_stage = ContextAssemblyStage()
        self.answer_generation_stage = AnswerGenerationStage()
        self.answer_verification_stage = AnswerVerificationStage()
        self.final_response_mapping_stage = FinalResponseMappingStage()

    def execute(self, query: str) -> AnswerRun:
        timer = StageTimer()
        run_id = new_run_id()
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

        timer.start_stage()
        query_analysis = self.query_analysis_stage.execute(query)
        timer.end_stage("query_analysis")

        timer.start_stage()
        answer_policy = self.answer_policy_resolution_stage.execute(query_analysis)
        timer.end_stage("answer_policy_resolution")

        timer.start_stage()
        scope_inference = self.scope_inference_stage.execute(query_analysis)
        timer.end_stage("scope_inference")

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

        timer.start_stage()
        context_pack = self.context_assembly_stage.execute(
            retrieval_result,
            answer_policy,
        )
        timer.end_stage("context_assembly")

        timer.start_stage()
        answer_result = self.answer_generation_stage.execute(
            query_analysis.normalized_query,
            context_pack,
            answer_policy,
            answer_generation_model,
        )
        timer.end_stage("answer_generation")

        timer.start_stage()
        verification_result = self.answer_verification_stage.execute(
            answer_result,
            context_pack,
            answer_policy,
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
            errors=[],
        )
