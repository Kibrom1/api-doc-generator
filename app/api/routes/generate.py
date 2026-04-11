import httpx
from fastapi import APIRouter, HTTPException, status

from app.models.requests import EndpointRequest, RepoRequest
from app.models.responses import GeneratedContract
from app.services import contract_generator, endpoint_analyzer, repo_analyzer, storage

router = APIRouter(prefix="/generate", tags=["Generate"])


@router.post(
    "/from-endpoint",
    response_model=GeneratedContract,
    summary="Generate API contract from a live endpoint",
    description=(
        "Call a live API endpoint and use AI to generate an OpenAPI 3.1.0 spec "
        "and Markdown documentation based on the observed request/response."
    ),
)
async def generate_from_endpoint(request: EndpointRequest):
    try:
        analysis = await endpoint_analyzer.analyze_endpoint(request)
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Request to {request.url} timed out.",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not reach {request.url}: {e}",
        )

    try:
        contract = await contract_generator.generate_from_endpoint(analysis)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    saved_path = storage.save(contract, replace_existing=request.replace_existing)
    contract.saved_to = str(saved_path)
    return contract


@router.post(
    "/from-repo",
    response_model=GeneratedContract,
    summary="Generate API contract from a source code repository",
    description=(
        "Clone a GitHub or GitLab repository, identify API source files, "
        "and use AI to generate an OpenAPI 3.1.0 spec and Markdown documentation."
    ),
)
async def generate_from_repo(request: RepoRequest):
    try:
        analysis = await repo_analyzer.analyze_repo(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to clone or read repository: {e}",
        )

    if not analysis.files:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No API-relevant source files found in the repository.",
        )

    try:
        contract = await contract_generator.generate_from_repo(analysis)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    saved_path = storage.save(contract, replace_existing=request.replace_existing)
    contract.saved_to = str(saved_path)
    return contract
