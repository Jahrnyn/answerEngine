import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import {
  AnswerEngineApiService,
  AnswerRunResponse,
  ExecuteRunHttpError,
  RunErrorEntry,
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
    } catch (error) {
      this.requestError = this.buildRequestErrorState(error);
    } finally {
      this.isSubmitting = false;
    }
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
