from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from os import getenv


@dataclass(frozen=True)
class StageRoutingDefault:
    stage_id: str
    provider_id: str
    model_id: str
    parameters: dict[str, str]


@dataclass(frozen=True)
class BackendSettings:
    cfhee_base_url: str = "http://127.0.0.1:8770"
    cfhee_timeout_seconds: float = 5.0
    stage_routing_defaults: dict[str, StageRoutingDefault] | None = None


@lru_cache(maxsize=1)
def get_settings() -> BackendSettings:
    base_url = getenv("ANSWER_ENGINE_CFHEE_BASE_URL", BackendSettings.cfhee_base_url)
    timeout_raw = getenv(
        "ANSWER_ENGINE_CFHEE_TIMEOUT_SECONDS",
        str(BackendSettings.cfhee_timeout_seconds),
    )
    try:
        timeout_seconds = float(timeout_raw)
    except ValueError:
        timeout_seconds = BackendSettings.cfhee_timeout_seconds

    stage_routing_defaults = {
        "query_analysis": StageRoutingDefault(
            stage_id="query_analysis",
            provider_id="rule_based",
            model_id="rule_based_default",
            parameters={"routing_mode": "rule_based"},
        ),
        "scope_inference_ranking": StageRoutingDefault(
            stage_id="scope_inference_ranking",
            provider_id="runtime",
            model_id="medium_capability_default",
            parameters={"routing_mode": "model", "capability_tier": "medium"},
        ),
        "answer_generation": StageRoutingDefault(
            stage_id="answer_generation",
            provider_id="runtime",
            model_id="strongest_available_default",
            parameters={
                "routing_mode": "model",
                "capability_tier": "strongest_available",
            },
        ),
        "answer_verification": StageRoutingDefault(
            stage_id="answer_verification",
            provider_id="runtime",
            model_id="small_or_medium_default",
            parameters={"routing_mode": "model", "capability_tier": "small_or_medium"},
        ),
    }

    return BackendSettings(
        cfhee_base_url=base_url.rstrip("/"),
        cfhee_timeout_seconds=timeout_seconds,
        stage_routing_defaults=stage_routing_defaults,
    )
