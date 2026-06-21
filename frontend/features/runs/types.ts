export type PolicyMode = "monitor" | "balanced" | "strict";

export type EntityResponse = {
  type: string;
  source: string;
  start_index: number;
  end_index: number;
  confidence: number;
  risk_level: string;
  action: string;
  replacement_value: string;
};

export type LlmCallResponse = {
  provider: string;
  model_name: string;
  latency_ms: number | null;
  status: string;
  error_message: string | null;
  created_at?: string | null;
};

export type RunCreateRequest = {
  input: string;
  policy_mode: PolicyMode;
  model?: string;
};

export type RunCreateResponse = {
  run_id: string;
  status: string;
  policy_mode: string;
  risk_level: string;
  protected_prompt: string;
  model_response: string | null;
  detected_entities: EntityResponse[];
  llm_call: LlmCallResponse | null;
  report: {
    llm_status?: string;
    input_entities_count?: number;
    response_entities_count?: number;
    critical_entities_count?: number;
    high_entities_count?: number;
    tokenized_count?: number;
    warned_count?: number;
    flagged_response_count?: number;
    original_input_detection_count?: number;
  };
};

export type RunListItem = {
  run_id: string;
  status: string;
  policy_mode: string;
  risk_level: string;
  model_provider: string;
  model_name: string;
  created_at: string;
  entities_count: number;
  llm_status: string | null;
};

export type RunListResponse = {
  items: RunListItem[];
  total: number;
};