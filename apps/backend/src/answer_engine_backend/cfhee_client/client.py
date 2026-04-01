from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from answer_engine_backend.settings import BackendSettings


@dataclass
class CfheeClientError(Exception):
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


class CfheeClient:
    def __init__(self, settings: BackendSettings) -> None:
        self._base_url = settings.cfhee_base_url
        self._api_base_url: str | None = None
        self._timeout_seconds = settings.cfhee_timeout_seconds

    def get_health(self) -> dict:
        return self._request_json("GET", "/api/v1/health")

    def get_capabilities(self) -> dict:
        return self._request_json("GET", "/api/v1/capabilities")

    def get_scope_values(self) -> dict:
        return self._request_json("GET", "/api/v1/scopes/values")

    def get_scope_tree(self) -> dict:
        return self._request_json("GET", "/api/v1/scopes/tree")

    def query_retrieval(self, payload: dict) -> dict:
        return self._request_json("POST", "/api/v1/retrieval/query", payload)

    def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        try:
            return self._request_json_once(method, path, payload, use_resolved_base=True)
        except CfheeClientError as error:
            if (
                self._api_base_url is None
                and (
                    (
                        error.status_code == 502
                        and error.body
                        and "<!doctype html>" in error.body.lower()
                    )
                    or error.status_code in {404, 405}
                )
            ):
                self._api_base_url = self._resolve_api_base_url()
                return self._request_json_once(method, path, payload, use_resolved_base=True)
            raise

    def _request_json_once(
        self,
        method: str,
        path: str,
        payload: dict | None,
        *,
        use_resolved_base: bool,
    ) -> dict:
        base_url = self._api_base_url if use_resolved_base and self._api_base_url else self._base_url
        url = f"{base_url}{path}"
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
            raise CfheeClientError(
                message="CfHEE returned an error response.",
                status_code=error.code,
                endpoint=path,
                body=body or None,
            ) from error
        except URLError as error:
            raise CfheeClientError(
                message=f"CfHEE request failed: {error.reason}",
                status_code=503,
                endpoint=path,
            ) from error
        except json.JSONDecodeError as error:
            raise CfheeClientError(
                message="CfHEE returned invalid JSON.",
                status_code=502,
                endpoint=path,
                body=body or None,
            ) from error

    def _resolve_api_base_url(self) -> str:
        runtime_config_path = "/runtime-config.js"
        request = Request(
            url=f"{self._base_url}{runtime_config_path}",
            headers={"Accept": "application/javascript, text/javascript, */*"},
            method="GET",
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                body = response.read().decode("utf-8", errors="replace")
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise CfheeClientError(
                message="CfHEE runtime config request failed.",
                status_code=error.code,
                endpoint=runtime_config_path,
                body=body or None,
            ) from error
        except URLError as error:
            raise CfheeClientError(
                message=f"CfHEE runtime config request failed: {error.reason}",
                status_code=503,
                endpoint=runtime_config_path,
            ) from error

        match = re.search(r'apiBaseUrl:\s*"([^"]+)"', body)
        if match is None:
            raise CfheeClientError(
                message="CfHEE runtime config did not expose apiBaseUrl.",
                status_code=502,
                endpoint=runtime_config_path,
                body=body or None,
            )

        return match.group(1).rstrip("/")
