import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  AnswerEngineApiService,
  AnswerRunResponse,
  ContextPack,
  ExecuteRunHttpError,
  RetrievalPlan,
  RetrievalResult,
  RunErrorEntry,
  RunEvent,
  ScopeInferenceResult,
  ScopeReference,
  StageModelConfig,
  StreamRunHttpError,
  StreamRunTerminalError,
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

type RunViewState = 'idle' | 'running_preview' | 'completed' | 'failed';

type PreviewState = {
  runId: string | null;
  currentStageId: string | null;
  currentStageLabel: string;
  latestMessage: string;
  latestSummaryRows: KeyValueRow[];
  generationPreviewText: string;
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
  inspectOpen = false;
  runViewState: RunViewState = 'idle';

  runResult: AnswerRunResponse | null = null;
  requestError: RequestErrorState | null = null;
  previewState: PreviewState = this.emptyPreviewState();

  get isSubmitting(): boolean {
    return this.runViewState === 'running_preview';
  }

  get hasRunResult(): boolean {
    return this.runResult !== null;
  }

  get isSubmitDisabled(): boolean {
    return this.isSubmitting || this.question.trim().length === 0;
  }

  get isRunningPreview(): boolean {
    return this.runViewState === 'running_preview';
  }

  get runningStatus(): string {
    if (!this.isRunningPreview) {
      return '';
    }

    return this.previewState.currentStageLabel
      ? `Running: ${this.previewState.currentStageLabel}`
      : 'Running the bounded answer pipeline...';
  }

  get previewTitle(): string {
    return this.previewState.currentStageLabel || 'Preparing run activity';
  }

  get previewSummaryRows(): KeyValueRow[] {
    return this.previewState.latestSummaryRows;
  }

  get previewRunId(): string | null {
    return this.previewState.runId;
  }

  get generationPreviewText(): string {
    return this.previewState.generationPreviewText;
  }

  get answerText(): string {
    return this.runResult?.final_response.answer_text || 'No final answer returned.';
  }

  get primaryScopeLabel(): string {
    return this.scopeLabel(this.scopeInference?.primary_scope);
  }

  get totalRunTimeLabel(): string {
    return this.runResult ? `${this.runResult.timings.total_time_ms} ms` : 'n/a';
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

  get resultState(): 'success' | 'limited' | 'cannot-answer' | 'uncertain' | 'idle' {
    if (!this.runResult) {
      return 'idle';
    }

    if (this.verificationDecision === 'cannot_answer') {
      return 'cannot-answer';
    }

    if (this.verificationDecision === 'limit') {
      return 'limited';
    }

    if (
      this.certaintyLabel === 'uncertain' ||
      this.certaintyLabel === 'low' ||
      (this.verificationResult?.confidence_score ?? 1) < 0.5
    ) {
      return 'uncertain';
    }

    return 'success';
  }

  get resultStateLabel(): string {
    switch (this.resultState) {
      case 'success':
        return 'Grounded answer';
      case 'limited':
        return 'Limited answer';
      case 'cannot-answer':
        return 'Cannot answer';
      case 'uncertain':
        return 'Uncertain answer';
      default:
        return 'No result';
    }
  }

  get resultLead(): string {
    switch (this.resultState) {
      case 'success':
        return 'The current run produced a kept answer with usable grounding from the bounded pipeline.';
      case 'limited':
        return 'The current run returned a constrained answer. Review the top limitations before relying on it.';
      case 'cannot-answer':
        return 'The current run could not produce a trustworthy final answer within the bounded V1 path.';
      case 'uncertain':
        return 'The current run produced an answer, but certainty is reduced and the result should be treated cautiously.';
      default:
        return 'Submit a run to see the final answer here.';
    }
  }

  get resultToneClass(): string {
    switch (this.resultState) {
      case 'success':
        return 'state-success';
      case 'limited':
        return 'state-limited';
      case 'cannot-answer':
        return 'state-cannot-answer';
      case 'uncertain':
        return 'state-uncertain';
      default:
        return 'state-idle';
    }
  }

  get topLimitations(): string[] {
    return this.limitations.slice(0, 3);
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

    this.runViewState = 'running_preview';
    this.requestError = null;
    this.runResult = null;
    this.previewState = {
      runId: null,
      currentStageId: null,
      currentStageLabel: 'Starting run',
      latestMessage: 'Opening the bounded run stream and waiting for the first stage event.',
      latestSummaryRows: [],
      generationPreviewText: '',
    };

    try {
      this.runResult = await this.api.streamRun(trimmedQuestion, {
        onEvent: (event) => this.applyRunEvent(event),
      });
      this.runViewState = this.runResult.verification_result.decision === 'cannot_answer' ? 'failed' : 'completed';
      this.inspectOpen = true;
      this.previewState = this.emptyPreviewState();
    } catch (error) {
      this.runViewState = 'failed';
      this.requestError = this.buildRequestErrorState(error);
      this.inspectOpen = false;
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

  private applyRunEvent(event: RunEvent): void {
    const nextStageId = event.stage_id ?? this.previewState.currentStageId;
    const nextPreviewText =
      event.event_type === 'stage_preview' && event.stage_id === 'answer_generation'
        ? String(event.preview_text ?? this.previewState.generationPreviewText)
        : nextStageId === 'answer_generation'
          ? this.previewState.generationPreviewText
          : '';

    this.previewState = {
      runId: event.run_id,
      currentStageId: nextStageId,
      currentStageLabel: this.stageLabelForEvent(event),
      latestMessage: this.messageForEvent(event),
      latestSummaryRows: this.summaryRowsForEvent(event),
      generationPreviewText: nextPreviewText,
    };
  }

  private stageLabelForEvent(event: RunEvent): string {
    if (event.event_type === 'run_started') {
      return 'Run started';
    }

    if (event.event_type === 'run_completed') {
      return 'Run completed';
    }

    if (event.event_type === 'run_failed') {
      return 'Run failed';
    }

    return event.stage_id ? this.humanizeStageId(event.stage_id) : 'Pipeline activity';
  }

  private messageForEvent(event: RunEvent): string {
    if (event.event_type === 'stage_preview') {
      return 'Generation produced a bounded preview snapshot. Final verified answer will only appear after completion.';
    }

    return event.message || 'Pipeline activity updated.';
  }

  private summaryRowsForEvent(event: RunEvent): KeyValueRow[] {
    const rows: KeyValueRow[] = [];
    const entries = this.orderedSummaryEntries(event)
      .filter(([key]) => key !== 'final_run')
      .slice(0, 6);

    for (const [key, value] of entries) {
      rows.push({
        label: this.summaryLabel(key),
        value: this.summaryValueLabel(value),
        tone: this.summaryTone(key, value),
      });
    }

    if (rows.length === 0 && event.stage_id) {
      rows.push({ label: 'Stage', value: this.humanizeStageId(event.stage_id) });
    }

    return rows;
  }

  private humanizeStageId(stageId: string): string {
    return this.humanizeLabel(stageId).replace(/\b\w/g, (match) => match.toUpperCase());
  }

  private humanizeLabel(value: string): string {
    return value.replace(/_/g, ' ');
  }

  private orderedSummaryEntries(event: RunEvent): Array<[string, unknown]> {
    const summary = event.summary ?? {};
    const entries = Object.entries(summary);
    const preferredOrder = this.preferredSummaryOrder(event.stage_id, event.event_type);

    if (preferredOrder.length === 0) {
      return entries;
    }

    return entries.sort(([leftKey], [rightKey]) => {
      const leftIndex = preferredOrder.indexOf(leftKey);
      const rightIndex = preferredOrder.indexOf(rightKey);
      const normalizedLeftIndex = leftIndex === -1 ? preferredOrder.length : leftIndex;
      const normalizedRightIndex = rightIndex === -1 ? preferredOrder.length : rightIndex;
      return normalizedLeftIndex - normalizedRightIndex;
    });
  }

  private preferredSummaryOrder(stageId: string | null | undefined, eventType: string): string[] {
    if (eventType === 'run_completed' || eventType === 'run_failed') {
      return ['decision', 'certainty', 'error_count', 'trace_id', 'source_count'];
    }

    switch (stageId) {
      case 'scope_inference':
        return ['status', 'primary_scope', 'fallback_applied', 'retained_secondary_scope_count', 'failure_reason'];
      case 'retrieval_execution':
        return ['status', 'executed_rounds', 'aggregated_result_count', 'failure_reason'];
      case 'context_assembly':
        return ['selected_chunk_count', 'token_estimate', 'source_count'];
      case 'answer_verification':
        return ['decision', 'grounded', 'adequacy_ok', 'regeneration_attempted'];
      default:
        return [];
    }
  }

  private summaryLabel(key: string): string {
    const labels: Record<string, string> = {
      adequacy_ok: 'Adequacy ok',
      aggregated_result_count: 'Aggregated results',
      candidate_count: 'Candidate scopes',
      error_count: 'Errors',
      executed_rounds: 'Executed rounds',
      failure_reason: 'Failure reason',
      fallback_applied: 'Fallback applied',
      max_retrieval_rounds: 'Max retrieval rounds',
      planned_rounds: 'Planned rounds',
      primary_scope: 'Primary scope',
      query_length: 'Query length',
      regeneration_attempted: 'Regeneration attempted',
      retained_secondary_scope_count: 'Secondary scopes kept',
      selected_chunk_count: 'Selected chunks',
      source_count: 'Sources',
      token_estimate: 'Context token estimate',
      trace_id: 'Trace id',
    };

    return labels[key] ?? this.humanizeLabel(key);
  }

  private summaryTone(key: string, value: unknown): 'default' | 'muted' | 'warn' {
    if (key === 'failure_reason' && value) {
      return 'warn';
    }

    if (key === 'status' && typeof value === 'string' && value !== 'ok') {
      return value === 'no_evidence' ? 'muted' : 'warn';
    }

    if (key === 'decision' && typeof value === 'string' && value !== 'keep') {
      return value === 'limit' ? 'muted' : 'warn';
    }

    return 'default';
  }

  private summaryValueLabel(value: unknown): string {
    if (value === null || value === undefined) {
      return 'n/a';
    }

    if (typeof value === 'boolean') {
      return value ? 'yes' : 'no';
    }

    if (typeof value === 'string' || typeof value === 'number') {
      return String(value);
    }

    if (Array.isArray(value)) {
      return `${value.length} item(s)`;
    }

    return 'structured payload';
  }

  private emptyPreviewState(): PreviewState {
    return {
      runId: null,
      currentStageId: null,
      currentStageLabel: '',
      latestMessage: '',
      latestSummaryRows: [],
      generationPreviewText: '',
    };
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
    if (error instanceof StreamRunTerminalError) {
      return {
        message: error.terminalEvent.message || 'Run failed before completion.',
        detail: error.terminalEvent.stage_id
          ? `Stage: ${this.humanizeStageId(error.terminalEvent.stage_id)}`
          : 'The live run stream ended with a terminal failure event.',
      };
    }

    if (error instanceof StreamRunHttpError) {
      const detail = error.detail;
      if (typeof detail === 'object') {
        return {
          message: detail.message || 'Backend stream request failed.',
          detail: detail.category
            ? `Category: ${detail.category}${detail.endpoint ? ` | Endpoint: ${detail.endpoint}` : ''}`
            : detail.endpoint
              ? `Endpoint: ${detail.endpoint}`
              : undefined,
        };
      }

      return {
        message: detail,
        detail: `HTTP ${error.status}`,
      };
    }

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

    if (error instanceof Error) {
      return {
        message: error.message,
      };
    }

    return {
      message: 'Unexpected frontend error while running the request.',
    };
  }
}
