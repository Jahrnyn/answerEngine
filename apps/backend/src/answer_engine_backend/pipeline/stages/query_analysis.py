import re

from answer_engine_backend.pipeline.models import QueryAnalysisResult


class QueryAnalysisStage:
    def execute(self, query: str) -> QueryAnalysisResult:
        normalized_query = self._normalize_query(query)
        lowered_query = normalized_query.lower()
        intent_type = self._detect_intent(lowered_query)
        requires_retrieval = self._determine_requires_retrieval(lowered_query, intent_type)
        variants = self._build_query_variants(normalized_query)

        return QueryAnalysisResult(
            normalized_query=normalized_query,
            intent_type=intent_type,
            requires_retrieval=requires_retrieval,
            query_variants=variants,
        )

    def _normalize_query(self, query: str) -> str:
        collapsed = " ".join(query.strip().split())
        normalized = re.sub(r"\s+([?.!,;:])", r"\1", collapsed)
        return normalized.strip('"').strip("'")

    def _detect_intent(self, lowered_query: str) -> str:
        if not lowered_query:
            return "unknown"
        if lowered_query.startswith(("what is", "what are", "who is", "who are", "where is")):
            return "lookup"
        if lowered_query.startswith(("explain", "describe", "how does", "why does", "why is")):
            return "explain"
        if lowered_query.endswith("?") or lowered_query.startswith(
            ("how ", "what ", "why ", "when ", "where ", "who ", "can ", "should ")
        ):
            return "question_answering"
        return "unknown"

    def _determine_requires_retrieval(self, lowered_query: str, intent_type: str) -> bool:
        if not lowered_query:
            return False

        direct_response_inputs = {
            "hi",
            "hello",
            "hey",
            "thanks",
            "thank you",
            "ok",
            "okay",
        }
        if lowered_query in direct_response_inputs:
            return False

        if intent_type in {"lookup", "question_answering", "explain"}:
            return True

        return True

    def _build_query_variants(self, normalized_query: str) -> list[str]:
        variants: list[str] = []
        seen: set[str] = set()

        def add_variant(value: str) -> None:
            candidate = value.strip()
            if candidate and candidate not in seen:
                variants.append(candidate)
                seen.add(candidate)

        add_variant(normalized_query)
        add_variant(normalized_query.rstrip("?"))
        add_variant(normalized_query.lower())

        return variants[:3]
