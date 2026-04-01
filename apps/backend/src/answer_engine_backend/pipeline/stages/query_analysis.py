from answer_engine_backend.pipeline.models import QueryAnalysisResult


class QueryAnalysisStage:
    def execute(self, query: str) -> QueryAnalysisResult:
        normalized_query = " ".join(query.strip().split())
        variants = [normalized_query]
        if normalized_query.endswith("?"):
            variants.append(normalized_query.rstrip("?"))

        return QueryAnalysisResult(
            normalized_query=normalized_query,
            intent_type="question_answering",
            requires_retrieval=True,
            query_variants=variants[:2],
        )
