from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from os import getenv


@dataclass(frozen=True)
class BackendSettings:
    cfhee_base_url: str = "http://127.0.0.1:8770"
    cfhee_timeout_seconds: float = 5.0


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

    return BackendSettings(
        cfhee_base_url=base_url.rstrip("/"),
        cfhee_timeout_seconds=timeout_seconds,
    )
