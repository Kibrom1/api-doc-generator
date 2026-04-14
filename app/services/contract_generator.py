import json
import re
from datetime import datetime, timezone

import anthropic
import yaml

from app.core.config import settings
from app.models.responses import GeneratedContract
from app.services.endpoint_analyzer import EndpointAnalysisResult
from app.services.repo_analyzer import RepoAnalysisResult

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are an expert API documentation engineer writing documentation for API consumers — developers who will integrate against this API. Your job is to analyze API information and produce two outputs:

1. A complete, valid OpenAPI 3.1.0 specification in YAML format.
2. A Markdown documentation document that follows the EXACT structure below — no more, no less.

## OpenAPI spec rules:
- Must be valid, parseable YAML.
- Include all endpoints, methods, request/response schemas, status codes, and parameters you can infer.
- Include validation rules (min, max, pattern, required, enum) in schemas where detectable.
- Use securitySchemes if authentication is detectable.

## Markdown structure rules:
The Markdown document MUST contain ONLY these sections, in this order:

1. `# <API Title>`
   Two to four sentences describing what this API does, who it is for, and what problems it solves. Be specific — mention the domain, the type of data managed, and any notable characteristics of the API.

2. `## Overview`
   - **Base URL:** the server URL
   - **Authentication:** method and how to supply credentials, or "None required"
   - **Content Type:** e.g. `application/json`
   - **Rate Limiting:** any known limits, or "Not specified"
   - A note stating that this document reflects observed or inferred behavior and that consumers should refer to the downstream service's own documentation for authoritative details, edge cases, and advanced usage not captured here.

3. `## Endpoints`
   A Markdown table with columns: Method | Path | Description

4. One `## <Tag or Resource Name>` section per logical group of endpoints, each containing:
   - One `### \`METHOD /path\`` subsection per endpoint with:

     A two to three sentence description of what this endpoint does, what it returns, and any important behavior consumers should know (e.g. pagination, ordering, side effects). Do not just repeat the path.

     - `#### Parameters` table (Name | In | Type | Required | Description) — omit if none. The Description column must explain the parameter's purpose and any constraints, not just its name.
     - `#### Request Body` — include the content type, then a table (Field | Type | Required | Description). The Description column must explain the field's purpose, accepted values, and any constraints. Omit if no request body.
     - `#### Responses` table (Status | Description) — the Description column must explain what the response contains and when that status is returned, not just the HTTP status phrase.
     - `#### Error Codes` table (Code | Meaning) — describe what triggers each error and how the consumer should handle it. Omit if no errors specific to this endpoint.
     - `#### Behavior Notes` — A detailed prose section (not just bullet points) covering:
       - How the endpoint behaves under normal conditions and edge cases
       - Any side effects (e.g. triggers an event, modifies related records)
       - Ordering, pagination, or filtering behavior where applicable
       - Important constraints consumers must respect (e.g. field immutability, uniqueness rules)
     - `#### Internal Implementation` — A technical section for developers maintaining or integrating deeply with this service, covering:
       - Input validation and constraint enforcement logic
       - Exception handling and what triggers each error response
       - Data mapping, transformation, or computation logic
       - Dependencies on other services, repositories, or utilities

STRICT RULES — violations are not acceptable:
- The Markdown document MUST end after the last `### \`METHOD /path\`` subsection. No sections after that.
- The downstream service reference note MUST appear inside `## Overview`, not as a standalone section.
- `#### Behavior Notes` and `#### Internal Implementation` are ALWAYS required for every endpoint. Do not omit them even if information seems limited — infer from context.
- The `<openapi>` block MUST NOT contain internal implementation details, utility calls, or exception logic unless they are part of the public contract (e.g. status codes).
- Do NOT add: Data Models, Notes, Observations, Caveats, Warnings, Examples, Request Examples, Request Headers, Summary tables beyond section 3, or any section not listed above.
- Do NOT add blockquotes, callout boxes, or ⚠️ notices.
- Do NOT include any explanation outside the two XML sections.
- Write for a developer audience. Be precise, specific, and useful. Avoid vague phrases like "handles the request" or "processes the data" — say exactly what happens.

Respond in exactly this format:

<openapi>
[YAML content here]
</openapi>

<markdown>
[Markdown content here]
</markdown>
"""


def _build_endpoint_prompt(result: EndpointAnalysisResult) -> str:
    return f"""Analyze the following live API endpoint observation and generate the API contract and documentation.

{result.to_prompt_context()}

Generate a complete OpenAPI 3.1.0 spec and Markdown documentation for this endpoint.
If the response reveals additional endpoints (e.g., from an error message or HATEOAS links), document those too.
"""


def _build_repo_prompt(result: RepoAnalysisResult) -> str:
    return f"""Analyze the following backend source code and generate a complete API contract and documentation.

{result.to_prompt_context()}

Generate a complete OpenAPI 3.1.0 spec covering ALL API endpoints found in the code.
Extract validation rules, required fields, authentication requirements, and error responses from the code.
"""


_ALLOWED_H2 = {"overview", "endpoints"}
_BLOCKED_H2 = {
    "notes", "observations", "notes & observations", "notes and observations",
    "caveats", "notes & caveats", "notes and caveats",
    "data models", "models", "schemas", "schema",
    "live data snapshot", "snapshot", "summary",
    "additional notes", "remarks", "internal calls",
}


def _strip_extra_sections(markdown: str) -> str:
    """Remove any ## sections that are not in the allowed list and are not resource/tag groups."""
    lines = markdown.splitlines()
    result: list[str] = []
    skip = False

    for line in lines:
        if line.startswith("## "):
            heading = line[3:].strip().lower().rstrip(":")
            # Strip trailing punctuation/emoji
            heading = heading.rstrip(" :-—")
            if heading in _BLOCKED_H2:
                skip = True
                continue
            else:
                skip = False
        elif line.startswith("# "):
            skip = False

        if not skip:
            result.append(line)

    # Remove trailing horizontal rules / blank lines
    text = "\n".join(result)
    text = re.sub(r"(\n---\s*)+$", "", text).strip()
    return text


def _parse_response(raw: str) -> tuple[str, str]:
    """Extract YAML and Markdown from Claude's response."""
    openapi_match = re.search(r"<openapi>(.*?)</openapi>", raw, re.DOTALL)
    markdown_match = re.search(r"<markdown>(.*?)</markdown>", raw, re.DOTALL)

    openapi_yaml = openapi_match.group(1).strip() if openapi_match else ""
    markdown_doc = markdown_match.group(1).strip() if markdown_match else ""

    if not openapi_yaml:
        raise ValueError("Claude did not return an <openapi> block in its response.")
    if not markdown_doc:
        raise ValueError("Claude did not return a <markdown> block in its response.")

    markdown_doc = _strip_extra_sections(markdown_doc)

    return openapi_yaml, markdown_doc


def _yaml_to_json(yaml_str: str) -> dict:
    try:
        return yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        raise ValueError(f"Generated OpenAPI YAML is not valid: {e}")


async def generate_from_endpoint(result: EndpointAnalysisResult) -> GeneratedContract:
    prompt = _build_endpoint_prompt(result)

    message = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=8096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    openapi_yaml, markdown_doc = _parse_response(raw)
    openapi_json = _yaml_to_json(openapi_yaml)

    return GeneratedContract(
        openapi_yaml=openapi_yaml,
        openapi_json=openapi_json,
        markdown_doc=markdown_doc,
        source="endpoint",
        source_ref=result.url,
        generated_at=datetime.now(timezone.utc),
    )


async def generate_from_repo(result: RepoAnalysisResult) -> GeneratedContract:
    prompt = _build_repo_prompt(result)

    message = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=8096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    openapi_yaml, markdown_doc = _parse_response(raw)
    openapi_json = _yaml_to_json(openapi_yaml)

    return GeneratedContract(
        openapi_yaml=openapi_yaml,
        openapi_json=openapi_json,
        markdown_doc=markdown_doc,
        source="repo",
        source_ref=result.repo_url,
        generated_at=datetime.now(timezone.utc),
    )
