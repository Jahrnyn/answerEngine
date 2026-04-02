import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import {
  AnswerEngineApiService,
  AnswerRunResponse,
  ContextPack,
  ExecuteRunHttpError,
  RetrievalPlan,
  RetrievalResult,
  RunErrorEntry,
  ScopeInferenceResult,
  ScopeReference,
  StageModelConfig,
  VerificationResult,
} from './answer-engine-api.service';

type RequestErrorState = {
  message: string;
  detail?: string;
};

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule, TitleCasePipe],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  private readonly api = inject(AnswerEngineApiService);

  question = '';
  isSubmitting = false;
  inspectOpen = false;
  readonly runningStatus = 'Running the bounded answer pipeline...';

  runResult: AnswerRunResponse | null = null;
  requestError: RequestErrorState | null = null;

  get hasRunResult(): boolean {
    return this.runResult !== null;
  }

  get isSubmitDisabled(): boolean {
    return this.isSubmitting || this.question.trim().length === 0;
  }

  get answerText(): string {
    return this.runResult?.final_response.answer_text || 'No final answer returned.';
  }

  get certaintyLabel(): string | null {
    return this.runResult?.final_response.certainty ?? null;
  }

  get limitations(): string[] {
    if (!this.runResult) {
      return [];
    }

    const finalLimitations = this.runResult.final_response.limitations ?? [];
    if (finalLimitations.length > 0) {
      return finalLimitations;
    }

    return this.runResult.verification_result.limitations ?? [];
  }

  get verificationDecision(): string {
    return this.runResult?.verification_result.decision ?? 'n/a';
  }

  get traceId(): string {
    return this.runResult?.final_response.trace_id ?? 'n/a';
  }

  get runErrors(): RunErrorEntry[] {
    return this.runResult?.errors ?? [];
  }

  get scopeInference(): ScopeInferenceResult | null {
    return this.runResult?.scope_inference ?? null;
  }

  get retrievalPlan(): RetrievalPlan | null {
    return this.runResult?.retrieval_plan ?? null;
  }

  get retrievalResult(): RetrievalResult | null {
    return this.runResult?.retrieval_result ?? null;
  }

  get contextPack(): ContextPack | null {
    return this.runResult?.context_pack ?? null;
  }

  get verificationResult(): VerificationResult | null {
    return this.runResult?.verification_result ?? null;
  }

  get stageModelRouting(): StageModelConfig[] {
    return this.runResult?.stage_model_routing ?? [];
  }

  get selectedChunkPreview(): string[] {
    return (this.contextPack?.selected_chunks ?? [])
      .slice(0, 3)
      .map((chunk) => `${this.chunkLabel(chunk.document_id, chunk.chunk_id)} — ${this.previewText(chunk.content, 180)}`);
  }

  get sourceMappingPreview(): string[] {
    return (this.contextPack?.source_mapping ?? [])
      .slice(0, 5)
      .map((source) => `${this.chunkLabel(source.document_id, source.chunk_id)} · position ${source.position}`);
  }

  get retrievalRoundSummary(): string[] {
    return (this.retrievalResult?.results_by_round ?? []).map((round, index) => {
      const failure = round.failure_reason ? ` · ${round.failure_reason}` : '';
      return `Round ${index + 1}: ${this.scopeLabel(round.scope)} · ${round.status} · ${round.result_count} chunk(s)${failure}`;
    });
  }

  get secondaryScopeSummary(): string[] {
    return (this.scopeInference?.secondary_scopes ?? []).map((scope) => this.scopeLabel(scope));
  }

  get stageTimes(): Array<{ stage: string; durationMs: number }> {
    return Object.entries(this.runResult?.timings.stage_times ?? {}).map(([stage, durationMs]) => ({
      stage,
      durationMs,
    }));
  }

  toggleInspectPanel(): void {
    this.inspectOpen = !this.inspectOpen;
  }

  async submitQuestion(): Promise<void> {
    const trimmedQuestion = this.question.trim();
    if (!trimmedQuestion || this.isSubmitting) {
      return;
    }

    this.isSubmitting = true;
    this.requestError = null;
    this.runResult = null;

    try {
      this.runResult = await firstValueFrom(this.api.executeRun(trimmedQuestion));
      this.inspectOpen = true;
    } catch (error) {
      this.requestError = this.buildRequestErrorState(error);
      this.inspectOpen = false;
    } finally {
      this.isSubmitting = false;
    }
  }

  scopeLabel(scope: ScopeReference | null | undefined): string {
    if (!scope) {
      return 'No scope selected';
    }

    return [scope.workspace, scope.domain, scope.project, scope.client, scope.module]
      .filter((value): value is string => Boolean(value))
      .join(' / ');
  }

  previewText(value: string | null | undefined, maxLength = 140): string {
    if (!value) {
      return 'No preview available.';
    }

    const normalized = value.replace(/\s+/g, ' ').trim();
    if (normalized.length <= maxLength) {
      return normalized;
    }

    return `${normalized.slice(0, maxLength - 1).trimEnd()}…`;
  }

  private chunkLabel(documentId: string, chunkId: string): string {
    return `${documentId} / ${chunkId}`;
  }

  private buildRequestErrorState(error: unknown): RequestErrorState {
    if (error instanceof HttpErrorResponse) {
      const payload = error.error as { detail?: ExecuteRunHttpError | string } | null;
      const detail = payload?.detail;

      if (detail && typeof detail === 'object') {
        return {
          message: detail.message || 'Backend request failed.',
          detail: detail.category
            ? `Category: ${detail.category}${detail.endpoint ? ` | Endpoint: ${detail.endpoint}` : ''}`
            : detail.endpoint
              ? `Endpoint: ${detail.endpoint}`
              : undefined,
        };
      }

      if (typeof detail === 'string') {
        return {
          message: detail,
          detail: `HTTP ${error.status}`,
        };
      }

      return {
        message: error.status === 0 ? 'Cannot reach the backend service.' : 'Backend request failed.',
        detail: error.status ? `HTTP ${error.status}` : 'Check that the backend is running on port 8761.',
      };
    }

    return {
      message: 'Unexpected frontend error while running the request.',
    };
  }
}
