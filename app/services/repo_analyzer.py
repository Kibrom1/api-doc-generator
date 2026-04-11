import os
import re
import shutil
import tempfile
from pathlib import Path

import git

from app.core.config import settings
from app.models.requests import RepoRequest

# Files/directories to always skip
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", ".nuxt", "coverage", ".pytest_cache",
    "migrations", "alembic", ".mypy_cache", "vendor",
}

# Extensions that are likely to contain API route/controller code
API_EXTENSIONS = {".py", ".ts", ".js", ".java", ".kt", ".go"}

# File name patterns that strongly indicate route/controller/handler files
ROUTE_PATTERNS = re.compile(
    r"(route|router|controller|handler|endpoint|view|api|resource|schema|dto|model|validator|middleware|serializer|service|logic|util|helper|exception|error|format)",
    re.IGNORECASE,
)

# Framework-specific entrypoint files
ENTRYPOINT_FILES = {
    "main.py", "app.py", "server.py", "index.ts", "index.js",
    "app.ts", "app.js", "main.ts", "main.go",
}


class RepoAnalysisResult:
    def __init__(self, repo_url: str, branch: str, framework_hint: str | None, files: list[dict]):
        self.repo_url = repo_url
        self.branch = branch
        self.framework_hint = framework_hint
        self.files = files  # list of {"path": str, "content": str}

    def to_prompt_context(self) -> str:
        lines = [
            f"## Repository Source Code",
            f"",
            f"**Repository:** {self.repo_url}",
            f"**Branch:** {self.branch}",
        ]

        if self.framework_hint:
            lines.append(f"**Framework hint:** {self.framework_hint}")

        lines += ["", f"The following {len(self.files)} files were identified as relevant API source files:", ""]

        for f in self.files:
            lines += [
                f"### File: `{f['path']}`",
                f"```",
                f"{f['content']}",
                f"```",
                "",
            ]

        return "\n".join(lines)


def _score_file(path: Path, service_root: Path) -> int:
    """Higher score = more likely to contain API contract-relevant code."""
    name = path.name.lower()
    rel = str(path.relative_to(service_root)).lower()
    score = 0

    if path.suffix not in API_EXTENSIONS:
        return -1

    # Strong signals
    if ROUTE_PATTERNS.search(name):
        score += 10
    if name in ENTRYPOINT_FILES:
        score += 5

    # Directory signals
    for segment in Path(rel).parts[:-1]:
        if ROUTE_PATTERNS.search(segment):
            score += 3

    # Penalize test files
    if "test" in rel or "spec" in rel:
        score -= 5

    return score


def _collect_files(service_root: Path, max_files: int, max_size_kb: int) -> list[dict]:
    candidates: list[tuple[int, Path]] = []

    for file_path in service_root.rglob("*"):
        if not file_path.is_file():
            continue
        # Skip ignored directories
        if any(part in SKIP_DIRS for part in file_path.parts):
            continue

        score = _score_file(file_path, service_root)
        if score < 0:
            continue

        candidates.append((score, file_path))

    # Sort by score descending, then by path for determinism
    candidates.sort(key=lambda x: (-x[0], str(x[1])))

    results = []
    for _, file_path in candidates[:max_files]:
        size_kb = file_path.stat().st_size / 1024
        if size_kb > max_size_kb:
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            results.append({
                "path": str(file_path.relative_to(service_root)),
                "content": content,
            })
        except Exception:
            continue

    return results


def _inject_token_into_url(repo_url: str, token: str) -> str:
    """Inject a personal access token into a HTTPS repo URL."""
    if repo_url.startswith("https://"):
        return repo_url.replace("https://", f"https://oauth2:{token}@", 1)
    return repo_url


async def analyze_repo(request: RepoRequest) -> RepoAnalysisResult:
    repo_url = request.repo_url
    is_local = os.path.isdir(repo_url)
    
    tmp_dir = None
    if not is_local:
        clone_url = repo_url
        if request.access_token:
            clone_url = _inject_token_into_url(clone_url, request.access_token)
        
        tmp_dir = tempfile.mkdtemp(prefix="api-doc-gen-")
        try:
            git.Repo.clone_from(
                clone_url,
                tmp_dir,
                branch=request.branch,
                depth=1,  # shallow clone — only latest snapshot
                no_single_branch=False,
            )
            service_root = Path(tmp_dir)
        except Exception as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise ValueError(f"Failed to clone repository: {e}")
    else:
        service_root = Path(repo_url)

    try:
        if request.service_path and request.service_path != ".":
            service_root = service_root / request.service_path

        if not service_root.exists():
            raise ValueError(f"Service path does not exist: {service_root}")

        files = _collect_files(
            service_root,
            max_files=settings.max_repo_files,
            max_size_kb=settings.max_repo_file_size_kb,
        )

        return RepoAnalysisResult(
            repo_url=request.repo_url,
            branch=request.branch,
            framework_hint=request.framework,
            files=files,
        )
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)
