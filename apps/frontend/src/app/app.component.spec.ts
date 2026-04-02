import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { AppComponent } from './app.component';
import { AnswerRunResponse } from './answer-engine-api.service';

const mockRunResponse: AnswerRunResponse = {
  id: 'run-test',
  query: 'What do we know about the Bechtle CRM rollout?',
  created_at: '2026-04-02T10:30:00Z',
  answer_policy: {
    retrieval_required: true,
    max_retrieval_rounds: 1,
    default_top_k: 4,
    allow_multi_scope: false,
    allow_regeneration: true,
    verification_profile: 'bounded_v1',
    response_style: 'grounded',
  },
  query_analysis: {
    normalized_query: 'what do we know about the bechtle crm rollout?',
    intent_type: 'question_answering',
    requires_retrieval: true,
    query_variants: [],
  },
  stage_model_routing: [
    {
      stage_id: 'answer_generation',
      provider_id: 'ollama',
      model_id: 'qwen2.5:7b',
      parameters: {},
    },
  ],
  scope_inference: {
    status: 'ok',
    primary_scope: {
      workspace: 'jade',
      domain: 'bechtle',
      project: 'crm',
    },
    secondary_scopes: [],
    candidate_scopes: [],
    rejected_scopes: [],
    confidence_scores: {},
    validation_scores: {},
    fallback_applied: false,
  },
  retrieval_plan: {
    rounds: [
      {
        scope: {
          workspace: 'jade',
          domain: 'bechtle',
          project: 'crm',
        },
        top_k: 4,
        strategy_type: 'primary',
      },
    ],
    fallback_rules: {},
  },
  retrieval_result: {
    status: 'ok',
    results_by_round: [],
    aggregated_results: [],
  },
  context_pack: {
    selected_chunks: [],
    source_mapping: [],
    structured_context: 'Context preview',
    token_estimate: 123,
  },
  answer_result: {
    answer_text: 'Bechtle CRM uses Dynamics 365 Sales.',
    token_usage: {
      prompt_tokens: 100,
      completion_tokens: 50,
      total_tokens: 150,
    },
    model_metadata: {
      provider: 'ollama',
      resolved_model: 'qwen2.5:7b',
    },
  },
  final_response: {
    answer_text: 'Bechtle CRM uses Dynamics 365 Sales.',
    certainty: 'medium',
    limitations: ['This is a bounded local run.'],
    sources: [],
    inferred_scopes: [],
    verification_summary: {},
    trace_id: 'run-test',
  },
  verification_result: {
    grounded: true,
    scope_consistency_ok: true,
    coverage_ok: true,
    adequacy_ok: true,
    limitations: ['This is a bounded local run.'],
    uncertainty_flags: [],
    decision: 'keep',
    requires_regeneration: false,
    regeneration_attempted: false,
    confidence_score: 0.8,
  },
  timings: {
    total_time_ms: 3210,
    stage_times: {
      scope_inference: 120,
      retrieval_execution: 340,
      answer_generation: 980,
      answer_verification: 420,
    },
  },
  errors: [],
  events: [],
};

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideHttpClient()],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render the main surface title', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Main Question/Answer Surface');
  });

  it('should open the inspect drawer and render run diagnostics', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    app.runResult = mockRunResponse;
    app.inspectOpen = true;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.inspect-drawer h2')?.textContent).toContain('Run Diagnostics');
    expect(compiled.textContent).toContain('run-test');
    expect(compiled.textContent).toContain('qwen2.5:7b');
    expect(compiled.textContent).toContain('prompt 100 | completion 50 | total 150');
  });

  it('should render the refined main result summary for a completed run', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    app.runResult = mockRunResponse;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.result-state-pill')?.textContent).toContain('Grounded answer');
    expect(compiled.textContent).toContain('Primary scope');
    expect(compiled.textContent).toContain('Trace id');
    expect(compiled.textContent).toContain('This is a bounded local run.');
  });

  it('should render the inspect drawer handle instead of the floating inspect CTA', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    app.runResult = mockRunResponse;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.inspect-handle')?.textContent).toContain('<<');
    expect(compiled.querySelector('.inspect-fab')).toBeNull();
  });

  it('should render a non-final running preview state separately from the final answer card', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    app.runViewState = 'running_preview';
    app.previewState = {
      runId: 'run-preview',
      currentStageId: 'retrieval_execution',
      currentStageLabel: 'Retrieval Execution',
      latestMessage: 'Retrieval execution started.',
      latestSummaryRows: [
        { label: 'Run id', value: 'run-preview' },
        { label: 'Executed rounds', value: '1' },
      ],
    };
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.preview-pill')?.textContent).toContain('Preview only');
    expect(compiled.textContent).toContain('Retrieval Execution');
    expect(compiled.textContent).toContain('Retrieval execution started.');
    expect(compiled.querySelector('.answer-card')).toBeNull();
  });

  it('should render generation preview text only in the running preview state', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    app.runViewState = 'running_preview';
    app.previewState = {
      runId: 'run-preview',
      currentStageId: 'answer_generation',
      currentStageLabel: 'Answer Generation',
      latestMessage: 'Generation preview updated.',
      latestSummaryRows: [{ label: 'Preview chars', value: '96' }],
      generationPreviewText: 'This is still preview-only text and not the final verified answer.',
    };
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.generation-preview-copy')?.textContent).toContain('preview-only text');
    expect(compiled.querySelector('.preview-text-pill')?.textContent).toContain('Draft text');
    expect(compiled.querySelector('.answer-card')).toBeNull();
  });
});
