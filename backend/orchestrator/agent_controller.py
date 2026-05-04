"""Top-level orchestration for the agentic cancer screening pipeline."""

from __future__ import annotations

from agents.explanation_agent import observe_explanation_agent, run_explanation_agent
from agents.guidelines_agent import observe_guidelines_agent, run_guidelines_agent
from agents.risk_agent import observe_risk_agent, run_risk_agent
from evaluation.evaluation import EvaluationContext, evaluate_run
from orchestrator.observability import workflow
from orchestrator.schemas import PatientInput, PredictionResponse


@workflow(name="agentic_cancer_screening_workflow")
def run_screening_pipeline(
    patient: PatientInput,
    *,
    debug: bool = False,
    prompt_version: str | None = None,
) -> PredictionResponse:
    """Execute the full multi-agent workflow and return a structured response."""

    risk = run_risk_agent(patient)
    risk_obs = observe_risk_agent(patient, risk)

    guideline = run_guidelines_agent(patient, risk)
    guideline_obs = observe_guidelines_agent(patient, risk, guideline)

    explanation = run_explanation_agent(patient, risk, guideline, prompt_version=prompt_version)
    explanation_obs = observe_explanation_agent(patient, risk, guideline, explanation)

    evaluation = evaluate_run(
        EvaluationContext(
            patient=patient,
            risk=risk,
            guideline=guideline,
            explanation=explanation,
            explanation_log_id=explanation_obs.respan_log_id,
        )
    )

    debug_payload = None
    if debug:
        debug_payload = {
            "risk_agent": risk.model_dump(),
            "guidelines_agent": guideline.model_dump(),
            "explanation_agent": explanation.model_dump(),
            "observations": [
                risk_obs.model_dump(mode="json"),
                guideline_obs.model_dump(mode="json"),
                explanation_obs.model_dump(mode="json"),
            ],
        }

    return PredictionResponse(
        risk_score=risk.risk_score,
        risk_label=risk.risk_label,
        recommendation=guideline.recommendation,
        explanation=explanation.explanation,
        reasoning_trace=explanation.reasoning_trace,
        citation=guideline.citation,
        prompt_version=explanation.prompt_version,
        evaluation=evaluation,
        debug=debug_payload,
    )
