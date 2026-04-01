from answer_engine_backend.pipeline.models import AnswerPolicy, QueryAnalysisResult


class AnswerPolicyResolutionStage:
    def execute(self, query_analysis: QueryAnalysisResult) -> AnswerPolicy:
        return AnswerPolicy(
            retrieval_required=query_analysis.requires_retrieval,
            max_retrieval_rounds=1,
            default_top_k=3,
            allow_multi_scope=False,
            allow_regeneration=False,
            verification_profile="v1_stub",
            response_style="grounded_answer",
        )
