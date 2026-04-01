from __future__ import annotations

import json
import re
import socket
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from answer_engine_backend.pipeline.models import StageModelConfig
from answer_engine_backend.settings import BackendSettings, get_settings


@dataclass
class ModelRuntimeError(Exception):
    message: str
    status_code: int
    endpoint: str
    body: str | None = None

    def to_detail(self) -> dict[str, str | int]:
        detail: dict[str, str | int] = {
            "message": self.message,
            "endpoint": self.endpoint,
            "status_code": self.status_code,
        }
        if self.body:
            detail["body"] = self.body
        return detail


@dataclass(frozen=True)
class ModelGenerationOutput:
    resolved_config: StageModelConfig
    answer_text: str
    token_usage: dict[str, int]
    model_metadata: dict[str, str | int | bool]


class OllamaRuntime:
    def __init__(self, settings: BackendSettings | None = None) -> None:
        self._settings = settings or get_settings()
        self._base_url = self._settings.ollama_base_url.rstrip("/")
        self._timeout_seconds = 60.0

    def resolve_stage_model(self, stage_config: StageModelConfig) -> StageModelConfig:
        if stage_config.provider_id != "ollama":
            return stage_config
        if stage_config.model_id != "strongest_available_default":
            return stage_config

        models = self._request_json("GET", "/api/tags").get("models", [])
        candidates = [model for model in models if self._is_generation_candidate(model)]
        if not candidates:
            raise ModelRuntimeError(
                message="Ollama did not expose any generative models for answer generation.",
                status_code=503,
                endpoint="/api/tags",
                body=json.dumps(models),
            )

        selected = max(
            candidates,
            key=lambda model: (
                0 if self._is_reasoning_heavy_candidate(model) else 1,
                int(model.get("size", 0)),
                str(model.get("name", "")),
            ),
        )

        return StageModelConfig(
            stage_id=stage_config.stage_id,
            provider_id=stage_config.provider_id,
            model_id=str(selected.get("name") or selected.get("model") or "unresolved"),
            parameters=dict(stage_config.parameters),
        )

    def generate(
        self,
        stage_config: StageModelConfig,
        prompt: str,
    ) -> ModelGenerationOutput:
        resolved_config = self.resolve_stage_model(stage_config)
        if resolved_config.provider_id != "ollama":
            raise ModelRuntimeError(
                message="Answer generation routing resolved to an unsupported provider.",
                status_code=500,
                endpoint="answer_generation",
                body=json.dumps(
                    {
                        "provider_id": resolved_config.provider_id,
                        "model_id": resolved_config.model_id,
                    }
                ),
            )

        response = self._request_json(
            "POST",
            "/api/generate",
            {
                "model": resolved_config.model_id,
                "prompt": prompt,
                "stream": False,
                "options": self._build_options(resolved_config.parameters),
            },
        )

        answer_text = self._sanitize_answer_text(str(response.get("response", "")))
        if not answer_text:
            raise ModelRuntimeError(
                message="Ollama returned an empty answer response.",
                status_code=502,
                endpoint="/api/generate",
                body=json.dumps(response),
            )

        prompt_tokens = self._as_int(response.get("prompt_eval_count"))
        completion_tokens = self._as_int(response.get("eval_count"))
        if prompt_tokens is None:
            prompt_tokens = max(1, len(prompt) // 4)
        if completion_tokens is None:
            completion_tokens = max(1, len(answer_text) // 4)

        return ModelGenerationOutput(
            resolved_config=resolved_config,
            answer_text=answer_text,
            token_usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            model_metadata={
                "provider_id": resolved_config.provider_id,
                "configured_model_id": stage_config.model_id,
                "resolved_model_id": resolved_config.model_id,
                "routing_mode": resolved_config.parameters.get("routing_mode", "model"),
                "capability_tier": resolved_config.parameters.get(
                    "capability_tier",
                    "unspecified",
                ),
                "done": bool(response.get("done", False)),
                "done_reason": str(response.get("done_reason", "unknown")),
            },
        )

    def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        url = f"{self._base_url}{path}"
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url=url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                body = response.read().decode("utf-8", errors="replace")
                return json.loads(body) if body else {}
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise ModelRuntimeError(
                message="Ollama returned an error response.",
                status_code=error.code,
                endpoint=path,
                body=body or None,
            ) from error
        except URLError as error:
            raise ModelRuntimeError(
                message=f"Ollama request failed: {error.reason}",
                status_code=503,
                endpoint=path,
            ) from error
        except TimeoutError as error:
            raise ModelRuntimeError(
                message="Ollama request timed out.",
                status_code=504,
                endpoint=path,
            ) from error
        except socket.timeout as error:
            raise ModelRuntimeError(
                message="Ollama request timed out.",
                status_code=504,
                endpoint=path,
            ) from error
        except json.JSONDecodeError as error:
            raise ModelRuntimeError(
                message="Ollama returned invalid JSON.",
                status_code=502,
                endpoint=path,
                body=body or None,
            ) from error

    def _is_generation_candidate(self, model: dict) -> bool:
        details = model.get("details", {})
        family = str(details.get("family", "")).lower()
        families = [str(item).lower() for item in details.get("families", [])]
        name = str(model.get("name", "")).lower()

        excluded_family_markers = {"bert", "clip"}
        if family in excluded_family_markers:
            return False
        if any(marker in families for marker in excluded_family_markers):
            return False
        if any(marker in name for marker in {"embed", "embedding", "bge"}):
            return False
        return True

    def _is_reasoning_heavy_candidate(self, model: dict) -> bool:
        name = str(model.get("name", "")).lower()
        return any(marker in name for marker in {"deepseek-r1", ":r1", "-r1"})

    def _build_options(self, parameters: dict[str, str]) -> dict[str, int | float]:
        options: dict[str, int | float] = {}
        temperature = self._as_float(parameters.get("temperature"))
        if temperature is not None:
            options["temperature"] = temperature

        num_predict = self._as_int(parameters.get("num_predict"))
        if num_predict is not None:
            options["num_predict"] = num_predict

        return options

    def _sanitize_answer_text(self, answer_text: str) -> str:
        without_reasoning = re.sub(
            r"(?is)^\s*<think>.*?(</think>|$)",
            "",
            answer_text,
        )
        return without_reasoning.strip()

    def _as_int(self, value: object) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    def _as_float(self, value: object) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None
