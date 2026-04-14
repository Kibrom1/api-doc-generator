import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

from app.core.config import settings
from app.models.responses import ContractSummary, GeneratedContract


def _slug_from_url(url: str) -> str:
    """Derive a safe directory name from a URL."""
    parsed = urlparse(url)
    # Use host + path, strip leading slash, replace unsafe chars
    raw = f"{parsed.netloc}{parsed.path}".strip("/")
    return re.sub(r"[^\w\-.]", "-", raw).strip("-") or "unknown"


def _slug_from_repo(repo_url: str) -> str:
    """Derive a safe directory name from a repo URL."""
    # e.g. https://github.com/org/repo.git → github.com-org-repo
    parsed = urlparse(repo_url)
    raw = f"{parsed.netloc}{parsed.path}".replace(".git", "").strip("/")
    return re.sub(r"[^\w\-.]", "-", raw).strip("-") or "unknown"


def save(contract: GeneratedContract, replace_existing: bool = False) -> Path:
    """
    Save the generated contract to the filesystem.

    Structure:
        output/{service-slug}/{timestamp}/
            openapi.yaml
            openapi.json
            contract.md

    Returns the directory path where files were saved.
    """
    if contract.source == "endpoint":
        slug = _slug_from_url(contract.source_ref)
    else:
        slug = _slug_from_repo(contract.source_ref)

    slug_path = Path(settings.output_dir) / slug
    
    # Handle replacement/overwrite
    if replace_existing and slug_path.exists():
        for item in slug_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)

    timestamp = contract.generated_at.strftime("%Y-%m-%dT%H-%M-%S")
    output_path = slug_path / timestamp
    output_path.mkdir(parents=True, exist_ok=True)

    (output_path / "openapi.yaml").write_text(contract.openapi_yaml, encoding="utf-8")
    (output_path / "openapi.json").write_text(
        json.dumps(contract.openapi_json, indent=2), encoding="utf-8"
    )
    (output_path / "contract.md").write_text(contract.markdown_doc, encoding="utf-8")
    (output_path / "meta.json").write_text(
        json.dumps({
            "source": contract.source,
            "source_ref": contract.source_ref,
            "generated_at": contract.generated_at.isoformat(),
        }),
        encoding="utf-8",
    )

    return output_path


def list_contracts() -> list[ContractSummary]:
    """Return a summary list of all saved contracts, newest first."""
    output_root = Path(settings.output_dir)
    if not output_root.exists():
        return []

    results = []
    for slug_dir in sorted(output_root.iterdir()):
        if not slug_dir.is_dir():
            continue
        for ts_dir in sorted(slug_dir.iterdir(), reverse=True):
            if not ts_dir.is_dir():
                continue
            meta = _read_meta(ts_dir)
            if meta:
                results.append(ContractSummary(
                    slug=slug_dir.name,
                    timestamp=ts_dir.name,
                    **meta,
                ))

    return sorted(results, key=lambda c: c.generated_at, reverse=True)


def load_contract(slug: str, timestamp: str) -> GeneratedContract | None:
    """Load a full contract from disk. Returns None if not found."""
    contract_dir = Path(settings.output_dir) / slug / timestamp
    if not contract_dir.exists():
        return None

    openapi_yaml = (contract_dir / "openapi.yaml").read_text(encoding="utf-8")
    openapi_json = json.loads((contract_dir / "openapi.json").read_text(encoding="utf-8"))
    markdown_doc = (contract_dir / "contract.md").read_text(encoding="utf-8")
    meta = _read_meta(contract_dir) or {}

    from datetime import datetime, timezone
    return GeneratedContract(
        openapi_yaml=openapi_yaml,
        openapi_json=openapi_json,
        markdown_doc=markdown_doc,
        source=meta.get("source", "endpoint"),
        source_ref=meta.get("source_ref", ""),
        generated_at=datetime.fromisoformat(meta.get("generated_at", datetime.now(timezone.utc).isoformat())),
        saved_to=str(contract_dir),
    )


def update_markdown(slug: str, timestamp: str, markdown_doc: str) -> bool:
    """Overwrite contract.md for an existing contract. Returns False if not found."""
    contract_dir = Path(settings.output_dir) / slug / timestamp
    if not contract_dir.exists():
        return False
    (contract_dir / "contract.md").write_text(markdown_doc, encoding="utf-8")
    return True


def _read_meta(contract_dir: Path) -> dict | None:
    """Read meta.json from a contract directory if it exists."""
    meta_file = contract_dir / "meta.json"
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            return None
    # Fall back: infer from directory name
    return None
