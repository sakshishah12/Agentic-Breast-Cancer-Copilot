"""Risk prediction agent built on top of the existing ML model."""

from __future__ import annotations

from orchestrator.observability import observability, timed_agent
from orchestrator.schemas import AgentObservation, PatientInput, RiskAssessment
from models.feature_mapper import MEAN, STD, map_patient_to_features
from .tools import model as risk_model


def score_to_label(score: float) -> str:
    if score < 0.33:
        return "low"
    if score < 0.66:
        return "medium"
    return "high"


@timed_agent("risk_prediction_agent")
def run_risk_agent(patient: PatientInput) -> RiskAssessment:
    """Run the existing ML model and return a structured risk assessment."""

    patient_dict = patient.model_dump()
    features = map_patient_to_features(patient_dict)
    risk_score = float(risk_model.predict_proba(features)[0][1])

    age_factor = min(patient.age / 100, 1.0)
    smoker_factor = float(patient.smoker)
    family_factor = float(patient.family_history)
    symptom_factor = min(len(patient.symptoms) / 5, 1.0)

    return RiskAssessment(
        risk_score=risk_score,
        risk_label=score_to_label(risk_score),
        model_version="risk_model.pkl",
        feature_summary={
            "age_factor": round(age_factor, 3),
            "smoker_factor": smoker_factor,
            "family_history_factor": family_factor,
            "symptom_factor": round(symptom_factor, 3),
            "baseline_feature_mean_0": round(float(MEAN[0]), 3),
            "baseline_feature_std_0": round(float(STD[0]), 3),
        },
    )


def observe_risk_agent(patient: PatientInput, result: RiskAssessment) -> AgentObservation:
    latency_ms = getattr(result, "_latency_ms", 0.0)
    log_id = observability.log_agent_run(
        agent_name="risk_agent",
        model_name="local_sklearn_model",
        input_payload=patient.model_dump(),
        output_payload=result.model_dump(),
        latency_ms=latency_ms,
        metadata={"risk_label": result.risk_label},
    )
    return AgentObservation(
        agent="risk_agent",
        latency_ms=latency_ms,
        input_payload=patient.model_dump(),
        output_payload=result.model_dump(),
        metadata={"model_version": result.model_version},
        respan_log_id=log_id,
    )
