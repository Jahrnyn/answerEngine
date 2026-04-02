import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { AppComponent } from './app.component';
import { AnswerRunResponse } from './answer-engine-api.service';

const mockRunResponse: AnswerRunResponse = {
  id: 'run-test',
  query: 'What do we know about the Bechtle CRM rollout?',
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
});
