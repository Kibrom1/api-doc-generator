import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.services.repo_analyzer import _collect_files, _inject_token_into_url, _score_file


class TestInjectTokenIntoUrl:
    def test_injects_token_into_https_url(self):
        url = "https://github.com/org/repo.git"
        result = _inject_token_into_url(url, "mytoken")
        assert result == "https://oauth2:mytoken@github.com/org/repo.git"

    def test_does_not_modify_ssh_url(self):
        url = "git@github.com:org/repo.git"
        result = _inject_token_into_url(url, "mytoken")
        assert result == url  # SSH unchanged


class TestScoreFile:
    def _make_file(self, tmp_path: Path, name: str, content: str = "x") -> Path:
        f = tmp_path / name
        f.write_text(content)
        return f

    def test_route_file_scores_high(self, tmp_path):
        f = self._make_file(tmp_path, "routes.py")
        score = _score_file(f, tmp_path)
        assert score >= 10

    def test_controller_file_scores_high(self, tmp_path):
        f = self._make_file(tmp_path, "user_controller.ts")
        score = _score_file(f, tmp_path)
        assert score >= 10

    def test_test_file_scores_low(self, tmp_path):
        f = self._make_file(tmp_path, "test_routes.py")
        score = _score_file(f, tmp_path)
        assert score < 10

    def test_non_api_extension_excluded(self, tmp_path):
        f = self._make_file(tmp_path, "styles.css")
        score = _score_file(f, tmp_path)
        assert score < 0

    def test_entrypoint_file_scores_higher(self, tmp_path):
        f = self._make_file(tmp_path, "main.py")
        score = _score_file(f, tmp_path)
        assert score >= 5


class TestCollectFiles:
    def test_collects_relevant_files(self, tmp_path):
        (tmp_path / "routes.py").write_text("from fastapi import APIRouter")
        (tmp_path / "models.py").write_text("from pydantic import BaseModel")
        (tmp_path / "README.md").write_text("# Docs")
        (tmp_path / "styles.css").write_text("body {}")

        files = _collect_files(tmp_path, max_files=10, max_size_kb=100)
        names = [f["path"] for f in files]

        assert "routes.py" in names
        assert "models.py" in names
        assert "README.md" not in names
        assert "styles.css" not in names

    def test_respects_max_files_limit(self, tmp_path):
        for i in range(10):
            (tmp_path / f"router_{i}.py").write_text(f"# router {i}")

        files = _collect_files(tmp_path, max_files=3, max_size_kb=100)
        assert len(files) <= 3

    def test_skips_node_modules(self, tmp_path):
        nm = tmp_path / "node_modules"
        nm.mkdir()
        (nm / "routes.js").write_text("module.exports = {}")

        files = _collect_files(tmp_path, max_files=10, max_size_kb=100)
        assert not any("node_modules" in f["path"] for f in files)

    def test_skips_oversized_files(self, tmp_path):
        big_file = tmp_path / "routes.py"
        big_file.write_text("x" * 200 * 1024)  # 200KB

        files = _collect_files(tmp_path, max_files=10, max_size_kb=100)
        assert not any(f["path"] == "routes.py" for f in files)
