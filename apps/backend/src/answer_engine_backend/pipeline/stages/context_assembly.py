from __future__ import annotations

from answer_engine_backend.pipeline.models import (
    AnswerPolicy,
    ContextPack,
    RetrievalResult,
    RetrievedChunk,
    SourceReference,
)


class ContextAssemblyStage:
    MAX_CONTEXT_CHUNKS = 8

    def execute(
        self,
        retrieval_result: RetrievalResult,
        answer_policy: AnswerPolicy,
    ) -> ContextPack:
        if retrieval_result.status in {"no_retrieval", "no_evidence"}:
            return self._build_empty_context(retrieval_result.failure_reason)

        selected_chunks = self._select_chunks(retrieval_result, answer_policy)
        if not selected_chunks:
            return self._build_empty_context(retrieval_result.failure_reason)

        source_mapping = [
            SourceReference(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                position=index,
            )
            for index, chunk in enumerate(selected_chunks, start=1)
        ]
        structured_context = self._format_context(selected_chunks, source_mapping)

        return ContextPack(
            selected_chunks=selected_chunks,
            source_mapping=source_mapping,
            structured_context=structured_context,
            token_estimate=self._estimate_tokens(structured_context),
        )

    def _select_chunks(
        self,
        retrieval_result: RetrievalResult,
        answer_policy: AnswerPolicy,
    ) -> list[RetrievedChunk]:
        max_chunks = min(
            self.MAX_CONTEXT_CHUNKS,
            max(1, answer_policy.default_top_k * max(1, answer_policy.max_retrieval_rounds)),
        )
        deduped_chunks: list[RetrievedChunk] = []
        seen_chunk_ids: set[str] = set()

        for chunk in retrieval_result.aggregated_results:
            chunk_key = f"{chunk.document_id}:{chunk.chunk_id}"
            if chunk_key in seen_chunk_ids:
                continue
            deduped_chunks.append(chunk)
            seen_chunk_ids.add(chunk_key)
            if len(deduped_chunks) >= max_chunks:
                break

        return deduped_chunks

    def _format_context(
        self,
        selected_chunks: list[RetrievedChunk],
        source_mapping: list[SourceReference],
    ) -> str:
        sections: list[str] = []
        for source, chunk in zip(source_mapping, selected_chunks, strict=True):
            sections.append(
                "\n".join(
                    [
                        f"[Source {source.position}] doc={chunk.document_id} chunk={chunk.chunk_id} score={chunk.score:.3f}",
                        chunk.content,
                    ]
                )
            )
        return "\n\n".join(sections)

    def _estimate_tokens(self, structured_context: str) -> int:
        if not structured_context:
            return 0
        return max(1, len(structured_context) // 4)

    def _build_empty_context(self, failure_reason: str | None) -> ContextPack:
        message = "No retrieved context available."
        if failure_reason:
            message = f"No retrieved context available ({failure_reason})."

        return ContextPack(
            selected_chunks=[],
            source_mapping=[],
            structured_context=message,
            token_estimate=self._estimate_tokens(message),
        )
