from __future__ import annotations

from answer_engine_backend.model_runtime import OllamaRuntime
from answer_engine_backend.pipeline.models import (
    AnswerPolicy,
    AnswerResult,
    ContextPack,
    StageModelConfig,
)


class AnswerGenerationStage:
    def __init__(self) -> None:
        self.runtime = OllamaRuntime()

    def execute(
        self,
        query: str,
        context_pack: ContextPack,
        answer_policy: AnswerPolicy,
        stage_model_config: StageModelConfig,
        generation_note: str | None = None,
    ) -> AnswerResult:
        prompt = self._build_prompt(query, context_pack, answer_policy, generation_note)
        generation = self.runtime.generate(stage_model_config, prompt)

        model_metadata = dict(generation.model_metadata)
        model_metadata.update(
            {
                "response_style": answer_policy.response_style,
                "context_chunk_count": len(context_pack.selected_chunks),
                "context_token_estimate": context_pack.token_estimate,
                "prompt_chars": len(prompt),
                "prompt_mode": "grounded_v1",
                "generation_note_applied": bool(generation_note),
            }
        )

        return AnswerResult(
            answer_text=generation.answer_text,
            token_usage=generation.token_usage,
            model_metadata=model_metadata,
        )

    def _build_prompt(
        self,
        query: str,
        context_pack: ContextPack,
        answer_policy: AnswerPolicy,
        generation_note: str | None,
    ) -> str:
        context_status = (
            "retrieved_context_available"
            if context_pack.selected_chunks
            else "no_retrieved_context_available"
        )
        prompt_parts = [
            "You are the Answer Engine.",
            "Answer the user using only the provided context.",
            "Do not invent facts that are not grounded in the context.",
            "If the context is weak or missing, say that the available evidence is insufficient.",
            "Do not include hidden reasoning or chain-of-thought in the answer.",
            f"Response style: {answer_policy.response_style}",
            f"Context status: {context_status}",
        ]
        if generation_note:
            prompt_parts.extend(["", "Revision note:", generation_note])

        prompt_parts.extend(
            [
                "",
                "User query:",
                query,
                "",
                "Structured context:",
                context_pack.structured_context,
                "",
                "Write a concise grounded answer for the user.",
            ]
        )
        return "\n".join(prompt_parts)
