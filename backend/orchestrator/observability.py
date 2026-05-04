"""Respan/Keywords AI observability helpers with graceful local fallbacks."""

from __future__ import annotations

import json
import os
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

import requests

try:
    from respan import Respan, agent as respan_agent, task as respan_task, workflow as respan_workflow
except ImportError:  # pragma: no cover - local fallback when SDK is absent
    Respan = None

    def _noop_decorator(*_args: Any, **_kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func

        return decorator

    respan_agent = respan_task = respan_workflow = _noop_decorator


class ObservabilityManager:
    """Wrap Respan tracing plus Keywords AI log/score ingestion."""

    def __init__(self) -> None:
        self.api_key = os.getenv("RESPAN_API_KEY") or os.getenv("KEYWORDSAI_API_KEY")
        self.organization_id = os.getenv("RESPAN_ORGANIZATION_ID") or os.getenv("KEYWORDSAI_ORGANIZATION_ID")
        self.base_url = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co").rstrip("/")
        self._respan = None
        self.debug_log_path = Path(__file__).resolve().parent.parent / "respan_debug.log"

        if self.api_key and Respan is not None:
            self._respan = Respan(api_key=self.api_key)
        self.last_error: str | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.organization_id:
            headers["X-Organization-Id"] = self.organization_id
        return headers

    def _extract_log_id(self, payload: Any) -> str | None:
        if isinstance(payload, dict):
            for key in ("id", "log_id", "request_log_id", "requestLogId"):
                value = payload.get(key)
                if value:
                    return str(value)
            for nested_key in ("data", "result", "request_log", "requestLog", "log"):
                nested = payload.get(nested_key)
                nested_id = self._extract_log_id(nested)
                if nested_id:
                    return nested_id
        if isinstance(payload, list):
            for item in payload:
                nested_id = self._extract_log_id(item)
                if nested_id:
                    return nested_id
        return None

    def _extract_score_id(self, payload: Any) -> str | None:
        return self._extract_log_id(payload)

    def _write_debug_payload(self, label: str, payload: Any) -> None:
        try:
            with self.debug_log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"[{label}]\n")
                handle.write(json.dumps(payload, indent=2, default=str))
                handle.write("\n\n")
        except Exception:
            pass

    def _retrieve_log_id_by_custom_identifier(self, custom_identifier: str) -> str | None:
        try:
            response = requests.get(
                f"{self.base_url}/api/request-logs/",
                headers=self.headers(),
                params={"custom_identifier": custom_identifier},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            self._write_debug_payload(f"RESPAN_LOOKUP_{custom_identifier}", data)
            extracted_id = self._extract_log_id(data)
            print(
                f"[RESPAN] lookup custom_identifier={custom_identifier} "
                f"id={extracted_id} response={json.dumps(data, default=str)[:600]}"
            )
            return extracted_id
        except Exception as exc:
            response_text = ""
            if "response" in locals():
                try:
                    response_text = response.text
                except Exception:
                    response_text = ""
            self.last_error = f"lookup failed custom_identifier={custom_identifier}: {exc} {response_text}".strip()
            print(f"[RESPAN] {self.last_error}")
            return None

    def _resolve_log_reference(self, log_reference: str) -> str | None:
        if log_reference.startswith("custom:"):
            custom_identifier = log_reference.split("custom:", 1)[1]
            for attempt in range(6):
                resolved = self._retrieve_log_id_by_custom_identifier(custom_identifier)
                if resolved:
                    return resolved
                delay = min(0.5 * (attempt + 1), 3.0)
                print(
                    f"[RESPAN] deferred score lookup retry {attempt + 1}/6 "
                    f"custom_identifier={custom_identifier} waiting={delay}s"
                )
                time.sleep(delay)
            self.last_error = f"deferred score lookup failed custom_identifier={custom_identifier}"
            print(f"[RESPAN] {self.last_error}")
            return None
        return log_reference

    def log_agent_run(
        self,
        *,
        agent_name: str,
        model_name: str,
        input_payload: dict[str, Any],
        output_payload: dict[str, Any],
        latency_ms: float,
        prompt: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str | None:
        if not self.enabled:
            self.last_error = "RESPAN disabled: missing RESPAN_API_KEY / KEYWORDSAI_API_KEY"
            print(f"[RESPAN] {self.last_error}")
            return None

        custom_identifier = f"{agent_name}-{uuid4()}"
        payload = {
            "input": {
                "agent": agent_name,
                "input": input_payload,
                "prompt": prompt,
            },
            "output": output_payload,
            "log_type": "workflow",
            "model": model_name,
            "latency": latency_ms,
            "prompt_messages": [
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "agent": agent_name,
                            "input": input_payload,
                            "prompt": prompt,
                        },
                        default=str,
                    ),
                }
            ],
            "completion_message": {
                "role": "assistant",
                "content": json.dumps(output_payload, default=str),
            },
            "custom_identifier": custom_identifier,
            "customer_params": {
                "customer_identifier": agent_name,
            },
            "metadata": {
                "latency_ms": latency_ms,
                **(metadata or {}),
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/request-logs/",
                headers=self.headers(),
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            self.last_error = None
            self._write_debug_payload(f"RESPAN_LOG_{agent_name}", data)
            extracted_id = self._extract_log_id(data) or self._retrieve_log_id_by_custom_identifier(custom_identifier)
            if extracted_id:
                print(f"[RESPAN] log ok agent={agent_name} id={extracted_id} response={json.dumps(data, default=str)[:600]}")
                return extracted_id
            print(
                f"[RESPAN] log accepted agent={agent_name} "
                f"custom_identifier={custom_identifier} response={json.dumps(data, default=str)[:600]}"
            )
            return f"custom:{custom_identifier}"
        except Exception as exc:
            response_text = ""
            if "response" in locals():
                try:
                    response_text = response.text
                except Exception:
                    response_text = ""
            self.last_error = f"log failed agent={agent_name}: {exc} {response_text}".strip()
            print(f"[RESPAN] {self.last_error}")
            return None

    def log_score(
        self,
        *,
        log_id: str | None,
        evaluator_slug: str,
        numerical_value: float | None = None,
        boolean_value: bool | None = None,
        string_value: str | None = None,
    ) -> str | None:
        if not self.enabled or not log_id:
            if not self.enabled:
                self.last_error = "RESPAN score skipped: missing API key"
                print(f"[RESPAN] {self.last_error}")
            elif not log_id:
                self.last_error = "RESPAN score deferred: missing log reference"
                print(f"[RESPAN] {self.last_error}")
            return None

        resolved_log_id = self._resolve_log_reference(log_id)
        if not resolved_log_id:
            return None

        payload = {
            "evaluator_slug": evaluator_slug,
            "numerical_value": numerical_value,
            "boolean_value": boolean_value,
            "string_value": string_value,
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/logs/{resolved_log_id}/scores/",
                headers=self.headers(),
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            self.last_error = None
            self._write_debug_payload(f"RESPAN_SCORE_{resolved_log_id}", data)
            extracted_id = self._extract_score_id(data)
            print(
                f"[RESPAN] score ok log_id={resolved_log_id} "
                f"id={extracted_id} response={json.dumps(data, default=str)[:600]}"
            )
            return extracted_id
        except Exception as exc:
            response_text = ""
            if "response" in locals():
                try:
                    response_text = response.text
                except Exception:
                    response_text = ""
            self.last_error = f"score failed log_id={resolved_log_id}: {exc} {response_text}".strip()
            print(f"[RESPAN] {self.last_error}")
            return None


observability = ObservabilityManager()


def timed_agent(name: str, span_type: str = "agent") -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that times a function and annotates the result with latency."""

    decorator = respan_agent if span_type == "agent" else respan_task

    def outer(func: Callable[..., Any]) -> Callable[..., Any]:
        decorated = decorator(name=name)(func)

        @wraps(decorated)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = decorated(*args, **kwargs)
            latency_ms = round((time.perf_counter() - start) * 1000, 3)
            try:
                object.__setattr__(result, "_latency_ms", latency_ms)
            except Exception:
                if isinstance(result, dict):
                    result["_latency_ms"] = latency_ms
            return result

        return wrapper

    return outer


workflow = respan_workflow
