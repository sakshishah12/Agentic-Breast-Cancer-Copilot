"""LLM-powered explanation agent with prompt versioning and fallbacks."""

from __future__ import annotations

import json
import os
import re

from orchestrator.observability import observability, timed_agent
from orchestrator.prompt_manager import PromptManager
from orchestrator.schemas import AgentObservation, ExplanationResult, GuidelineDecision, PatientInput, RiskAssessment

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency during local bootstrap
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency during local bootstrap
    genai = None


PROMPT_MANAGER = PromptManager()


def _log_provider_error(provider: str, exc: Exception) -> None:
    print(f"[EXPLANATION_AGENT] {provider} failed: {type(exc).__name__}: {exc}")


def _parse_json_response(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if not cleaned:
        raise json.JSONDecodeError("Empty response", cleaned, 0)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", cleaned, re.DOTALL | re.IGNORECASE)
        if fenced_match:
            return json.loads(fenced_match.group(1))

        object_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if object_match:
            return json.loads(object_match.group(1))

        raise


def _build_fallback_explanation(
    patient: PatientInput,
    risk: RiskAssessment,
    guideline: GuidelineDecision,
    prompt_version: str,
) -> ExplanationResult:
    explanation = (
        f"The patient is classified as {risk.risk_label} risk with a predicted score of {risk.risk_score:.2f}. "
        f"Based on age {patient.age}, symptoms {patient.symptoms or ['none reported']}, and the guideline match, "
        f"the recommended next step is: {guideline.recommendation}"
    )
    trace = [
        f"ML model produced a {risk.risk_label} risk label from structured clinical features.",
        f"Guidelines agent matched rule(s): {', '.join(guideline.matched_rules)}.",
        f"Citation source applied: {guideline.citation}.",
    ]
    return ExplanationResult(
        explanation=explanation,
        reasoning_trace=trace,
        prompt_version=prompt_version,
        provider="fallback",
        model="template",
    )


@timed_agent("explanation_agent")
def run_explanation_agent(
    patient: PatientInput,
    risk: RiskAssessment,
    guideline: GuidelineDecision,
    prompt_version: str | None = None,
) -> ExplanationResult:
    """Generate an explanation with OpenAI, Gemini, or a deterministic fallback."""

    selected_version, rendered_prompt = PROMPT_MANAGER.render(
        patient=patient,
        risk=risk,
        guideline=guideline,
        prompt_version=prompt_version,
    )

    provider_preference = os.getenv("EXPLANATION_PROVIDER", "auto").lower()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if provider_preference in {"auto", "openai"} and openai_api_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=openai_api_key, timeout=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20")))
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            completion = client.chat.completions.create(
                model=model_name,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You write safe, grounded clinical screening explanations."},
                    {"role": "user", "content": rendered_prompt},
                ],
            )
            content = completion.choices[0].message.content or "{}"
            parsed = _parse_json_response(content)
            return ExplanationResult(
                explanation=parsed["explanation"],
                reasoning_trace=parsed["reasoning_trace"],
                prompt_version=selected_version,
                provider="openai",
                model=model_name,
            )
        except Exception as exc:
            _log_provider_error("openai", exc)

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if provider_preference in {"auto", "gemini"} and gemini_api_key and genai is not None:
        try:
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            genai.configure(api_key=gemini_api_key)
            response = genai.GenerativeModel(model_name).generate_content(
                rendered_prompt,
                request_options={"timeout": int(float(os.getenv("GEMINI_TIMEOUT_SECONDS", "20")) * 1000)},
            )
            raw_text = (response.text or "").strip()
            parsed = _parse_json_response(raw_text)
            return ExplanationResult(
                explanation=parsed["explanation"],
                reasoning_trace=parsed["reasoning_trace"],
                prompt_version=selected_version,
                provider="gemini",
                model=model_name,
            )
        except Exception as exc:
            try:
                preview = (raw_text or "")[:600]
                if preview:
                    print(f"[EXPLANATION_AGENT] gemini raw preview: {preview}")
            except Exception:
                pass
            _log_provider_error("gemini", exc)

    return _build_fallback_explanation(patient, risk, guideline, selected_version)


def observe_explanation_agent(
    patient: PatientInput,
    risk: RiskAssessment,
    guideline: GuidelineDecision,
    result: ExplanationResult,
) -> AgentObservation:
    latency_ms = getattr(result, "_latency_ms", 0.0)
    _, rendered_prompt = PROMPT_MANAGER.render(
        patient=patient,
        risk=risk,
        guideline=guideline,
        prompt_version=result.prompt_version,
    )
    input_payload = {
        "patient": patient.model_dump(),
        "risk": risk.model_dump(),
        "guideline": guideline.model_dump(),
    }
    log_id = observability.log_agent_run(
        agent_name="explanation_agent",
        model_name=result.model,
        input_payload=input_payload,
        output_payload=result.model_dump(),
        latency_ms=latency_ms,
        prompt=rendered_prompt,
        metadata={
            "prompt_version": result.prompt_version,
            "provider": result.provider,
        },
    )
    return AgentObservation(
        agent="explanation_agent",
        latency_ms=latency_ms,
        input_payload=input_payload,
        output_payload=result.model_dump(),
        metadata={"prompt_version": result.prompt_version, "provider": result.provider},
        respan_log_id=log_id,
    )
