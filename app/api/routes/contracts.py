from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.models.responses import ContractSummary, GeneratedContract
from app.services import storage


class MarkdownUpdateRequest(BaseModel):
    markdown_doc: str

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.get(
    "",
    response_model=list[ContractSummary],
    summary="List all saved contracts",
)
async def list_contracts():
    return storage.list_contracts()


@router.get(
    "/{slug}/{timestamp}",
    response_model=GeneratedContract,
    summary="Get a saved contract by slug and timestamp",
)
async def get_contract(slug: str, timestamp: str):
    contract = storage.load_contract(slug, timestamp)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {slug}/{timestamp} not found.",
        )
    return contract


@router.patch(
    "/{slug}/{timestamp}/markdown",
    response_model=GeneratedContract,
    summary="Update the Markdown documentation for a saved contract",
)
async def update_markdown(slug: str, timestamp: str, body: MarkdownUpdateRequest):
    updated = storage.update_markdown(slug, timestamp, body.markdown_doc)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {slug}/{timestamp} not found.",
        )
    contract = storage.load_contract(slug, timestamp)
    return contract
