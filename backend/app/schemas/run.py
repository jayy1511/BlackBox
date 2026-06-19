from datetime import datetime
from pydantic import BaseModel, Field


class RunCreateRequest(BaseModel):
    input: str = Field(..., min_length=1)
    policy_mode: str = Field(default="balanced", pattern="^(monitor|balanced|strict)$")
    model: str | None = None


class EntityResponse(BaseModel):
    type: str
    source: str
    start_index: int
    end_index: int
    confidence: float
    risk_level: str
    action: str
    replacement_value: str


class PolicyDecisionResponse(BaseModel):
    rule_id: str
    policy_mode: str
    action: str
    reason: str
    created_at: datetime


class LlmCallResponse(BaseModel):
    provider: str
    model_name: str
    latency_ms: int | None
    status: str
    error_message: str | None = None
    created_at: datetime | None = None


class RunCreateResponse(BaseModel):
    run_id: str
    status: str
    policy_mode: str
    risk_level: str
    protected_prompt: str
    model_response: str | None
    detected_entities: list[EntityResponse]
    llm_call: LlmCallResponse | None
    report: dict


class RunListItemResponse(BaseModel):
    run_id: str
    status: str
    policy_mode: str
    risk_level: str
    model_provider: str
    model_name: str
    created_at: datetime
    entities_count: int
    llm_status: str | None


class RunListResponse(BaseModel):
    items: list[RunListItemResponse]
    total: int


class RunDetailResponse(BaseModel):
    run_id: str
    status: str
    policy_mode: str
    risk_level: str
    model_provider: str
    model_name: str
    created_at: datetime
    protected_prompt: str | None
    model_response: str | None
    detected_entities: list[EntityResponse]
    policy_decisions: list[PolicyDecisionResponse]
    llm_call: LlmCallResponse | None
    report: dict