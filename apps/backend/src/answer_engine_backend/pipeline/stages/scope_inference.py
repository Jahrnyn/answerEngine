from __future__ import annotations

import re
from dataclasses import dataclass

from answer_engine_backend.cfhee_client import CfheeClient, CfheeClientError
from answer_engine_backend.pipeline.models import (
    QueryAnalysisResult,
    ScopeInferenceResult,
    ScopeReference,
)
from answer_engine_backend.settings import get_settings


@dataclass(frozen=True)
class RankedScopeCandidate:
    scope: ScopeReference
    heuristic_score: float


class ScopeInferenceStage:
    MAX_HEURISTIC_CANDIDATES = 12
    MAX_RANKED_CANDIDATES = 6
    MAX_VALIDATED_SCOPES = 3
    MAX_MAIN_RETRIEVAL_SCOPES = 2
    VALIDATION_TOP_K = 2
    MIN_ACCEPTED_VALIDATION_SCORE = 0.35

    def __init__(self, cfhee_client: CfheeClient | None = None) -> None:
        self.cfhee_client = cfhee_client or CfheeClient(get_settings())

    def execute(self, query_analysis: QueryAnalysisResult) -> ScopeInferenceResult:
        try:
            available_scopes = self._load_available_scopes()
            heuristic_candidates = self._filter_candidates(query_analysis, available_scopes)
            ranked_candidates = heuristic_candidates[: self.MAX_RANKED_CANDIDATES]
            validation_scores = self._validate_candidates(
                query_analysis.normalized_query,
                ranked_candidates[: self.MAX_VALIDATED_SCOPES],
            )
        except CfheeClientError as error:
            return ScopeInferenceResult(
                status=error.category,
                primary_scope=None,
                secondary_scopes=[],
                candidate_scopes=[],
                rejected_scopes=[],
                confidence_scores={},
                validation_scores={},
                fallback_applied=False,
                failure_reason=error.category,
            )

        accepted_candidates = [
            candidate
            for candidate in ranked_candidates[: self.MAX_VALIDATED_SCOPES]
            if validation_scores.get(self._scope_id(candidate.scope), 0.0)
            >= self.MIN_ACCEPTED_VALIDATION_SCORE
        ]
        if accepted_candidates:
            return self._build_result(
                status="ok",
                heuristic_candidates=heuristic_candidates,
                ranked_candidates=ranked_candidates,
                validation_scores=validation_scores,
                accepted_candidates=accepted_candidates,
                fallback_applied=False,
                failure_reason=None,
            )

        fallback_candidate = self._attempt_fallback(
            query_analysis.normalized_query,
            ranked_candidates,
            validation_scores,
        )
        if fallback_candidate is not None:
            fallback_scope_id = self._scope_id(fallback_candidate.scope)
            accepted_candidates = [fallback_candidate]
            if fallback_scope_id not in validation_scores:
                validation_scores[fallback_scope_id] = self._validate_scope(
                    query_analysis.normalized_query,
                    fallback_candidate.scope,
                )
            return self._build_result(
                status="fallback",
                heuristic_candidates=heuristic_candidates,
                ranked_candidates=ranked_candidates,
                validation_scores=validation_scores,
                accepted_candidates=accepted_candidates,
                fallback_applied=True,
                failure_reason=None,
            )

        return self._build_result(
            status="no_reliable_scope",
            heuristic_candidates=heuristic_candidates,
            ranked_candidates=ranked_candidates,
            validation_scores=validation_scores,
            accepted_candidates=[],
            fallback_applied=bool(ranked_candidates),
            failure_reason="no_reliable_scope",
        )

    def _load_available_scopes(self) -> list[ScopeReference]:
        response = self.cfhee_client.get_scope_tree()
        scopes = self._flatten_scopes(response)
        if scopes:
            return scopes

        values_response = self.cfhee_client.get_scope_values()
        return self._flatten_scopes(values_response)

    def _flatten_scopes(self, payload: object) -> list[ScopeReference]:
        collected: list[ScopeReference] = []
        seen: set[str] = set()

        def visit(node: object, context: dict[str, str | None]) -> None:
            if isinstance(node, dict):
                next_context = dict(context)
                for key in ("workspace", "domain", "project", "client", "module"):
                    value = node.get(key)
                    if isinstance(value, str) and value.strip():
                        next_context[key] = value.strip()

                handled_plural_keys = {
                    "workspaces",
                    "domains",
                    "projects",
                    "clients",
                    "modules",
                }
                for plural_key, singular_key in (
                    ("workspaces", "workspace"),
                    ("domains", "domain"),
                    ("projects", "project"),
                    ("clients", "client"),
                    ("modules", "module"),
                ):
                    nested_values = node.get(plural_key)
                    if isinstance(nested_values, list):
                        for item in nested_values:
                            child_context = dict(next_context)
                            if isinstance(item, dict):
                                raw_name = item.get("name")
                                if isinstance(raw_name, str) and raw_name.strip():
                                    child_context[singular_key] = raw_name.strip()
                            visit(item, child_context)

                if next_context.get("workspace") and next_context.get("domain"):
                    scope = ScopeReference(
                        workspace=next_context["workspace"] or "",
                        domain=next_context["domain"] or "",
                        project=next_context.get("project"),
                        client=next_context.get("client"),
                        module=next_context.get("module"),
                    )
                    scope_id = self._scope_id(scope)
                    if scope_id not in seen:
                        collected.append(scope)
                        seen.add(scope_id)

                for key, value in node.items():
                    if key in handled_plural_keys:
                        continue
                    if isinstance(value, (dict, list)):
                        visit(value, next_context)

            elif isinstance(node, list):
                for item in node:
                    visit(item, context)

        visit(payload, {})
        return sorted(collected, key=self._scope_sort_key)

    def _filter_candidates(
        self,
        query_analysis: QueryAnalysisResult,
        available_scopes: list[ScopeReference],
    ) -> list[RankedScopeCandidate]:
        query_tokens = self._collect_query_tokens(query_analysis)
        ranked_candidates: list[RankedScopeCandidate] = []

        for scope in available_scopes:
            heuristic_score = self._score_scope(scope, query_tokens)
            if heuristic_score <= 0:
                continue
            ranked_candidates.append(
                RankedScopeCandidate(scope=scope, heuristic_score=heuristic_score)
            )

        ranked_candidates.sort(
            key=lambda candidate: (
                -candidate.heuristic_score,
                self._scope_sort_key(candidate.scope),
            )
        )
        return ranked_candidates[: self.MAX_HEURISTIC_CANDIDATES]

    def _collect_query_tokens(self, query_analysis: QueryAnalysisResult) -> set[str]:
        tokens: set[str] = set()
        for value in [query_analysis.normalized_query, *query_analysis.query_variants]:
            tokens.update(self._tokenize(value))
        return tokens

    def _score_scope(self, scope: ScopeReference, query_tokens: set[str]) -> float:
        if not query_tokens:
            return 0.0

        score = 0.0
        component_weights = (
            ("workspace", scope.workspace, 0.5),
            ("domain", scope.domain, 1.0),
            ("project", scope.project, 1.5),
            ("client", scope.client, 2.0),
            ("module", scope.module, 2.5),
        )

        for _, raw_value, weight in component_weights:
            if not raw_value:
                continue
            value_tokens = self._tokenize(raw_value)
            if not value_tokens:
                continue

            overlap = query_tokens.intersection(value_tokens)
            if overlap:
                score += len(overlap) * weight
                continue

            normalized_value = self._normalize_text(raw_value)
            if any(token in normalized_value for token in query_tokens):
                score += 0.35 * weight

        return round(score, 3)

    def _validate_candidates(
        self,
        query: str,
        candidates: list[RankedScopeCandidate],
    ) -> dict[str, float]:
        scores: dict[str, float] = {}
        for candidate in candidates:
            scores[self._scope_id(candidate.scope)] = self._validate_scope(query, candidate.scope)
        return scores

    def _validate_scope(self, query: str, scope: ScopeReference) -> float:
        response = self.cfhee_client.query_retrieval(
            {
                "query": query,
                "scope": scope.model_dump(),
                "top_k": self.VALIDATION_TOP_K,
                "include_chunks": True,
            }
        )
        results = response.get("results", [])
        result_count = response.get("result_count")

        if not isinstance(results, list) or (result_count == 0 and not results):
            return 0.0

        similarity_scores: list[float] = []
        for result in results:
            if not isinstance(result, dict):
                continue
            similarity_value = result.get("similarity_score")
            if isinstance(similarity_value, (int, float)):
                similarity_scores.append(float(similarity_value))

        if similarity_scores:
            return round(min(1.0, max(similarity_scores)), 3)

        return 0.5 if results else 0.0

    def _attempt_fallback(
        self,
        query: str,
        ranked_candidates: list[RankedScopeCandidate],
        validation_scores: dict[str, float],
    ) -> RankedScopeCandidate | None:
        if not ranked_candidates:
            return None

        base_candidate = ranked_candidates[0]
        fallback_scope = self._broaden_scope_once(base_candidate.scope)
        if fallback_scope is None:
            return None

        fallback_score = self._validate_scope(query, fallback_scope)
        fallback_scope_id = self._scope_id(fallback_scope)
        validation_scores[fallback_scope_id] = fallback_score

        if fallback_score < self.MIN_ACCEPTED_VALIDATION_SCORE:
            return None

        return RankedScopeCandidate(
            scope=fallback_scope,
            heuristic_score=max(base_candidate.heuristic_score - 0.25, 0.0),
        )

    def _broaden_scope_once(self, scope: ScopeReference) -> ScopeReference | None:
        if scope.module:
            return ScopeReference(
                workspace=scope.workspace,
                domain=scope.domain,
                project=scope.project,
                client=scope.client,
                module=None,
            )
        if scope.client:
            return ScopeReference(
                workspace=scope.workspace,
                domain=scope.domain,
                project=scope.project,
                client=None,
                module=None,
            )
        if scope.project:
            return ScopeReference(
                workspace=scope.workspace,
                domain=scope.domain,
                project=None,
                client=None,
                module=None,
            )
        return None

    def _build_result(
        self,
        *,
        status: str,
        heuristic_candidates: list[RankedScopeCandidate],
        ranked_candidates: list[RankedScopeCandidate],
        validation_scores: dict[str, float],
        accepted_candidates: list[RankedScopeCandidate],
        fallback_applied: bool,
        failure_reason: str | None,
    ) -> ScopeInferenceResult:
        accepted_scope_ids = {
            self._scope_id(candidate.scope)
            for candidate in accepted_candidates[: self.MAX_MAIN_RETRIEVAL_SCOPES]
        }
        carried_candidates = accepted_candidates[: self.MAX_MAIN_RETRIEVAL_SCOPES]
        rejected_scopes = [
            candidate.scope
            for candidate in heuristic_candidates
            if self._scope_id(candidate.scope) not in accepted_scope_ids
        ]
        confidence_scores = {
            self._scope_id(candidate.scope): candidate.heuristic_score
            for candidate in heuristic_candidates
        }

        primary_scope = carried_candidates[0].scope if carried_candidates else None
        secondary_scopes = [candidate.scope for candidate in carried_candidates[1:]]

        return ScopeInferenceResult(
            status=status,
            primary_scope=primary_scope,
            secondary_scopes=secondary_scopes,
            candidate_scopes=[candidate.scope for candidate in heuristic_candidates],
            rejected_scopes=rejected_scopes,
            confidence_scores=confidence_scores,
            validation_scores=validation_scores,
            fallback_applied=fallback_applied,
            failure_reason=failure_reason,
        )

    def _scope_id(self, scope: ScopeReference) -> str:
        parts = [scope.workspace, scope.domain]
        for value in (scope.project, scope.client, scope.module):
            if value:
                parts.append(value)
        return "/".join(parts)

    def _scope_sort_key(self, scope: ScopeReference) -> tuple[int, str]:
        specificity = sum(1 for value in (scope.project, scope.client, scope.module) if value)
        return (-specificity, self._scope_id(scope))

    def _normalize_text(self, value: str) -> str:
        return " ".join(re.findall(r"[a-z0-9]+", value.lower()))

    def _tokenize(self, value: str | None) -> set[str]:
        if not value:
            return set()
        return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) >= 2}
