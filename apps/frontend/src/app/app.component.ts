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

type KeyValueRow = {
  label: string;
  value: string;
  tone?: 'default' | 'muted' | 'warn';
};

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

  get sourceCount(): number {
    return this.runResult?.final_response.sources.length ?? 0;
  }

  get selectedChunkPreview(): string[] {
    return (this.contextPack?.selected_chunks ?? [])
      .slice(0, 3)
      .map((chunk) => `${this.chunkLabel(chunk.document_id, chunk.chunk_id)} - ${this.previewText(chunk.content, 180)}`);
  }

  get sourceMappingPreview(): string[] {
    return (this.contextPack?.source_mapping ?? [])
      .slice(0, 5)
      .map((source) => `${this.chunkLabel(source.document_id, source.chunk_id)} - position ${source.position}`);
  }

  get retrievalRoundSummary(): string[] {
    return (this.retrievalResult?.results_by_round ?? []).map((round, index) => {
      const failure = round.failure_reason ? ` | ${round.failure_reason}` : '';
      return `Round ${index + 1}: ${this.scopeLabel(round.scope)} | ${round.status} | ${round.result_count} chunk(s)${failure}`;
    });
  }

  get retrievalScopeSummary(): string[] {
    return (this.retrievalPlan?.rounds ?? []).map((round, index) => {
      return `Round ${index + 1}: ${this.scopeLabel(round.scope)} | top_k ${round.top_k} | ${round.strategy_type}`;
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

  get runSummaryRows(): KeyValueRow[] {
    if (!this.runResult) {
      return [];
    }

    return [
      { label: 'Run id', value: this.runResult.id },
      { label: 'Trace id', value: this.traceId },
      { label: 'Total run time', value: `${this.runResult.timings.total_time_ms} ms` },
      { label: 'Certainty', value: this.certaintyLabel ?? 'not available' },
      { label: 'Verification decision', value: this.verificationDecision },
      { label: 'Sources', value: `${this.sourceCount}` },
    ];
  }

  get scopeRows(): KeyValueRow[] {
    if (!this.scopeInference) {
      return [];
    }

    return [
      { label: 'Scope status', value: this.scopeInference.status },
      { label: 'Primary scope', value: this.scopeLabel(this.scopeInference.primary_scope) },
      {
        label: 'Fallback applied',
        value: this.scopeInference.fallback_applied ? 'yes' : 'no',
      },
      {
        label: 'Failure reason',
        value: this.scopeInference.failure_reason ?? 'not applicable',
        tone: this.scopeInference.failure_reason ? 'warn' : 'muted',
      },
    ];
  }

  get retrievalRows(): KeyValueRow[] {
    if (!this.retrievalResult) {
      return [];
    }

    return [
      { label: 'Retrieval status', value: this.retrievalResult.status },
      { label: 'Planned rounds', value: `${this.retrievalPlan?.rounds.length ?? 0}` },
      { label: 'Executed rounds', value: `${this.retrievalResult.results_by_round.length}` },
      { label: 'Aggregated results', value: `${this.retrievalResult.aggregated_results.length}` },
      {
        label: 'Failure reason',
        value: this.retrievalResult.failure_reason ?? 'not applicable',
        tone: this.retrievalResult.failure_reason ? 'warn' : 'muted',
      },
    ];
  }

  get generationRows(): KeyValueRow[] {
    if (!this.runResult) {
      return [];
    }

    const tokenUsage = this.runResult.answer_result.token_usage;
    const provider = this.modelMetadataValue('provider');
    const model = this.modelMetadataValue('resolved_model');

    return [
      { label: 'Answer text present', value: this.runResult.answer_result.answer_text ? 'yes' : 'no' },
      { label: 'Provider', value: provider ?? 'not available', tone: provider ? 'default' : 'muted' },
      { label: 'Model', value: model ?? 'not available', tone: model ? 'default' : 'muted' },
      {
        label: 'Token usage',
        value: Object.keys(tokenUsage).length > 0 ? this.formatTokenUsage(tokenUsage) : 'not available',
        tone: Object.keys(tokenUsage).length > 0 ? 'default' : 'muted',
      },
    ];
  }

  get verificationRows(): KeyValueRow[] {
    if (!this.verificationResult) {
      return [];
    }

    return [
      { label: 'Decision', value: this.verificationResult.decision },
      { label: 'Grounded', value: this.boolLabel(this.verificationResult.grounded) },
      { label: 'Scope consistent', value: this.boolLabel(this.verificationResult.scope_consistency_ok) },
      { label: 'Coverage ok', value: this.boolLabel(this.verificationResult.coverage_ok) },
      { label: 'Adequacy ok', value: this.boolLabel(this.verificationResult.adequacy_ok) },
      { label: 'Confidence score', value: `${this.verificationResult.confidence_score}` },
      { label: 'Regeneration attempted', value: this.boolLabel(this.verificationResult.regeneration_attempted) },
    ];
  }

  get contextRows(): KeyValueRow[] {
    if (!this.contextPack) {
      return [];
    }

    return [
      { label: 'Selected chunks', value: `${this.contextPack.selected_chunks.length}` },
      {
        label: 'Context token estimate',
        value: Number.isFinite(this.contextPack.token_estimate) ? `${this.contextPack.token_estimate}` : 'not available',
      },
      { label: 'Source mapping entries', value: `${this.contextPack.source_mapping.length}` },
    ];
  }

  get routingRows(): KeyValueRow[] {
    return this.stageModelRouting.map((route) => ({
      label: route.stage_id,
      value: `${route.provider_id} / ${route.model_id}`,
    }));
  }

  get modelMetadataRows(): KeyValueRow[] {
    const metadata = this.runResult?.answer_result.model_metadata ?? {};

    return Object.entries(metadata).map(([label, value]) => ({
      label,
      value: String(value),
    }));
  }

  openInspectPanel(): void {
    this.inspectOpen = true;
  }

  closeInspectPanel(): void {
    this.inspectOpen = false;
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

    return `${normalized.slice(0, maxLength - 3).trimEnd()}...`;
  }

  private boolLabel(value: boolean): string {
    return value ? 'yes' : 'no';
  }

  private chunkLabel(documentId: string, chunkId: string): string {
    return `${documentId} / ${chunkId}`;
  }

  private formatTokenUsage(tokenUsage: Record<string, number>): string {
    const promptTokens = tokenUsage['prompt_tokens'];
    const completionTokens = tokenUsage['completion_tokens'];
    const totalTokens = tokenUsage['total_tokens'];

    if (
      typeof promptTokens === 'number' &&
      typeof completionTokens === 'number' &&
      typeof totalTokens === 'number'
    ) {
      return `prompt ${promptTokens} | completion ${completionTokens} | total ${totalTokens}`;
    }

    return Object.entries(tokenUsage)
      .map(([key, value]) => `${key} ${value}`)
      .join(' | ');
  }

  private modelMetadataValue(key: string): string | null {
    const value = this.runResult?.answer_result.model_metadata[key];
    return value === undefined ? null : String(value);
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
