from answer_engine_backend.pipeline.models import ContextPack, RetrievalResult, SourceReference


class ContextAssemblyStage:
    def execute(self, retrieval_result: RetrievalResult) -> ContextPack:
        sources = [
            SourceReference(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                position=index,
            )
            for index, chunk in enumerate(retrieval_result.aggregated_results, start=1)
        ]
        structured_context = "\n".join(
            f"[{source.position}] {chunk.content}"
            for source, chunk in zip(sources, retrieval_result.aggregated_results, strict=True)
        )
        return ContextPack(
            selected_chunks=retrieval_result.aggregated_results,
            source_mapping=sources,
            structured_context=structured_context,
            token_estimate=max(1, len(structured_context.split())),
        )
