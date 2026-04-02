import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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

export type VerificationResult = {
  decision: string;
  limitations: string[];
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

export type AnswerRunResponse = {
  id: string;
  query: string;
  final_response: FinalResponse;
  verification_result: VerificationResult;
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
