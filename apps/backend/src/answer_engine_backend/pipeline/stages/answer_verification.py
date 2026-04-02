from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Callable

from answer_engine_backend.model_runtime import ModelRuntimeError, OllamaRuntime
from answer_engine_backend.pipeline.models import (
    AnswerPolicy,
    AnswerResult,
    ContextPack,
    ScopeInferenceResult,
    StageModelConfig,
    VerificationResult,
)
from answer_engine_backend.pipeline.stages.answer_generation import AnswerGenerationStage


@dataclass(frozen=True)
class VerificationStageOutcome:
    answer_result: AnswerResult
    verification_result: VerificationResult


@dataclass(frozen=True)
class VerificationAssessment:
    grounded: bool
    scope_consistency_ok: bool
    coverage_ok: bool
    adequacy_ok: bool
    uncertainty_flags: list[str]
    limitations: list[str]
    decision: str
    confidence_score: float


class AnswerVerificationStage:
    MIN_GROUNDED_OVERLAP = 0.18
    MIN_COVERAGE_OVERLAP = 0.2

    def __init__(self, answer_generation_stage: AnswerGenerationStage | None = None) -> None:
        self.runtime = OllamaRuntime()
        self.answer_generation_stage = answer_generation_stage or AnswerGenerationStage()

    def execute(
        self,
        query: str,
        answer_result: AnswerResult,
        context_pack: ContextPack,
        scope_inference: ScopeInferenceResult,
        answer_policy: AnswerPolicy,
        verification_stage_model: StageModelConfig,
        answer_generation_stage_model: StageModelConfig,
        on_regeneration_started: Callable[[], None] | None = None,
        regeneration_preview_sink: Callable[[str], None] | None = None,
    ) -> VerificationStageOutcome:
        initial_assessment = self._assess_candidate(
            query=query,
            answer_result=answer_result,
            context_pack=context_pack,
            scope_inference=scope_inference,
            answer_policy=answer_policy,
            verification_stage_model=verification_stage_model,
            regeneration_attempted=False,
            regeneration_allowed=answer_policy.allow_regeneration,
        )

        if (
            initial_assessment.decision == "regenerate"
            and answer_policy.allow_regeneration
            and context_pack.selected_chunks
        ):
            if on_regeneration_started is not None:
                on_regeneration_started()
            regenerated_answer = self.answer_generation_stage.execute(
                query,
                context_pack,
                answer_policy,
                answer_generation_stage_model,
                self._build_regeneration_note(initial_assessment),
                preview_sink=regeneration_preview_sink,
            )
            regenerated_answer.model_metadata["regeneration_attempt"] = 1

            regenerated_assessment = self._assess_candidate(
                query=query,
                answer_result=regenerated_answer,
                context_pack=context_pack,
                scope_inference=scope_inference,
                answer_policy=answer_policy,
                verification_stage_model=verification_stage_model,
                regeneration_attempted=True,
                regeneration_allowed=False,
            )
            final_decision = regenerated_assessment.decision
            if final_decision == "regenerate":
                final_decision = "limit" if context_pack.selected_chunks else "cannot_answer"

            return VerificationStageOutcome(
                answer_result=regenerated_answer,
                verification_result=VerificationResult(
                    grounded=regenerated_assessment.grounded,
                    scope_consistency_ok=regenerated_assessment.scope_consistency_ok,
                    coverage_ok=regenerated_assessment.coverage_ok,
                    adequacy_ok=regenerated_assessment.adequacy_ok,
                    uncertainty_flags=self._unique(
                        [*regenerated_assessment.uncertainty_flags, "regenerated_once"]
                    ),
                    limitations=regenerated_assessment.limitations,
                    decision=final_decision,
                    requires_regeneration=False,
                    regeneration_attempted=True,
                    confidence_score=regenerated_assessment.confidence_score,
                ),
            )

        return VerificationStageOutcome(
            answer_result=answer_result,
            verification_result=VerificationResult(
                grounded=initial_assessment.grounded,
                scope_consistency_ok=initial_assessment.scope_consistency_ok,
                coverage_ok=initial_assessment.coverage_ok,
                adequacy_ok=initial_assessment.adequacy_ok,
                uncertainty_flags=initial_assessment.uncertainty_flags,
                limitations=initial_assessment.limitations,
                decision=initial_assessment.decision,
                requires_regeneration=initial_assessment.decision == "regenerate",
                regeneration_attempted=False,
                confidence_score=initial_assessment.confidence_score,
            ),
        )

    def _assess_candidate(
        self,
        *,
        query: str,
        answer_result: AnswerResult,
        context_pack: ContextPack,
        scope_inference: ScopeInferenceResult,
        answer_policy: AnswerPolicy,
        verification_stage_model: StageModelConfig,
        regeneration_attempted: bool,
        regeneration_allowed: bool,
    ) -> VerificationAssessment:
        rule_assessment = self._evaluate_rules(
            query,
            answer_result,
            context_pack,
            scope_inference,
        )
        model_assessment = self._evaluate_with_model(
            query,
            answer_result,
            context_pack,
            scope_inference,
            answer_policy,
            verification_stage_model,
        )

        grounded = rule_assessment["grounded"]
        scope_consistency_ok = rule_assessment["scope_consistency_ok"]
        coverage_ok = rule_assessment["coverage_ok"]
        adequacy_ok = rule_assessment["adequacy_ok"]
        uncertainty_flags = list(rule_assessment["uncertainty_flags"])
        limitations = list(rule_assessment["limitations"])
        confidence_score = float(rule_assessment["confidence_score"])

        if model_assessment is not None:
            grounded = grounded and bool(model_assessment.get("grounded", grounded))
            scope_consistency_ok = scope_consistency_ok and bool(
                model_assessment.get("scope_consistency_ok", scope_consistency_ok)
            )
            coverage_ok = coverage_ok and bool(model_assessment.get("coverage_ok", coverage_ok))
            adequacy_ok = adequacy_ok and bool(
                model_assessment.get("adequacy_ok", adequacy_ok)
            )
            uncertainty_flags.extend(self._as_string_list(model_assessment.get("uncertainty_flags")))
            limitations.extend(self._as_string_list(model_assessment.get("limitations")))
            confidence_score = min(
                confidence_score,
                self._clamp_confidence(model_assessment.get("confidence_score"), confidence_score),
            )
        else:
            uncertainty_flags.append("verification_model_fallback_to_rules")

        uncertainty_flags = self._unique(uncertainty_flags)
        limitations = self._unique(limitations)

        decision = self._decide_outcome(
            grounded=grounded,
            scope_consistency_ok=scope_consistency_ok,
            coverage_ok=coverage_ok,
            adequacy_ok=adequacy_ok,
            regeneration_attempted=regeneration_attempted,
            regeneration_allowed=regeneration_allowed,
            has_context=bool(context_pack.selected_chunks),
        )
        confidence_score = self._finalize_confidence(
            grounded=grounded,
            scope_consistency_ok=scope_consistency_ok,
            coverage_ok=coverage_ok,
            adequacy_ok=adequacy_ok,
            base_confidence=confidence_score,
            decision=decision,
        )

        if not grounded and "answer_not_sufficiently_grounded" not in limitations:
            limitations.append("answer_not_sufficiently_grounded")
        if not scope_consistency_ok and "scope_consistency_not_confirmed" not in limitations:
            limitations.append("scope_consistency_not_confirmed")
        if not coverage_ok and "answer_does_not_fully_address_query" not in limitations:
            limitations.append("answer_does_not_fully_address_query")
        if not adequacy_ok and "answer_adequacy_is_limited" not in limitations:
            limitations.append("answer_adequacy_is_limited")

        return VerificationAssessment(
            grounded=grounded,
            scope_consistency_ok=scope_consistency_ok,
            coverage_ok=coverage_ok,
            adequacy_ok=adequacy_ok,
            uncertainty_flags=self._unique(uncertainty_flags),
            limitations=self._unique(limitations),
            decision=decision,
            confidence_score=confidence_score,
        )

    def _evaluate_rules(
        self,
        query: str,
        answer_result: AnswerResult,
        context_pack: ContextPack,
        scope_inference: ScopeInferenceResult,
    ) -> dict[str, object]:
        answer_tokens = self._content_tokens(answer_result.answer_text)
        context_tokens = self._content_tokens(context_pack.structured_context)
        query_tokens = self._content_tokens(query)

        grounded_overlap = self._overlap_ratio(answer_tokens, context_tokens)
        coverage_overlap = self._overlap_ratio(query_tokens, answer_tokens)
        grounded = bool(context_pack.selected_chunks) and grounded_overlap >= self.MIN_GROUNDED_OVERLAP
        scope_consistency_ok = scope_inference.primary_scope is not None and scope_inference.status in {
            "ok",
            "fallback",
        }
        coverage_ok = coverage_overlap >= self.MIN_COVERAGE_OVERLAP or self._contains_limitation_phrase(
            answer_result.answer_text
        )
        adequacy_ok = coverage_ok and len(answer_tokens) >= 4

        uncertainty_flags: list[str] = []
        limitations: list[str] = []
        if not context_pack.selected_chunks:
            uncertainty_flags.append("no_retrieved_context")
            limitations.append("no_retrieved_context_available")
        if grounded_overlap < self.MIN_GROUNDED_OVERLAP:
            uncertainty_flags.append("weak_grounding_signal")
        if scope_inference.primary_scope is None:
            uncertainty_flags.append("no_validated_scope")
            limitations.append("no_validated_scope_available")
        if coverage_overlap < self.MIN_COVERAGE_OVERLAP:
            uncertainty_flags.append("weak_query_coverage_signal")

        confidence = min(
            0.95,
            max(
                0.05,
                0.35
                + (0.35 * grounded_overlap)
                + (0.2 * coverage_overlap)
                + (0.1 if scope_consistency_ok else 0.0),
            ),
        )

        return {
            "grounded": grounded,
            "scope_consistency_ok": scope_consistency_ok,
            "coverage_ok": coverage_ok,
            "adequacy_ok": adequacy_ok,
            "uncertainty_flags": uncertainty_flags,
            "limitations": limitations,
            "confidence_score": round(confidence, 3),
        }

    def _evaluate_with_model(
        self,
        query: str,
        answer_result: AnswerResult,
        context_pack: ContextPack,
        scope_inference: ScopeInferenceResult,
        answer_policy: AnswerPolicy,
        verification_stage_model: StageModelConfig,
    ) -> dict[str, object] | None:
        prompt = self._build_verification_prompt(
            query,
            answer_result,
            context_pack,
            scope_inference,
            answer_policy,
        )
        try:
            generation = self.runtime.generate(verification_stage_model, prompt)
        except ModelRuntimeError:
            return None
        return self._parse_verification_json(generation.answer_text)

    def _build_verification_prompt(
        self,
        query: str,
        answer_result: AnswerResult,
        context_pack: ContextPack,
        scope_inference: ScopeInferenceResult,
        answer_policy: AnswerPolicy,
    ) -> str:
        scope_summary = "none"
        if scope_inference.primary_scope is not None:
            parts = [
                scope_inference.primary_scope.workspace,
                scope_inference.primary_scope.domain,
            ]
            for value in (
                scope_inference.primary_scope.project,
                scope_inference.primary_scope.client,
                scope_inference.primary_scope.module,
            ):
                if value:
                    parts.append(value)
            scope_summary = "/".join(parts)

        return "\n".join(
            [
                "You are verifying a candidate answer for the Answer Engine.",
                "Return JSON only.",
                "Be conservative and evaluate whether the answer is grounded in the provided context and stays within scope.",
                "Allowed decision values: keep, limit, regenerate, cannot_answer.",
                f"Verification profile: {answer_policy.verification_profile}",
                "",
                "User query:",
                query,
                "",
                "Validated scope:",
                scope_summary,
                "",
                "Structured context:",
                context_pack.structured_context,
                "",
                "Candidate answer:",
                answer_result.answer_text,
                "",
                "Return exactly this JSON shape:",
                '{"grounded": true, "scope_consistency_ok": true, "coverage_ok": true, "adequacy_ok": true, "uncertainty_flags": [], "limitations": [], "decision": "keep", "confidence_score": 0.0}',
            ]
        )

    def _parse_verification_json(self, text: str) -> dict[str, object] | None:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match is None:
            return None
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    def _build_regeneration_note(self, assessment: VerificationAssessment) -> str:
        issues = ", ".join(assessment.limitations[:4]) or "improve grounding and coverage"
        return (
            "Revise the answer so it is more directly supported by the provided context, "
            "stays within scope, and addresses the user query more clearly. "
            f"Focus on these issues: {issues}."
        )

    def _decide_outcome(
        self,
        *,
        grounded: bool,
        scope_consistency_ok: bool,
        coverage_ok: bool,
        adequacy_ok: bool,
        regeneration_attempted: bool,
        regeneration_allowed: bool,
        has_context: bool,
    ) -> str:
        if not has_context:
            return "cannot_answer"
        if grounded and scope_consistency_ok and coverage_ok and adequacy_ok:
            return "keep"
        if regeneration_allowed and not regeneration_attempted and (
            not grounded or not coverage_ok or not adequacy_ok
        ):
            return "regenerate"
        if grounded and scope_consistency_ok:
            return "limit"
        return "cannot_answer"

    def _finalize_confidence(
        self,
        *,
        grounded: bool,
        scope_consistency_ok: bool,
        coverage_ok: bool,
        adequacy_ok: bool,
        base_confidence: float,
        decision: str,
    ) -> float:
        confidence = base_confidence
        if not grounded:
            confidence = min(confidence, 0.32)
        if not scope_consistency_ok:
            confidence = min(confidence, 0.38)
        if not coverage_ok:
            confidence = min(confidence, 0.48)
        if not adequacy_ok:
            confidence = min(confidence, 0.56)
        if decision == "limit":
            confidence = min(confidence, 0.62)
        if decision == "cannot_answer":
            confidence = min(confidence, 0.22)
        return round(max(0.0, min(1.0, confidence)), 3)

    def _content_tokens(self, value: str) -> set[str]:
        tokens = set(re.findall(r"[a-z0-9]{3,}", value.lower()))
        return {token for token in tokens if token not in self._stopwords()}

    def _overlap_ratio(self, left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        return len(left.intersection(right)) / max(1, len(left))

    def _contains_limitation_phrase(self, value: str) -> bool:
        lowered = value.lower()
        return any(
            phrase in lowered
            for phrase in (
                "insufficient",
                "cannot answer",
                "can't answer",
                "not enough evidence",
                "available evidence",
            )
        )

    def _as_string_list(self, value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    def _clamp_confidence(self, value: object, default: float) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return default
        return max(0.0, min(1.0, numeric))

    def _unique(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for value in values:
            if value and value not in seen:
                seen.add(value)
                ordered.append(value)
        return ordered

    def _stopwords(self) -> set[str]:
        return {
            "about",
            "according",
            "after",
            "against",
            "answer",
            "available",
            "because",
            "between",
            "could",
            "from",
            "have",
            "into",
            "only",
            "that",
            "their",
            "there",
            "these",
            "this",
            "through",
            "using",
            "user",
            "with",
            "within",
            "would",
        }
