from __future__ import annotations

from answer_engine_backend.model_runtime import OllamaRuntime
from answer_engine_backend.pipeline.models import StageModelConfig
from answer_engine_backend.settings import BackendSettings, get_settings


class StageModelResolver:
    def __init__(self, settings: BackendSettings | None = None) -> None:
        self.settings = settings or get_settings()
        self.ollama_runtime = OllamaRuntime(self.settings)

    def resolve(self, stage_id: str) -> StageModelConfig:
        routing_defaults = self.settings.stage_routing_defaults or {}
        default = routing_defaults.get(stage_id)
        if default is None:
            return StageModelConfig(
                stage_id=stage_id,
                provider_id="unresolved",
                model_id="unresolved",
                parameters={"routing_mode": "unresolved"},
            )

        resolved = StageModelConfig(
            stage_id=default.stage_id,
            provider_id=default.provider_id,
            model_id=default.model_id,
            parameters=dict(default.parameters),
        )
        if resolved.provider_id == "ollama":
            return self.ollama_runtime.resolve_stage_model(resolved)
        return resolved

    def resolve_many(self, stage_ids: list[str]) -> list[StageModelConfig]:
        return [self.resolve(stage_id) for stage_id in stage_ids]
