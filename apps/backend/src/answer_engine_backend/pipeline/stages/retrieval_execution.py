from __future__ import annotations

from answer_engine_backend.cfhee_client import CfheeClient
from answer_engine_backend.pipeline.models import (
    RetrievedChunk,
    RetrievalPlan,
    RetrievalResult,
    RetrievalRoundResult,
)
from answer_engine_backend.settings import get_settings


class RetrievalExecutionStage:
    def __init__(self, cfhee_client: CfheeClient | None = None) -> None:
        self.cfhee_client = cfhee_client or CfheeClient(get_settings())

    def execute(self, retrieval_plan: RetrievalPlan, query: str) -> RetrievalResult:
        if not retrieval_plan.rounds:
            scope_status = retrieval_plan.fallback_rules.get("scope_status")
            return RetrievalResult(
                status="no_retrieval",
                results_by_round=[],
                aggregated_results=[],
                failure_reason=scope_status or "retrieval_not_required",
            )

        round_results: list[RetrievalRoundResult] = []
        aggregated_by_key: dict[str, RetrievedChunk] = {}

        for round_index, round_ in enumerate(retrieval_plan.rounds, start=1):
            response = self.cfhee_client.query_retrieval(
                {
                    "query": query,
                    "scope": round_.scope.model_dump(),
                    "top_k": round_.top_k,
                    "include_chunks": True,
                }
            )
            chunks = self._map_chunks(
                response.get("results", []),
                round_index=round_index,
                strategy_type=round_.strategy_type,
            )
            round_results.append(
                RetrievalRoundResult(
                    scope=round_.scope,
                    status="ok" if chunks else "empty",
                    result_count=len(chunks),
                    chunks=chunks,
                )
            )
            for chunk in chunks:
                chunk_key = f"{chunk.document_id}:{chunk.chunk_id}"
                existing = aggregated_by_key.get(chunk_key)
                if existing is None or chunk.score > existing.score:
                    aggregated_by_key[chunk_key] = chunk

        aggregated_results = sorted(
            aggregated_by_key.values(),
            key=lambda chunk: (-chunk.score, chunk.document_id, chunk.chunk_id),
        )
        status = "ok" if aggregated_results else "no_evidence"

        return RetrievalResult(
            status=status,
            results_by_round=round_results,
            aggregated_results=aggregated_results,
            failure_reason=None if aggregated_results else "no_evidence",
        )

    def _map_chunks(
        self,
        results: object,
        *,
        round_index: int,
        strategy_type: str,
    ) -> list[RetrievedChunk]:
        if not isinstance(results, list):
            return []

        chunks: list[RetrievedChunk] = []
        for item_index, item in enumerate(results, start=1):
            if not isinstance(item, dict):
                continue

            document_id = str(item.get("document_id", f"unknown-doc-{round_index}-{item_index}"))
            chunk_id = str(item.get("chunk_id", f"unknown-chunk-{round_index}-{item_index}"))
            content = str(item.get("text", "")).strip()
            similarity_score = item.get("similarity_score", 0.0)
            try:
                score = float(similarity_score)
            except (TypeError, ValueError):
                score = 0.0

            chunks.append(
                RetrievedChunk(
                    document_id=document_id,
                    chunk_id=chunk_id,
                    content=content,
                    score=score,
                    metadata={
                        "stage": "retrieval_execution",
                        "strategy": strategy_type,
                        "round_index": str(round_index),
                        "result_index": str(item_index),
                    },
                )
            )

        return chunks
