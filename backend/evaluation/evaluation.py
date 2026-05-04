"""Evaluation helpers for the agentic screening workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.explanation_agent import run_explanation_agent
from orchestrator.observability import observability, timed_agent
from orchestrator.schemas import EvaluationResult, ExplanationResult, GuidelineDecision, PatientInput, RiskAssessment


@dataclass
class EvaluationContext:
    patient: PatientInput
    risk: RiskAssessment
    guideline: GuidelineDecision
    explanation: ExplanationResult
    explanation_log_id: str | None


def expected_guideline_types(patient: PatientInput, risk: RiskAssessment) -> set[str]:
    expected = {"follow_up"}
    if patient.age >= 45:
        expected.add("screening")
    if patient.smoker and patient.age >= 50 and risk.risk_score >= 0.45:
        expected.add("screening")
    if any(symptom.lower() in {"bleeding", "lump", "weight loss"} for symptom in patient.symptoms):
        expected.add("diagnostic")
    if risk.risk_score >= 0.65:
        expected.add("review")
    return expected


def guideline_correctness(patient: PatientInput, risk: RiskAssessment, guideline: GuidelineDecision) -> tuple[bool, float]:
    expected = expected_guideline_types(patient, risk)
    correct = guideline.recommendation_type in expected
    score = 1.0 if correct else 0.0
    return correct, score


def heuristic_explanation_score(
    patient: PatientInput,
    risk: RiskAssessment,
    guideline: GuidelineDecision,
    explanation: ExplanationResult,
) -> float:
    text = explanation.explanation.lower()
    score = 0.0
    if risk.risk_label in text:
        score += 0.35
    if guideline.citation.lower().split()[0] in text:
        score += 0.15
    if any(symptom.lower() in text for symptom in patient.symptoms[:2]):
        score += 0.2
    if guideline.recommendation.lower().split()[0] in text:
        score += 0.15
    if len(explanation.reasoning_trace) >= 2:
        score += 0.15
    return round(min(score, 1.0), 3)


def consistency_score(
    patient: PatientInput,
    risk: RiskAssessment,
    guideline: GuidelineDecision,
    baseline: ExplanationResult,
) -> float:
    comparison = run_explanation_agent(
        patient=patient,
        risk=risk,
        guideline=guideline,
        prompt_version=baseline.prompt_version,
    )
    same_explanation = baseline.explanation.strip() == comparison.explanation.strip()
    same_trace = baseline.reasoning_trace == comparison.reasoning_trace
    if same_explanation and same_trace:
        return 1.0
    if same_explanation or same_trace:
        return 0.5
    return 0.0


@timed_agent("evaluation_agent", span_type="task")
def evaluate_run(context: EvaluationContext) -> EvaluationResult:
    """Evaluate a full multi-agent run using deterministic heuristics."""

    guideline_ok, guideline_score = guideline_correctness(context.patient, context.risk, context.guideline)
    explanation_score = heuristic_explanation_score(
        context.patient,
        context.risk,
        context.guideline,
        context.explanation,
    )
    consistency = consistency_score(
        context.patient,
        context.risk,
        context.guideline,
        context.explanation,
    )

    notes = []
    if not guideline_ok:
        notes.append("Guidelines agent recommendation_type differed from the deterministic reference rules.")
    if explanation_score < 0.6:
        notes.append("Explanation score was below the desired quality threshold.")
    if consistency < 1.0:
        notes.append("Explanation output changed when rerun with the same prompt version.")

    score_ids = [
        observability.log_score(
            log_id=context.explanation_log_id,
            evaluator_slug="guideline_correctness",
            numerical_value=guideline_score,
            boolean_value=guideline_ok,
            string_value="Guideline rules match" if guideline_ok else "Guideline mismatch",
        ),
        observability.log_score(
            log_id=context.explanation_log_id,
            evaluator_slug="explanation_quality",
            numerical_value=explanation_score,
            string_value="Heuristic explanation quality score",
        ),
        observability.log_score(
            log_id=context.explanation_log_id,
            evaluator_slug="consistency_score",
            numerical_value=consistency,
            boolean_value=consistency == 1.0,
            string_value="Repeatability of explanation output",
        ),
    ]

    return EvaluationResult(
        guideline_correct=guideline_ok,
        guideline_score=guideline_score,
        explanation_quality_score=explanation_score,
        consistency_score=consistency,
        notes=notes,
        respan_score_ids=[score_id for score_id in score_ids if score_id],
    )
