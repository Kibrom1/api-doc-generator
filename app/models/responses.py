from datetime import datetime
from pydantic import BaseModel


class GeneratedContract(BaseModel):
    openapi_yaml: str
    openapi_json: dict
    markdown_doc: str
    source: str           # "endpoint" or "repo"
    source_ref: str       # the URL or repo URL used
    generated_at: datetime
    saved_to: str | None = None  # filesystem path where files were written


class ContractSummary(BaseModel):
    slug: str
    timestamp: str
    source: str
    source_ref: str
    generated_at: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: str | None = None
