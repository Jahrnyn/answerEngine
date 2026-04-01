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
        if not answer_policy.retrieval_required or scope_inference.primary_scope is None:
            scope_status = (
                "retrieval_not_required"
                if not answer_policy.retrieval_required
                else scope_inference.status
            )
            return RetrievalPlan(
                rounds=[],
                fallback_rules={
                    "on_empty": "return_no_evidence",
                    "policy": answer_policy.response_style,
                    "query": query_analysis.normalized_query,
                    "scope_status": scope_status,
                },
            )

        rounds = [
            RetrievalRound(
                scope=scope_inference.primary_scope,
                top_k=answer_policy.default_top_k,
                strategy_type="validated_primary_scope",
            )
        ]

        if answer_policy.allow_multi_scope and scope_inference.secondary_scopes:
            remaining_rounds = max(0, answer_policy.max_retrieval_rounds - len(rounds))
            for secondary_scope in scope_inference.secondary_scopes[:remaining_rounds]:
                rounds.append(
                    RetrievalRound(
                        scope=secondary_scope,
                        top_k=max(1, answer_policy.default_top_k - 1),
                        strategy_type="validated_secondary_scope",
                    )
                )

        return RetrievalPlan(
            rounds=rounds,
            fallback_rules={
                "on_empty": "return_no_evidence",
                "policy": answer_policy.response_style,
                "query": query_analysis.normalized_query,
                "scope_status": scope_inference.status,
                "planned_round_count": str(len(rounds)),
                "max_retrieval_rounds": str(answer_policy.max_retrieval_rounds),
            },
        )
