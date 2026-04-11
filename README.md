# api-doc-generator

AI-powered FastAPI service that generates OpenAPI 3.1.0 specifications and Markdown documentation from a live API endpoint or a source code repository.

## How it works

**From a live endpoint** — the service calls the target URL, captures the real request/response, and sends it to Claude to infer the full API contract.

**From a repository** — the service shallow-clones the repo, scores source files by likelihood of containing route definitions, and sends the most relevant files to Claude to generate a complete OpenAPI spec.

Generated contracts are stored on disk and served back through a REST API consumed by [api-doc-portal](../api-doc-portal).

## Requirements

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

```bash
cd api-doc-generator
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
ANTHROPIC_API_KEY=sk-ant-...
```

## Running

```bash
uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

## Configuration

All settings are read from `.env` or environment variables.

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | required | Anthropic API key |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Claude model to use |
| `OUTPUT_DIR` | `output` | Directory where contracts are saved |
| `MAX_REPO_FILES` | `30` | Max source files sent to Claude per repo analysis |
| `MAX_REPO_FILE_SIZE_KB` | `100` | Files larger than this are skipped |
| `REQUEST_TIMEOUT_SECONDS` | `30` | HTTP timeout when probing live endpoints |

## API Reference

### Generate

#### `POST /api/v1/generate/from-endpoint`

Call a live endpoint and generate a contract from the observed response.

```json
{
  "url": "https://api.example.com/users",
  "method": "GET",
  "headers": {},
  "body": null,
  "auth": null,
  "description": "Optional context hint for Claude",
  "replace_existing": false
}
```

**Auth options** (`auth` field):

| Type | Required fields |
|---|---|
| `bearer` | `token` |
| `api_key` | `api_key`, optionally `header_name` (default: `X-API-Key`) |
| `basic` | `username`, `password` |

#### `POST /api/v1/generate/from-repo`

Shallow-clone a repository and generate a contract from its source code.

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

`service_path` is useful for monorepos — set it to the subdirectory containing the API service (e.g. `"services/users"`).  
`framework` is an optional hint to Claude (e.g. `"fastapi"`, `"nestjs"`, `"express"`).

### Contracts

#### `GET /api/v1/contracts`

List all saved contracts, newest first.

#### `GET /api/v1/contracts/{slug}/{timestamp}`

Retrieve a specific contract by its slug and timestamp.

### Health

#### `GET /health`

Returns `{"status": "ok"}`.

## Output

Each generated contract is saved under `output/{slug}/{timestamp}/`:

```
output/
  api.example.com-users/
    2026-04-10T14-30-00/
      openapi.yaml   ← OpenAPI 3.1.0 spec
      openapi.json   ← same spec as JSON
      contract.md    ← Markdown documentation
      meta.json      ← source, source_ref, generated_at
```

Multiple generations for the same source URL accumulate as separate timestamped directories. Set `replace_existing: true` in the request to overwrite previous versions for the same slug.

## Running tests

```bash
pytest
```

## Project structure

```
app/
  api/routes/
    generate.py    — /generate endpoints
    contracts.py   — /contracts endpoints
    health.py      — /health endpoint
  services/
    endpoint_analyzer.py   — HTTP probe + response capture
    repo_analyzer.py       — repo clone + file scoring
    contract_generator.py  — Claude prompt construction + response parsing
    storage.py             — filesystem read/write
  models/
    requests.py    — EndpointRequest, RepoRequest, AuthConfig
    responses.py   — GeneratedContract, ContractSummary
  core/
    config.py      — Settings (pydantic-settings)
  main.py          — FastAPI app + middleware
```
