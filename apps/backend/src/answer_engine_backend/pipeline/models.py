from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_run_id() -> str:
    return f"run-{uuid4().hex}"


class ExecuteRunRequest(BaseModel):
    query: str = Field(min_length=1)


class QueryAnalysisResult(BaseModel):
    normalized_query: str
    intent_type: str
    requires_retrieval: bool
    query_variants: list[str] = Field(default_factory=list)


class AnswerPolicy(BaseModel):
    retrieval_required: bool
    max_retrieval_rounds: int
    default_top_k: int
    allow_multi_scope: bool
    allow_regeneration: bool
    verification_profile: str
    response_style: str


class StageModelConfig(BaseModel):
    stage_id: str
    provider_id: str
    model_id: str
    parameters: dict[str, str] = Field(default_factory=dict)


class ScopeReference(BaseModel):
    workspace: str
    domain: str
    project: str | None = None
    client: str | None = None
    module: str | None = None


class ScopeInferenceResult(BaseModel):
    status: str = "ok"
    primary_scope: ScopeReference | None = None
    secondary_scopes: list[ScopeReference] = Field(default_factory=list)
    candidate_scopes: list[ScopeReference] = Field(default_factory=list)
    rejected_scopes: list[ScopeReference] = Field(default_factory=list)
    confidence_scores: dict[str, float] = Field(default_factory=dict)
    validation_scores: dict[str, float] = Field(default_factory=dict)
    fallback_applied: bool = False
    failure_reason: str | None = None


class RetrievalRound(BaseModel):
    scope: ScopeReference
    top_k: int
    strategy_type: str


class RetrievalPlan(BaseModel):
    rounds: list[RetrievalRound]
    fallback_rules: dict[str, str] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    document_id: str
    chunk_id: str
    content: str
    score: float
    metadata: dict[str, str] = Field(default_factory=dict)


class RetrievalRoundResult(BaseModel):
    scope: ScopeReference
    status: str = "ok"
    result_count: int = 0
    chunks: list[RetrievedChunk]


class RetrievalResult(BaseModel):
    status: str = "ok"
    results_by_round: list[RetrievalRoundResult]
    aggregated_results: list[RetrievedChunk]
    failure_reason: str | None = None


class SourceReference(BaseModel):
    document_id: str
    chunk_id: str
    position: int


class ContextPack(BaseModel):
    selected_chunks: list[RetrievedChunk]
    source_mapping: list[SourceReference]
    structured_context: str
    token_estimate: int


class AnswerResult(BaseModel):
    answer_text: str
    token_usage: dict[str, int] = Field(default_factory=dict)
    model_metadata: dict[str, str] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    grounded: bool
    scope_consistency_ok: bool
    coverage_ok: bool
    adequacy_ok: bool
    uncertainty_flags: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    decision: str
    requires_regeneration: bool
    confidence_score: float


class FinalResponse(BaseModel):
    answer_text: str
    sources: list[SourceReference]
    inferred_scopes: list[ScopeReference]
    certainty: str
    limitations: list[str]
    verification_summary: dict[str, str | bool | float]
    trace_id: str


class TimingInfo(BaseModel):
    total_time_ms: int
    stage_times: dict[str, int]


class AnswerRun(BaseModel):
    id: str
    query: str
    created_at: datetime
    answer_policy: AnswerPolicy
    stage_model_routing: list[StageModelConfig] = Field(default_factory=list)
    query_analysis: QueryAnalysisResult
    scope_inference: ScopeInferenceResult
    retrieval_plan: RetrievalPlan
    retrieval_result: RetrievalResult
    context_pack: ContextPack
    answer_result: AnswerResult
    verification_result: VerificationResult
    final_response: FinalResponse
    timings: TimingInfo
    errors: list[str] = Field(default_factory=list)


class StageTimer:
    def __init__(self) -> None:
        self._started_at = perf_counter()
        self._stage_started_at = self._started_at
        self.stage_times: dict[str, int] = {}

    def start_stage(self) -> None:
        self._stage_started_at = perf_counter()

    def end_stage(self, stage_name: str) -> None:
        elapsed_ms = int((perf_counter() - self._stage_started_at) * 1000)
        self.stage_times[stage_name] = elapsed_ms

    def build(self) -> TimingInfo:
        total_ms = int((perf_counter() - self._started_at) * 1000)
        return TimingInfo(total_time_ms=total_ms, stage_times=self.stage_times)
