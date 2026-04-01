from answer_engine_backend.pipeline.models import (
    AnswerResult,
    FinalResponse,
    ScopeInferenceResult,
    VerificationResult,
)


class FinalResponseMappingStage:
    def execute(
        self,
        run_id: str,
        answer_result: AnswerResult,
        scope_inference: ScopeInferenceResult,
        verification_result: VerificationResult,
        source_mapping,
    ) -> FinalResponse:
        certainty = "high" if verification_result.confidence_score >= 0.8 else "medium"
        return FinalResponse(
            answer_text=answer_result.answer_text,
            sources=source_mapping,
            inferred_scopes=[
                scope_inference.primary_scope,
                *scope_inference.secondary_scopes,
            ],
            certainty=certainty,
            limitations=verification_result.limitations,
            verification_summary={
                "decision": verification_result.decision,
                "grounded": verification_result.grounded,
                "confidence_score": verification_result.confidence_score,
            },
            trace_id=run_id,
        )
