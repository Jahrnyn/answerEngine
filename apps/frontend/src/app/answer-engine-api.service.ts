import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export type ExecuteRunHttpError = {
  message?: string;
  category?: string;
  endpoint?: string;
};

export type RunErrorEntry = {
  stage: string;
  category: string;
  message: string;
  endpoint?: string | null;
};

export type ScopeReference = {
  workspace: string;
  domain: string;
  project?: string | null;
  client?: string | null;
  module?: string | null;
};

export type SourceReference = {
  document_id: string;
  chunk_id: string;
  position: number;
};

export type StageModelConfig = {
  stage_id: string;
  provider_id: string;
  model_id: string;
  parameters: Record<string, string>;
};

export type RetrievedChunk = {
  document_id: string;
  chunk_id: string;
  content: string;
  score: number;
  metadata: Record<string, string>;
};

export type ScopeInferenceResult = {
  status: string;
  primary_scope: ScopeReference | null;
  secondary_scopes: ScopeReference[];
  candidate_scopes: ScopeReference[];
  rejected_scopes: ScopeReference[];
  confidence_scores: Record<string, number>;
  validation_scores: Record<string, number>;
  fallback_applied: boolean;
  failure_reason?: string | null;
};

export type RetrievalRound = {
  scope: ScopeReference;
  top_k: number;
  strategy_type: string;
};

export type RetrievalPlan = {
  rounds: RetrievalRound[];
  fallback_rules: Record<string, string>;
};

export type RetrievalRoundResult = {
  scope: ScopeReference;
  status: string;
  result_count: number;
  chunks: RetrievedChunk[];
  failure_reason?: string | null;
};

export type RetrievalResult = {
  status: string;
  results_by_round: RetrievalRoundResult[];
  aggregated_results: RetrievedChunk[];
  failure_reason?: string | null;
};

export type ContextPack = {
  selected_chunks: RetrievedChunk[];
  source_mapping: SourceReference[];
  structured_context: string;
  token_estimate: number;
};

export type AnswerResult = {
  answer_text: string;
  token_usage: Record<string, number>;
  model_metadata: Record<string, string | number | boolean>;
};

export type VerificationResult = {
  grounded: boolean;
  scope_consistency_ok: boolean;
  coverage_ok: boolean;
  adequacy_ok: boolean;
  limitations: string[];
  uncertainty_flags: string[];
  decision: string;
  requires_regeneration: boolean;
  regeneration_attempted: boolean;
  confidence_score: number;
};

export type FinalResponse = {
  answer_text: string;
  certainty: string;
  limitations: string[];
  sources: SourceReference[];
  inferred_scopes: ScopeReference[];
  verification_summary: Record<string, string | boolean | number>;
  trace_id: string;
};

export type TimingInfo = {
  total_time_ms: number;
  stage_times: Record<string, number>;
};

export type AnswerRunResponse = {
  id: string;
  query: string;
  stage_model_routing: StageModelConfig[];
  scope_inference: ScopeInferenceResult;
  retrieval_plan: RetrievalPlan;
  retrieval_result: RetrievalResult;
  context_pack: ContextPack;
  answer_result: AnswerResult;
  final_response: FinalResponse;
  verification_result: VerificationResult;
  timings: TimingInfo;
  errors: RunErrorEntry[];
};

@Injectable({
  providedIn: 'root',
})
export class AnswerEngineApiService {
  private readonly http = inject(HttpClient);

  executeRun(query: string): Observable<AnswerRunResponse> {
    return this.http.post<AnswerRunResponse>('/runs/execute', { query });
  }
}
