import json
from typing import Any

import httpx

from app.core.config import settings
from app.models.requests import AuthConfig, EndpointRequest


class EndpointAnalysisResult:
    def __init__(
        self,
        url: str,
        method: str,
        request_headers: dict[str, str],
        request_body: dict[str, Any] | None,
        status_code: int,
        response_headers: dict[str, str],
        response_body: Any,
        description: str | None,
    ):
        self.url = url
        self.method = method
        self.request_headers = request_headers
        self.request_body = request_body
        self.status_code = status_code
        self.response_headers = response_headers
        self.response_body = response_body
        self.description = description

    def to_prompt_context(self) -> str:
        lines = [
            f"## Live API Endpoint Observation",
            f"",
            f"**URL:** {self.url}",
            f"**Method:** {self.method}",
            f"",
            f"### Request Headers Sent",
            f"```json",
            json.dumps(self.request_headers, indent=2),
            f"```",
        ]

        if self.request_body is not None:
            lines += [
                f"",
                f"### Request Body Sent",
                f"```json",
                json.dumps(self.request_body, indent=2),
                f"```",
            ]

        lines += [
            f"",
            f"### Response",
            f"**Status Code:** {self.status_code}",
            f"",
            f"**Response Headers:**",
            f"```json",
            json.dumps(dict(self.response_headers), indent=2),
            f"```",
            f"",
            f"**Response Body:**",
            f"```json",
            json.dumps(self.response_body, indent=2) if isinstance(self.response_body, (dict, list)) else str(self.response_body),
            f"```",
        ]

        if self.description:
            lines = [f"## Context\n{self.description}\n"] + lines

        return "\n".join(lines)


def _build_auth_headers(auth: AuthConfig) -> dict[str, str]:
    if auth.type == "bearer" and auth.token:
        return {"Authorization": f"Bearer {auth.token}"}
    if auth.type == "api_key" and auth.api_key:
        return {auth.header_name: auth.api_key}
    if auth.type == "basic" and auth.username and auth.password:
        import base64
        creds = base64.b64encode(f"{auth.username}:{auth.password}".encode()).decode()
        return {"Authorization": f"Basic {creds}"}
    return {}


async def analyze_endpoint(request: EndpointRequest) -> EndpointAnalysisResult:
    headers = dict(request.headers)
    if request.auth:
        headers.update(_build_auth_headers(request.auth))

    # Sanitize auth headers from what we store (don't include secrets in the prompt)
    safe_headers = {
        k: ("***" if k.lower() in ("authorization", "x-api-key") else v)
        for k, v in headers.items()
    }

    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, follow_redirects=True) as client:
        if request.method in ("GET", "DELETE", "HEAD"):
            response = await client.request(request.method, request.url, headers=headers)
        else:
            response = await client.request(
                request.method,
                request.url,
                headers=headers,
                json=request.body,
            )

    try:
        response_body = response.json()
    except Exception:
        response_body = response.text

    return EndpointAnalysisResult(
        url=request.url,
        method=request.method,
        request_headers=safe_headers,
        request_body=request.body,
        status_code=response.status_code,
        response_headers=dict(response.headers),
        response_body=response_body,
        description=request.description,
    )
