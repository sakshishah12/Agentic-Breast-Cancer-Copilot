"""Guidelines agent using local JSON retrieval plus deterministic rules."""

from __future__ import annotations

import json
from pathlib import Path

from orchestrator.observability import observability, timed_agent
from orchestrator.schemas import AgentObservation, GuidelineDecision, PatientInput, RiskAssessment

KB_PATH = Path(__file__).resolve().parent / "guidelines_kb.json"


def load_knowledge_base() -> list[dict]:
    return json.loads(KB_PATH.read_text(encoding="utf-8"))


def chunk_matches(patient: PatientInput, risk: RiskAssessment, chunk: dict) -> bool:
    gender = chunk.get("gender", "any")
    smoker = chunk.get("smoker")
    symptom_keywords = [item.lower() for item in chunk.get("symptom_keywords", [])]

    if patient.age < chunk.get("age_min", 0):
        return False
    if risk.risk_score < chunk.get("risk_min", 0.0):
        return False
    if gender != "any" and patient.gender.lower() != gender.lower():
        return False
    if smoker is not None and patient.smoker != smoker:
        return False
    if symptom_keywords and not any(symptom.lower() in symptom_keywords for symptom in patient.symptoms):
        return False
    return True


@timed_agent("guidelines_agent")
def run_guidelines_agent(patient: PatientInput, risk: RiskAssessment) -> GuidelineDecision:
    """Retrieve matching guideline chunks and synthesize a deterministic recommendation."""

    knowledge_base = load_knowledge_base()
    matches = [chunk for chunk in knowledge_base if chunk_matches(patient, risk, chunk)]

    if not matches:
        fallback = {
            "id": "guideline_default_surveillance",
            "recommendation": "Recommend routine clinician follow-up and continued preventive screening based on age and symptoms.",
            "recommendation_type": "follow_up",
            "citation": "Internal preventive screening baseline",
            "keywords": ["follow up", "preventive"],
        }
        matches = [fallback]

    primary = sorted(matches, key=lambda item: item.get("risk_min", 0.0), reverse=True)[0]
    matched_rules = [match["id"] for match in matches]

    return GuidelineDecision(
        recommendation=primary["recommendation"],
        recommendation_type=primary["recommendation_type"],
        rationale=(
            f"Matched {len(matches)} guideline rule(s) using age={patient.age}, "
            f"gender={patient.gender}, risk_score={risk.risk_score:.3f}, symptoms={patient.symptoms}."
        ),
        citation=primary["citation"],
        matched_rules=matched_rules,
        retrieved_chunks=matches,
    )


def observe_guidelines_agent(
    patient: PatientInput,
    risk: RiskAssessment,
    result: GuidelineDecision,
) -> AgentObservation:
    latency_ms = getattr(result, "_latency_ms", 0.0)
    input_payload = {
        "patient": patient.model_dump(),
        "risk": risk.model_dump(),
    }
    log_id = observability.log_agent_run(
        agent_name="guidelines_agent",
        model_name="rules_plus_json_retrieval",
        input_payload=input_payload,
        output_payload=result.model_dump(),
        latency_ms=latency_ms,
        metadata={"matched_rules": ",".join(result.matched_rules)},
    )
    return AgentObservation(
        agent="guidelines_agent",
        latency_ms=latency_ms,
        input_payload=input_payload,
        output_payload=result.model_dump(),
        metadata={"citation": result.citation},
        respan_log_id=log_id,
    )
