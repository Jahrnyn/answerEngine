from answer_engine_backend.pipeline.models import (
    AnswerPolicy,
    AnswerResult,
    ContextPack,
    VerificationResult,
)


class AnswerVerificationStage:
    def execute(
        self,
        answer_result: AnswerResult,
        context_pack: ContextPack,
        answer_policy: AnswerPolicy,
    ) -> VerificationResult:
        limitations: list[str] = []
        if not context_pack.selected_chunks:
            limitations.append("No retrieved evidence was available in the stub pipeline.")

        return VerificationResult(
            grounded=bool(context_pack.selected_chunks),
            scope_consistency_ok=True,
            coverage_ok=True,
            adequacy_ok=True,
            uncertainty_flags=[],
            limitations=limitations,
            decision="keep",
            requires_regeneration=False,
            confidence_score=0.88 if answer_policy.verification_profile == "v1_stub" else 0.5,
        )
