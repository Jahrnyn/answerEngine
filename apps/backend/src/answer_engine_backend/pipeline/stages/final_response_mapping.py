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
        certainty = self._resolve_certainty(verification_result)
        inferred_scopes = []
        if scope_inference.primary_scope is not None:
            inferred_scopes.append(scope_inference.primary_scope)
        inferred_scopes.extend(scope_inference.secondary_scopes)
        answer_text = self._resolve_answer_text(answer_result, verification_result)

        return FinalResponse(
            answer_text=answer_text,
            sources=source_mapping,
            inferred_scopes=inferred_scopes,
            certainty=certainty,
            limitations=verification_result.limitations,
            verification_summary={
                "decision": verification_result.decision,
                "grounded": verification_result.grounded,
                "scope_consistency_ok": verification_result.scope_consistency_ok,
                "coverage_ok": verification_result.coverage_ok,
                "adequacy_ok": verification_result.adequacy_ok,
                "regeneration_attempted": verification_result.regeneration_attempted,
                "confidence_score": verification_result.confidence_score,
            },
            trace_id=run_id,
        )

    def _resolve_certainty(self, verification_result: VerificationResult) -> str:
        if verification_result.decision == "cannot_answer":
            return "uncertain"
        if verification_result.confidence_score >= 0.8:
            return "high"
        if verification_result.confidence_score >= 0.6:
            return "medium"
        return "low"

    def _resolve_answer_text(
        self,
        answer_result: AnswerResult,
        verification_result: VerificationResult,
    ) -> str:
        if verification_result.decision == "cannot_answer":
            joined_limitations = " ".join(verification_result.limitations).lower()
            if "timed out" in joined_limitations or "upstream_timeout" in joined_limitations:
                return "I can't answer this reliably because upstream retrieval timed out before the run completed."
            if "unavailable" in joined_limitations or "upstream_unavailable" in joined_limitations:
                return "I can't answer this reliably because the upstream retrieval service is currently unavailable."
            if "no reliable scope" in joined_limitations or "no_reliable_scope" in joined_limitations:
                return "I can't answer this reliably because no validated scope could be confirmed for the query."
            if "no evidence" in joined_limitations:
                return "I can't answer this reliably because no evidence was retrieved for the query."
            if "generation failed" in joined_limitations or "generation_failure" in joined_limitations:
                return "I can't answer this reliably because answer generation failed during the run."
            if "verification failed" in joined_limitations or "verification_failure" in joined_limitations:
                return "I can't answer this reliably because answer verification failed during the run."
            return "I can't answer this reliably from the available evidence."
        return answer_result.answer_text
