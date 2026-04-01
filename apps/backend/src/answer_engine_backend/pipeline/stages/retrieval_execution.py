from answer_engine_backend.pipeline.models import (
    RetrievedChunk,
    RetrievalPlan,
    RetrievalResult,
    RetrievalRoundResult,
)


class RetrievalExecutionStage:
    def execute(self, retrieval_plan: RetrievalPlan, query: str) -> RetrievalResult:
        round_results: list[RetrievalRoundResult] = []
        aggregated_results: list[RetrievedChunk] = []

        for index, round_ in enumerate(retrieval_plan.rounds, start=1):
            chunk = RetrievedChunk(
                document_id=f"stub-doc-{index}",
                chunk_id=f"stub-chunk-{index}",
                content=(
                    "Stub retrieval result for pipeline skeleton execution. "
                    f"Query: {query}"
                ),
                score=1.0,
                metadata={"stage": "retrieval_execution", "strategy": round_.strategy_type},
            )
            round_results.append(RetrievalRoundResult(scope=round_.scope, chunks=[chunk]))
            aggregated_results.append(chunk)

        return RetrievalResult(
            results_by_round=round_results,
            aggregated_results=aggregated_results,
        )
