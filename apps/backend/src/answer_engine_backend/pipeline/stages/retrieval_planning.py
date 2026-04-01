from answer_engine_backend.pipeline.models import (
    AnswerPolicy,
    QueryAnalysisResult,
    RetrievalPlan,
    RetrievalRound,
    ScopeInferenceResult,
)


class RetrievalPlanningStage:
    def execute(
        self,
        query_analysis: QueryAnalysisResult,
        answer_policy: AnswerPolicy,
        scope_inference: ScopeInferenceResult,
    ) -> RetrievalPlan:
        round_ = RetrievalRound(
            scope=scope_inference.primary_scope,
            top_k=answer_policy.default_top_k,
            strategy_type="stub_single_round",
        )
        return RetrievalPlan(
            rounds=[round_],
            fallback_rules={
                "on_empty": "return_no_evidence",
                "policy": answer_policy.response_style,
                "query": query_analysis.normalized_query,
            },
        )
