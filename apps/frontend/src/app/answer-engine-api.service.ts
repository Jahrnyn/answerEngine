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

export type QueryAnalysisResult = {
  normalized_query: string;
  intent_type: string;
  requires_retrieval: boolean;
  query_variants: string[];
};

export type AnswerPolicy = {
  retrieval_required: boolean;
  max_retrieval_rounds: number;
  default_top_k: number;
  allow_multi_scope: boolean;
  allow_regeneration: boolean;
  verification_profile: string;
  response_style: string;
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

export type RunEvent = {
  run_id: string;
  event_type: string;
  stage_id?: string | null;
  timestamp: string;
  message?: string | null;
  preview_text?: string | null;
  summary: Record<string, unknown>;
};

export type AnswerRunResponse = {
  id: string;
  query: string;
  created_at?: string;
  answer_policy: AnswerPolicy;
  query_analysis: QueryAnalysisResult;
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
  events: RunEvent[];
};

export type StreamRunCallbacks = {
  onEvent?: (event: RunEvent) => void;
};

@Injectable({
  providedIn: 'root',
})
export class AnswerEngineApiService {
  private readonly http = inject(HttpClient);

  executeRun(query: string): Observable<AnswerRunResponse> {
    return this.http.post<AnswerRunResponse>('/runs/execute', { query });
  }

  async streamRun(query: string, callbacks: StreamRunCallbacks = {}): Promise<AnswerRunResponse> {
    const response = await fetch('/runs/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new StreamRunHttpError(await this.buildStreamErrorDetail(response), response.status);
    }

    if (!response.body) {
      throw new Error('Streaming response body is not available.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let terminalEvent: RunEvent | null = null;
    const events: RunEvent[] = [];

    try {
      while (terminalEvent === null) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const parsed = this.consumeEventBlocks(buffer);
        buffer = parsed.remainder;

        for (const event of parsed.events) {
          events.push(event);
          callbacks.onEvent?.(event);

          if (event.event_type === 'run_completed' || event.event_type === 'run_failed') {
            terminalEvent = event;
            break;
          }
        }
      }

      buffer += decoder.decode();
      if (terminalEvent === null && buffer.trim().length > 0) {
        const parsed = this.consumeEventBlocks(buffer);
        for (const event of parsed.events) {
          events.push(event);
          callbacks.onEvent?.(event);
          if (event.event_type === 'run_completed' || event.event_type === 'run_failed') {
            terminalEvent = event;
            break;
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    if (!terminalEvent) {
      throw new Error('Run stream closed without a terminal event.');
    }

    const finalRun = terminalEvent.summary['final_run'];
    if (!this.isAnswerRunResponse(finalRun)) {
      if (terminalEvent.event_type === 'run_failed') {
        throw new StreamRunTerminalError(terminalEvent);
      }

      throw new Error('Run stream completed without a final run payload.');
    }

    return {
      ...finalRun,
      events,
    };
  }

  private consumeEventBlocks(buffer: string): { events: RunEvent[]; remainder: string } {
    const events: RunEvent[] = [];
    const blocks = buffer.split(/\r?\n\r?\n/);
    const remainder = blocks.pop() ?? '';

    for (const block of blocks) {
      const event = this.parseEventBlock(block);
      if (event) {
        events.push(event);
      }
    }

    return { events, remainder };
  }

  private parseEventBlock(block: string): RunEvent | null {
    const lines = block
      .split(/\r?\n/)
      .map((line) => line.trimEnd())
      .filter((line) => line.length > 0);

    if (lines.length === 0) {
      return null;
    }

    const dataLines: string[] = [];
    for (const line of lines) {
      if (line.startsWith('data:')) {
        dataLines.push(line.slice(5).trimStart());
      }
    }

    if (dataLines.length === 0) {
      return null;
    }

    return JSON.parse(dataLines.join('\n')) as RunEvent;
  }

  private async buildStreamErrorDetail(response: Response): Promise<ExecuteRunHttpError | string> {
    const contentType = response.headers.get('content-type') ?? '';

    if (contentType.includes('application/json')) {
      const payload = (await response.json()) as { detail?: ExecuteRunHttpError | string };
      return payload.detail ?? `HTTP ${response.status}`;
    }

    const text = await response.text();
    return text || `HTTP ${response.status}`;
  }

  private isAnswerRunResponse(value: unknown): value is Omit<AnswerRunResponse, 'events'> {
    if (!value || typeof value !== 'object') {
      return false;
    }

    const candidate = value as Record<string, unknown>;
    return (
      typeof candidate['id'] === 'string' &&
      typeof candidate['query'] === 'string' &&
      typeof candidate['final_response'] === 'object' &&
      typeof candidate['verification_result'] === 'object'
    );
  }
}

export class StreamRunHttpError extends Error {
  constructor(
    readonly detail: ExecuteRunHttpError | string,
    readonly status: number,
  ) {
    super(typeof detail === 'string' ? detail : detail.message || 'Backend stream request failed.');
  }
}

export class StreamRunTerminalError extends Error {
  constructor(readonly terminalEvent: RunEvent) {
    super(terminalEvent.message || 'Run failed before a final run payload was available.');
  }
}
