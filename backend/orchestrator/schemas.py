"""Shared Pydantic schemas for the agentic screening pipeline."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


RiskLabel = Literal["low", "medium", "high"]


class PatientInput(BaseModel):
    """Structured patient profile consumed by every agent."""

    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., min_length=1)
    smoker: bool
    family_history: bool
    symptoms: list[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    """Output of the risk prediction agent."""

    model_config = {"protected_namespaces": ()}

    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_label: RiskLabel
    model_version: str
    feature_summary: dict[str, float]


class GuidelineDecision(BaseModel):
    """Structured output of the guidelines agent."""

    recommendation: str
    recommendation_type: str
    rationale: str
    citation: str
    matched_rules: list[str] = Field(default_factory=list)
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list)


class ExplanationResult(BaseModel):
    """Human-readable explanation produced by the reasoning agent."""

    explanation: str
    reasoning_trace: list[str] = Field(default_factory=list)
    prompt_version: str
    provider: str
    model: str


class AgentObservation(BaseModel):
    """Observability payload for an individual agent execution."""

    agent: str
    latency_ms: float
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    logged_at: datetime = Field(default_factory=datetime.utcnow)
    respan_log_id: str | None = None


class EvaluationResult(BaseModel):
    """Evaluation metrics for a full orchestrated run."""

    guideline_correct: bool
    guideline_score: float
    explanation_quality_score: float
    consistency_score: float
    notes: list[str] = Field(default_factory=list)
    respan_score_ids: list[str] = Field(default_factory=list)


class PredictionResponse(BaseModel):
    """Final API response returned by the controller."""

    risk_score: float
    risk_label: RiskLabel
    recommendation: str
    explanation: str
    reasoning_trace: list[str]
    citation: str
    prompt_version: str
    evaluation: EvaluationResult | None = None
    debug: dict[str, Any] | None = None
