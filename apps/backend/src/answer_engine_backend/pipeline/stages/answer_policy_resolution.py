from answer_engine_backend.pipeline.models import AnswerPolicy, QueryAnalysisResult


class AnswerPolicyResolutionStage:
    def execute(self, query_analysis: QueryAnalysisResult) -> AnswerPolicy:
        intent_type = query_analysis.intent_type
        retrieval_required = query_analysis.requires_retrieval

        max_retrieval_rounds = 2 if retrieval_required else 0
        default_top_k = 5 if intent_type == "lookup" else 4
        allow_multi_scope = intent_type in {"lookup", "explain"} and retrieval_required
        allow_regeneration = False
        verification_profile = "v1_strict"
        response_style = self._resolve_response_style(intent_type)

        return AnswerPolicy(
            retrieval_required=retrieval_required,
            max_retrieval_rounds=max_retrieval_rounds,
            default_top_k=default_top_k,
            allow_multi_scope=allow_multi_scope,
            allow_regeneration=allow_regeneration,
            verification_profile=verification_profile,
            response_style=response_style,
        )

    def _resolve_response_style(self, intent_type: str) -> str:
        if intent_type == "explain":
            return "grounded_explanation"
        if intent_type == "lookup":
            return "grounded_lookup"
        if intent_type == "question_answering":
            return "grounded_answer"
        return "grounded_response"
