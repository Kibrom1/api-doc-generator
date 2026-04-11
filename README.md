# api-doc-generator

AI-powered FastAPI service that generates OpenAPI 3.1.0 specifications and Markdown documentation from a live API endpoint or a source code repository. Contracts are stored on disk and served back through a REST API consumed by [api-doc-portal](../api-doc-portal).

## How it works

```
Input Mode A — Live Endpoint
  ┌─────────────┐     HTTP probe      ┌────────────────┐    Claude    ┌──────────────┐
  │  Endpoint   │ ─── real req/resp ─▶│ EndpointAnalyzer│ ──────────▶│  OpenAPI +   │
  │  URL        │                     └────────────────┘              │  Markdown    │
  └─────────────┘                                                      └──────────────┘

Input Mode B — Repository
  ┌─────────────┐   shallow clone     ┌────────────────┐    Claude    ┌──────────────┐
  │  Repo URL   │ ─── score files ──▶ │  RepoAnalyzer  │ ──────────▶│  OpenAPI +   │
  │  (GitHub /  │                     └────────────────┘              │  Markdown    │
  │  GitLab /   │                                                      └──────────────┘
  │  local)     │
  └─────────────┘
```

Both modes produce the same output: an **OpenAPI 3.1.0 spec** (YAML + JSON) and a **structured Markdown document**, saved to disk and returned in the API response.

## Requirements

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)
- `git` CLI on `$PATH` (required by the repo analyzer)

## Setup

```bash
cd api-doc-generator
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=sk-ant-...
```

## Running

```bash
uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

## Configuration

All settings are loaded from `.env` or environment variables via `pydantic-settings`.

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | **required** | Anthropic API key |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Model used for generation |
| `OUTPUT_DIR` | `output` | Root directory for saved contracts |
| `MAX_REPO_FILES` | `30` | Max source files sent to Claude per repo job |
| `MAX_REPO_FILE_SIZE_KB` | `100` | Files exceeding this are skipped |
| `REQUEST_TIMEOUT_SECONDS` | `30` | HTTP timeout when probing live endpoints |

## API reference

### Generate

#### `POST /api/v1/generate/from-endpoint`

Probes a live endpoint and uses the observed request/response to generate a contract.

**Request body:**

```json
{
  "url": "https://api.example.com/users",
  "method": "GET",
  "headers": {},
  "body": null,
  "auth": null,
  "description": "Optional plain-English hint sent to Claude",
  "replace_existing": false
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `url` | string | yes | Full URL including scheme |
| `method` | string | no | Default: `GET`. Automatically uppercased |
| `headers` | object | no | Extra request headers |
| `body` | object | no | JSON body for POST/PUT/PATCH |
| `auth` | object | no | See auth config below |
| `description` | string | no | Context hint appended to the Claude prompt |
| `replace_existing` | bool | no | If `true`, deletes all previous versions for this slug before saving |

**Auth config (`auth` field):**

| `type` | Additional fields |
|---|---|
| `bearer` | `token` |
| `api_key` | `api_key`, optionally `header_name` (default: `X-API-Key`) |
| `basic` | `username`, `password` |

Auth header values are **sanitized before being sent to Claude** — Authorization and X-API-Key values are replaced with `***` in the prompt context.

#### `POST /api/v1/generate/from-repo`

Shallow-clones a repository, identifies API-relevant source files by scoring them against route definition patterns, and uses those files to generate a contract.

**Request body:**

```json
{
  "repo_url": "https://github.com/org/my-api",
  "access_token": null,
  "branch": "main",
  "service_path": ".",
  "framework": "fastapi",
  "replace_existing": false
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `repo_url` | string | yes | GitHub, GitLab, or any clonable git URL |
| `access_token` | string | no | Personal access token for private repos |
| `branch` | string | no | Default: `main` |
| `service_path` | string | no | Subdirectory to treat as root (monorepos), default: `.` |
| `framework` | string | no | Optional hint to Claude: `fastapi`, `nestjs`, `express`, `django`, etc. |
| `replace_existing` | bool | no | Same as endpoint mode |

**File scoring:** The analyzer walks the repo and scores each file by matching its path against patterns like `routes`, `controllers`, `views`, `handlers`, `router`, `api`, `endpoints`. The top-scoring files up to `MAX_REPO_FILES` (within the `MAX_REPO_FILE_SIZE_KB` limit) are sent to Claude.

**Error responses:**

| Status | Condition |
|---|---|
| `400` | Failed to clone or read repository |
| `422` | No API-relevant source files found after scoring |

### Contracts

#### `GET /api/v1/contracts`

Returns all saved contracts as a list, sorted newest first.

**Response:** `ContractSummary[]`

```json
[
  {
    "slug": "api.example.com-users",
    "timestamp": "2026-04-10T14-30-00",
    "source": "endpoint",
    "source_ref": "https://api.example.com/users",
    "generated_at": "2026-04-10T14:30:00Z"
  }
]
```

#### `GET /api/v1/contracts/{slug}/{timestamp}`

Returns the full contract for a specific slug + timestamp.

**Response:** `GeneratedContract`

```json
{
  "openapi_yaml": "openapi: 3.1.0\n...",
  "openapi_json": { "openapi": "3.1.0", "..." },
  "markdown_doc": "# API Title\n...",
  "source": "endpoint",
  "source_ref": "https://api.example.com/users",
  "generated_at": "2026-04-10T14:30:00Z",
  "saved_to": "output/api.example.com-users/2026-04-10T14-30-00"
}
```

**Error:** `404` if slug/timestamp not found.

### Health

#### `GET /health`

Returns `{"status": "ok"}`. Use for liveness probes.

## Output / storage

Each contract is saved under `output/{slug}/{timestamp}/`:

```
output/
  api.example.com-users/           ← slug (derived from URL or repo)
    2026-04-10T14-30-00/           ← timestamp (ISO 8601, colons → dashes)
      openapi.yaml                 ← OpenAPI 3.1.0 YAML
      openapi.json                 ← same spec as JSON
      contract.md                  ← Markdown documentation
      meta.json                    ← source, source_ref, generated_at
    2026-04-11T09-15-00/           ← second version of same slug
      ...
```

**Slug derivation:**
- Endpoint URL `https://api.example.com/users` → `api.example.com-users`
- Repo URL `https://github.com/org/my-api` → `github.com-org-my-api`

Multiple generations for the same source accumulate as separate timestamped directories. `replace_existing: true` removes all previous timestamp directories for the slug before saving the new one.

## Markdown output format

Claude is constrained by a strict system prompt and server-side post-processing to produce only these sections, in this order:

1. `# <API Title>` — one-sentence description
2. `## Overview` — base URL, auth method, content type, and a note directing consumers to the downstream service's own documentation for authoritative details not captured here
3. `## Endpoints` — table with Method / Path / Description columns
4. One `## <Tag>` section per endpoint group, each containing `### METHOD /path` subsections with:
   - Parameters table
   - Request body table
   - Responses table
   - Error codes table
   - Implementation details

Sections not in this list (`## Notes`, `## Data Models`, `## Schemas`, `## Observations`, `## Caveats`, `## Summary`, `## Live Data Snapshot`, etc.) are **stripped by `_strip_extra_sections()`** before the contract is saved, regardless of what Claude generates.

## Running tests

```bash
pytest
```

## Project structure

```
app/
  api/routes/
    generate.py       — POST /api/v1/generate/from-endpoint and /from-repo
    contracts.py      — GET /api/v1/contracts and /{slug}/{timestamp}
    health.py         — GET /health
  services/
    endpoint_analyzer.py   — HTTP probe, auth header handling, response capture
    repo_analyzer.py       — git clone, file scoring, source extraction
    contract_generator.py  — Claude prompt construction, response parsing, section stripping
    storage.py             — filesystem save/load, slug derivation, version management
  models/
    requests.py       — EndpointRequest, RepoRequest, AuthConfig
    responses.py      — GeneratedContract, ContractSummary, ErrorDetail
  core/
    config.py         — Settings loaded from .env via pydantic-settings
  main.py             — FastAPI app, CORS middleware, router registration
tests/
  test_endpoint_analyzer.py
  test_repo_analyzer.py
  test_contract_generator.py
```
