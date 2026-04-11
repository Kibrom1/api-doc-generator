from typing import Any
from pydantic import BaseModel, HttpUrl, field_validator


class AuthConfig(BaseModel):
    type: str  # "bearer", "api_key", "basic"
    token: str | None = None       # for bearer
    api_key: str | None = None     # for api_key
    header_name: str = "X-API-Key" # for api_key
    username: str | None = None    # for basic
    password: str | None = None    # for basic


class EndpointRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: dict[str, str] = {}
    body: dict[str, Any] | None = None
    auth: AuthConfig | None = None
    description: str | None = None  # optional context hint for Claude
    replace_existing: bool = False

    @field_validator("method")
    @classmethod
    def uppercase_method(cls, v: str) -> str:
        return v.upper()


class RepoRequest(BaseModel):
    repo_url: str
    access_token: str | None = None  # for private repos
    branch: str = "main"
    service_path: str = "."          # for monorepos, relative path to service root
    framework: str | None = None     # optional hint: "fastapi", "nestjs", etc.
    replace_existing: bool = False
